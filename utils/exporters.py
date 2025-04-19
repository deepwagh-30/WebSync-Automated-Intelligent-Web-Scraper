import streamlit as st
import pandas as pd
import json
import io
import base64

def export_results(results, export_format):
    """Export scraping results in the selected format"""
    if not results:
        st.error("No results to export!")
        return
    
    try:
        # Create a DataFrame from results
        df = pd.DataFrame(results)
        
        # Process based on selected format
        if export_format == "CSV":
            export_as_csv(df)
        elif export_format == "JSON":
            export_as_json(results)
        elif export_format == "Excel":
            export_as_excel(df)
    except Exception as e:
        st.error(f"Error during export: {str(e)}")

def export_as_csv(df):
    """Export results as CSV file"""
    try:
        # Ensure all required columns exist, use safe column selection
        columns_to_include = ["domain", "title", "url", "found_links", "found_images", "social_media", "emails", "phones"]
        available_columns = [col for col in columns_to_include if col in df.columns]
        
        # If some required columns are missing, use all available columns
        if len(available_columns) < len(columns_to_include) / 2:
            filtered_df = df
        else:
            filtered_df = df[available_columns]
        
        # Convert complex objects (lists, dicts) to strings for CSV compatibility
        for col in filtered_df.columns:
            if filtered_df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                filtered_df[col] = filtered_df[col].apply(lambda x: str(x) if isinstance(x, (list, dict)) else x)
        
        csv = filtered_df.to_csv(index=False)
        
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="web_scraper_results.csv",
            mime="text/csv",
            key="download-csv-button",
            help="Download results as CSV file"
        )
        
        st.markdown(
            """<style>.stDownloadButton button {color: #333 !important; background-color: white !important;}</style>""", 
            unsafe_allow_html=True
        )
        
        st.success("CSV file ready for download!")
    except Exception as e:
        st.error(f"Error creating CSV: {str(e)}")

def export_as_json(results):
    """Export results as JSON file"""
    try:
        # Handle any non-serializable objects
        def json_serializer(obj):
            try:
                return str(obj)
            except:
                return "Unserializable object"
        
        # Convert results to JSON string with indentation for readability
        json_str = json.dumps(results, indent=2, default=json_serializer)
        
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name="web_scraper_results.json",
            mime="application/json",
            key="download-json-button",
            help="Download results as JSON file"
        )
        
        st.markdown(
            """<style>.stDownloadButton button {color: #333 !important; background-color: white !important;}</style>""", 
            unsafe_allow_html=True
        )
        
        st.success("JSON file ready for download!")
    except Exception as e:
        st.error(f"Error creating JSON: {str(e)}")

def export_as_excel(df):
    """Export results as Excel file"""
    try:
        # Create a buffer
        buffer = io.BytesIO()
        
        # Convert complex objects (lists, dicts) to strings for Excel compatibility
        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict)) else x)
        
        # Create Excel writer
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Scraping Results', index=False)
            
            # Get the worksheet
            workbook = writer.book
            worksheet = writer.sheets['Scraping Results']
            
            # Add some formatting
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D9EAD3',
                'border': 1
            })
            
            # Write the column headers with the defined format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            # Set column widths
            worksheet.set_column('A:A', 30)  # URL column
            worksheet.set_column('B:Z', 20)  # Other columns
        
        # Download button
        buffer.seek(0)
        st.download_button(
            label="📥 Download Excel",
            data=buffer,
            file_name="web_scraper_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download-excel-button",
            help="Download results as Excel file"
        )
        
        st.markdown(
            """<style>.stDownloadButton button {color: #333 !important; background-color: white !important;}</style>""", 
            unsafe_allow_html=True
        )
        
        st.success("Excel file ready for download!")
    except Exception as e:
        st.error(f"Error creating Excel file: {str(e)}")