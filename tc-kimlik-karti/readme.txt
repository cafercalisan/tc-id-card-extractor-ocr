# T.C. Kimlik Kartı OCR ve FastAPI Uygulaması

Bu proje, T.C. kimlik kartı üzerindeki bilgileri OCR (Optik Karakter Tanıma) kullanarak okuyup işleyen ve bu bilgileri FastAPI aracılığıyla sunan bir uygulamadır.

## Gereksinimler

Bu projeyi çalıştırmak için aşağıdaki yazılımlar gereklidir:

- Python 3.7 veya üstü
- pip (Python paket yöneticisi)

## Kurulum

### 1. Python Sanal Ortamı Oluşturun

Öncelikle, bir sanal ortam oluşturup aktif hale getirmeniz önerilir.

```bash
python -m venv venv
source venv/bin/activate  # macOS ve Linux için
venv\Scripts\activate  # Windows için

pip install opencv-python-headless easyocr fastapi uvicorn