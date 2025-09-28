#!/usr/bin/env python3
"""
Amerika At Hesaplama Terminal Uygulaması
Basit mesafe-zaman performans hesaplaması
Zemin adaptasyonu ve kilo hesaplaması yok
"""

import os
import json
import csv
import sys
from datetime import datetime
import logging
from single_track_scraper import scrape_single_track
from horse_profile_scraper import HorseProfileScraper

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def time_to_seconds(time_str):
    """Zaman string'ini saniyeye çevir (1:25.61 -> 85.61)"""
    try:
        if not time_str or str(time_str).strip() == '' or str(time_str) == 'nan':
            return 0
        
        time_str = str(time_str).strip()
        
        if ':' in time_str:
            parts = time_str.split(':')
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        else:
            return float(time_str)
    except:
        return 0

def distance_to_meters(distance_str):
    """Mesafe string'ini metreye çevir"""
    try:
        if not distance_str or str(distance_str).strip() == '':
            return 1200
        
        distance_str = str(distance_str).strip().lower()
        
        # Furlong işleme (1f = ~201.17m)
        if 'f' in distance_str:
            furlongs = float(distance_str.replace('f', '').strip())
            return furlongs * 201.17
        
        # Mile işleme (1 mile = 1609.34m)
        elif 'mile' in distance_str or 'm' in distance_str:
            if 'mile' in distance_str:
                miles = float(distance_str.replace('mile', '').strip())
            else:
                miles = float(distance_str.replace('m', '').strip())
            return miles * 1609.34
        
        # Yard işleme (1 yard = 0.9144m)
        elif 'y' in distance_str or 'yard' in distance_str:
            yards = float(distance_str.replace('y', '').replace('yard', '').strip())
            return yards * 0.9144
        
        # Direkt metre
        else:
            return float(distance_str)
            
    except:
        return 1200

def calculate_simple_performance(horse_profile, current_distance_str):
    """Basit performans hesaplama - sadece zaman ve mesafe"""
    try:
        # Gerekli veriler kontrolü
        if not horse_profile.get('time') or not horse_profile.get('distance'):
            return None
        
        # Zamanı saniyeye çevir
        time_seconds = time_to_seconds(horse_profile['time'])
        if time_seconds <= 0:
            return None
        
        # Mesafeyi metreye çevir
        prev_distance_meters = distance_to_meters(horse_profile['distance'])
        current_distance_meters = distance_to_meters(current_distance_str)
        
        # Önceki yarıştaki 100m başına süre
        time_per_100m_prev = time_seconds / (prev_distance_meters / 100)
        
        # Mesafe adaptasyonu (basit)
        distance_diff = current_distance_meters - prev_distance_meters
        
        if distance_diff != 0:
            # Mesafe farklılığı faktörü (basit hesaplama)
            if distance_diff > 0:  # Daha uzun mesafe
                distance_factor = 1 + (abs(distance_diff) / current_distance_meters) * 0.02
            else:  # Daha kısa mesafe
                distance_factor = 1 - (abs(distance_diff) / current_distance_meters) * 0.015
        else:
            distance_factor = 1.0
        
        # Final performans skoru
        adjusted_time_per_100m = time_per_100m_prev * distance_factor
        
        return {
            'original_time': time_seconds,
            'original_distance_meters': prev_distance_meters,
            'target_distance_meters': current_distance_meters,
            'time_per_100m_original': time_per_100m_prev,
            'distance_factor': distance_factor,
            'final_score': adjusted_time_per_100m
        }
        
    except Exception as e:
        logger.error(f"Performans hesaplama hatası: {e}")
        return None

def load_horse_data_from_csv(csv_file):
    """CSV dosyasından at verilerini yükle"""
    try:
        horses = []
        with open(csv_file, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                horses.append(dict(row))
        return horses
    except Exception as e:
        logger.error(f"CSV okuma hatası: {e}")
        return []

def process_track_data(track_slug, race_date):
    """Hipodrom verilerini çek ve hesapla"""
    try:
        print(f"\n🔄 {track_slug} verisi çekiliyor - {race_date}")
        
        # İlk önce yarış verilerini çek (entries CSV)
        success = scrape_single_track(track_slug, race_date)
        
        if not success:
            print(f"❌ {track_slug} yarış verileri çekilemedi")
            return []
        
        # CSV dosyasını bul
        entries_csv = f"{track_slug}_{race_date.replace('-', '_')}_{track_slug}_entries.csv"
        
        if not os.path.exists(entries_csv):
            print(f"❌ Entries dosyası bulunamadı: {entries_csv}")
            return []
        
        # At entries verilerini yükle
        entries_data = load_horse_data_from_csv(entries_csv)
        
        if not entries_data:
            print(f"❌ {track_slug} at verileri yüklenemedi")
            return []
        
        print(f"✅ {len(entries_data)} at bulundu")
        
        # At profil verilerini çek
        print(f"🐎 At profil verileri çekiliyor...")
        scraper = HorseProfileScraper()
        
        calculated_horses = []
        success_count = 0
        
        for i, entry in enumerate(entries_data):
            horse_name = entry.get('horse_name', '').strip()
            race_number = entry.get('race_number', '1')
            program_number = entry.get('program_number', '')
            entry_distance = entry.get('distance', '6f')
            entry_surface = entry.get('surface', 'Dirt')
            
            print(f"  {i+1}/{len(entries_data)}: {horse_name}")
            
            if not horse_name:
                calculated_horses.append({
                    'track': track_slug,
                    'date': race_date,
                    'race_number': race_number,
                    'program_number': program_number,
                    'horse_name': horse_name,
                    'entry_distance': entry_distance,
                    'entry_surface': entry_surface,
                    'profile_distance': '',
                    'profile_time': '',
                    'profile_surface': '',
                    'performance_score': '',
                    'calculation_status': 'İsim yok'
                })
                continue
            
            try:
                # At profilini çek
                profile = scraper.scrape_horse_profile(horse_name)
                
                if not profile or not profile.get('race_history'):
                    calculated_horses.append({
                        'track': track_slug,
                        'date': race_date,
                        'race_number': race_number,
                        'program_number': program_number,
                        'horse_name': horse_name,
                        'entry_distance': entry_distance,
                        'entry_surface': entry_surface,
                        'profile_distance': '',
                        'profile_time': '',
                        'profile_surface': '',
                        'performance_score': '',
                        'calculation_status': 'Profil yok'
                    })
                    continue
                
                # En son yarışı al
                latest_race = profile['race_history'][0]
                profile_distance = latest_race.get('distance', '')
                profile_time = latest_race.get('time', '')
                profile_surface = latest_race.get('surface', '')
                
                # Performans hesapla
                horse_profile_data = {
                    'time': profile_time,
                    'distance': profile_distance,
                    'surface': profile_surface
                }
                
                performance = calculate_simple_performance(horse_profile_data, entry_distance)
                
                if performance:
                    performance_score = round(performance['final_score'], 2)
                    calculation_status = 'Başarılı'
                    success_count += 1
                else:
                    performance_score = ''
                    calculation_status = 'Hesaplama hatası'
                
                calculated_horses.append({
                    'track': track_slug,
                    'date': race_date,
                    'race_number': race_number,
                    'program_number': program_number,
                    'horse_name': horse_name,
                    'entry_distance': entry_distance,
                    'entry_surface': entry_surface,
                    'profile_distance': profile_distance,
                    'profile_time': profile_time,
                    'profile_surface': profile_surface,
                    'performance_score': performance_score,
                    'calculation_status': calculation_status
                })
                
            except Exception as e:
                logger.warning(f"Profil çekme hatası {horse_name}: {e}")
                calculated_horses.append({
                    'track': track_slug,
                    'date': race_date,
                    'race_number': race_number,
                    'program_number': program_number,
                    'horse_name': horse_name,
                    'entry_distance': entry_distance,
                    'entry_surface': entry_surface,
                    'profile_distance': '',
                    'profile_time': '',
                    'profile_surface': '',
                    'performance_score': '',
                    'calculation_status': f'Hata: {str(e)}'
                })
        
        print(f"📊 Hesaplama tamamlandı: {success_count}/{len(entries_data)} başarılı")
        return calculated_horses
        
    except Exception as e:
        logger.error(f"Track işleme hatası: {e}")
        return []

def save_to_csv(horses_data, filename):
    """Verileri CSV'ye kaydet"""
    try:
        if not horses_data:
            print("❌ Kaydedilecek veri yok")
            return False
        
        fieldnames = [
            'track', 'date', 'race_number', 'program_number', 'horse_name',
            'entry_distance', 'entry_surface', 'profile_distance', 'profile_time', 
            'profile_surface', 'performance_score', 'calculation_status'
        ]
        
        with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(horses_data)
        
        print(f"✅ Veriler kaydedildi: {filename}")
        return True
        
    except Exception as e:
        logger.error(f"CSV kaydetme hatası: {e}")
        return False

def print_summary(horses_data):
    """Özet istatistikleri yazdır"""
    if not horses_data:
        return
    
    total = len(horses_data)
    successful = len([h for h in horses_data if h['calculation_status'] == 'Başarılı'])
    success_rate = (successful / total * 100) if total > 0 else 0
    
    # Yarış bazında grupla
    races = {}
    for horse in horses_data:
        race_num = horse['race_number']
        if race_num not in races:
            races[race_num] = []
        races[race_num].append(horse)
    
    print(f"\n📊 ÖZET İSTATİSTİKLER:")
    print(f"   Toplam At: {total}")
    print(f"   Başarılı Hesaplama: {successful}")
    print(f"   Başarı Oranı: {success_rate:.1f}%")
    print(f"   Toplam Yarış: {len(races)}")
    
    print(f"\n🏁 YARIŞ BAZINDA:")
    for race_num in sorted(races.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        race_horses = races[race_num]
        race_successful = len([h for h in race_horses if h['calculation_status'] == 'Başarılı'])
        print(f"   Yarış {race_num}: {race_successful}/{len(race_horses)} at")

def main():
    """Ana fonksiyon"""
    
    # Hipodrom listesi
    tracks = {
        '1': 'aqueduct',
        '2': 'belmont-park', 
        '3': 'churchill-downs',
        '4': 'del-mar',
        '5': 'gulfstream-park',
        '6': 'keeneland',
        '7': 'laurel-park',
        '8': 'oaklawn-park',
        '9': 'pimlico',
        '10': 'santa-anita',
        '11': 'saratoga',
        '12': 'woodbine',
        '13': 'remington-park',
        '14': 'fair-grounds',
        '15': 'tampa-bay-downs'
    }
    
    print("🏇 Amerika At Hesaplama Terminal Uygulaması")
    print("=" * 50)
    
    # Hipodrom seçimi
    print("\n📍 Mevcut Hipodromlar:")
    for key, track in tracks.items():
        print(f"   {key}. {track.replace('-', ' ').title()}")
    
    while True:
        try:
            choice = input("\nHipodrom seçin (1-15): ").strip()
            if choice in tracks:
                selected_track = tracks[choice]
                break
            else:
                print("❌ Geçersiz seçim! 1-15 arası bir sayı girin.")
        except KeyboardInterrupt:
            print("\n👋 Çıkış yapılıyor...")
            return
    
    # Tarih seçimi
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\n📅 Tarih (varsayılan: {today}):")
    date_input = input("Tarih girin (YYYY-MM-DD) veya Enter'a basın: ").strip()
    
    if not date_input:
        selected_date = today
    else:
        try:
            # Tarih formatı kontrolü
            datetime.strptime(date_input, '%Y-%m-%d')
            selected_date = date_input
        except ValueError:
            print("❌ Geçersiz tarih formatı! Varsayılan tarih kullanılacak.")
            selected_date = today
    
    print(f"\n🎯 Seçilen: {selected_track.replace('-', ' ').title()} - {selected_date}")
    print("🔄 İşlem başlıyor...\n")
    
    # Verileri çek ve hesapla
    horses_data = process_track_data(selected_track, selected_date)
    
    if horses_data:
        # CSV dosya adı oluştur
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"american_{selected_track}_{selected_date.replace('-', '_')}_{timestamp}.csv"
        
        # CSV'ye kaydet
        if save_to_csv(horses_data, csv_filename):
            print_summary(horses_data)
            print(f"\n🎉 İşlem tamamlandı! Dosya: {csv_filename}")
        else:
            print("❌ CSV kaydetme başarısız!")
    else:
        print("❌ Veri çekilemedi veya hesaplanamadı!")

if __name__ == "__main__":
    main()