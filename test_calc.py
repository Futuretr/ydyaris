import sys, os
sys.path.insert(0, 'hrn_scraper')
from american_horse_calculator_with_position import load_horses_from_csv, process_horses_data

horses = load_horses_from_csv('gulfstream-park_2025_09_28_gulfstream-park_essential.csv')
print(f'Loaded {len(horses)} horses')

# İlk birkaç atı test et
for i in range(min(3, len(horses))):
    h = horses[i] 
    print(f'Horse {i+1}: {h.get("horse_name", "N/A")}')
    print(f'  - latest_finish_position: {h.get("latest_finish_position", "Missing")}')
    print(f'  - latest_time: {h.get("latest_time", "Missing")}')
    print(f'  - latest_distance: {h.get("latest_distance", "Missing")}')

print('\nProcessing first 3 horses...')
results = process_horses_data(horses[:3])
for r in results:
    print(f'{r["horse_name"]}: pos={r.get("latest_finish_position", "N/A")}, score={r["performance_score"]}, status={r["calculation_status"]}')