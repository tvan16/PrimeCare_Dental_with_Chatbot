document.addEventListener('DOMContentLoaded', function() {
    // 1. Xác định ngôn ngữ hiện tại dựa trên URL
    function detectCurrentLanguage() {
        const currentUrl = window.location.pathname;
        if (currentUrl.includes('index-2.html')) {
            return 'ENG';
        }
        return 'VIE';
    }

    // 2. Cập nhật hiển thị ngôn ngữ hiện tại
    function updateCurrentLanguageDisplay() {
        const currentLang = detectCurrentLanguage();
        const currentLangElement = document.querySelector('.language-btn .lang-text');
        const currentFlagElement = document.querySelector('.language-btn .flag-icon');
        
        if (currentLangElement) {
            currentLangElement.textContent = currentLang;
        }
        
        if (currentFlagElement) {
            if (currentLang === 'ENG') {
                currentFlagElement.src = 'images/flags/uk-flag.png';
                currentFlagElement.alt = 'English';
            } else {
                currentFlagElement.src = 'images/flags/vn-flag.png';
                currentFlagElement.alt = 'Tiếng Việt';
            }
        }
    }

    // 3. Lưu lựa chọn ngôn ngữ vào localStorage
    function saveLanguagePreference(lang) {
        localStorage.setItem('preferredLanguage', lang);
    }

    // 4. Xử lý sự kiện click cho nút ngôn ngữ
    const languageBtn = document.querySelector('.language-btn');
    const languageDropdown = document.querySelector('.language-dropdown');
    const dropdown = document.querySelector('.language-dropdown-content');
    
    if (languageBtn && dropdown) {
        // Xử lý click vào nút
        languageBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Toggle class 'show' cho dropdown và 'active' cho dropdown container
            dropdown.classList.toggle('show');
            languageDropdown.classList.toggle('active');
            
            // Xoay mũi tên khi dropdown được hiển thị
            const arrow = languageBtn.querySelector('.fa-chevron-down');
            if (arrow) {
                if (dropdown.classList.contains('show')) {
                    arrow.style.transform = 'rotate(180deg)';
                } else {
                    arrow.style.transform = 'rotate(0)';
                }
            }
        });
        
        // Đóng dropdown khi click ra ngoài
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.language-dropdown')) {
                dropdown.classList.remove('show');
                languageDropdown.classList.remove('active');
                
                // Reset mũi tên
                const arrow = languageBtn.querySelector('.fa-chevron-down');
                if (arrow) {
                    arrow.style.transform = 'rotate(0)';
                }
            }
        });
    }

    // 5. Thêm sự kiện click cho các tùy chọn ngôn ngữ
    const langOptions = document.querySelectorAll('.lang-option');
    langOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            // Lấy thông tin ngôn ngữ đã chọn
            const langText = this.querySelector('.lang-text').textContent;
            saveLanguagePreference(langText);
            
            // Cập nhật hiển thị ngôn ngữ hiện tại ngay lập tức (không cần tải lại trang)
            const btnText = document.querySelector('.language-btn .lang-text');
            const btnFlag = document.querySelector('.language-btn .flag-icon');
            
            if (btnText) {
                btnText.textContent = langText;
            }
            
            if (btnFlag) {
                if (langText === 'ENG') {
                    btnFlag.src = 'images/flags/uk-flag.png';
                    btnFlag.alt = 'English';
                } else {
                    btnFlag.src = 'images/flags/vn-flag.png';
                    btnFlag.alt = 'Tiếng Việt';
                }
            }
            
            // Cho phép chuyển hướng trang nếu href được đặt
            // Không ngăn chặn sự kiện mặc định ở đây
        });
    });

    // 6. Xử lý sự kiện hover trên desktop
    if (window.innerWidth > 992) {
        const languageDropdown = document.querySelector('.language-dropdown');
        if (languageDropdown) {
            // Thêm class khi hover vào dropdown
            languageDropdown.addEventListener('mouseenter', function() {
                this.classList.add('hover');
            });
            
            // Xóa class khi rời khỏi dropdown
            languageDropdown.addEventListener('mouseleave', function() {
                this.classList.remove('hover');
                
                // Nếu dropdown không được hiển thị bởi click, đóng nó
                if (!dropdown.classList.contains('show')) {
                    dropdown.style.display = '';
                }
            });
        }
    }

    // 7. Kiểm tra nếu có ngôn ngữ đã lưu trong localStorage
    function loadSavedLanguage() {
        const savedLang = localStorage.getItem('preferredLanguage');
        if (savedLang) {
            const currentLang = detectCurrentLanguage();
            if (savedLang !== currentLang) {
                // Tự động chuyển hướng dựa trên ngôn ngữ đã lưu
                if (savedLang === 'ENG' && currentLang !== 'ENG') {
                    window.location.href = 'index-2.html';
                } else if (savedLang === 'VIE' && currentLang !== 'VIE') {
                    window.location.href = 'index.html';
                }
            }
        }
    }

    // 8. Xử lý các vấn đề trên thiết bị di động
    function setupMobileSupport() {
        if (window.innerWidth <= 992) {
            // Trên thiết bị di động, đảm bảo dropdown hiển thị đúng
            const languageDropdown = document.querySelector('.language-dropdown');
            if (languageDropdown) {
                languageDropdown.addEventListener('touchstart', function(e) {
                    // Ngăn chặn hành vi mặc định của touch để tránh các vấn đề trên mobile
                    if (e.target.closest('.language-btn')) {
                        e.preventDefault();
                    }
                }, { passive: false });
            }
        }
    }

    // 9. Kiểm tra và xử lý các lỗi
    function handleErrors() {
        // Kiểm tra các phần tử cần thiết
        if (!document.querySelector('.language-btn')) {
            console.warn('Language button not found. Check your HTML structure.');
        }
        
        if (!document.querySelector('.language-dropdown-content')) {
            console.warn('Language dropdown content not found. Check your HTML structure.');
        }
        
        // Kiểm tra hình ảnh cờ
        const flags = document.querySelectorAll('.flag-icon');
        flags.forEach(flag => {
            flag.onerror = function() {
                console.warn('Flag image could not be loaded: ' + this.src);
                // Thay thế bằng text nếu hình ảnh không tải được
                this.style.display = 'none';
                const langText = this.nextElementSibling;
                if (langText) {
                    langText.style.marginLeft = '0';
                }
            };
        });
    }

    // Khởi tạo các chức năng
    updateCurrentLanguageDisplay();
    setupMobileSupport();
    handleErrors();
    
    // Bỏ comment dòng dưới nếu muốn tự động chuyển hướng dựa trên ngôn ngữ đã lưu
    // loadSavedLanguage();
});
