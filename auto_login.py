import requests
import json
import urllib.parse
import sys

# Constants
BASE_URL = "http://210.27.177.172/eportal/InterFace.do"
LOGIN_URL = f"{BASE_URL}?method=login"
LOGOUT_URL = f"{BASE_URL}?method=logout"
STATUS_URL = f"{BASE_URL}?method=getOnlineUserInfo"

# Headers
DEFAULT_HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,ja;q=0.5,zh-TW;q=0.4',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': '210.27.177.172',
    'Origin': 'http://210.27.177.172',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
}

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please create it with your credentials.")
        sys.exit(1)

def get_status():
    """Get current online user information"""
    try:
        response = requests.get(STATUS_URL, headers=DEFAULT_HEADERS)
        result = response.json()
        if result.get("result") == "success":
            return result
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting status: {e}")
        return None

def get_cookies(user_id, password):
    """Generate cookies for login request"""
    cookies = {
        'EPORTAL_COOKIE_SAVEPASSWORD': 'true',
        'EPORTAL_COOKIE_NEWV': 'true',
        'EPORTAL_AUTO_LAND': '',
        'EPORTAL_COOKIE_DOMAIN': 'undefined',
        'EPORTAL_COOKIE_OPERATORPWD': '',
        'EPORTAL_COOKIE_USERNAME': user_id,
        'EPORTAL_COOKIE_PASSWORD': password,
        'EPORTAL_COOKIE_SERVER': urllib.parse.quote('校园移动'),
        'EPORTAL_COOKIE_SERVER_NAME': urllib.parse.quote('校园移动'),
        'EPORTAL_USER_GROUP': urllib.parse.quote('本科生组')
    }
    return cookies

def login(user_id, password, query_string, service="校园移动"):
    """Attempt to login to the campus network"""
    data = {
        'userId': user_id,
        'password': password,
        'service': service,
        'queryString': query_string,
        'operatorPwd': '',
        'operatorUserId': '',
        'validcode': '',
        'passwordEncrypt': 'true'
    }

    try:
        cookies = get_cookies(user_id, password)
        response = requests.post(
            LOGIN_URL,
            data=data,
            headers=DEFAULT_HEADERS,
            cookies=cookies
        )
        result = response.json()
        print(f"Login Response: {result}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error during login request: {e}")
        return None

def logout():
    """Logout from the campus network using current session's userIndex"""
    status = get_status()
    if not status or not status.get("userIndex"):
        print("Error: Could not get current user index. Are you logged in?")
        return None

    try:
        data = {
            'userIndex': status["userIndex"]
        }
        response = requests.post(LOGOUT_URL, data=data, headers=DEFAULT_HEADERS)
        result = response.json()
        print(f"Logout Response: {status}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error during logout request: {e}")
        return None

def main():
    """Main function to handle login/logout operations"""
    config = load_config()
    
    if len(sys.argv) < 2:
        print("Usage: python auto_login.py [login|logout]")
        action = "login"
    else:
        action = sys.argv[1].lower()
    
    if action == "login":
        result = login(
            config['userId'],
            config['password'],
            config['queryString'],
            config.get('service', '校园移动')
        )
        if result:
            print("Login operation completed.")
    elif action == "logout":
        result = logout()
        if result:
            print("Logout operation completed.")
    else:
        print("Invalid action. Use 'login' or 'logout'")

if __name__ == "__main__":
    main()