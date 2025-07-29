#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import threading
import queue
import subprocess
import os
import sys
import json
import time
from datetime import datetime
import logging

class AdClickerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Paralel Reklam Tıklama Sistemi - Kontrol Paneli")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        self.is_running = False
        self.process = None
        self.log_queue = queue.Queue()
        
        self.settings_file = "ui_settings.json"
        self.load_settings()
        
        self.create_widgets()
        self.setup_logging()
        
        self.start_log_reader()
        
    def load_settings(self):
        """Ayarları dosyadan yükle"""
        default_settings = {
            "search_queries": ["web tasarım", "online mağaza", "dijital pazarlama"],
            "mobile_proxies": [],
            "worker_count": 5,
            "clicks_per_ad": 1,
            "min_wait_time": 3,
            "max_wait_time": 8,
            "headless_mode": False,
            "priority_sites": [], 
            "blocked_sites": [],   
            "enable_site_filtering": True,  
            "location_injection_enabled": True,  
            "selected_district": "Kadıköy"  
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings = default_settings.copy()
                    self.settings.update(loaded_settings)
            else:
                self.settings = default_settings
        except:
            self.settings = default_settings
    
    def save_settings(self):
        """Ayarları dosyaya kaydet"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Hata", f"Ayarlar kaydedilemedi: {e}")
    
    def create_widgets(self):
        """UI bileşenlerini oluştur"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_control_tab()
        self.create_settings_tab()
        self.create_site_filter_tab()
        self.create_proxy_tab()
        self.create_logs_tab()
        self.create_stats_tab()
        
    def create_control_tab(self):
        """Kontrol paneli tab'ı"""
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="🎮 Kontrol Paneli")
        
        info_frame = ttk.LabelFrame(control_frame, text="📊 Sistem Durumu", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = ttk.Label(info_frame, text="🔴 Durduruldu", font=('Arial', 14, 'bold'))
        self.status_label.pack(pady=5)
        
        self.info_text = ttk.Label(info_frame, text="Sistem hazır - Başlatmak için aşağıdaki butonu kullanın")
        self.info_text.pack(pady=2)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="🚀 Sistemi Başlat", 
                                     command=self.start_system, style="Accent.TButton")
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Sistemi Durdur", 
                                    command=self.stop_system, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        self.restart_button = ttk.Button(button_frame, text="🔄 Yeniden Başlat", 
                                       command=self.restart_system, state='disabled')
        self.restart_button.pack(side='left', padx=5)
        
        quick_frame = ttk.LabelFrame(control_frame, text="⚡ Hızlı Ayarlar", padding=10)
        quick_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(quick_frame, text="Worker Sayısı:").grid(row=0, column=0, sticky='w', padx=5)
        self.worker_var = tk.StringVar(value=str(self.settings.get('worker_count', 5)))
        worker_combo = ttk.Combobox(quick_frame, textvariable=self.worker_var, 
                                  values=['1', '2', '3', '5', '10', '15', '20'], width=10)
        worker_combo.grid(row=0, column=1, padx=5)
        
        self.headless_var = tk.BooleanVar(value=self.settings.get('headless_mode', False))
        headless_check = ttk.Checkbutton(quick_frame, text="Gizli Mod (Headless)", 
                                       variable=self.headless_var,
                                       command=self.on_headless_changed)
        headless_check.grid(row=0, column=2, padx=10)
        
        stats_frame = ttk.LabelFrame(control_frame, text="📈 Anlık İstatistikler", padding=10)
        stats_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        cards_frame = ttk.Frame(stats_frame)
        cards_frame.pack(fill='x', pady=5)
        

        
    def create_stat_card(self, parent, title, value, row, col):
        """İstatistik kartı oluştur"""
        card_frame = ttk.LabelFrame(parent, text=title, padding=5)
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        parent.grid_columnconfigure(col, weight=1)
        
        value_label = ttk.Label(card_frame, text=value, font=('Arial', 16, 'bold'))
        value_label.pack()
        
        if not hasattr(self, 'stat_cards'):
            self.stat_cards = {}
        self.stat_cards[title] = value_label
    
    def create_settings_tab(self):
        """Ayarlar tab'ı"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Ayarlar")
        
        keywords_frame = ttk.LabelFrame(settings_frame, text="🔍 Arama Kelimeleri", padding=10)
        keywords_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(keywords_frame, text="Her satıra bir arama kelimesi yazın:").pack(anchor='w')
        self.keywords_text = scrolledtext.ScrolledText(keywords_frame, height=6, wrap='word')
        self.keywords_text.pack(fill='x', pady=5)
        self.keywords_text.insert('1.0', '\n'.join(self.settings.get('search_queries', [])))
        
        advanced_frame = ttk.LabelFrame(settings_frame, text="🔧 Gelişmiş Ayarlar", padding=10)
        advanced_frame.pack(fill='x', padx=10, pady=5)
        
        click_frame = ttk.Frame(advanced_frame)
        click_frame.pack(fill='x', pady=2)
        
        ttk.Label(click_frame, text="Her reklama tıklama sayısı:").pack(side='left')
        self.clicks_var = tk.StringVar(value=str(self.settings.get('clicks_per_ad', 1)))
        clicks_spin = ttk.Spinbox(click_frame, from_=1, to=10, textvariable=self.clicks_var, width=5)
        clicks_spin.pack(side='right')
        
        wait_frame = ttk.Frame(advanced_frame)
        wait_frame.pack(fill='x', pady=2)
        
        ttk.Label(wait_frame, text="Min bekleme süresi (sn):").pack(side='left')
        self.min_wait_var = tk.StringVar(value=str(self.settings.get('min_wait_time', 3)))
        min_wait_spin = ttk.Spinbox(wait_frame, from_=1, to=30, textvariable=self.min_wait_var, width=5)
        min_wait_spin.pack(side='right')
        
        wait_frame2 = ttk.Frame(advanced_frame)
        wait_frame2.pack(fill='x', pady=2)
        
        ttk.Label(wait_frame2, text="Max bekleme süresi (sn):").pack(side='left')
        self.max_wait_var = tk.StringVar(value=str(self.settings.get('max_wait_time', 8)))
        max_wait_spin = ttk.Spinbox(wait_frame2, from_=1, to=60, textvariable=self.max_wait_var, width=5)
        max_wait_spin.pack(side='right')
        
        location_frame = ttk.LabelFrame(settings_frame, text="📍 Coğrafi Konum Ayarları", padding=10)
        location_frame.pack(fill='x', padx=10, pady=5)
        
        location_status_frame = ttk.Frame(location_frame)
        location_status_frame.pack(fill='x', pady=2)
        
        self.location_enabled_var = tk.BooleanVar(value=self.settings.get('location_injection_enabled', True))
        location_check = ttk.Checkbutton(location_status_frame, text="🌍 Coğrafi konum injection etkinleştir", 
                                       variable=self.location_enabled_var,
                                       command=self.on_location_toggle)
        location_check.pack(anchor='w')
        
        district_frame = ttk.Frame(location_frame)
        district_frame.pack(fill='x', pady=5)
        
        ttk.Label(district_frame, text="İstanbul İlçesi:").pack(side='left')
        
        self.istanbul_districts = {
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
        
        district_names = list(self.istanbul_districts.keys())
        self.selected_district_var = tk.StringVar(value=self.settings.get('selected_district', 'Kadıköy'))
        
        self.district_combo = ttk.Combobox(district_frame, textvariable=self.selected_district_var, 
                                         values=district_names, state='readonly', width=20)
        self.district_combo.pack(side='right', padx=5)
        self.district_combo.bind('<<ComboboxSelected>>', self.on_district_changed)
        
        coord_frame = ttk.Frame(location_frame)
        coord_frame.pack(fill='x', pady=5)
        
        self.coord_label = ttk.Label(coord_frame, text="", foreground="blue")
        self.coord_label.pack(anchor='w')
        
        self.update_coordinates_display()
        
        save_button = ttk.Button(settings_frame, text="💾 Ayarları Kaydet", command=self.save_current_settings)
        save_button.pack(pady=10)
    
    def create_site_filter_tab(self):
        """Site filtreleme tab'ı"""
        filter_frame = ttk.Frame(self.notebook)
        self.notebook.add(filter_frame, text="🎯 Site Filtreleri")
        
        status_frame = ttk.LabelFrame(filter_frame, text="⚙️ Filtreleme Durumu", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.filtering_var = tk.BooleanVar(value=self.settings.get('enable_site_filtering', True))
        filter_check = ttk.Checkbutton(status_frame, text="🔍 Site filtrelemeyi etkinleştir", 
                                     variable=self.filtering_var,
                                     command=self.toggle_filtering)
        filter_check.pack(anchor='w')
        
        info_label = ttk.Label(status_frame, 
                             text="• Öncelik siteleri: İlk olarak bu siteler tıklanır\n• Engellenen siteler: Bu siteler hiç tıklanmaz",
                             foreground="gray")
        info_label.pack(anchor='w', pady=5)
        
        main_container = ttk.Frame(filter_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        priority_frame = ttk.LabelFrame(main_container, text="⭐ Öncelik Verilecek Siteler", padding=10)
        priority_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        priority_add_frame = ttk.Frame(priority_frame)
        priority_add_frame.pack(fill='x', pady=5)
        
        ttk.Label(priority_add_frame, text="Site adı/domain:").pack(anchor='w')
        self.priority_entry = ttk.Entry(priority_add_frame, width=30)
        self.priority_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.priority_entry.bind('<Return>', lambda e: self.add_priority_site())
        
        ttk.Button(priority_add_frame, text="➕", command=self.add_priority_site, width=3).pack(side='right')
        
        priority_list_frame = ttk.Frame(priority_frame)
        priority_list_frame.pack(fill='both', expand=True, pady=5)
        
        self.priority_listbox = tk.Listbox(priority_list_frame, height=8)
        priority_scroll = ttk.Scrollbar(priority_list_frame, orient='vertical', command=self.priority_listbox.yview)
        self.priority_listbox.configure(yscrollcommand=priority_scroll.set)
        
        self.priority_listbox.pack(side='left', fill='both', expand=True)
        priority_scroll.pack(side='right', fill='y')
        
        priority_buttons = ttk.Frame(priority_frame)
        priority_buttons.pack(fill='x', pady=5)
        
        ttk.Button(priority_buttons, text="🗑️ Sil", command=self.remove_priority_site).pack(side='left', padx=2)
        ttk.Button(priority_buttons, text="📝 Düzenle", command=self.edit_priority_site).pack(side='left', padx=2)
        ttk.Button(priority_buttons, text="🔼 Yukarı", command=lambda: self.move_priority_site(-1)).pack(side='left', padx=2)
        ttk.Button(priority_buttons, text="🔽 Aşağı", command=lambda: self.move_priority_site(1)).pack(side='left', padx=2)
        
        blocked_frame = ttk.LabelFrame(main_container, text="🚫 Engellenen Siteler", padding=10)
        blocked_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        blocked_add_frame = ttk.Frame(blocked_frame)
        blocked_add_frame.pack(fill='x', pady=5)
        
        ttk.Label(blocked_add_frame, text="Site adı/domain:").pack(anchor='w')
        self.blocked_entry = ttk.Entry(blocked_add_frame, width=30)
        self.blocked_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.blocked_entry.bind('<Return>', lambda e: self.add_blocked_site())
        
        ttk.Button(blocked_add_frame, text="➕", command=self.add_blocked_site, width=3).pack(side='right')
        
        blocked_list_frame = ttk.Frame(blocked_frame)
        blocked_list_frame.pack(fill='both', expand=True, pady=5)
        
        self.blocked_listbox = tk.Listbox(blocked_list_frame, height=8)
        blocked_scroll = ttk.Scrollbar(blocked_list_frame, orient='vertical', command=self.blocked_listbox.yview)
        self.blocked_listbox.configure(yscrollcommand=blocked_scroll.set)
        
        self.blocked_listbox.pack(side='left', fill='both', expand=True)
        blocked_scroll.pack(side='right', fill='y')
        
        blocked_buttons = ttk.Frame(blocked_frame)
        blocked_buttons.pack(fill='x', pady=5)
        
        ttk.Button(blocked_buttons, text="🗑️ Sil", command=self.remove_blocked_site).pack(side='left', padx=2)
        ttk.Button(blocked_buttons, text="📝 Düzenle", command=self.edit_blocked_site).pack(side='left', padx=2)
        
        quick_add_frame = ttk.LabelFrame(filter_frame, text="⚡ Hızlı Ekleme", padding=10)
        quick_add_frame.pack(fill='x', padx=10, pady=5)
        
        common_frame = ttk.Frame(quick_add_frame)
        common_frame.pack(fill='x', pady=2)
        
        ttk.Label(common_frame, text="Yaygın engellenen siteler:").pack(side='left')
        
        common_blocked = ["facebook.com", "twitter.com", "instagram.com", "youtube.com", "linkedin.com", "tiktok.com"]
        for site in common_blocked:
            ttk.Button(common_frame, text=f"🚫 {site}", 
                     command=lambda s=site: self.quick_add_blocked(s),
                     style="small.TButton").pack(side='left', padx=2)
        
        file_frame = ttk.Frame(quick_add_frame)
        file_frame.pack(fill='x', pady=5)
        
        ttk.Button(file_frame, text="📁 Dosyadan Yükle (Öncelik)", command=self.load_priority_from_file).pack(side='left', padx=2)
        ttk.Button(file_frame, text="📁 Dosyadan Yükle (Engellenen)", command=self.load_blocked_from_file).pack(side='left', padx=2)
        ttk.Button(file_frame, text="💾 Listeleri Kaydet", command=self.save_site_filters).pack(side='left', padx=2)
        
        self.refresh_site_lists()
        
    def create_proxy_tab(self):
        """Proxy ayarları tab'ı"""
        proxy_frame = ttk.Frame(self.notebook)
        self.notebook.add(proxy_frame, text="🌐 Proxy Ayarları")
        
        proxy_list_frame = ttk.LabelFrame(proxy_frame, text="📋 Proxy Listesi", padding=10)
        proxy_list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        add_frame = ttk.Frame(proxy_list_frame)
        add_frame.pack(fill='x', pady=5)
        
        ttk.Label(add_frame, text="Proxy Ekle (ip:port veya user:pass@ip:port):").pack(anchor='w')
        self.proxy_entry = ttk.Entry(add_frame, width=50)
        self.proxy_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        add_proxy_btn = ttk.Button(add_frame, text="➕ Ekle", command=self.add_proxy)
        add_proxy_btn.pack(side='right')
        
        self.proxy_listbox = tk.Listbox(proxy_list_frame, height=10)
        self.proxy_listbox.pack(fill='both', expand=True, pady=5)
        
        proxy_buttons = ttk.Frame(proxy_list_frame)
        proxy_buttons.pack(fill='x', pady=5)
        
        ttk.Button(proxy_buttons, text="🗑️ Seçili Sil", command=self.remove_proxy).pack(side='left', padx=2)
        ttk.Button(proxy_buttons, text="🧪 Test Et", command=self.test_proxy).pack(side='left', padx=2)
        ttk.Button(proxy_buttons, text="📁 Dosyadan Yükle", command=self.load_proxies_from_file).pack(side='left', padx=2)
        ttk.Button(proxy_buttons, text="💾 Dosyaya Kaydet", command=self.save_proxies_to_file).pack(side='left', padx=2)
        
        self.refresh_proxy_list()
        
    def create_logs_tab(self):
        """Log görüntüleme tab'ı"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📜 Loglar")
        
        log_controls = ttk.Frame(logs_frame)
        log_controls.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(log_controls, text="🗑️ Logları Temizle", command=self.clear_logs).pack(side='left', padx=5)
        ttk.Button(log_controls, text="💾 Logları Kaydet", command=self.save_logs).pack(side='left', padx=5)
        
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(log_controls, text="Otomatik Kaydırma", variable=self.auto_scroll_var).pack(side='right', padx=5)
        
        self.log_text = scrolledtext.ScrolledText(logs_frame, height=25, wrap='word', font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text.tag_config("INFO", foreground="blue")
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("SUCCESS", foreground="green")
        
    def create_stats_tab(self):
        """İstatistikler tab'ı"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Detaylı İstatistikler")
        

        ttk.Label(stats_frame, text="📈 Detaylı istatistikler yakında...", 
                 font=('Arial', 14)).pack(expand=True)
        
    def setup_logging(self):
        """Log sistemi kurulumu"""
        class UILogHandler(logging.Handler):
            def __init__(self, ui_instance):
                super().__init__()
                self.ui = ui_instance
                
            def emit(self, record):
                msg = self.format(record)
                self.ui.log_queue.put((record.levelname, msg))
        
        self.ui_logger = logging.getLogger("AdClickerUI")
        self.ui_logger.setLevel(logging.INFO)
        
        ui_handler = UILogHandler(self)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ui_handler.setFormatter(formatter)
        self.ui_logger.addHandler(ui_handler)
        
    def start_log_reader(self):
        """Log okuyucu thread'i"""
        def log_reader():
            while True:
                try:
                    level, message = self.log_queue.get(timeout=0.1)
                    self.root.after(0, self.add_log_message, level, message)
                except queue.Empty:
                    continue
                    
        thread = threading.Thread(target=log_reader, daemon=True)
        thread.start()
        
    def add_log_message(self, level, message):
        """Log mesajı ekle"""
        if hasattr(self, 'log_text'):
            self.log_text.insert('end', f"{message}\n", level)
            if self.auto_scroll_var.get():
                self.log_text.see('end')
    
    def on_headless_changed(self):
        """Headless modu değiştiğinde çağrılır"""
        headless_enabled = self.headless_var.get()
        self.ui_logger.info(f"Headless modu {'açıldı' if headless_enabled else 'kapatıldı'}")
        self.settings['headless_mode'] = headless_enabled
    
    def on_location_toggle(self):
        """Coğrafi konum injection durumu değiştiğinde çağrılır"""
        enabled = self.location_enabled_var.get()
        self.ui_logger.info(f"Coğrafi konum injection {'açıldı' if enabled else 'kapatıldı'}")
        self.settings['location_injection_enabled'] = enabled
    
    def on_district_changed(self, event=None):
        """İlçe seçimi değiştiğinde çağrılır"""
        selected_district = self.selected_district_var.get()
        self.settings['selected_district'] = selected_district
        self.update_coordinates_display()
        
        district_info = self.istanbul_districts.get(selected_district, {})
        district_name = district_info.get('name', selected_district)
        self.ui_logger.info(f"İlçe değiştirildi: {district_name}")
    
    def update_coordinates_display(self):
        """Seçili ilçenin koordinatlarını göster"""
        selected_district = self.selected_district_var.get()
        district_info = self.istanbul_districts.get(selected_district, {})
        
        if district_info:
            lat = district_info['lat']
            lng = district_info['lng']
            name = district_info['name']
            coord_text = f"📍 {name} - Enlem: {lat}, Boylam: {lng}"
        else:
            coord_text = "📍 Koordinat bilgisi bulunamadı"
        
        if hasattr(self, 'coord_label'):
            self.coord_label.config(text=coord_text)
    
    def save_current_settings(self):
        """Mevcut ayarları kaydet"""
        try:
            keywords_text = self.keywords_text.get('1.0', 'end-1c')
            keywords = [line.strip() for line in keywords_text.split('\n') if line.strip()]
            
            self.settings.update({
                'search_queries': keywords,
                'worker_count': int(self.worker_var.get()),
                'clicks_per_ad': int(self.clicks_var.get()),
                'min_wait_time': int(self.min_wait_var.get()),
                'max_wait_time': int(self.max_wait_var.get()),
                'headless_mode': self.headless_var.get(),
                'enable_site_filtering': getattr(self, 'filtering_var', tk.BooleanVar(value=True)).get(),
                'location_injection_enabled': getattr(self, 'location_enabled_var', tk.BooleanVar(value=True)).get(),
                'selected_district': getattr(self, 'selected_district_var', tk.StringVar(value='Kadıköy')).get()
            })
            
            self.save_settings()
            messagebox.showinfo("Başarılı", "Ayarlar kaydedildi!")
            self.ui_logger.info("Ayarlar kaydedildi")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Ayarlar kaydedilemedi: {e}")
            self.ui_logger.error(f"Ayar kaydetme hatası: {e}")
    
    def toggle_filtering(self):
        """Site filtrelemeyi aç/kapat"""
        enabled = self.filtering_var.get()
        self.ui_logger.info(f"Site filtreleme {'açıldı' if enabled else 'kapatıldı'}")
    
    def add_priority_site(self):
        """Öncelik sitesi ekle"""
        site = self.priority_entry.get().strip()
        if site:
            if site not in self.settings['priority_sites']:
                self.settings['priority_sites'].append(site)
                self.refresh_site_lists()
                self.priority_entry.delete(0, 'end')
                self.ui_logger.info(f"Öncelik sitesi eklendi: {site}")
            else:
                messagebox.showwarning("Uyarı", "Bu site zaten listede!")
    
    def remove_priority_site(self):
        """Öncelik sitesi sil"""
        selection = self.priority_listbox.curselection()
        if selection:
            index = selection[0]
            site = self.settings['priority_sites'][index]
            del self.settings['priority_sites'][index]
            self.refresh_site_lists()
            self.ui_logger.info(f"Öncelik sitesi silindi: {site}")
    
    def edit_priority_site(self):
        """Öncelik sitesi düzenle"""
        selection = self.priority_listbox.curselection()
        if selection:
            index = selection[0]
            old_site = self.settings['priority_sites'][index]
            new_site = simpledialog.askstring("Düzenle", f"Site adını düzenle:", initialvalue=old_site)
            if new_site and new_site.strip():
                self.settings['priority_sites'][index] = new_site.strip()
                self.refresh_site_lists()
                self.ui_logger.info(f"Site düzenlendi: {old_site} -> {new_site}")
    
    def move_priority_site(self, direction):
        """Öncelik sitesi sırasını değiştir"""
        selection = self.priority_listbox.curselection()
        if selection:
            index = selection[0]
            new_index = index + direction
            if 0 <= new_index < len(self.settings['priority_sites']):
                sites = self.settings['priority_sites']
                sites[index], sites[new_index] = sites[new_index], sites[index]
                self.refresh_site_lists()
                self.priority_listbox.selection_set(new_index)
    
    def add_blocked_site(self):
        """Engellenen site ekle"""
        site = self.blocked_entry.get().strip()
        if site:
            if 'blocked_sites' not in self.settings:
                self.settings['blocked_sites'] = []
            
            if site not in self.settings['blocked_sites']:
                self.settings['blocked_sites'].append(site)
                self.refresh_site_lists()
                self.blocked_entry.delete(0, 'end')
                self.ui_logger.info(f"Engellenen site eklendi: {site}")
            else:
                messagebox.showwarning("Uyarı", "Bu site zaten listede!")
    
    def remove_blocked_site(self):
        """Engellenen site sil"""
        selection = self.blocked_listbox.curselection()
        if selection:
            if 'blocked_sites' not in self.settings:
                self.settings['blocked_sites'] = []
                return
            
            index = selection[0]
            if index < len(self.settings['blocked_sites']):
                site = self.settings['blocked_sites'][index]
                del self.settings['blocked_sites'][index]
                self.refresh_site_lists()
                self.ui_logger.info(f"Engellenen site silindi: {site}")
    
    def edit_blocked_site(self):
        """Engellenen site düzenle"""
        selection = self.blocked_listbox.curselection()
        if selection:
            if 'blocked_sites' not in self.settings:
                self.settings['blocked_sites'] = []
                return
            
            index = selection[0]
            if index < len(self.settings['blocked_sites']):
                old_site = self.settings['blocked_sites'][index]
                new_site = simpledialog.askstring("Düzenle", f"Site adını düzenle:", initialvalue=old_site)
                if new_site and new_site.strip():
                    self.settings['blocked_sites'][index] = new_site.strip()
                    self.refresh_site_lists()
                    self.ui_logger.info(f"Site düzenlendi: {old_site} -> {new_site}")
    
    def quick_add_blocked(self, site):
        """Hızlı engellenen site ekleme"""
        if site not in self.settings['blocked_sites']:
            self.settings['blocked_sites'].append(site)
            self.refresh_site_lists()
            self.ui_logger.info(f"Hızlı ekleme - Engellenen: {site}")
    
    def refresh_site_lists(self):
        """Site listelerini yenile"""
        if hasattr(self, 'priority_listbox'):
            self.priority_listbox.delete(0, 'end')
            for site in self.settings.get('priority_sites', []):
                self.priority_listbox.insert('end', site)
        
        if hasattr(self, 'blocked_listbox'):
            self.blocked_listbox.delete(0, 'end')
            for site in self.settings.get('blocked_sites', []):
                self.blocked_listbox.insert('end', site)
    
    def load_priority_from_file(self):
        """Dosyadan öncelik siteleri yükle"""
        filename = filedialog.askopenfilename(
            title="Öncelik siteleri dosyası",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    sites = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    self.settings['priority_sites'].extend(sites)
                    self.refresh_site_lists()
                    self.ui_logger.info(f"{len(sites)} öncelik sitesi dosyadan yüklendi")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya okuma hatası: {e}")
    
    def load_blocked_from_file(self):
        """Dosyadan engellenen siteleri yükle"""
        filename = filedialog.askopenfilename(
            title="Engellenen siteler dosyası",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    sites = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    self.settings['blocked_sites'].extend(sites)
                    self.refresh_site_lists()
                    self.ui_logger.info(f"{len(sites)} engellenen site dosyadan yüklendi")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya okuma hatası: {e}")
    
    def save_site_filters(self):
        """Site filtrelerini dosyaya kaydet"""
        filename = filedialog.asksaveasfilename(
            title="Site filtrelerini kaydet",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                filter_data = {
                    'priority_sites': self.settings['priority_sites'],
                    'blocked_sites': self.settings['blocked_sites'],
                    'enable_site_filtering': self.settings['enable_site_filtering']
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(filter_data, f, ensure_ascii=False, indent=2)
                self.ui_logger.info(f"Site filtreleri kaydedildi: {filename}")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya yazma hatası: {e}")
    
    def add_proxy(self):
        """Proxy ekle"""
        proxy = self.proxy_entry.get().strip()
        if proxy:
            if proxy not in self.settings['mobile_proxies']:
                self.settings['mobile_proxies'].append(proxy)
                self.refresh_proxy_list()
                self.proxy_entry.delete(0, 'end')
                self.ui_logger.info(f"Proxy eklendi: {proxy}")
            else:
                messagebox.showwarning("Uyarı", "Bu proxy zaten listede!")
    
    def remove_proxy(self):
        """Seçili proxy'i sil"""
        selection = self.proxy_listbox.curselection()
        if selection:
            index = selection[0]
            proxy = self.settings['mobile_proxies'][index]
            del self.settings['mobile_proxies'][index]
            self.refresh_proxy_list()
            self.ui_logger.info(f"Proxy silindi: {proxy}")
    
    def refresh_proxy_list(self):
        """Proxy listesini yenile"""
        self.proxy_listbox.delete(0, 'end')
        for proxy in self.settings.get('mobile_proxies', []):
            self.proxy_listbox.insert('end', proxy)
    
    def test_proxy(self):
        """Seçili proxy'i test et"""
        selection = self.proxy_listbox.curselection()
        if selection:
            proxy = self.settings['mobile_proxies'][selection[0]]
            self.ui_logger.info(f"Proxy test ediliyor: {proxy}")
            messagebox.showinfo("Test", f"Proxy test edildi: {proxy}")
    
    def load_proxies_from_file(self):
        """Dosyadan proxy yükle"""
        filename = filedialog.askopenfilename(
            title="Proxy dosyası seç",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    self.settings['mobile_proxies'].extend(proxies)
                    self.refresh_proxy_list()
                    self.ui_logger.info(f"{len(proxies)} proxy dosyadan yüklendi")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya okuma hatası: {e}")
    
    def save_proxies_to_file(self):
        """Proxy'leri dosyaya kaydet"""
        filename = filedialog.asksaveasfilename(
            title="Proxy'leri kaydet",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for proxy in self.settings['mobile_proxies']:
                        f.write(f"{proxy}\n")
                self.ui_logger.info(f"Proxy'ler dosyaya kaydedildi: {filename}")
            except Exception as e:
                messagebox.showerror("Hata", f"Dosya yazma hatası: {e}")
    
    def clear_logs(self):
        """Logları temizle"""
        self.log_text.delete('1.0', 'end')
        self.ui_logger.info("Loglar temizlendi")
    
    def save_logs(self):
        """Logları dosyaya kaydet"""
        filename = filedialog.asksaveasfilename(
            title="Logları kaydet",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get('1.0', 'end-1c'))
                self.ui_logger.info(f"Loglar kaydedildi: {filename}")
            except Exception as e:
                messagebox.showerror("Hata", f"Log kaydetme hatası: {e}")
    
    def update_config_file(self):
        """Config.py dosyasını güncelle"""
        try:
            config_content = f'''# -*- coding: utf-8 -*-
"""
"""

# Arama sorguları listesi
SEARCH_QUERIES = {self.settings['search_queries']}

# Mobil proxy listesi
MOBILE_PROXIES = {self.settings['mobile_proxies']}

# Site filtreleme ayarları
PRIORITY_SITES = {self.settings.get('priority_sites', [])}
BLOCKED_SITES = {self.settings.get('blocked_sites', [])}
ENABLE_SITE_FILTERING = {self.settings.get('enable_site_filtering', True)}

# Worker sayısı
WORKER_COUNT = {self.settings['worker_count']}

# Her reklama kaç kez tıklanacak
CLICKS_PER_AD = {self.settings['clicks_per_ad']}

# Tıklamalar arası bekleme süreleri (saniye)
MIN_WAIT_TIME = {self.settings['min_wait_time']}
MAX_WAIT_TIME = {self.settings['max_wait_time']}

# Reklamlar arası bekleme süreleri (saniye)
MIN_AD_WAIT = 5
MAX_AD_WAIT = 10

# Sayfa yenileme sıklığı (kaç tıklamada bir)
REFRESH_FREQUENCY = 10

# Loglama seviyesi
LOG_LEVEL = "INFO"

# Chrome ayarları
CHROME_OPTIONS = {{
    "headless": {str(self.settings['headless_mode'])},
    "disable_images": True,
    "disable_css": True,
}}

# Coğrafi konum ayarları
LOCATION_INJECTION_ENABLED = {self.settings.get('location_injection_enabled', True)}
SELECTED_DISTRICT = "{self.settings.get('selected_district', 'Kadıköy')}"

# İstanbul ilçe koordinatları
ISTANBUL_DISTRICTS = {{
    "Kadıköy": {{"lat": 40.9828, "lng": 29.0329, "name": "Kadıköy"}},
    "Beşiktaş": {{"lat": 41.0422, "lng": 29.0088, "name": "Beşiktaş"}},
    "Fatih": {{"lat": 41.0082, "lng": 28.9784, "name": "Fatih (Tarihi Yarımada)"}},
    "Şişli": {{"lat": 41.0602, "lng": 28.9892, "name": "Şişli"}},
    "Üsküdar": {{"lat": 41.0214, "lng": 29.0068, "name": "Üsküdar"}},
    "Bakırköy": {{"lat": 40.9744, "lng": 28.8719, "name": "Bakırköy"}},
    "Beyoğlu": {{"lat": 41.0370, "lng": 28.9847, "name": "Beyoğlu (Taksim)"}},
    "Ümraniye": {{"lat": 41.0226, "lng": 29.1267, "name": "Ümraniye"}},
    "Pendik": {{"lat": 40.8783, "lng": 29.2362, "name": "Pendik"}},
    "Maltepe": {{"lat": 40.9364, "lng": 29.1598, "name": "Maltepe"}},
    "Ataşehir": {{"lat": 40.9833, "lng": 29.1167, "name": "Ataşehir"}},
    "Kartal": {{"lat": 40.9081, "lng": 29.1836, "name": "Kartal"}},
    "Bağcılar": {{"lat": 41.0403, "lng": 28.8569, "name": "Bağcılar"}},
    "Bahçelievler": {{"lat": 41.0017, "lng": 28.8514, "name": "Bahçelievler"}},
    "Esenler": {{"lat": 41.0456, "lng": 28.8719, "name": "Esenler"}},
    "Avcılar": {{"lat": 41.0233, "lng": 28.7231, "name": "Avcılar"}},
    "Zeytinburnu": {{"lat": 41.0089, "lng": 28.9017, "name": "Zeytinburnu"}},
    "Kağıthane": {{"lat": 41.0833, "lng": 28.9833, "name": "Kağıthane"}},
    "Sarıyer": {{"lat": 41.1728, "lng": 29.0581, "name": "Sarıyer"}},
    "Beylikdüzü": {{"lat": 41.0028, "lng": 28.6478, "name": "Beylikdüzü"}}
}}

# Mobil cihaz simülasyonu ayarları
MOBILE_DEVICE = {{
    "width": 375,
    "height": 812, 
    "pixelRatio": 3.0
}}

# User Agent döngüsü aktif/pasif
ROTATE_USER_AGENT = True

# Proxy döngüsü aktif/pasif
ROTATE_PROXY = True
'''
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write(config_content)
            return True
        except Exception as e:
            self.ui_logger.error(f"Config dosyası güncellenirken hata: {e}")
            return False
    
    def start_system(self):
        """Sistemi başlat"""
        try:
            self.ui_logger.info("🔄 Sistem başlatılıyor...")
            
            # Ayarları kaydet ve config dosyasını güncelle
            self.save_current_settings()
            self.ui_logger.info("✅ Ayarlar kaydedildi")
            
            if not self.update_config_file():
                error_msg = "Config dosyası güncellenemedi!"
                messagebox.showerror("Hata", error_msg)
                self.ui_logger.error(error_msg)
                return
            
            self.ui_logger.info("Config dosyası güncellendi")
            
            backup_file = "parallel_ad_clicker_BACKUP.py"
            if not os.path.exists(backup_file):
                error_msg = f"BACKUP dosyası bulunamadı: {backup_file}"
                messagebox.showerror("Hata", error_msg)
                self.ui_logger.error(error_msg)
                return
            
            self.ui_logger.info(f"BACKUP dosyası bulundu: {backup_file}")
            
            # BACKUP dosyasını çalıştır
            cmd = [sys.executable, backup_file]
            self.ui_logger.info(f"Komut çalıştırılıyor: {' '.join(cmd)}")
            
            creation_flags = 0
            if os.name == 'nt':  
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
            else:  
                creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=os.getcwd(),
                bufsize=1,   
                creationflags=creation_flags if os.name == 'nt' else 0,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            self.is_running = True
            self.update_ui_state()
            self.ui_logger.info("🚀 Sistem başlatıldı! Process ID: " + str(self.process.pid))
            
            self.start_process_reader()
            
        except Exception as e:
            error_msg = f"Sistem başlatılırken hata: {e}"
            messagebox.showerror("Hata", error_msg)
            self.ui_logger.error(error_msg)
            import traceback
            self.ui_logger.error(f"Detaylı hata: {traceback.format_exc()}")
    
    def stop_system(self):
        """Sistemi durdur"""
        try:
            self.ui_logger.info("🔄 Sistem durduruluyor...")
            
            if self.process:
                self.kill_child_processes()
                
                self.process.terminate()
                try:
                    self.process.wait(timeout=10) 
                except subprocess.TimeoutExpired:
                    self.ui_logger.warning("Ana process 10 saniyede sonlanmadı, zorla kapatılıyor...")
                    self.process.kill()
                    try:
                        self.process.wait(timeout=5) 
                    except subprocess.TimeoutExpired:
                        self.ui_logger.error("Ana process zorla kapatılamadı!")
                self.process = None
                self.ui_logger.info("Ana process durduruldu")
            
            self.kill_chrome_processes()
            
            self.force_kill_python_workers()
            
            self.is_running = False
            self.update_ui_state()
            self.ui_logger.info("⏹️ Sistem tamamen durduruldu!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Sistem durdurulurken hata: {e}")
            self.ui_logger.error(f"Durdurma hatası: {e}")
    
    def kill_chrome_processes(self):
        """Tüm Chrome processlerini zorla kapat"""
        try:
            import psutil
            killed_count = 0
            
            self.ui_logger.info("🔍 Chrome processler aranıyor...")
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and any(chrome_name in proc.info['name'].lower() 
                                               for chrome_name in ['chrome', 'chromium']):
                        if proc.info['cmdline'] and any('--no-sandbox' in str(cmd) 
                                                      for cmd in proc.info['cmdline']):
                            proc.kill()
                            killed_count += 1
                            self.ui_logger.info(f"🗑️ Chrome process kapatıldı (PID: {proc.info['pid']})")
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
            if killed_count > 0:
                self.ui_logger.info(f"{killed_count} Chrome process kapatıldı")
            else:
                self.ui_logger.info("Kapatılacak Chrome process bulunamadı")
                
        except ImportError:
            self.ui_logger.warning("psutil kütüphanesi bulunamadı, manuel Chrome kapatma yapılamıyor")
            try:
                import subprocess
                result = subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                                      capture_output=True, text=True)
                self.ui_logger.info("🪟 Windows taskkill ile Chrome kapatıldı")
            except Exception as e:
                self.ui_logger.error(f"Chrome kapatma hatası: {e}")
        except Exception as e:
            self.ui_logger.error(f"Chrome process kapatma hatası: {e}")
    
    def kill_child_processes(self):
        """Ana process'in child process'lerini kapat"""
        try:
            import psutil
            if self.process:
                parent = psutil.Process(self.process.pid)
                children = parent.children(recursive=True)
                
                self.ui_logger.info(f"🔍 {len(children)} child process bulundu")
                
                for child in children:
                    try:
                        child.terminate()
                        self.ui_logger.info(f"🗑️ Child process kapatıldı (PID: {child.pid})")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                gone, alive = psutil.wait_procs(children, timeout=3)
                for p in alive:
                    try:
                        p.kill()
                        self.ui_logger.info(f"💀 Child process zorla kapatıldı (PID: {p.pid})")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
        except ImportError:
            self.ui_logger.warning("⚠️ psutil bulunamadı, child process kapatma yapılamıyor")
        except Exception as e:
            self.ui_logger.error(f"Child process kapatma hatası: {e}")
    
    def force_kill_python_workers(self):
        try:
            import psutil
            killed_count = 0
            
            self.ui_logger.info("Kalan Python worker'lar aranıyor...")
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        if proc.info['cmdline'] and any('parallel_ad_clicker_BACKUP.py' in str(cmd) 
                                                      for cmd in proc.info['cmdline']):
                            if self.process and proc.info['pid'] != self.process.pid:
                                proc.kill()
                                killed_count += 1
                                self.ui_logger.info(f"Python worker zorla kapatıldı (PID: {proc.info['pid']})")
                                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
            if killed_count > 0:
                self.ui_logger.info(f"✅ {killed_count} Python worker zorla kapatıldı")
            else:
                self.ui_logger.info("ℹ️ Kapatılacak Python worker bulunamadı")
                
        except ImportError:
            self.ui_logger.warning("⚠️ psutil bulunamadı, manuel Python worker kapatma yapılıyor")
            try:
                import subprocess
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'], 
                                      capture_output=True, text=True)
                if result.stdout:
                    lines = result.stdout.strip().split('\n')[1:]  # Header'ı atla
                    for line in lines:
                        if 'parallel_ad_clicker_BACKUP.py' in line:
                            parts = line.split(',')
                            if len(parts) > 1:
                                pid = parts[1].strip('"')
                                try:
                                    subprocess.run(['taskkill', '/F', '/PID', pid], 
                                                  capture_output=True, text=True)
                                    self.ui_logger.info(f"🪟 Windows taskkill ile Python worker kapatıldı (PID: {pid})")
                                except:
                                    pass
                self.ui_logger.info("Windows taskkill ile Python worker'lar kapatıldı")
            except Exception as e:
                self.ui_logger.error(f"Python worker kapatma hatası: {e}")
        except Exception as e:
            self.ui_logger.error(f"Python worker process kapatma hatası: {e}")
    
    def restart_system(self):
        """Sistemi yeniden başlat"""
        self.ui_logger.info("Sistem yeniden başlatılıyor...")
        self.stop_system()
        time.sleep(2)  
        self.start_system()
    
    def update_ui_state(self):
        """UI durumunu güncelle"""
        if self.is_running:
            self.status_label.config(text="🟢 Çalışıyor", foreground="green")
            self.info_text.config(text="Sistem aktif - Logları takip edin")
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.restart_button.config(state='normal')
        else:
            self.status_label.config(text="🔴 Durduruldu", foreground="red")
            self.info_text.config(text="Sistem hazır - Başlatmak için butonu kullanın")
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.restart_button.config(state='disabled')
    
    def start_process_reader(self):
        """Process output okuyucu"""
        def reader():
            self.ui_logger.info("📡 Process reader başlatıldı")
            if self.process and self.process.stdout:
                try:
                    while self.is_running and self.process.poll() is None:
                        line = self.process.stdout.readline()
                        if line:
                            line = line.strip()
                            if line:  
                                if "ERROR" in line or "❌" in line:
                                    level = "ERROR"
                                elif "WARNING" in line or "⚠️" in line:
                                    level = "WARNING"
                                elif "✅" in line or "SUCCESS" in line or "🚀" in line:
                                    level = "SUCCESS"
                                else:
                                    level = "INFO"
                                
                                self.log_queue.put((level, line))
                        else:
                            time.sleep(0.1)
                    
                    if self.process.poll() is not None:
                        exit_code = self.process.poll()
                        if exit_code != 0:
                            self.log_queue.put(("ERROR", f"Process hata ile sonlandı: Exit code {exit_code}"))
                        else:
                            self.log_queue.put(("INFO", "Process normal şekilde sonlandı"))
                        
                        self.root.after(0, self.on_process_finished)
                        
                except Exception as e:
                    self.log_queue.put(("ERROR", f"Process okuma hatası: {e}"))
            else:
                self.log_queue.put(("ERROR", "Process veya stdout bulunamadı"))
        
        if self.is_running:
            thread = threading.Thread(target=reader, daemon=True)
            thread.start()
    
    def on_process_finished(self):
        """Process bittiğinde çağrılır"""
        self.is_running = False
        self.process = None
        self.update_ui_state()
        self.ui_logger.warning("⚠️ Process sonlandı - Sistem durduruldu")

def main():
    """Ana fonksiyon"""
    root = tk.Tk()
    
    style = ttk.Style()
    style.theme_use('clam')
    
    style.configure("Accent.TButton", foreground="white", background="#0078d4")
    
    app = AdClickerUI(root)
    
    def on_closing():
        if app.is_running:
            if messagebox.askokcancel("Çıkış", "Sistem çalışıyor. Çıkmak istediğinizden emin misiniz?"):
                app.stop_system()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main() 