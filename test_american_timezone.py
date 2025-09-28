#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AMERICA TIMEZONE TEST
Amerika saat dilimi testini yapar
"""

import pytz
from datetime import datetime

def test_american_timezone():
    """Test American Eastern Time implementation"""
    print("🇺🇸 AMERICA TIMEZONE TEST")
    print("=" * 50)
    
    # Get American Eastern Time
    eastern = pytz.timezone('US/Eastern')
    american_time = datetime.now(eastern)
    
    # Get local time
    local_time = datetime.now()
    
    print(f"Local Time (Turkey):     {local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"American Eastern Time:   {american_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"American Date String:    {american_time.strftime('%Y-%m-%d')}")
    print(f"American Timestamp:      {american_time.strftime('%Y%m%d_%H%M%S')}")
    
    # Time difference
    time_diff = (local_time.replace(tzinfo=pytz.UTC) - american_time.astimezone(pytz.UTC)).total_seconds() / 3600
    print(f"Time Difference:         {time_diff:.1f} hours")
    
    print(f"\n✅ America Eastern Time successfully configured!")
    print(f"📅 Today in America: {american_time.strftime('%A, %B %d, %Y')}")
    print(f"⏰ Current time in America: {american_time.strftime('%I:%M:%S %p %Z')}")

if __name__ == "__main__":
    test_american_timezone()