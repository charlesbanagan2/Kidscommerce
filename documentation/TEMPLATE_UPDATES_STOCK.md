# TEMPLATE UPDATES FOR STOCK DISPLAY

## 1. Product Detail Template (product_detail.html)

Replace the stock display section with:

```jinja2
{# Calculate available stock #}
{% set available_stock = product.stock - (product.reserved_stock or 0) %}

<div class="mb-3 small">
    <span class="me-2">Stock:</span>
    {% if available_stock > 0 %}
      <span class="badge bg-success">In stock</span>
      <span class="text-muted ms-1">({{ available_stock }} available)</span>
      <span class="text-muted ms-1" style="font-size: 0.85em;">
        [Total: {{ product.stock }}, Reserved: {{ product.reserved_stock or 0 }}]
      </span>
    {% else %}
      <span class="badge bg-danger">Out of Stock</span>
      <span class="text-muted ms-1">All items reserved or sold</span>
    {% endif %}
</div>

<!-- Out of Stock Label on Product Image -->
{% if available_stock <= 0 %}
<div class="product-image-sold-out">
    <span>Out of Stock</span>
</div>
{% endif %}

{% if session.user_role == 'admin' %}
    <div class="alert alert-secondary mb-3">
        <i class="fas fa-eye me-2"></i>Admin accounts are view-only. Shopping actions are disabled.
    </div>
{% elif session.user_id %}
    {% if available_stock > 0 %}
    <div class="purchase-row d-flex align-items-center flex-wrap gap-3 mb-3">
        <div class="input-group input-group-sm qty-group" style="width: 160px;">
            <button class="btn btn-outline-secondary" id="qtyMinus" type="button">-</button>
            <input id="qtyInput" type="number" class="form-control text-center" 
                   min="1" max="{{ available_stock }}" value="1">
            <button class="btn btn-outline-secondary" id="qtyPlus" type="button">+</button>
        </div>
        <a id="addToCartBtn" href="{{ url_for('add_to_cart', product_id=product.id) }}" 
           data-product-id="{{ product.id }}" class="btn btn-success flex-fill">
            <i class="fas fa-cart-plus me-2"></i><span class="btn-text">Add to Cart</span>
        </a>
        <a id="buyNowBtn" href="{{ url_for('buy_now', product_id=product.id) }}" 
           class="btn btn-warning flex-fill">
            <i class="fas fa-bolt me-2"></i>Buy Now
        </a>
    </div>
    {% else %}
    <div class="sold-out-minimal">
        <div class="sold-out-label">
            <span>Out of Stock</span>
        </div>
        <p class="sold-out-text">All items have been reserved or sold. Check back later for restocking.</p>
        <div class="sold-out-actions">
            <button class="btn btn-sm btn-outline-secondary" onclick="continueShopping()">
                <i class="fas fa-arrow-left me-2"></i>Continue Shopping
            </button>
        </div>
    </div>
    {% endif %}
{% else %}
    <div class="alert alert-info mb-3">
        <i class="fas fa-info-circle me-2"></i>
        <a href="{{ url_for('login') }}" class="text-decoration-none">Login</a> to add or buy this item.
    </div>
{% endif %}
```

Add this JavaScript for real-time updates:

```javascript
<script>
// Real-time stock updates
if (typeof socket !== 'undefined') {
    socket.on('product_stock_update', function(data) {
        const productId = data.product_id;
        const available = data.available_stock;
        const currentProductId = '{{ product.id }}';
        
        if (productId == currentProductId) {
            updateStockDisplay(available, data.stock, data.reserved_stock);
        }
    });
    
    socket.on('product_price_update', function(data) {
        const productId = data.product_id;
        const newPrice = data.price;
        const currentProductId = '{{ product.id }}';
        
        if (productId == currentProductId) {
            updatePriceDisplay(newPrice);
        }
    });
}

function updateStockDisplay(available, total, reserved) {
    const stockBadge = document.querySelector('.badge.bg-success, .badge.bg-danger');
    const stockText = document.querySelector('.text-muted.ms-1');
    
    if (stockBadge && stockText) {
        if (available > 0) {
            stockBadge.className = 'badge bg-success';
            stockBadge.textContent = 'In stock';
            stockText.innerHTML = `(${available} available) <span class="text-muted ms-1" style="font-size: 0.85em;">[Total: ${total}, Reserved: ${reserved}]</span>`;
            
            // Show purchase buttons
            const purchaseRow = document.querySelector('.purchase-row');
            const soldOutMinimal = document.querySelector('.sold-out-minimal');
            if (purchaseRow) purchaseRow.style.display = 'flex';
            if (soldOutMinimal) soldOutMinimal.style.display = 'none';
            
            // Update quantity input max
            const qtyInput = document.getElementById('qtyInput');
            if (qtyInput) {
                qtyInput.max = available;
                qtyInput.value = Math.min(parseInt(qtyInput.value) || 1, available);
            }
        } else {
            stockBadge.className = 'badge bg-danger';
            stockBadge.textContent = 'Out of Stock';
            stockText.textContent = 'All items reserved or sold';
            
            // Hide purchase buttons
            const purchaseRow = document.querySelector('.purchase-row');
            const soldOutMinimal = document.querySelector('.sold-out-minimal');
            if (purchaseRow) purchaseRow.style.display = 'none';
            if (soldOutMinimal) soldOutMinimal.style.display = 'block';
        }
    }
}

function updatePriceDisplay(newPrice) {
    const priceEl = document.querySelector('.product-price');
    if (priceEl) {
        priceEl.textContent = '₱' + newPrice.toFixed(2);
        
        // Show price update notification
        showMessage('Price updated to ₱' + newPrice.toFixed(2), 'info');
    }
}
</script>
```

## 2. Shop Template (shop.html)

Replace product card stock display:

```jinja2
{% for product in products %}
<div class="p-card">
    <a href="{{ url_for('product_detail', product_id=product.id) }}" class="p-card__inner-link">
        {% if product.image_filename %}
        <div class="p-card__media">
            <img src="{{ url_for('static', filename='uploads/' ~ product.image_filename) }}" 
                 alt="{{ product.name }}">
            {% set available_stock = product.stock - (product.reserved_stock or 0) %}
            {% if available_stock <= 0 %}
            <div class="product-image-sold-out">
                <span>Out of Stock</span>
            </div>
            {% endif %}
        </div>
        {% else %}
        <div class="p-card__media">
            <div class="p-card__ph"><i class="fas fa-image"></i></div>
        </div>
        {% endif %}

        <div class="p-card__body">
            <div class="small text-muted mb-1 brand-pill">
                <i class="fas fa-store me-1"></i>
                <span>{{ (product.seller.seller_applications[0].store_name if product.seller.seller_applications) or (product.seller.first_name) }}</span>
            </div>
            <div class="p-card__title" title="{{ product.name }}">{{ product.name }}</div>
            <div class="p-card__price-row">
                <span class="p-card__price" data-product-id="{{ product.id }}" data-price="{{ product.price }}">
                    ₱{{ '%.2f'|format(product.price) }}
                </span>
            </div>
        </div>

        <div class="p-card__footer">
            {% set available_stock = product.stock - (product.reserved_stock or 0) %}
            {% if available_stock > 0 %}
                <span class="badge bg-success-subtle text-success border-success p-card__stock" 
                      data-product-id="{{ product.id }}"
                      data-stock="{{ product.stock }}"
                      data-reserved="{{ product.reserved_stock or 0 }}">
                    In stock ({{ available_stock }})
                </span>
            {% else %}
                <span class="badge bg-danger-subtle text-danger border-danger p-card__stock" 
                      data-product-id="{{ product.id }}"
                      data-stock="{{ product.stock }}"
                      data-reserved="{{ product.reserved_stock or 0 }}">
                    Out of Stock
                </span>
            {% endif %}
        </div>
    </a>
</div>
{% endfor %}
```

Add JavaScript for real-time updates:

```javascript
<script>
// Real-time stock and price updates for shop page
if (typeof socket !== 'undefined') {
    socket.on('product_stock_update', function(data) {
        const productId = data.product_id;
        const available = data.available_stock;
        const total = data.stock;
        const reserved = data.reserved_stock;
        
        // Update all product cards with this product ID
        document.querySelectorAll(`[data-product-id="${productId}"].p-card__stock`).forEach(badge => {
            badge.dataset.stock = total;
            badge.dataset.reserved = reserved;
            
            if (available > 0) {
                badge.className = 'badge bg-success-subtle text-success border-success p-card__stock';
                badge.textContent = `In stock (${available})`;
            } else {
                badge.className = 'badge bg-danger-subtle text-danger border-danger p-card__stock';
                badge.textContent = 'Out of Stock';
            }
        });
    });
    
    socket.on('product_price_update', function(data) {
        const productId = data.product_id;
        const newPrice = data.price;
        
        // Update all price displays for this product
        document.querySelectorAll(`[data-product-id="${productId}"].p-card__price`).forEach(priceEl => {
            priceEl.textContent = '₱' + newPrice.toFixed(2);
            priceEl.dataset.price = newPrice;
        });
    });
}
</script>
```

## 3. Cart Template (cart.html)

Add stock validation before checkout:

```jinja2
{% for item in cart_items %}
{% set available_stock = item.product.stock - (item.product.reserved_stock or 0) %}
<tr>
    <td>{{ item.product.name }}</td>
    <td>₱{{ '%.2f'|format(item.product.price) }}</td>
    <td>
        <input type="number" class="form-control" value="{{ item.quantity }}" 
               min="1" max="{{ available_stock }}"
               data-item-id="{{ item.id }}"
               data-available="{{ available_stock }}">
        <small class="text-muted">Available: {{ available_stock }}</small>
    </td>
    <td>₱{{ '%.2f'|format(item.product.price * item.quantity) }}</td>
</tr>
{% endfor %}
```

Add validation JavaScript:

```javascript
<script>
// Validate cart quantities against available stock
document.querySelectorAll('input[data-item-id]').forEach(input => {
    input.addEventListener('change', function() {
        const available = parseInt(this.dataset.available);
        const requested = parseInt(this.value);
        
        if (requested > available) {
            alert(`Only ${available} items available for this product`);
            this.value = available;
        }
    });
});

// Real-time stock updates in cart
if (typeof socket !== 'undefined') {
    socket.on('product_stock_update', function(data) {
        // Update available stock displays in cart
        document.querySelectorAll('input[data-item-id]').forEach(input => {
            const row = input.closest('tr');
            const productId = row.dataset.productId;
            
            if (productId == data.product_id) {
                const available = data.available_stock;
                input.max = available;
                input.dataset.available = available;
                
                const availText = row.querySelector('.text-muted');
                if (availText) {
                    availText.textContent = `Available: ${available}`;
                }
                
                // Adjust quantity if it exceeds available
                if (parseInt(input.value) > available) {
                    input.value = available;
                }
            }
        });
    });
}
</script>
```
