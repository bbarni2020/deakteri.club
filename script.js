const API_BASE_URL = 'https://api.deakteri.club/api';

async function loadSupporters() {
    const supportersSection = document.getElementById('supporters');
    const loadingElement = document.getElementById('supporters-loading');
    
    try {
        supportersSection.style.display = 'block';
        loadingElement.style.display = 'block';
        
        const sponsorsResponse = await Promise.race([
            fetch(`${API_BASE_URL}/sponsors`),
            new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
        ]);
        
        if (!sponsorsResponse.ok) {
            throw new Error(`HTTP ${sponsorsResponse.status}: ${sponsorsResponse.statusText}`);
        }
        
        const sponsorsData = await sponsorsResponse.json();
        
        const donatorsResponse = await Promise.race([
            fetch(`${API_BASE_URL}/donators`),
            new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
        ]);
        
        if (!donatorsResponse.ok) {
            throw new Error(`HTTP ${donatorsResponse.status}: ${donatorsResponse.statusText}`);
        }
        
        const donatorsData = await donatorsResponse.json();
        
        if (sponsorsData.success && donatorsData.success) {
            loadingElement.style.display = 'none';
            
            displaySponsors(sponsorsData.sponsors);
            displayDonators(donatorsData.donators);
            
            if (sponsorsData.sponsors.length === 0 && donatorsData.donators.length === 0) {
                supportersSection.style.display = 'none';
            } else {
                supportersSection.style.display = 'block';
            }
        }
    } catch (error) {
        console.error('Error loading supporters:', error);
        
        const currentLang = window.languageManager ? window.languageManager.getCurrentLanguage() : 'hu';
        const errorMessages = {
            hu: {
                general: 'Nem sikerült betölteni a támogatókat.',
                cors: 'API szolgáltatás ideiglenesen nem elérhető (CORS hiba).',
                timeout: 'API válasz túllépte az időkorlátot.',
                http: `Szerver hiba: ${error.message}`,
                fallback: 'A támogatók listája hamarosan elérhető lesz.'
            },
            en: {
                general: 'Failed to load supporters.',
                cors: 'API service temporarily unavailable (CORS error).',
                timeout: 'API response exceeded time limit.',
                http: `Server error: ${error.message}`,
                fallback: 'The supporters list will be available soon.'
            }
        };
        
        let errorMessage = errorMessages[currentLang].general;
        
        if (error.message.includes('cors') || error.message.includes('CORS') || 
            error.message.includes('Access-Control-Allow-Origin') ||
            error.name === 'TypeError' && error.message.includes('fetch')) {
            errorMessage = errorMessages[currentLang].cors;
            console.info('CORS error detected - API might not be properly configured for this domain');
        } else if (error.message === 'timeout') {
            errorMessage = errorMessages[currentLang].timeout;
        } else if (error.message.includes('HTTP')) {
            errorMessage = errorMessages[currentLang].http;
        }
        
        loadingElement.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #b0b0b0;">
                <p>⚠️ ${errorMessage}</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem;">${errorMessages[currentLang].fallback}</p>
            </div>
        `;
        
        setTimeout(() => {
            supportersSection.style.display = 'none';
        }, 5000);
    }
}

function displaySponsors(sponsors) {
    const sponsorsGrid = document.querySelector('.sponsors-grid');
    const sponsorsCategory = document.getElementById('sponsors-category');
    
    if (sponsors.length === 0) {
        sponsorsCategory.style.display = 'none';
        return;
    }
    
    sponsorsCategory.style.display = 'block';
    sponsorsGrid.innerHTML = '';
    
    sponsors.forEach((sponsor, index) => {
        const sponsorElement = document.createElement('div');
        sponsorElement.className = 'sponsor-item';
        sponsorElement.style.animationDelay = `${index * 0.1}s`;
        
        // Square container
        sponsorElement.style.width = '150px';
        sponsorElement.style.height = '150px';
        sponsorElement.style.padding = '1rem';
        sponsorElement.style.margin = '0.5rem';
        sponsorElement.style.transition = 'all 0.3s ease';
        sponsorElement.style.display = 'flex';
        sponsorElement.style.flexDirection = 'column';
        sponsorElement.style.alignItems = 'center';
        sponsorElement.style.justifyContent = 'center';
        sponsorElement.style.textAlign = 'center';
        sponsorElement.style.cursor = sponsor.website ? 'pointer' : 'default';
        
        // Hover effects
        sponsorElement.addEventListener('mouseenter', () => {
            sponsorElement.style.transform = 'translateY(-8px) scale(1.1)';
        });
        
        sponsorElement.addEventListener('mouseleave', () => {
            sponsorElement.style.transform = 'translateY(0) scale(1)';
        });
        
        if (sponsor.logo_url && sponsor.logo_url.trim() !== '') {
            // Logo/Icon
            const img = document.createElement('img');
            img.src = sponsor.logo_url;
            img.alt = sponsor.name;
            img.title = sponsor.name;
            img.className = 'sponsor-logo';
            img.style.width = '80px';
            img.style.height = '80px';
            img.style.objectFit = 'contain';
            img.style.marginBottom = '0.8rem';
            img.style.transition = 'all 0.3s ease';
            
            sponsorElement.appendChild(img);
            
        } else {
            // Fallback emoji icon
            const iconElement = document.createElement('div');
            iconElement.style.fontSize = '4rem';
            iconElement.style.marginBottom = '0.8rem';
            iconElement.style.transition = 'all 0.3s ease';
            
            const sponsorEmojis = ['🏢', '🏭', '🏗️', '🏛️', '🏪', '🏬', '🏦', '💼', '📊', '📈', '💹', '⚡', '🔧', '🛠️', '⚙️', '🔩', '💻', '🖥️', '📱', '💡', '🚀', '🎯', '🌟', '💎', '👑', '🏆', '🎁'];
            const randomEmoji = sponsorEmojis[Math.floor(Math.random() * sponsorEmojis.length)];
            iconElement.textContent = randomEmoji;
            
            sponsorElement.appendChild(iconElement);
        }
        
        // Company name
        const nameElement = document.createElement('h4');
        nameElement.style.color = '#ffffff';
        nameElement.style.margin = '0';
        nameElement.style.fontSize = '1rem';
        nameElement.style.fontWeight = '500';
        nameElement.style.transition = 'all 0.3s ease';
        nameElement.textContent = sponsor.name;
        sponsorElement.appendChild(nameElement);
        
        // Click to open website
        if (sponsor.website) {
            sponsorElement.addEventListener('click', () => {
                window.open(sponsor.website, '_blank');
            });
            
            // Enhanced hover effect for clickable sponsors
            sponsorElement.addEventListener('mouseenter', () => {
                sponsorElement.style.transform = 'translateY(-8px) scale(1.1)';
                nameElement.style.color = '#4ECDC4';
            });
            
            sponsorElement.addEventListener('mouseleave', () => {
                sponsorElement.style.transform = 'translateY(0) scale(1)';
                nameElement.style.color = '#ffffff';
            });
        }
        
        sponsorsGrid.appendChild(sponsorElement);
    });
}

function displayDonators(donators) {
    const donatorsGrid = document.querySelector('.donators-grid');
    const donatorsCategory = document.getElementById('donators-category');
    
    if (donators.length === 0) {
        donatorsCategory.style.display = 'none';
        return;
    }
    
    donatorsCategory.style.display = 'block';
    donatorsGrid.innerHTML = '';
    
    const visibleDonators = donators
        .filter(donator => !donator.anonymous)
        .sort((a, b) => new Date(b.added_date) - new Date(a.added_date))
        .slice(0, 6);
    
    visibleDonators.forEach((donator, index) => {
        const donatorElement = document.createElement('div');
        donatorElement.className = 'donator-item';
        donatorElement.style.animationDelay = `${index * 0.1}s`;
        
        const colorfulEmojis = ['🌟', '💎', '🚀', '⭐', '🎯', '🔥', '💡', '🎨', '💫', '✨', '🎪', '🎊', '🎉', '🌺', '🦄', '🎭', '🎨', '🌸', '🍀', '💝', '🎁', '🏆', '👑', '💰', '🌻', '🦋', '🎈', '🎪', '🎯'];
        const randomEmoji = colorfulEmojis[Math.floor(Math.random() * colorfulEmojis.length)];
        
        donatorElement.innerHTML = `
            <div class="donator-avatar">${randomEmoji}</div>
            <div class="donator-info">
                <h4>${donator.name}</h4>
                <p class="donator-amount">${donator.amount} ${donator.currency}</p>
            </div>
        `;
        
        donatorsGrid.appendChild(donatorElement);
    });
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const header = document.querySelector('.header');
            const headerHeight = header ? header.offsetHeight : 80;
            const targetPosition = target.offsetTop - headerHeight - 20;
            
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

window.addEventListener('scroll', () => {
    const header = document.querySelector('.header');
    const aboutSection = document.querySelector('#about');
    
    if (window.innerWidth > 768 && aboutSection) {
        const aboutSectionTop = aboutSection.offsetTop;
        const scrollPosition = window.scrollY;
        
        if (scrollPosition >= aboutSectionTop - 100) {
            header.style.background = 'rgba(10, 10, 10, 0.95)';
            header.style.backdropFilter = 'blur(15px)';
            header.style.borderBottom = '1px solid rgba(78, 205, 196, 0.2)';
            header.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.4)';
        } else {
            header.style.background = 'transparent';
            header.style.backdropFilter = 'none';
            header.style.borderBottom = 'none';
            header.style.boxShadow = 'none';
        }
    }
}, { passive: true });

function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    const speed = 100;

    counters.forEach(counter => {
        const updateCount = () => {
            const target = parseInt(counter.getAttribute('data-target') || counter.innerText.replace(/[^\d]/g, ''));
            const count = parseInt(counter.innerText.replace(/[^\d]/g, '')) || 0;
            const increment = Math.ceil(target / speed);

            if (count < target) {
                const newCount = Math.min(count + increment, target);
                counter.innerText = newCount;
                if (newCount < target) {
                    requestAnimationFrame(updateCount);
                } else {
                    if (counter.innerText.includes('+')) {
                        counter.innerText = target + '+';
                    } else {
                        counter.innerText = target;
                    }
                }
            }
        };
        requestAnimationFrame(updateCount);
    });
}

const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            requestAnimationFrame(() => {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                
                if (entry.target.classList.contains('community-stats')) {
                    setTimeout(() => requestAnimationFrame(animateCounters), 300);
                }
            });
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.feature-card, .benefit-card, .step, .stat, .donation-card, .sponsor-item, .donator-item, .animate-on-scroll');
    
    animatedElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        el.style.transitionDelay = `${Math.min(index * 0.05, 0.5)}s`;
        observer.observe(el);
    });

    const statsSection = document.querySelector('.community-stats');
    if (statsSection) {
        observer.observe(statsSection);
    }
    
    const donationCards = document.querySelectorAll('.donation-card');
    donationCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });
});

let ticking = false;

function updateHeader() {
    const header = document.querySelector('.header');
    const aboutSection = document.querySelector('#about');
    
    if (window.innerWidth > 768 && aboutSection) {
        const aboutSectionTop = aboutSection.offsetTop;
        const scrollPosition = window.scrollY;
        
        if (scrollPosition >= aboutSectionTop - 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    }
    ticking = false;
}

window.addEventListener('scroll', () => {
    if (!ticking) {
        requestAnimationFrame(updateHeader);
        ticking = true;
    }
}, { passive: true });

function toggleMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    navLinks.classList.toggle('active');
}

function addMobileMenu() {
    if (window.innerWidth <= 768) {
        const nav = document.querySelector('.nav');
        const existingButton = nav.querySelector('.mobile-menu-button');
        
        if (!existingButton) {
            const mobileButton = document.createElement('button');
            mobileButton.className = 'mobile-menu-button';
            mobileButton.innerHTML = '☰';
            mobileButton.style.cssText = `
                background: none;
                border: none;
                font-size: 1.5rem;
                color: #e0e0e0;
                cursor: pointer;
                display: none;
            `;
            
            mobileButton.addEventListener('click', toggleMobileMenu);
            nav.appendChild(mobileButton);
        }
    }
}

window.addEventListener('resize', addMobileMenu);
addMobileMenu();

const mobileMenuCSS = `
@media (max-width: 768px) {
    .mobile-menu-button {
        display: block !important;
    }
    
    .nav-links {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: #0f0f0f;
        flex-direction: column;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        transform: translateY(-100%);
        opacity: 0;
        pointer-events: none;
        transition: all 0.3s ease;
    }
    
    .nav-links.active {
        transform: translateY(0);
        opacity: 1;
        pointer-events: all;
    }
}
`;

const style = document.createElement('style');
style.textContent = mobileMenuCSS;
document.head.appendChild(style);

let currentSponsorshipType = 'onetime';

function openInvoiceForm(sponsorshipType = 'onetime') {
    currentSponsorshipType = sponsorshipType;
    const modal = document.getElementById('invoiceModal');
    const modalHeader = modal.querySelector('.modal-header h2');
    const frequencyGroup = document.getElementById('frequencyGroup');
    const frequencyField = document.getElementById('frequency');
    const noticeContent = modal.querySelector('.notice-content');
    
    const lm = window.languageManager;
    if (sponsorshipType === 'recurring') {
        modalHeader.textContent = lm.getTranslation('invoice.recurringTitle');
        frequencyGroup.style.display = 'block';
        frequencyField.required = true;
        const title = lm.getTranslation('invoice.recurringNotice.title');
        const desc = lm.getTranslation('invoice.recurringNotice.description');
        noticeContent.innerHTML = `
            <h4>${title}</h4>
            <p>${desc}</p>
        `;
    } else {
        modalHeader.textContent = lm.getTranslation('invoice.onetimeTitle');
        frequencyGroup.style.display = 'none';
        frequencyField.required = false;
        frequencyField.value = '';
        const title = lm.getTranslation('invoice.onetimeNotice.title');
        const desc = lm.getTranslation('invoice.onetimeNotice.description');
        noticeContent.innerHTML = `
            <h4>${title}</h4>
            <p>${desc}</p>
        `;
    }
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeInvoiceForm() {
    const modal = document.getElementById('invoiceModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

window.addEventListener('click', function(event) {
    const modal = document.getElementById('invoiceModal');
    if (event.target === modal) {
        closeInvoiceForm();
    }
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeInvoiceForm();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    loadSupporters();
    
    const invoiceForm = document.getElementById('invoiceForm');
    if (invoiceForm) {
        invoiceForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = 'Küldés...';
            submitButton.disabled = true;
            
            try {
                const formData = new FormData(this);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                
                data.sponsorshipType = currentSponsorshipType;
                if (currentSponsorshipType === 'recurring' && !data.frequency) {
                    throw new Error('Kérjük, válassza ki a támogatás gyakoriságát!');
                }
                
                const response = await Promise.race([
                    fetch(`${API_BASE_URL}/invoice`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    }),
                    new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 10000))
                ]);
                
                const result = await response.json();
                
                if (result.success) {
                    const sponsorshipTypeText = currentSponsorshipType === 'recurring' ? 'rendszeres' : 'egyszeri';
                    const frequencyText = data.frequency ? ` (${getFrequencyText(data.frequency)})` : '';
                    
                    alert(`${sponsorshipTypeText.charAt(0).toUpperCase() + sponsorshipTypeText.slice(1)} szponzorálási kérelem sikeresen elküldve!${frequencyText}\n\n📧 Hamarosan email-ben felvesszük Önnel a kapcsolatot a számlázási részletek egyeztetésére.`);
                    
                    closeInvoiceForm();
                    this.reset();
                } else {
                    throw new Error(result.error || 'Ismeretlen hiba történt');
                }
                
            } catch (error) {
                console.error('Error submitting invoice:', error);
                
                if (error.message.includes('gyakoriságát')) {
                    alert(error.message);
                    return;
                }
                
                let shouldFallback = true;
                let errorMsg = 'API szolgáltatás ideiglenesen nem elérhető.';
                
                if (error.message.includes('cors') || error.message.includes('CORS') || 
                    error.name === 'TypeError' && error.message.includes('fetch')) {
                    errorMsg = 'API szolgáltatás CORS konfigurációs problémája miatt nem elérhető.';
                } else if (error.message === 'timeout') {
                    errorMsg = 'API válasz túllépte az időkorlátot.';
                } else if (error.message.includes('HTTP')) {
                    errorMsg = `Szerver hiba: ${error.message}`;
                }
                
                if (shouldFallback) {
                    const useEmail = confirm(`${errorMsg}\n\nSzeretné inkább emailben elküldeni a kérelmet?`);
                    
                    if (useEmail) {
                        const sponsorshipTypeText = currentSponsorshipType === 'recurring' ? 'Rendszeres' : 'Egyszeri';
                        const frequencyText = data.frequency ? `\nGyakoriság: ${getFrequencyText(data.frequency)}` : '';
                        
                        const emailBody = `
${sponsorshipTypeText} Számlázási kérelem - Deáktéri Hack Club Szponzorálás
Tisztelt Deák Téri Evagélikus Gimnázium Hack Club Csapata,
Kérem, vegyék figyelembe az alábbi szponzorálási kérelmet:

SZPONZOR ADATOK:
Név/Cégnév: ${data.companyName}
Email: ${data.contactEmail}
Cím: ${data.streetAddress}${data.suite ? ', ' + data.suite : ''}
Város: ${data.city}
Megye/Állam: ${data.state}
Irányítószám: ${data.zip}
Ország: ${data.country}

SZÁMLÁZÁSI RÉSZLETEK:
Támogatás típusa: ${sponsorshipTypeText}${frequencyText}
Összeg: $${data.amount} USD

📧 Kérjük, vegyék fel velem a kapcsolatot a számlázási folyamat megkezdéséhez.
✅ Várom a számla kiállítását.

Köszönettel,
${data.companyName}
                        `.trim();
                        
                        const mailtoLink = `mailto:balogh.barnabas@deakteri.hu?subject=${sponsorshipTypeText} Számlázási kérelem - ${data.companyName}&body=${encodeURIComponent(emailBody)}`;
                        window.location.href = mailtoLink;
                        
                        alert('Email kliens megnyitva! Kérjük, küldje el az előre kitöltött emailt a számlázási kérelem feldolgozásához.');
                        closeInvoiceForm();
                        this.reset();
                    }
                } else {
                    alert(errorMsg);
                }
            } finally {
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            }
        });
    }
});

function getFrequencyText(frequency) {
    const frequencyMap = {
        'weekly': 'hetente',
        'monthly': 'havonta',
        'quarterly': 'negyedévente', 
        'yearly': 'évente'
    };
    return frequencyMap[frequency] || frequency;
}

