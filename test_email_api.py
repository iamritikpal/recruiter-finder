#!/usr/bin/env python3
"""
Test script for the email guessing API endpoint
"""
import requests
import json

def test_email_api():
    url = "http://localhost:5000/api/guess_emails"
    
    test_cases = [
        {
            "first_name": "John",
            "last_name": "Smith", 
            "domain": "google.com"
        },
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "domain": "microsoft.com"
        },
        {
            "first_name": "Test",
            "last_name": "User",
            "domain": "natwest.com"
        }
    ]
    
    print("Testing Email Guessing API")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['first_name']} {test_case['last_name']} @ {test_case['domain']}")
        print("-" * 30)
        
        try:
            response = requests.post(url, json=test_case, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success!")
                print(f"   Domain: {data.get('domain', 'N/A')}")
                print(f"   Valid emails: {len(data.get('valid_emails', []))}")
                print(f"   Patterns tested: {data.get('total_patterns_tested', 'N/A')}")
                print(f"   MX hosts found: {data.get('mx_hosts_found', 'N/A')}")
                
                if data.get('valid_emails'):
                    print("   Found emails:")
                    for email in data['valid_emails']:
                        print(f"     - {email}")
                else:
                    print("   No valid emails found")
                    
            else:
                print(f"❌ Error {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Message: {error_data.get('message', 'Unknown error')}")
                    if 'alternatives_tried' in error_data:
                        print(f"   Alternatives tried: {error_data['alternatives_tried']}")
                except:
                    print(f"   Response: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            print("   Make sure the Flask server is running on http://localhost:5000")

if __name__ == "__main__":
    test_email_api() 