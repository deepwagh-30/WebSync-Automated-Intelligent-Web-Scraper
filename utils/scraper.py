import requests
from bs4 import BeautifulSoup
import validators
import re
import time
from urllib.parse import urlparse
import streamlit as st
from utils.parsers import extract_base_info, extract_contact_info

def create_soup(url, timeout=10):
    """Create a BeautifulSoup object from a URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return BeautifulSoup(response.text, 'html.parser'), None
    except requests.exceptions.RequestException as e:
        return None, str(e)

def scrape_url(url, extract_options):
    """Scrape a single URL and return the extracted information"""
    if not validators.url(url):
        return {"error": f"Invalid URL: {url}", "url": url}
    
    soup, error = create_soup(url)
    if error:
        return {"error": f"Failed to access {url}: {error}", "url": url}
    
    results = {"url": url}
    
    # Extract information based on selected options
    if extract_options["Basic Info"]:
        results.update(extract_base_info(soup, url))
    
    if extract_options["Contact"]:
        results.update(extract_contact_info(soup))
    
    # Add timestamp
    results["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    return results

def scrape_multiple_urls(urls, progress_bar, extract_options):
    """Scrape multiple URLs with progress tracking"""
    results = []
    
    for i, url in enumerate(urls):
        result = scrape_url(url, extract_options)
        results.append(result)
        
        # Update progress
        progress_value = (i + 1) / len(urls)
        progress_bar.progress(progress_value)
        
        # Small delay to avoid overwhelming servers
        time.sleep(0.5)  # Increased from 0.2 to 0.5 to avoid rate limiting
    
    return results