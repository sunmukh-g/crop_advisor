/**
 * Kisan AI - Main JavaScript
 * Handles form interactions, weather fetch, animations
 */

document.addEventListener('DOMContentLoaded', function () {

    // ============================================
    // Navbar Mobile Toggle (PRIORITY)
    // ============================================
    const navToggle = document.getElementById('nav-toggle');
    const navbarWrapper = document.querySelector('.navbar-wrapper');
    const navMenuLinks = document.querySelectorAll('.nav-container-main .nav-link');

    if (navToggle && navbarWrapper) {
        navToggle.addEventListener('click', function() {
            console.log('Navbar toggle clicked'); // Debugging
            navbarWrapper.classList.toggle('navbar--open');
            document.body.classList.toggle('no-scroll');
        });

        navMenuLinks.forEach(link => {
            link.addEventListener('click', () => {
                navbarWrapper.classList.remove('navbar--open');
                document.body.classList.remove('no-scroll');
            });
        });
    }

    // ============================================

    // Submit button loader
    // ============================================
    const form = document.getElementById('crop-form');
    const submitBtn = document.getElementById('submit-btn');

    if (form && submitBtn) {
        form.addEventListener('submit', function (e) {
            const btnText = submitBtn.querySelector('.btn-text');
            const btnLoading = submitBtn.querySelector('.btn-loading');
            if (btnText && btnLoading) {
                btnText.classList.add('hidden');
                btnLoading.classList.remove('hidden');
                submitBtn.disabled = true;
            }
        });
    }

    // ============================================
    // Weather preview on location input
    // ============================================
    const locationInput = document.getElementById('location-input');
    const weatherPreview = document.getElementById('weather-preview');
    const weatherText = document.getElementById('weather-text');

    if (locationInput && weatherPreview) {
        let debounceTimer;
        locationInput.addEventListener('input', function () {
            clearTimeout(debounceTimer);
            const loc = this.value.trim();
            if (loc.length < 3) {
                weatherPreview.classList.add('hidden');
                return;
            }
            debounceTimer = setTimeout(() => {
                weatherPreview.classList.remove('hidden');
                if (weatherText) weatherText.textContent = '🌤 Fetching weather for ' + loc + '...';
                fetch(`/api/weather/?location=${encodeURIComponent(loc)}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.temperature && weatherText) {
                            weatherText.textContent = `🌡 ${data.temperature}°C · ${data.condition} · Humidity: ${data.humidity}% (${data.location_found})`;
                        }
                    })
                    .catch(() => {
                        if (weatherText) weatherText.textContent = '☁ Weather data will be fetched on submission';
                    });
            }, 800);
        });
    }

    // ============================================
    // Soil type info tooltip
    // ============================================
    const soilSelect = document.getElementById('soil-type-select');
    const soilInfo = document.getElementById('soil-info');
    const soilDescriptions = {
        loamy: '✓ Best for most crops — retains moisture, drains well',
        sandy: '⚡ Fast drainage — good for root vegetables, needs frequent irrigation',
        clay: '💧 Holds water well — good for paddy/rice, prone to waterlogging',
        silt: '🌱 Very fertile — excellent for vegetable growing',
        black: '🌾 Ideal for wheat, cotton, soybean — excellent water retention',
        red: '🟤 Good for pulses, groundnut — needs extra fertilizer',
        alluvial: '⭐ Most fertile — suitable for all crops'
    };
    if (soilSelect && soilInfo) {
        soilSelect.addEventListener('change', function () {
            soilInfo.textContent = soilDescriptions[this.value] || '';
        });
        // Trigger on load if value pre-selected
        if (soilSelect.value) soilInfo.textContent = soilDescriptions[soilSelect.value] || '';
    }

    // ============================================
    // Language toggle - Update form labels
    // ============================================
    const langRadios = document.querySelectorAll('.lang-radio');
    langRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            if (this.value === 'hi') {
                document.body.setAttribute('data-lang', 'hi');
            } else {
                document.body.setAttribute('data-lang', 'en');
            }
        });
    });

    // ============================================
    // Crop card intersection observer (results page)
    // ============================================
    const cropCards = document.querySelectorAll('.crop-card');
    if (cropCards.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        cropCards.forEach(card => observer.observe(card));
    }

    // ============================================
    // Calendar - highlight current month
    // ============================================
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'];
    const currentMonth = monthNames[new Date().getMonth()];

    document.querySelectorAll('.calendar-card').forEach(card => {
        const monthEl = card.querySelector('.month-en');
        if (monthEl && monthEl.textContent.trim() === currentMonth) {
            card.style.borderColor = '#f5a623';
            card.style.boxShadow = '0 4px 20px rgba(245, 166, 35, 0.25)';
            const badge = document.createElement('span');
            badge.style.cssText = 'background:#f5a623;color:white;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;display:block;margin-bottom:4px;';
            badge.textContent = '📅 This Month';
            card.insertBefore(badge, card.firstChild);
        }
    });

    // ============================================
    // Page scroll fade-in animation
    // ============================================
    const animateElements = document.querySelectorAll('.step-card, .recent-card, .summary-card');
    const fadeObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, i * 100);
                fadeObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        fadeObserver.observe(el);
    });

    // ============================================
    // Download button loading state
    // ============================================
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function () {
            const orig = this.innerHTML;
            this.innerHTML = '<div class="spinner" style="width:16px;height:16px;border-width:2px;margin-right:8px;"></div> Generating PDF...';
            this.style.opacity = '0.8';
            setTimeout(() => {
                this.innerHTML = orig;
                this.style.opacity = '1';
            }, 3000);
        });
    }

    // ============================================
    // Navbar hide on scroll down, show on scroll up
    // ============================================
    const navbar = document.querySelector('.navbar-wrapper');
    if (navbar) {
        let lastScrollY = window.scrollY;
        
        window.addEventListener('scroll', () => {
            const currentScrollY = window.scrollY;
            
            if (currentScrollY > lastScrollY && currentScrollY > 100) {
                navbar.classList.add('navbar--hidden');
            } else if (currentScrollY < lastScrollY) {
                navbar.classList.remove('navbar--hidden');
            }
            
            lastScrollY = currentScrollY;
        }, { passive: true });
    }
});



