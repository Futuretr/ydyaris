#!/usr/bin/env python3
"""
Utility functions for Horse Racing Nation scraper
"""

import re
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin


def normalize_track_name(name):
    """Track adını normalize eder"""
    # Özel karakterleri kaldır ve küçük harfe çevir
    normalized = re.sub(r'[^\w\s-]', '', name.lower())
    normalized = re.sub(r'\s+', '-', normalized.strip())
    return normalized


def parse_odds(odds_str):
    """Odds string'ini parse eder"""
    if not odds_str:
        return None
    
    odds_str = odds_str.strip()
    
    # Fraction odds (5/2, 3/1)
    fraction_match = re.match(r'^(\d+)/(\d+)$', odds_str)
    if fraction_match:
        num = float(fraction_match.group(1))
        den = float(fraction_match.group(2))
        return num / den
    
    # Even money
    if odds_str.lower() in ['even', 'evens', '1/1']:
        return 1.0
    
    # Decimal format already
    try:
        return float(odds_str)
    except ValueError:
        return None


def parse_purse(purse_str):
    """Purse string'ini parse eder ve sayıya çevirir"""
    if not purse_str:
        return None
    
    # Sadece sayıları ve virgülleri al
    numbers_only = re.sub(r'[^\d,]', '', purse_str)
    numbers_only = numbers_only.replace(',', '')
    
    try:
        return int(numbers_only)
    except ValueError:
        return None


def parse_distance(distance_str):
    """Distance string'ini parse eder"""
    if not distance_str:
        return None
    
    distance_str = distance_str.strip().upper()
    
    # Furlong formatı (6F, 7F)
    furlong_match = re.match(r'^(\d+)F$', distance_str)
    if furlong_match:
        return {
            'value': int(furlong_match.group(1)),
            'unit': 'furlong',
            'yards': int(furlong_match.group(1)) * 220
        }
    
    # Mile formatı (1M, 1 1/8M)
    mile_match = re.match(r'^(\d+)(?:\s*(\d+)/(\d+))?\s*M$', distance_str)
    if mile_match:
        miles = int(mile_match.group(1))
        if mile_match.group(2) and mile_match.group(3):
            fraction = int(mile_match.group(2)) / int(mile_match.group(3))
            miles += fraction
        
        return {
            'value': miles,
            'unit': 'mile',
            'yards': int(miles * 1760)
        }
    
    # Kilometre formatı (1000m gibi)
    meter_match = re.match(r'^(\d+)m?$', distance_str)
    if meter_match:
        meters = int(meter_match.group(1))
        return {
            'value': meters,
            'unit': 'meter',
            'yards': int(meters * 1.094)
        }
    
    return {'raw': distance_str}


def format_time_to_24h(time_str):
    """12 saat formatını 24 saat formatına çevirir"""
    if not time_str:
        return None
    
    try:
        # "11:00 PM" -> "23:00"
        dt = datetime.strptime(time_str, '%I:%M %p')
        return dt.strftime('%H:%M')
    except ValueError:
        # Zaten 24 saat formatında olabilir
        if re.match(r'^\d{1,2}:\d{2}$', time_str):
            return time_str
        return None


def calculate_race_start_datetime(race_date_str, post_time_str):
    """Yarış tarih ve saatinden datetime objesi oluşturur"""
    if not race_date_str or not post_time_str:
        return None
    
    try:
        # Tarihi parse et
        date_formats = [
            '%Y-%m-%d',
            '%B %d, %Y',
            '%A, %B %d, %Y'
        ]
        
        race_date = None
        for fmt in date_formats:
            try:
                race_date = datetime.strptime(race_date_str, fmt)
                break
            except ValueError:
                continue
        
        if not race_date:
            return None
        
        # Saati parse et
        time_24h = format_time_to_24h(post_time_str)
        if not time_24h:
            return None
        
        hour, minute = map(int, time_24h.split(':'))
        
        # Gece yarısından sonraki saatler ertesi güne geçer
        if hour < 12 and 'AM' in post_time_str.upper() and hour < 6:
            race_date += timedelta(days=1)
        
        race_datetime = race_date.replace(hour=hour, minute=minute)
        return race_datetime
        
    except Exception:
        return None


def extract_jockey_trainer(trainer_jockey_str):
    """Trainer ve jockey bilgilerini ayırır"""
    if not trainer_jockey_str:
        return {'trainer': None, 'jockey': None}
    
    # Farklı formatlar olabilir:
    # "John Smith Mike Jones" (trainer jockey)
    # "John Smith / Mike Jones" 
    # "Trainer: John Smith Jockey: Mike Jones"
    
    trainer_jockey_str = trainer_jockey_str.strip()
    
    # Slash ile ayrılmış
    if '/' in trainer_jockey_str:
        parts = trainer_jockey_str.split('/')
        return {
            'trainer': parts[0].strip() if len(parts) > 0 else None,
            'jockey': parts[1].strip() if len(parts) > 1 else None
        }
    
    # Explicit labels varsa
    if 'trainer:' in trainer_jockey_str.lower():
        trainer_match = re.search(r'trainer:\s*([^jockey]+)', trainer_jockey_str, re.I)
        jockey_match = re.search(r'jockey:\s*(.+)', trainer_jockey_str, re.I)
        
        return {
            'trainer': trainer_match.group(1).strip() if trainer_match else None,
            'jockey': jockey_match.group(1).strip() if jockey_match else None
        }
    
    # Space ile ayrılmış (son iki kelime jockey, öncekiler trainer)
    words = trainer_jockey_str.split()
    if len(words) >= 3:
        # Son iki kelime jockey, geri kalanı trainer
        jockey = ' '.join(words[-2:])
        trainer = ' '.join(words[:-2])
        return {'trainer': trainer, 'jockey': jockey}
    elif len(words) == 2:
        return {'trainer': words[0], 'jockey': words[1]}
    else:
        return {'trainer': trainer_jockey_str, 'jockey': None}


def validate_url(url):
    """URL'nin geçerli olup olmadığını kontrol eder"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def get_track_slug_from_url(url):
    """URL'den track slug'ını çıkarır"""
    try:
        path = urlparse(url).path
        parts = path.strip('/').split('/')
        if len(parts) >= 2 and parts[0] == 'entries-results':
            return parts[1]
        return None
    except:
        return None


def clean_horse_name(name):
    """At ismini temizler"""
    if not name:
        return None
    
    # Başta ve sonda boşlukları kaldır
    cleaned = name.strip()
    
    # Speed figure'ı kaldır (parantez içindeki sayı)
    cleaned = re.sub(r'\s*\(\d+\)\s*', ' ', cleaned)
    
    # Fazla boşlukları kaldır
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned if cleaned else None


def format_payout(payout_str):
    """Payout string'ini düzenler"""
    if not payout_str:
        return None
    
    # Sadece $ işareti ve sayıları bırak
    cleaned = re.sub(r'[^\d.$,]', '', payout_str)
    
    if cleaned.startswith('$'):
        return cleaned
    elif cleaned:
        return f'${cleaned}'
    
    return None


def get_date_range(start_date, num_days):
    """Belirli bir tarihten itibaren N gün için tarih listesi"""
    start = datetime.strptime(start_date, '%Y-%m-%d')
    dates = []
    
    for i in range(num_days):
        date = start + timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
    
    return dates


def is_valid_date(date_str):
    """Tarih string'inin geçerli olup olmadığını kontrol eder"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    # Test utilities
    print("Testing utility functions...")
    
    # Test odds parsing
    print(f"Odds 5/2: {parse_odds('5/2')}")
    print(f"Odds Even: {parse_odds('Even')}")
    
    # Test distance parsing
    print(f"Distance 6F: {parse_distance('6F')}")
    print(f"Distance 1 1/8M: {parse_distance('1 1/8M')}")
    
    # Test time conversion
    print(f"Time 11:00 PM: {format_time_to_24h('11:00 PM')}")
    
    # Test trainer/jockey parsing
    print(f"T/J: {extract_jockey_trainer('John Smith Mike Jones')}")
    
    print("All tests completed!")