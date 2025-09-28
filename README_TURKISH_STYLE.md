# Amerika At Hesaplama Sistemi - Turkish Style

Bu sistem Amerika at yarışları için Türk hesaplama mantığını kullanır.

## 🚀 Yeni Özellikler (Turkish Style)

### 1. **Derece Bazlı Penalty Sistemi**
- **1. ile 2. arası**: 0.10 saniye penalty
- **1. ile 3. arası**: 0.20 saniye penalty
- **1. ile 4. arası**: 0.30 saniye penalty
- **1. ile 5. arası**: 0.40 saniye penalty
- Ve böyle devam eder...

### 2. **Mesafe Bazlı Dağıtım**
Penalty yarışın toplam uzunluğuna göre 100 metrelik bölümlere dağıtılır:
```
Penalty per 100m = (derece - 1) × 0.10 ÷ (mesafe ÷ 100)
```

### 3. **Kazanan Referans Sistemi**
- **Önemli**: Sistemdeki veriler atın kendi derecesi değil, **o yarıştaki birincinin derecesidir**
- Eğer at geçmiş yarışta 1. olduysa penalty eklenmez
- Diğer dereceler için mesafe bazlı penalty eklenir

## 📊 Hesaplama Adımları

### Adım 1: Temel Süre Hesaplama
```python
base_time_per_100m = total_time_seconds ÷ (distance_meters ÷ 100)
```

### Adım 2: Zemin Adaptasyonu
```python
surface_factors = {
    ('Dirt', 'Turf'): 1.02,     # +%2 penalty
    ('Turf', 'Dirt'): 0.98,     # -%2 bonus
    ('Synthetic', 'Dirt'): 0.99,
    # vs...
}
```

### Adım 3: Mesafe Adaptasyonu
```python
if mesafe_farki > 0:  # Uzun mesafe
    factor = 1 + (fark/100) × 0.04/6.0
else:  # Kısa mesafe
    factor = 1 + (fark/100) × (-0.03)/6.0
```

### Adım 4: Derece Penalty'si
```python
if finish_position > 1:
    penalty_per_race = (position - 1) × 0.10
    penalty_per_100m = penalty_per_race ÷ (distance_meters ÷ 100)
    final_time = adjusted_time + penalty_per_100m
```

## 🎯 Örnek Hesaplama

**At**: Thunder Bolt  
**Geçmiş**: 1:24.50, 6F, Dirt, **3. sıra**  
**Bugün**: 7F, Turf  

```
1. Base time: 84.5s ÷ (1207m ÷ 100) = 7.00 s/100m
2. Surface: 7.00 × 1.02 (Dirt→Turf) = 7.14 s/100m
3. Distance: 7.14 × 1.013 (6F→7F) = 7.24 s/100m
4. Position: 7.24 + 0.014 (3rd place penalty) = 7.25 s/100m
```

**Final Score: 7.25 s/100m**

## 📁 Dosya Yapısı

```
hrn_scraper/
├── american_horse_calculator_turkish_style.py  # Yeni Turkish Style hesaplama
├── american_horse_calculator.py                # Ana calculator (güncellendi)
├── american_horse_calculator_pure.py           # Saf hesaplama (eski)
├── american_horse_calculator_with_position.py  # Position bazlı (eski)
└── templates/
    └── american_index.html                     # Web arayüzü (güncellendi)
```

## 🛠️ Kullanım

### 1. Terminal'den Çalıştırma
```bash
cd hrn_scraper
python american_horse_calculator_turkish_style.py
```

### 2. Web Arayüzünden
```bash
python american_horse_calculator.py
# http://localhost:5000 adresine git
```

### 3. Programmatik Kullanım
```python
from american_horse_calculator_turkish_style import process_horses_data_turkish_style

horses = [...] # CSV'den yüklenen at verileri
results = process_horses_data_turkish_style(horses)
```

## 📈 Çıktı Formatı

CSV çıktısında şu kolonlar bulunur:
- `horse_name`: At adı
- `performance_score`: Final performans skoru (s/100m)
- `latest_finish_position`: Geçmiş yarıştaki sıralama
- `calc_position_penalty_applied`: Penalty uygulandı mı?
- `calc_surface_factor`: Zemin adaptasyon faktörü
- `calc_distance_factor`: Mesafe adaptasyon faktörü
- `calc_total_race_time`: Tahmini toplam yarış süresi

## 🔧 Geliştirici Notları

### Penalty Hesaplama Detayları
- Her derece için **0.10 saniye** eklenir (toplam yarış için)
- Bu penalty **100m bazında** dağıtılır
- Kısa yarışlarda penalty etkisi daha fazla
- Uzun yarışlarda penalty etkisi daha az

### Zemin Adaptasyonu
- Dirt → Turf: +%2 (daha yavaş)
- Turf → Dirt: -%2 (daha hızlı)
- Synthetic geçişleri: ±%1-3

### Mesafe Adaptasyonu  
- Uzun mesafe: Her 100m için +0.04s penalty
- Kısa mesafe: Her 100m için -0.03s bonus
- 100m'den az fark: adaptasyon yok

## ⚡ Performans

Sistem şu özellikleri destekler:
- ✅ Saniyede 100+ at hesaplama
- ✅ Çoklu yarış desteği
- ✅ Otomatik sıralama (düşük skor = iyi)
- ✅ Detaylı hata raporlama
- ✅ CSV/JSON çıktı

## 🐛 Bilinen Sorunlar

1. **Position Data Missing**: Bazı atlarda derece bilgisi eksik olabilir
2. **Surface Mapping**: Zemin türü eşleme bazen hatalı olabilir
3. **Distance Parsing**: Karmaşık mesafe formatları (1 1/16M) bazen parse edilemez

## 📞 Destek

Sorularınız için: Turkish Style American Horse Calculator v1.0