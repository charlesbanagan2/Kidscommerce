const express = require('express');
const http = require('http');
const path = require('path');
const fs = require('fs');
const cors = require('cors');
const multer = require('multer');
const Database = require('better-sqlite3');
const { Server } = require('socket.io');
const crypto = require('crypto');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*'} });

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const ROOT = __dirname;
const UPLOAD_DIR = path.join(ROOT, 'uploads');
const DB_DIR = path.join(ROOT, 'db');

for (const dir of [UPLOAD_DIR, DB_DIR, path.join(ROOT, 'public')]) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOAD_DIR),
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname || '') || '';
    cb(null, `${Date.now()}-${Math.round(Math.random()*1e9)}${ext}`);
  }
});
const upload = multer({ storage, limits: { fileSize: 20 * 1024 * 1024 } });

const db = new Database(path.join(DB_DIR, 'data.db'));
db.pragma('journal_mode = WAL');

db.exec(`
CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  buyer_id TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  payment_method TEXT NOT NULL,
  status TEXT NOT NULL,
  return_status TEXT NOT NULL DEFAULT 'NONE',
  last_status_msg TEXT,
  total REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS order_items (
  id TEXT PRIMARY KEY,
  order_id TEXT NOT NULL,
  name TEXT NOT NULL,
  qty INTEGER NOT NULL,
  price REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS return_requests (
  id TEXT PRIMARY KEY,
  order_id TEXT NOT NULL,
  buyer_id TEXT NOT NULL,
  reason TEXT,
  explanation TEXT,
  media_json TEXT,
  created_at INTEGER NOT NULL
);
`);

const insertOrder = db.prepare(`INSERT INTO orders (id,buyer_id,created_at,payment_method,status,return_status,last_status_msg,total) VALUES (?,?,?,?,?,?,?,?)`);
const insertItem = db.prepare(`INSERT INTO order_items (id,order_id,name,qty,price) VALUES (?,?,?,?,?)`);
const getOrdersByBuyer = db.prepare(`SELECT * FROM orders WHERE buyer_id = ? ORDER BY created_at DESC`);
const getItemsByOrder = db.prepare(`SELECT * FROM order_items WHERE order_id = ?`);
const getOrder = db.prepare(`SELECT * FROM orders WHERE id = ?`);
const updateOrderStatus = db.prepare(`UPDATE orders SET status=?, last_status_msg=? WHERE id=?`);
const setReturnRequested = db.prepare(`UPDATE orders SET return_status='REQUESTED' WHERE id=?`);
const cancelOrderStmt = db.prepare(`UPDATE orders SET status='CANCELLED', last_status_msg='Your order has been cancelled.' WHERE id=?`);
const insertReturn = db.prepare(`INSERT INTO return_requests (id,order_id,buyer_id,reason,explanation,media_json,created_at) VALUES (?,?,?,?,?,?,?)`);

function uid() { return crypto.randomUUID(); }

function emitToBuyer(buyerId, event, payload) {
  io.to(`buyer:${buyerId}`).emit(event, payload);
}

function enrich(order) {
  const items = getItemsByOrder.all(order.id);
  return { ...order, items };
}

// Seed demo data if empty
(function seed() {
  const row = db.prepare('SELECT COUNT(*) as c FROM orders').get();
  if (row.c > 0) return;
  const now = Date.now();
  const buyer = 'buyer1';
  const samples = [
    { status: 'TO_PAY', msg: 'Awaiting seller to process. Payment: COD.' },
    { status: 'TO_SHIP', msg: 'Seller is preparing your item.' },
    { status: 'OUT_FOR_DELIVERY', msg: 'Rider has picked up your order.' },
    { status: 'COMPLETED', msg: 'Order Completed' },
    { status: 'CANCELLED', msg: 'Your order has been cancelled.' }
  ];
  for (let i=0;i<samples.length;i++) {
    const id = uid();
    insertOrder.run(id, buyer, now - i*100000, 'COD', samples[i].status, 'NONE', samples[i].msg, 29.99 + i);
    insertItem.run(uid(), id, 'Sample Product #' + (i+1), 1, 29.99 + i);
  }
})();

// Socket.IO auth by buyerId
io.on('connection', (socket) => {
  const buyerId = socket.handshake.query.buyerId || 'buyer1';
  socket.join(`buyer:${buyerId}`);
});

app.use('/uploads', express.static(UPLOAD_DIR));
app.use('/', express.static(path.join(ROOT, 'public')));

// Helpers
function ensureState(order, expected) {
  if (order.status !== expected) {
    const err = new Error(`Invalid state. Expected ${expected}, got ${order.status}`);
    err.status = 400;
    throw err;
  }
}

function notifyAndPatch(order, msg) {
  const enriched = enrich(order);
  emitToBuyer(order.buyer_id, 'notify', { orderId: order.id, message: msg });
  emitToBuyer(order.buyer_id, 'order_updated', { order: enriched });
}

// Routes
app.get('/api/orders', (req, res) => {
  const buyerId = req.query.buyerId || 'buyer1';
  const orders = getOrdersByBuyer.all(buyerId).map(enrich);
  res.json({ orders });
});

app.post('/api/orders', (req, res) => {
  const { buyerId = 'buyer1', items = [{ name: 'New Product', qty: 1, price: 19.99 }], paymentMethod = 'COD' } = req.body || {};
  const id = uid();
  const now = Date.now();
  const total = items.reduce((s, it) => s + (it.price * it.qty), 0);
  insertOrder.run(id, buyerId, now, paymentMethod, 'TO_PAY', 'NONE', 'Awaiting seller to process. Payment: COD.', total);
  for (const it of items) insertItem.run(uid(), id, it.name, it.qty, it.price);
  const order = getOrder.get(id);
  notifyAndPatch(order, 'New order created.');
  res.status(201).json({ order: enrich(order) });
});

app.post('/api/orders/:id/cancel', (req, res, next) => {
  try {
    const id = req.params.id; const order = getOrder.get(id);
    if (!order) return res.status(404).json({ error: 'Order not found' });
    ensureState(order, 'TO_PAY');
    cancelOrderStmt.run(id);
    const updated = getOrder.get(id);
    notifyAndPatch(updated, 'Your order has been cancelled.');
    res.json({ ok: true, message: 'Your order has been cancelled.', order: enrich(updated) });
  } catch (e) { next(e); }
});

app.post('/api/orders/:id/seller/process', (req, res, next) => {
  try {
    const id = req.params.id; const order = getOrder.get(id);
    if (!order) return res.status(404).json({ error: 'Order not found' });
    ensureState(order, 'TO_PAY');
    updateOrderStatus.run('TO_SHIP', 'Seller is preparing your item.', id);
    const updated = getOrder.get(id);
    notifyAndPatch(updated, 'Seller processed your order.');
    res.json({ ok: true, order: enrich(updated) });
  } catch (e) { next(e); }
});

app.post('/api/orders/:id/rider/pickup', (req, res, next) => {
  try {
    const id = req.params.id; const order = getOrder.get(id);
    if (!order) return res.status(404).json({ error: 'Order not found' });
    ensureState(order, 'TO_SHIP');
    updateOrderStatus.run('OUT_FOR_DELIVERY', 'Rider has picked up your order.', id);
    const updated = getOrder.get(id);
    notifyAndPatch(updated, 'Rider has picked up your order.');
    res.json({ ok: true, order: enrich(updated) });
  } catch (e) { next(e); }
});

app.post('/api/orders/:id/rider/in_transit', (req, res, next) => {
  try {
    const id = req.params.id; const order = getOrder.get(id);
    if (!order) return res.status(404).json({ error: 'Order not found' });
    ensureState(order, 'OUT_FOR_DELIVERY');
    updateOrderStatus.run('OUT_FOR_DELIVERY', 'Your order is on the way.', id);
    const updated = getOrder.get(id);
    notifyAndPatch(updated, 'Your order is on the way.');
    res.json({ ok: true, order: enrich(updated) });
  } catch (e) { next(e); }
});

app.post('/api/orders/:id/complete', (req, res, next) => {
  try {
    const id = req.params.id; const order = getOrder.get(id);
    if (!order) return res.status(404).json({ error: 'Order not found' });
    const allowed = ['OUT_FOR_DELIVERY', 'TO_RECEIVE'];
    if (!allowed.includes(order.status) && order.status !== 'OUT_FOR_DELIVERY') {
      const err = new Error('Only receivable orders can be completed'); err.status = 400; throw err;
    }
    updateOrderStatus.run('COMPLETED', 'Order Completed', id);
    const updated = getOrder.get(id);
    notifyAndPatch(updated, 'Order Completed');
    res.json({ ok: true, order: enrich(updated) });
  } catch (e) { next(e); }
});

app.post('/api/orders/:id/return', upload.array('media', 6), (req, res, next) => {
  try {
    const id = req.params.id; const order = getOrder.get(id);
    if (!order) return res.status(404).json({ error: 'Order not found' });
    const { reason = '', explanation = '' } = req.body || {};
    const media = (req.files || []).map(f => ({ filename: f.filename, url: `/uploads/${f.filename}`, mimetype: f.mimetype, size: f.size }));
    insertReturn.run(uid(), id, order.buyer_id, reason, explanation, JSON.stringify(media), Date.now());
    setReturnRequested.run(id);
    const updated = getOrder.get(id);
    notifyAndPatch(updated, 'Your return/refund request has been sent to the seller.');
    res.json({ ok: true, message: 'Your return/refund request has been sent to the seller.', order: enrich(updated) });
  } catch (e) { next(e); }
});

// Error handler
app.use((err, req, res, next) => {
  console.error(err);
  res.status(err.status || 500).json({ error: err.message || 'Server error' });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Buyer OMS running at http://localhost:${PORT}`);
});
