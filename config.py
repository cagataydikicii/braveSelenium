# -*- coding: utf-8 -*-
"""
Google Reklam Tıklama Botu Yapılandırması - UI tarafından otomatik oluşturuldu
"""

# Arama sorguları listesi
SEARCH_QUERIES = ['şişli çilingir']

# Mobil proxy listesi
MOBILE_PROXIES = ['WTi1QEkCY8:B5v0JIzhXI@rotate.saglamproxy.net:3508']

# Site filtreleme ayarları
PRIORITY_SITES = []
BLOCKED_SITES = []
ENABLE_SITE_FILTERING = True

# Worker sayısı
WORKER_COUNT = 5

# Her reklama kaç kez tıklanacak
CLICKS_PER_AD = 1

# Tıklamalar arası bekleme süreleri (saniye)
MIN_WAIT_TIME = 3
MAX_WAIT_TIME = 8

# Reklamlar arası bekleme süreleri (saniye)
MIN_AD_WAIT = 5
MAX_AD_WAIT = 10

# Sayfa yenileme sıklığı (kaç tıklamada bir)
REFRESH_FREQUENCY = 10

# Loglama seviyesi
LOG_LEVEL = "INFO"

# Chrome ayarları
CHROME_OPTIONS = {
    "headless": False,
    "disable_images": True,
    "disable_css": True,
}

# Coğrafi konum ayarları
LOCATION_INJECTION_ENABLED = True
SELECTED_DISTRICT = "Şişli"

# İstanbul ilçe koordinatları
ISTANBUL_DISTRICTS = {
    "Kadıköy": {"lat": 40.9828, "lng": 29.0329, "name": "Kadıköy"},
    "Beşiktaş": {"lat": 41.0422, "lng": 29.0088, "name": "Beşiktaş"},
    "Fatih": {"lat": 41.0082, "lng": 28.9784, "name": "Fatih (Tarihi Yarımada)"},
    "Şişli": {"lat": 41.0602, "lng": 28.9892, "name": "Şişli"},
    "Üsküdar": {"lat": 41.0214, "lng": 29.0068, "name": "Üsküdar"},
    "Bakırköy": {"lat": 40.9744, "lng": 28.8719, "name": "Bakırköy"},
    "Beyoğlu": {"lat": 41.0370, "lng": 28.9847, "name": "Beyoğlu (Taksim)"},
    "Ümraniye": {"lat": 41.0226, "lng": 29.1267, "name": "Ümraniye"},
    "Pendik": {"lat": 40.8783, "lng": 29.2362, "name": "Pendik"},
    "Maltepe": {"lat": 40.9364, "lng": 29.1598, "name": "Maltepe"},
    "Ataşehir": {"lat": 40.9833, "lng": 29.1167, "name": "Ataşehir"},
    "Kartal": {"lat": 40.9081, "lng": 29.1836, "name": "Kartal"},
    "Bağcılar": {"lat": 41.0403, "lng": 28.8569, "name": "Bağcılar"},
    "Bahçelievler": {"lat": 41.0017, "lng": 28.8514, "name": "Bahçelievler"},
    "Esenler": {"lat": 41.0456, "lng": 28.8719, "name": "Esenler"},
    "Avcılar": {"lat": 41.0233, "lng": 28.7231, "name": "Avcılar"},
    "Zeytinburnu": {"lat": 41.0089, "lng": 28.9017, "name": "Zeytinburnu"},
    "Kağıthane": {"lat": 41.0833, "lng": 28.9833, "name": "Kağıthane"},
    "Sarıyer": {"lat": 41.1728, "lng": 29.0581, "name": "Sarıyer"},
    "Beylikdüzü": {"lat": 41.0028, "lng": 28.6478, "name": "Beylikdüzü"}
}

# Mobil cihaz simülasyonu ayarları
MOBILE_DEVICE = {
    "width": 375,
    "height": 812, 
    "pixelRatio": 3.0
}

# User Agent döngüsü aktif/pasif
ROTATE_USER_AGENT = True

# Proxy döngüsü aktif/pasif
ROTATE_PROXY = True
