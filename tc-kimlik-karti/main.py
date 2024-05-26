import cv2
import easyocr
import re
import json
import os
from fastapi import FastAPI, UploadFile,File, HTTPException

app = FastAPI()

# Kontrol fonksiyonları
def is_tc_id(text):
    return re.match(r'^[1-9]\d{10}$', text)

def is_date(text):
    # Tarih kontrolü için güncellenmiş regex, çeşitli ayırıcıları kabul eder
    return re.match(r'^\d{2}[./,\\]\d{2}[./,\\]\d{4}$', text)

def is_serial_no(text):
    # Seri numarası için güncellenmiş kontrol, büyük harfle başlar ve 8 rakamla devam eder
    return re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{9}$', text)

def is_gender(text):
    # Cinsiyet bilgisini tanıyan genişletilmiş regex, 'EM' ve 'KF' ihtimallerini de içerir
    return re.match(r'^(K|E)(\s?\/\s?(F|M))?$', text, re.IGNORECASE) or \
           re.match(r'^(K|E)I\s?(F|M)?$', text, re.IGNORECASE) or \
           re.match(r'^(E)(I\s?M|\/\s?M)$', text, re.IGNORECASE) or \
           re.match(r'^(K)\s?I\/F$', text, re.IGNORECASE) or \
           re.match(r'^EM$', text, re.IGNORECASE) or \
           re.match(r'^KF$', text, re.IGNORECASE)

def is_all_caps(text):
    return text.isupper()

# EasyOCR reader'ı başlat
reader = easyocr.Reader(['tr', 'en'], gpu=False, model_storage_directory='.')

# Görüntüyü işleyen fonksiyon
def process_image(image_path):
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    results = reader.readtext(gray_image)
    
    # Filtrelenen veriler için değişkenler
    tc_id = None
    birth_date = None
    expiry_date = None
    serial_no = None
    surname = None
    name = None
    gender = None
    previous_dates = []
    
    for roi_order, detection in enumerate(results, start=1):
        text = detection[1]
        top_left = tuple(map(int, detection[0][0]))
        bottom_right = tuple(map(int, detection[0][2]))
    
        if is_tc_id(text) and not tc_id:
            tc_id = text
        elif is_date(text) and not birth_date:
            birth_date = text
            previous_dates.append(birth_date)
        elif is_date(text) and text not in previous_dates:
            expiry_date = text
        elif is_serial_no(text) and not serial_no:
            serial_no = text
        elif is_gender(text) and not gender:
            gender = text
        elif is_all_caps(text):
            if tc_id and not surname:
                surname = text
            elif surname and not name:
                name = text
    
    data = {
        'T.C Kimlik No': tc_id,
        'Doğum Tarihi': birth_date,
        'Son Geçerlilik Tarihi': expiry_date,
        'Seri No': serial_no,
        'Soyadı': surname,
        'Adı': name,
        'Cinsiyet': gender,  
        'Uyruğu': 'T.C./TUR'  
    }
    
    return data

# FastAPI endpoint'i
@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Geçici dosya yolu oluşturma
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(await file.read())
        
        # Resmi işleme ve sonuçları alma
        result = process_image(temp_file_path)
        
        # Geçici dosyayı sil
        os.remove(temp_file_path)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
