document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.search-input');
    const searchResults = document.querySelector('.search-results');
    let searchTimeout;

    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        
        // Xóa timeout cũ nếu có
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        // Nếu query quá ngắn, ẩn kết quả
        if (query.length < 2) {
            searchResults.style.display = 'none';
            return;
        }
        
        // Đợi 300ms sau khi người dùng ngừng gõ
        searchTimeout = setTimeout(() => {
            fetch(`/search/?q=${encodeURIComponent(query)}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // Xóa kết quả cũ
                    searchResults.innerHTML = '';
                    
                    // Kiểm tra nếu có lỗi
                    if (data.error) {
                        searchResults.innerHTML = `
                            <div class="error">
                                <div>${data.error}</div>
                                <div class="error-details">${data.details || ''}</div>
                            </div>`;
                        searchResults.style.display = 'block';
                        return;
                    }
                    
                    // Kiểm tra nếu không có kết quả
                    if (!data.services.length && !data.blogs.length && !data.doctors.length) {
                        searchResults.innerHTML = '<div class="no-results">Không tìm thấy kết quả</div>';
                        searchResults.style.display = 'block';
                        return;
                    }
                    
                    // Hiển thị kết quả dịch vụ
                    if (data.services.length) {
                        const servicesSection = document.createElement('div');
                        servicesSection.className = 'search-section';
                        servicesSection.innerHTML = `
                            <h4>Dịch vụ</h4>
                            ${data.services.map(service => `
                                <a href="${service.url}" class="search-item">
                                    <div class="search-item-content">
                                        <div class="search-item-title">${service.name}</div>
                                        <div class="search-item-subtitle">${service.main_service}</div>
                                    </div>
                                </a>
                            `).join('')}
                        `;
                        searchResults.appendChild(servicesSection);
                    }
                    
                    // Hiển thị kết quả bài viết
                    if (data.blogs.length) {
                        const blogsSection = document.createElement('div');
                        blogsSection.className = 'search-section';
                        blogsSection.innerHTML = `
                            <h4>Bài viết</h4>
                            ${data.blogs.map(blog => `
                                <a href="${blog.url}" class="search-item">
                                    <div class="search-item-content">
                                        <div class="search-item-title">${blog.title}</div>
                                        <div class="search-item-subtitle">${blog.excerpt}</div>
                                    </div>
                                </a>
                            `).join('')}
                        `;
                        searchResults.appendChild(blogsSection);
                    }
                    
                    // Hiển thị kết quả bác sĩ
                    if (data.doctors.length) {
                        const doctorsSection = document.createElement('div');
                        doctorsSection.className = 'search-section';
                        doctorsSection.innerHTML = `
                            <h4>Bác sĩ</h4>
                            ${data.doctors.map(doctor => `
                                <a href="${doctor.url}" class="search-item">
                                    <div class="search-item-content">
                                        <div class="search-item-title">${doctor.name}</div>
                                        <div class="search-item-subtitle">${doctor.specialty}</div>
                                    </div>
                                </a>
                            `).join('')}
                        `;
                        searchResults.appendChild(doctorsSection);
                    }
                    
                    searchResults.style.display = 'block';
                })
                .catch(error => {
                    console.error('Error:', error);
                    searchResults.innerHTML = `
                        <div class="error">
                            <div>Có lỗi xảy ra khi tìm kiếm</div>
                            <div class="error-details">${error.message}</div>
                        </div>`;
                    searchResults.style.display = 'block';
                });
        }, 300);
    });
    
    // Ẩn kết quả khi click ra ngoài
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
}); 