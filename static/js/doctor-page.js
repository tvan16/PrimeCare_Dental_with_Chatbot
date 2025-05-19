/**
 * Doctor Page Script - Xử lý tương tác và hiệu ứng cho trang bác sĩ
 */

document.addEventListener('DOMContentLoaded', function() {
    // Khởi tạo các chức năng
    initDoctorSearch();
    initDoctorCards();
    initSkillBars();
    initDoctorSlider();
    fixFontAwesomeIcons();
});

/**
 * Thêm hiệu ứng khi nhấn nút
 */
function addButtonClickEffect(button) {
    button.classList.add('clicked');
    
    // Tạo hiệu ứng ripple
    const ripple = document.createElement('span');
    ripple.classList.add('ripple-effect');
    button.appendChild(ripple);
    
    // Xóa hiệu ứng sau khi hoàn thành
    setTimeout(() => {
        ripple.remove();
        button.classList.remove('clicked');
    }, 600);
}

/**
 * Cập nhật số lượng bác sĩ hiển thị
 */
function updateDoctorCount(countElement) {
    if (!countElement) return;
    
    // Đếm số lượng bác sĩ hiển thị trên trang
    const doctorItems = document.querySelectorAll('.team-member-item');
    
    if (doctorItems && doctorItems.length > 0) {
        countElement.textContent = doctorItems.length;
    }
}

/**
 * Khởi tạo hiệu ứng cho card bác sĩ
 */
function initDoctorCards() {
    const doctorCards = document.querySelectorAll('.team-member-item');
    
    doctorCards.forEach(card => {
        // Hiệu ứng hover cho card
        card.addEventListener('mouseenter', function() {
            this.classList.add('hover');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('hover');
        });
        
        // Hiệu ứng hiển thị mạng xã hội
        const socialIcons = card.querySelectorAll('.doctor-social-media a');
        socialIcons.forEach(icon => {
            icon.style.opacity = '0';
            icon.style.transform = 'translateX(20px)';
        });
    });
    
    // Hiệu ứng hiện thẻ khi cuộn
    window.addEventListener('scroll', function() {
        doctorCards.forEach((card, index) => {
            const cardTop = card.getBoundingClientRect().top;
            if (cardTop < window.innerHeight - 100) {
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    });
    
    // Kích hoạt hiệu ứng ban đầu
    setTimeout(() => {
        window.dispatchEvent(new Event('scroll'));
    }, 500);
}

/**
 * Khởi tạo chức năng tìm kiếm bác sĩ
 */
function initDoctorSearch() {
    const searchInput = document.getElementById('doctorSearch');
    const doctorCards = document.querySelectorAll('.team-member-item');
    const countElement = document.getElementById('doctorCount');
    
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        let visibleCount = 0;
        
        doctorCards.forEach(card => {
            const doctorName = card.querySelector('h3 a').textContent.toLowerCase();
            const doctorArea = card.querySelector('.team-content p:nth-child(3)')?.textContent.toLowerCase() || '';
            
            if (doctorName.includes(searchTerm) || doctorArea.includes(searchTerm)) {
                card.style.display = 'block';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Cập nhật số lượng bác sĩ hiển thị
        if (countElement) {
            countElement.textContent = visibleCount;
        }
    });
    
    // Thêm hiệu ứng cho nút tìm kiếm
    const searchButton = document.getElementById('doctorSearchButton');
    if (searchButton) {
        searchButton.addEventListener('click', function() {
            addButtonClickEffect(this);
            
            // Xử lý tìm kiếm
            searchInput.dispatchEvent(new Event('input'));
        });
    }
    
    // Cập nhật số lượng ban đầu
    updateDoctorCount(countElement);
}

/**
 * Khởi tạo slider cho phần hiển thị bác sĩ
 */
function initDoctorSlider() {
    console.log('Khởi tạo slider bác sĩ...');
    
    const swiperContainer = document.querySelector('.swiper-container');
    
    if (!swiperContainer) {
        console.error('Không tìm thấy .swiper-container!');
        return;
    }
    
    try {
        // Hủy swiper cũ nếu đã khởi tạo
        if (swiperContainer.swiper) {
            swiperContainer.swiper.destroy(true, true);
        }
        
        // Khởi tạo Swiper mới với cấu hình chuẩn
        const doctorSwiper = new Swiper(swiperContainer, {
            slidesPerView: 4,         // CHÍNH XÁC 4 bác sĩ
            spaceBetween: 20,         // Khoảng cách giữa các slides
            slidesPerGroup: 1,        // Di chuyển 1 slide mỗi lần
            loop: true,               // Cho phép lặp vô hạn
            loopFillGroupWithBlank: false,
            speed: 500,               // Tốc độ chuyển slide
            watchSlidesProgress: true, // Theo dõi tiến trình hiển thị slide
            watchSlidesVisibility: true, // Theo dõi khả năng hiển thị slide
            grabCursor: true,          // Con trỏ grab khi hover
            preventClicksPropagation: true,
            preventClicks: false,
            threshold: 10,             // Ngưỡng vuốt nhẹ
            touchReleaseOnEdges: true,
            
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
                hideOnClick: false,    // Không ẩn nút khi click
            },
            
            pagination: {
                el: '.swiper-pagination',
                clickable: true,
            },
            
            breakpoints: {
                320: { slidesPerView: 1, spaceBetween: 10 },
                576: { slidesPerView: 2, spaceBetween: 15 },
                768: { slidesPerView: 3, spaceBetween: 15 },
                992: { slidesPerView: 4, spaceBetween: 20 }
            },
            
            on: {
                init: function() {
                    console.log('Swiper đã khởi tạo!');
                    // Đảm bảo nút điều hướng hiển thị
                    document.querySelector('.swiper-button-next').style.display = 'flex';
                    document.querySelector('.swiper-button-prev').style.display = 'flex';
                },
                slideChange: function() {
                    // Đảm bảo không có slide nào bị hiển thị một phần
                    this.snapGrid = [...this.slidesGrid];
                }
            }
        });
        
        console.log('Doctor Swiper khởi tạo thành công');
        
    } catch (error) {
        console.error('Lỗi khởi tạo Swiper:', error);
    }
}

// Đảm bảo chạy khi trang đã tải xong
window.addEventListener('load', function() {
    setTimeout(initDoctorSlider, 300);
});
/**
 * Khởi tạo hiệu ứng cho thanh skill
 */
function initSkillBars() {
    const skillbars = document.querySelectorAll('.skillbar');
    
    if (!skillbars.length) return;
    
    // Hàm xử lý animation cho skill bar
    function animateSkillBars() {
        skillbars.forEach(skillbar => {
            const percent = skillbar.getAttribute('data-percent');
            const countBar = skillbar.querySelector('.count-bar');
            
            if (countBar) {
                countBar.style.width = percent;
            }
        });
    }
    
    // Xử lý animation khi scroll đến phần skills
    const handleScroll = () => {
        const skillSection = document.querySelector('.team-member-skills');
        if (!skillSection) return;
        
        const sectionTop = skillSection.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;
        
        if (sectionTop < windowHeight - 100) {
            animateSkillBars();
            window.removeEventListener('scroll', handleScroll);
        }
    };
    
    // Thêm listener cho scroll event
    window.addEventListener('scroll', handleScroll);
    
    // Kiểm tra vị trí ban đầu nếu section đã hiển thị
    handleScroll();
}

/**
 * Thêm styles cho page
 */
function addStyles() {
    if (!document.getElementById('doctor-page-styles')) {
        const style = document.createElement('style');
        style.id = 'doctor-page-styles';
        style.textContent = `
            /* Hiệu ứng click button */
            .clicked {
                transform: scale(0.95) !important;
            }
            
            .ripple-effect {
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                background: rgba(255, 255, 255, 0.4);
                border-radius: 50%;
                transform: translate(-50%, -50%);
                animation: ripple 0.6s linear;
                z-index: 1;
                pointer-events: none;
            }
            
            @keyframes ripple {
                to {
                    width: 250%;
                    height: 250%;
                    opacity: 0;
                }
            }
            
            /* Đối tượng hover */
            .team-member-item.hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
                cursor: pointer;
            }
            
            /* Icon mạng xã hội */
            .doctor-social-media {
                position: absolute;
                right: 10px;
                top: 50%;
                transform: translateY(-50%);
                display: flex;
                flex-direction: column;
                gap: 10px;
                z-index: 99;
                opacity: 0;
                transition: opacity 0.4s ease;
            }
            
            .team-member-item:hover .doctor-social-media {
                opacity: 1;
                right: 15px;
            }
            
            .icon-img {
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                width: 36px;
                height: 36px;
                background: rgba(52, 90, 162, 0.9);
                color: white;
                border-radius: 50%;
                transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                opacity: 0;
                transform: translateX(20px);
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.25);
                margin: 5px 0;
                border: 1px solid rgba(255, 255, 255, 0.2);
                background-position: center;
                background-repeat: no-repeat;
                background-size: 50%;
            }
            
            /* Hiệu ứng hiện tuần tự */
            .team-member-item .doctor-social-media a:nth-child(1) {
                transition-delay: 0s;
            }
            
            .team-member-item .doctor-social-media a:nth-child(2) {
                transition-delay: 0.1s;
            }
            
            .team-member-item .doctor-social-media a:nth-child(3) {
                transition-delay: 0.2s;
            }
            
            .team-member-item .doctor-social-media a.icon-img:hover {
                transform: scale(1.2);
                background: #34c3ff;
                box-shadow: 0 6px 15px rgba(52, 195, 255, 0.5);
                border-color: rgba(255, 255, 255, 0.3);
            }
            
            /* Icon cụ thể */
            .icon-facebook {
                background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path fill="white" d="M279.14 288l14.22-92.66h-88.91v-60.13c0-25.35 12.42-50.06 52.24-50.06h40.42V6.26S260.43 0 225.36 0c-73.22 0-121.08 44.38-121.08 124.72v70.62H22.89V288h81.39v224h100.17V288z"/></svg>');
            }
            
            .icon-instagram {
                background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path fill="white" d="M224.1 141c-63.6 0-114.9 51.3-114.9 114.9s51.3 114.9 114.9 114.9S339 319.5 339 255.9 287.7 141 224.1 141zm0 189.6c-41.1 0-74.7-33.5-74.7-74.7s33.5-74.7 74.7-74.7 74.7 33.5 74.7 74.7-33.6 74.7-74.7 74.7zm146.4-194.3c0 14.9-12 26.8-26.8 26.8-14.9 0-26.8-12-26.8-26.8s12-26.8 26.8-26.8 26.8 12 26.8 26.8zm76.1 27.2c-1.7-35.9-9.9-67.7-36.2-93.9-26.2-26.2-58-34.4-93.9-36.2-37-2.1-147.9-2.1-184.9 0-35.8 1.7-67.6 9.9-93.9 36.1s-34.4 58-36.2 93.9c-2.1 37-2.1 147.9 0 184.9 1.7 35.9 9.9 67.7 36.2 93.9s58 34.4 93.9 36.2c37 2.1 147.9 2.1 184.9 0 35.9-1.7 67.7-9.9 93.9-36.2 26.2-26.2 34.4-58 36.2-93.9 2.1-37 2.1-147.8 0-184.8zM398.8 388c-7.8 19.6-22.9 34.7-42.6 42.6-29.5 11.7-99.5 9-132.1 9s-102.7 2.6-132.1-9c-19.6-7.8-34.7-22.9-42.6-42.6-11.7-29.5-9-99.5-9-132.1s-2.6-102.7 9-132.1c7.8-19.6 22.9-34.7 42.6-42.6 29.5-11.7 99.5-9 132.1-9s102.7-2.6 132.1 9c19.6 7.8 34.7 22.9 42.6 42.6 11.7 29.5 9 99.5 9 132.1s2.7 102.7-9 132.1z"/></svg>');
            }
            
            .icon-twitter {
                background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="white" d="M459.37 151.716c.325 4.548.325 9.097.325 13.645 0 138.72-105.583 298.558-298.558 298.558-59.452 0-114.68-17.219-161.137-47.106 8.447.974 16.568 1.299 25.34 1.299 49.055 0 94.213-16.568 130.274-44.832-46.132-.975-84.792-31.188-98.112-72.772 6.498.974 12.995 1.624 19.818 1.624 9.421 0 18.843-1.3 27.614-3.573-48.081-9.747-84.143-51.98-84.143-102.985v-1.299c13.969 7.797 30.214 12.67 47.431 13.319-28.264-18.843-46.781-51.005-46.781-87.391 0-19.492 5.197-37.36 14.294-52.954 51.655 63.675 129.3 105.258 216.365 109.807-1.624-7.797-2.599-15.918-2.599-24.04 0-57.828 46.782-104.934 104.934-104.934 30.213 0 57.502 12.67 76.67 33.137 23.715-4.548 46.456-13.32 66.599-25.34-7.798 24.366-24.366 44.833-46.132 57.827 21.117-2.273 41.584-8.122 60.426-16.243-14.292 20.791-32.161 39.308-52.628 54.253z"/></svg>');
            }
            
            /* Style cho Doctor Slider */
            .doctor-slider {
                position: relative;
                padding: 0 40px;
                margin-bottom: 40px;
            }
            
            /* Nút điều hướng */
            .swiper-button-next,
            .swiper-button-prev {
                width: 40px;
                height: 40px;
                background-color: #fff;
                border-radius: 50%;
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                color: #333;
            }
            
            .swiper-button-next:after,
            .swiper-button-prev:after {
                font-size: 18px;
                font-weight: bold;
            }
            
            .swiper-button-next:hover,
            .swiper-button-prev:hover {
                background-color: #6247ea;
                color: white;
            }
            
            /* Hiển thị nhiều slide */
            .swiper-container {
                overflow: hidden;
                padding: 20px 0;
            }
            
            @media (min-width: 992px) {
                .swiper-slide {
                    width: 25% !important; /* Force hiển thị 4 slides trên màn hình lớn */
                }
            }
            
            /* Animation khi slide thay đổi */
            .swiper-slide-active .team-member-item {
                transform: scale(1.03);
                transition: transform 0.3s ease;
            }
            
            /* Fix cho social media icons trong slider */
            .swiper-slide-active .team-member-item:hover .doctor-social-media a {
                opacity: 1;
                transform: translateX(0);
            }
            
            /* Fix Ghost Cursor */
            .team-member-item .team-image img {
                border-radius: 10px 10px 0 0;
                width: 100%;
                height: auto;
                object-fit: cover;
                aspect-ratio: 3/4;
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Fix icon mạng xã hội trên iOS
 */
function fixFontAwesomeIcons() {
    // Kiểm tra tất cả các icon social media
    setTimeout(() => {
        document.querySelectorAll('.icon-img').forEach(icon => {
            icon.style.opacity = '1';
            icon.style.transform = 'translateX(0)';
        });
    }, 1000);
}

// Khởi chạy khi trang đã load hoàn toàn
window.addEventListener('load', function() {
    // Animation khi load trang
    document.querySelectorAll('.team-member-item').forEach((item, index) => {
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Thêm styles
    addStyles();
    
    // Cập nhật slider để đảm bảo hiển thị đúng
    if (typeof Swiper !== 'undefined') {
        const swiperInstances = document.querySelectorAll('.swiper-container');
        swiperInstances.forEach(container => {
            const swiper = container.swiper;
            if (swiper) {
                swiper.update();
            }
        });
    }
});