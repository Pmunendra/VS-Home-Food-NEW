// ========== NAVBAR ==========
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
    if (window.scrollY > 50) navbar?.classList.add('scrolled');
    else navbar?.classList.remove('scrolled');
});

// Hamburger
document.getElementById('hamburger')?.addEventListener('click', () => {
    document.getElementById('mobileMenu')?.classList.add('open');
    document.getElementById('overlay')?.classList.add('active');
});
document.getElementById('mobileClose')?.addEventListener('click', closeMenus);

// Cart Toggle
document.getElementById('cartToggleBtn')?.addEventListener('click', () => {
    document.getElementById('cartSidebar')?.classList.add('open');
    document.getElementById('overlay')?.classList.add('active');
});
document.getElementById('cartCloseBtn')?.addEventListener('click', closeMenus);

// Overlay click
document.getElementById('overlay')?.addEventListener('click', closeMenus);

function closeMenus() {
    document.getElementById('mobileMenu')?.classList.remove('open');
    document.getElementById('cartSidebar')?.classList.remove('open');
    document.getElementById('overlay')?.classList.remove('active');
}

// Search toggle
document.getElementById('navSearchBtn')?.addEventListener('click', () => {
    const bar = document.getElementById('navSearchBar');
    bar?.classList.toggle('active');
    if (bar?.classList.contains('active')) document.getElementById('navSearchInput')?.focus();
});

// ========== SCROLL REVEAL ==========
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, { threshold: 0.15 });

document.querySelectorAll('.reveal, .reveal-right').forEach(el => revealObserver.observe(el));

// ========== SMOOTH SCROLL FOR ANCHOR LINKS ==========
document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
        const target = document.querySelector(link.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            closeMenus();
        }
    });
});

// ========== ACTIVE NAV LINK ==========
const currentPath = window.location.pathname;
document.querySelectorAll('.nav-link').forEach(link => {
    if (link.getAttribute('href') === currentPath) link.classList.add('active');
});

// ========== PAYMENT OPTION SELECTION ==========
document.querySelectorAll('.payment-option').forEach(opt => {
    opt.addEventListener('click', () => {
        document.querySelectorAll('.payment-option').forEach(o => o.classList.remove('active'));
        opt.classList.add('active');
    });
});
