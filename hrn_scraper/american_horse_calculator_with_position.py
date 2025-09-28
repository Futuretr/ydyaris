#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AMERICAN HORSE CALCULATOR WITH FINISH POSITION
*** DEPRECATED - TURKISH STYLE KULLANIN! ***
Bu dosya artık kullanılmıyor.
Bunun yerine american_horse_calculator_turkish_style.py kullanın.
Turkish Style daha gelişmiş position penalty sistemi içerir.
"""

import pandas as pd
import time
import os
import json
import re
import math
from datetime import datetime

def time_to_seconds(time_str):
    """Convert time string to seconds for American format"""
    if (not time_str or 
        str(time_str).strip() in ['', '-', '0', 'nan'] or
        (isinstance(time_str, float) and math.isnan(time_str))):
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
        except:
            pass
    
    # Simple decimal format: 85.61 (total seconds)
    try:
        return float(time_str)
    except:
        pass
    
    return 0

def distance_to_meters(distance_str):
    """Convert distance string to meters"""
    if (not distance_str or 
        str(distance_str).strip() in ['', '-', '0', 'nan'] or
        (isinstance(distance_str, float) and math.isnan(distance_str))):
        return 0
    
    distance_str = str(distance_str).strip()
    
    # American formats
    # 1M 70Y = 1 mile + 70 yards
    # 6F = 6 furlongs
    # 1200Y = 1200 yards
    
    total_meters = 0
    
    # Mile + yards format (e.g., "1M 70Y")
    mile_yard_match = re.match(r'(\d+)M\s*(\d+)Y', distance_str)
    if mile_yard_match:
        miles = int(mile_yard_match.group(1))
        yards = int(mile_yard_match.group(2))
        total_meters = miles * 1609.34 + yards * 0.9144
        return int(total_meters)
    
    # Just miles (e.g., "1M")
    mile_match = re.match(r'(\d+)M$', distance_str)
    if mile_match:
        miles = int(mile_match.group(1))
        return int(miles * 1609.34)
    
    # Furlongs (e.g., "6F" or "5 f")
    furlong_match = re.match(r'(\d+)\s*[Ff]$', distance_str)
    if furlong_match:
        furlongs = int(furlong_match.group(1))
        return int(furlongs * 201.168)  # 1 furlong = 201.168 meters
    
    # Yards (e.g., "1200Y")
    yard_match = re.match(r'(\d+)Y$', distance_str)
    if yard_match:
        yards = int(yard_match.group(1))
        return int(yards * 0.9144)
    
    # Try to extract just numbers (assuming meters)
    number_match = re.search(r'\d+', distance_str)
    if number_match:
        return int(number_match.group())
    
    return 0

def calculate_performance_score_with_position(horse):
    """Calculate performance score using finish position"""
    try:
        # Temel bilgileri al
        profile_distance = horse.get('profile_distance', '')
        profile_time = horse.get('profile_time', '')
        profile_surface = horse.get('profile_surface', '')
        latest_finish_position = horse.get('latest_finish_position', '')
        
        # Finish position kontrolü
        if (not latest_finish_position or 
            str(latest_finish_position).strip() in ['', '-', '0', 'nan'] or
            (isinstance(latest_finish_position, float) and math.isnan(latest_finish_position))):
            return None, "No finish position"
        
        try:
            # Float olarak geliyorsa önce float'a sonra int'e çevir
            finish_pos_float = float(str(latest_finish_position).strip())
            if math.isnan(finish_pos_float):
                return None, "No finish position"
            finish_pos = int(finish_pos_float)
        except:
            return None, "Invalid finish position"
        
        # Mesafe kontrolü
        distance_meters = distance_to_meters(profile_distance)
        if distance_meters == 0:
            return None, "Invalid distance"
        
        # Zaman kontrolü
        time_seconds = time_to_seconds(profile_time)
        if time_seconds == 0:
            return None, "Invalid time"
        
        # Mesafe bazlı derece farkı hesabı
        # Her 100 metrede 1. ile 2. arasında 0.10s fark
        # Formül: (derece-1) * (mesafe/100) * 0.10
        if finish_pos == 1:
            # Kazanan at - temel zaman
            penalty = 0
        else:
            # Kazanan olmayan at - mesafe bazlı ek süre
            # Her 100m için her derece 0.10s ek
            distance_factor = distance_meters / 100.0  # 100m birimleri
            penalty = (finish_pos - 1) * distance_factor * 0.10
        
        # Final score = orijinal zaman + penalty (düşük = iyi)
        # Ancak 10'la bölerek daha makul değerler elde edelim
        final_score = (time_seconds + penalty) / 10.0
        
        return final_score, "Success"
        
    except Exception as e:
        return None, f"Calculation error: {str(e)}"

def load_horses_from_csv(csv_file):
    """Load horses from CSV file"""
    try:
        df = pd.read_csv(csv_file)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ CSV yükleme hatası: {e}")
        return None

def process_horses_data(horses_list):
    """Process list of horses and calculate performance scores using finish position"""
    results = []
    
    for horse in horses_list:
        horse_name = horse.get('horse_name', '')
        track = horse.get('track', '')
        date = horse.get('date', '')
        race_number = horse.get('race_number', '')
        program_number = horse.get('program_number', '')
        
        # Calculate performance score with finish position
        score, status = calculate_performance_score_with_position(horse)
        
        result = {
            'track': track,
            'date': date,
            'race_number': race_number,
            'program_number': program_number,
            'horse_name': horse_name,
            'entry_distance': horse.get('entry_distance', ''),
            'entry_surface': horse.get('entry_surface', ''),
            'profile_distance': horse.get('profile_distance', ''),
            'profile_time': horse.get('profile_time', ''),
            'profile_surface': horse.get('profile_surface', ''),
            'latest_finish_position': horse.get('latest_finish_position', ''),
            'performance_score': score if score is not None else 'Invalid',
            'calculation_status': status
        }
        
        results.append(result)
    
    return results

def group_by_race_and_sort(results):
    """Group results by race and sort by performance score"""
    # Group by track, date, and race number
    grouped = {}
    
    for result in results:
        key = f"{result['track']}_{result['date']}_R{result['race_number']}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(result)
    
    # Sort each group by performance score (lower is better)
    for key in grouped:
        # Separate valid and invalid scores
        valid_horses = [h for h in grouped[key] if h['performance_score'] != 'Invalid']
        invalid_horses = [h for h in grouped[key] if h['performance_score'] == 'Invalid']
        
        # Sort valid horses by performance score (ascending - lower time is better)
        valid_horses.sort(key=lambda x: float(x['performance_score']))
        
        # Combine: valid horses first, then invalid
        grouped[key] = valid_horses + invalid_horses
    
    return grouped

def save_results_to_csv(results, filename_prefix="american_horses_with_position"):
    """Save calculation results to CSV file"""
    if not results:
        print("❌ Kaydedilecek sonuç yok")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{filename_prefix}_{timestamp}.csv"
    
    try:
        df = pd.DataFrame(results)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✅ Sonuçlar kaydedildi: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Dosya kaydetme hatası: {e}")
        return None

def main():
    """Test fonksiyonu - DEPRECATED"""
    print("*** DEPRECATED CALCULATOR - USE TURKISH STYLE INSTEAD! ***")
    print("==========================================================")
    print("Bu calculator artık kullanılmıyor!")
    print("Bunun yerine american_horse_calculator_turkish_style.py kullanın.")
    
    choice = input("Yine de test etmek istiyor musunuz? (y/N): ").strip().lower()
    if choice != 'y':
        print("İptal edildi. Turkish Style calculator'ı kullanın!")
        return
    
    print("\n⚠️  WARNING: Deprecated calculator test başlıyor!")
    print("American Horse Calculator with Finish Position Test - DEPRECATED")
    
    # Örnek test verisi - farklı mesafeler
    test_horses = [
        {
            'horse_name': 'Test Horse 1 (6F-1st)',
            'track': 'Test Track',
            'date': '2025-01-01',
            'race_number': '1',
            'program_number': '1',
            'profile_distance': '6F',  # 6F = 1206m
            'profile_time': '1:12.50',
            'profile_surface': 'D',
            'latest_finish_position': '1'
        },
        {
            'horse_name': 'Test Horse 2 (6F-3rd)',
            'track': 'Test Track',
            'date': '2025-01-01',
            'race_number': '1',
            'program_number': '2',
            'profile_distance': '6F',  # 6F = 1206m
            'profile_time': '1:12.50',
            'profile_surface': 'D',
            'latest_finish_position': '3'
        },
        {
            'horse_name': 'Test Horse 3 (1200Y-1st)',
            'track': 'Test Track',
            'date': '2025-01-01',
            'race_number': '2',
            'program_number': '1',
            'profile_distance': '1200Y',  # 1200Y = 1097m
            'profile_time': '1:10.00',
            'profile_surface': 'D',
            'latest_finish_position': '1'
        },
        {
            'horse_name': 'Test Horse 4 (1200Y-2nd)',
            'track': 'Test Track',
            'date': '2025-01-01',
            'race_number': '2',
            'program_number': '2',
            'profile_distance': '1200Y',  # 1200Y = 1097m
            'profile_time': '1:10.00',
            'profile_surface': 'D',
            'latest_finish_position': '2'
        }
    ]
    
    results = process_horses_data(test_horses)
    
    for result in results:
        print(f"At: {result['horse_name']}")
        print(f"Mesafe: {result['profile_distance']}")
        print(f"Zaman: {result['profile_time']}")
        print(f"Derece: {result['latest_finish_position']}")
        print(f"Skor: {result['performance_score']}")
        print(f"Durum: {result['calculation_status']}")
        print("-" * 50)

if __name__ == "__main__":
    main()