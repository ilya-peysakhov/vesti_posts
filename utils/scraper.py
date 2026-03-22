import requests
from bs4 import BeautifulSoup
import time
import random

class IGNDeepScraper:
    def __init__(self):
        self.session = requests.Session()
        # Updated to a very recent 2026 browser string
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/'
        })
        self.base_url = "https://www.ignboards.com"

    def get_thread_list(self, forum_url, num_pages=1):
        threads = []
        for p in range(1, num_pages + 1):
            url = f"{forum_url}page-{p}"
            resp = self.session.get(url, timeout=15)
            
            # DEBUG: If we get blocked, we'll see it here
            if resp.status_code != 200:
                print(f"Error {resp.status_code} on page {p}")
                continue
                
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Robust selector: Look for the 'structItem' div directly
            items = soup.select('div.structItem--thread')
            for item in items:
                # Look for the title link specifically in the title area
                title_link = item.select_one('div.structItem-title a[href*="threads/"]')
                if title_link:
                    threads.append({
                        'title': title_link.text.strip(),
                        'url': self.base_url + title_link['href'] if not title_link['href'].startswith('http') else title_link['href'],
                        'thread_id': title_link['href'].split('.')[-1].replace('/', '')
                    })
            
            time.sleep(random.uniform(0.5, 1.0))
        return threads

    def scrape_thread_posts(self, thread_url, max_thread_pages=2):
        all_posts = []
        current_page = 1
        
        while current_page <= max_thread_pages:
            resp = self.session.get(f"{thread_url}page-{current_page}", timeout=15)
            if resp.status_code != 200: break
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Robust Post Selector: XenForo uses 'article' tags for messages
            posts = soup.select('article.message--post, article.js-post')
            
            if not posts: # Fallback for newer XenForo versions
                posts = soup.find_all('article', {'data-content': True})

            for post in posts:
                author = post.get('data-author', 'Unknown')
                # Find the post body
                content_box = post.select_one('div.bbWrapper')
                content = content_box.get_text(separator=" ").strip() if content_box else ""
                
                if content: # Only add if we found text
                    all_posts.append({
                        'author': author,
                        'content': content,
                        'page': current_page
                    })
            
            # Improved Pagination Check
            next_link = soup.select_one('a.pageNav-jump--next, a.pageNav-button--next')
            if not next_link or current_page >= max_thread_pages:
                break
                
            current_page += 1
            time.sleep(random.uniform(0.3, 0.6))
            
        return all_posts
