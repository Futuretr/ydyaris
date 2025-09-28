#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AMERICAN HORSE CALCULATOR - TURKISH STYLE
Amerika atları için Türk sistemi hesaplama mantığı
- Kazananın derecesi referans alınır
- Finish position'a göre penalty eklenir
- 100 metre bazlı mesafe adaptasyonu
- Zemin adaptasyonu korunur
"""

import pandas as pd
import time
import os
import json
import re
import math
import logging
import pytz
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# America Eastern Time Zone
def get_american_time():
    """Get current time in American Eastern Time (EST/EDT)"""
    eastern = pytz.timezone('US/Eastern')
    return datetime.now(eastern)

def time_to_seconds(time_str):
    """Convert American time string to seconds"""
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

def calculate_surface_adaptation(previous_surface, current_surface):
    """Calculate surface adaptation factor"""
    # Surface adaptation factors
    surface_factors = {
        ('Dirt', 'Dirt'): 1.0,
        ('Dirt', 'Turf'): 1.02,     # Dirt'ten Turf'e geçiş
        ('Dirt', 'Synthetic'): 1.01,
        ('Turf', 'Dirt'): 0.98,     # Turf'ten Dirt'e geçiş
        ('Turf', 'Turf'): 1.0,
        ('Turf', 'Synthetic'): 1.01,
        ('Synthetic', 'Dirt'): 0.99,
        ('Synthetic', 'Turf'): 1.03,
        ('Synthetic', 'Synthetic'): 1.0
    }
    
    return surface_factors.get((previous_surface, current_surface), 1.0)

def calculate_distance_adaptation(profile_distance, target_distance):
    """Calculate distance adaptation factor - like Turkish system"""
    try:
        distance_diff = target_distance - profile_distance
        
        if abs(distance_diff) < 100:  # Less than 100m difference
            return 1.0
        
        # Turkish style distance adaptation
        if distance_diff > 0:  # Longer distance
            # For every 100m longer: +0.04 seconds per 100m
            factor = 1 + (distance_diff / 100) * 0.04 / 6.0  # Normalize to ~6 second base
        else:  # Shorter distance
            # For every 100m shorter: -0.03 seconds per 100m
            factor = 1 + (abs(distance_diff) / 100) * (-0.03) / 6.0
        
        # Limit factor between 0.8 and 1.2
        return max(0.8, min(1.2, factor))
        
    except:
        return 1.0

def calculate_position_penalty(finish_position, winner_time_per_100m, distance_meters):
    """
    Calculate penalty based on finish position - Turkish style
    
    Args:
        finish_position: Horse's finish position (1, 2, 3, etc.)
        winner_time_per_100m: Winner's time per 100m (reference)
        distance_meters: Race distance in meters
        
    Returns:
        Adjusted time per 100m for this horse
    """
    try:
        if not finish_position or finish_position == '' or finish_position == 'nan':
            return winner_time_per_100m  # No position data, return winner time
        
        # Convert to int
        if isinstance(finish_position, float) and math.isnan(finish_position):
            return winner_time_per_100m
            
        try:
            pos = int(float(str(finish_position).strip()))
        except:
            return winner_time_per_100m
        
        if pos <= 0:
            return winner_time_per_100m
        
        if pos == 1:
            # Winner - no penalty
            return winner_time_per_100m
        
        # Calculate penalty based on position and distance
        # Turkish system: Each position adds time based on distance
        # 1st vs 2nd: 0.30 seconds per full race (3x penalty)
        # 1st vs 3rd: 0.60 seconds per full race, etc.
        
        position_penalty_per_race = (pos - 1) * 0.30  # 0.30s per position (3x optimized)
        
        # Convert to per 100m penalty
        # If race is 1200m, penalty should be distributed over 12 x 100m segments
        segments_100m = distance_meters / 100.0
        penalty_per_100m = position_penalty_per_race / segments_100m
        
        adjusted_time_per_100m = winner_time_per_100m + penalty_per_100m
        
        logger.info(f"Position penalty: Pos {pos}, Distance {distance_meters}m, "
                   f"Base time: {winner_time_per_100m:.2f}, Penalty: +{penalty_per_100m:.3f}, "
                   f"Final: {adjusted_time_per_100m:.2f}")
        
        return adjusted_time_per_100m
        
    except Exception as e:
        logger.error(f"Position penalty calculation error: {e}")
        return winner_time_per_100m

def calculate_american_horse_performance_turkish_style(horse_data, race_data, winner_data=None):
    """
    Calculate American horse performance using Turkish methodology
    
    Args:
        horse_data: Individual horse's profile data
        race_data: Today's race information  
        winner_data: Winner's performance data (optional, for reference)
    """
    try:
        # Get basic data
        profile_time = horse_data.get('profile_time', '') or horse_data.get('time', '')
        profile_distance = horse_data.get('profile_distance', '') or horse_data.get('distance', '')
        profile_surface = horse_data.get('profile_surface', '') or horse_data.get('surface', '')
        finish_position = horse_data.get('latest_finish_position', '') or horse_data.get('finish_position', '')
        
        # Validation
        if not profile_time or not profile_distance:
            return None
        
        # Convert to standard units
        time_seconds = time_to_seconds(profile_time)
        distance_meters = distance_to_meters(profile_distance)
        
        if time_seconds <= 0 or distance_meters <= 0:
            return None
        
        # Get race information
        target_distance = distance_to_meters(race_data.get('distance', '6f'))
        target_surface = race_data.get('surface', 'Dirt')
        
        if target_distance <= 0:
            target_distance = 1200  # Default 6 furlongs
        
        # Step 1: Calculate base time per 100m from profile
        base_time_per_100m = time_seconds / (distance_meters / 100)
        
        # Step 2: Apply surface adaptation
        surface_factor = calculate_surface_adaptation(profile_surface, target_surface)
        surface_adjusted = base_time_per_100m * surface_factor
        
        # Step 3: Apply distance adaptation (Turkish style)
        distance_factor = calculate_distance_adaptation(distance_meters, target_distance)
        distance_adjusted = surface_adjusted * distance_factor
        
        # Step 4: Apply position penalty (Turkish style)
        # If this horse was not the winner, add penalty based on position
        final_time_per_100m = distance_adjusted
        
        if finish_position and str(finish_position).strip() not in ['', '1', 'nan']:
            try:
                pos = int(float(str(finish_position).strip()))
                if pos > 1:
                    # This horse was not the winner, apply penalty
                    # Use the winner's theoretical time as reference
                    winner_reference_time = distance_adjusted  # Assume this would be winner time
                    final_time_per_100m = calculate_position_penalty(
                        pos, winner_reference_time, target_distance
                    )
            except:
                pass
        
        # Calculate total race time for reference
        total_race_time = final_time_per_100m * (target_distance / 100)
        
        return {
            'raw_time_per_100m': base_time_per_100m,
            'surface_factor': surface_factor,
            'distance_factor': distance_factor,
            'finish_position': finish_position,
            'position_penalty_applied': str(finish_position).strip() not in ['', '1', 'nan'] if finish_position else False,
            'final_score': final_time_per_100m,
            'total_race_time': total_race_time,
            'original_time': time_seconds,
            'original_distance': distance_meters,
            'target_distance': target_distance,
            'surface_transition': f"{profile_surface} -> {target_surface}"
        }
        
    except Exception as e:
        logger.error(f"Turkish style performance calculation error: {e}")
        return None

def process_horses_data_turkish_style(horses_list):
    """Process list of horses using Turkish calculation methodology"""
    results = []
    
    for horse in horses_list:
        horse_name = horse.get('horse_name', '')
        track = horse.get('track', '')
        date = horse.get('date', '')
        race_number = horse.get('race_number', '')
        program_number = horse.get('program_number', '')
        
        # Prepare race data
        race_data = {
            'distance': horse.get('entry_distance', ''),
            'surface': horse.get('entry_surface', '')
        }
        
        # Calculate performance score using Turkish methodology
        performance = calculate_american_horse_performance_turkish_style(horse, race_data)
        
        # Prepare result
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
            'performance_score': performance['final_score'] if performance else 'Invalid',
            'calculation_details': {
                'raw_time_per_100m': performance.get('raw_time_per_100m') if performance else None,
                'surface_factor': performance.get('surface_factor') if performance else None,
                'distance_factor': performance.get('distance_factor') if performance else None,
                'position_penalty_applied': performance.get('position_penalty_applied') if performance else None,
                'total_race_time': performance.get('total_race_time') if performance else None
            } if performance else None,
            'calculation_status': 'Success' if performance else 'Failed'
        }
        
        results.append(result)
    
    return results

def group_by_race_and_sort(results):
    """Group results by race and sort by performance score (Turkish style)"""
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

def save_results_to_csv(results, filename_prefix="american_horses_turkish_style"):
    """Save calculation results to CSV file with proper sorting"""
    if not results:
        print("No results to save")
        return None
    
    try:
        # Group and sort results
        grouped_results = group_by_race_and_sort(results)
        
        # Flatten results with proper race ordering
        sorted_results = []
        for race_key in sorted(grouped_results.keys()):
            sorted_results.extend(grouped_results[race_key])
        
        # Create DataFrame
        df = pd.DataFrame(sorted_results)
        
        # Expand calculation_details into separate columns if exists
        if 'calculation_details' in df.columns and df['calculation_details'].notna().any():
            detail_columns = {}
            for i, details in enumerate(df['calculation_details']):
                if details and isinstance(details, dict):
                    for key, value in details.items():
                        col_name = f'calc_{key}'
                        if col_name not in detail_columns:
                            detail_columns[col_name] = [None] * len(df)
                        detail_columns[col_name][i] = value
            
            # Add detail columns to DataFrame
            for col_name, values in detail_columns.items():
                df[col_name] = values
        
        # Remove the nested calculation_details column
        if 'calculation_details' in df.columns:
            df = df.drop('calculation_details', axis=1)
        
        # Generate filename with timestamp (America Eastern Time)
        timestamp = get_american_time().strftime('%Y%m%d_%H%M%S')
        filename = f"{filename_prefix}_{timestamp}.csv"
        
        # Save to CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        
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
    print("RACE SUMMARY - AMERICAN HORSES TURKISH STYLE CALCULATION")
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
                position = horse.get('latest_finish_position', 'N/A')
                distance = horse['entry_distance']
                surface = horse['entry_surface']
                print(f"  {i}. {name} - {score:.2f}s/100m (Pos: {position}, {distance} {surface})")
        
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
        df = pd.read_csv(csv_file_path)
        horses = df.to_dict('records')
        
        print(f"Loaded {len(horses)} horses from {csv_file_path}")
        
        # Check data structure
        if horses:
            sample = horses[0]
            print("Sample horse data structure:")
            for key, value in sample.items():
                print(f"  {key}: {value}")
        
        return horses
        
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return []

def main():
    """Main function to run the Turkish-style calculation"""
    print("🏇 AMERICAN HORSE PERFORMANCE CALCULATOR - TURKISH STYLE")
    print("=========================================================")
    print("🇹🇷 Bu sistem Türk hesaplama mantığını Amerika atlarına uygular:")
    print("✅ Kazananın derecesi referans alınır")
    print("✅ Derece bazlı penalty sistemi (her derece 0.10s)")
    print("✅ 100 metre bazlı mesafe adaptasyonu")
    print("✅ Zemin geçiş adaptasyonları")
    print("✅ Sadece bu yöntem kullanılır - diğerleri devre dışı!\n")
    
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
        print("No horse data loaded. Exiting.")
        return
    
    print(f"\nProcessing {len(horses_list)} horses...")
    
    # Process horses using Turkish methodology
    results = process_horses_data_turkish_style(horses_list)
    
    # Group and display results
    grouped_results = group_by_race_and_sort(results)
    print_race_summary(grouped_results)
    
    # Save results
    filename = save_results_to_csv(results)
    if filename:
        print(f"\n✅ Results saved successfully to: {filename}")
    
    # Ask if user wants to see detailed results
    show_details = input("\nShow detailed calculation info? (y/n): ").strip().lower()
    if show_details == 'y':
        print("\nDETAILED CALCULATION RESULTS:")
        print("="*80)
        for result in results[:10]:  # Show first 10
            if result['performance_score'] != 'Invalid':
                details = result.get('calculation_details', {})
                print(f"\n{result['horse_name']} (Race {result['race_number']}):")
                print(f"  Final Score: {result['performance_score']:.2f} s/100m")
                if details:
                    print(f"  Raw time/100m: {details.get('raw_time_per_100m', 'N/A'):.2f}")
                    print(f"  Surface factor: {details.get('surface_factor', 'N/A'):.3f}")
                    print(f"  Distance factor: {details.get('distance_factor', 'N/A'):.3f}")
                    print(f"  Position penalty: {details.get('position_penalty_applied', 'N/A')}")
                    print(f"  Est. race time: {details.get('total_race_time', 'N/A'):.1f}s")

if __name__ == "__main__":
    main()