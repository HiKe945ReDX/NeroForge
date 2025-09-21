#!/usr/bin/env python3
"""Test script for Guidora services"""

import asyncio
import httpx
import json

async def test_services():
    """Test all services are working"""
    
    services = {
        "Career Atlas": "http://localhost:5002/api/v1/health",
        "User Service": "http://localhost:5007/health"
    }
    
    async with httpx.AsyncClient() as client:
        for name, url in services.items():
            try:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"✅ {name}: HEALTHY")
                else:
                    print(f"❌ {name}: ERROR ({response.status_code})")
            except Exception as e:
                print(f"❌ {name}: CONNECTION FAILED - {str(e)}")
    
    # Test user registration
    try:
        register_response = await client.post(
            "http://localhost:5007/auth/register",
            json={
                "email": f"test_{int(asyncio.get_event_loop().time())}@guidora.com",
                "password": "secure123",
                "full_name": "Test User"
            }
        )
        
        if register_response.status_code == 201:
            print("✅ User Registration: WORKING")
            
            # Test login
            data = register_response.json()
            login_response = await client.post(
                "http://localhost:5007/auth/login",
                json={
                    "email": data["user"]["email"],
                    "password": "secure123"
                }
            )
            
            if login_response.status_code == 200:
                print("✅ User Login: WORKING")
                
                # Test profile access
                token = login_response.json()["access_token"]
                profile_response = await client.get(
                    "http://localhost:5007/users/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if profile_response.status_code == 200:
                    print("✅ User Profile Access: WORKING")
                else:
                    print(f"❌ User Profile Access: ERROR ({profile_response.status_code})")
            else:
                print(f"❌ User Login: ERROR ({login_response.status_code})")
        else:
            print(f"❌ User Registration: ERROR ({register_response.status_code})")
    
    except Exception as e:
        print(f"❌ User Service Test: FAILED - {str(e)}")

if __name__ == "__main__":
    print("🚀 TESTING GUIDORA SERVICES")
    print("=" * 40)
    asyncio.run(test_services())
    print("=" * 40)
    print("🏁 TEST COMPLETED")
