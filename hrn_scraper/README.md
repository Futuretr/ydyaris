# Horse Racing Nation Scraper 🏇

Bu proje Horse Racing Nation sitesinden (https://entries.horseracingnation.com/) günlük at yarışı verilerini çekmeye yarar.

## ✅ Başarıyla Test Edildi!

**Santa Anita 2024-12-27 Test Sonuçları:**
- ✅ 9 yarış başarıyla çekildi
- ✅ 66 at girişi toplamda çekildi  
- ✅ Yarış sonuçları çekildi
- ✅ JSON ve CSV dosyaları oluştu
- ✅ Tüm veriler doğru formatta

## Özellikler

- 🎯 **Tam URL Desteği**: Doğrudan HRN linklerini kullanabilirsiniz
- 🏆 **Kapsamlı Veri**: Yarış bilgileri, at girişleri, sonuçlar
- 📊 **Çoklu Format**: JSON ve CSV export
- 🔧 **Kolay Kullanım**: Batch dosyaları ile tek tık
- 📝 **Detaylı Log**: Her adım kayıt altında
- 🛡️ **Hata Yönetimi**: Güvenilir scraping

## Kurulum

### 1. Python Kurulumu
Python 3.8+ gerekli. Bu projede Python 3.13 test edildi.

### 2. Paket Kurulumu
```bash
# Otomatik kurulum (Windows)
install_packages.bat

# Manuel kurulum  
pip install -r requirements.txt
```

## Kullanım

### 🚀 Hızlı Başlangıç - URL ile

```bash
# Doğrudan HRN URL'si ile
python single_track_scraper.py "https://entries.horseracingnation.com/races/2024-12-27/santa-anita"
```

### 📁 Batch Dosyaları

```bash
# Test yap
run_test.bat

# Sadece Santa Anita'yı tara  
scrape_santa_anita.bat

# Günün tüm pistlerini tara
scrape_all_today.bat
```

### 💻 Manuel Kullanım

```python
# Belirli bir pist için
python single_track_scraper.py santa-anita 2024-12-27

# Mevcut pistleri listele
python single_track_scraper.py --list-tracks 2024-12-27

# Ana scraper ile tüm pistler
python hrn_scraper.py
```

## 📁 Çıktı Dosyaları

Scraper şu dosyaları oluşturur:

### JSON Dosyası
- **Dosya**: `santa-anita_2024_12_27.json`
- **İçerik**: Tüm veri yapılandırılmış formatta

### CSV Dosyaları  
- **Entries**: `santa-anita_2024_12_27_santa-anita_entries.csv`
- **Results**: `santa-anita_2024_12_27_santa-anita_results.csv`

### CSV Sütunları (Entries)
- track_name, race_number, post_position, program_number
- horse_name, speed_figure, sire, trainer_jockey, morning_line

## 🔍 Örnek Kullanım

```bash
# URL örneği (tercih edilen)
python single_track_scraper.py "https://entries.horseracingnation.com/races/2024-12-27/santa-anita"

# Slug + tarih örneği  
python single_track_scraper.py santa-anita 2024-12-27

# Bugün için
python single_track_scraper.py santa-anita

# Farklı pistler
python single_track_scraper.py gulfstream 2024-12-27
python single_track_scraper.py oaklawn 2024-12-27
```

## 🛠️ Debug ve Geliştirme

```bash
# HTML yapısını incele
python debug_html.py

# Tek yarışı test et
python debug_single_race.py

# Bağlantı testi
python test_scraper.py

# URL formatlarını test et
python test_url.py
```

## 📊 Veri Yapısı

### Race Data
```json
{
  "track_name": "santa-anita",
  "race_number": 1,
  "post_time": "12:00 PM", 
  "distance": "6F",
  "surface": "Turf",
  "purse": "$34,000",
  "entries": [...],
  "results": [...]
}
```

### Entry Data
```json
{
  "post_position": 1,
  "program_number": 1,
  "horse_info": {
    "horse_name": "Shop Till You Drop",
    "speed_figure": 91,
    "sire": "Free Drop Billy"
  },
  "trainer_jockey": "Richard BaltasKazushi Kimura",
  "morning_line": "10/1"
}
```

## ⚠️ Önemli Notlar

- **URL Formatı**: `/races/` URL'leri otomatik olarak `/entries-results/` formatına çevrilir
- **Rate Limiting**: Siteden çok hızlı veri çekmemeye dikkat edin
- **Logging**: `hrn_scraper.log` dosyasında detaylı loglar
- **Hata Durumu**: Network hataları otomatik yeniden denenir

## 🚨 Sorun Giderme

### Python Bulunamıyor
```bash
# install_packages.bat dosyasında Python path'ini güncelleyin
set PYTHON_PATH="C:\Users\...\python.exe"
```

### Bağlantı Hatası
```bash
# Test script ile kontrol edin
python test_url.py
```

### Veri Çekilmiyor
```bash
# Debug script ile inceleyin
python debug_single_race.py
```

## 📈 Desteklenen Pistler

Tüm Horse Racing Nation'da bulunan pistler desteklenir:
- Santa Anita, Gulfstream, Oaklawn
- Keeneland, Churchill Downs, Belmont
- ve daha fazlası...

---

**Son Güncelleme**: 2025-09-28  
**Test Edilen**: Santa Anita 2024-12-27 ✅  
**Durum**: Tam Çalışır 🎉