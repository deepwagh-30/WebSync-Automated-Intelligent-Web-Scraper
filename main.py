import streamlit as st
from components.results_display import display_results
from utils.scraper import scrape_multiple_urls
from utils.exporters import export_results

def set_custom_styles():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(120deg, #1a202c, #2d3748);
        color: #f7fafc;
    }
    .main-header {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        text-align: center;
        padding: 2rem 0 1rem;
        color: #ffffff;
        font-weight: 800;
        letter-spacing: -0.025em;
    }
    .header-subtitle {
        font-family: 'Inter', 'Segoe UI', sans-serif;
        text-align: center;
        color: #a0aec0;
        font-weight: 400;
        margin-bottom: 2rem;
        letter-spacing: 0.025em;
    }
    .url-input-container, .export-section, .stats-container, .options-container {
        background-color: rgba(45, 55, 72, 0.7);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
        border: 1px solid rgba(74, 85, 104, 0.3);
    }
    /* Fix Start Scraping button - no white */
    .button-primary > button {
        background: linear-gradient(90deg, #4c51bf, #6b46c1) !important;
        color: #f0e6ff !important; /* Light purple text */
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
    }
    .button-primary > button:hover, .button-primary > button:active, .button-primary > button:focus {
        background: linear-gradient(90deg, #5a67d8, #805ad5) !important;
        color: #f0e6ff !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
        transform: translateY(-1px) !important;
    }
    /* Force all regular buttons to use the same styling */
    button {
        background: linear-gradient(90deg, #4c51bf, #6b46c1) !important;
        color: #f0e6ff !important; /* Light purple text */
        border: none !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
    }
    button:hover, button:active, button:focus {
        background: linear-gradient(90deg, #5a67d8, #805ad5) !important;
        color: #f0e6ff !important;
    }
    .section-header {
        background: linear-gradient(90deg, #4c51bf, #6b46c1);
        color: #fff;
        padding: 1rem;
        border-radius: 8px;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        font-size: 0.85rem;
        color: #a0aec0;
    }
    .stText, .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {
        color: #f7fafc !important;
    }
    .stRadio > label, .stCheckbox > label {
        color: #f7fafc !important;
        font-weight: 500;
    }
    .stExpander > details > summary {
        color: #f7fafc !important;
        font-weight: 500;
        border-radius: 6px;
        background-color: rgba(74, 85, 104, 0.2);
        padding: 0.75rem 1rem;
    }
    .stExpander > details[open] > summary {
        border-bottom-left-radius: 0;
        border-bottom-right-radius: 0;
        border-bottom: 1px solid rgba(74, 85, 104, 0.3);
    }
    .stExpander > details > div {
        border: 1px solid rgba(74, 85, 104, 0.3);
        border-top: none;
        border-bottom-left-radius: 6px;
        border-bottom-right-radius: 6px;
        padding: 1rem;
    }
    .stProgress > div > div > div {
        background-color: #4c51bf !important;
    }
    .success {
        color: white !important;
        background-color: rgba(72, 187, 120, 0.7) !important;
        border-radius: 6px;
    }
    .stSuccess {
        color: white !important;
    }
    /* Fix Download buttons - No white! */
    .download-button > button, .stDownloadButton button {
        background: #2d3748 !important; /* Dark background */
        color: #90cdf4 !important; /* Light blue text */
        border: 1px solid #4c51bf !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
    }
    .download-button > button:hover, .stDownloadButton button:hover {
        background: #3c4a63 !important; /* Slightly lighter on hover */
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06) !important;
        transform: translateY(-1px) !important;
    }
    .stTextArea textarea {
        background-color: rgba(45, 55, 72, 0.5);
        color: #f7fafc;
        border: 1px solid rgba(74, 85, 104, 0.3);
        border-radius: 6px;
    }
    .stTextArea textarea:focus {
        border-color: #4c51bf;
        box-shadow: 0 0 0 1px #4c51bf;
    }
    /* Fixed Radio Button Styling for Export Format - with visible text */
    .stRadio > div {
        display: flex;
        justify-content: center;
        gap: 15px;
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
    }
    /* Fix text color inside radio buttons */
    .stRadio > div > label {
        flex: 1;
        background-color: #2d3748 !important;
        border: 2px solid #4a5568 !important;
        padding: 0.75rem 0 !important;
        border-radius: 8px !important;
        text-align: center !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        color: #f0e6ff !important; /* Light purple text - FIXED */
    }
    .stRadio > div > label:hover {
        background-color: #3c4a63 !important;
        border-color: #4c51bf !important;
        transform: translateY(-2px) !important;
    }
    /* Selected radio button styling - No white */
    .stRadio [data-testid="stRadio"] label[aria-checked="true"] {
        background: linear-gradient(90deg, #4c51bf, #6b46c1) !important;
        border-color: #6b46c1 !important;
        color: #e9d8fd !important; /* Light purple text */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    /* Target all text elements inside radio buttons to ensure visibility */
    .stRadio label span, .stRadio label p, .stRadio label div {
        color: #f0e6ff !important; /* Light purple text - FIXED */
    }
    /* Force radio button text color */
    .stRadio [data-testid="stMarkdownContainer"] p {
        color: #f0e6ff !important; /* Light purple text - FIXED */
    }
    /* Another target for radio button text */
    .stRadio [role="radiogroup"] label div {
        color: #f0e6ff !important; /* Light purple text - FIXED */
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(45, 55, 72, 0.5);
        border-radius: 6px;
        padding: 0.5rem 1rem;
        color: #f7fafc;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #4c51bf, #6b46c1);
        color: white !important;
        font-weight: 600;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f7fafc;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #a0aec0;
    }
    .stAlert {
        background-color: rgba(45, 55, 72, 0.7);
        border: 1px solid rgba(74, 85, 104, 0.3);
        color: #f7fafc;
    }
    .stAlert a {
        color: #90cdf4;
    }
    /* Additional radio button styling to ensure text visibility */
    .stRadio [data-baseweb="radio"] {
        color: #f0e6ff !important;
    }
    /* Target the actual option text specifically */
    .stRadio [data-baseweb="radio"] div[data-testid] {
        color: #f0e6ff !important;
    }
    .stRadio svg {
        fill: #f0e6ff !important;
    }
    /* Fix for any potential nested elements in radio buttons */
    .stRadio * {
        color: #f0e6ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Advanced Web Scraper",
        page_icon="apps.png",
        layout="wide"
    )
    
    # Apply custom styles
    set_custom_styles()
    
    # Header
    st.markdown('<h1 class="main-header">📡 WebSync Intelligence </h1>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Advanced Web scrapper that extracts and analyze information across Internet</p>', unsafe_allow_html=True)
    
    # Initialize session state for results if it doesn't exist
    if 'scraping_results' not in st.session_state:
        st.session_state.scraping_results = None
    
    # URL Input Section
    st.markdown('<div class="url-input-container">', unsafe_allow_html=True)
    st.markdown("### 🌐 Enter URLs to Scrape")
    
    # Text area for URLs
    url_input = st.text_area(
        "Enter one URL per line:",
        height=100,
        help="Enter the URLs you want to scrape, one per line"
    )
    
    # Extraction options
    st.markdown("### 🔧 Extraction Options")
    
    # Create columns for checkboxes
    col1, col2 = st.columns(2)
    
    # Define extraction options
    extract_options = {
        "Basic Info": col1.checkbox("Basic Information", value=True, help="Extract title, domain, etc."),
        "Content": col1.checkbox("Main Content", value=True, help="Extract and summarize page content"),
        "Contact": col2.checkbox("Contact Information", value=True, help="Extract emails, phones, social media"),
        "Stats": col2.checkbox("Page Statistics", value=True, help="Count paragraphs, links, images")
    }
    
    # Start scraping button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start_button = st.button("🚀 Start Scraping", key="start-scraping", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process URLs when button is clicked
    if start_button and url_input:
        # Split URLs
        urls = [url.strip() for url in url_input.split("\n") if url.strip()]
        
        if not urls:
            st.warning("Please enter at least one valid URL")
        else:
            # Create a progress bar
            st.markdown("### ⏳ Scraping Progress")
            progress_bar = st.progress(0)
            
            # Perform scraping
            results = scrape_multiple_urls(urls, progress_bar, extract_options)
            
            # Store results in session state
            st.session_state.scraping_results = results
            
            # Set progress to complete
            progress_bar.progress(1.0)
            st.success(f"✅ Successfully processed {len(urls)} URLs")
    
    # Display results if available
    if st.session_state.scraping_results:
        results = st.session_state.scraping_results
        
        # Display results
        display_results(results, extract_options)
        
        # Export section
        st.markdown('<div class="export-section">', unsafe_allow_html=True)
        st.markdown("### 📥 Export Results")
        
        # Export format options with custom inline styling for visibility
        st.markdown("""
        <style>
        /* Immediate fix for radio button text */
        .stRadio label span, .stRadio label div {
            color: #f0e6ff !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        export_format = st.radio(
            "Choose export format:",
            options=["CSV", "JSON", "Excel"],
            horizontal=True
        )
        
        # Export button
        export_col1, export_col2, export_col3 = st.columns([3, 2, 3])
        
        with export_col2:
            export_button = st.button("Export Results", key="export-button", use_container_width=True)
            
        if export_button:
            export_results(results, export_format)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer">
        Advanced Web Scraper App © 2025 | Built with Streamlit
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()