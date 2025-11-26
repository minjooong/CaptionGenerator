import requests
import re
import json
import time

def get_passport_key():
    url = 'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query=맞춤법검사기'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }
    res = requests.get(url, headers=headers)
    match = re.search(r'passportKey=([a-zA-Z0-9]+)', res.text)
    if match:
        return match.group(1)
    return None

def check_grammar(text):
    key = get_passport_key()
    if not key:
        print("Failed to get passport key")
        return

    base_url = 'https://m.search.naver.com/p/csearch/ocontent/util/SpellerProxy'
    payload = {
        'q': text,
        'color_blindness': 0,
        'passportKey': key
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }
    
    try:
        response = requests.get(base_url, params=payload, headers=headers)
        data = json.loads(response.text)
        print("Response:", data)
        if 'message' in data and 'result' in data['message']:
            print("Corrected HTML:", data['message']['result']['html'])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_grammar("맞춤법틀리면외않되?")
