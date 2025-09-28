#!/usr/bin/env python3
"""
Çoklu pist veri çekme aracı - Tüm pistlerden yarış verilerini çeker
Multi-track racing data scraper - Scrapes race data from all tracks
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from single_track_scraper import scrape_single_track
from scrape_all_horse_profiles import read_horses_from_csv
from horse_profile_scraper import HorseProfileScraper
import requests
from bs4 import BeautifulSoup
import logging
import csv
import json

# Logging ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tüm pistlerin bilgileri
TRACKS = {
    1: {
        'name': 'Santa Anita',
        'slug': 'santa-anita',
        'description': 'Santa Anita Park, California'
    },
    2: {
        'name': 'Woodbine',
        'slug': 'woodbine', 
        'description': 'Woodbine Racetrack, Ontario'
    },
    3: {
        'name': 'Laurel Park',
        'slug': 'laurel-park',
        'description': 'Laurel Park, Maryland'
    },
    4: {
        'name': 'Belmont at Aqueduct',
        'slug': 'belmont-at-aqueduct',
        'description': 'Belmont at Aqueduct, New York'
    },
    5: {
        'name': 'Belterra Park',
        'slug': 'belterra-park',
        'description': 'Belterra Park Gaming, Ohio'
    },
    6: {
        'name': 'Churchill Downs',
        'slug': 'churchill-downs',
        'description': 'Churchill Downs, Kentucky'
    },
    7: {
        'name': 'Gulfstream Park',
        'slug': 'gulfstream-park',
        'description': 'Gulfstream Park, Florida'
    },
    8: {
        'name': 'Delaware Park',
        'slug': 'delaware-park',
        'description': 'Delaware Park, Delaware'
    },
    9: {
        'name': 'Lethbridge - Rmtc',
        'slug': 'lethbridge-rmtc',
        'description': 'Lethbridge Racing, Alberta'
    },
    10: {
        'name': 'Fairmount Park',
        'slug': 'fairmount-park',
        'description': 'Fairmount Park, Illinois'
    },
    11: {
        'name': 'Hastings Park',
        'slug': 'hastings-park',
        'description': 'Hastings Racecourse, British Columbia'
    },
    12: {
        'name': 'Charles Town',
        'slug': 'charles-town',
        'description': 'Charles Town Races, West Virginia'
    },
    13: {
        'name': 'Remington Park',
        'slug': 'remington-park',
        'description': 'Remington Park, Oklahoma'
    },
    14: {
        'name': 'Albuquerque Downs',
        'slug': 'albuquerque-downs',
        'description': 'Albuquerque Downs, New Mexico'
    },
    15: {
        'name': 'Los Alamitos',
        'slug': 'los-alamitos',
        'description': 'Los Alamitos Race Course, California'
    }
}

def show_menu():
    """Pist seçim menüsünü gösterir"""
    print("\n" + "="*60)
    print("🏇 ÇOK PİSTLİ YARIŞ VERİSİ ÇEKME ARACI")
    print("   MULTI-TRACK RACING DATA SCRAPER")
    print("="*60)
    print("\nMevcut Pistler / Available Tracks:")
    print("-" * 40)
    
    for track_id, track_info in TRACKS.items():
        print(f"{track_id:2d}. {track_info['name']:<25} - {track_info['description']}")
    
    print(f"\n{len(TRACKS)+1:2d}. Tümü (Hepsi) / All Tracks")
    print(f"{len(TRACKS)+2:2d}. Çıkış / Exit")
    print("-" * 40)

def get_date_input():
    """Kullanıcıdan tarih alır"""
    print("\nTarih seçimi / Date selection:")
    print("1. Bugün / Today")
    print("2. Dün / Yesterday (Amerika saati için)")
    print("3. Yarın / Tomorrow") 
    print("4. Özel tarih / Custom date (YYYY-MM-DD)")
    
    choice = input("\nSeçiminiz / Your choice (1-4): ").strip()
    
    if choice == "1":
        return datetime.now().strftime("%Y-%m-%d")
    elif choice == "2":
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif choice == "3":
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    elif choice == "4":
        date_str = input("Tarihi girin (YYYY-MM-DD): ").strip()
        try:
            # Tarihi doğrula
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("❌ Geçersiz tarih formatı! Varsayılan olarak bugün kullanılacak.")
            return datetime.now().strftime("%Y-%m-%d")
    else:
        print("❌ Geçersiz seçim! Varsayılan olarak bugün kullanılacak.")
        return datetime.now().strftime("%Y-%m-%d")

def scrape_track_data(track_info, date_str):
    """Tek bir pist için veri çeker"""
    print(f"\n🔄 {track_info['name']} verisi çekiliyor...")
    print(f"   Tarih: {date_str}")
    
    try:
        # Önce yarış olup olmadığını kontrol et
        if not check_if_races_exist(track_info['slug'], date_str):
            print(f"⚠️  {track_info['name']} - Bu tarihte yarış yok")
            return
        
        # Entries ve results çek
        success = scrape_single_track(track_info['slug'], date_str)
        
        if success:
            print(f"✅ {track_info['name']} - Yarış verileri başarıyla çekildi")
            
            # At profil verilerini çek
            entries_file = f"{track_info['slug']}_{date_str.replace('-', '_')}_{track_info['slug']}_entries.csv"
            if os.path.exists(entries_file):
                print(f"🐎 At profil verileri çekiliyor...")
                scrape_horse_profiles_for_track(entries_file)
            else:
                print(f"⚠️  Entries dosyası bulunamadı: {entries_file}")
        else:
            print(f"❌ {track_info['name']} - Veri çekilemedi")
            
    except Exception as e:
        logger.error(f"Error scraping {track_info['name']}: {e}")
        print(f"❌ {track_info['name']} - Hata: {str(e)}")

def check_if_races_exist(track_slug, date_str):
    """Belirli bir pistte belirli bir tarihte yarış olup olmadığını kontrol et"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # İlk entries sayfasını dene (daha güvenilir)
        entries_url = f"https://entries.horseracingnation.com/entries-results/{track_slug}/{date_str}"
        
        try:
            response = session.get(entries_url, timeout=15)
            if response.status_code == 200:
                # Entries sayfası title'da tarih ve pist adı varsa yarış vardır
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('title')
                if title and track_slug.replace('-', ' ').title() in title.get_text():
                    logger.info(f"Found races at entries page: {entries_url}")
                    return True
        except:
            pass
        
        # Eğer entries sayfası çalışmazsa normal track sayfasını dene
        track_url = f"https://www.horseracingnation.com/tracks/{track_slug}/{date_str}"
        response = session.get(track_url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            race_cards = soup.find_all('div', class_='race-card') or soup.find_all('section', class_='race')
            return len(race_cards) > 0
        
        return False
        
    except Exception as e:
        logger.warning(f"Error checking races for {track_slug}: {e}")
        return True  # Hata durumunda çekmeyi dene

def scrape_horse_profiles_for_track(entries_file):
    """Belirli bir pist için essential at profil verilerini çeker"""
    try:
        # Çıktı dosya adlarını hazırla
        base_name = entries_file.replace('_entries.csv', '')
        output_csv = f"{base_name}_essential.csv"
        output_json = f"{base_name}_essential.json"
        
        print(f"   📝 Essential çıktı: {output_csv}")
        
        # At profil scraper'ı başlat
        scraper = HorseProfileScraper()
        
        results = []
        successful = 0
        failed = 0
        
        # CSV dosyasını okuyup işle
        with open(entries_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            horses = list(reader)
        
        total_horses = len(horses)
        print(f"   🏇 {total_horses} at bulundu, essential veriler çekiliyor...")
        
        for i, row in enumerate(horses, 1):
            horse_name = row.get('horse_name', '').strip()
            race_number = row.get('race_number', '').strip()
            program_number = row.get('program_number', '').strip()
            
            if not horse_name:
                print(f"   [{i:3d}/{total_horses}] ⚠️ Boş at ismi atlanıyor")
                continue
                
            print(f"   [{i:3d}/{total_horses}] {horse_name[:20]:<20}", end=" ... ")
            
            try:
                # At profil verisini çek
                horse_data = scraper.scrape_horse_profile(horse_name)
                
                if horse_data and horse_data.get('race_history') and len(horse_data['race_history']) > 0:
                    # En son yarış verilerini al
                    latest_race = horse_data['race_history'][0]  # İlk eleman en son yarış
                    
                    # Sonucu hazırla
                    result = {
                        'race_number': race_number,
                        'program_number': program_number,
                        'horse_name': horse_name,
                        'latest_surface': latest_race.get('surface', ''),
                        'latest_distance': latest_race.get('distance', ''),
                        'latest_time': latest_race.get('time', '')
                    }
                    
                    results.append(result)
                    successful += 1
                    print("✅")
                    
                else:
                    failed += 1
                    print("❌")
                    
                    # Başarısız durumda da temel bilgileri ekle
                    result = {
                        'race_number': race_number,
                        'program_number': program_number,
                        'horse_name': horse_name,
                        'latest_surface': '',
                        'latest_distance': '',
                        'latest_time': ''
                    }
                    results.append(result)
                    
            except Exception as e:
                failed += 1
                print(f"❌")
                
                # Hata durumunda da temel bilgileri ekle
                result = {
                    'race_number': race_number,
                    'program_number': program_number,
                    'horse_name': horse_name,
                    'latest_surface': '',
                    'latest_distance': '',
                    'latest_time': ''
                }
                results.append(result)
        
        print(f"   📊 Sonuç: ✅{successful} / ❌{failed} / 📋{len(results)}")
        
        if results:
            # CSV dosyasına kaydet
            fieldnames = [
                'race_number',
                'program_number', 
                'horse_name',
                'latest_surface',
                'latest_distance',
                'latest_time'
            ]
            
            with open(output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            
            # JSON dosyasına kaydet
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            # Başarılı örnekleri göster
            successful_examples = [r for r in results if r['latest_time']]
            if successful_examples:
                print(f"   🎯 {len(successful_examples)}/{len(results)} kayıtta tam veri mevcut")
                
                # İlk 2 örneği göster
                for i, result in enumerate(successful_examples[:2], 1):
                    print(f"      {i}. {result['horse_name']}: "
                          f"{result['latest_surface']}, "
                          f"{result['latest_distance']}, "
                          f"{result['latest_time']}")
            
            print(f"   💾 Essential veriler kaydedildi: {output_csv}")
            
        return successful
        
        # Sonuçları kaydet
        output_csv = entries_file.replace('_entries.csv', '_entries_horse_profiles.csv')
        scraper.save_profiles_to_csv(output_csv, horses_data)
        
        print(f"   ✅ {successful_scrapes}/{len(horse_names)} at profili başarıyla çekildi")
        print(f"   💾 Sonuçlar kaydedildi: {output_csv}")
        
    except Exception as e:
        logger.error(f"Error processing horse profiles: {e}")
        print(f"   ❌ At profilleri çekilirken hata: {str(e)}")

def scrape_all_tracks(date_str):
    """Tüm pistlerin verilerini çeker"""
    print(f"\n🚀 TÜM PİSTLERİN VERİSİ ÇEKİLİYOR - {date_str}")
    print("="*50)
    
    total_tracks = len(TRACKS)
    successful_tracks = 0
    
    for track_id, track_info in TRACKS.items():
        print(f"\n📍 {track_id}/{total_tracks}: {track_info['name']}")
        scrape_track_data(track_info, date_str)
        successful_tracks += 1
    
    print(f"\n🎯 ÖZET / SUMMARY:")
    print(f"   İşlenen pistler / Processed tracks: {successful_tracks}/{total_tracks}")
    print("   Tüm veriler ilgili CSV dosyalarına kaydedildi")

def main():
    """Ana program döngüsü"""
    while True:
        try:
            show_menu()
            choice = input("\nSeçiminiz / Your choice: ").strip()
            
            if not choice.isdigit():
                print("❌ Lütfen bir sayı girin!")
                continue
                
            choice = int(choice)
            
            # Çıkış
            if choice == len(TRACKS) + 2:
                print("\n👋 Programdan çıkılıyor...")
                break
            
            # Tarih seç
            date_str = get_date_input()
            
            # Tüm pistler
            if choice == len(TRACKS) + 1:
                scrape_all_tracks(date_str)
            
            # Tek pist
            elif choice in TRACKS:
                track_info = TRACKS[choice]
                print(f"\n🎯 Seçilen pist: {track_info['name']}")
                scrape_track_data(track_info, date_str)
            
            else:
                print("❌ Geçersiz seçim! Lütfen menüdeki numaralardan birini seçin.")
                continue
            
            # Devam etmek istiyor mu?
            print("\n" + "-"*50)
            continue_choice = input("Başka bir işlem yapmak istiyor musunuz? (y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes', 'e', 'evet']:
                print("\n👋 Program sonlandırılıyor...")
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Program kullanıcı tarafından sonlandırıldı...")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"\n❌ Beklenmeyen hata: {str(e)}")
            print("Program devam ediyor...")

if __name__ == "__main__":
    main()