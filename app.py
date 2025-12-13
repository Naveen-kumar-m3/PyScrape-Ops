import streamlit as st
from pyscrape_ops.scraper import Scraper
from pyscrape_ops.processor import process
from pyscrape_ops.exporter import export_to_excel

st.set_page_config(
    page_title="PyScrape Ops",
    page_icon="🌐",
    layout="centered"
)

# Header
st.markdown(
    """
    <h1 style='text-align:center;'>🌐 PyScrape Ops</h1>
    <p style='text-align:center;color:#9BA1A6;'>
    Web Scraping Automation Platform
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# Input section
st.markdown("### 🔗 Enter Website URL")
url = st.text_input(
    "",
    placeholder="https://example.com"
)

# Action
if st.button("🚀 Scrape Website", use_container_width=True):
    if not url.startswith("http"):
        st.error("Please enter a valid URL starting with http or https")
    else:
        with st.spinner("Scraping website..."):
            try:
                scraper = Scraper()
                raw_data = scraper.scrape(url)

                if not raw_data:
                    st.warning("No content found on this page.")
                else:
                    df = process(raw_data)
                    file_path = export_to_excel(df, "scraped_data.xlsx")

                    st.success("Scraping completed successfully 🎉")

                    st.markdown("### 📊 Preview (Top Rows)")
                    st.dataframe(df.head(20), use_container_width=True)

                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="⬇ Download Excel File",
                            data=f,
                            file_name="scraped_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )

            except Exception as e:
                st.error(f"Error occurred: {e}")

# Footer
st.divider()
st.markdown(
    "<p style='text-align:center;color:#6B7280;'>Built with Python • Streamlit • BeautifulSoup</p>",
    unsafe_allow_html=True
)
