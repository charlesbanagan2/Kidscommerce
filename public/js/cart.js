(function(){
  const buyerId = (localStorage.getItem('buyerId') || 'buyer-1');
  localStorage.setItem('buyerId', buyerId);

  const listEl = document.getElementById('cart-list');
  const totalEl = document.getElementById('total-amount');
  const checkoutBtn = document.getElementById('checkout-btn');
  const selectAllEl = document.getElementById('select-all');
  const selectedCountEl = document.getElementById('selected-count');

  let items = []; // joined items from API

  function money(n){ return `₱${n.toFixed(2)}`; }

  async function loadCart(){
    const res = await fetch(`/api/cart?buyerId=${encodeURIComponent(buyerId)}`);
    const data = await res.json();
    items = (data.items || []);
    render();
  }

  function render(){
    listEl.innerHTML = '';
    if(items.length === 0){
      listEl.innerHTML = '<div class="empty">Your cart is empty.</div>';
      updateTotals();
      return;
    }
    for (const it of items){
      const row = document.createElement('div');
      row.className = 'cart-row';
      row.dataset.id = it.id;
      const disabled = !it.selectable;

      row.innerHTML = `
        <label class="check">
          <input type="checkbox" class="item-check" ${disabled ? 'disabled' : ''}>
        </label>
        <img class="thumb" src="${it.product?.imageUrl || ''}" alt="">
        <div class="info">
          <div class="name">${it.product?.name || 'Unknown product'}</div>
          <div class="price">${it.product ? money(it.product.price) : ''}</div>
          ${disabled ? `<div class="warn">${it.notSelectableReason}</div>` : ''}
        </div>
        <div class="qty">
          <button class="qty-btn minus" aria-label="decrease">−</button>
          <input class="qty-input" value="${it.quantity}" inputmode="numeric" />
          <button class="qty-btn plus" aria-label="increase">+</button>
        </div>
        <button class="remove">Remove</button>
      `;

      // set max/min for qty input via dataset
      const qtyInput = row.querySelector('.qty-input');
      qtyInput.min = 1;
      qtyInput.max = it.product?.stock ?? 1;

      // Remove
      row.querySelector('.remove').addEventListener('click', async () => {
        await fetch(`/api/cart/${encodeURIComponent(it.id)}`, { method: 'DELETE' });
        items = items.filter(x => x.id !== it.id);
        render();
      });

      // Quantity controls
      row.querySelector('.minus').addEventListener('click', () => changeQty(it.id, (it.quantity - 1)));
      row.querySelector('.plus').addEventListener('click', () => changeQty(it.id, (it.quantity + 1)));
      qtyInput.addEventListener('change', () => {
        const v = parseInt(qtyInput.value, 10) || it.quantity;
        changeQty(it.id, v);
      });

      // Selection checkbox
      const cb = row.querySelector('.item-check');
      cb.addEventListener('change', updateTotals);

      listEl.appendChild(row);
    }

    wireSelectAll();
    updateTotals();
  }

  function wireSelectAll(){
    selectAllEl.addEventListener('change', () => {
      const all = Array.from(document.querySelectorAll('.item-check'));
      for(const c of all){ if(!c.disabled){ c.checked = selectAllEl.checked; } }
      updateTotals();
    });
  }

  function getSelectedIds(){
    const rows = Array.from(document.querySelectorAll('.cart-row'));
    const ids = [];
    rows.forEach(r => {
      const cb = r.querySelector('.item-check');
      if (cb && cb.checked && !cb.disabled){ ids.push(r.dataset.id); }
    });
    return ids;
  }

  function updateSelectAllState(){
    const checks = Array.from(document.querySelectorAll('.item-check'));
    const enabled = checks.filter(c => !c.disabled);
    const selected = enabled.filter(c => c.checked);
    if (enabled.length === 0){
      selectAllEl.checked = false; selectAllEl.indeterminate = false;
    } else if (selected.length === enabled.length){
      selectAllEl.checked = true; selectAllEl.indeterminate = false;
    } else if (selected.length === 0){
      selectAllEl.checked = false; selectAllEl.indeterminate = false;
    } else {
      selectAllEl.checked = false; selectAllEl.indeterminate = true;
    }
    selectedCountEl.textContent = `${selected.length} selected`;
  }

  function updateTotals(){
    const ids = getSelectedIds();
    let total = 0;
    for (const id of ids){
      const it = items.find(x => x.id === id);
      if (it && it.product){ total += it.product.price * it.quantity; }
    }
    totalEl.textContent = money(total);
    checkoutBtn.disabled = ids.length === 0;
    updateSelectAllState();
  }

  async function changeQty(id, qty){
    if (qty < 1) qty = 1;
    const res = await fetch(`/api/cart/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ quantity: qty })
    });
    if (!res.ok){
      alert('Failed to update quantity');
      return;
    }
    const updated = await res.json();
    // Update local item
    const idx = items.findIndex(x => x.id === id);
    if (idx >= 0){ items[idx] = updated; }
    render();
  }

  checkoutBtn.addEventListener('click', async () => {
    const ids = getSelectedIds();
    if (ids.length === 0) return;
    // Validate via quote before redirect
    const res = await fetch('/api/checkout/quote', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ buyerId, cartItemIds: ids })
    });
    if (!res.ok){
      const data = await res.json().catch(() => ({}));
      const msgs = (data.invalid || []).map(x => `• ${x.cartItemId}: ${x.reason}`).join('\n');
      alert('Some items cannot be checked out:\n' + (msgs || 'Unknown error'));
      // Re-load to refresh states
      await loadCart();
      return;
    }
    const qs = new URLSearchParams({ buyerId, ids: ids.join(',') });
    window.location.href = `/checkout.html?${qs.toString()}`;
  });

  // Initial load
  loadCart();
})();
