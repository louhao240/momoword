import requests
import sys


API_BASE_URL = "https://open.maimemo.com/open/api/v1/notepads"

class Momo:
    def __init__(self, token, notepad_name):
        self.token = f"Bearer {token}"  # 使用f-string格式化
        self.notepad_name = notepad_name
        self.headers = {  # 统一headers定义
            "Accept": "application/json",
            "Authorization": self.token
        }

    def find_notepads(self) -> str:
        '''查找云词库，返回词库ID或空字符串'''
        querystring = {"limit": "0", "offset": "0"}
        response = requests.get(API_BASE_URL, headers=self.headers, params=querystring)
        response.raise_for_status()  # 添加HTTP状态检查
        
        for notepad in response.json()["data"]["notepads"]:
            if notepad["title"] == self.notepad_name:
                return notepad["id"]
        return ""

    def create_notepad(self) -> str:
        '''创建词库并返回新词库ID'''
        payload = {
            "notepad": {
                "status": "PUBLISHED",
                "content": "test",
                "title": self.notepad_name,
                "brief": " ",
                "tags": [" "]
            }
        }
        
        try:
            response = requests.post(
                API_BASE_URL,
                json=payload,
                headers={**self.headers, "Content-Type": "application/json"}
            )
            response.raise_for_status()
            if response.json().get('success'):
                return response.json()['data']['notepad']['id']
            return ""
        except Exception as e:
            raise RuntimeError(f"创建词库失败: {str(e)}")

    def get_notepad(self, id: str) -> list:
        '''获取词库单词列表'''
        try:
            response = requests.get(f"{API_BASE_URL}/{id}", headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            return [
                item['word'] 
                for item in data['data']['notepad']['list'] 
                if item['type'] == 'WORD'
            ]
        except (requests.RequestException, KeyError):
            return []

    def add_word(self, id: str, words: list) -> bool:
        '''添加单词，返回操作是否成功'''
        content = ",".join(words) if isinstance(words, list) else str(words)
        
        payload = {
            "notepad": {
                "status": "PUBLISHED",
                "content": content,
                "title": self.notepad_name,
                "brief": " ",
                "tags": [" "]
            }
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/{id}",
                json=payload,
                headers={**self.headers, "Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json().get('success', False)
        except requests.RequestException:
            return False

    def sync_words(self, words: list) -> bool:
        """同步单词到词库（增量更新）"""
        notepad_id = self.find_notepads()
        if not notepad_id:
            notepad_id = self.create_notepad()
        
        existing_words = set(self.get_notepad(notepad_id))
        # 合并原有单词和新单词
        combined_words = list(existing_words.union(set(words)))
        
        # 只有当有新单词需要添加时才更新
        if len(combined_words) == len(existing_words):
            return False
            
        content = ",".join(combined_words)
        return self._update_notepad_content(notepad_id, content)

    def _update_notepad_content(self, notepad_id: str, content: str) -> bool:
        """内部方法：更新词库内容"""
        payload = {
            "notepad": {
                "status": "PUBLISHED",
                "content": content,
                "title": self.notepad_name,
                "brief": " ",
                "tags": [" "]
            }
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/{notepad_id}",
                json=payload,
                headers={**self.headers, "Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json().get('success', False)
        except Exception as e:
            raise RuntimeError(f"更新词库失败: {str(e)}")



