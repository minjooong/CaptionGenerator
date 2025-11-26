import requests
import re
import json
import time
from collections import namedtuple

CheckedResult = namedtuple('CheckedResult', ['result', 'original', 'checked', 'errors', 'words', 'time'])

class HanspellClient:
    def __init__(self):
        self.base_url = 'https://m.search.naver.com/p/csearch/ocontent/util/SpellerProxy'
        self.passport_key = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }

    def _get_passport_key(self):
        if self.passport_key:
            return self.passport_key
            
        url = 'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query=맞춤법검사기'
        try:
            res = requests.get(url, headers=self.headers)
            match = re.search(r'passportKey=([a-zA-Z0-9]+)', res.text)
            if match:
                self.passport_key = match.group(1)
                return self.passport_key
        except Exception as e:
            print(f"Error getting passport key: {e}")
        return None

    def check(self, text):
        key = self._get_passport_key()
        if not key:
            return CheckedResult(False, text, text, 0, {}, 0)

        payload = {
            'q': text,
            'color_blindness': 0,
            'passportKey': key
        }
        
        try:
            start_time = time.time()
            response = requests.get(self.base_url, params=payload, headers=self.headers)
            data = json.loads(response.text)
            
            if 'message' in data and 'result' in data['message']:
                result = data['message']['result']
                html = result['html']
                checked_text = result['notag_html']
                # Simple parsing, we just want the corrected text mostly
                # But let's try to be compatible with py-hanspell structure if needed
                # For now, just return the corrected text in the named tuple
                
                return CheckedResult(True, text, checked_text, result['errata_count'], {}, time.time() - start_time)
            
        except Exception as e:
            print(f"Error checking grammar: {e}")
            
        return CheckedResult(False, text, text, 0, {}, 0)

# Singleton instance
hanspell = HanspellClient()
