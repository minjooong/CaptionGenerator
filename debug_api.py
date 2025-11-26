import requests
import json

def check_grammar(text):
    base_url = 'https://m.search.naver.com/p/csearch/ocontent/util/SpellerProxy'
    payload = {
        'q': text,
        'color_blindness': 0
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }
    
    try:
        response = requests.get(base_url, params=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Raw Response: {response.text[:500]}...") # Print first 500 chars
        
        data = json.loads(response.text)
        print("JSON Keys:", data.keys())
        if 'message' in data:
             print("Message Keys:", data['message'].keys())
             if 'result' in data['message']:
                 print("Result Keys:", data['message']['result'].keys())
                 print("HTML:", data['message']['result']['html'])
                 
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_grammar("맞춤법틀리면외않되?")
