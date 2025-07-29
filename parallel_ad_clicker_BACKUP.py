import os
import sys
import multiprocessing
import random
import time
import logging
import os
import zipfile
import json
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import SEARCH_QUERIES, CLICKS_PER_AD, MOBILE_PROXIES
RED = "\033[91m"
RESET = "\033[0m"

if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def safe_print(text):
    try:
        print(text, flush=True)
    except UnicodeEncodeError:
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text, flush=True)
    except Exception as e:
        print(f"Print error: {e}", flush=True)
try:
    from config import PRIORITY_SITES, BLOCKED_SITES, ENABLE_SITE_FILTERING
    if 'ui_settings.json' in os.listdir('.'):
        import json
        try:
            with open('ui_settings.json', 'r', encoding='utf-8') as f:
                ui_settings = json.load(f)
                PRIORITY_SITES = ui_settings.get('priority_sites', PRIORITY_SITES)
                BLOCKED_SITES = ui_settings.get('blocked_sites', BLOCKED_SITES)
                ENABLE_SITE_FILTERING = ui_settings.get('enable_site_filtering', ENABLE_SITE_FILTERING)
        except:
            pass
except ImportError:
    PRIORITY_SITES = []
    BLOCKED_SITES = []
    ENABLE_SITE_FILTERING = False

try:
    from config import CHROME_OPTIONS
except ImportError:
    CHROME_OPTIONS = {"headless": False}

try:
    from config import LOCATION_INJECTION_ENABLED, SELECTED_DISTRICT, ISTANBUL_DISTRICTS
except ImportError:
    LOCATION_INJECTION_ENABLED = False
    SELECTED_DISTRICT = "Kadıköy"
    ISTANBUL_DISTRICTS = {
        "Kadıköy": {"lat": 40.9828, "lng": 29.0329, "name": "Kadıköy"}
    }

try:
    from config import MIN_WAIT_TIME, MAX_WAIT_TIME
except ImportError:
    MIN_WAIT_TIME = 5
    MAX_WAIT_TIME = 15

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

MOBILE_DEVICES = [
    {
        "name": "iPhone 13 Pro",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "viewport": {"width": 390, "height": 844},
        "device_scale_factor": 3
    },
    {
        "name": "iPhone 12",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
        "viewport": {"width": 375, "height": 812},
        "device_scale_factor": 3
    },
    {
        "name": "Samsung Galaxy S21",
        "user_agent": "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
        "viewport": {"width": 360, "height": 800},
        "device_scale_factor": 3
    },
    {
        "name": "Samsung Galaxy S20",
        "user_agent": "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36",
        "viewport": {"width": 360, "height": 760},
        "device_scale_factor": 3
    },
    {
        "name": "Google Pixel 6",
        "user_agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36",
        "viewport": {"width": 393, "height": 852},
        "device_scale_factor": 2.75
    },
    {
        "name": "Google Pixel 5",
        "user_agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
        "viewport": {"width": 393, "height": 851},
        "device_scale_factor": 3
    },
    {
        "name": "OnePlus 9",
        "user_agent": "Mozilla/5.0 (Linux; Android 11; LE2113) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
        "viewport": {"width": 412, "height": 892},
        "device_scale_factor": 3.5
    },
    {
        "name": "Xiaomi Mi 11",
        "user_agent": "Mozilla/5.0 (Linux; Android 11; M2011K2G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
        "viewport": {"width": 393, "height": 873},
        "device_scale_factor": 3
    },
    {
        "name": "Huawei P40",
        "user_agent": "Mozilla/5.0 (Linux; Android 10; ANA-LX4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36",
        "viewport": {"width": 360, "height": 780},
        "device_scale_factor": 3
    },
    {
        "name": "iPhone 11 Pro",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Mobile/15E148 Safari/604.1",
        "viewport": {"width": 375, "height": 812},
        "device_scale_factor": 3
    },
    {
        "name": "Samsung Galaxy Note 20",
        "user_agent": "Mozilla/5.0 (Linux; Android 10; SM-N981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36",
        "viewport": {"width": 412, "height": 915},
        "device_scale_factor": 3
    },
    {
        "name": "iPhone SE 2020",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
        "viewport": {"width": 375, "height": 667},
        "device_scale_factor": 2
    },
    {
        "name": "Samsung Galaxy A52",
        "user_agent": "Mozilla/5.0 (Linux; Android 11; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
        "viewport": {"width": 360, "height": 800},
        "device_scale_factor": 2.75
    },
    {
        "name": "Oppo Find X3",
        "user_agent": "Mozilla/5.0 (Linux; Android 11; CPH2173) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
        "viewport": {"width": 412, "height": 892},
        "device_scale_factor": 3.5
    },
    {
        "name": "Vivo V21",
        "user_agent": "Mozilla/5.0 (Linux; Android 11; V2059) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
        "viewport": {"width": 393, "height": 873},
        "device_scale_factor": 3
    },
    {
        "name": "Realme GT",
        "user_agent": "Mozilla/5.0 (Linux; Android 11; RMX2202) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
        "viewport": {"width": 412, "height": 892},
        "device_scale_factor": 3.5
    },
    {
        "name": "Motorola Edge 20",
        "user_agent": "Mozilla/5.0 (Linux; Android 11; motorola edge 20) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
        "viewport": {"width": 393, "height": 873},
        "device_scale_factor": 3
    },
    {
        "name": "Nokia 8.3",
        "user_agent": "Mozilla/5.0 (Linux; Android 10; Nokia 8.3 5G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.127 Mobile Safari/537.36",
        "viewport": {"width": 393, "height": 851},
        "device_scale_factor": 2.75
    },
    {
        "name": "LG V60",
        "user_agent": "Mozilla/5.0 (Linux; Android 10; LM-V600) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36",
        "viewport": {"width": 393, "height": 873},
        "device_scale_factor": 3
    },
    {
        "name": "Sony Xperia 1 III",
        "user_agent": "Mozilla/5.0 (Linux; Android 11; XQ-BC52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36",
        "viewport": {"width": 393, "height": 873},
        "device_scale_factor": 3.5
    }
]

worker_count = 5
try:
    import config
    if hasattr(config, 'WORKER_COUNT'):
        worker_count = config.WORKER_COUNT
        safe_print(f"Worker count config.WORKER_COUNT'tan okundu: {worker_count}")
    else:
        import importlib
        importlib.reload(config)
        if hasattr(config, 'WORKER_COUNT'):
            worker_count = config.WORKER_COUNT
            safe_print(f"Worker count reload sonrasi okundu: {worker_count}")
        else:
            safe_print(f"WORKER_COUNT bulunamadi, varsayilan kullaniliyor: {worker_count}")
except Exception as e:
    safe_print(f"Worker count okuma hatasi: {e}, varsayilan kullaniliyor: {worker_count}")

if worker_count > 50:
    safe_print(f"Worker count cok yuksek ({worker_count}), 50 ile sinirlaniyor")
    worker_count = 50
elif worker_count < 1:
    safe_print(f"Worker count gecersiz ({worker_count}), 1 olarak ayarlaniyor")
    worker_count = 1

def parse_proxy_string(proxy_string):
    try:
        
        if not proxy_string or '@' not in proxy_string:
            return None
            
        auth_part, server_part = proxy_string.split('@', 1)
        username, password = auth_part.split(':', 1)
        host, port = server_part.split(':', 1)
        
        result = {
            'username': username,
            'password': password,
            'host': host,
            'port': int(port)
        }
        
        return result
        
    except Exception as e:
        return None

def create_proxy_extension(proxy_info):
    try:
        manifest = {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Proxy Extension",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version": "22.0.0"
        }
        
        background_script = f"""
        var config = {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{proxy_info['host']}",
                    port: {proxy_info['port']}
                }},
                bypassList: ["localhost"]
            }}
        }};

        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{proxy_info['username']}",
                    password: "{proxy_info['password']}"
                }}
            }};
        }}

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
        );
        """
        
        temp_dir = tempfile.mkdtemp()
        extension_path = os.path.join(temp_dir, "proxy_extension")
        os.makedirs(extension_path)
        
        with open(os.path.join(extension_path, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)
        with open(os.path.join(extension_path, "background.js"), "w") as f:
            f.write(background_script)
        
        zip_path = os.path.join(temp_dir, "proxy_extension.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(extension_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, extension_path)
                    zipf.write(file_path, arcname)
        
        return zip_path
        
    except Exception as e:
        safe_print(f"Proxy extension olusturma hatasi: {e}")
        return None

class MobileAdClicker:
    def __init__(self, device_id, device_config, proxy_string=None):
        self.device_id = device_id
        self.device_config = device_config
        self.proxy_string = proxy_string
        self.proxy_info = None
        self.proxy_extension_path = None
        self.driver = None
        self.logger = logging.getLogger(f"Device{device_id:02d}")
        
        safe_print(f"MobileAdClicker.__init__ - proxy_string: {proxy_string}")
        
        if proxy_string:
            self.proxy_info = parse_proxy_string(proxy_string)
            if self.proxy_info:
                self.proxy_extension_path = create_proxy_extension(self.proxy_info)
                safe_print(f"Proxy extension oluşturuldu: {self.proxy_extension_path}")
            else:
                safe_print(f"Proxy parsing başarısız: {proxy_string}")
        else:
            safe_print(f"Proxy string yok")
        
    def create_driver(self):
        """Mobil cihaz için Chrome driver oluşturur"""
        try:
            chrome_options = webdriver.ChromeOptions()
            
            brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
            if os.path.exists(brave_path):
                chrome_options.binary_location = brave_path
            
            if self.proxy_string and (not self.proxy_extension_path or not os.path.exists(self.proxy_extension_path)):
                safe_print(f"Proxy extension yeniden oluşturuluyor: {self.proxy_string}")
                
                self.proxy_info = parse_proxy_string(self.proxy_string)
                if self.proxy_info:
                    self.proxy_extension_path = create_proxy_extension(self.proxy_info)
                    if self.proxy_extension_path:
                        safe_print(f"Proxy extension yeniden oluşturuldu: {self.proxy_extension_path}")
                    else:
                        safe_print(f"Proxy extension oluşturulamadı: {self.proxy_string}")
                else:
                    safe_print(f"Proxy parsing başarısız: {self.proxy_string}")
            
            if self.proxy_extension_path and os.path.exists(self.proxy_extension_path):
                chrome_options.add_extension(self.proxy_extension_path)
                safe_print(f"Proxy extension yüklendi: {self.proxy_extension_path}")
            elif self.proxy_string:
                safe_print(f"Proxy extension bulunamadı: {self.proxy_string}")

            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-gpu")
            # chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-java")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--no-first-run")
            chrome_options.add_argument("--no-default-browser-check")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-ssl-errors")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-geolocation")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-permissions-api")
            chrome_options.add_argument("--disable-features=LocationProvider")
            chrome_options.add_argument("--disable-features=GeolocationPermissionContext")
            chrome_options.add_argument("--disable-features=NotificationPermissionContext")
            
            chrome_options.add_argument("--clear-token-service")
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-breakpad")
            chrome_options.add_argument("--disable-client-side-phishing-detection")
            chrome_options.add_argument("--disable-component-update")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-domain-reliability")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-hang-monitor")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--force-color-profile=srgb")
            chrome_options.add_argument("--metrics-recording-only")
            chrome_options.add_argument("--no-crash-upload")
            chrome_options.add_argument("--no-zygote")
            chrome_options.add_argument("--use-mock-keychain")
            # chrome_options.add_argument("--incognito")  
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-webgl")
            chrome_options.add_argument("--disable-webgl2")
            chrome_options.add_argument("--disable-3d-apis")
            chrome_options.add_argument("--disable-webgl-image-chromium")
            chrome_options.add_argument("--disable-features=AudioServiceOutOfProcess")
            chrome_options.add_argument("--disable-features=MediaRouter")
            chrome_options.add_argument("--disable-speech-api")
            chrome_options.add_argument("--disable-file-system")
            chrome_options.add_argument("--disable-shared-workers")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor,VizServiceDisplay")
            chrome_options.add_argument("--disable-features=UserAgentClientHint")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--disable-log-file")
            chrome_options.add_argument("--disable-logging-redirect")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--silent")
            chrome_options.add_argument("--disable-background-mode")
            chrome_options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
            chrome_options.add_argument("--disable-features=ScriptStreaming")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-lcd-text")
            chrome_options.add_argument("--disable-gpu-rasterization")            


            if CHROME_OPTIONS.get("headless", False):
                chrome_options.add_argument("--headless")
                self.logger.info(f"{self.device_config['name']} - Headless modda başlatılıyor")
            
            chrome_options.add_argument(f"--user-agent={self.device_config['user_agent']}")
            
            chrome_options.add_argument(f"--window-size={self.device_config['viewport']['width']},{self.device_config['viewport']['height']}")
            
            prefs = {
                "profile.default_content_setting_values": {
                    "notifications": 2,  
                    "geolocation": 2,    
                    "media_stream": 2,   
                    "plugins": 2,        
                    "popups": 2,         
                    "mixed_script": 2,   
                    "mouselock": 2,      
                    "images": 2,         
                    "automatic_downloads": 2  
                },
                "profile.managed_default_content_settings": {
                    "notifications": 2,
                    "geolocation": 2
                }
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                self.logger.info(f"{self.device_config['name']} - Brave başlatıldı")
                return True
            except Exception as e:
                self.logger.error(f"Driver oluşturma hatası: {e}")
                return False
            
            self.driver.set_window_size(
                self.device_config['viewport']['width'],
                self.device_config['viewport']['height']
            )
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.inject_geolocation()
            
            self.clear_cookies_and_cache()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Driver oluşturma hatası: {e}")
            return False
    
    def inject_geolocation(self):
        """Coğrafi konum injection yapar"""
        if not self.driver or not LOCATION_INJECTION_ENABLED:
            return
            
        try:
            district_info = ISTANBUL_DISTRICTS.get(SELECTED_DISTRICT, {})
            if not district_info:
                safe_print(f"Ilce bilgisi bulunamadi: {SELECTED_DISTRICT}")
                return
                
            lat = district_info['lat']
            lng = district_info['lng']
            district_name = district_info['name']
            
            try:
                self.driver.execute_cdp_cmd('Browser.grantPermissions', {
                    'permissions': ['geolocation'],
                    'origin': 'https://www.google.com'
                })
                
                self.driver.execute_cdp_cmd('Emulation.setGeolocationOverride', {
                    'latitude': lat,
                    'longitude': lng,
                    'accuracy': 100
                })
                
                safe_print(f"Cografi konum ayarlandi: {district_name} ({lat}, {lng})")
                
            except Exception as cdp_error:
                safe_print(f"CDP desteklenmiyor, JavaScript override deneniyor: {cdp_error}")
                self.inject_geolocation_js(lat, lng, district_name)
                
        except Exception as e:
            safe_print(f"Geolocation injection hatasi: {e}")
    
    def inject_geolocation_js(self, lat, lng, district_name):
        """JavaScript ile geolocation override yapar"""
        try:
            geolocation_script = f"""

            Object.defineProperty(navigator.geolocation, 'getCurrentPosition', {{
                value: function(success, error, options) {{
                    setTimeout(function() {{
                        success({{
                            coords: {{
                                latitude: {lat},
                                longitude: {lng},
                                accuracy: 100,
                                altitude: null,
                                altitudeAccuracy: null,
                                heading: null,
                                speed: null
                            }},
                            timestamp: Date.now()
                        }});
                    }}, 100);
                }},
                writable: false,
                configurable: false
            }});
            
            Object.defineProperty(navigator.geolocation, 'watchPosition', {{
                value: function(success, error, options) {{
                    return navigator.geolocation.getCurrentPosition(success, error, options);
                }},
                writable: false,
                configurable: false
            }});
            
            // Koordinatları console'a yazdır
            console.log('Geolocation override: {district_name} - Lat: {lat}, Lng: {lng}');
            """
            
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': geolocation_script
            })
            
            self.driver.execute_script(geolocation_script)
            
            safe_print(f"JavaScript geolocation override uygulandı: {district_name}")
            
        except Exception as e:
            safe_print(f"JavaScript geolocation injection hatasi: {e}")
    
    def clear_cookies_and_cache(self):
        """Çerezleri ve cache'i temizler"""
        if not self.driver:
            return
            
        try:
            self.driver.get("about:blank")
            
            self.driver.delete_all_cookies()
            
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            
            self.driver.execute_script("""
                if (window.indexedDB) {
                    window.indexedDB.databases().then(function(dbs) {
                        dbs.forEach(function(db) {
                            window.indexedDB.deleteDatabase(db.name);
                        });
                    });
                }
            """)
            
            self.logger.info("Çerezler ve cache temizlendi")
            
        except Exception as e:
            self.logger.debug(f"Çerez temizleme hatası: {e}")
    
    def check_recaptcha(self):

        if not self.driver:
            return False
            
        try:

            recaptcha_selectors = [
                "div.g-recaptcha",
                "iframe[src*='recaptcha']",
                "div[class*='recaptcha']",
                "div[id*='recaptcha']",
                ".recaptcha",
                "div.captcha",
                "div[class*='captcha']",
                "div[id*='captcha']",
                ".captcha"
            ]
            
            for selector in recaptcha_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        return True
                except:
                    continue
            
            title = self.driver.title.lower()
            if any(word in title for word in ['captcha', 'recaptcha', 'robot', 'verify']):
                return True
            
            url = self.driver.current_url.lower()
            if any(word in url for word in ['captcha', 'recaptcha', 'robot', 'verify']):
                return True
            
            return False
            
        except Exception as e:
            self.logger.debug(f"reCAPTCHA kontrol hatası: {e}")
            return False
    
    def search_google(self, query):
        """Google'da arama yapar - reCAPTCHA kontrolü ile"""
        if not self.driver:
            return False
            
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                search_url = f"https://www.google.com.tr/search?q={query}&gl=tr&hl=tr"
                self.driver.get(search_url)
                time.sleep(random.uniform(2, 4))
                
                if self.check_recaptcha():
                    self.logger.warning(f"reCAPTCHA algılandı (Deneme {attempt + 1}/{max_attempts})")
                    if attempt < max_attempts - 1:
                        time.sleep(2)  # 2 saniye bekle
                        continue
                    else:
                        self.logger.error("reCAPTCHA çözülemedi, başarısız")
                        return False
                
                self.close_location_popup()
                
                self.logger.info(f"Arama yapıldı: {query}")
                
                time.sleep(1)
                self.close_location_popup()
                
                return True
                
            except Exception as e:
                self.logger.error(f"Arama hatası (Deneme {attempt + 1}): {e}")
                if attempt < max_attempts - 1:
                    time.sleep(2)
                    continue
                else:
                    return False
        
        return False
    
    def find_sponsored_ads(self):
        """Sadece sponsorlu reklamları bulur - tam odaklı versiyon"""
        if not self.driver:
            return []
            
        try:
            self.close_location_popup()
            
            sponsored_selectors = [
                "a[href*='/aclk?']",  
                "a[href*='&gclid=']", 
                "a[href*='adurl=']",  
                "a[href*='googleadservices.com']", 
                "a[href*='googlesyndication.com']", 
                "a[href*='doubleclick.net']", 
                "a[href*='googleads.g.doubleclick.net']", 
                "div[id*='tads'] a[href]", 
                "div[class*='ads'] a[href]", 
                "div[data-text-ad] a[href]", 
                "div[class*='commercial'] a[href]",
                "div[class*='sponsored'] a[href]", 
                "div[class*='mnr-c'] a[href]", 
                "div[class*='commercial-unit'] a[href]", 
                "li[class*='ads'] a[href]", 
                "li[data-ad] a[href]",
                "div[class*='pla-unit'] a[href]", 
                "div[class*='shopping-unit'] a[href]", 
                "div[data-async-context*='shopping'] a[href]", 
                
                "a[ping][href*='google']",
                "a[data-ctbtn][href]", 
                "a[data-ved][href*='aclk']", 
                "a[href*='click.googleadservices.com']", 
                "a[href*='&adurl=']"
            ]
            
            sponsored_xpath_selectors = [
                "//div[contains(text(), 'Sponsorlu') or contains(text(), 'Reklam') or contains(text(), 'Ad')]//a[@href]",
                "//span[contains(text(), 'Sponsorlu') or contains(text(), 'Reklam') or contains(text(), 'Ad')]//a[@href]",
                "//div[contains(@class, 'ad') or contains(@class, 'ads')]//a[@href and (contains(@href, 'aclk') or contains(@href, 'gclid') or contains(@href, 'adurl'))]",
                "//a[contains(@href, 'aclk') or contains(@href, 'gclid') or contains(@href, 'adurl')]",
                "//a[contains(@href, 'googleadservices') or contains(@href, 'googlesyndication')]",
                "//div[contains(@class, 'commercial') or contains(@class, 'sponsored')]//a[@href]"
            ]
            
            sponsored_ads = []
            processed_urls = set()
            
            for selector in sponsored_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and self.is_sponsored_ad(href) and href not in processed_urls:
                            text = element.text.strip()
                            if len(text) > 0:  
                                sponsored_ads.append({
                                    'element': element,
                                    'href': href,
                                    'text': text,
                                    'visible': element.is_displayed(),
                                    'clickable': True
                                })
                                processed_urls.add(href)
                except Exception as e:
                    self.logger.debug(f"CSS selector hatası {selector}: {e}")
                    continue
            
            for xpath in sponsored_xpath_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        href = element.get_attribute('href')
                        if href and self.is_sponsored_ad(href) and href not in processed_urls:
                            text = element.text.strip()
                            if len(text) > 0:
                                sponsored_ads.append({
                                    'element': element,
                                    'href': href,
                                    'text': text,
                                    'visible': element.is_displayed(),
                                    'clickable': True
                                })
                                processed_urls.add(href)
                except Exception as e:
                    self.logger.debug(f"XPath hatası {xpath}: {e}")
                    continue
            
            filtered_ads = []
            for ad in sponsored_ads:
                try:
                    if ad['visible'] and ad['element'].is_enabled():
                        location = ad['element'].location
                        size = ad['element'].size
                        if location['x'] >= 0 and location['y'] >= 0 and size['width'] > 0 and size['height'] > 0:
                            if self.verify_sponsored_ad(ad['element']):
                                filtered_ads.append(ad)
                except Exception as e:
                    self.logger.debug(f"Element filtreleme hatası: {e}")
                    continue
            
            unique_ads = []
            seen_domains = set()
            
            for ad in filtered_ads:
                try:
                    domain = self.extract_site_name(ad['href'])
                    if domain not in seen_domains:
                        unique_ads.append(ad)
                        seen_domains.add(domain)
                except Exception as e:
                    self.logger.debug(f"Domain çıkarma hatası: {e}")
                    continue
            
            if ENABLE_SITE_FILTERING:
                filtered_unique_ads = self.sort_ads_by_priority(unique_ads)
                self.logger.info(f"{len(filtered_unique_ads)} benzersiz sponsorlu reklam bulundu (Filtrelenmeden önce: {len(sponsored_ads)}, Filtrelendikten sonra: {len(unique_ads)})")
                return filtered_unique_ads
            else:
                self.logger.info(f"{len(unique_ads)} benzersiz sponsorlu reklam bulundu (Toplam: {len(sponsored_ads)})")
                return unique_ads
            
        except Exception as e:
            self.logger.error(f"Sponsorlu reklam arama hatası: {e}")
            return []
    
    def is_valid_web_url(self, url):
        """URL'nin geçerli web URL'si olup olmadığını kontrol eder - uygulama seçim ekranını önler"""
        if not url:
            return False
            
        if not (url.startswith('http://') or url.startswith('https://')):
            return False
            
        blocked_patterns = [
            'intent://',
            'market://',
            'app://',
            'applink://',
            'android-app://',
            'ios-app://',
            'itms://',
            'itms-apps://',
            'tel:',
            'mailto:',
            'sms:',
            'whatsapp:',
            'fb:',
            'twitter:',
            'instagram:',
            'linkedin:',
            'youtube:',
            'spotify:',
            'netflix:',
            'file://',
            'ftp://',
            'chrome://',
            'edge://',
            'firefox://',
            'about:',
            'javascript:',
            'data:',
            'blob:',
            'vbscript:',
            'play.google.com/store/apps',
            'apps.apple.com',
            'itunes.apple.com',
            'appstore://',
            'googleplay://',
            'facebook.com/tr/?',
            'twitter.com/intent/',
            'instagram.com/accounts/',
            'linkedin.com/oauth/',
            'youtube.com/redirect?',
            'viber://',
            'telegram://',
            'skype:',
            'zoom://',
            'slack://',
            'discord://',
            'tiktok://',
            'snapchat://',
            'pinterest://',
            'reddit://'
        ]
        
        url_lower = url.lower()
        for pattern in blocked_patterns:
            if pattern in url_lower:
                return False
        
        return True

    def is_sponsored_ad(self, href):
        """URL'nin sponsorlu reklam linki olup olmadığını kontrol eder - daha sıkı kriterler"""
        if not href:
            return False
            
        if not self.is_valid_web_url(href):
            self.logger.debug(f"URL reddedildi (uygulama linki): {href[:100]}...")
            return False
            
        sponsored_indicators = [
            'aclk', 'gclid=', 'adurl=', 'googleadservices', 'googlesyndication',
            'doubleclick', 'googleads.g.doubleclick.net',
            
            'click.googleadservices.com', '&adurl=', 'adnxs.com',
            'adsystem', 'adclick'
        ]
        
        href_lower = href.lower()
        return any(indicator in href_lower for indicator in sponsored_indicators)
    
    def verify_sponsored_ad(self, element):
        if not element:
            return False
            
        try:
            parent = element
            for _ in range(5):  
                try:
                    parent = parent.find_element(By.XPATH, "..")
                    parent_text = parent.text.lower()
                    parent_class = parent.get_attribute('class') or ""
                    parent_id = parent.get_attribute('id') or ""
                    
                    if any(word in parent_text for word in ['sponsorlu', 'reklam', 'ad', 'sponsored']):
                        return True
                    if any(word in parent_class.lower() for word in ['ad', 'ads', 'commercial', 'sponsored']):
                        return True
                    if any(word in parent_id.lower() for word in ['ad', 'ads', 'commercial', 'sponsored']):
                        return True
                except:
                    break
            
            element_class = element.get_attribute('class') or ""
            element_id = element.get_attribute('id') or ""
            
            if any(word in element_class.lower() for word in ['ad', 'ads', 'commercial', 'sponsored']):
                return True
            if any(word in element_id.lower() for word in ['ad', 'ads', 'commercial', 'sponsored']):
                return True
            
            return True  
            
        except Exception as e:
            self.logger.debug(f"Sponsored ad verification hatası: {e}")
            return True  
    
    def is_site_allowed(self, site_name):
        """Site'in tıklanmasına izin verilip verilmediğini kontrol eder"""
        if not ENABLE_SITE_FILTERING:
            return True
            
        if not PRIORITY_SITES and not BLOCKED_SITES:
            safe_print(f"Tüm siteler kabul - listeler boş: {site_name}")
            self.logger.info(f"Tüm siteler kabul (listeler boş): {site_name}")
            return True
            
        normalized_site = site_name.lower().replace('www.', '')
        
        for blocked_site in BLOCKED_SITES:
            blocked_normalized = blocked_site.lower().replace('www.', '')
            
            if (blocked_site.lower() in site_name.lower() or 
                blocked_normalized in normalized_site or
                normalized_site in blocked_normalized):
                
                safe_print(f"Site engellendi: {site_name} (kural: {blocked_site}) - Engellenen listede")
                self.logger.info(f"Site engellendi: {site_name} (kural: {blocked_site}) - Engellenen listede")
                return False
        
        if PRIORITY_SITES:
            for priority_site in PRIORITY_SITES:
                priority_normalized = priority_site.lower().replace('www.', '')
                
                if (priority_site.lower() in site_name.lower() or 
                    priority_normalized in normalized_site or
                    normalized_site in priority_normalized):
                    
                    safe_print(f"Öncelik sitesi kabul edildi: {site_name} (kural: {priority_site})")
                    self.logger.info(f"Öncelik sitesi kabul edildi: {site_name} (kural: {priority_site})")
                    return True
            
            safe_print(f"Site engellendi: {site_name} (öncelik listesinde değil - sadece öncelik sitelere izin)")
            self.logger.info(f"Site engellendi: {site_name} (öncelik listesinde değil)")
            return False
        
        safe_print(f"Site izin verildi: {site_name} (öncelik listesi boş, engellenmemiş)")
        self.logger.info(f"Site izin verildi: {site_name}")
        return True
    
    def is_priority_site(self, site_name):
        """Site'in öncelik sitesi olup olmadığını kontrol eder"""
        if not ENABLE_SITE_FILTERING:
            return False
            
        normalized_site = site_name.lower().replace('www.', '')
        
        for priority_site in PRIORITY_SITES:
            priority_normalized = priority_site.lower().replace('www.', '')
            
            if (priority_site.lower() in site_name.lower() or 
                priority_normalized in normalized_site or
                normalized_site in priority_normalized):
                
                safe_print(f"ncelik sitesi bulundu: {site_name} (kural: {priority_site})")
                self.logger.debug(f"Öncelik sitesi: {site_name} (kural: {priority_site})")
                return True
        
        return False
    
    def sort_ads_by_priority(self, ads):
        if not ENABLE_SITE_FILTERING or not ads:
            safe_print(f"Site filtreleme pasif veya reklam yok (Aktif: {ENABLE_SITE_FILTERING}, Reklam: {len(ads) if ads else 0})")
            return ads
        
        priority_ads = []
        regular_ads = []
        blocked_count = 0
        
        safe_print(f"Site filtreleme başlatılıyor - {len(ads)} reklam kontrol edilecek")
        safe_print(f"Engellenen siteler: {BLOCKED_SITES}")
        safe_print(f"Öncelik siteleri: {PRIORITY_SITES}")
        
        for ad in ads:
            try:
                site_name = self.extract_site_name(ad['href'])
                safe_print(f"Kontrol edilen site: {site_name}")
                
                if not self.is_site_allowed(site_name):
                    blocked_count += 1
                    safe_print(f"Reklam engellendi: {site_name}")
                    continue  
                
                if self.is_priority_site(site_name):
                    priority_ads.append(ad)
                    safe_print(f"Öncelik sitesi eklendi: {site_name}")
                else:
                    regular_ads.append(ad)
                    safe_print(f"Normal site eklendi: {site_name}")
                    
            except Exception as e:
                self.logger.debug(f"Site filtreleme hatası: {e}")
                regular_ads.append(ad)  # Hata durumunda normal listeye ekle
                safe_print(f"Site filtreleme hatası: {e}")
        
        filtered_ads = priority_ads + regular_ads
        

        
        self.logger.info(f"Site filtreleme: {len(priority_ads)} öncelik, {len(regular_ads)} normal, {blocked_count} engellendi")
        
        return filtered_ads
    
    def extract_site_name(self, ad_href):
        try:
            from urllib.parse import unquote, urlparse
            import re
            
            decoded_url = unquote(ad_href)
            
            param_patterns = [
                r'[?&]adurl=([^&]+)',
                r'[?&]url=([^&]+)',
                r'[?&]q=([^&]+)',
                r'[?&]dest_url=([^&]+)',
                r'[?&]link=([^&]+)',
                r'[?&]target=([^&]+)',
                r'[?&]goto=([^&]+)',
                r'[?&]redirect=([^&]+)'
            ]
            
            for pattern in param_patterns:
                matches = re.findall(pattern, decoded_url, re.IGNORECASE)
                for match in matches:
                    target_url = unquote(match)
                    if target_url.startswith(('http://', 'https://')):
                        try:
                            parsed = urlparse(target_url)
                            domain = parsed.netloc.replace('www.', '')
                            if domain and '.' in domain and 'google' not in domain.lower():
                                return domain
                        except:
                            continue
            
            try:
                parsed = urlparse(decoded_url)
                domain = parsed.netloc.replace('www.', '')
                if domain and '.' in domain and 'google' not in domain.lower():
                    return domain
            except:
                pass
            
            domain_patterns = [
                r'(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'//([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'\.([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            ]
            
            for pattern in domain_patterns:
                matches = re.findall(pattern, decoded_url, re.IGNORECASE)
                for match in matches:
                    domain = match.replace('www.', '')
                    if (domain and '.' in domain and 
                        not any(x in domain.lower() for x in ['google', 'gstatic', 'googleapis', 'doubleclick'])):
                        return domain
            
            return "Bilinmeyen Site"
            
        except Exception as e:
            self.logger.debug(f"Site adı çıkarma hatası: {e}")
            return "Site Adresi"
    
    def close_location_popup(self):
        if not self.driver:
            return False
            
        try:
            simdi_degil_selectors = [
                "//button[normalize-space(text())='Şimdi değil']",
                "//button[contains(normalize-space(text()), 'Şimdi değil')]",
                "//div[@role='button'][normalize-space(text())='Şimdi değil']",
                "//div[@role='button'][contains(normalize-space(text()), 'Şimdi değil')]",
                "//span[normalize-space(text())='Şimdi değil']",
                "//span[contains(normalize-space(text()), 'Şimdi değil')]",
                "//a[normalize-space(text())='Şimdi değil']",
                "//a[contains(normalize-space(text()), 'Şimdi değil')]",
                "//*[normalize-space(text())='Şimdi değil' and (name()='button' or name()='div' or name()='span' or name()='a')]",
                "//*[contains(normalize-space(text()), 'Şimdi değil')][@role='button']",
                "//*[contains(normalize-space(text()), 'Şimdi değil')][contains(@class, 'button')]"
            ]
            
            for selector in simdi_degil_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            self.logger.info("'Şimdi değil' popup'ı kapatıldı")
                            time.sleep(0.5)
                            return True
                except:
                    continue
            
            popup_selectors = [
                "button[aria-label*='Block']",
                "button[aria-label*='Engelle']",
                "button[aria-label*='Reddet']",
                "button[aria-label*='Deny']",
                "button[aria-label*='Don\'t allow']",
                "button[data-value='block']",
                "button[data-value='deny']",
                "div[role='button'][aria-label*='Block']",
                "div[role='button'][aria-label*='Engelle']"
            ]
            
            for selector in popup_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            self.logger.info("Konum bildirisi popup'ı kapatıldı (CSS)")
                            time.sleep(0.5)
                            return True
                except:
                    continue
            
            xpath_selectors = [
                "//button[contains(text(), 'Reddet')]",
                "//button[contains(text(), 'Engelle')]",
                "//button[contains(text(), 'İptal')]",
                "//button[contains(text(), 'Hayır')]",
                "//button[contains(text(), 'Deny')]",
                "//button[contains(text(), 'Block')]",
                "//button[contains(text(), 'Not now')]",
                "//button[contains(text(), 'Don\\'t allow')]",
                "//div[@role='button'][contains(text(), 'Reddet')]",
                "//div[@role='button'][contains(text(), 'Engelle')]",
                "//span[contains(text(), 'Reddet')]",
                "//a[contains(text(), 'Reddet')]",
                "//button[contains(text(), 'X')]",
                "//button[text()='×']",
                "//button[text()='✕']",
                "//button[@aria-label='Close']",
                "//button[@aria-label='Kapat']",
                "//button[@title='Close']",
                "//button[@title='Kapat']"
            ]
            
            for xpath in xpath_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            self.logger.info("Konum bildirisi popup'ı kapatıldı (XPath)")
                            time.sleep(0.5)
                            return True
                except:
                    continue
            
            general_selectors = [
                "[data-testid*='deny']",
                "[data-testid*='block']",
                "[data-testid*='cancel']",
                "[data-role='button'][aria-label*='Close']",
                "[data-role='button'][aria-label*='Kapat']",
                "button[class*='deny']",
                "button[class*='block']",
                "button[class*='cancel']",
                "button[class*='close']",
                "button[class*='reject']",
                "button[class*='decline']",
                "div[class*='popup'] button",
                "div[class*='dialog'] button",
                "div[class*='modal'] button",
                "[role='dialog'] button",
                "[role='alertdialog'] button"
            ]
            
            for selector in general_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element.click()
                            self.logger.info("Konum bildirisi popup'ı kapatıldı (Genel)")
                            time.sleep(0.5)
                            return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            self.logger.debug(f"Popup kapatma hatası: {e}")
            return False
    
    def click_sponsored_ad_with_new_tab(self, ad_element, ad_href, site_name):
        """Sponsorlu reklama yeni sekme açarak tıklar ve hemen kapatır - özel odaklı versiyon"""
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        if not self.driver:
            return False
            
        try:
            self.close_location_popup()
            
            if not self.verify_sponsored_ad(ad_element):
                self.logger.warning(f"{site_name} - Sponsorlu reklam doğrulanamadı")
                return False
            
            wait = WebDriverWait(self.driver, 5)
            clickable_element = wait.until(EC.element_to_be_clickable(ad_element))
            
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", clickable_element)
            time.sleep(0.5)
            
            if not clickable_element.is_displayed():
                self.logger.warning(f"{site_name} - Element görünür değil")
                return False
            
            initial_tabs = len(self.driver.window_handles)
            initial_window = self.driver.current_window_handle
            
            try:
                self.driver.execute_script("arguments[0].focus();", clickable_element)
                time.sleep(0.2)
                
                self.driver.execute_script("window.open(arguments[0], '_blank');", ad_href)
                
                time.sleep(0.05) 
                
                current_tabs = len(self.driver.window_handles)
                if current_tabs > initial_tabs:
                    new_window = None
                    for handle in self.driver.window_handles:
                        if handle != initial_window:
                            new_window = handle
                            break
                    
                    if new_window:
                        self.driver.switch_to.window(new_window)
                        
                        
                         
                        self.driver.close()
                        
                        self.driver.switch_to.window(initial_window)
                        
                        self.logger.info(f"{site_name} - JavaScript ile yeni sekme açıldı ve ANINDA kapatıldı")
                        return True
                        
            except Exception as js_open_error:
                self.logger.debug(f"JavaScript window.open hatası: {js_open_error}")
                
            try:
                clickable_element.click()
                time.sleep(0.1)
                
                actions = ActionChains(self.driver)
                actions.key_down(Keys.CONTROL).click(clickable_element).key_up(Keys.CONTROL).perform()
                
                time.sleep(0.05) 
                
                current_tabs = len(self.driver.window_handles)
                if current_tabs > initial_tabs:
                    new_window = None
                    for handle in self.driver.window_handles:
                        if handle != initial_window:
                            new_window = handle
                            break
                    
                    if new_window:
                        self.driver.switch_to.window(new_window)
                        

                        self.driver.close()
                        

                        self.driver.switch_to.window(initial_window)
                        
                        self.logger.info(f"{site_name} - Ctrl+Click ile yeni sekme açıldı ve ANINDA kapatıldı")
                        return True
                        
            except Exception as ctrl_click_error:
                self.logger.debug(f"Ctrl+Click hatası: {ctrl_click_error}")
                
            try:
                clickable_element.click()
                
                self.close_location_popup()
                
                self.driver.back()
                
                self.close_location_popup()
                
                self.logger.info(f"{RED}{site_name} - Normal click ile tıklandı (geri dönüldü)")
                return True
                
            except Exception as normal_click_error:
                self.logger.debug(f"Normal click hatası: {normal_click_error}")
                
            try:
                self.driver.execute_script("arguments[0].click();", clickable_element)
                
                self.close_location_popup()
                
                self.driver.back()
                
                self.close_location_popup()
                
                self.logger.info(f"{RED}{site_name} - JavaScript click ile tıklandı (geri dönüldü)")
                return True
                
            except Exception as js_click_error:
                self.logger.debug(f"JavaScript click hatası: {js_click_error}")
                
            return False
            
        except Exception as e:
            self.logger.error(f"{site_name} - Sponsorlu reklam tıklama hatası: {e}")
            return False
    
    def run_continuous_session(self, query):
        cycle_count = 0
        total_clicks = 0
        clicked_sites = set() 
        
        while True:
            try:
                cycle_count += 1
                self.logger.info(f"{self.device_config['name']} - Döngü #{cycle_count} başlatılıyor...")
                
                
                if not self.create_driver():
                    time.sleep(5)
                    continue
                
                
                if not self.search_google(query):
                    self.cleanup_driver()
                    continue
                
                ads = self.find_sponsored_ads()
                
                self.close_location_popup()
                
                if not ads:
                    self.cleanup_driver()
                    continue
                
                ads_to_click = []
                for ad in ads:
                    site_name = self.extract_site_name(ad['href'])
                    if site_name not in clicked_sites:
                        ads_to_click.append({
                            'ad': ad,
                            'site_name': site_name
                        })
                        clicked_sites.add(site_name)
                
                if not ads_to_click:
                    self.logger.info(f"Döngü #{cycle_count} - Yeni reklam yok, tüm siteler zaten tıklandı")
                    self.cleanup_driver()
                    time.sleep(random.uniform(5, 10))
                    continue
                
                self.logger.info(f"Döngü #{cycle_count} - {len(ads_to_click)} yeni reklam bulundu (Toplam: {len(ads)})")
                
                click_success_count = 0
                for i, ad_info in enumerate(ads_to_click, 1):
                    ad = ad_info['ad']
                    site_name = ad_info['site_name']
                    
                    self.logger.info(f"Döngü #{cycle_count} - Reklam {i}/{len(ads_to_click)}: {site_name}")
                    
                    self.close_location_popup()
                    
                    self.logger.info(f"{site_name} - Tıklanıyor...")
                    if self.click_sponsored_ad_with_new_tab(ad['element'], ad['href'], site_name):
                        click_success_count += 1
                        total_clicks += 1
                        self.logger.info(f"{site_name} - Tıklama başarılı")
                    else:
                        self.logger.warning(f"{site_name} - Tıklama başarısız")
                        clicked_sites.discard(site_name)
                    
                    self.close_location_popup()
                    
                    if i < len(ads_to_click):
                        time.sleep(random.uniform(0.5, 1.5))
                

                
                self.cleanup_driver()
                
                wait_time = random.uniform(8, 15)
                self.logger.info(f"{wait_time:.1f} saniye beklenecek...")
                time.sleep(wait_time)
                
            except KeyboardInterrupt:
                self.logger.info("Kullanıcı tarafından durduruldu")
                break
            except Exception as e:
                self.logger.error(f"Döngü #{cycle_count} hatası: {e}")
                self.cleanup_driver()
                time.sleep(5)
                continue
        
        # Final temizlik
        self.cleanup_driver()
        self.logger.info(f"{self.device_config['name']} - Toplam {cycle_count} döngü, {total_clicks} tıklama tamamlandı")
    
    def cleanup_driver(self):
        if self.driver:
            try:
                self.driver.quit()
                self.logger.debug("Driver kapatıldı")
            except:
                pass
            finally:
                self.driver = None
        
        if self.proxy_extension_path and os.path.exists(self.proxy_extension_path):
            try:
                os.remove(self.proxy_extension_path)
                temp_dir = os.path.dirname(self.proxy_extension_path)
                if os.path.exists(temp_dir):
                    import shutil
                    shutil.rmtree(temp_dir)
                self.logger.debug("Proxy extension temizlendi")
            except Exception as e:
                self.logger.debug(f"Proxy extension temizleme hatasi: {e}")

def run_continuous_parallel_device(device_id, device_config, query, proxy_string=None):
    clicker = MobileAdClicker(device_id, device_config, proxy_string)
    return clicker.run_continuous_session(query)

def main():
    try:
        import os
        if hasattr(os, 'setpgrp'):
            os.setpgrp()  
        elif hasattr(os, 'setpgid'):
            os.setpgid(0, 0)  
    except:
        pass  
    
    safe_print(f"{worker_count} Paralel Mobil Cihaz - Brave Tarayıcı ile Geliştirilmiş Reklam Tıklama Sistemi")
    safe_print("=" * 60)
    
    if not SEARCH_QUERIES:
        safe_print("Arama sorguları yapılandırılmamış!")
        return
    
    query = SEARCH_QUERIES[0]
    

    
    if ENABLE_SITE_FILTERING:
        safe_print(f"Site filtreleme: AKTİF")
        if PRIORITY_SITES:
            safe_print(f"Öncelik siteleri: {len(PRIORITY_SITES)} adet")
            for site in PRIORITY_SITES[:3]:  
                safe_print(f"   • {site}")
            if len(PRIORITY_SITES) > 3:
                safe_print(f"   • ... ve {len(PRIORITY_SITES) - 3} tane daha")
        
        if BLOCKED_SITES:
            safe_print(f"Engellenen siteler: {len(BLOCKED_SITES)} adet")
            for site in BLOCKED_SITES[:3]:  
                safe_print(f"   • {site}")
            if len(BLOCKED_SITES) > 3:
                safe_print(f"   • ... ve {len(BLOCKED_SITES) - 3} tane daha")
    else:
        safe_print(f"Site filtreleme: PASİF")
    
    safe_print("=" * 60)
    
    proxies = MOBILE_PROXIES if MOBILE_PROXIES else [None] * worker_count
    safe_print(f"🌐 Proxy sayisi: {len(proxies)}")
    for i, proxy in enumerate(proxies):
        if proxy:
            safe_print(f"   • Proxy {i+1}: {proxy.split('@')[1] if '@' in proxy else proxy}")
        else:
            safe_print(f"   • Proxy {i+1}: Yok")
    
    headless_status = "Evet" if CHROME_OPTIONS.get("headless", False) else "Hayır"
    safe_print(f"Headless modu: {headless_status}")
    
    if LOCATION_INJECTION_ENABLED:
        district_info = ISTANBUL_DISTRICTS.get(SELECTED_DISTRICT, {})
        district_name = district_info.get('name', SELECTED_DISTRICT)
        lat = district_info.get('lat', 'Bilinmiyor')
        lng = district_info.get('lng', 'Bilinmiyor') 
    else:
        safe_print(f"Cografi konum injection: PASIF")
    
    try:
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = []
            
            for i in range(worker_count):
                device_config = MOBILE_DEVICES[i % len(MOBILE_DEVICES)]  # Cihaz listesi döngüsel
                proxy_string = proxies[i % len(proxies)] if proxies and proxies[0] else None
                
                safe_print(f"Worker {i+1} için proxy_string: {proxy_string}")
                
                future = executor.submit(
                    run_continuous_parallel_device,
                    i + 1,
                    device_config,
                    query,
                    proxy_string
                )
                futures.append(future)
                
                if i < worker_count - 1:  
                    time.sleep(0.5)
            
            safe_print("Tüm cihazlar başlatıldı - Sürekli döngü aktif")
            safe_print("Durdurmak için Ctrl+C kullanın")
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    safe_print(f"Bir cihaz durdu")
                except Exception as e:
                    safe_print(f"Cihaz hatası: {e}")
    
    except KeyboardInterrupt:
        safe_print("Tüm cihazlar durduruluyor...")
    
    except Exception as e:
        safe_print(f"Sistem hatası: {e}")
    
    finally:
        safe_print("Sistem tamamen durduruldu")

if __name__ == "__main__":
    main() 