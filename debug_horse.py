import sys
sys.path.insert(0, 'hrn_scraper')
from american_horse_calculator_with_position import distance_to_meters, calculate_performance_score_with_position

# Test single horse
horse = {
    'horse_name': 'Dont Go Astray', 
    'profile_distance': '5 f',
    'profile_time': '0:56.77',
    'latest_finish_position': 9.0
}

print('Distance:', horse['profile_distance'])
print('Distance in meters:', distance_to_meters(horse['profile_distance']))
print('Time:', horse['profile_time'])
print('Position:', horse['latest_finish_position'])

score, status = calculate_performance_score_with_position(horse)
print('Result score:', score)
print('Result status:', status)