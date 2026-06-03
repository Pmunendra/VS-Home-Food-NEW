// ========== SEARCH FUNCTIONALITY ==========

function initSearch() {
    // Hero search
    const heroInput = document.getElementById('heroSearchInput');
    if (heroInput) {
        heroInput.addEventListener('keydown', e => {
            if (e.key === 'Enter') {
                window.location.href = `/menu?search=${heroInput.value}`;
            }
        });
        document.querySelector('.hero-search-btn')?.addEventListener('click', () => {
            if (heroInput.value.trim()) window.location.href = `/menu?search=${heroInput.value}`;
        });
    }

    // Navbar search
    const navInput = document.getElementById('navSearchInput');
    if (navInput) {
        navInput.addEventListener('keydown', e => {
            if (e.key === 'Enter' && navInput.value.trim()) {
                window.location.href = `/menu?search=${navInput.value}`;
            }
        });
    }

    // Menu page live search
    const menuInput = document.getElementById('menuSearchInput');
    if (menuInput) {
        // Pre-fill from URL param
        const params = new URLSearchParams(window.location.search);
        const q = params.get('search') || params.get('cat') || '';
        if (q) {
            menuInput.value = q;
            setTimeout(() => searchMenu(q), 100);
        }
        menuInput.addEventListener('input', () => searchMenu(menuInput.value));
    }
}

function searchMenu(query) {
    const q = query.toLowerCase().trim();
    const cards = document.querySelectorAll('#menuGrid .product-card');
    let visible = 0;
    cards.forEach(card => {
        const name = card.querySelector('.product-name')?.textContent.toLowerCase() || '';
        const cat = card.dataset.category || '';
        const desc = card.querySelector('.product-desc')?.textContent.toLowerCase() || '';
        const show = !q || name.includes(q) || cat.includes(q) || desc.includes(q);
        card.style.display = show ? '' : 'none';
        if (show) visible++;
    });
    const noResults = document.getElementById('noResults');
    if (noResults) noResults.style.display = visible === 0 ? 'block' : 'none';
}

document.addEventListener('DOMContentLoaded', initSearch);
