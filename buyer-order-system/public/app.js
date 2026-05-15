(() => {
  const qs = new URLSearchParams(location.search);
  const buyerId = qs.get('buyerId') || 'buyer1';
  const debug = qs.get('debug') === '1';
  document.getElementById('buyerLabel').textContent = `Buyer: ${buyerId}`;

  const socket = io({ query: { buyerId } });
  socket.on('notify', ({ orderId, message }) => toast(message));
  socket.on('order_updated', ({ order }) => {
    state.ordersById[order.id] = order; render();
  });

  const state = { tab: 'TO_PAY', ordersById: {} };

  const tabsEl = document.getElementById('tabs');
  const listEl = document.getElementById('list');
  const modalRoot = document.getElementById('modalRoot');
  const toastRoot = document.getElementById('toastRoot');

  tabsEl.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-tab]');
    if (!btn) return;
    state.tab = btn.dataset.tab;
    for (const b of tabsEl.querySelectorAll('.tab')) b.classList.toggle('active', b===btn);
    render();
  });

  function toast(msg) {
    const div = document.createElement('div');
    div.className = 'toast'; div.textContent = msg;
    toastRoot.appendChild(div);
    setTimeout(()=>{ div.remove(); }, 3500);
  }

  function tabOf(order) {
    if (order.status === 'CANCELLED') return 'CANCELLED';
    if (order.return_status === 'REQUESTED') return 'RETURN_REFUND';
    if (order.status === 'TO_PAY') return 'TO_PAY';
    if (order.status === 'TO_SHIP') return 'TO_SHIP';
    if (order.status === 'OUT_FOR_DELIVERY') return 'TO_RECEIVE';
    if (order.status === 'COMPLETED') return 'COMPLETED';
    return 'TO_PAY';
  }

  async function fetchOrders() {
    const res = await fetch(`/api/orders?buyerId=${encodeURIComponent(buyerId)}`);
    const data = await res.json();
    state.ordersById = Object.fromEntries(data.orders.map(o => [o.id, o]));
    render();
  }

  function render() {
    const groups = { TO_PAY:[], TO_SHIP:[], TO_RECEIVE:[], COMPLETED:[], RETURN_REFUND:[], CANCELLED:[] };
    Object.values(state.ordersById).forEach(o => groups[tabOf(o)].push(o));
    for (const [k, arr] of Object.entries(groups)) {
      const badge = document.getElementById(`count-${k}`); if (badge) badge.textContent = arr.length;
    }
    const orders = groups[state.tab];
    listEl.innerHTML = '';
    if (!orders.length) {
      listEl.innerHTML = `<div class="small">No orders.</div>`; return;
    }
    for (const o of orders) listEl.appendChild(orderCard(o));
  }

  function orderCard(order) {
    const card = document.createElement('div'); card.className = 'card';
    const total = (order.total || 0).toFixed(2);
    const statusText = order.last_status_msg || '';
    const tab = tabOf(order);
    card.innerHTML = `
      <div class="card-head">
        <div>
          <div class="pill">${labelOf(tab)}</div>
          <div class="status">${escapeHtml(statusText)}</div>
        </div>
        <div class="status small">Order ID: ${order.id.slice(0,8)}</div>
      </div>
      <div class="items">
        ${order.items.map(it => `<div class="item"><div>${escapeHtml(it.name)} x ${it.qty}</div><div>$${(it.qty*it.price).toFixed(2)}</div></div>`).join('')}
      </div>
      <div class="card-foot">
        <div class="small">Payment: ${order.payment_method}</div>
        <div class="small">Total: $${total}</div>
      </div>
      <div class="actions"></div>
      ${debug ? debugPanel(order) : ''}
    `;
    const actions = card.querySelector('.actions');
    if (tab === 'TO_PAY') {
      const cancelBtn = btn('Cancel Order', () => openCancelModal(order));
      actions.append(cancelBtn);
    }
    if (tab === 'TO_RECEIVE') {
      const completedBtn = primBtn('Mark as Completed', () => completeOrder(order));
      actions.append(completedBtn);
    }
    if (tab === 'COMPLETED' && order.return_status !== 'REQUESTED') {
      const rrBtn = btn('Return / Refund', () => openReturnModal(order));
      actions.append(rrBtn);
    }
    return card;
  }

  function labelOf(tab) {
    return ({ TO_PAY: 'To Pay', TO_SHIP: 'To Ship', TO_RECEIVE: 'Out for Delivery', COMPLETED: 'Completed', RETURN_REFUND: 'Return / Refund', CANCELLED: 'Cancelled' })[tab] || tab;
  }

  function btn(text, onClick) { const b = document.createElement('button'); b.className='btn'; b.textContent=text; b.onclick=onClick; return b; }
  function primBtn(text, onClick) { const b = btn(text, onClick); b.classList.add('primary'); return b; }

  function debugPanel(order) {
    return `<div class="debug small">
      <div><strong>Debug</strong></div>
      <div>
        ${order.status==='TO_PAY'?`<button class='btn' data-act='seller-process' data-id='${order.id}'>Seller: Process</button>`:''}
        ${order.status==='TO_SHIP'?`<button class='btn' data-act='rider-pickup' data-id='${order.id}'>Rider: Pickup</button>`:''}
        ${order.status==='OUT_FOR_DELIVERY'?`<button class='btn' data-act='rider-intransit' data-id='${order.id}'>Update: On the way</button>`:''}
      </div>
    </div>`;
  }

  listEl.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-act]'); if (!btn) return;
    const id = btn.dataset.id; const act = btn.dataset.act;
    if (act==='seller-process') post(`/api/orders/${id}/seller/process`);
    if (act==='rider-pickup') post(`/api/orders/${id}/rider/pickup`);
    if (act==='rider-intransit') post(`/api/orders/${id}/rider/in_transit`);
  });

  async function completeOrder(order) {
    await post(`/api/orders/${order.id}/complete`);
  }

  function openCancelModal(order) {
    const modal = document.createElement('div'); modal.className='modal-backdrop';
    modal.innerHTML = `
      <div class='modal'>
        <h3>Cancel Order</h3>
        <div class='row small'>Choose one reason:</div>
        <form id='cancelForm'>
          ${['Ordered by mistake','Change of mind','Found a cheaper price','Wrong item ordered','Seller took too long to process','Other reasons'].map((r,i)=>
            `<label style='display:block;margin:6px 0;'><input type='radio' name='reason' value='${r}' ${i===0?'checked':''}/> ${r}</label>`).join('')}
          <footer>
            <button type='button' class='btn' id='keepBtn'>Keep Order</button>
            <button type='submit' class='btn primary'>Submit Cancellation</button>
          </footer>
        </form>
      </div>`;
    modalRoot.appendChild(modal);
    modal.querySelector('#keepBtn').onclick = () => modal.remove();
    modal.querySelector('#cancelForm').onsubmit = async (e) => {
      e.preventDefault();
      const reason = new FormData(e.target).get('reason');
      try { await post(`/api/orders/${order.id}/cancel`, { reason }); toast('Your order has been cancelled.'); }
      catch (err) { toast(err.message || 'Cancel failed'); }
      finally { modal.remove(); }
    };
  }

  function openReturnModal(order) {
    const modal = document.createElement('div'); modal.className='modal-backdrop';
    modal.innerHTML = `
      <div class='modal'>
        <h3>Return / Refund</h3>
        <form id='rrForm'>
          <div class='row'>
            <label class='small'>Reason for return</label>
            <select name='reason' required>
              <option value='Wrong item received'>Wrong item received</option>
              <option value='Damaged item'>Damaged item</option>
              <option value='Missing items / Incomplete'>Missing items / Incomplete</option>
              <option value='Not as described'>Not as described</option>
              <option value='Change of mind'>Change of mind</option>
              <option value='Other'>Other</option>
            </select>
          </div>
          <div class='row'>
            <label class='small'>Upload photos/videos (max 6)</label>
            <input type='file' name='media' multiple accept='image/*,video/*' />
          </div>
          <div class='row'>
            <label class='small'>Explanation</label>
            <textarea name='explanation' placeholder='Tell the seller what went wrong'></textarea>
          </div>
          <footer>
            <button type='button' class='btn' id='closeRR'>Close</button>
            <button type='submit' class='btn primary'>Submit</button>
          </footer>
        </form>
      </div>`;
    modalRoot.appendChild(modal);
    modal.querySelector('#closeRR').onclick = () => modal.remove();
    modal.querySelector('#rrForm').onsubmit = async (e) => {
      e.preventDefault();
      const fd = new FormData(e.target);
      try {
        const res = await fetch(`/api/orders/${order.id}/return`, { method:'POST', body: fd });
        const data = await res.json(); if (!res.ok) throw new Error(data.error||'Submit failed');
        toast('Your return/refund request has been sent to the seller.');
      } catch (err) { toast(err.message); }
      finally { modal.remove(); }
    };
  }

  async function post(url, json) {
    const opts = json ? { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(json) } : { method:'POST' };
    const res = await fetch(url, opts);
    const data = await res.json().catch(()=>({}));
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
  }

  function escapeHtml(s) {
    return String(s||'').replace(/[&<>"']/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;' }[c]));
  }

  fetchOrders();
})();
