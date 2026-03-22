import requests
from bs4 import BeautifulSoup
import time
import random

class IGNDeepScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        })
        self.base_url = "https://www.ignboards.com"

    def get_thread_list(self, forum_url, num_pages=1):
        threads = []
        for p in range(1, num_pages + 1):
            try:
                url = f"{forum_url}page-{p}"
                resp = self.session.get(url, timeout=10)
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                items = soup.find_all('div', class_='structItem--thread')
                for item in items:
                    title_link = item.find('div', class_='structItem-title').find('a', href=True)
                    threads.append({
                        'title': title_link.text.strip(),
                        'url': self.base_url + title_link['href'],
                        'thread_id': title_link['href'].split('.')[-1].replace('/', '')
                    })
                # Lowered delay for indexing
                time.sleep(random.uniform(0.3, 0.7))
            except Exception:
                continue
        return threads

    def scrape_thread_posts(self, thread_url, max_thread_pages=2):
        all_posts = []
        current_page = 1
        
        while current_page <= max_thread_pages:
            try:
                url = f"{thread_url}page-{current_page}"
                resp = self.session.get(url, timeout=10)
                if resp.status_code != 200: break
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                posts = soup.find_all('article', class_='message--post')
                
                for post in posts:
                    # Clean extraction logic
                    author = post.get('data-author', 'Unknown')
                    content_div = post.find('div', class_='bbWrapper')
                    content = content_div.text.strip() if content_div else ""
                    
                    all_posts.append({
                        'author': author,
                        'content': content,
                        'page': current_page
                    })
                
                # Check for pagination
                if not soup.find('a', class_='pageNav-jump--next'):
                    break
                    
                current_page += 1
                # Aggressive delay for multi-page threads
                time.sleep(random.uniform(0.2, 0.5))
            except Exception:
                break
                
        return all_posts
