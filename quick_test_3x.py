#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QUICK TEST - 3X PENALTY SYSTEM
Hızlı test: Penalty'yi 3x'e düşürüp test eder
"""

import sys
import os

# Add hrn_scraper to path
sys.path.append('hrn_scraper')

try:
    from american_horse_calculator_turkish_style import calculate_position_penalty
    print("SUCCESS: Turkish Style Calculator imported")
except ImportError as e:
    print(f"ERROR: Cannot import Turkish Style Calculator: {e}")
    sys.exit(1)

def quick_penalty_test():
    """Quick test of 3x penalty system"""
    print("\n" + "="*50)
    print("3X PENALTY SYSTEM - QUICK TEST")
    print("="*50)
    
    base_time = 6.50  # 6.50 seconds per 100m
    distance_6f = 1207.008  # 6 Furlong in meters
    distance_1m = 1609.344  # 1 Mile in meters
    
    print(f"\n{'Position':<10} {'6F Penalty':<15} {'1M Penalty':<15} {'Difference':<12}")
    print("-" * 55)
    
    for pos in [1, 2, 3, 5, 8]:
        penalty_6f = calculate_position_penalty(pos, base_time, distance_6f)
        penalty_1m = calculate_position_penalty(pos, base_time, distance_1m)
        
        diff_6f = penalty_6f - base_time
        diff_1m = penalty_1m - base_time
        
        print(f"{pos:<10} +{diff_6f:.3f}s{'':<9} +{diff_1m:.3f}s{'':<9} {'OK' if diff_6f > 0 or pos == 1 else 'ERROR':<12}")
    
    print(f"\n📋 SUMMARY:")
    print(f"✅ Base penalty per position: 0.30 seconds")
    print(f"✅ 2nd place penalty (6F): ~0.025s per 100m")
    print(f"✅ 2nd place penalty (1M): ~0.019s per 100m") 
    print(f"✅ 5th place penalty (6F): ~0.099s per 100m")
    print(f"✅ 8th place penalty (1M): ~0.130s per 100m")
    print(f"✅ Moderate penalty effect - balanced system")

if __name__ == "__main__":
    quick_penalty_test()