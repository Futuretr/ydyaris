#!/usr/bin/env python3
"""Import test"""

try:
    print("Flask importing...")
    from flask import Flask, render_template, request, jsonify, send_file, url_for
    print("✅ Flask OK")
    
    print("Basic imports...")
    import pandas as pd
    import numpy as np
    import os
    import sys
    import csv
    import json
    import glob
    import logging
    from datetime import datetime
    print("✅ Basic imports OK")
    
    print("Timezone imports...")
    import pytz
    print("✅ Timezone imports OK")
    
    print("Current directory modules...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    hrn_scraper_path = os.path.join(current_dir, 'hrn_scraper')
    if hrn_scraper_path not in sys.path:
        sys.path.insert(0, hrn_scraper_path)
    
    from american_horse_calculator_turkish_style import load_horses_from_csv
    print("✅ Turkish calculator OK")
    
    from horse_profile_scraper import HorseProfileScraper  
    print("✅ Horse profile scraper OK")
    
    from hrn_scraper import HorseRacingNationScraper
    print("✅ HRN scraper OK")
    
    print("🎉 ALL IMPORTS SUCCESSFUL!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()