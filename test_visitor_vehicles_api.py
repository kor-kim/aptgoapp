#!/usr/bin/env python3
"""
Test script to verify visitor vehicle data from the server API.
"""
import requests
import json
import asyncio
from datetime import datetime

# Server configuration
BASE_URL = "https://aptgo.org"
USERNAME = "newtest1754832743"
PASSWORD = "admin123"

async def test_comprehensive_api():
    """Test the comprehensive vehicle data API"""
    print("=" * 60)
    print("Testing Comprehensive Vehicle Data API")
    print("=" * 60)
    
    # 1. Login first
    print("\n1. Logging in...")
    login_url = f"{BASE_URL}/api/login/"
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    login_response = requests.post(login_url, json=login_data)
    print(f"   Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        token = login_result.get('token')
        print(f"   Token received: {token[:20]}..." if token else "No token")
        
        # 2. Call comprehensive API
        print("\n2. Fetching comprehensive vehicle data...")
        comprehensive_url = f"{BASE_URL}/api/comprehensive/"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        comprehensive_response = requests.get(comprehensive_url, headers=headers)
        print(f"   API status: {comprehensive_response.status_code}")
        
        if comprehensive_response.status_code == 200:
            data = comprehensive_response.json()
            
            # 3. Analyze the response
            print("\n3. Response Analysis:")
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            
            vehicles = data.get('vehicles', [])
            visitor_vehicles = data.get('visitorVehicles', [])
            residents = data.get('residents', [])
            sub_accounts = data.get('subAccounts', [])
            
            print(f"\n   Data counts:")
            print(f"   - Regular vehicles: {len(vehicles)}")
            print(f"   - Visitor vehicles: {len(visitor_vehicles)}")
            print(f"   - Residents: {len(residents)}")
            print(f"   - Sub accounts: {len(sub_accounts)}")
            
            # 4. Display visitor vehicles details
            if visitor_vehicles:
                print(f"\n4. Visitor Vehicles Details:")
                for i, visitor in enumerate(visitor_vehicles[:5], 1):  # Show first 5
                    print(f"\n   Visitor Vehicle #{i}:")
                    print(f"   - ID: {visitor.get('id')}")
                    print(f"   - Plate Number: {visitor.get('plateNumber')}")
                    print(f"   - Owner Name: {visitor.get('ownerName')}")
                    print(f"   - Contact: {visitor.get('contactNumber')}")
                    print(f"   - Visit Date: {visitor.get('visitDate')}")
                    print(f"   - Registered By: {visitor.get('registeredBy')}")
                    print(f"   - Dong/Ho: {visitor.get('dong')}/{visitor.get('ho')}")
                    print(f"   - Active: {visitor.get('isActive')}")
                    
                if len(visitor_vehicles) > 5:
                    print(f"\n   ... and {len(visitor_vehicles) - 5} more visitor vehicles")
            else:
                print("\n4. No visitor vehicles found in the response")
                
            # 5. Save full response for debugging
            with open('api_response_debug.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("\n5. Full response saved to api_response_debug.json")
                
        else:
            print(f"   Error: {comprehensive_response.text}")
    else:
        print(f"   Login failed: {login_response.text}")

if __name__ == "__main__":
    print(f"Testing server: {BASE_URL}")
    print(f"Test account: {USERNAME}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    asyncio.run(test_comprehensive_api())