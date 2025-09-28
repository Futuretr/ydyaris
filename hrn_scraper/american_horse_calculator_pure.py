#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AMERICAN HORSE CALCULATOR - PURE CALCULATION ONLY
Amerika atları için saf hesaplama sistemi
Web'den veri çekmez, sadece hesaplama yapar
Zemin adaptasyonu ve kilo hesaplamaları kaldırılmıştır
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

def load_horses_from_csv(csv_file_path):
    """Load horses data from CSV file (from scraper output)"""
    try:
        print(f"Loading horses data from: {csv_file_path}")
        
        if not os.path.exists(csv_file_path):
            print(f"File not found: {csv_file_path}")
            return []
        
        df = pd.read_csv(csv_file_path)
        
        # Map column names from essential CSV format to expected format
        column_mapping = {
            'latest_distance': 'profile_distance',
            'latest_time': 'profile_time', 
            'latest_surface': 'profile_surface'
        }
        
        # Rename columns if they exist in the mapping
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df[new_col] = df[old_col]
        
        # Convert DataFrame to list of dictionaries
        horses_list = df.to_dict('records')
        
        print(f"Loaded {len(horses_list)} horses from CSV")
        return horses_list
        
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return []

def main():
    """Main function to run the calculation"""
    print("AMERICAN HORSE PERFORMANCE CALCULATOR")
    print("=====================================")
    print("This calculator processes American horse racing data")
    print("and calculates performance scores based on time and distance only.")
    print("No surface or weight adjustments are applied.\n")
    
    # Ask user for input file
    csv_file = input("Enter CSV file path (or press Enter for default test): ").strip()
    
    if not csv_file:
        # Look for recent CSV files in current directory
        csv_files = [f for f in os.listdir('.') if f.endswith('.csv') and 'american' in f.lower()]
        if csv_files:
            # Sort by modification time, newest first
            csv_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            csv_file = csv_files[0]
            print(f"Using most recent American CSV file: {csv_file}")
        else:
            print("No CSV files found. Please provide a valid file path.")
            return
    
    # Load horses data
    horses_list = load_horses_from_csv(csv_file)
    if not horses_list:
        return
    
    print(f"\nProcessing {len(horses_list)} horses...")
    
    # Process calculations
    results = process_horses_data(horses_list)
    
    # Group and sort results
    grouped_results = group_by_race_and_sort(results)
    
    # Print summary
    print_race_summary(grouped_results)
    
    # Save results to CSV
    print(f"\nSaving results...")
    base_filename = os.path.splitext(os.path.basename(csv_file))[0]
    output_filename = save_results_to_csv(results, f"{base_filename}_calculated")
    
    if output_filename:
        print(f"\n✅ Calculation completed successfully!")
        print(f"📄 Output file: {output_filename}")
    else:
        print(f"\n❌ Error saving results")

if __name__ == "__main__":
    main()