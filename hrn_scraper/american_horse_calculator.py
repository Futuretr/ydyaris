from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
import pandas as pd
import math
import sys
import logging
import csv

# Mevcut scraper'ları import et
from single_track_scraper import scrape_single_track
from horse_profile_scraper import HorseProfileScraper

app = Flask(__name__)

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Turkish style calculator'ı import et - ZORUNLU!
try:
    from american_horse_calculator_turkish_style import (
        calculate_american_horse_performance_turkish_style,
        process_horses_data_turkish_style,
        group_by_race_and_sort
    )
    TURKISH_STYLE_AVAILABLE = True
    calculate_american_horse_performance_turkish_style_func = calculate_american_horse_performance_turkish_style
    logger.info("Turkish style calculator loaded successfully - ONLY Turkish Style will be used!")
except ImportError as e:
    TURKISH_STYLE_AVAILABLE = False
    calculate_american_horse_performance_turkish_style_func = None
    logger.error(f"CRITICAL: Turkish style calculator not available: {e}")
    raise ImportError("Turkish Style Calculator is REQUIRED! Cannot proceed without it.")

def clean_json_data(obj):
    """JSON serialize edilebilir hale getir - NaN ve None değerlerini temizle"""
    if isinstance(obj, dict):
        return {k: clean_json_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_json_data(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif obj is None:
        return None
    else:
        return obj

def time_to_seconds(time_str):
    """Convert American time string to seconds - Enhanced"""
    if not time_str or str(time_str).strip() in ['', '-', '0', 'nan']:
        return 0
    
    time_str = str(time_str).strip()
    
    # American format: 1:25.61 (minutes:seconds.hundredths)
    if ':' in time_str:
        try:
            parts = time_str.split(':')
            if len(parts) == 2:
                minutes = int(parts[0])
                # Handle seconds with decimal
                seconds_part = parts[1]
                if '.' in seconds_part:
                    seconds = float(seconds_part)
                else:
                    seconds = int(seconds_part)
                return minutes * 60 + seconds
        except Exception:
            pass
    
    # Simple decimal format: 85.61 (total seconds)
    try:
        return float(time_str)
    except Exception:
        pass
    
    return 0

def calculate_time_per_100m(total_seconds, distance_meters):
    """100m başına süre hesapla"""
    try:
        if total_seconds <= 0 or distance_meters <= 0:
            return 0
        return total_seconds / (distance_meters / 100)
    except Exception:
        return 0

def calculate_surface_adaptation(previous_surface, current_surface):
    """Zemin adaptasyon faktörü hesapla"""
    # Amerika zemin tipleri: Dirt, Turf, Synthetic
    surface_factors = {
        ('Dirt', 'Dirt'): 1.0,
        ('Dirt', 'Turf'): 1.05,    # Dirt'ten Turf'e geçiş
        ('Dirt', 'Synthetic'): 1.02,
        ('Turf', 'Dirt'): 0.98,     # Turf'ten Dirt'e geçiş
        ('Turf', 'Turf'): 1.0,
        ('Turf', 'Synthetic'): 1.01,
        ('Synthetic', 'Dirt'): 0.99,
        ('Synthetic', 'Turf'): 1.03,
        ('Synthetic', 'Synthetic'): 1.0
    }
    
    # Varsayılan adaptasyon faktörü
    return surface_factors.get((previous_surface, current_surface), 1.0)

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
            
    except Exception:
        return 1200

def calculate_position_penalty_american(finish_position, base_time_per_100m, distance_meters):
    """
    Calculate position penalty for American horses - Turkish style
    """
    try:
        if not finish_position or str(finish_position).strip() in ['', 'nan', '0']:
            return base_time_per_100m
        
        pos = int(float(str(finish_position).strip()))
        if pos <= 1:
            return base_time_per_100m  # Winner, no penalty
        
        # Turkish system penalty: each position adds 0.10s per race
        position_penalty_per_race = (pos - 1) * 0.10
        
        # Convert to per 100m penalty
        segments_100m = distance_meters / 100.0
        penalty_per_100m = position_penalty_per_race / segments_100m
        
        return base_time_per_100m + penalty_per_100m
        
    except Exception:
        return base_time_per_100m

def calculate_american_horse_performance(horse_data, race_data):
    """Amerika atı için performans hesapla - SADECE Turkish Style kullanılır"""
    # Turkish Style calculator'ı kullan - ZORUNLU!
    if TURKISH_STYLE_AVAILABLE and calculate_american_horse_performance_turkish_style_func:
        try:
            logger.debug(f"Using Turkish Style for: {horse_data.get('horse_name', 'Unknown')}")
            return calculate_american_horse_performance_turkish_style_func(horse_data, race_data)
        except Exception as e:
            logger.error(f"Turkish Style hesaplama hatası: {e}")
            return None
    else:
        logger.error("CRITICAL: Turkish Style calculator mevcut değil - sistem çalışamaz!")
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

def load_horse_profiles_from_json(json_file):
    """JSON dosyasından at profil verilerini yükle"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"JSON okuma hatası: {e}")
        return []

def process_american_race_data(track_slug, race_date):
    """Amerika yarış verilerini işle ve hesapla"""
    try:
        logger.info(f"İşleniyor: {track_slug} - {race_date}")
        
        # İlk önce yarış verilerini çek (entries CSV)
        success = scrape_single_track(track_slug, race_date)
        
        if not success:
            return None, "Yarış verileri çekilemedi"
        
        # CSV dosyasını bul
        entries_csv = f"{track_slug}_{race_date.replace('-', '_')}_{track_slug}_entries.csv"
        essential_json = f"{track_slug}_{race_date.replace('-', '_')}_{track_slug}_essential.json"
        
        if not os.path.exists(entries_csv):
            return None, f"Entries dosyası bulunamadı: {entries_csv}"
        
        # At entries verilerini yükle
        entries_data = load_horse_data_from_csv(entries_csv)
        
        if not entries_data:
            return None, "At verileri yüklenemedi"
        
        # Eğer essential JSON varsa, at profil verilerini yükle
        profile_data = []
        if os.path.exists(essential_json):
            profile_data = load_horse_profiles_from_json(essential_json)
        else:
            # Profil verilerini çek
            logger.info("At profil verileri çekiliyor...")
            scraper = HorseProfileScraper()
            
            for entry in entries_data:
                horse_name = entry.get('horse_name', '')
                if horse_name:
                    try:
                        profile = scraper.scrape_horse_profile(horse_name)
                        if profile and profile.get('race_history'):
                            # En son yarışı al
                            latest_race = profile['race_history'][0]
                            profile_data.append({
                                'horse_name': horse_name,
                                'race_number': entry.get('race_number', '1'),
                                'program_number': entry.get('program_number', ''),
                                'surface': latest_race.get('surface', ''),
                                'distance': latest_race.get('distance', ''),
                                'time': latest_race.get('time', ''),
                                'date': latest_race.get('date', '')
                            })
                    except Exception as e:
                        logger.warning(f"Profil çekme hatası {horse_name}: {e}")
                        continue
            
            # JSON'a kaydet
            with open(essential_json, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
        
        # Yarışları grupla
        races = {}
        for entry in entries_data:
            race_num = str(entry.get('race_number', '1'))
            if race_num not in races:
                races[race_num] = {
                    'race_info': {
                        'number': race_num,
                        'surface': entry.get('surface', 'Dirt'),
                        'distance': entry.get('distance', '6f'),
                        'track': track_slug,
                        'date': race_date
                    },
                    'horses': []
                }
        
        # TURKISH STYLE kullanarak at verilerini işle ve hesapla
        logger.info("TURKISH STYLE CALCULATION STARTED - Diğer yöntemler devre dışı!")
        
        # Turkish Style için veri formatını hazırla
        turkish_style_horses = []
        for entry in entries_data:
            horse_name = entry.get('horse_name', '')
            race_number = str(entry.get('race_number', '1'))
            
            # Bu atın profil verilerini bul
            horse_profile = next((p for p in profile_data if p['horse_name'] == horse_name), {})
            
            # Turkish Style format'ına uygun data structure oluştur
            turkish_horse_data = {
                'horse_name': horse_name,
                'track': track_slug,
                'date': race_date,
                'race_number': race_number,
                'program_number': entry.get('program_number', ''),
                'entry_distance': entry.get('distance', ''),
                'entry_surface': entry.get('surface', ''),
                'profile_distance': horse_profile.get('distance', ''),
                'profile_time': horse_profile.get('time', ''),
                'profile_surface': horse_profile.get('surface', ''),
                'latest_finish_position': horse_profile.get('finish_position', '')  # Eğer varsa
            }
            turkish_style_horses.append(turkish_horse_data)
        
        # Turkish Style ile hesaplama yap
        if TURKISH_STYLE_AVAILABLE:
            turkish_results = process_horses_data_turkish_style(turkish_style_horses)
            logger.info(f"Turkish Style hesaplama tamamlandı: {len(turkish_results)} at işlendi")
        else:
            logger.error("CRITICAL: Turkish Style mevcut değil!")
            return None, "Turkish Style calculator gerekli ama mevcut değil"
        
        # Sonuçları eski format'a dönüştür (backward compatibility için)
        calculated_horses = []
        for result in turkish_results:
            horse_data = {
                'horse_name': result['horse_name'],
                'race_number': result['race_number'],
                'program_number': result['program_number'],
                'surface': result['profile_surface'],
                'distance': result['profile_distance'],
                'time': result['profile_time'],
                'performance_score': result['performance_score'] if result['performance_score'] != 'Invalid' else None,
                'raw_score': result.get('calculation_details', {}).get('raw_time_per_100m') if result.get('calculation_details') else None,
                'surface_factor': result.get('calculation_details', {}).get('surface_factor') if result.get('calculation_details') else None,
                'distance_factor': result.get('calculation_details', {}).get('distance_factor') if result.get('calculation_details') else None,
                'finish_position': result.get('latest_finish_position', ''),
                'position_penalty_applied': result.get('calculation_details', {}).get('position_penalty_applied') if result.get('calculation_details') else False,
                'track': track_slug,
                'date': race_date,
                'valid_calculation': result['performance_score'] != 'Invalid'
            }
            
            calculated_horses.append(horse_data)
            
            # Yarış grubuna ekle
            race_number = result['race_number']
            if race_number in races:
                races[race_number]['horses'].append(horse_data)
        
        return races, calculated_horses
        
    except Exception as e:
        logger.error(f"Veri işleme hatası: {e}")
        return None, str(e)

# Amerika hipodromları
AMERICAN_TRACKS = {
    'aqueduct': 'Aqueduct',
    'belmont-park': 'Belmont Park',
    'churchill-downs': 'Churchill Downs',
    'del-mar': 'Del Mar',
    'gulfstream-park': 'Gulfstream Park',
    'keeneland': 'Keeneland',
    'laurel-park': 'Laurel Park',
    'oaklawn-park': 'Oaklawn Park',
    'pimlico': 'Pimlico',
    'santa-anita': 'Santa Anita',
    'saratoga': 'Saratoga',
    'woodbine': 'Woodbine',
    'remington-park': 'Remington Park',
    'fair-grounds': 'Fair Grounds',
    'tampa-bay-downs': 'Tampa Bay Downs'
}

@app.route('/')
def index():
    """Ana sayfa"""
    return render_template('american_index.html')

@app.route('/api/get_tracks', methods=['GET'])
def get_tracks():
    """Mevcut hipodromları getir"""
    try:
        return jsonify({
            'status': 'success',
            'tracks': AMERICAN_TRACKS
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Hata: {str(e)}'
        }), 500

@app.route('/api/scrape_track', methods=['POST'])
def scrape_american_track():
    """Tek hipodrom için at verilerini çek ve hesapla"""
    try:
        data = request.get_json()
        track = data.get('track', '').lower()
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        if track not in AMERICAN_TRACKS:
            return jsonify({
                'status': 'error',
                'message': f'Desteklenmeyen hipodrom: {track}'
            }), 400
        
        track_name = AMERICAN_TRACKS[track]
        
        logger.info(f"[AMERICAN] {track_name} at verileri çekiliyor - {date}")
        
        # Veriyi işle ve hesapla
        races_data, calculated_horses = process_american_race_data(track, date)
        
        if not races_data:
            return jsonify({
                'status': 'error',
                'message': f'{track_name} için veri çekilemedi'
            }), 500
        
        # CSV dosyası oluştur
        if calculated_horses:
            df = pd.DataFrame(calculated_horses)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"american_{track}_{date}_{timestamp}.csv"
            filepath = os.path.join('static', 'downloads', filename)
            
            # Downloads klasörü yoksa oluştur
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            # İstatistikler
            total_horses = len(calculated_horses)
            valid_calculations = sum(1 for h in calculated_horses if h['valid_calculation'])
            success_rate = (valid_calculations / total_horses * 100) if total_horses else 0
            
            # JSON formatına çevir
            races_list = []
            for race_num in sorted(races_data.keys(), key=lambda x: int(x) if x.isdigit() else 0):
                race = races_data[race_num]
                horses_with_scores = []
                
                for horse in race['horses']:
                    horse_info = {
                        'horse_name': horse['horse_name'],
                        'program_number': horse['program_number'],
                        'performance_score': horse['performance_score'],
                        'surface': horse['surface'],
                        'distance': horse['distance'],
                        'time': horse['time'],
                        'valid_calculation': horse['valid_calculation']
                    }
                    horses_with_scores.append(horse_info)
                
                races_list.append({
                    'race_number': race_num,
                    'race_info': race['race_info'],
                    'horses': horses_with_scores
                })
            
            response_data = {
                'status': 'success',
                'message': f'{track_name} verileri başarıyla çekildi ve hesaplandı!',
                'data': {
                    'track': track_name,
                    'date': date,
                    'total_horses': total_horses,
                    'valid_calculations': valid_calculations,
                    'success_rate': round(success_rate, 1),
                    'races': races_list,
                    'download_url': f'/download/{filename}',
                    'filename': filename
                }
            }
            
            return jsonify(clean_json_data(response_data))
        
        else:
            return jsonify({
                'status': 'error',
                'message': f'{track_name} için hesaplanabilir veri bulunamadı'
            }), 500
            
    except Exception as e:
        logger.error(f"Scraping hatası: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Hata: {str(e)}'
        }), 500

@app.route('/api/scrape_multiple_tracks', methods=['POST'])
def scrape_multiple_tracks():
    """Birden fazla hipodrom için veri çek"""
    try:
        data = request.get_json()
        tracks = data.get('tracks', [])
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        if not tracks:
            return jsonify({
                'status': 'error',
                'message': 'Hipodrom seçilmedi'
            }), 400
        
        all_results = {}
        all_horses = []
        total_success = 0
        total_horses = 0
        
        for track in tracks:
            if track not in AMERICAN_TRACKS:
                continue
                
            logger.info(f"[MULTI] İşleniyor: {AMERICAN_TRACKS[track]}")
            
            try:
                races_data, calculated_horses = process_american_race_data(track, date)
                
                if races_data and calculated_horses:
                    all_results[track] = {
                        'track_name': AMERICAN_TRACKS[track],
                        'races': races_data,
                        'horses_count': len(calculated_horses),
                        'valid_count': sum(1 for h in calculated_horses if h['valid_calculation'])
                    }
                    
                    all_horses.extend(calculated_horses)
                    total_horses += len(calculated_horses)
                    total_success += sum(1 for h in calculated_horses if h['valid_calculation'])
                    
            except Exception as track_error:
                logger.error(f"[MULTI] {track} hatası: {track_error}")
                continue
        
        if all_horses:
            # Birleşik CSV dosyası oluştur
            df = pd.DataFrame(all_horses)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"american_multiple_tracks_{date}_{timestamp}.csv"
            filepath = os.path.join('static', 'downloads', filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            success_rate = (total_success / total_horses * 100) if total_horses else 0
            
            return jsonify({
                'status': 'success',
                'message': f'{len(all_results)} hipodrom başarıyla işlendi!',
                'data': {
                    'date': date,
                    'processed_tracks': len(all_results),
                    'total_horses': total_horses,
                    'valid_calculations': total_success,
                    'success_rate': round(success_rate, 1),
                    'track_results': all_results,
                    'download_url': f'/download/{filename}',
                    'filename': filename
                }
            })
        
        else:
            return jsonify({
                'status': 'error',
                'message': 'Hiçbir hipodromdan veri çekilemedi'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Hata: {str(e)}'
        }), 500

@app.route('/api/check_saved_data', methods=['POST'])
def check_saved_american_data():
    """Kaydedilmiş Amerika verisi var mı kontrol et"""
    try:
        data = request.get_json()
        track = data.get('track', '').lower()
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        if track not in AMERICAN_TRACKS:
            return jsonify({
                'status': 'error',
                'message': f'Desteklenmeyen hipodrom: {track}'
            }), 400
        
        track_name = AMERICAN_TRACKS[track]
        
        # Bugünkü tarih için dosya adı oluştur
        saved_filename = f"american_{track}_{date}.json"
        saved_filepath = os.path.join('data', 'american', saved_filename)
        
        if os.path.exists(saved_filepath):
            with open(saved_filepath, 'r', encoding='utf-8') as f:
                horses_data = json.load(f)
            
            return jsonify({
                'status': 'success',
                'has_data': True,
                'message': f'{track_name} için {date} tarihli veriler mevcut!',
                'data': {
                    'track': track_name,
                    'date': date,
                    'total_horses': len(horses_data),
                    'filename': saved_filename
                }
            })
        else:
            return jsonify({
                'status': 'success',
                'has_data': False,
                'message': f'{track_name} için {date} tarihli veri henüz çekilmemiş',
                'data': {
                    'track': track_name,
                    'date': date
                }
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Hata: {str(e)}'
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    """CSV dosyasını indir"""
    try:
        filepath = os.path.join('static', 'downloads', filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'Dosya bulunamadı'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_performance_analysis', methods=['POST'])
def get_performance_analysis():
    """Detaylu performans analizi"""
    try:
        data = request.get_json()
        track = data.get('track', '')
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Veri analizi yap
        races_data, calculated_horses = process_american_race_data(track, date)
        
        if not calculated_horses:
            return jsonify({
                'status': 'error',
                'message': 'Analiz için veri bulunamadı'
            }), 404
        
        # Performans istatistikleri
        valid_horses = [h for h in calculated_horses if h['valid_calculation']]
        
        if not valid_horses:
            return jsonify({
                'status': 'error',
                'message': 'Geçerli performans verisi bulunamadı'
            }), 404
        
        scores = [h['performance_score'] for h in valid_horses if h['performance_score']]
        
        analysis = {
            'total_horses': len(calculated_horses),
            'valid_calculations': len(valid_horses),
            'average_score': sum(scores) / len(scores) if scores else 0,
            'min_score': min(scores) if scores else 0,
            'max_score': max(scores) if scores else 0,
            'score_distribution': {
                'excellent': len([s for s in scores if s < 6.0]),
                'good': len([s for s in scores if 6.0 <= s < 7.0]),
                'average': len([s for s in scores if 7.0 <= s < 8.0]),
                'below_average': len([s for s in scores if s >= 8.0])
            }
        }
        
        return jsonify({
            'status': 'success',
            'analysis': analysis,
            'top_performers': sorted(valid_horses, key=lambda x: x['performance_score'] or 999)[:10]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Analiz hatası: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Gerekli klasörleri oluştur
    os.makedirs('data/american', exist_ok=True)
    os.makedirs('static/downloads', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5001)  # Farklı port kullan