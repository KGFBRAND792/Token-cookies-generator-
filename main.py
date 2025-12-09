from flask import Flask, render_template, request
import sys
import os
import requests
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


app = Flask(__name__)

def get_headers(cookies):
    """Common headers for Facebook requests"""
    return {
        "authority": "www.facebook.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "cookie": cookies,
        "sec-ch-ua": '"Chromium";v="120", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

def get_eaad_token(cookies):
    """Extract EAAD full permission access token from Facebook Events Manager"""
    try:
        headers = get_headers(cookies)
        
        eaad_endpoints = [
            "https://www.facebook.com/events_manager2/overview",
            "https://www.facebook.com/events_manager/pixel",
            "https://business.facebook.com/events_manager2/overview",
            "https://www.facebook.com/events_manager/data_sources",
            "https://www.facebook.com/events_manager2/list/pixel",
            "https://www.facebook.com/adsmanager/manage/campaigns",
            "https://business.facebook.com/latest/home",
            "https://www.facebook.com/ajax/bootloader-endpoint/?modules=AdsLWIDescribeCustomersContainer.react",
            "https://www.facebook.com/business_locations",
            "https://business.facebook.com/business_locations",
        ]
        
        for endpoint in eaad_endpoints:
            try:
                resp = requests.get(endpoint, headers=headers, timeout=20, allow_redirects=True)
                patterns = [
                    r'{"accessToken":"(EAAD[A-Za-z0-9]+)"',
                    r'"accessToken":"(EAAD[A-Za-z0-9]+)"',
                    r'access_token=(EAAD[A-Za-z0-9]+)',
                    r'accessToken":"(EAAD[A-Za-z0-9]+)',
                    r'"token":"(EAAD[A-Za-z0-9]+)"',
                    r'(EAAD[A-Za-z0-9]{50,})',
                ]
                for pattern in patterns:
                    token_match = re.search(pattern, resp.text)
                    if token_match:
                        token = token_match.group(1)
                        if len(token) > 50:
                            return {"success": True, "token": token, "token_type": "EAAD"}
            except:
                continue
        
        return {"success": False, "error": "EAAD token extract nahi ho paya. Business Manager ya Events Manager access required hai."}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_all_tokens(cookies):
    """Extract all available access tokens (EAAD, EAAB, EAAG, etc.)"""
    try:
        headers = get_headers(cookies)
        tokens = {}
        
        fb_home = requests.get("https://www.facebook.com/", headers=headers, timeout=30)
        home_html = fb_home.text
        
        fb_dtsg_match = re.search(r'DTSGInitialData.*?"token":"([^"]+)"', home_html)
        fb_id_match = re.search(r'"actorID":"(\d+)"', home_html)
        
        if not fb_dtsg_match and not fb_id_match:
            if 'login' in fb_home.url.lower() or 'checkpoint' in fb_home.url.lower():
                return {"success": False, "error": "Cookies expired ya invalid hain. Please fresh cookies use karein."}
        
        fb_id = fb_id_match.group(1) if fb_id_match else None
        fb_dtsg = fb_dtsg_match.group(1) if fb_dtsg_match else None
        
        token_sources = [
            ("EAAD", [
                "https://www.facebook.com/events_manager2/overview",
                "https://www.facebook.com/events_manager/pixel",
                "https://business.facebook.com/events_manager2/overview",
            ]),
            ("EAAB", [
                "https://www.facebook.com/adsmanager/manage/campaigns",
                "https://business.facebook.com/content_management",
            ]),
            ("EAAG", [
                "https://business.facebook.com/business_locations",
                "https://business.facebook.com/settings",
            ]),
        ]
        
        for token_type, endpoints in token_sources:
            for endpoint in endpoints:
                try:
                    resp = requests.get(endpoint, headers=headers, timeout=15, allow_redirects=True)
                    pattern = rf'(?:"accessToken"|accessToken=)"?({token_type}\w+)"?'
                    token_match = re.search(pattern, resp.text)
                    if token_match and token_type not in tokens:
                        tokens[token_type] = token_match.group(1)
                        break
                    simple_pattern = rf'({token_type}[A-Za-z0-9]+)'
                    simple_match = re.search(simple_pattern, resp.text)
                    if simple_match and token_type not in tokens:
                        tokens[token_type] = simple_match.group(1)
                        break
                except:
                    continue
        
        if tokens:
            return {
                "success": True, 
                "tokens": tokens,
                "fb_id": fb_id,
                "fb_dtsg": fb_dtsg
            }
        
        if fb_dtsg or fb_id:
            return {"success": True, "tokens": {}, "fb_id": fb_id, "fb_dtsg": fb_dtsg, "cookies_valid": True}
        
        return {"success": False, "error": "Koi bhi token extract nahi ho paya. Please fresh cookies use karein."}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_token_from_cookies(cookies):
    """Extract EAAB access token from Facebook cookies"""
    try:
        headers = get_headers(cookies)
        
        fb_home = requests.get("https://www.facebook.com/", headers=headers, timeout=30)
        home_html = fb_home.text
        
        fb_dtsg_match = re.search(r'DTSGInitialData.*?"token":"([^"]+)"', home_html)
        fb_id_match = re.search(r'"actorID":"(\d+)"', home_html)
        
        if not fb_dtsg_match and not fb_id_match:
            if 'login' in fb_home.url.lower() or 'checkpoint' in fb_home.url.lower():
                return {"success": False, "error": "Cookies expired ya invalid hain. Please fresh cookies use karein."}
        
        fb_id = fb_id_match.group(1) if fb_id_match else None
        fb_dtsg = fb_dtsg_match.group(1) if fb_dtsg_match else None
        
        token_endpoints = [
            "https://business.facebook.com/content_management",
            "https://business.facebook.com/business_locations",
            "https://www.facebook.com/adsmanager/manage/campaigns",
            "https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed",
            "https://www.facebook.com/ajax/bootloader-endpoint/?modules=AdssppLiteManagerPage"
        ]
        
        for endpoint in token_endpoints:
            try:
                resp = requests.get(endpoint, headers=headers, timeout=15)
                token_match = re.search(r'(EAAB\w+)', resp.text)
                if token_match:
                    return {"success": True, "token": token_match.group(1), "fb_id": fb_id}
            except:
                continue
        
        if fb_dtsg or fb_id:
            return {"success": True, "token": None, "fb_dtsg": fb_dtsg, "fb_id": fb_id, "cookies_valid": True}
        
        return {"success": False, "error": "Cookies se data extract nahi ho paya. Please check karein."}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_user_id_from_cookies(cookies):
    """Extract user ID from cookies"""
    try:
        if 'c_user=' in cookies:
            return cookies.split('c_user=')[1].split(';')[0]
    except:
        pass
    return 'N/A'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    login_type = request.form.get('login_type', 'email')
    token_type = request.form.get('token_type', 'all')
    
    if login_type == 'cookie':
        cookies = request.form.get('cookies', '').strip()
        
        if not cookies:
            return render_template('result.html', 
                                 success=False, 
                                 error="Cookies required hain!")
        
        try:
            user_id = get_user_id_from_cookies(cookies)
            
            if token_type == 'eaad':
                token_result = get_eaad_token(cookies)
                if token_result.get('success'):
                    return render_template('result.html',
                                         success=True,
                                         access_token=token_result.get('token'),
                                         token_type='EAAD (Full Permission)',
                                         cookies=cookies,
                                         user_id=user_id,
                                         login_type='cookie')
                else:
                    return render_template('result.html',
                                         success=False,
                                         error=token_result.get('error', 'EAAD token extract nahi ho paya'))
            
            elif token_type == 'all':
                all_tokens_result = get_all_tokens(cookies)
                if all_tokens_result.get('success'):
                    tokens = all_tokens_result.get('tokens', {})
                    if tokens:
                        return render_template('result.html',
                                             success=True,
                                             all_tokens=tokens,
                                             cookies=cookies,
                                             user_id=user_id,
                                             login_type='cookie',
                                             show_all_tokens=True)
                    else:
                        return render_template('result.html',
                                             success=True,
                                             access_token="Cookies valid hain lekin tokens directly extract nahi ho paye. Aap manually try kar sakte hain.",
                                             cookies=cookies,
                                             user_id=user_id,
                                             cookies_valid=True,
                                             login_type='cookie')
                else:
                    return render_template('result.html',
                                         success=False,
                                         error=all_tokens_result.get('error', 'Tokens extract nahi ho paye'))
            
            else:
                token_result = get_token_from_cookies(cookies)
                if token_result.get('success'):
                    access_token = token_result.get('token')
                    if access_token:
                        return render_template('result.html',
                                             success=True,
                                             access_token=access_token,
                                             token_type='EAAB',
                                             cookies=cookies,
                                             user_id=user_id,
                                             login_type='cookie')
                    else:
                        return render_template('result.html',
                                             success=True,
                                             access_token="Cookies valid hain lekin EAAB token directly extract nahi ho paya.",
                                             cookies=cookies,
                                             user_id=user_id,
                                             cookies_valid=True,
                                             login_type='cookie')
                else:
                    return render_template('result.html',
                                         success=False,
                                         error=token_result.get('error', 'Token extract karne mein error aaya'))
                
        except Exception as e:
            return render_template('result.html',
                                 success=False,
                                 error=str(e))
    else:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        twofa = request.form.get('twofa', '').strip() or None
        login_method = request.form.get('login_method', 'mobile')
        
        if not username or not password:
            return render_template('result.html', 
                                 success=False, 
                                 error="Email/Phone aur Password dono required hain!")
        
        try:
            if login_method == 'web' or token_type == 'eaad':
                client = __facebookLoginV2.webLoginFB(username, password, twofa)
                result = client.login()
            else:
                client = __facebookLoginV2.loginFB(username, password, twofa)
                result = client.main()
            
            if result.get('success') is not None:
                login_cookies = result['success']['setCookies']
                login_token = result['success']['accessTokenFB']
                login_user_id = login_cookies.split('c_user=')[1].split(';')[0] if 'c_user=' in login_cookies else 'N/A'
                
                if token_type == 'eaad' or token_type == 'all':
                    eaad_result = get_eaad_token(login_cookies)
                    all_result = get_all_tokens(login_cookies)
                    
                    all_tokens = all_result.get('tokens', {}) if all_result.get('success') else {}
                    if login_token and login_token.startswith('EAA'):
                        token_prefix = login_token[:4]
                        if token_prefix not in all_tokens:
                            all_tokens[token_prefix] = login_token
                    
                    if eaad_result.get('success') and 'EAAD' not in all_tokens:
                        all_tokens['EAAD'] = eaad_result.get('token')
                    
                    if all_tokens:
                        return render_template('result.html',
                                             success=True,
                                             all_tokens=all_tokens,
                                             cookies=login_cookies,
                                             user_id=login_user_id,
                                             login_type='email',
                                             show_all_tokens=True)
                
                return render_template('result.html',
                                     success=True,
                                     access_token=login_token,
                                     token_type='Login Token',
                                     cookies=login_cookies,
                                     user_id=login_user_id,
                                     login_type='email')
            else:
                error_msg = result.get('error', {}).get('description', 'Unknown error occurred')
                return render_template('result.html',
                                     success=False,
                                     error=error_msg)
        except Exception as e:
            return render_template('result.html',
                                 success=False,
                                 error=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
