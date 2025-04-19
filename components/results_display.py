import streamlit as st
import pandas as pd
import plotly.express as px
def display_results(results, extract_options):
    """Display scraping results in an attractive format"""
    if not results:
        return
    
    try:
        # Summary stats
        st.markdown("""
        <div class="section-header">
            <h2>📊 Scraping Results Summary</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Calculate success rate
        total_urls = len(results)
        successful = sum(1 for r in results if "error" not in r)
        
        # Stats container
        st.markdown('<div class="stats-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total URLs", total_urls)
        col2.metric("Successfully Scraped", successful)
        col3.metric("Success Rate", f"{int(successful/total_urls*100)}%" if total_urls > 0 else "0%")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Data visualization if we have successful results
        if successful > 0:
            create_visualizations(results)
        
        # Individual results
        st.markdown("""
        <div class="section-header">
            <h2>🔍 Detailed Results</h2>
        </div>
        """, unsafe_allow_html=True)
        
        for i, result in enumerate(results):
            with st.expander(f"📄 {result.get('title', result.get('url', f'Result {i+1}'))}"):
                if "error" in result:
                    st.error(result["error"])
                    continue
                
                # Custom tab styling with CSS
                st.markdown("""
                <style>
                .stTabs [data-baseweb="tab-list"] {
                    gap: 8px;
                }
                .stTabs [data-baseweb="tab"] {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 8px 16px;
                    color: white;
                    transition: all 0.3s ease;
                }
                .stTabs [aria-selected="true"] {
                    background: linear-gradient(90deg, #00b09b, #96c93d);
                    color: white !important;
                    font-weight: bold;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Display in tabs
                tab1, tab2, tab3 = st.tabs(["Overview", "Content", "Contact"])
                
                with tab1:
                    if extract_options["Basic Info"]:
                        st.markdown(f"""
                        ### Basic Information
                        **URL:** <a href="{result['url']}" target="_blank">{result['url']}</a>  
                        **Domain:** {result.get('domain', 'N/A')}  
                        **Title:** {result.get('title', 'N/A')}  
                        **Description:** {result.get('description', 'N/A')}
                        """, unsafe_allow_html=True)
                    
                    if extract_options["Stats"]:
                        st.markdown("### Page Statistics")
                        stat_cols = st.columns(3)
                        stat_cols[0].metric("Paragraphs", result.get('paragraph_count', 'N/A'))
                        stat_cols[1].metric("Links", result.get('link_count', 'N/A'))
                        stat_cols[2].metric("Images", result.get('image_count', 'N/A'))
                    
                    # Add a section for links found
                    if extract_options["Stats"] and result.get('link_count', 0) > 0:
                        st.markdown("### 🔗 Found Links")
                        if 'found_links' in result and result['found_links']:
                            for idx, link in enumerate(result['found_links'][:10]):  # Show first 10 links
                                st.markdown(f"<a href='{link}' target='_blank'>{link}</a>", unsafe_allow_html=True)
                            if len(result['found_links']) > 10:
                                st.info(f"{len(result['found_links']) - 10} more links found")
                        else:
                            st.info("No links details available")
                    
                    # Add a section for images found
                    if extract_options["Stats"] and result.get('image_count', 0) > 0:
                        st.markdown("### 🖼️ Found Images")
                        if 'found_images' in result and result['found_images']:
                            image_cols = st.columns(3)
                            for idx, img_src in enumerate(result['found_images'][:6]):  # Show first 6 images
                                if idx < 6:  # Limit to first 6 images
                                    with image_cols[idx % 3]:
                                        st.markdown(f"<img src='{img_src}' style='max-width:100%; border-radius:4px;'>", unsafe_allow_html=True)
                            if len(result['found_images']) > 6:
                                st.info(f"{len(result['found_images']) - 6} more images found")
                        else:
                            st.info("No image details available")
                
                with tab2:
                    if extract_options["Content"]:
                        st.markdown("### Main Content Preview")
                        st.markdown("""
                        <div style="max-height: 300px; overflow-y: auto; background-color: rgba(255, 255, 255, 0.9); 
                        color: #333; padding: 1rem; border-radius: 8px; border: 1px solid #E5E7EB;">
                        """, unsafe_allow_html=True)
                        st.markdown(result.get('main_content', 'No content extracted'))
                        st.markdown("</div>", unsafe_allow_html=True)
                
                with tab3:
                    if extract_options["Contact"]:
                        st.markdown("### Contact Information")
                        
                        # Emails
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 📧 Emails")
                            if result.get('emails'):
                                for email in result['emails']:
                                    st.markdown(f"""
                                    <div style="background-color: rgba(240, 249, 255, 0.8); color: #333; padding: 0.5rem; 
                                    border-radius: 4px; margin-bottom: 0.5rem; border: 1px solid #D1D5DB;">
                                    {email}
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("No emails found")
                        
                        with col2:
                            st.markdown("#### 📞 Phone Numbers")
                            if result.get('phones'):
                                for phone in result['phones']:
                                    st.markdown(f"""
                                    <div style="background-color: rgba(240, 249, 255, 0.8); color: #333; padding: 0.5rem; 
                                    border-radius: 4px; margin-bottom: 0.5rem; border: 1px solid #D1D5DB;">
                                    {phone}
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("No phone numbers found")
                        
                        # Social Media
                        st.markdown("#### 🌐 Social Media")
                        if result.get('social_media'):
                            social_cols = st.columns(4)
                            for i, (platform, handle) in enumerate(result['social_media'].items()):
                                social_cols[i % 4].markdown(f"""
                                <div style="background-color: rgba(240, 249, 255, 0.8); color: #333; padding: 0.5rem; 
                                border-radius: 4px; margin-bottom: 0.5rem; border: 1px solid #D1D5DB;">
                                <strong>{platform.capitalize()}:</strong> {handle}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No social media profiles found")
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")

def create_visualizations(results):
    """Create data visualizations from the scraping results"""
    # Filter out results with errors
    valid_results = [r for r in results if "error" not in r]
    
    if not valid_results:
        return
    
    st.markdown("""
    <div class="section-header">
        <h2>📈 Data Visualizations</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Create a DataFrame for visualization
    df = pd.DataFrame([
        {
            'domain': r.get('domain', 'unknown'),
            'paragraphs': r.get('paragraph_count', 0),
            'links': r.get('link_count', 0),
            'images': r.get('image_count', 0),
            'title_length': len(r.get('title', '')),
            'has_email': len(r.get('emails', [])) > 0,
            'has_phone': len(r.get('phones', [])) > 0
        }
        for r in valid_results
    ])
    
    col1, col2 = st.columns(2)
    
    # Chart 1: Content elements comparison with improved styling
    with col1:
        fig1 = px.bar(
            df, 
            x='domain', 
            y=['paragraphs', 'links', 'images'],
            title='Content Elements by Domain',
            labels={'value': 'Count', 'variable': 'Element Type'},
            height=400,
            color_discrete_sequence=['#00b09b', '#96c93d', '#7AA0CB']
        )
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#f5f5f5',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color="#f5f5f5")
            )
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    # Chart 2: Contact information presence
    with col2:
        contact_data = pd.DataFrame({
            'Status': ['Has Email', 'No Email', 'Has Phone', 'No Phone'],
            'Count': [
                df['has_email'].sum(),
                len(df) - df['has_email'].sum(),
                df['has_phone'].sum(),
                len(df) - df['has_phone'].sum()
            ],
            'Type': ['Email', 'Email', 'Phone', 'Phone']
        })
        
        fig2 = px.bar(
            contact_data,
            x='Type',
            y='Count',
            color='Status',
            title='Contact Information Availability',
            height=400,
            color_discrete_sequence=['#00b09b', '#2b5876', '#96c93d', '#4e4376']
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#f5f5f5',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color="#f5f5f5")
            )
        )
        st.plotly_chart(fig2, use_container_width=True)