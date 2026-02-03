// Presentation Script
document.addEventListener('DOMContentLoaded', function() {
    // Set current date
    const dateElement = document.getElementById('currentDate');
    if (dateElement) {
        const today = new Date();
        const options = { year: 'numeric', month: 'long', day: 'numeric' };
        dateElement.textContent = today.toLocaleDateString('en-US', options);
    }

    // Slide navigation
    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const slideCounter = document.getElementById('slideCounter');
    let currentSlide = 0;
    const totalSlides = slides.length;

    // Update slide counter
    function updateCounter() {
        slideCounter.textContent = `${currentSlide + 1} / ${totalSlides}`;
    }

    // Show specific slide
    function showSlide(index) {
        // Remove active class from all slides
        slides.forEach(slide => {
            slide.classList.remove('active');
        });

        // Add active class to current slide
        slides[index].classList.add('active');

        // Update button states
        prevBtn.disabled = index === 0;
        nextBtn.disabled = index === totalSlides - 1;

        // Update counter
        updateCounter();

        // Save current slide to localStorage
        localStorage.setItem('currentSlide', index);
    }

    // Navigate to previous slide
    function prevSlide() {
        if (currentSlide > 0) {
            currentSlide--;
            showSlide(currentSlide);
        }
    }

    // Navigate to next slide
    function nextSlide() {
        if (currentSlide < totalSlides - 1) {
            currentSlide++;
            showSlide(currentSlide);
        }
    }

    // Event listeners for navigation buttons
    prevBtn.addEventListener('click', prevSlide);
    nextBtn.addEventListener('click', nextSlide);

    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        switch(e.key) {
            case 'ArrowLeft':
            case 'ArrowUp':
                prevSlide();
                break;
            case 'ArrowRight':
            case 'ArrowDown':
            case ' ':
                e.preventDefault();
                nextSlide();
                break;
            case 'Home':
                currentSlide = 0;
                showSlide(currentSlide);
                break;
            case 'End':
                currentSlide = totalSlides - 1;
                showSlide(currentSlide);
                break;
        }
    });

    // Touch/swipe support for mobile
    let touchStartX = 0;
    let touchEndX = 0;

    document.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    });

    document.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });

    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe left - next slide
                nextSlide();
            } else {
                // Swipe right - previous slide
                prevSlide();
            }
        }
    }

    // Restore last viewed slide from localStorage
    const savedSlide = localStorage.getItem('currentSlide');
    if (savedSlide !== null) {
        currentSlide = parseInt(savedSlide);
    }

    // Initialize presentation
    showSlide(currentSlide);

    // Add animation to lifecycle items
    const lifecycleItems = document.querySelectorAll('.lifecycle-item');
    lifecycleItems.forEach((item, index) => {
        item.style.animation = `fadeInScale 0.5s ease-out ${index * 0.1}s both`;
    });

    // Add entrance animations to various elements
    const animateOnScroll = () => {
        const elements = document.querySelectorAll('.point-card, .principle-item, .tool-card, .benefit-card, .practice-card');
        
        elements.forEach((element, index) => {
            const rect = element.getBoundingClientRect();
            const isVisible = rect.top < window.innerHeight && rect.bottom >= 0;
            
            if (isVisible && !element.classList.contains('animated')) {
                element.style.animation = `fadeInUp 0.6s ease-out ${index * 0.05}s both`;
                element.classList.add('animated');
            }
        });
    };

    // Listen for scroll events on slide content
    const slideContents = document.querySelectorAll('.slide-content');
    slideContents.forEach(content => {
        content.addEventListener('scroll', animateOnScroll);
    });

    // Trigger animation on slide change
    slides.forEach(slide => {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'class') {
                    if (slide.classList.contains('active')) {
                        animateOnScroll();
                    }
                }
            });
        });

        observer.observe(slide, { attributes: true });
    });

    // Initial animation trigger
    animateOnScroll();

    // Fullscreen toggle (F key)
    document.addEventListener('keydown', function(e) {
        if (e.key === 'f' || e.key === 'F') {
            toggleFullscreen();
        }
    });

    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.log(`Error attempting to enable fullscreen: ${err.message}`);
            });
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }

    // Add progress indicator
    const progressBar = document.createElement('div');
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.3s ease;
        z-index: 10000;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.5);
    `;
    document.body.appendChild(progressBar);

    function updateProgress() {
        const progress = ((currentSlide + 1) / totalSlides) * 100;
        progressBar.style.width = `${progress}%`;
    }

    // Update progress on slide change
    const originalShowSlide = showSlide;
    showSlide = function(index) {
        originalShowSlide(index);
        updateProgress();
    };

    // Initialize progress
    updateProgress();

    // Add slide number indicators
    const slideIndicators = document.createElement('div');
    slideIndicators.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        display: flex;
        gap: 8px;
        z-index: 1000;
    `;

    for (let i = 0; i < totalSlides; i++) {
        const dot = document.createElement('div');
        dot.style.cssText = `
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transition: all 0.3s ease;
            cursor: pointer;
        `;
        dot.addEventListener('click', () => {
            currentSlide = i;
            showSlide(currentSlide);
            updateDots();
        });
        slideIndicators.appendChild(dot);
    }

    document.body.appendChild(slideIndicators);

    function updateDots() {
        const dots = slideIndicators.children;
        for (let i = 0; i < dots.length; i++) {
            if (i === currentSlide) {
                dots[i].style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                dots[i].style.width = '24px';
            } else {
                dots[i].style.background = 'rgba(255, 255, 255, 0.3)';
                dots[i].style.width = '8px';
            }
        }
    }

    // Update dots on slide change
    const originalShowSlide2 = showSlide;
    showSlide = function(index) {
        originalShowSlide2(index);
        updateDots();
    };

    // Initialize dots
    updateDots();

    // Add help overlay (press 'h' or '?')
    const helpOverlay = document.createElement('div');
    helpOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.9);
        backdrop-filter: blur(10px);
        display: none;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;

    const helpContent = document.createElement('div');
    helpContent.style.cssText = `
        background: rgba(255, 255, 255, 0.1);
        padding: 40px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 600px;
    `;

    helpContent.innerHTML = `
        <h2 style="font-size: 32px; margin-bottom: 30px; color: #ffffff;">Keyboard Shortcuts</h2>
        <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 15px; color: #e0e0e0; font-size: 16px;">
            <div><strong>→ / ↓ / Space</strong></div><div>Next slide</div>
            <div><strong>← / ↑</strong></div><div>Previous slide</div>
            <div><strong>Home</strong></div><div>First slide</div>
            <div><strong>End</strong></div><div>Last slide</div>
            <div><strong>F</strong></div><div>Toggle fullscreen</div>
            <div><strong>H / ?</strong></div><div>Show this help</div>
            <div><strong>Esc</strong></div><div>Close help</div>
        </div>
        <p style="margin-top: 30px; text-align: center; color: #b0b0b0;">Press any key to close</p>
    `;

    helpOverlay.appendChild(helpContent);
    document.body.appendChild(helpOverlay);

    document.addEventListener('keydown', function(e) {
        if (e.key === 'h' || e.key === 'H' || e.key === '?') {
            helpOverlay.style.display = 'flex';
        } else if (e.key === 'Escape' && helpOverlay.style.display === 'flex') {
            helpOverlay.style.display = 'none';
        }
    });

    helpOverlay.addEventListener('click', function() {
        helpOverlay.style.display = 'none';
    });

    // Prevent context menu
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
    });

    // Add print styles
    const printStyles = document.createElement('style');
    printStyles.textContent = `
        @media print {
            .slide-controls,
            .slide-indicators {
                display: none !important;
            }
            
            .slide {
                page-break-after: always;
                opacity: 1 !important;
                transform: none !important;
                position: relative !important;
                width: 100% !important;
                height: auto !important;
                margin-bottom: 20px;
            }
            
            body {
                background: white;
            }
        }
    `;
    document.head.appendChild(printStyles);

    console.log('DevOps Presentation loaded successfully!');
    console.log('Press "H" or "?" for keyboard shortcuts');
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.8);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
`;
document.head.appendChild(style);
