// ========== SCROLL ANIMATIONS ==========
document.addEventListener('DOMContentLoaded', () => {
    // Re-observe any dynamically added elements
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('visible');
        });
    }, { threshold: 0.1 });

    setTimeout(() => {
        document.querySelectorAll('.reveal, .reveal-right').forEach(el => observer.observe(el));
    }, 300);
});
