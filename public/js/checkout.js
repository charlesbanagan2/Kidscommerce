(function(){
  function money(n){ return `₱${n.toFixed(2)}`; }

  const params = new URLSearchParams(location.search);
  const idsParam = params.get('ids') || '';
  const buyerId = params.get('buyerId') || localStorage.getItem('buyerId') || 'buyer-1';
  const cartItemIds = idsParam.split(',').filter(Boolean);

  const listEl = document.getElementById('summary-list');
  const subtotalEl = document.getElementById('subtotal');
  const shippingEl = document.getElementById('shipping');
  const totalEl = document.getElementById('grand-total');
  const placeBtn = document.getElementById('place-order-btn');
  const errorEl = document.getElementById('error');

  async function loadQuote(){
    if (cartItemIds.length === 0){
      location.href = '/cart.html';
      return;
    }
    const res = await fetch('/api/checkout/quote', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ buyerId, cartItemIds })
    });
    const data = await res.json();
    if (!res.ok){
      errorEl.style.display = 'block';
      errorEl.textContent = 'Cannot proceed to checkout: ' + (data.invalid?.map(x => `${x.cartItemId}: ${x.reason}`).join(', ') || 'Unknown error');
      placeBtn.disabled = true;
      return;
    }
    render(data);
    placeBtn.disabled = false;
    placeBtn.onclick = () => placeOrder(cartItemIds);
  }

  function render(quote){
    listEl.innerHTML = '';
    for (const li of quote.lineItems){
      const row = document.createElement('div');
      row.className = 'summary-row';
      row.innerHTML = `
        <img class="thumb" src="${li.imageUrl}" alt="" />
        <div class="info">
          <div class="name">${li.name}</div>
          <div class="qty">Qty: ${li.quantity}</div>
        </div>
        <div class="price">${money(li.lineTotal)}</div>
      `;
      listEl.appendChild(row);
    }
    subtotalEl.textContent = money(quote.subtotal);
    shippingEl.textContent = money(quote.shippingFee);
    totalEl.textContent = money(quote.total);
  }

  async function placeOrder(ids){
    placeBtn.disabled = true;
    const res = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ buyerId, cartItemIds: ids })
    });
    const data = await res.json();
    if (!res.ok){
      alert('Failed to place order: ' + (data.error || 'Unknown'));
      placeBtn.disabled = false;
      return;
    }
    alert(`Order placed! Order ID: ${data.order.id}`);
    window.location.href = '/cart.html';
  }

  loadQuote();
})();
