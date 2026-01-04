document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });

        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768 && 
                sidebar.classList.contains('open') && 
                !sidebar.contains(e.target) && 
                !menuToggle.contains(e.target)) {
                sidebar.classList.remove('open');
            }
        });
    }

    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.tile').forEach(tile => {
        observer.observe(tile);
    });

    const scrollArrow = document.getElementById('scroll-arrow');
    const heroSection = document.querySelector('.hero');

    if (scrollArrow && heroSection) {
        const scrollToHero = () => {
            heroSection.scrollIntoView({ behavior: 'smooth' });
        };

        scrollArrow.addEventListener('click', scrollToHero);
        
        scrollArrow.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                scrollToHero();
            }
        });
    }
});

window.equalizeTileHeights = function() {
    const tiles = document.querySelectorAll('.tile');
    if (tiles.length === 0) return;

    tiles.forEach(tile => tile.style.height = 'auto');

    let maxHeight = 0;
    tiles.forEach(tile => {
        if (tile.offsetHeight > maxHeight) {
            maxHeight = tile.offsetHeight;
        }
    });

    tiles.forEach(tile => tile.style.height = `${maxHeight}px`);
};

window.addEventListener('load', window.equalizeTileHeights);
window.addEventListener('resize', () => {
    window.equalizeTileHeights();
});
