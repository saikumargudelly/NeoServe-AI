"""
NeoServe AI Test Script

This script tests the NeoServe AI API endpoints and verifies their functionality.
"""
import os
import sys
import time
import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8001/api/v1"
TEST_USERS = {
    "customer": {
        "email": "customer1@example.com",
        "password": "password123"
    },
    "agent": {
        "email": "agent1@example.com",
        "password": "password123"
    }
}

class TestRunner:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_type = None
        self.test_results = []
        self.session_id = f"test-session-{int(time.time())}"
    
    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result with timestamp."""
        result = {
            "test": name,
            "status": "PASS" if success else "FAIL",
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        status = "\033[92mPASS\033[0m" if success else "\033[91mFAIL\033[0m"
        print(f"[{status}] {name}")
        if details and not success:
            print(f"   Details: {details}")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        total = len(self.test_results)
        
        print(f"Tests Run: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed < total:
            print("\nFailed Tests:")
            for test in self.test_results:
                if test["status"] == "FAIL":
                    print(f"- {test['test']}: {test.get('details', 'No details')}")
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with auth token if available."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def test_authentication(self, user_type: str) -> bool:
        """Test user authentication."""
        self.user_type = user_type
        user = TEST_USERS[user_type]
        
        try:
            # Test login
            response = self.session.post(
                f"{BASE_URL}/auth/token",
                data={"username": user["email"], "password": user["password"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code != 200:
                self.log_test("Authentication", False, f"Login failed: {response.text}")
                return False
            
            self.token = response.json().get("access_token")
            if not self.token:
                self.log_test("Authentication", False, "No access token in response")
                return False
            
            self.log_test("Authentication", True)
            return True
            
        except Exception as e:
            self.log_test("Authentication", False, str(e))
            return False
    
    def test_user_profile(self) -> bool:
        """Test getting user profile."""
        try:
            response = self.session.get(
                f"{BASE_URL}/auth/me",
                headers=self.get_headers()
            )
            
            if response.status_code != 200:
                self.log_test("Get User Profile", False, f"Failed: {response.text}")
                return False
            
            profile = response.json()
            if not profile.get("email"):
                self.log_test("Get User Profile", False, "Invalid profile data")
                return False
            
            self.log_test("Get User Profile", True, f"User: {profile['email']}")
            return True
            
        except Exception as e:
            self.log_test("Get User Profile", False, str(e))
            return False
    
    def test_chat(self) -> bool:
        """Test chat functionality."""
        test_messages = [
            "Hello, how are you?",
            "What services do you offer?",
            "I need help with my account"
        ]
        
        all_success = True
        
        for i, message in enumerate(test_messages, 1):
            try:
                response = self.session.post(
                    f"{BASE_URL}/chat",
                    json={
                        "message": message,
                        "session_id": self.session_id
                    },
                    headers=self.get_headers()
                )
                
                if response.status_code != 200:
                    self.log_test(
                        f"Chat Message {i}", 
                        False, 
                        f"Failed: {response.status_code} - {response.text}"
                    )
                    all_success = False
                    continue
                
                response_data = response.json()
                self.log_test(
                    f"Chat Message {i}", 
                    True, 
                    f"You: {message}\n   Bot: {response_data.get('response', 'No response')}"
                )
                
            except Exception as e:
                self.log_test(f"Chat Message {i}", False, str(e))
                all_success = False
        
        return all_success
    
    def test_chat_history(self) -> bool:
        """Test retrieving chat history."""
        try:
            response = self.session.get(
                f"{BASE_URL}/chat/history/{self.session_id}",
                headers=self.get_headers()
            )
            
            if response.status_code != 200:
                self.log_test("Get Chat History", False, f"Failed: {response.text}")
                return False
            
            history = response.json()
            if not isinstance(history, list):
                self.log_test("Get Chat History", False, "Invalid history format")
                return False
            
            self.log_test("Get Chat History", True, f"Found {len(history)} messages")
            return True
            
        except Exception as e:
            self.log_test("Get Chat History", False, str(e))
            return False
    
    def test_system_status(self) -> bool:
        """Test system status endpoint."""
        try:
            response = self.session.get(
                f"{BASE_URL}/chat/status",
                headers=self.get_headers()
            )
            
            if response.status_code != 200:
                self.log_test("System Status", False, f"Failed: {response.text}")
                return False
            
            status_data = response.json()
            self.log_test(
                "System Status", 
                True, 
                f"Status: {status_data.get('status', 'unknown')}"
            )
            return True
            
        except Exception as e:
            self.log_test("System Status", False, str(e))
            return False

def run_tests(user_type: str = "customer"):
    """Run all tests for the specified user type."""
    print(f"\n{'='*50}")
    print(f"RUNNING TESTS AS {user_type.upper()}")
    print("="*50)
    
    tester = TestRunner()
    
    # Run tests in sequence
    if tester.test_authentication(user_type):
        tester.test_user_profile()
        tester.test_chat()
        tester.test_chat_history()
        tester.test_system_status()
    
    # Print summary
    tester.print_summary()
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{user_type}_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(tester.test_results, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")

if __name__ == "__main__":
    # Run tests for customer by default
    user_type = sys.argv[1] if len(sys.argv) > 1 else "customer"
    run_tests(user_type)
