import streamlit as st
import time
from utils.scraper import IGNDeepScraper
from utils.data_handler import process_scraped_data

st.set_page_config(page_title="IGN Deep Scraper", layout="wide")
st.title("🧵 IGN Deep Thread Scraper")

# Sidebar
forum_url = st.sidebar.text_input("Forum URL", "https://www.ignboards.com/forums/the-vestibule.5296/")
pages_to_index = st.sidebar.number_input("Pages of Threads to Index", 1, 99, 1)
max_pages_per_thread = st.sidebar.number_input("Max Pages per Thread", 1, 1000, 2)

if st.sidebar.button("🚀 Start Deep Scrape", type="primary"):
    scraper = IGNDeepScraper()
    all_posts_map = {}
    
    # --- PHASE 1: INDEXING ---
    with st.spinner("Phase 1: Indexing Threads...", show_time=True):
        thread_list = scraper.get_thread_list(forum_url, pages_to_index)
    
    st.success(f"Indexed {len(thread_list)} threads. Starting deep extraction...")

    # --- PHASE 2: DEEP SCRAPING ---
    progress_text = "Extracting posts from threads..."
    my_bar = st.progress(0, text=progress_text)
    
    # Persistent spinner for the whole scraping block
    with st.spinner("Scraping in progress... Please keep this tab open.", show_time=True):
        for i, thread in enumerate(thread_list):
            # The actual scrape call
            posts = scraper.scrape_thread_posts(thread['url'], max_pages_per_thread)
            all_posts_map[thread['thread_id']] = posts
            
            # Update progress bar
            percent_complete = (i + 1) / len(thread_list)
            my_bar.progress(percent_complete, text=f"Processing thread {i+1}/{len(thread_list)}: {thread['title'][:40]}...")

    # --- PHASE 3: FINALIZE ---
    df = process_scraped_data(thread_list, all_posts_map)
    st.balloons()
    st.success(f"Complete! Collected {len(df):,} total posts.")
    
    # Preview and Download
    st.dataframe(df.head(50), use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Full Dataset (CSV)",
        data=csv,
        file_name="ign_full_scrape.csv",
        mime="text/csv",
    )
