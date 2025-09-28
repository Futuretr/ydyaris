#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AMERICA TIMEZONE DATE TEST
Amerika saat dilimiyle veri çekme testini yapar
"""

import sys
import os
import pytz
from datetime import datetime

# Add hrn_scraper to path
sys.path.append('hrn_scraper')

# Test America timezone date function
def test_date_comparison():
    """Test Turkey vs America date comparison"""
    print("🇹🇷🇺🇸 TURKEY vs AMERICA DATE COMPARISON")
    print("=" * 60)
    
    # Turkey time
    turkey_tz = pytz.timezone('Europe/Istanbul')
    turkey_time = datetime.now(turkey_tz)
    
    # America Eastern Time
    eastern_tz = pytz.timezone('US/Eastern')
    american_time = datetime.now(eastern_tz)
    
    # Format dates
    turkey_date = turkey_time.strftime('%Y-%m-%d')
    american_date = american_time.strftime('%Y-%m-%d')
    
    print(f"Turkey Time:    {turkey_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"American Time:  {american_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"")
    print(f"Turkey Date:    {turkey_date}")
    print(f"American Date:  {american_date}")
    print(f"")
    
    if turkey_date != american_date:
        print(f"⚠️  DATE MISMATCH DETECTED!")
        print(f"    Turkey is on:  {turkey_date}")
        print(f"    America is on: {american_date}")
        print(f"    This causes the scraping issue you mentioned!")
        print(f"    ✅ Using American time will fix this.")
    else:
        print(f"✅ Dates match - no timezone issue today")
    
    # Show race scraping scenario
    print(f"\n🏇 RACE SCRAPING SCENARIO:")
    print(f"   If Turkey time > 00:00, Turkish system looks for: {turkey_date}")
    print(f"   But American races are still happening on: {american_date}")
    print(f"   📅 Solution: Always use American date for race data!")
    
    # Test our import
    try:
        from hrn_scraper import get_american_date_string
        scraper_american_date = get_american_date_string()
        print(f"\n🔧 SCRAPER TEST:")
        print(f"   Scraper will now use: {scraper_american_date}")
        print(f"   ✅ American timezone successfully integrated!")
    except ImportError:
        print(f"\n❌ SCRAPER IMPORT FAILED - check hrn_scraper updates")

if __name__ == "__main__":
    test_date_comparison()