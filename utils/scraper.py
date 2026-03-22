import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd

class IGNDeepScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.base_url = "https://www.ignboards.com"

    def get_thread_list(self, forum_url, num_pages=1):
        """Pass 1: Collect thread URLs and basic metadata"""
        threads = []
        for p in range(1, num_pages + 1):
            url = f"{forum_url}page-{p}"
            resp = self.session.get(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            items = soup.find_all('div', class_='structItem--thread')
            for item in items:
                title_link = item.find('div', class_='structItem-title').find('a', href=True)
                threads.append({
                    'title': title_link.text.strip(),
                    'url': self.base_url + title_link['href'],
                    'thread_id': title_link['href'].split('.')[-1].replace('/', '')
                })
            time.sleep(random.uniform(1, 2))
        return threads

    def scrape_thread_posts(self, thread_url, max_thread_pages=3):
        """Pass 2: Visit a specific thread and scrape all posts across pages"""
        all_posts = []
        current_page = 1
        
        while current_page <= max_thread_pages:
            url = f"{thread_url}page-{current_page}"
            resp = self.session.get(url)
            if resp.status_code != 200: break
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            posts = soup.find_all('article', class_='message--post')
            
            for post in posts:
                author = post.get('data-author', 'Unknown')
                content = post.find('div', class_='bbWrapper').text.strip()
                post_id = post.get('data-content', '')
                
                all_posts.append({
                    'author': author,
                    'content': content,
                    'post_id': post_id,
                    'page': current_page
                })
            
            # Check if there's a "Next" page
            if not soup.find('a', class_='pageNav-jump--next'):
                break
                
            current_page += 1
            time.sleep(random.uniform(0.5, 1.5))
            
        return all_posts
