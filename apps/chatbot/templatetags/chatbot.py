import json
import os
import numpy as np
import re
import faiss
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
import google.generativeai as genai
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables or .env file")
genai.configure(api_key=API_KEY)

# Available Gemini models to try
GEMINI_MODELS = ["gemini-2.0-flash"]

# Welcome messages
WELCOME_MESSAGES = [
    "👋 Xin chào! Tôi là trợ lý ảo của Nha khoa PrimeCare. Tôi có thể giúp bạn tìm hiểu thông tin về các dịch vụ, bác sĩ của chúng tôi hoặc giải đáp thắc mắc về nha khoa. Bạn cần hỗ trợ gì hôm nay? 😊",
    "👋 Hello! I'm the virtual assistant for PrimeCare Dental Clinic. I can help you learn about our services, doctors, or answer dental questions. How can I assist you today? 😊"
]

# Appointment booking message
BOOKING_MESSAGE_VI = "\n\n📅 **Đặt lịch hẹn:** Bạn có thể [đặt lịch hẹn trực tuyến](frontend/pages/contact.html) hoặc gọi số 1900-6900 để được hỗ trợ trực tiếp."
BOOKING_MESSAGE_EN = "\n\n📅 **Book an appointment:** You can [book an appointment online](frontend/pages/contact.html) or call 1900-6900 for direct assistance."

class AgentRole(Enum):
    DENTAL_CONSULTANT = auto()
    CUSTOMER_SERVICE = auto()

@dataclass
class Message:
    role: str  # "user" or "assistant"
    content: str
    agent_type: Optional[AgentRole] = None

class EmbeddingModel:
    def __init__(self):
        # Import here to ensure dependencies are available
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch
            
            # Load pre-trained model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            self.model_loaded = True
        except Exception as e:
            print(f"Warning: Could not load embedding model: {str(e)}")
            print("Falling back to simple embedding method")
            self.model_loaded = False
            
    def get_embeddings(self, texts):
        """Convert texts to embeddings"""
        if not self.model_loaded:
            # Fallback to simple embedding method
            return self._get_simple_embeddings(texts)
            
        try:
            import torch
            
            # Tokenize the input texts
            encoded_input = self.tokenizer(texts, padding=True, truncation=True, 
                                          max_length=512, return_tensors='pt').to(self.device)
            
            # Get embeddings without gradient calculation
            with torch.no_grad():
                model_output = self.model(**encoded_input)
                
            # Use CLS token embedding as the sentence embedding
            sentence_embeddings = model_output[0][:, 0]
            # Normalize the embeddings
            sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
            
            return sentence_embeddings.cpu().numpy()
        except Exception as e:
            print(f"Error during embedding generation: {str(e)}")
            print("Falling back to simple embedding method")
            return self._get_simple_embeddings(texts)
    
    def _get_simple_embeddings(self, texts):
        """Simple fallback embedding method using character frequency"""
        import numpy as np
        
        # Create a simple character-based embedding (not ideal but works as fallback)
        embeddings = []
        
        for text in texts:
            # Count character frequencies (simple embedding)
            # Expanded to support Vietnamese characters
            char_freq = {}
            for char in text:
                if char in char_freq:
                    char_freq[char] += 1
                else:
                    char_freq[char] = 1
                    
            # Convert to vector and normalize
            chars = sorted(char_freq.keys())
            vec = np.array([char_freq[c] for c in chars])
            total = sum(vec) + 1e-10  # Avoid division by zero
            vec = vec / total
            
            # Create fixed-size embedding by hashing
            embedding = np.zeros(384)
            for i, val in enumerate(vec):
                idx = hash(chars[i]) % 384
                embedding[idx] += val
                
            embeddings.append(embedding)
            
        return np.array(embeddings)

class DataProcessor:
    def __init__(self, dental_path: str, doctor_path: str, price_path: str = "data/service-prices.json", financial_path: str = "data/financial_services.json"):
        self.embedding_model = EmbeddingModel()
        self.dental_data = self._load_json(dental_path)
        self.doctor_data = self._load_json(doctor_path)
        self.dental_index, self.dental_texts = self._create_vector_index(self.dental_data, "dental")
        self.doctor_index, self.doctor_texts = self._create_vector_index(self.doctor_data, "doctor")
        
        # Khởi tạo processors cho giá dịch vụ và dịch vụ tài chính
        self.price_processor = PriceProcessor(price_path)
        self.financial_processor = FinancialProcessor(financial_path)
        
    def _load_json(self, path: str) -> List[Dict[str, Any]]:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
            
    def _create_vector_index(self, data: List[Dict[str, Any]], data_type: str):
        # Extract text content from JSON data
        texts = []
        for item in data:
            if data_type == "dental":
                # Handle dental articles from news.detail.json
                title = item.get('title', '')
                content_parts = []
                
                # Extract content from sections
                sections = item.get('sections', [])
                for section in sections:
                    heading = section.get('heading', '')
                    content = section.get('content', '')
                    content_parts.append(f"{heading}: {content}")
                
                content = " ".join(content_parts)
                texts.append(f"{title} {content}")
            else:  # doctor
                # Handle doctor information from doctors.json
                name = item.get('name', '')
                area = item.get('area', '')
                education = item.get('education', '')
                certificate = item.get('certificate', '')
                texts.append(f"{name} {area} {education} {certificate}")
                
        # Create embeddings
        embeddings = self.embedding_model.get_embeddings(texts)
        
        # Create FAISS index
        try:
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings.astype(np.float32))
        except Exception as e:
            print(f"Error creating index: {str(e)}")
            # Create a dummy index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            # Add a small amount of data to avoid empty index
            if len(embeddings) > 0:
                index.add(embeddings[0:1].astype(np.float32))
        
        return index, texts
        
    def search_dental_data(self, query: str, k: int = 3):
        query_vector = self.embedding_model.get_embeddings([query])
        distances, indices = self.dental_index.search(query_vector.astype(np.float32), k)
        results = [self.dental_data[i] for i in indices[0]]
        
        # Extract the URLs for the "Tìm hiểu thêm" section
        for result in results:
            if 'url' not in result:
                result['url'] = "https://primecare.vn"  # Default URL if none found
        
        return results
        
    def search_doctor_data(self, query: str, k: int = 5):
        query_vector = self.embedding_model.get_embeddings([query])
        distances, indices = self.doctor_index.search(query_vector.astype(np.float32), k)
        return [self.doctor_data[i] for i in indices[0]]

    def get_doctor_count(self):
        """Return the total number of doctors"""
        return len(self.doctor_data)
    
    def get_doctor_names(self):
        """Return a list of all doctor names"""
        return [doc.get('name', 'Unknown') for doc in self.doctor_data]
    
    def get_doctors_by_region(self, region: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get doctors by region (miền Nam, miền Bắc, miền Trung)"""
        # Normalize region names to handle variations
        normalized_region = region.lower()
        region_mapping = {
            "miền nam": ["miền nam", "phía nam", "nam"],
            "miền bắc": ["miền bắc", "phía bắc", "bắc"],
            "miền trung": ["miền trung", "phía trung", "trung"]
        }
        
        # Find the standardized region
        target_region = None
        for std_region, variations in region_mapping.items():
            if any(variation in normalized_region for variation in variations):
                target_region = std_region
                break
        
        if target_region is None:
            return []
            
        # Match the standardized region to the actual values in the data
        matching_doctors = []
        for doctor in self.doctor_data:
            doctor_area = doctor.get('area', '').lower()
            
            # Check if the doctor's area matches any variation of the target region
            for variation in region_mapping[target_region]:
                if variation in doctor_area:
                    matching_doctors.append(doctor)
                    break
                    
        return matching_doctors[:limit]
    
    def get_doctors_by_education(self, education_query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get doctors by education (university or training)"""
        education_query = education_query.lower()
        matching_doctors = []
        
        for doctor in self.doctor_data:
            doctor_education = doctor.get('education', '').lower()
            
            if education_query in doctor_education:
                matching_doctors.append(doctor)
                
        return matching_doctors[:limit]
    
    def get_doctors_by_certificate(self, certificate_query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get doctors by certificate"""
        certificate_query = certificate_query.lower()
        matching_doctors = []
        
        for doctor in self.doctor_data:
            doctor_certificate = doctor.get('certificate', '').lower()
            
            if certificate_query in doctor_certificate:
                matching_doctors.append(doctor)
                
        return matching_doctors[:limit]
    
    def get_price_info(self, query: str, is_vietnamese: bool = True) -> str:
        """Lấy thông tin giá cho một dịch vụ cụ thể"""
        # Thử tìm kiếm dịch vụ chính xác
        exact_match = False
        
        # Kiểm tra xem query có chứa từ "invisalign express" không
        if "invisalign express" in query.lower() or "niềng trong suốt express" in query.lower():
            services = self.price_processor.get_service_by_exact_name("Gói niềng trong suốt Invisalign Express")
            if services:
                exact_match = True
        
        # Nếu không có kết quả chính xác, dùng tìm kiếm thông thường
        if not exact_match:
            services = self.price_processor.search_service(query)
        
        # Nếu vẫn không có kết quả, thử tìm một số từ khóa đặc biệt
        if not services:
            special_keywords = {
                "invisalign": "Gói niềng trong suốt",
                "niềng răng": "niềng răng",
                "implant": "Implant",
                "trồng răng": "Implant",
                "veneer": "veneer",
                "dán sứ": "veneer",
                "tẩy trắng": "Tẩy trắng"
            }
            
            for keyword, search_term in special_keywords.items():
                if keyword in query.lower():
                    services = self.price_processor.search_service(search_term)
                    if services:
                        break
        
        return self.price_processor.format_price_info(services, is_vietnamese)
    
    def get_affordable_services(self, budget: float, is_vietnamese: bool = True) -> str:
        """Gợi ý dịch vụ dựa trên ngân sách"""
        affordable_services = self.price_processor.get_services_by_budget(budget)
        return self.price_processor.format_budget_recommendations(budget, affordable_services, is_vietnamese)
    
    def get_payment_plans(self, is_vietnamese: bool = True) -> str:
        """Lấy thông tin về các kế hoạch thanh toán"""
        return self.financial_processor.get_payment_plans(is_vietnamese)
    
    def get_special_promotions(self, is_vietnamese: bool = True) -> str:
        """Lấy thông tin về các chương trình khuyến mãi đặc biệt"""
        return self.financial_processor.get_special_promotions(is_vietnamese)
    
    def get_current_promotions(self, is_vietnamese: bool = True) -> str:
        """Lấy thông tin về các chương trình khuyến mãi hiện tại"""
        return self.financial_processor.get_current_seasonal_promotions(is_vietnamese)
    
    def get_all_promotions(self, is_vietnamese: bool = True) -> str:
        """Lấy thông tin về tất cả các chương trình khuyến mãi theo mùa"""
        return self.financial_processor.get_all_seasonal_promotions(is_vietnamese)

class PriceProcessor:
    def __init__(self, price_data_path: str):
        self.price_data = self._load_price_data(price_data_path)
        self.categories = self._extract_categories()
        self.price_ranges = self._calculate_price_ranges()

        # Từ điển đồng nghĩa mở rộng cho các dịch vụ
        self.service_synonyms = {
            # Niềng răng
            "niềng răng invisalign": ["niềng trong suốt", "invisalign", "niềng trong", "niềng suốt", "niềng tháo lắp"],
            "niềng răng invisalign express": ["invisalign express", "niềng express", "express invisalign", "niềng nhanh"],
            "niềng răng invisalign lite": ["invisalign lite", "niềng lite", "lite invisalign", "niềng ngắn hạn"],
            "niềng răng invisalign moderate": ["invisalign moderate", "moderate invisalign", "niềng trung bình"],
            "niềng răng invisalign comprehensive": ["invisalign comprehensive", "comprehensive invisalign", "niềng toàn diện"],
            "niềng răng invisalign first": ["invisalign first", "first invisalign", "niềng cho trẻ em"],
            "niềng răng mắc cài sứ": ["mắc cài sứ", "niềng sứ", "niềng răng sứ", "braces sứ"],
            "niềng răng mắc cài kim loại": ["mắc cài kim loại", "niềng kim loại", "braces kim loại"],
            "niềng răng mắc cài pha lê": ["mắc cài pha lê", "niềng pha lê", "braces pha lê"],
            
            # Implant
            "trồng răng implant": ["cấy ghép implant", "implant", "cấy răng", "ghép răng"],
            "implant straumann": ["cấy ghép straumann", "straumann", "răng straumann"],
            "implant neodent": ["cấy ghép neodent", "neodent", "răng neodent", "neodent acqua"],
            "implant dentium": ["cấy ghép dentium", "dentium", "răng dentium"],
            "all-on-4": ["all on 4", "all on four", "trồng răng toàn hàm", "phục hình toàn hàm"],
            "cấy ghép implant combo": ["combo implant", "gói implant", "trồng răng trọn gói"],
            
            # Nha khoa tổng quát
            "nhổ răng khôn": ["răng khôn", "nhổ răng số 8", "răng số 8", "răng góc"],
            "nhổ răng thường": ["nhổ răng", "rút răng", "rút răng thường"],
            "điều trị tủy": ["chữa tủy", "trị tủy", "lấy tủy", "root canal"],
            "điều trị nha chu": ["trị nha chu", "chữa nha chu", "viêm nha chu", "nướu"],
            "lấy cao răng": ["cạo vôi răng", "vệ sinh răng", "làm sạch răng"],
            "trám răng": ["hàn răng", "bịt răng", "lấp lỗ sâu", "trám răng sâu"],
            
            # Nha khoa thẩm mỹ
            "răng sứ": ["bọc răng sứ", "crown sứ", "mão sứ", "mão răng"],
            "răng sứ emax": ["emax", "sứ emax", "bọc emax", "mão emax"],
            "răng sứ zirconia": ["zirconia", "zircad", "răng zirconia", "bọc zirconia"],
            "dán sứ veneer": ["veneer", "mặt dán", "dán răng", "dán sứ"],
            "tẩy trắng răng": ["làm trắng răng", "làm trắng", "tẩy răng", "răng trắng"],
            "tẩy trắng express": ["tẩy nhanh", "làm trắng nhanh", "tẩy cấp tốc"],
            "tẩy trắng zoom laser": ["zoom laser", "tẩy laser", "làm trắng laser"],
            
            # Nha khoa trẻ em
            "nha khoa trẻ em": ["răng trẻ em", "nha khoa nhi", "răng trẻ", "răng sữa"],
            "trám răng sữa": ["hàn răng sữa", "trám răng trẻ em"],
            "nhổ răng sữa": ["rút răng sữa", "nhổ răng trẻ em"],
            
            # Nha khoa phục hồi
            "phục hình": ["phục hồi răng", "làm lại răng", "tái tạo răng"],
            "cầu răng": ["bridge", "cầu răng sứ", "cầu nối răng"],
            "phục hình tháo lắp": ["hàm giả", "răng giả tháo lắp", "denture"],
            "inlay": ["onlaSSy", "trám đúc", "trám sứ"]
        }

    def _load_price_data(self, path: str) -> Dict[str, Any]:
        """Tải dữ liệu giá từ file JSON"""
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu giá: {str(e)}")
            return {"metadata": {}, "services_by_category": {}}
    
    def _extract_categories(self) -> List[str]:
        """Trích xuất danh sách các loại dịch vụ"""
        return list(self.price_data.get("services_by_category", {}).keys())
    
    def _calculate_price_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Tính toán khoảng giá cho mỗi danh mục dịch vụ"""
        price_ranges = {}
        
        for category, services in self.price_data.get("services_by_category", {}).items():
            min_price = float('inf')
            max_price = 0
            
            for service in services:
                price_display = service.get("Giá hiển thị", "")
                if price_display:
                    # Trích xuất số từ chuỗi giá
                    numbers = re.findall(r'\d+(?:\.\d+)?', price_display.replace(',', ''))
                    if numbers:
                        try:
                            numbers = [float(num) for num in numbers]
                            min_price = min(min_price, min(numbers))
                            max_price = max(max_price, max(numbers))
                        except:
                            pass
            
            if min_price != float('inf') and max_price > 0:
                price_ranges[category] = (min_price, max_price)
                
        return price_ranges
    
    def get_all_categories(self) -> List[str]:
        """Trả về tất cả danh mục dịch vụ"""
        return self.categories
    
    def get_services_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Lấy tất cả dịch vụ trong một danh mục"""
        if category in self.categories:
            return self.price_data["services_by_category"][category]
        return []
    
    def search_service(self, query: str) -> List[Dict[str, Any]]:
        """Tìm kiếm dịch vụ phù hợp với từ khóa"""
        if not query or not isinstance(query, str) or len(query.strip()) < 2:
            return []
            
        query = query.lower().strip()
        results = []
        
        # Loại bỏ các từ phổ biến không liên quan
        stop_words = ["giá", "chi phí", "phí", "bao nhiêu", "tiền", "đắt", "rẻ", 
                    "báo giá", "dịch vụ", "là", "có", "của", "thế nào"]
        for word in stop_words:
            query = query.replace(word, " ")
            
        # Chuẩn hóa truy vấn
        query = " ".join(query.split())
        
        # Tách query thành các từ khóa riêng lẻ
        query_words = query.split()
        
        # Kiểm tra từ đồng nghĩa và mở rộng truy vấn
        expanded_queries = [query]
        
        # Thêm các truy vấn mở rộng từ từ điển đồng nghĩa
        for service, synonyms in self.service_synonyms.items():
            for synonym in synonyms:
                if synonym in query:
                    if service not in expanded_queries:
                        expanded_queries.append(service)
                    break
        
        # Xử lý các trường hợp đặc biệt
        service_specific_words = {
            "invisalign express": ["express", "invisalign", "niềng trong suốt express"],
            "niềng răng": ["niềng", "braces", "chỉnh nha"],
            "trồng răng": ["implant", "cấy ghép", "trồng"],
            "tẩy trắng": ["tẩy", "làm trắng", "whitening"],
            "veneer": ["dán sứ", "mặt dán", "dán răng"]
        }
        
        for service, keywords in service_specific_words.items():
            if any(keyword in query for keyword in keywords):
                expanded_queries.append(service)
        
        # Thực hiện tìm kiếm với các truy vấn mở rộng
        matched_services = {}  # Dùng dict để tránh trùng lặp
        
        for expanded_query in expanded_queries:
            for category, services in self.price_data.get("services_by_category", {}).items():
                for service in services:
                    if "Tên dịch vụ" not in service or not isinstance(service.get("Tên dịch vụ"), str):
                        continue
                        
                    service_name = service.get("Tên dịch vụ", "").lower()
                    
                    # Kiểm tra match toàn bộ hoặc từng phần
                    if expanded_query in service_name:
                        service_copy = service.copy()
                        service_copy["Danh mục"] = category
                        
                        # Sử dụng tên dịch vụ làm key để tránh trùng lặp
                        matched_services[service_name] = service_copy
                        continue
                        
                    # Kiểm tra match từng từ
                    matched_words = 0
                    important_words = 0
                    for word in query_words:
                        if len(word) > 2 and word in service_name:
                            matched_words += 1
                            # Từ quan trọng có trọng số cao hơn
                            if word in ["invisalign", "express", "implant", "straumann", "veneer", "emax"]:
                                important_words += 1
                    
                    # Nếu khớp đủ từ quan trọng hoặc nhiều từ thông thường
                    if important_words >= 1 or matched_words >= 2:
                        service_copy = service.copy()
                        service_copy["Danh mục"] = category
                        matched_services[service_name] = service_copy
        
        # Chuyển kết quả từ dict sang list
        results = list(matched_services.values())
        
        # Sắp xếp kết quả theo độ phù hợp
        if results and query_words:
            # Tính điểm phù hợp
            def relevance_score(service):
                name = service.get("Tên dịch vụ", "").lower()
                score = 0
                
                # Ưu tiên nếu tên dịch vụ chứa toàn bộ truy vấn
                if query in name:
                    score += 100
                
                # Tính điểm cho từng từ khóa phù hợp
                for word in query_words:
                    if word in name:
                        score += len(word)  # Từ dài có điểm cao hơn
                
                return score
                
            # Sắp xếp kết quả theo điểm giảm dần
            results.sort(key=relevance_score, reverse=True)
        
        return results
    
    def get_services_by_budget(self, budget: float) -> Dict[str, List[Dict[str, Any]]]:
        """Tìm dịch vụ phù hợp với ngân sách"""
        affordable_services = {}
        
        for category, services in self.price_data.get("services_by_category", {}).items():
            category_services = []
            
            for service in services:
                # Lấy giá khuyến mãi nếu có, nếu không thì lấy giá gốc
                price_str = service.get("Giá khuyến mãi", service.get("Giá gốc", ""))
                
                # Trích xuất số từ chuỗi giá
                numbers = re.findall(r'\d+(?:\.\d+)?', price_str.replace(',', ''))
                if numbers:
                    try:
                        numbers = [float(num) for num in numbers]
                        min_price = min(numbers)
                        
                        # Nếu giá thấp nhất trong dải giá nằm trong ngân sách
                        if min_price <= budget:
                            service_copy = service.copy()
                            service_copy["Danh mục"] = category
                            category_services.append(service_copy)
                    except:
                        pass
            
            if category_services:
                affordable_services[category] = category_services
                
        return affordable_services
    
    def format_price_info(self, services: List[Dict[str, Any]], is_vietnamese: bool = True) -> str:
        """Định dạng thông tin giá để hiển thị"""
        if not services:
            if is_vietnamese:
                return "Không tìm thấy thông tin giá cho dịch vụ này. Vui lòng thử tìm kiếm với tên dịch vụ khác hoặc liên hệ trực tiếp với chúng tôi để được tư vấn chi tiết."
            else:
                return "No price information found for this service. Please try with a different service name or contact us directly for detailed consultation."
        
        if is_vietnamese:
            result = "💲 **THÔNG TIN GIÁ DỊCH VỤ:**\n\n"
        else:
            result = "💲 **SERVICE PRICE INFORMATION:**\n\n"
                
        for i, service in enumerate(services):
            # Giới hạn số lượng kết quả hiển thị nếu có quá nhiều
            if i >= 5:  # Tối đa hiển thị 5 dịch vụ
                if is_vietnamese:
                    result += f"\n... và {len(services) - 5} dịch vụ khác phù hợp với yêu cầu của bạn."
                else:
                    result += f"\n... and {len(services) - 5} other services matching your request."
                break
                
            name = service.get("Tên dịch vụ", "")
            original_price = service.get("Giá gốc", "")
            discount = service.get("Giảm giá", "")
            discounted_price = service.get("Giá khuyến mãi", "")
            unit = service.get("Đơn vị", "")
            category = service.get("Danh mục", "")
            
            if name:
                if is_vietnamese:
                    result += f"## {name}\n"
                    if category:
                        result += f"**Danh mục:** {category}\n"
                    if original_price:
                        result += f"**Giá gốc:** {original_price}\n"
                    if discount and discount != "0%":
                        result += f"**Giảm giá:** {discount}\n"
                    if discounted_price and discounted_price != "":
                        result += f"**Giá khuyến mãi:** {discounted_price}\n"
                    elif original_price:
                        result += f"**Giá hiện tại:** {original_price}\n"
                    if unit:
                        result += f"**Đơn vị:** {unit}\n"
                else:
                    result += f"## {name}\n"
                    if category:
                        result += f"**Category:** {category}\n"
                    if original_price:
                        result += f"**Original price:** {original_price}\n"
                    if discount and discount != "0%":
                        result += f"**Discount:** {discount}\n"
                    if discounted_price and discounted_price != "":
                        result += f"**Promotional price:** {discounted_price}\n"
                    elif original_price:
                        result += f"**Current price:** {original_price}\n"
                    if unit:
                        result += f"**Unit:** {unit}\n"
                
                result += "\n"
        
        # Thêm ghi chú về chính sách giá
        if is_vietnamese:
            result += "*Xin lưu ý rằng giá có thể thay đổi dựa trên yêu cầu cụ thể và tình trạng răng miệng của từng người. Vui lòng liên hệ với chúng tôi để được tư vấn chi tiết nhất.*"
        else:
            result += "*Please note that prices may vary based on specific requirements and individual dental conditions. Please contact us for the most detailed consultation.*"
            
        return result
    
    def get_service_by_exact_name(self, service_name: str) -> List[Dict[str, Any]]:
        """Tìm kiếm dịch vụ chính xác theo tên"""
        service_name = service_name.lower().strip()
        results = []
        
        for category, services in self.price_data.get("services_by_category", {}).items():
            for service in services:
                if "Tên dịch vụ" in service and isinstance(service.get("Tên dịch vụ"), str):
                    if service.get("Tên dịch vụ", "").lower() == service_name:
                        service_copy = service.copy()
                        service_copy["Danh mục"] = category
                        results.append(service_copy)
        
        return results

    def format_budget_recommendations(self, budget: float, affordable_services: Dict[str, List[Dict[str, Any]]], is_vietnamese: bool = True) -> str:
        """Định dạng gợi ý dịch vụ dựa trên ngân sách"""
        if not affordable_services:
            if is_vietnamese:
                return f"💰 Với ngân sách {budget:,.0f} VND, hiện tại chúng tôi không có dịch vụ phù hợp. Vui lòng liên hệ trực tiếp với chúng tôi để được tư vấn về các lựa chọn phù hợp."
            else:
                return f"💰 With a budget of {budget:,.0f} VND, we currently don't have services that fit your budget. Please contact us directly for advice on suitable options."
        
        if is_vietnamese:
            result = f"💰 **GỢI Ý DỊCH VỤ PHÙ HỢP VỚI NGÂN SÁCH {budget:,.0f} VND:**\n\n"
        else:
            result = f"💰 **RECOMMENDED SERVICES FOR YOUR {budget:,.0f} VND BUDGET:**\n\n"
        
        for category, services in affordable_services.items():
            if is_vietnamese:
                result += f"## {category}\n"
            else:
                result += f"## {category}\n"
            
            # Giới hạn số dịch vụ hiển thị mỗi danh mục
            display_limit = 3
            for i, service in enumerate(services[:display_limit]):
                name = service.get("Tên dịch vụ", "")
                price = service.get("Giá khuyến mãi", service.get("Giá gốc", ""))
                
                if is_vietnamese:
                    result += f"- **{name}**: {price}\n"
                else:
                    result += f"- **{name}**: {price}\n"
            
            # Hiển thị số lượng dịch vụ khác nếu có
            remaining = len(services) - display_limit
            if remaining > 0:
                if is_vietnamese:
                    result += f"- *và {remaining} dịch vụ khác...*\n"
                else:
                    result += f"- *and {remaining} more services...*\n"
            
            result += "\n"
        
        # Thêm thông tin về các tùy chọn thanh toán
        if is_vietnamese:
            result += "**Bạn cũng có thể xem xét các tùy chọn trả góp của chúng tôi để tiếp cận các dịch vụ cao cấp hơn.**"
        else:
            result += "**You may also consider our installment payment options to access higher-tier services.**"
        
        return result

class FinancialProcessor:
    def __init__(self, financial_data_path: str):
        self.financial_data = self._load_financial_data(financial_data_path)
        
    def _load_financial_data(self, path: str) -> Dict[str, Any]:
        """Tải dữ liệu tài chính từ file JSON"""
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu tài chính: {str(e)}")
            return {"payment_plans": {}, "special_promotions": {}, "seasonal_promotions": {}}
    
    def get_payment_plans(self, is_vietnamese: bool = True) -> str:
        """Trả về thông tin về các kế hoạch thanh toán"""
        payment_plans = self.financial_data.get("payment_plans", {})
        
        if is_vietnamese:
            result = "💳 **CÁC PHƯƠNG THỨC THANH TOÁN & TRẢ GÓP:**\n\n"
        else:
            result = "💳 **PAYMENT & INSTALLMENT OPTIONS:**\n\n"
            
        for plan_id, plan in payment_plans.items():
            name = plan.get("name" if is_vietnamese else "name_en", "")
            description = plan.get("description" if is_vietnamese else "description_en", "")
            interest = plan.get("interest", "")
            min_cost = plan.get("min_treatment_cost", "")
            partners = plan.get("partners", [])
            
            result += f"### {name}\n"
            result += f"{description}\n"
            
            if interest:
                if is_vietnamese:
                    result += f"**Lãi suất:** {interest}\n"
                else:
                    result += f"**Interest:** {interest}\n"
                    
            if min_cost:
                if is_vietnamese:
                    result += f"**Chi phí điều trị tối thiểu:** {min_cost}\n"
                else:
                    result += f"**Minimum treatment cost:** {min_cost}\n"
                    
            if partners:
                if is_vietnamese:
                    result += f"**Đối tác ngân hàng:** {', '.join(partners)}\n"
                else:
                    result += f"**Banking partners:** {', '.join(partners)}\n"
                    
            result += "\n"
            
        return result
    
    def get_special_promotions(self, is_vietnamese: bool = True) -> str:
        """Trả về thông tin về các chương trình khuyến mãi đặc biệt"""
        special_promotions = self.financial_data.get("special_promotions", {})
        
        if is_vietnamese:
            result = "🎁 **KHUYẾN MÃI DÀNH CHO NHÓM ĐẶC BIỆT:**\n\n"
        else:
            result = "🎁 **SPECIAL GROUP PROMOTIONS:**\n\n"
            
        for promo_id, promo in special_promotions.items():
            name = promo.get("name" if is_vietnamese else "name_en", "")
            description = promo.get("description" if is_vietnamese else "description_en", "")
            discount = promo.get("discount" if is_vietnamese else "discount_en", "")
            conditions = promo.get("conditions" if is_vietnamese else "conditions_en", "")
            
            result += f"### {name}\n"
            result += f"{description}\n"
            
            if discount:
                if is_vietnamese:
                    result += f"**Giảm giá:** {discount}\n"
                else:
                    result += f"**Discount:** {discount}\n"
                    
            if conditions:
                if is_vietnamese:
                    result += f"**Điều kiện áp dụng:** {conditions}\n"
                else:
                    result += f"**Conditions:** {conditions}\n"
                    
            result += "\n"
            
        return result
    
    def get_current_seasonal_promotions(self, is_vietnamese: bool = True) -> str:
        """Trả về thông tin về các chương trình khuyến mãi theo mùa hiện tại"""
        seasonal_promotions = self.financial_data.get("seasonal_promotions", {})
        
        # Lấy ngày hiện tại
        from datetime import datetime
        now = datetime.now()
        current_month = now.month
        current_day = now.day
        
        # Xác định khuyến mãi hiện tại
        current_promos = []
        for promo_id, promo in seasonal_promotions.items():
            valid_period = promo.get("valid_period" if is_vietnamese else "valid_period_en", "")
            
            # Phân tích khoảng thời gian
            try:
                # Định dạng: "DD/MM - DD/MM hàng năm"
                period_parts = valid_period.split("-")
                start_part = period_parts[0].strip().split("/")
                end_part = period_parts[1].split("hàng năm")[0].strip().split("/")
                
                start_day = int(start_part[0])
                start_month = int(start_part[1])
                end_day = int(end_part[0])
                end_month = int(end_part[1])
                
                # Kiểm tra xem ngày hiện tại có trong khoảng thời gian hay không
                if (start_month < end_month and 
                    ((current_month > start_month and current_month < end_month) or
                     (current_month == start_month and current_day >= start_day) or
                     (current_month == end_month and current_day <= end_day))):
                    current_promos.append(promo)
                elif (start_month > end_month and  # Trường hợp khuyến mãi kéo dài từ năm cũ sang năm mới
                      ((current_month > start_month) or
                       (current_month < end_month) or
                       (current_month == start_month and current_day >= start_day) or
                       (current_month == end_month and current_day <= end_day))):
                    current_promos.append(promo)
                elif start_month == end_month and current_month == start_month:
                    if (start_day <= end_day and current_day >= start_day and current_day <= end_day) or \
                       (start_day > end_day and (current_day >= start_day or current_day <= end_day)):
                        current_promos.append(promo)
            except:
                # Bỏ qua nếu định dạng không hợp lệ
                pass
        
        if not current_promos:
            # Nếu không có khuyến mãi hiện tại, lấy khuyến mãi sắp tới
            upcoming_promo = None
            min_months_away = 12
            
            for promo_id, promo in seasonal_promotions.items():
                valid_period = promo.get("valid_period" if is_vietnamese else "valid_period_en", "")
                
                # Phân tích khoảng thời gian
                try:
                    period_parts = valid_period.split("-")
                    start_part = period_parts[0].strip().split("/")
                    
                    start_day = int(start_part[0])
                    start_month = int(start_part[1])
                    
                    # Tính số tháng đến khuyến mãi tiếp theo
                    months_away = (start_month - current_month) % 12
                    
                    # Nếu cùng tháng, so sánh ngày
                    if months_away == 0 and start_day <= current_day:
                        months_away = 12  # Đã qua, đợi đến năm sau
                        
                    if months_away < min_months_away:
                        min_months_away = months_away
                        upcoming_promo = promo
                except:
                    # Bỏ qua nếu định dạng không hợp lệ
                    pass
                
            if upcoming_promo:
                if is_vietnamese:
                    result = "🗓️ **CHƯƠNG TRÌNH KHUYẾN MÃI SẮP TỚI:**\n\n"
                else:
                    result = "🗓️ **UPCOMING PROMOTION:**\n\n"
                    
                name = upcoming_promo.get("name" if is_vietnamese else "name_en", "")
                description = upcoming_promo.get("description" if is_vietnamese else "description_en", "")
                discount = upcoming_promo.get("discount" if is_vietnamese else "discount_en", "")
                valid_period = upcoming_promo.get("valid_period" if is_vietnamese else "valid_period_en", "")
                
                result += f"### {name}\n"
                result += f"{description}\n"
                
                if discount:
                    if is_vietnamese:
                        result += f"**Giảm giá:** {discount}\n"
                    else:
                        result += f"**Discount:** {discount}\n"
                        
                if valid_period:
                    if is_vietnamese:
                        result += f"**Thời gian áp dụng:** {valid_period}\n"
                    else:
                        result += f"**Valid period:** {valid_period}\n"
                        
                return result
            else:
                if is_vietnamese:
                    return "Hiện không có chương trình khuyến mãi nào đang diễn ra. Vui lòng liên hệ chúng tôi để biết thêm chi tiết về các ưu đãi hiện có."
                else:
                    return "There are currently no ongoing seasonal promotions. Please contact us for more details about available offers."
        else:
            if is_vietnamese:
                result = "🔥 **CHƯƠNG TRÌNH KHUYẾN MÃI ĐANG DIỄN RA:**\n\n"
            else:
                result = "🔥 **CURRENT PROMOTIONS:**\n\n"
                
            for promo in current_promos:
                name = promo.get("name" if is_vietnamese else "name_en", "")
                description = promo.get("description" if is_vietnamese else "description_en", "")
                discount = promo.get("discount" if is_vietnamese else "discount_en", "")
                valid_period = promo.get("valid_period" if is_vietnamese else "valid_period_en", "")
                
                result += f"### {name}\n"
                result += f"{description}\n"
                
                if discount:
                    if is_vietnamese:
                        result += f"**Giảm giá:** {discount}\n"
                    else:
                        result += f"**Discount:** {discount}\n"
                        
                if valid_period:
                    if is_vietnamese:
                        result += f"**Thời gian áp dụng:** {valid_period}\n"
                    else:
                        result += f"**Valid period:** {valid_period}\n"
                        
                result += "\n"
                
            return result
    
    def get_all_seasonal_promotions(self, is_vietnamese: bool = True) -> str:
        """Trả về thông tin về tất cả các chương trình khuyến mãi theo mùa"""
        seasonal_promotions = self.financial_data.get("seasonal_promotions", {})
        
        if is_vietnamese:
            result = "🗓️ **LỊCH KHUYẾN MÃI THEO MÙA:**\n\n"
        else:
            result = "🗓️ **SEASONAL PROMOTION CALENDAR:**\n\n"
            
        for promo_id, promo in seasonal_promotions.items():
            name = promo.get("name" if is_vietnamese else "name_en", "")
            description = promo.get("description" if is_vietnamese else "description_en", "")
            discount = promo.get("discount" if is_vietnamese else "discount_en", "")
            valid_period = promo.get("valid_period" if is_vietnamese else "valid_period_en", "")
            
            result += f"### {name}\n"
            result += f"{description}\n"
            
            if discount:
                if is_vietnamese:
                    result += f"**Giảm giá:** {discount}\n"
                else:
                    result += f"**Discount:** {discount}\n"
                    
            if valid_period:
                if is_vietnamese:
                    result += f"**Thời gian áp dụng:** {valid_period}\n"
                else:
                    result += f"**Valid period:** {valid_period}\n"
                    
            result += "\n"
            
        return result

class DentalChatbot:
    def __init__(self, data_processor: DataProcessor):
        self.data_processor = data_processor
        self.conversation_history: List[Message] = []
        self.current_role = None
        
        # Try available models until one works
        self.model = None
        for model_name in GEMINI_MODELS:
            try:
                print(f"Trying to initialize model: {model_name}")
                self.model = genai.GenerativeModel(model_name)
                # Test the model with a simple prompt
                test_response = self.model.generate_content("Hello")
                print(f"Successfully initialized model: {model_name}")
                break
            except Exception as e:
                print(f"Failed to initialize model {model_name}: {str(e)}")
                continue
                
        if self.model is None:
            print("WARNING: No Gemini models are available. Using fallback response generation.")
        
        # Display welcome message
        self.display_welcome_message()
    
    def display_welcome_message(self):
        """Display a welcome message at the start of the conversation"""
        welcome_msg = WELCOME_MESSAGES[0]  # Default to Vietnamese
        print(f"\n[Trợ lý] {welcome_msg}")
    
    def _is_vietnamese(self, text):
        """Determine if a text is primarily in Vietnamese"""
        # Vietnamese specific characters
        vn_chars = "àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ"
        vn_chars += vn_chars.upper()
        
        # Count Vietnamese specific characters
        vn_char_count = sum(1 for c in text if c in vn_chars)
        
        # Check for common Vietnamese words
        vn_words = ["tôi", "bạn", "của", "và", "là", "có", "không", "được", "trong", "đó", "này"]
        word_count = sum(1 for word in vn_words if word in text.lower())
        
        # If Vietnamese characters or words are present, consider it Vietnamese
        return vn_char_count > 0 or word_count > 0
    
    def _append_booking_and_learn_more(self, response: str, sources: List[Dict] = None, is_vietnamese: bool = True) -> str:
        """Append booking information and learn more links to the response"""
        # Add "Learn more" section if sources are provided
        if sources and len(sources) > 0:
            learn_more_links = []
            for source in sources:
                if 'url' in source:
                    title = source.get('title', 'Bài viết liên quan')
                    url = source['url']
                    learn_more_links.append(f"[{title}]({url})")
            
            if learn_more_links:
                if is_vietnamese:
                    response += "\n\n🔍 **Tìm hiểu thêm:**\n" + "\n".join(learn_more_links)
                else:
                    response += "\n\n🔍 **Learn more:**\n" + "\n".join(learn_more_links)
        
        # Add booking information
        if is_vietnamese:
            response += BOOKING_MESSAGE_VI
        else:
            response += BOOKING_MESSAGE_EN
        
        return response
        
    def _determine_role(self, query: str) -> AgentRole:
        """Determine which agent should handle the query"""
        # Dental keywords in English and Vietnamese
        dental_keywords = [
            # English
            "tooth", "teeth", "dental", "dentist", "cavity", "gum", 
            "floss", "filling", "crown", "root canal", "braces", "mouth",
            "ache", "pain", "sensitivity", "hygiene", "brushing", "invisalign",
            # Vietnamese
            "răng", "nha khoa", "nha sĩ", "sâu răng", "lợi", "nướu",
            "chỉ nha khoa", "trám răng", "mão răng", "chữa tủy", "niềng răng", "miệng",
            "đau", "đau nhức", "ê buốt", "vệ sinh", "đánh răng", "invisalign"
        ]
                          
        # Service keywords in English and Vietnamese
        service_keywords = [
            # English
            "appointment", "schedule", "book", "price", "cost", 
            "insurance", "doctor", "available", "time", "location",
            "office", "hours", "payment", "contact", "address",
            # Vietnamese
            "cuộc hẹn", "lịch hẹn", "đặt lịch", "giá", "chi phí", 
            "bảo hiểm", "bác sĩ", "lịch trống", "thời gian", "địa điểm",
            "văn phòng", "giờ làm việc", "thanh toán", "liên hệ", "địa chỉ"
        ]
        
        # Check for explicit doctor inquiry in both languages
        doctor_patterns = ["how many doctors", "bác sĩ", "doctor", "số lượng bác sĩ", "danh sách bác sĩ", 
                          "miền nam", "miền bắc", "miền trung", "phía nam", "phía bắc", "phía trung"]
        if any(pattern in query.lower() for pattern in doctor_patterns):
            return AgentRole.CUSTOMER_SERVICE
            
        dental_score = sum(1 for word in dental_keywords if word.lower() in query.lower())
        service_score = sum(1 for word in service_keywords if word.lower() in query.lower())
        
        return AgentRole.DENTAL_CONSULTANT if dental_score >= service_score else AgentRole.CUSTOMER_SERVICE
    
    def _identify_doctor_query_type(self, query: str) -> Tuple[str, str]:
        """Identify the type of doctor query (region, education, certificate)"""
        query_lower = query.lower()
        
        # Check for region queries
        region_patterns = ["miền nam", "miền bắc", "miền trung", "phía nam", "phía bắc", "phía trung"]
        for pattern in region_patterns:
            if pattern in query_lower:
                return "region", pattern
        
        # Check for education queries
        education_patterns = ["đại học", "university", "tốt nghiệp", "graduate", "học tại", "studied at", "đh"]
        for pattern in education_patterns:
            if pattern in query_lower:
                # Extract the education institution
                words_after = query_lower.split(pattern)[1].strip()
                if words_after:
                    # Get a few words after the pattern
                    education_query = words_after.split()[0:3]
                    return "education", " ".join(education_query)
        
        # Check for certificate queries
        certificate_patterns = ["chứng chỉ", "certificate", "chuyên về", "specialist", "chuyên ngành"]
        for pattern in certificate_patterns:
            if pattern in query_lower:
                # Extract the certificate type
                words_after = query_lower.split(pattern)[1].strip()
                if words_after:
                    # Get a few words after the pattern
                    certificate_query = words_after.split()[0:3]
                    return "certificate", " ".join(certificate_query)
        
        # Default: general doctor query
        return "general", ""
    
    def _format_doctor_list(self, doctors: List[Dict[str, Any]], is_vietnamese: bool = True, detailed_limit: int = 3) -> str:
        """Format a list of doctors with detailed information for the first few"""
        if not doctors:
            if is_vietnamese:
                return "❌ Không tìm thấy bác sĩ nào phù hợp với yêu cầu của bạn."
            else:
                return "❌ No doctors found matching your criteria."
        
        if is_vietnamese:
            result = f"🩺 **Đã tìm thấy {len(doctors)} bác sĩ:**\n\n"
        else:
            result = f"🩺 **Found {len(doctors)} doctors:**\n\n"
        
        # Add detailed information for the first few doctors
        for i, doctor in enumerate(doctors[:detailed_limit]):
            name = doctor.get('name', 'Không có tên')
            area = doctor.get('area', 'Không có thông tin khu vực')
            education = doctor.get('education', 'Không có thông tin học vấn')
            certificate = doctor.get('certificate', 'Không có thông tin chứng chỉ')
            
            result += f"**{i+1}. {name}** 👨‍⚕️\n"
            result += f"   • **{'Khu vực' if is_vietnamese else 'Area'}:** {area}\n"
            result += f"   • **{'Học vấn' if is_vietnamese else 'Education'}:** {education}\n"
            result += f"   • **{'Chứng chỉ' if is_vietnamese else 'Certificates'}:** {certificate}\n\n"
        
        # List remaining doctors by name only
        if len(doctors) > detailed_limit:
            if is_vietnamese:
                result += "**Các bác sĩ khác:** "
            else:
                result += "**Other doctors:** "
                
            other_names = [doctor.get('name', 'Không có tên') for doctor in doctors[detailed_limit:]]
            result += ", ".join(other_names)
        
        return result
    
    def _generate_response_with_template(self, prompt_type, query):
        """Fallback method for generating responses without Gemini API"""
        is_vietnamese = self._is_vietnamese(query)
        
        if prompt_type == "dental":
            if is_vietnamese:
                response = f"🦷 Là chuyên viên tư vấn nha khoa tại PrimeCare, tôi khuyên bạn nên gặp một trong các chuyên gia của chúng tôi về vấn đề '{query}'. Các vấn đề răng miệng cần được xử lý kịp thời để tránh biến chứng. Bạn có muốn đặt lịch hẹn với một trong các nha sĩ của chúng tôi không?"
            else:
                response = f"🦷 As a dental consultant at PrimeCare, I recommend seeing one of our specialists about your '{query}' concern. Dental issues should be addressed promptly to prevent complications. Would you like to schedule an appointment with one of our dentists?"
        else:  # customer service
            if "price" in query.lower() or "cost" in query.lower() or "giá" in query.lower() or "chi phí" in query.lower():
                if is_vietnamese:
                    response = f"💰 Tại PrimeCare, chi phí cho dịch vụ {query} thường từ 300.000 đến 800.000 VND tùy thuộc vào mức độ phức tạp. Chúng tôi sẽ cung cấp chi phí cụ thể hơn trong buổi tư vấn. Bạn có muốn đặt lịch hẹn không?"
                else:
                    response = f"💰 At PrimeCare, our {query} procedures typically range from 300,000 to 800,000 VND depending on complexity. We'd be happy to provide a more specific estimate during a consultation. Would you like to schedule one?"
            elif "doctor" in query.lower() or "bác sĩ" in query.lower():
                if is_vietnamese:
                    response = f"👨‍⚕️ PrimeCare có nhiều chuyên gia nha khoa giàu kinh nghiệm chuyên về các lĩnh vực khác nhau của nha khoa. Các bác sĩ của chúng tôi đều được đào tạo chuyên sâu và có nhiều chứng chỉ chuyên môn. Bạn có muốn biết thông tin về bác sĩ cụ thể hoặc chuyên khoa nha khoa nào không?"
                else:
                    response = f"👨‍⚕️ PrimeCare has multiple experienced dental professionals specializing in various areas of dentistry. Our doctors have extensive training and certifications. Would you like information about a specific doctor or dental specialty?"
            else:
                if is_vietnamese:
                    response = f"ℹ️ Cảm ơn bạn đã hỏi về '{query}'. Phòng khám Nha khoa PrimeCare mở cửa từ thứ Hai đến thứ Sáu (8:00-20:00), thứ Bảy (8:00-18:00) và Chủ nhật (8:00-17:00). Bạn có muốn đặt lịch hẹn hoặc có câu hỏi nào khác không?"
                else:
                    response = f"ℹ️ Thank you for your inquiry about '{query}'. PrimeCare Dental Clinic is open Monday-Friday 8AM-8PM, Saturday 8AM-6PM, and Sunday 8AM-5PM. Would you like to schedule an appointment or do you have other questions?"
        
        return self._append_booking_and_learn_more(response, None, is_vietnamese)
    
    def _generate_dental_response(self, query: str) -> str:
        """Generate response as dental consultant"""
        # Detect language
        is_vietnamese = self._is_vietnamese(query)
        
        # Retrieve relevant dental information
        results = self.data_processor.search_dental_data(query)
        
        # Format context from results
        context_items = []
        for result in results:
            title = result.get('title', 'Dental Information')
            
            # Process sections to extract information
            sections = result.get('sections', [])
            section_texts = []
            for section in sections:
                heading = section.get('heading', '')
                content = section.get('content', '')
                section_texts.append(f"SECTION: {heading}\n{content}")
            
            article_content = "\n\n".join(section_texts)
            context_items.append(f"ARTICLE: {title}\n{article_content}")
            
        context = "\n\n".join(context_items)
        
        # Create prompt for Gemini
        if is_vietnamese:
            prompt = f"""
            Bạn là một chuyên viên tư vấn nha khoa có kiến thức chuyên sâu tại Phòng khám Nha khoa PrimeCare, đang nói chuyện với một bệnh nhân bằng tiếng Việt.
            Sử dụng thông tin nha khoa sau đây để trả lời câu hỏi của người dùng.
            Hãy nói chuyện thân thiện, hữu ích và chính xác. Thêm emoji phù hợp để làm cho câu trả lời sinh động hơn.
            Nếu thông tin không chứa câu trả lời rõ ràng, hãy cung cấp lời khuyên nha khoa chung liên quan đến chủ đề nhưng nói rõ rằng bạn đang đưa ra thông tin chung.
            
            THÔNG TIN NHA KHOA:
            {context}
            
            CÂU HỎI CỦA NGƯỜI DÙNG: {query}
            
            Vui lòng cung cấp câu trả lời hữu ích, dễ hiểu với giọng điệu thân thiện như một chuyên viên tư vấn nha khoa tại PrimeCare.
            Sử dụng markdown để định dạng câu trả lời và thêm emoji phù hợp:
            """
        else:
            prompt = f"""
            You are a knowledgeable dental consultant at PrimeCare Dental Clinic speaking with a patient. 
            Use the following dental information to answer the user's question.
            Be conversational, helpful, and accurate. Add appropriate emojis to make your answer more engaging.
            If the information doesn't contain a clear answer, provide general dental advice related to the topic but make it clear you're giving general information.
            
            DENTAL INFORMATION:
            {context}
            
            USER QUESTION: {query}
            
            Please provide a helpful, conversational response as a dental consultant at PrimeCare.
            Use markdown formatting for your answer and include appropriate emojis:
            """
        
        # Try to use Gemini API
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                response_text = response.text
                # Add emoji if none present
                if not any(char in response_text for char in "🦷😊👨‍⚕️🩺🔍💊💉"):
                    response_text = "🦷 " + response_text
                return self._append_booking_and_learn_more(response_text, results, is_vietnamese)
            except Exception as e:
                print(f"Error generating response with Gemini: {str(e)}")
                print("Using fallback response generation")
                
        # Fallback to template-based response
        return self._generate_response_with_template("dental", query)
    
    def _generate_service_response(self, query: str) -> str:
        """Generate response as customer service consultant"""
        # Detect language
        is_vietnamese = self._is_vietnamese(query)
        
        # Check if it's a specific doctor query type
        query_type, query_value = self._identify_doctor_query_type(query)
        
        if query_type == "region" and query_value:
            # Handle region-specific doctor query
            doctors = self.data_processor.get_doctors_by_region(query_value)
            doctor_list = self._format_doctor_list(doctors, is_vietnamese)
            
            if is_vietnamese:
                intro = f"👨‍⚕️ Dưới đây là danh sách các bác sĩ ở {query_value} của Nha khoa PrimeCare:\n\n"
            else:
                intro = f"👨‍⚕️ Here are the doctors in the {query_value} region at PrimeCare Dental Clinic:\n\n"
                
            return self._append_booking_and_learn_more(intro + doctor_list, None, is_vietnamese)
            
        elif query_type == "education" and query_value:
            # Handle education-specific doctor query
            doctors = self.data_processor.get_doctors_by_education(query_value)
            doctor_list = self._format_doctor_list(doctors, is_vietnamese)
            
            if is_vietnamese:
                intro = f"👨‍⚕️ Dưới đây là danh sách các bác sĩ có liên quan đến '{query_value}' tại Nha khoa PrimeCare:\n\n"
            else:
                intro = f"👨‍⚕️ Here are the doctors associated with '{query_value}' at PrimeCare Dental Clinic:\n\n"
                
            return self._append_booking_and_learn_more(intro + doctor_list, None, is_vietnamese)
            
        elif query_type == "certificate" and query_value:
            # Handle certificate-specific doctor query
            doctors = self.data_processor.get_doctors_by_certificate(query_value)
            doctor_list = self._format_doctor_list(doctors, is_vietnamese)
            
            if is_vietnamese:
                intro = f"👨‍⚕️ Dưới đây là danh sách các bác sĩ có chứng chỉ liên quan đến '{query_value}' tại Nha khoa PrimeCare:\n\n"
            else:
                intro = f"👨‍⚕️ Here are the doctors with certificates related to '{query_value}' at PrimeCare Dental Clinic:\n\n"
                
            return self._append_booking_and_learn_more(intro + doctor_list, None, is_vietnamese)
        
        # Kiểm tra nếu là truy vấn về ngân sách
        budget_match = re.search(r'(\d{1,3}([,.]\d{3})*([,.]\d+)?)(\s*)(triệu|tr|nghìn|ngàn|k|đồng|vnd|đ)', query.lower())
        if budget_match:
            try:
                # Xử lý chuỗi số thành số nguyên
                budget_str = budget_match.group(1).replace('.', '').replace(',', '')
                budget = float(budget_str)
                
                # Điều chỉnh dựa trên đơn vị
                unit = budget_match.group(5).lower()
                if unit in ['triệu', 'tr']:
                    budget *= 1000000
                elif unit in ['nghìn', 'ngàn', 'k']:
                    budget *= 1000
                
                # Lấy gợi ý dịch vụ phù hợp với ngân sách
                budget_recommendations = self.data_processor.get_affordable_services(budget, is_vietnamese)
                
                # Thêm thông tin về các kế hoạch thanh toán
                if budget > 5000000:  # Cho các dịch vụ có giá trị cao
                    payment_plans = self.data_processor.get_payment_plans(is_vietnamese)
                    budget_recommendations += "\n\n" + payment_plans
                    
                return self._append_booking_and_learn_more(budget_recommendations, None, is_vietnamese)
            except Exception as e:
                print(f"Error processing budget query: {str(e)}")
        
        # Kiểm tra nếu là truy vấn về kế hoạch thanh toán/trả góp
        if any(word in query.lower() for word in 
            ["payment plan", "installment", "credit", "finance", "loan", 
            "trả góp", "góp", "vay", "thanh toán", "tín dụng"]):
            
            payment_plans = self.data_processor.get_payment_plans(is_vietnamese)
            return self._append_booking_and_learn_more(payment_plans, None, is_vietnamese)
        
        # Kiểm tra nếu là truy vấn về chương trình khuyến mãi đặc biệt
        if any(word in query.lower() for word in 
            ["student discount", "special offer", "discount", "offer", "promotion", 
            "sinh viên", "khuyến mãi", "giảm giá", "ưu đãi", "đặc biệt", "cao tuổi", "khuyết tật"]):
            
            special_promo = self.data_processor.get_special_promotions(is_vietnamese)
            return self._append_booking_and_learn_more(special_promo, None, is_vietnamese)
        
        # Kiểm tra nếu là truy vấn về khuyến mãi theo mùa
        if any(word in query.lower() for word in 
            ["seasonal", "holiday", "new year", "christmas", "event", 
            "theo mùa", "ngày lễ", "tết", "năm mới", "lễ hội", "sự kiện"]):
            
            # Lấy khuyến mãi đang diễn ra
            current_promos = self.data_processor.get_current_promotions(is_vietnamese)
            
            # Nếu cụ thể hơn về tất cả các khuyến mãi theo mùa
            if any(word in query.lower() for word in ["all", "list", "upcoming", "tất cả", "danh sách", "sắp tới"]):
                all_promos = self.data_processor.get_all_promotions(is_vietnamese)
                if is_vietnamese:
                    return self._append_booking_and_learn_more(f"{current_promos}\n\n## THÔNG TIN TẤT CẢ KHUYẾN MÃI THEO MÙA\n\n{all_promos}", None, is_vietnamese)
                else:
                    return self._append_booking_and_learn_more(f"{current_promos}\n\n## ALL SEASONAL PROMOTIONS\n\n{all_promos}", None, is_vietnamese)
            
            return self._append_booking_and_learn_more(current_promos, None, is_vietnamese)
        
        # Check for specific doctor count question
        if any(pattern in query.lower() for pattern in ["how many doctors", "số lượng bác sĩ", "có bao nhiêu bác sĩ"]):
            doctor_count = self.data_processor.get_doctor_count()
            doctor_names = self.data_processor.get_doctor_names()
            names_list = ", ".join(doctor_names[:5])
            
            if is_vietnamese:
                prompt = f"""
                Bạn là một chuyên viên tư vấn dịch vụ khách hàng tại Phòng khám Nha khoa PrimeCare. Người dùng đã hỏi về số lượng bác sĩ.
                
                Phòng khám Nha khoa PrimeCare có {doctor_count} bác sĩ, bao gồm {names_list} và những người khác.
                
                CÂU HỎI CỦA NGƯỜI DÙNG: {query}
                
                Vui lòng cung cấp câu trả lời hữu ích, dễ hiểu bằng tiếng Việt với tư cách là chuyên viên tư vấn dịch vụ khách hàng tại PrimeCare.
                Sử dụng markdown để định dạng câu trả lời và thêm emoji phù hợp:
                """
            else:
                prompt = f"""
                You are a helpful customer service consultant for PrimeCare Dental Clinic. A user has asked about the number of doctors.
                
                We have {doctor_count} doctors at PrimeCare Dental Clinic, including {names_list} and others.
                
                USER QUESTION: {query}
                
                Please provide a helpful, conversational response as a customer service consultant at PrimeCare, telling them about our doctors.
                Use markdown formatting for your answer and include appropriate emojis:
                """
            
            if self.model:
                try:
                    response = self.model.generate_content(prompt)
                    response_text = response.text
                    # Add emoji if none present
                    if not any(char in response_text for char in "👨‍⚕️🩺🔍💊💉"):
                        response_text = "👨‍⚕️ " + response_text
                    return self._append_booking_and_learn_more(response_text, None, is_vietnamese)
                except Exception as e:
                    print(f"Error generating response with Gemini: {str(e)}")
                    if is_vietnamese:
                        return self._append_booking_and_learn_more(f"👨‍⚕️ Phòng khám Nha khoa PrimeCare có {doctor_count} bác sĩ giàu kinh nghiệm, bao gồm {names_list} và nhiều người khác. Tất cả các bác sĩ của chúng tôi đều có trình độ cao với nhiều năm đào tạo chuyên sâu trong các chuyên khoa của họ. Bạn có muốn biết thêm về bác sĩ cụ thể nào không?", None, is_vietnamese)
                    else:
                        return self._append_booking_and_learn_more(f"👨‍⚕️ PrimeCare Dental Clinic has {doctor_count} experienced doctors, including {names_list} and others. All our doctors are highly qualified with extensive training in their specialties. Would you like to know more about any specific doctor?", None, is_vietnamese)
            else:
                if is_vietnamese:
                    return self._append_booking_and_learn_more(f"👨‍⚕️ Phòng khám Nha khoa PrimeCare có {doctor_count} bác sĩ giàu kinh nghiệm, bao gồm {names_list} và nhiều người khác. Tất cả các bác sĩ của chúng tôi đều có trình độ cao với nhiều năm đào tạo chuyên sâu trong các chuyên khoa của họ. Bạn có muốn biết thêm về bác sĩ cụ thể nào không?", None, is_vietnamese)
                else:
                    return self._append_booking_and_learn_more(f"👨‍⚕️ PrimeCare Dental Clinic has {doctor_count} experienced doctors, including {names_list} and others. All our doctors are highly qualified with extensive training in their specialties. Would you like to know more about any specific doctor?", None, is_vietnamese)
            
        # Retrieve relevant doctor information
        results = self.data_processor.search_doctor_data(query)
        
        # Check if query is about pricing or appointments
        is_price_query = any(word in query.lower() for word in 
                        ["price", "cost", "fee", "expensive", "cheap", "afford", "payment",
                            "giá", "chi phí", "phí", "đắt", "rẻ", "chi trả", "thanh toán"])
        is_appointment_query = any(word in query.lower() for word in 
                                ["appointment", "schedule", "book", "available", "time", "when", "visit",
                                "lịch hẹn", "đặt lịch", "đặt hẹn", "sẵn sàng", "thời gian", "khi nào", "thăm khám"])
        
        # Format context from results
        doctor_info = []
        for result in results:
            name = result.get('name', 'Unknown')
            area = result.get('area', 'Unknown Area')
            education = result.get('education', 'Education information not available')
            certificate = result.get('certificate', 'No certificates listed')
            
            if is_vietnamese:
                doctor_info.append(f"Bác sĩ: {name}\nKhu vực: {area}\nHọc vấn: {education}\nChứng chỉ: {certificate}")
            else:
                doctor_info.append(f"Doctor: {name}\nArea: {area}\nEducation: {education}\nCertificates: {certificate}")
            
        context = "\n\n".join(doctor_info)
        
        # Look for specific service in the query if it's a price query
        if is_price_query:
            service_keywords = [
                # Orthodontics
                "niềng răng", "mắc cài", "braces", "orthodontic", "invisalign",
                # Implants
                "implant", "trồng răng", "cấy ghép", 
                # General dentistry
                "nhổ răng", "extraction", "trám răng", "filling", "tẩy trắng", "whitening",
                "cạo vôi", "scaling", "vệ sinh", "cleaning", "khám", "check-up",
                # Restorative
                "mão răng", "crown", "cầu răng", "bridge", "veneer",
                # Children
                "trẻ em", "children", "nhi", "pediatric"
            ]
            
            # Check if query contains specific service keywords
            specific_service_query = False
            for keyword in service_keywords:
                if keyword in query.lower():
                    specific_service_query = True
                    # Lấy thông tin giá từ processor thay vì dùng dữ liệu cứng
                    pricing_info = self.data_processor.get_price_info(keyword, is_vietnamese)
                    break
            
            # Nếu không tìm thấy dịch vụ cụ thể, cung cấp tổng quan về giá
            if not specific_service_query:
                if is_vietnamese:
                    pricing_info = "📊 **BẢNG GIÁ TỔNG QUAN:**\n\n"
                    for category in self.data_processor.price_processor.categories:
                        price_range = self.data_processor.price_processor.price_ranges.get(category, (0, 0))
                        pricing_info += f"• **{category}**: {price_range[0]:,.0f}đ - {price_range[1]:,.0f}đ\n"
                    pricing_info += "\n*Vui lòng liên hệ chúng tôi để được tư vấn chi tiết về giá của từng dịch vụ cụ thể.*"
                else:
                    pricing_info = "📊 **PRICE OVERVIEW:**\n\n"
                    for category in self.data_processor.price_processor.categories:
                        price_range = self.data_processor.price_processor.price_ranges.get(category, (0, 0))
                        pricing_info += f"• **{category}**: {price_range[0]:,.0f} VND - {price_range[1]:,.0f} VND\n"
                    pricing_info += "\n*Please contact us for detailed pricing on specific services.*"
        else:
            pricing_info = ""
        
        # Add appointment information if requested
        if is_vietnamese:
            appointment_info = """
            🕒 **GIỜ LÀM VIỆC:**
            • Thứ Hai - Thứ Sáu: 8:00 - 20:00
            • Thứ Bảy: 8:00 - 18:00
            • Chủ Nhật: 8:00 - 17:00
            
            Chúng tôi thường có lịch trống trong vòng 1-2 ngày cho các cuộc hẹn thông thường.
            Các cuộc hẹn khẩn cấp thường có thể được sắp xếp trong cùng ngày.
            """
        else:
            appointment_info = """
            🕒 **OFFICE HOURS:**
            • Monday-Friday: 8:00 AM - 8:00 PM
            • Saturday: 8:00 AM - 6:00 PM
            • Sunday: 8:00 AM - 5:00 PM
            
            We typically have availability within 1-2 days for regular appointments.
            Emergency appointments can often be accommodated on the same day.
            """
        
        # Create prompt for Gemini
        if is_vietnamese:
            prompt = f"""
            Bạn là một chuyên viên tư vấn dịch vụ khách hàng tại Phòng khám Nha khoa PrimeCare. Hãy sử dụng thông tin sau để trả lời câu hỏi của người dùng.
            Hãy trả lời một cách thân thiện, hữu ích và dễ hiểu bằng tiếng Việt.
            
            THÔNG TIN BÁC SĨ:
            {context}
            
            {pricing_info if is_price_query else ""}
            {appointment_info if is_appointment_query else ""}
            
            CÂU HỎI CỦA NGƯỜI DÙNG: {query}
            
            Vui lòng cung cấp câu trả lời hữu ích, dễ hiểu với tư cách là chuyên viên tư vấn dịch vụ khách hàng tại PrimeCare.
            Sử dụng markdown để định dạng câu trả lời và thêm emoji phù hợp:
            """
        else:
            prompt = f"""
            You are a helpful customer service consultant for PrimeCare Dental Clinic. Use the following information to answer the user's question.
            Be conversational, friendly, and helpful.
            
            DOCTOR INFORMATION:
            {context}
            
            {pricing_info if is_price_query else ""}
            {appointment_info if is_appointment_query else ""}
            
            USER QUESTION: {query}
            
            Please provide a helpful, conversational response as a customer service consultant at PrimeCare.
            Use markdown formatting for your answer and include appropriate emojis:
            """
        
        # Try to use Gemini API
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                response_text = response.text
                # Add emoji if none present
                if not any(char in response_text for char in "💰🕒👨‍⚕️🩺🔍💊💉"):
                    if is_price_query:
                        response_text = "💰 " + response_text
                    elif is_appointment_query:
                        response_text = "🕒 " + response_text
                    else:
                        response_text = "👨‍⚕️ " + response_text
                return self._append_booking_and_learn_more(response_text, None, is_vietnamese)
            except Exception as e:
                print(f"Error generating response with Gemini: {str(e)}")
                print("Using fallback response generation")
                
        # Fallback to template-based response
        if is_price_query:
            # Extract any service names from the query for more specific response
            service_name = None
            for keyword in service_keywords:
                if keyword in query.lower():
                    service_name = keyword
                    break
            
            if service_name:
                services = self.data_processor.price_processor.search_service(service_name)
                if services and len(services) > 0:
                    service = services[0]
                    service_name = service.get("Tên dịch vụ", service_name)
                    price_range = service.get("Giá khuyến mãi", "")
                    discount = service.get("Giảm giá", "")
                    
                    if is_vietnamese:
                        return self._append_booking_and_learn_more(
                            f"💰 Dịch vụ {service_name} của chúng tôi có giá {price_range}. "
                            f"{'Hiện đang giảm giá ' + discount + '.' if discount else ''} "
                            f"Vui lòng đặt lịch hẹn để được tư vấn chi tiết hơn tại Phòng khám Nha khoa PrimeCare.",
                            None, is_vietnamese
                        )
                    else:
                        return self._append_booking_and_learn_more(
                            f"💰 Our {service_name} service costs {price_range}. "
                            f"{'We currently have a ' + discount + ' discount.' if discount else ''} "
                            f"Please schedule an appointment for a more detailed consultation at PrimeCare Dental Clinic.",
                            None, is_vietnamese
                        )
            
            # Default pricing response
            if is_vietnamese:
                return self._append_booking_and_learn_more(
                    f"💰 Đối với {query}, chi phí của chúng tôi thường dao động tùy thuộc vào thủ thuật cụ thể và mức độ phức tạp. "
                    f"Hãy liên hệ với chúng tôi để được tư vấn chi tiết và báo giá chính xác tại Phòng khám Nha khoa PrimeCare.",
                    None, is_vietnamese
                )
            else:
                return self._append_booking_and_learn_more(
                    f"💰 For {query}, our prices typically vary depending on the specific procedure and complexity. "
                    f"Please contact us for detailed consultation and accurate pricing at PrimeCare Dental Clinic.",
                    None, is_vietnamese
                )
        elif is_appointment_query:
            if is_vietnamese:
                return self._append_booking_and_learn_more(f"🕒 Phòng khám Nha khoa PrimeCare mở cửa từ Thứ Hai đến Thứ Sáu (8:00-20:00), Thứ Bảy (8:00-18:00) và Chủ Nhật (8:00-17:00). Chúng tôi thường có thể sắp xếp lịch hẹn mới trong vòng 1-2 ngày. Bạn có muốn đặt lịch hẹn cho nhu cầu nha khoa của mình không?", None, is_vietnamese)
            else:
                return self._append_booking_and_learn_more(f"🕒 PrimeCare Dental Clinic is open Monday-Friday (8AM-8PM), Saturday (8AM-6PM), and Sunday (8AM-5PM). We can usually accommodate new appointments within 1-2 days. Would you like to schedule an appointment for your dental needs?", None, is_vietnamese)
        else:
            return self._generate_response_with_template("service", query)
        
    def process_query(self, query: str) -> Dict[str, str]:
        """Process a user query and return a response"""
        # Record user message
        self.conversation_history.append(Message(role="user", content=query))
        
        # Determine which agent should respond
        self.current_role = self._determine_role(query)
        
        # Generate response based on agent role
        if self.current_role == AgentRole.DENTAL_CONSULTANT:
            response = self._generate_dental_response(query)
            agent_type = "Dental Consultant" if not self._is_vietnamese(query) else "Chuyên viên tư vấn nha khoa"
        else:
            response = self._generate_service_response(query)
            agent_type = "Customer Service" if not self._is_vietnamese(query) else "Dịch vụ khách hàng"
            
        # Record assistant message
        self.conversation_history.append(Message(
            role="assistant", 
            content=response,
            agent_type=self.current_role
        ))
        
        return {"response": response, "agent_type": agent_type}

# Example usage when run directly
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PrimeCare Dental Chatbot")
    parser.add_argument("--dental-data", default="data/news-detail.json", help="Path to dental articles JSON file")
    parser.add_argument("--doctor-data", default="data/doctors.json", help="Path to doctor information JSON file")
    parser.add_argument("--price-data", default="data/service-prices.json", help="Path to service prices JSON file")
    parser.add_argument("--financial-data", default="data/financial_services.json", help="Path to financial services JSON file")
    
    args = parser.parse_args()
    
    try:
        print("Khởi tạo trợ lý nha khoa PrimeCare...")
        
       # Kiểm tra xem các tệp có tồn tại không
        if not os.path.exists(args.dental_data):
            raise FileNotFoundError(f"Dental data file not found: {args.dental_data}")
        if not os.path.exists(args.doctor_data):
            raise FileNotFoundError(f"Doctor data file not found: {args.doctor_data}")
        if not os.path.exists(args.price_data):
            raise FileNotFoundError(f"Price data file not found: {args.price_data}")
        if not os.path.exists(args.financial_data):
            raise FileNotFoundError(f"Financial data file not found: {args.financial_data}")
        
        # Khởi tạo data processor và chatbot
        data_processor = DataProcessor(
            dental_path=args.dental_data,
            doctor_path=args.doctor_data,
            price_path=args.price_data,
            financial_path=args.financial_data
        )
        chatbot = DentalChatbot(data_processor)
        
        print("Khởi tạo hoàn tất!")
        print("\nTrợ lý nha khoa PrimeCare (Gõ 'exit' để thoát)")
        print("=" * 50)
        
        # Interactive chat loop
        while True:
            try:
                user_input = input("\nBạn: ")
                
                if user_input.lower() == 'exit':
                    if chatbot._is_vietnamese(user_input):
                        print("Cảm ơn bạn đã sử dụng Trợ lý nha khoa PrimeCare. Tạm biệt! 👋")
                    else:
                        print("Thank you for using PrimeCare Dental Assistant. Goodbye! 👋")
                    break
                    
                # Process query directly through the chatbot
                result = chatbot.process_query(user_input)
                
                # Print the response along with agent type
                print(f"\n[{result['agent_type']}]")
                print(f"Trợ lý: {result['response']}")
            except Exception as e:
                print(f"\nLỗi xử lý truy vấn: {str(e)}")
                print("Vui lòng thử câu hỏi khác.")
    except Exception as e:
        print(f"Lỗi khởi tạo chatbot: {str(e)}")
        print("Vui lòng kiểm tra các tệp dữ liệu và thư viện phụ thuộc.")
