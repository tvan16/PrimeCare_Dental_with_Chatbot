class Chatbot {
    constructor() {
        this.container = document.querySelector('.chatbot-container');
        this.toggleBtn = document.querySelector('.chatbot-toggle');
        this.minimizeBtn = document.querySelector('.chatbot-minimize');
        this.input = document.querySelector('.chatbot-input');
        this.sendBtn = document.querySelector('.chatbot-send');
        this.body = document.querySelector('.chatbot-body');
        this.loading = document.querySelector('.chatbot-loading');
        
        this.isOpen = false;
        this.isProcessing = false;

        // Đảm bảo các elements tồn tại trước khi khởi tạo
        if (!this.container || !this.toggleBtn) {
            console.error('Chatbot elements not found');
            return;
        }
        
        // Đảm bảo container được hiển thị
        this.container.style.display = 'flex';
        
        this.initializeEventListeners();
        this.loadChatHistory(); // Khôi phục lịch sử chat khi khởi tạo
        this.restoreChatbotState(); // Khôi phục trạng thái mở/thu nhỏ
        this.ensureWelcomeMessage(); // Đảm bảo luôn có câu chào đầu tiên
    }
    
    initializeEventListeners() {
        // Toggle chatbot
        this.toggleBtn.addEventListener('click', () => this.toggleChatbot());

        // Minimize chatbot
        this.minimizeBtn.addEventListener('click', () => this.minimizeChatbot());
        
        // Send message on button click
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        // Send message on Enter key
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
        }
    });
    }
    
    toggleChatbot() {
        this.isOpen = !this.isOpen;
        if (this.isOpen) {
            this.container.classList.remove('minimized');
            this.container.classList.add('active');
            this.toggleBtn.style.display = 'none';
            this.input.focus();
        } else {
            this.container.classList.remove('active');
            this.toggleBtn.style.display = 'flex';
        }
        this.saveChatbotState();
    }
    
    minimizeChatbot() {
        this.container.classList.toggle('minimized');
        if (this.container.classList.contains('minimized')) {
            this.isOpen = false;
            this.container.classList.remove('active');
            this.toggleBtn.style.display = 'flex';
        }
        this.saveChatbotState();
    }
    
    showWelcomeMessage() {
        const welcomeMessage = {
            text: "👋 Xin chào! Tôi là trợ lý ảo của Nha khoa PrimeCare. Tôi có thể giúp bạn tìm hiểu thông tin về các dịch vụ, bác sĩ của chúng tôi hoặc giải đáp thắc mắc về nha khoa. Bạn cần hỗ trợ gì hôm nay? 😊",
            time: new Date().toLocaleTimeString()
        };
        this.addMessage(welcomeMessage.text, 'bot', welcomeMessage.time);
    }
    
    async sendMessage() {
        const message = this.input.value.trim();
        if (!message || this.isProcessing) return;
        
        // Add user message
        this.addMessage(message, 'user');
        this.input.value = '';
        
        // Show loading indicator
        this.isProcessing = true;
        this.loading.classList.add('active');
        
        try {
            const response = await this.getChatbotResponse(message);
            this.addMessage(response.response, 'bot');
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.', 'bot');
        } finally {
            this.isProcessing = false;
            this.loading.classList.remove('active');
        }
    }
    
    async getChatbotResponse(message) {
        try {
            const response = await fetch('/chatbot/api/', {
                method: 'POST',
            headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ message })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching chatbot response:', error);
            throw error;
        }
    }

    getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
                }
        }
        return '';
    }
    
    addMessage(text, sender, time = new Date().toLocaleTimeString()) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.innerHTML = this.formatMessage(text);
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = time;
        
        messageDiv.appendChild(messageText);
        messageDiv.appendChild(messageTime);
        
        this.body.appendChild(messageDiv);
        this.scrollToBottom();
        this.saveChatHistory(); // Lưu lại lịch sử chat mỗi khi có tin nhắn mới
    }
    
    formatMessage(text) {
        // Convert markdown links to HTML
        text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
        
        // Convert markdown bold to HTML
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Convert markdown italic to HTML
        text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        
        // Convert markdown headings to HTML
        text = text.replace(/^### (.*$)/gm, '<h3>$1</h3>');
        text = text.replace(/^## (.*$)/gm, '<h2>$1</h2>');
        
        // Convert line breaks to HTML
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }
    
    scrollToBottom() {
        this.body.scrollTop = this.body.scrollHeight;
    }

    saveChatHistory() {
        localStorage.setItem('primecare_chat_history', this.body.innerHTML);
    }

    loadChatHistory() {
        const history = localStorage.getItem('primecare_chat_history');
        if (history) {
            this.body.innerHTML = history;
        }
    }

    ensureWelcomeMessage() {
        // Nếu chưa có câu chào ở đầu, thêm vào đầu đoạn chat
        const firstMsg = this.body.querySelector('.bot-message .message-text');
        const welcomeText = "Xin chào! Tôi là trợ lý ảo của Nha khoa PrimeCare. Tôi có thể giúp bạn tìm hiểu thông tin về các dịch vụ, bác sĩ của chúng tôi hoặc giải đáp thắc mắc về nha khoa. Bạn cần hỗ trợ gì hôm nay? 😊";
        if (!firstMsg || !firstMsg.textContent.includes("Xin chào! Tôi là trợ lý ảo của Nha khoa PrimeCare")) {
            // Thêm vào đầu
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot-message';
            const messageText = document.createElement('div');
            messageText.className = 'message-text';
            messageText.innerHTML = welcomeText;
            const messageTime = document.createElement('div');
            messageTime.className = 'message-time';
            messageTime.textContent = new Date().toLocaleTimeString();
            messageDiv.appendChild(messageText);
            messageDiv.appendChild(messageTime);
            this.body.insertBefore(messageDiv, this.body.firstChild);
            this.saveChatHistory();
        }
    }

    saveChatbotState() {
        // Lưu trạng thái mở/thu nhỏ vào localStorage
        localStorage.setItem('primecare_chatbot_isOpen', this.isOpen ? '1' : '0');
        localStorage.setItem('primecare_chatbot_minimized', this.container.classList.contains('minimized') ? '1' : '0');
    }

    restoreChatbotState() {
        // Khôi phục trạng thái mở/thu nhỏ từ localStorage
        const isOpen = localStorage.getItem('primecare_chatbot_isOpen');
        const minimized = localStorage.getItem('primecare_chatbot_minimized');
        if (isOpen === '1') {
            this.isOpen = true;
            this.container.classList.add('active');
            this.toggleBtn.style.display = 'none';
        } else {
            this.isOpen = false;
            this.container.classList.remove('active');
            this.toggleBtn.style.display = 'flex';
        }
        if (minimized === '1') {
            this.container.classList.add('minimized');
        } else {
            this.container.classList.remove('minimized');
        }
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new Chatbot();
});