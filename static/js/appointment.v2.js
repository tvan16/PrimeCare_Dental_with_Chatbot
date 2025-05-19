document.addEventListener('DOMContentLoaded', function() {
    const appointmentForm = document.getElementById('appointmentForm');
    const specificIssueContainer = document.getElementById('specificIssueContainer');
    const timeInput = document.getElementById('time');
    const dateInput = document.getElementById('date');

    // Định nghĩa giờ làm việc
    const workingHours = {
        'Monday': { start: '08:00', end: '19:00' },
        'Tuesday': { start: '08:00', end: '19:00' },
        'Wednesday': { start: '08:00', end: '19:00' },
        'Thursday': { start: '08:00', end: '19:00' },
        'Friday': { start: '08:00', end: '19:00' },
        'Saturday': { start: '07:00', end: '18:00' },
        'Sunday': { start: '07:00', end: '16:00' }
    };

    // Hàm kiểm tra xem thời gian có nằm trong giờ làm việc không
    function isWithinWorkingHours(time, day) {
        const dayName = day;
        const hours = workingHours[dayName];
        if (!hours) return false;
        
        return time >= hours.start && time <= hours.end;
    }

    // Hàm format thời gian từ 24h sang 12h với AM/PM
    function formatTime(time) {
        const [hours, minutes] = time.split(':');
        const hour = parseInt(hours);
        const period = hour >= 12 ? 'CH' : 'SA';
        const hour12 = hour % 12 || 12;
        return `${hour12}:${minutes} ${period}`;
    }

    // Xử lý time picker
    if (timeInput) {
        // Thêm xử lý phím ESC để đóng time picker
        timeInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.blur();
            }
        });

        // Xử lý khi thay đổi giờ
        timeInput.addEventListener('change', function() {
            const selectedDate = new Date(dateInput.value);
            const dayName = selectedDate.toLocaleDateString('en-US', { weekday: 'long' });
            
            if (!isWithinWorkingHours(this.value, dayName)) {
                Swal.fire({
                    title: 'Thông báo',
                    text: 'Vui lòng chọn giờ trong khung giờ làm việc!',
                    icon: 'warning',
                    confirmButtonText: 'OK'
                });
                this.value = '';
            }
        });
    }

    // Xử lý form đặt lịch
    if (appointmentForm) {
        appointmentForm.removeAttribute('action');
        appointmentForm.removeAttribute('method');

        appointmentForm.addEventListener('submit', function(event) {
            event.preventDefault();
            if (!validateForm()) return false;

            const name = document.getElementById('name').value || 'Quý khách';
            const dateInput = document.getElementById('date').value;
            const timeValue = document.getElementById('time').value;

            const date = new Date(dateInput);
            const dayOfWeek = ['Chủ nhật', 'Thứ hai', 'Thứ ba', 'Thứ tư', 'Thứ năm', 'Thứ sáu', 'Thứ bảy'][date.getDay()];
            const formattedDate = `${dayOfWeek}, ngày ${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`;
            const formattedTime = formatTimeToVietnamese(timeValue);

            showSuccessMessage(name, formattedTime, formattedDate);
            this.reset();
            if (specificIssueContainer) specificIssueContainer.style.display = 'none';
        });
    }

    // Hiển thị textarea khi chọn "Vấn đề cụ thể"
    document.querySelectorAll('input[name="reason"]').forEach(function(radio) {
        radio.addEventListener('change', function() {
            if (this.id === 'specific' && specificIssueContainer) {
                specificIssueContainer.style.display = 'block';
                document.getElementById('specificIssueDetail').focus();
            } else if (specificIssueContainer) {
                specificIssueContainer.style.display = 'none';
            }
        });
    });

    // Click vào reason-box cũng chọn radio
    document.querySelectorAll('.reason-box').forEach(function(box) {
        box.addEventListener('click', function() {
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
                radio.dispatchEvent(new Event('change'));
            }
        });
    });

    // Validate form
    function validateForm() {
        const nameInput = document.getElementById('name');
        if (!nameInput || !nameInput.value.trim()) {
            alert('Vui lòng nhập họ tên của bạn');
            nameInput?.focus();
            return false;
        }
        const emailInput = document.getElementById('email');
        if (!emailInput || !emailInput.value.trim()) {
            alert('Vui lòng nhập email của bạn');
            emailInput?.focus();
            return false;
        }
        const phoneInput = document.getElementById('recordno');
        if (!phoneInput || !phoneInput.value.trim()) {
            alert('Vui lòng nhập số điện thoại của bạn');
            phoneInput?.focus();
            return false;
        }
        const dateInput = document.getElementById('date');
        if (!dateInput || !dateInput.value) {
            alert('Vui lòng chọn ngày hẹn');
            dateInput?.focus();
            return false;
        }
        const timeField = document.getElementById('time');
        if (!timeField || !timeField.value) {
            alert('Vui lòng chọn giờ hẹn');
            timeField?.focus();
            return false;
        }

        // Kiểm tra thời gian làm việc
        const selectedDate = new Date(dateInput.value);
        const dayOfWeek = selectedDate.getDay(); // 0: CN, 1-5: T2-T6, 6: T7
        const timeValue = timeField.value;
        const [hours, minutes] = timeValue.split(':').map(Number);
        const selectedTime = hours + minutes/60; // Chuyển đổi thành giờ thập phân

        // Xác định khung giờ làm việc dựa trên ngày trong tuần
        let openTime, closeTime;
        if (dayOfWeek >= 1 && dayOfWeek <= 5) {
            // Thứ 2 đến Thứ 6: 8:00 - 19:00
            openTime = 8;
            closeTime = 19;
        } else {
            // Thứ 7 và Chủ nhật: 9:00 - 16:00
            openTime = 9;
            closeTime = 16;
        }

        // Kiểm tra nếu giờ không nằm trong khung giờ làm việc
        if (selectedTime < openTime || selectedTime >= closeTime) {
            const dayNames = ["Chủ nhật", "Thứ hai", "Thứ ba", "Thứ tư", "Thứ năm", "Thứ sáu", "Thứ bảy"];
            const dayName = dayNames[dayOfWeek];
            
            if (dayOfWeek >= 1 && dayOfWeek <= 5) {
                alert(`${dayName} chúng tôi chỉ làm việc từ 8:00 đến 19:00. Vui lòng chọn thời gian khác.`);
            } else {
                alert(`${dayName} chúng tôi chỉ làm việc từ 9:00 đến 16:00. Vui lòng chọn thời gian khác.`);
            }
            return false;
        }

        const specificRadio = document.getElementById('specific');
        const specificDetail = document.getElementById('specificIssueDetail');
        if (specificRadio?.checked && specificDetail && !specificDetail.value.trim()) {
            alert('Vui lòng mô tả vấn đề răng miệng bạn đang gặp phải');
            specificDetail.focus();
            return false;
        }
        return true;
    }

    // Định dạng giờ kiểu Việt Nam
    function formatTimeToVietnamese(timeValue) {
        if (!timeValue) return '';
        const [hours, minutes] = timeValue.split(':');
        const hour = parseInt(hours);
        const period = hour >= 12 ? 'Chiều' : 'Sáng';
        const displayHour = hour > 12 ? hour - 12 : hour;
        return `${displayHour}:${minutes} ${period}`;
    }

    // Hiển thị modal thông báo thành công
    function showSuccessMessage(name, time, date) {
        let successModal = document.getElementById('appointmentSuccessModal');
        if (!successModal) {
            const modalHtml = `
            <div class="modal fade" id="appointmentSuccessModal" tabindex="-1" aria-labelledby="appointmentSuccessModalLabel" aria-hidden="true">
              <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title" id="appointmentSuccessModalLabel">Đặt lịch thành công</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                  </div>
                  <div class="modal-body">
                    <img src="/static/images/logo.svg" alt="PrimeCare Logo" class="modal-logo">
                    <div class="success-icon">
                      <i class="fa fa-check-circle"></i>
                    </div>
                    <p id="appointmentSuccessMessage"></p>
                    <p class="appointment-time" id="appointmentTime"></p>
                    <p class="appointment-follow">Nhân viên sẽ sớm liên hệ lại với bạn</p>
                    <p class="appointment-closing">Hẹn gặp lại bạn ở PrimeCare <span class="heart-emoji">❤️</span></p>
                  </div>
                  <div class="modal-footer">
                    <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Đóng</button>
                  </div>
                </div>
              </div>
            </div>`;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            successModal = document.getElementById('appointmentSuccessModal');
            // Thêm CSS nếu chưa có
            if (!document.getElementById('appointment-modal-styles')) {
                const styles = `
                <style id="appointment-modal-styles">
                    #appointmentSuccessModal .modal-content { border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); border: none; }
                    #appointmentSuccessModal .modal-header { background: linear-gradient(135deg, #34c3ff 0%, #4a90e2 100%); color: white; border-radius: 15px 15px 0 0; padding: 15px 20px; border: none; }
                    #appointmentSuccessModal .btn-close-white { filter: brightness(0) invert(1); }
                    #appointmentSuccessModal .modal-body { padding: 30px 25px; text-align: center; }
                    #appointmentSuccessModal .success-icon { margin: 20px auto; width: 80px; height: 80px; background: rgba(40, 167, 69, 0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; }
                    #appointmentSuccessModal .success-icon i { font-size: 45px; color: #28a745; }
                    #appointmentSuccessModal #appointmentSuccessMessage { font-size: 18px; margin: 15px 0; }
                    #appointmentSuccessModal .highlight { color: #34c3ff; font-weight: bold; }
                    #appointmentSuccessModal .appointment-time { font-size: 17px; margin: 20px 0; padding: 12px; background: rgba(52, 195, 255, 0.1); border-radius: 8px; font-weight: 500; }
                    #appointmentSuccessModal .appointment-follow { margin: 15px 0; color: #666; }
                    #appointmentSuccessModal .appointment-closing { margin-top: 20px; font-weight: 500; }
                    #appointmentSuccessModal .heart-emoji { color: #ff3366; }
                    #appointmentSuccessModal .modal-logo { max-width: 120px; margin: 0 auto 15px; }
                    #appointmentSuccessModal .modal-footer { border-top: 1px solid rgba(0,0,0,0.05); }
                    #appointmentSuccessModal .modal-footer .btn-primary { background: #34c3ff; border-color: #34c3ff; padding: 8px 20px; font-weight: 500; }
                    #appointmentSuccessModal .modal-footer .btn-primary:hover { background: #28a0d5; }
                </style>`;
                document.head.insertAdjacentHTML('beforeend', styles);
            }
        }
        // Cập nhật nội dung
        const successMessage = document.getElementById('appointmentSuccessMessage');
        const appointmentTime = document.getElementById('appointmentTime');
        if (successMessage) {
            successMessage.innerHTML = `Cảm ơn <span class="highlight">${name}</span> đã tin tưởng Nha khoa PrimeCare.`;
        }
        if (appointmentTime) {
            appointmentTime.innerHTML = `<strong>${time} - ${date}</strong>`;
        }
        // Hiển thị modal
        try {
            if (typeof bootstrap !== 'undefined') {
                const modal = new bootstrap.Modal(successModal);
                modal.show();
            } else {
                successModal.style.display = 'block';
                successModal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
                successModal.classList.add('show');
                // Đóng modal khi click nút đóng
                const closeButtons = successModal.querySelectorAll('[data-bs-dismiss="modal"], .btn-primary');
                closeButtons.forEach(btn => {
                    btn.addEventListener('click', function() {
                        successModal.style.display = 'none';
                        successModal.classList.remove('show');
                    });
                });
            }
        } catch (error) {
            alert(`Đặt lịch thành công! Cảm ơn ${name} đã tin tưởng Nha khoa PrimeCare. Lịch hẹn của bạn: ${time} - ${date}`);
        }
    }

    // Xử lý khi chọn ngày
    dateInput.addEventListener('change', function() {
        const selectedDate = new Date(this.value);
        const dayName = selectedDate.toLocaleDateString('en-US', { weekday: 'long' });
        const hours = workingHours[dayName];
        
        if (hours) {
            timeInput.min = hours.start;
            timeInput.max = hours.end;
        }
    });
});