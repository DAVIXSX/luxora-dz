#!/usr/bin/env python3
"""
Test script to demonstrate the product requests API
Run this while your Flask app is running to test the API endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"

def test_submit_product_request():
    """Test submitting a product request via API"""
    print("🧪 Testing Product Request Submission API...")
    
    # Sample product request data
    request_data = {
        "product_id": 1,  # Make sure this product exists in your database
        "user_name": "أحمد علي",
        "email": "ahmed@example.com",
        "phone": "+213555123456",
        "state": "الجزائر العاصمة",
        "address": "شارع الشهداء، حي المقريا",
        "quantity": 2,
        "message": "أريد معرفة المزيد عن هذا المنتج والأسعار المتاحة"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/product-requests",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        response_data = response.json()
        print(f"Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 201:
            print("✅ Product request submitted successfully!")
            return response_data.get('request_id')
        else:
            print("❌ Failed to submit product request")
            return None
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return None

def test_get_all_requests():
    """Test getting all product requests (requires admin login)"""
    print("\n🧪 Testing Get All Requests API...")
    print("Note: This requires admin session, so it might fail if not logged in via browser")
    
    try:
        response = requests.get(f"{BASE_URL}/api/product-requests")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Number of requests: {response_data.get('count', 0)}")
            print("✅ Successfully retrieved requests list")
        else:
            print("❌ Failed to get requests (probably need admin login)")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def test_update_request_status(request_id):
    """Test updating request status"""
    if not request_id:
        print("\n⚠️ Skipping status update test - no request ID available")
        return
        
    print(f"\n🧪 Testing Update Request Status API for request {request_id}...")
    
    status_data = {"status": "approved"}
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/product-requests/{request_id}",
            json=status_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            print("✅ Status updated successfully!")
        else:
            print("❌ Failed to update status (probably need admin login)")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def check_server_status():
    """Check if the Flask server is running"""
    print("🔍 Checking if Flask server is running...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Flask server is running!")
            return True
        else:
            print("❌ Flask server returned unexpected status")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server. Make sure it's running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 PRODUCT REQUESTS API TEST SUITE")
    print("=" * 60)
    
    # Check if server is running
    if not check_server_status():
        print("\n💡 To run the server:")
        print("   python app.py")
        return
    
    print("\n" + "=" * 60)
    
    # Test product request submission
    request_id = test_submit_product_request()
    
    # Test getting all requests
    test_get_all_requests()
    
    # Test status update
    test_update_request_status(request_id)
    
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    print("1. ✅ Product request submission API tested")
    print("2. ⚠️  Get all requests API tested (may need admin session)")
    print("3. ⚠️  Update status API tested (may need admin session)")
    print("\n💡 To test admin APIs fully:")
    print("   1. Open browser and go to http://localhost:5000/login")
    print("   2. Login with: youcef / kadari")
    print("   3. Visit http://localhost:5000/admin/requests")
    print("   4. Use the interface to manage requests")
    
    print("\n🔗 USEFUL ENDPOINTS:")
    print("   • Main site: http://localhost:5000")
    print("   • Admin panel: http://localhost:5000/admin")
    print("   • Product requests: http://localhost:5000/admin/requests")
    print("   • API endpoint: http://localhost:5000/api/product-requests")

if __name__ == "__main__":
    main()
