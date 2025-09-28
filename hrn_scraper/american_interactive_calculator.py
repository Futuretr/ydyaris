#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AMERICAN HORSE CALCULATOR - INTERACTIVE TERMINAL VERSION
Amerika atları için interaktif terminal sistemi
Kullanıcı track seçer, sistem otomatik veri çeker ve hesaplama yapar
Zemin adaptasyonu ve kilo hesaplamaları kaldırılmıştır
"""

import pandas as pd
import time
import os
import json
import re
import math
from datetime import datetime
import sys

# Import our scraper modules
try:
    from multi_track_scraper import scrape_track_data, scrape_horse_profiles_for_track
    from single_track_scraper import scrape_single_track
except ImportError as e:
    print(f"Error importing scraper modules: {e}")
    print("Make sure multi_track_scraper.py and single_track_scraper.py are in the same directory")
    sys.exit(1)

def time_to_seconds(time_str):
    """Convert time string to seconds for American format"""
    if not time_str or str(time_str).strip() in ['', '-', '0']:
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
    """Convert American distance formats to meters"""
    if not distance_str or str(distance_str).strip() in ['', '-', '0']:
        return 0
    
    distance_str = str(distance_str).strip().lower()
    
    # Handle fraction formats: "1 1/16M" = 1.0625 miles
    fraction_match = re.match(r'(\d+)\s*(\d+)/(\d+)\s*([mf])', distance_str)
    if fraction_match:
        whole = int(fraction_match.group(1))
        numerator = int(fraction_match.group(2))
        denominator = int(fraction_match.group(3))
        unit = fraction_match.group(4)
        
        total = whole + (numerator / denominator)
        
        if unit == 'm':  # Miles
            return total * 1609.344
        elif unit == 'f':  # Furlongs
            return total * 201.168
    
    # Handle simple fraction: "6 1/2F" = 6.5 furlongs
    simple_fraction_match = re.match(r'(\d+)\s*(\d+)/(\d+)\s*([mf])', distance_str)
    if simple_fraction_match:
        whole = int(simple_fraction_match.group(1))
        numerator = int(simple_fraction_match.group(2))
        denominator = int(simple_fraction_match.group(3))
        unit = simple_fraction_match.group(4)
        
        total = whole + (numerator / denominator)
        
        if unit == 'm':  # Miles
            return total * 1609.344
        elif unit == 'f':  # Furlongs
            return total * 201.168
    
    # Handle "1 mile", "1 m", "6f", "5F"
    standard_match = re.match(r'(\d+(?:\.\d+)?)\s*(mile|miles|m|f|furlong|furlongs|y|yard|yards)?', distance_str)
    if standard_match:
        number = float(standard_match.group(1))
        unit = standard_match.group(2) or 'f'  # Default to furlongs
        
        if unit in ['mile', 'miles', 'm']:
            return number * 1609.344  # Miles to meters
        elif unit in ['f', 'furlong', 'furlongs']:
            return number * 201.168   # Furlongs to meters
        elif unit in ['y', 'yard', 'yards']:
            return number * 0.9144    # Yards to meters
    
    # Try to parse as pure number (assume furlongs)
    try:
        number = float(re.sub(r'[^\d\.]', '', distance_str))
        return number * 201.168  # Default to furlongs
    except:
        pass
    
    return 0

def calculate_performance_score(horse_data):
    """
    Calculate simple performance score for American horses
    Only uses time and distance - no surface or weight adjustments
    """
    try:
        # Get profile race data (from past performance)
        profile_distance = horse_data.get('profile_distance', '')
        profile_time = horse_data.get('profile_time', '')
        
        # Convert distance to meters
        distance_meters = distance_to_meters(profile_distance)
        if distance_meters <= 0:
            return None, "Invalid distance"
        
        # Convert time to seconds
        time_seconds = time_to_seconds(profile_time)
        if time_seconds <= 0:
            return None, "Invalid time"
        
        # Calculate speed in meters per second
        speed_mps = distance_meters / time_seconds
        
        # Calculate time per 100 meters (lower is better)
        time_per_100m = 100 / speed_mps
        
        # Return performance score (time per 100m)
        return round(time_per_100m, 2), "Success"
        
    except Exception as e:
        return None, f"Calculation error: {str(e)}"

def process_horses_data(horses_list):
    """Process list of horses and calculate performance scores"""
    results = []
    
    for horse in horses_list:
        horse_name = horse.get('horse_name', '')
        track = horse.get('track', '')
        date = horse.get('date', '')
        race_number = horse.get('race_number', '')
        program_number = horse.get('program_number', '')
        
        # Calculate performance score
        score, status = calculate_performance_score(horse)
        
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

def save_results_to_csv(results, filename_prefix="american_horses_calculation"):
    """Save calculation results to CSV file with proper sorting"""
    try:
        if not results:
            print("No data to save")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Sort by race, then by performance score (better scores first)
        # First separate valid and invalid scores
        valid_df = df[df['performance_score'] != 'Invalid'].copy()
        invalid_df = df[df['performance_score'] == 'Invalid'].copy()
        
        # Sort valid scores by race_number, then by performance_score (ascending - lower is better)
        if not valid_df.empty:
            valid_df['performance_score_num'] = pd.to_numeric(valid_df['performance_score'], errors='coerce')
            valid_df = valid_df.sort_values(['race_number', 'performance_score_num'])
            valid_df = valid_df.drop('performance_score_num', axis=1)
        
        # Sort invalid scores by race_number only
        if not invalid_df.empty:
            invalid_df = invalid_df.sort_values(['race_number'])
        
        # Combine: valid first, then invalid, both sorted by race
        df_sorted = pd.concat([valid_df, invalid_df], ignore_index=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename_prefix}_{timestamp}.csv"
        
        # Save to CSV
        df_sorted.to_csv(filename, index=False, encoding='utf-8')
        
        print(f"Results saved to: {filename}")
        print(f"Total horses processed: {len(results)}")
        
        # Print summary statistics
        valid_count = len([r for r in results if r['performance_score'] != 'Invalid'])
        invalid_count = len(results) - valid_count
        success_rate = (valid_count / len(results)) * 100 if results else 0
        
        print(f"Valid calculations: {valid_count}")
        print(f"Invalid calculations: {invalid_count}")
        print(f"Success rate: {success_rate:.1f}%")
        
        return filename
        
    except Exception as e:
        print(f"Error saving results: {e}")
        return None

def print_race_summary(grouped_results):
    """Print summary of results grouped by race"""
    print("\n" + "="*80)
    print("RACE SUMMARY - AMERICAN HORSES PERFORMANCE CALCULATION")
    print("="*80)
    
    for race_key in sorted(grouped_results.keys()):
        horses = grouped_results[race_key]
        if not horses:
            continue
            
        # Extract race info from first horse
        first_horse = horses[0]
        track = first_horse['track']
        date = first_horse['date']
        race_num = first_horse['race_number']
        
        print(f"\n{track.upper()} - {date} - Race {race_num}")
        print("-" * 60)
        
        # Count valid vs invalid
        valid_horses = [h for h in horses if h['performance_score'] != 'Invalid']
        invalid_horses = [h for h in horses if h['performance_score'] == 'Invalid']
        
        print(f"Valid calculations: {len(valid_horses)}/{len(horses)} horses")
        
        # Show top performers
        if valid_horses:
            print("\nTop Performers (by speed - lower score is better):")
            for i, horse in enumerate(valid_horses[:5], 1):
                score = horse['performance_score']
                name = horse['horse_name']
                distance = horse['entry_distance']
                time = horse['profile_time']
                print(f"  {i}. {name} - {score}s/100m (Distance: {distance}, Time: {time})")
        
        # Show invalid horses
        if invalid_horses:
            print(f"\nInvalid calculations ({len(invalid_horses)} horses):")
            for horse in invalid_horses[:3]:  # Show first 3
                name = horse['horse_name']
                status = horse['calculation_status']
                print(f"  - {name}: {status}")
            if len(invalid_horses) > 3:
                print(f"  ... and {len(invalid_horses) - 3} more")

# Available tracks and their codes
AVAILABLE_TRACKS = {
    "1": {"name": "Aqueduct", "code": "aqueduct"},
    "2": {"name": "Belmont Park", "code": "belmont-park"},
    "3": {"name": "Churchill Downs", "code": "churchill-downs"},
    "4": {"name": "Del Mar", "code": "del-mar"},
    "5": {"name": "Gulfstream Park", "code": "gulfstream-park"},
    "6": {"name": "Keeneland", "code": "keeneland"},
    "7": {"name": "Laurel Park", "code": "laurel-park"},
    "8": {"name": "Oaklawn Park", "code": "oaklawn-park"},
    "9": {"name": "Pimlico", "code": "pimlico"},
    "10": {"name": "Santa Anita", "code": "santa-anita"},
    "11": {"name": "Saratoga", "code": "saratoga"},
    "12": {"name": "Woodbine", "code": "woodbine"}
}

def display_track_menu():
    """Display available tracks menu"""
    print("\n" + "="*50)
    print("AVAILABLE AMERICAN RACE TRACKS")
    print("="*50)
    for key, track in AVAILABLE_TRACKS.items():
        print(f"{key:2}. {track['name']}")
    print("="*50)

def get_user_track_choice():
    """Get user's track choice"""
    while True:
        display_track_menu()
        choice = input("\nSelect track number (or 'q' to quit): ").strip()
        
        if choice.lower() == 'q':
            return None, None
        
        if choice in AVAILABLE_TRACKS:
            track_info = AVAILABLE_TRACKS[choice]
            return track_info['code'], track_info['name']
        else:
            print(f"Invalid choice '{choice}'. Please select a number from 1-{len(AVAILABLE_TRACKS)}")

def get_target_date():
    """Get target date from user"""
    while True:
        print(f"\nEnter date (YYYY-MM-DD) or press Enter for today ({datetime.now().strftime('%Y-%m-%d')}):")
        date_input = input().strip()
        
        if not date_input:
            return datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Validate date format
            datetime.strptime(date_input, '%Y-%m-%d')
            return date_input
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD")

def scrape_and_calculate_track(track_code, track_name, target_date):
    """Scrape track data and calculate performance scores"""
    print(f"\n🏇 Processing {track_name} for {target_date}")
    print("="*60)
    
    try:
        # Step 1: Scrape entries using single track scraper
        print("📋 Step 1: Scraping race entries...")
        success = scrape_single_track(track_code, target_date)
        
        if not success:
            print(f"❌ No entries found for {track_name} on {target_date}")
            return None
        
        # Expected filename from single track scraper
        entries_file = f"{track_code}_{target_date.replace('-', '_')}_{track_code}_entries.csv"
        
        if not os.path.exists(entries_file):
            print(f"❌ Entries file not created: {entries_file}")
            return None
        
        print(f"✅ Entries scraped successfully: {entries_file}")
        
        # Step 2: Scrape horse profiles using multi track function
        print("🐴 Step 2: Scraping horse profiles...")
        scrape_horse_profiles_for_track(entries_file)
        
        # Expected essential file
        essential_file = entries_file.replace('_entries.csv', '_essential.csv')
        
        if not os.path.exists(essential_file):
            print(f"❌ Essential data file not created: {essential_file}")
            return None
        
        print(f"✅ Horse profiles scraped successfully: {essential_file}")
        
        # Step 3: Load the scraped data
        print("📊 Step 3: Loading scraped data...")
        df = pd.read_csv(essential_file)
        
        # Map column names to match calculator expectations
        column_mapping = {
            'latest_distance': 'profile_distance',
            'latest_time': 'profile_time',
            'latest_surface': 'profile_surface'
        }
        
        # Add required columns with track info
        df['track'] = track_code
        df['date'] = target_date
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        horses_data = df.to_dict('records')
        
        print(f"✅ Loaded {len(horses_data)} horses from scraped data")
        
        # Step 4: Calculate performance scores
        print("🧮 Step 4: Calculating performance scores...")
        results = process_horses_data(horses_data)
        
        # Step 5: Group and sort results
        grouped_results = group_by_race_and_sort(results)
        
        # Step 6: Display results
        print_race_summary(grouped_results)
        
        # Step 7: Save to CSV
        print(f"\n💾 Step 7: Saving results...")
        filename_prefix = f"american_{track_code}_{target_date.replace('-', '_')}"
        output_file = save_results_to_csv(results, filename_prefix)
        
        if output_file:
            print(f"\n✅ Process completed successfully!")
            print(f"📄 Results saved to: {output_file}")
            return output_file
        else:
            print(f"\n❌ Error saving results")
            return None
            
    except Exception as e:
        print(f"❌ Error processing {track_name}: {e}")
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")
        return None

def main():
    """Main interactive function"""
    print("🏇 AMERICAN HORSE PERFORMANCE CALCULATOR")
    print("========================================")
    print("Interactive terminal version - Select track and calculate performance scores")
    print("No surface or weight adjustments - Pure time/distance calculation")
    
    while True:
        try:
            # Get user's track choice
            track_code, track_name = get_user_track_choice()
            
            if not track_code:  # User chose to quit
                print("👋 Goodbye!")
                break
            
            # Get target date
            target_date = get_target_date()
            
            # Confirm selection
            print(f"\n🎯 Selected: {track_name} ({track_code}) for {target_date}")
            confirm = input("Proceed? (y/n): ").strip().lower()
            
            if confirm not in ['y', 'yes']:
                print("❌ Cancelled")
                continue
            
            # Process the track
            result_file = scrape_and_calculate_track(track_code, track_name, target_date)
            
            # Ask if user wants to process another track
            print(f"\n" + "="*60)
            another = input("Process another track? (y/n): ").strip().lower()
            if another not in ['y', 'yes']:
                print("👋 Process completed!")
                break
                
        except KeyboardInterrupt:
            print(f"\n\n👋 Process interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            continue

if __name__ == "__main__":
    main()