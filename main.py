import streamlit as st
from utils.scraper import IGNDeepScraper
from utils.data_handler import process_scraped_data

st.set_page_config(page_title="IGN Deep Scraper", layout="wide")
st.title("🧵 IGN Deep Thread Scraper")

# Sidebar
forum_url = st.sidebar.text_input("Forum URL", "https://www.ignboards.com/forums/the-vestibule.5296/")
pages_to_index = st.sidebar.slider("Pages of Threads to Index", 1, 5, 1)
max_pages_per_thread = st.sidebar.slider("Max Pages per Thread", 1, 10, 2)

if st.sidebar.button("Run Deep Scrape"):
    scraper = IGNDeepScraper()
    
    # Step 1: Indexing
    with st.status("Phase 1: Indexing Threads...") as status:
        thread_list = scraper.get_thread_list(forum_url, pages_to_index)
        st.write(f"Found {len(thread_list)} threads.")
        
    # Step 2: Deep Scraping
    all_posts_map = {}
    progress_bar = st.progress(0)
    
    st.subheader("Phase 2: Extracting Posts")
    for i, thread in enumerate(thread_list):
        with st.empty():
            st.write(f"Scraping: {thread['title']}")
            posts = scraper.scrape_thread_posts(thread['url'], max_pages_per_thread)
            all_posts_map[thread['thread_id']] = posts
        
        progress_bar.progress((i + 1) / len(thread_list))
    
    # Step 3: Finalize
    df = process_scraped_data(thread_list, all_posts_map)
    st.success(f"Done! Collected {len(df)} total posts.")
    st.dataframe(df.head(100))
    
    st.download_button("Download Full CSV", df.to_csv(index=False), "ign_deep_scrape.csv", "text/csv")
