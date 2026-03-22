import pandas as pd

def process_scraped_data(thread_list, all_posts_map):
    """Combines thread info with their respective posts"""
    flattened = []
    for thread in thread_list:
        tid = thread['thread_id']
        posts = all_posts_map.get(tid, [])
        for p in posts:
            row = {**thread, **p}
            flattened.append(row)
    return pd.DataFrame(flattened)
