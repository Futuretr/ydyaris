#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API ENDPOINTS TEST
Web arayüzü API endpoint'lerini test eder
"""

import requests
import json

def test_api_endpoints():
    """API endpoint'lerini test et"""
    print("🔌 API ENDPOINTS TEST")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5010"
    
    endpoints = [
        {
            'name': 'Check Saved Data',
            'url': f'{base_url}/api/check_saved_data',
            'method': 'POST',
            'data': {'city': 'finger-lakes'}
        },
        {
            'name': 'Scrape Data',
            'url': f'{base_url}/api/scrape_data',
            'method': 'POST', 
            'data': {'city': 'finger-lakes'}
        },
        {
            'name': 'Quick Calculate',
            'url': f'{base_url}/api/quick_calculate',
            'method': 'POST',
            'data': {'city': 'finger-lakes'}
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n🎯 Testing: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        
        try:
            if endpoint['method'] == 'POST':
                response = requests.post(
                    endpoint['url'], 
                    json=endpoint['data'],
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
            else:
                response = requests.get(endpoint['url'], timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Response: Valid JSON ✅")
                    if 'success' in data:
                        print(f"   Success: {data['success']}")
                    if 'message' in data:
                        print(f"   Message: {data['message'][:100]}...")
                except json.JSONDecodeError:
                    print(f"   Response: Invalid JSON ❌")
                    print(f"   Text: {response.text[:200]}...")
            else:
                print(f"   Error: {response.status_code}")
                print(f"   Text: {response.text[:200]}...")
                
        except requests.RequestException as e:
            print(f"   ❌ Request Error: {e}")
        except Exception as e:
            print(f"   ❌ Other Error: {e}")

if __name__ == "__main__":
    test_api_endpoints()