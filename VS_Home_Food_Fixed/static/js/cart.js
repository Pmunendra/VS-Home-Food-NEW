// ============================================================
//  CART UI LOGIC
//  Fixed: sidebar ID mismatch, total ID mismatch, image display,
//         cart-page rendering, open-time refresh, timing issues
// ============================================================

let PRODUCTS = [];

// ── Fetch products from API ──────────────────────────────────
async function loadProducts() {
    try {
        const res  = await fetch('/api/products');
        const data = await res.json();
        if (data.success) {
            PRODUCTS = data.products;
            console.log('[cart.js] Loaded', PRODUCTS.length, 'products');
        }
    } catch (e) {
        console.error('[cart.js] Failed to load products:', e);
    }
}

// ── RENDER PRODUCT CARD ──────────────────────────────────────
function renderProductCard(product) {
    const cart    = Storage.getCart();
    const sel     = document.getElementById(`weight-${product.id}`);
    const weight  = sel?.value || (product.variants?.[0]?.label || '');
    const inCart  = cart.find(i => String(i.id) === String(product.id) && i.weight === weight);
    const inStock = product.in_stock !== false && product.status !== 'out_of_stock';

    const badge    = product.badge
        ? `<div class="product-badge ${product.badge.toLowerCase() === 'bestseller' ? 'bestseller' : ''}">${product.badge}</div>` : '';
    const vegBadge = product.is_veg
        ? '<div class="product-badge veg" style="right:12px;left:auto;">🌿 Veg</div>' : '';
    const oosOverlay = !inStock
        ? `<div class="oos-overlay" style="position:absolute;inset:0;background:rgba(0,0,0,0.45);display:flex;align-items:center;justify-content:center;border-radius:0;"><span style="background:#DC2626;color:white;font-size:12px;font-weight:700;padding:5px 14px;border-radius:50px;">Out of Stock</span></div>` : '';

    const imgContent = product.image_file
        ? `<img src="/static/images/products/${product.image_file}" alt="${product.name}" style="width:100%;height:100%;object-fit:cover;">`
        : `<span style="font-size:52px;">${product.emoji || '🍱'}</span>`;

    const variants = product.variants || [];
    let variantSelect = '';
    if (variants.length > 0) {
        const opts = variants.map(v =>
            `<option value="${v.label}" data-price="${v.price}">${v.label} — ₹${v.price}</option>`
        ).join('');
        variantSelect = `<select class="weight-select" id="weight-${product.id}" onchange="updateVariantPrice(${product.id})">${opts}</select>`;
    }

    const basePrice = variants.length > 0 ? variants[0].price : product.price;

    let cartControl;
    if (!inStock) {
        cartControl = `<button class="add-to-cart-btn oos-btn" disabled style="background:#9CA3AF;cursor:not-allowed;font-size:11px;padding:8px 14px;">Out of Stock</button>`;
    } else if (inCart) {
        cartControl = `<div class="qty-control">
            <button class="qty-btn" onclick="updateCartQty(${product.id}, -1)">−</button>
            <span class="qty-num">${inCart.qty}</span>
            <button class="qty-btn" onclick="updateCartQty(${product.id}, 1)">+</button>
        </div>`;
    } else {
        cartControl = `<button class="add-to-cart-btn" onclick="addToCart(${product.id})">+</button>`;
    }

    return `
    <div class="product-card fade-in" data-id="${product.id}" data-category="${product.category || ''}">
        <div class="product-card-img" style="position:relative;">
            ${badge}${vegBadge}${imgContent}${oosOverlay}
        </div>
        <div class="product-card-body">
            <div class="product-category">${product.category || ''}</div>
            <h3 class="product-name"><a href="/product/${product.id}">${product.name}</a></h3>
            <p class="product-desc">${product.description || ''}</p>
            ${variantSelect}
            <div class="product-footer">
                <div>
                    <span class="product-price" id="price-display-${product.id}">₹${basePrice}</span>
                </div>
                ${cartControl}
            </div>
        </div>
    </div>`;
}

// ── Update price when variant changes ────────────────────────
function updateVariantPrice(productId) {
    const sel = document.getElementById(`weight-${productId}`);
    if (!sel) return;
    const price = sel.options[sel.selectedIndex]?.dataset?.price;
    const el    = document.getElementById(`price-display-${productId}`);
    if (el && price) el.textContent = `₹${price}`;
}

// ── ADD TO CART ──────────────────────────────────────────────
function addToCart(id) {
    const product = PRODUCTS.find(p => String(p.id) === String(id));
    if (!product) { console.warn('[cart.js] Product not found:', id); return; }

    const inStock = product.in_stock !== false && product.status !== 'out_of_stock';
    if (!inStock) {
        showCartToast(`${product.name} is currently out of stock.`, false);
        return;
    }

    const sel      = document.getElementById(`weight-${id}`);
    const variants = product.variants || [];
    let weight = variants.length > 0 ? (variants[0].label || '') : '';
    let price  = variants.length > 0 ? variants[0].price : product.price;

    if (sel) {
        weight = sel.value;
        price  = parseFloat(sel.options[sel.selectedIndex]?.dataset?.price) || price;
    }

    Storage.addItem({
        id:         product.id,
        name:       product.name,
        emoji:      product.emoji      || '🍱',
        image_file: product.image_file || '',
        image_url:  product.image_url  || '',
        price,
        weight
    });

    updateCartUI();
    refreshProductCard(id);
    showCartToast(`${product.name} added to cart!`, true);
}

// ── UPDATE QUANTITY on product card ──────────────────────────
function updateCartQty(id, delta) {
    const strId  = String(id);
    const cart   = Storage.getCart();
    const selEl  = document.getElementById(`weight-${id}`);
    // Try selected weight first; fall back to any matching item
    let item = selEl
        ? cart.find(i => String(i.id) === strId && i.weight === selEl.value)
        : null;
    if (!item) item = cart.find(i => String(i.id) === strId);
    if (!item) return;

    Storage.updateQty(strId, item.weight, item.qty + delta);
    updateCartUI();
    refreshProductCard(id);
}

// ── Re-render a single product card control ──────────────────
function refreshProductCard(id) {
    document.querySelectorAll(`[data-id="${id}"]`).forEach(card => {
        const newCart  = Storage.getCart();
        const selEl    = document.getElementById(`weight-${id}`);
        const w        = selEl ? selEl.value : '';
        const newItem  = newCart.find(i => String(i.id) === String(id) && i.weight === w)
                      || newCart.find(i => String(i.id) === String(id));
        const footer   = card.querySelector('.product-footer > :last-child');
        if (!footer) return;

        if (newItem) {
            footer.outerHTML = `<div class="qty-control">
                <button class="qty-btn" onclick="updateCartQty(${id}, -1)">−</button>
                <span class="qty-num">${newItem.qty}</span>
                <button class="qty-btn" onclick="updateCartQty(${id}, 1)">+</button>
            </div>`;
        } else {
            footer.outerHTML = `<button class="add-to-cart-btn" onclick="addToCart(${id})">+</button>`;
        }
    });
}

// ── TOAST NOTIFICATION ───────────────────────────────────────
function showCartToast(message, success = true) {
    const existing = document.getElementById('cartAddToast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'cartAddToast';
    toast.style.cssText = `
        position:fixed;bottom:24px;right:24px;z-index:99999;
        background:${success ? '#059669' : '#DC2626'};color:white;
        padding:14px 24px;border-radius:50px;
        font-size:14px;font-weight:600;
        box-shadow:0 4px 20px rgba(0,0,0,0.2);
        display:flex;align-items:center;gap:8px;
        animation:slideUpFade 0.3s ease forwards;
        max-width:320px;`;
    toast.innerHTML = `${success ? '✅' : '❌'} ${message}`;
    document.body.appendChild(toast);

    if (!document.getElementById('_toastCSS')) {
        const s = document.createElement('style');
        s.id = '_toastCSS';
        s.textContent = `@keyframes slideUpFade{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}`;
        document.head.appendChild(s);
    }
    setTimeout(() => {
        toast.style.cssText += 'opacity:0;transition:opacity 0.3s ease;';
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

// ── BUILD SIDEBAR ITEM HTML ───────────────────────────────────
function buildSidebarItemHTML(item) {
    const imgHTML = item.image_file
        ? `<img src="/static/images/products/${item.image_file}" alt="${item.name}"
               style="width:44px;height:44px;object-fit:cover;border-radius:8px;flex-shrink:0;">`
        : `<span style="font-size:28px;width:44px;height:44px;display:flex;align-items:center;justify-content:center;background:#FDF6EE;border-radius:8px;flex-shrink:0;">${item.emoji || '🍱'}</span>`;

    const subtotal = Math.round(parseFloat(item.price) * parseInt(item.qty));
    // Escape for inline onclick
    const safeId     = String(item.id).replace(/'/g, "\\'");
    const safeWeight = (item.weight || '').replace(/'/g, "\\'");

    return `
    <div class="sidebar-cart-item" style="display:flex;align-items:center;gap:10px;padding:12px 0;border-bottom:1px solid #F5EDE0;">
        ${imgHTML}
        <div style="flex:1;min-width:0;">
            <div style="font-size:13px;font-weight:600;color:#1A1A1A;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${item.name}</div>
            ${item.weight ? `<div style="font-size:11px;color:#888;margin-top:1px;">${item.weight}</div>` : ''}
            <div style="font-size:12px;color:#E8471A;font-weight:600;margin-top:2px;">₹${item.price} × ${item.qty} = <strong>₹${subtotal}</strong></div>
        </div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:4px;">
            <div style="display:flex;align-items:center;gap:4px;">
                <button onclick="sidebarQtyChange('${safeId}','${safeWeight}',-1)"
                    style="width:22px;height:22px;border-radius:50%;border:1.5px solid #E8471A;background:white;color:#E8471A;font-size:14px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;line-height:1;">−</button>
                <span style="font-size:13px;font-weight:700;min-width:16px;text-align:center;">${item.qty}</span>
                <button onclick="sidebarQtyChange('${safeId}','${safeWeight}',1)"
                    style="width:22px;height:22px;border-radius:50%;border:1.5px solid #E8471A;background:#E8471A;color:white;font-size:14px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;line-height:1;">+</button>
            </div>
            <button onclick="sidebarRemove('${safeId}','${safeWeight}')"
                style="background:none;border:none;color:#aaa;font-size:11px;cursor:pointer;padding:0;">✕ Remove</button>
        </div>
    </div>`;
}

// ── SIDEBAR HELPERS (called from inline onclick) ─────────────
function sidebarRemove(id, weight) {
    Storage.removeItem(id, weight);
    updateCartUI();
}
function sidebarQtyChange(id, weight, delta) {
    const cart = Storage.getCart();
    const item = cart.find(i => String(i.id) === String(id) && i.weight === weight);
    if (!item) return;
    Storage.updateQty(id, weight, item.qty + delta);
    updateCartUI();
    refreshProductCard(id);
}

// ── MAIN CART UI UPDATE ──────────────────────────────────────
function updateCartUI() {
    const cart     = Storage.getCart();
    const count    = Storage.getCount();
    const subtotal = Storage.getTotal();
    const delivery = subtotal > 0 ? 40 : 0;
    const total    = subtotal + delivery;

    console.log('[updateCartUI] items:', cart.length, '| qty:', count, '| subtotal: ₹', subtotal);

    // ── Badges ──
    ['cartBadge', 'mobileCartBadge'].forEach(id => {
        const el = document.getElementById(id);
        if (el) { el.textContent = count; el.style.display = count > 0 ? 'flex' : 'none'; }
    });

    // ── Sidebar body  (id="cartItemsContainer" in sidebar-cart.html) ──
    const sidebarBody = document.getElementById('cartItemsContainer');
    const cartEmpty   = document.getElementById('cartEmpty');
    const footer      = document.getElementById('cartSidebarFooter');

    if (sidebarBody) {
        if (cart.length === 0) {
            // Show empty state, hide injected items
            if (cartEmpty) cartEmpty.style.display = 'block';
            // Remove any previously injected items list
            const injected = document.getElementById('_sidebarItemsList');
            if (injected) injected.remove();
            if (footer) footer.style.display = 'none';
        } else {
            // Hide empty state
            if (cartEmpty) cartEmpty.style.display = 'none';

            // Build or replace items list
            let listEl = document.getElementById('_sidebarItemsList');
            if (!listEl) {
                listEl = document.createElement('div');
                listEl.id = '_sidebarItemsList';
                listEl.style.cssText = 'overflow-y:auto;max-height:calc(100vh - 280px);padding:0 16px;';
                sidebarBody.appendChild(listEl);
            }

            listEl.innerHTML = cart.map(item => buildSidebarItemHTML(item)).join('');
            if (footer) footer.style.display = 'block';
        }
    }

    // ── Sidebar totals (ids in sidebar-cart.html) ──
    const sidebarSubEl  = document.getElementById('sidebarSubtotal');
    const sidebarDelEl  = document.getElementById('sidebarDelivery');
    const sidebarTotEl  = document.getElementById('sidebarTotal');
    if (sidebarSubEl) sidebarSubEl.textContent = `₹${subtotal}`;
    if (sidebarDelEl) sidebarDelEl.textContent  = delivery > 0 ? `₹${delivery}` : 'Free';
    if (sidebarTotEl) sidebarTotEl.textContent  = `₹${total}`;

    // ── Also update checkout/cart page totals if present ──
    ['cartSubtotal','summarySubtotal','pageSubtotal'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = `₹${subtotal}`;
    });
    ['cartTotal','summaryTotal','pageTotal'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = `₹${total}`;
    });

    // ── Cart page (cart.html) ──
    if (document.getElementById('cartPageItems')) {
        renderCartPage(cart);
    }
}

// ── RENDER CART PAGE ─────────────────────────────────────────
function renderCartPage(cart) {
    // Accept no-arg call (from cart.html extra_js)
    if (cart === undefined) cart = Storage.getCart();

    const pageItems     = document.getElementById('cartPageItems');
    const summarySection = document.getElementById('cartSummarySection');
    if (!pageItems) return;

    if (cart.length === 0) {
        pageItems.innerHTML = `
            <div class="cart-empty-state">
                <span>🍽️</span>
                <h3>Your cart is empty</h3>
                <p>Looks like you haven't added anything yet!</p>
                <a href="/menu" class="btn-primary">Browse Menu</a>
            </div>`;
        if (summarySection) summarySection.style.display = 'none';
        return;
    }

    if (summarySection) summarySection.style.display = 'block';

    pageItems.innerHTML = cart.map(item => {
        const subtotal   = Math.round(parseFloat(item.price) * parseInt(item.qty));
        const imgHTML    = item.image_file
            ? `<img src="/static/images/products/${item.image_file}" alt="${item.name}" style="width:100%;height:100%;object-fit:cover;border-radius:8px;">`
            : `<span style="font-size:36px;">${item.emoji || '🍱'}</span>`;
        const safeId     = String(item.id).replace(/'/g, "\\'");
        const safeWeight = (item.weight || '').replace(/'/g, "\\'");

        return `
        <div class="cart-item">
            <div class="cart-item-emoji" style="overflow:hidden;">${imgHTML}</div>
            <div class="cart-item-info">
                <div class="cart-item-name">${item.name}</div>
                ${item.weight ? `<div class="cart-item-weight">${item.weight}</div>` : ''}
                <div class="cart-item-price">₹${item.price}</div>
            </div>
            <div class="cart-item-actions">
                <div class="qty-control">
                    <button class="qty-btn" onclick="sidebarQtyChange('${safeId}','${safeWeight}',-1)">−</button>
                    <span class="qty-num">${item.qty}</span>
                    <button class="qty-btn" onclick="sidebarQtyChange('${safeId}','${safeWeight}',1)">+</button>
                </div>
                <div style="font-size:15px;font-weight:700;color:#E8471A;">₹${subtotal}</div>
                <button class="cart-remove-btn" onclick="sidebarRemove('${safeId}','${safeWeight}')">✕ Remove</button>
            </div>
        </div>`;
    }).join('');

    // Update summary amounts
    const subtotal = Storage.getTotal();
    const delivery = 40;
    const el = id => document.getElementById(id);
    if (el('pageSubtotal')) el('pageSubtotal').textContent = `₹${subtotal}`;
    if (el('pageDelivery')) el('pageDelivery').textContent = `₹${delivery}`;
    if (el('pageTotal'))    el('pageTotal').textContent    = `₹${subtotal + delivery}`;
}

// ── RENDER MENU PAGE ─────────────────────────────────────────
async function renderMenuPage() {
    const grid = document.getElementById('menuGrid');
    if (!grid) return;
    grid.innerHTML = '<div style="text-align:center;padding:60px;color:#888;">Loading menu...</div>';
    await loadProducts();
    if (PRODUCTS.length === 0) {
        grid.innerHTML = '<div style="text-align:center;padding:60px;color:#888;">No products available yet.</div>';
        return;
    }
    grid.innerHTML = PRODUCTS.map(p => renderProductCard(p)).join('');
    updateCartUI();
    setupMenuFilters();
}

// ── MENU FILTERS ─────────────────────────────────────────────
function setupMenuFilters() {
    const tabs   = document.querySelectorAll('.filter-tab');
    const search = document.getElementById('menuSearchInput');
    const sort   = document.getElementById('sortSelect');
    let currentCat  = 'all', currentQ = '', currentSort = 'default';

    function applyFilters() {
        let filtered = [...PRODUCTS];
        if (currentCat !== 'all') filtered = filtered.filter(p => p.category === currentCat);
        if (currentQ) {
            const q = currentQ.toLowerCase();
            filtered = filtered.filter(p =>
                p.name.toLowerCase().includes(q) || (p.description || '').toLowerCase().includes(q)
            );
        }
        if (currentSort === 'price-low')  filtered.sort((a, b) => a.price - b.price);
        if (currentSort === 'price-high') filtered.sort((a, b) => b.price - a.price);

        const grid   = document.getElementById('menuGrid');
        const noRes  = document.getElementById('noResults');
        grid.innerHTML = filtered.length
            ? filtered.map(p => renderProductCard(p)).join('')
            : '';
        if (noRes) noRes.style.display = filtered.length ? 'none' : 'block';
        updateCartUI();
    }

    tabs.forEach(tab => tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentCat = tab.dataset.filter;
        applyFilters();
    }));
    if (search) search.addEventListener('input', e => { currentQ = e.target.value; applyFilters(); });
    if (sort)   sort.addEventListener('change', e => { currentSort = e.target.value; applyFilters(); });
}

// ── INIT ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    console.log('[cart.js] Init...');
    await loadProducts();
    updateCartUI();
    console.log('[cart.js] Ready. Cart:', Storage.getCount(), 'items');
});
