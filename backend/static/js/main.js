// Main JavaScript for Kids & Baby Store
/*
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            const alertInstance = new bootstrap.Alert(alert);
            alertInstance.close();
        });
    }, 5000);

    // Cart quantity update handlers
    const cartQuantityButtons = document.querySelectorAll('.quantity-btn');
    cartQuantityButtons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const action = this.dataset.action;
            const productId = this.dataset.productId;
            const quantityInput = document.querySelector(`input[data-product-id="${productId}"]`);
            let currentQuantity = parseInt(quantityInput.value);

            if (action === 'increase') {
                currentQuantity++;
            } else if (action === 'decrease' && currentQuantity > 1) {
                currentQuantity--;
            }

            quantityInput.value = currentQuantity;
            updateCartItem(productId, currentQuantity);
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Search functionality
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="search"]');
        if (searchInput) {
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchForm.submit();
                }
            });
        }
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Image preview for file uploads
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Create or update preview
                    let preview = document.getElementById('image-preview');
                    if (!preview) {
                        preview = document.createElement('img');
                        preview.id = 'image-preview';
                        preview.className = 'img-thumbnail mt-2';
                        preview.style.maxWidth = '200px';
                        input.parentNode.appendChild(preview);
                    }
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Confirmation dialogs for dangerous actions
    const dangerousButtons = document.querySelectorAll('.btn-danger, .btn-outline-danger');
    dangerousButtons.forEach(function(btn) {
        if (btn.textContent.includes('Delete') || btn.textContent.includes('Remove') || btn.textContent.includes('Reject')) {
            btn.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to perform this action?')) {
                    e.preventDefault();
                }
            });
        }
    });

    // Loading states for forms
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                this.disabled = true;
            }
        });
    });

    // Tooltip initialization
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Copy to clipboard functionality
    window.copyToClipboard = function(text) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copied to clipboard!', 'success');
        });
    };

    // Toast notifications
    window.showToast = function(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || createToastContainer();
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    };

    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }
});

// Cart update function
function updateCartItem(productId, quantity) {
    fetch('/update-cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart total
            document.querySelector('.cart-total').textContent = '₱' + data.total.toFixed(2);
            // Update cart count in navbar
            const cartBadge = document.querySelector('.cart-count');
            if (cartBadge) {
                cartBadge.textContent = data.cart_count;
            }
        } else {
            showToast('Error updating cart', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error updating cart', 'danger');
    });
}

// Product search with debouncing
let searchTimeout;
function debounceSearch(input) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        if (input.value.length > 2 || input.value.length === 0) {
            window.location.href = `/shop?search=${encodeURIComponent(input.value)}`;
        }
    }, 500);
}

// Image lazy loading
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', lazyLoadImages);
} else {
    lazyLoadImages();
}

// PayMongo Integration Functions (for future use)
window.PayMongoCheckout = {
    init: function(publicKey) {
        this.publicKey = publicKey;
    },
    
    createCheckoutSession: function(orderData) {
        return fetch('/create-checkout-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        })
        .then(response => response.json());
    },
    
    redirectToCheckout: function(sessionId) {
        // This would redirect to PayMongo checkout page
        window.location.href = `https://checkout.paymongo.com/sessions/${sessionId}`;
    }
};

// Analytics tracking (placeholder)
function trackEvent(eventName, properties = {}) {
    console.log('Event:', eventName, properties);
    // Add your analytics implementation here (Google Analytics, etc.)
}

// Track product views
if (window.location.pathname.includes('/product/')) {
    trackEvent('product_view', {
        product_id: window.location.pathname.split('/').pop(),
        page: window.location.pathname
    });
}

// Track add to cart clicks
document.addEventListener('click', function(e) {
    if (e.target.closest('a[href*="add-to-cart"]')) {
        const productId = e.target.closest('a').href.split('/').pop();
        trackEvent('add_to_cart', { product_id: productId });
    }
});
*/

/**
 * Seller sidebar enhancements (used on seller dashboard pages):
 * - Ensures the active menu item matches data-active-page
 * - Allows collapsing the sidebar on mobile, with preference stored in localStorage
 */
(function () {
    document.addEventListener('DOMContentLoaded', function () {
        var sidebarCard = document.querySelector('[data-seller-sidebar]');
        if (!sidebarCard) return;

        // Ensure active link matches data-active-page with smooth transition
        var activePage = sidebarCard.getAttribute('data-active-page');
        if (activePage) {
            var links = sidebarCard.querySelectorAll('.seller-sidebar .list-group-item');
            var target = sidebarCard.querySelector('.seller-sidebar .list-group-item[data-page="' + activePage + '"]');
            if (target) {
                links.forEach(function (link) {
                    if (link !== target) {
                        link.classList.remove('active');
                    }
                });
                // Use a tiny delay to trigger the transition when the class is added
                setTimeout(function () {
                    target.classList.add('active');
                }, 10);
            }
        }

        // Mobile collapse / expand behaviour
        var toggleBtn = sidebarCard.querySelector('[data-sidebar-toggle]');
        if (!toggleBtn) return;

        var COLLAPSE_KEY = 'sellerSidebarCollapsed';
        var isDesktop = function () { return window.innerWidth >= 992; };
        var icon = toggleBtn.querySelector('i');

        var updateIcon = function (collapsed) {
            if (!icon) return;
            icon.style.transition = 'transform 0.24s ease';
            icon.style.transform = collapsed ? 'rotate(180deg)' : 'rotate(0deg)';
            icon.classList.toggle('fa-chevron-left', !collapsed);
            icon.classList.toggle('fa-chevron-right', collapsed);
        };

        var applyState = function (collapsed) {
            if (collapsed && !isDesktop()) {
                sidebarCard.classList.add('is-collapsed');
                toggleBtn.setAttribute('aria-expanded', 'false');
            } else {
                sidebarCard.classList.remove('is-collapsed');
                toggleBtn.setAttribute('aria-expanded', 'true');
            }
            updateIcon(collapsed && !isDesktop());
        };

        // Initialize from saved preference (fallback: collapsed on mobile, expanded on desktop)
        try {
            var stored = localStorage.getItem(COLLAPSE_KEY);
            if (stored === null) {
                var defaultCollapsed = !isDesktop();
                applyState(defaultCollapsed);
            } else {
                applyState(stored === '1');
            }
        } catch (e) {
            var fallbackCollapsed = !isDesktop();
            applyState(fallbackCollapsed);
        }

        toggleBtn.addEventListener('click', function () {
            var collapsed = sidebarCard.classList.toggle('is-collapsed');
            toggleBtn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
            updateIcon(collapsed);
            try {
                localStorage.setItem(COLLAPSE_KEY, collapsed ? '1' : '0');
            } catch (e) {}
        });

        // Keep state consistent on resize
        window.addEventListener('resize', function () {
            var collapsed = sidebarCard.classList.contains('is-collapsed');
            applyState(collapsed);
        });
    });
})();
