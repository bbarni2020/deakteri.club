const translations = {
    en: {
        "website-title": "Welcome To The Deak Teri HC Guides",
        "other-resources-title": "Other Resources",
        "other-resources-intro": "Here you can find additional links to help you on your journey with Hack Club."
    },
    hu: {
        "website-title": "Üdvözlünk a Deák Téri Hack Club Guide Oldalán",
        "other-resources-title": "Egyéb Források",
        "other-resources-intro": "Itt további linkeket találsz, amelyek segítenek az utadon a Hack Clubbal."
    }
};

function setLanguage(lang) {
    localStorage.setItem('preferredLanguage', lang);
    document.documentElement.lang = lang;
    
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });

    const currentLangSpan = document.getElementById('current-lang');
    if (currentLangSpan) {
        currentLangSpan.textContent = lang.toUpperCase();
    }

    document.querySelectorAll('.lang-option').forEach(opt => opt.classList.remove('active'));
    const activeBtn = document.getElementById(`lang-${lang}`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('preferredLanguage') || 'en';
    setLanguage(savedLang);
});
