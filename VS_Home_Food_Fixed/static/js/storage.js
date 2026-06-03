// ========== LOCALSTORAGE CART MANAGEMENT ==========

const CART_KEY = 'ammavanta_cart';

const Storage = {
    getCart() {
        try {
            const raw = localStorage.getItem(CART_KEY);
            if (!raw) return [];
            const cart = JSON.parse(raw);
            if (!Array.isArray(cart)) return [];
            return cart.filter(item => item && item.id && item.name && item.price !== undefined);
        } catch (e) {
            console.error('[Storage] Error retrieving cart:', e);
            return [];
        }
    },

    saveCart(cart) {
        try {
            const validCart = cart.map(item => ({
                id:         item.id,
                name:       item.name,
                emoji:      item.emoji      || '🍱',
                image_file: item.image_file || '',
                image_url:  item.image_url  || '',
                price:      parseFloat(item.price) || 0,
                weight:     item.weight || '',
                qty:        parseInt(item.qty)   || 1
            }));
            localStorage.setItem(CART_KEY, JSON.stringify(validCart));
            console.log('[Storage] Saved', validCart.length, 'items');
            return validCart;
        } catch (e) {
            console.error('[Storage] Error saving cart:', e);
            return [];
        }
    },

    addItem(item) {
        if (!item.id || !item.name) {
            console.error('[Storage] Invalid item:', item);
            return this.getCart();
        }
        const cart = this.getCart();
        const idx = cart.findIndex(i => String(i.id) === String(item.id) && i.weight === item.weight);
        if (idx > -1) {
            cart[idx].qty += 1;
            console.log('[Storage] Qty++ for:', item.name, '→', cart[idx].qty);
        } else {
            cart.push({
                id:         item.id,
                name:       item.name,
                emoji:      item.emoji      || '🍱',
                image_file: item.image_file || '',
                image_url:  item.image_url  || '',
                price:      parseFloat(item.price) || 0,
                weight:     item.weight || '',
                qty:        1
            });
            console.log('[Storage] Added:', item.name, '| weight:', item.weight, '| Cart size:', cart.length);
        }
        return this.saveCart(cart);
    },

    removeItem(id, weight) {
        const cart = this.getCart().filter(
            i => !(String(i.id) === String(id) && i.weight === weight)
        );
        console.log('[Storage] Removed id:', id, 'weight:', weight, '| Remaining:', cart.length);
        return this.saveCart(cart);
    },

    updateQty(id, weight, qty) {
        const cart = this.getCart();
        const item = cart.find(i => String(i.id) === String(id) && i.weight === weight);
        if (item) {
            if (qty <= 0) return this.removeItem(id, weight);
            item.qty = Math.max(1, parseInt(qty));
        }
        return this.saveCart(cart);
    },

    clearCart() {
        try {
            localStorage.removeItem(CART_KEY);
            console.log('[Storage] Cart cleared');
        } catch (e) {
            console.error('[Storage] Error clearing cart:', e);
        }
    },

    getTotal() {
        return Math.round(
            this.getCart().reduce((sum, i) => sum + (parseFloat(i.price) || 0) * (parseInt(i.qty) || 1), 0)
        );
    },

    getCount() {
        return this.getCart().reduce((sum, i) => sum + (parseInt(i.qty) || 1), 0);
    },

    validateCart() {
        const cart = this.getCart();
        console.log('[Storage] Validate → items:', cart.length, '| qty:', this.getCount(), '| total:', this.getTotal());
        cart.forEach((i, n) => console.log(`  [${n}]`, i.name, '|', i.weight, '| qty:', i.qty, '| price:', i.price));
        return cart;
    }
};
