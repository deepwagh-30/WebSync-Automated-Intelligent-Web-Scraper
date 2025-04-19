import re
from urllib.parse import urlparse
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
import spacy
import traceback

# Download necessary NLTK resources (only needed once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load spaCy model - using the small model for efficiency
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # Fallback if spaCy model isn't available
    import subprocess
    try:
        # Try to download the model
        subprocess.run([
            "python", "-m", "spacy", "download", "en_core_web_sm"
        ], check=True)
        nlp = spacy.load("en_core_web_sm")
    except:
        nlp = None

def summarize_content(content, max_sentences=5):
    """Summarize content using frequency-based analysis"""
    if not content or content == "Could not extract main content":
        return "No content to summarize"
        
    try:
        words = word_tokenize(content.lower())
        stop_words = set(stopwords.words("english"))
        filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
        
        word_freq = Counter(filtered_words)
        sentence_scores = {}
        
        for sentence in sent_tokenize(content):
            sentence_score = sum(word_freq.get(word.lower(), 0) for word in word_tokenize(sentence))
            sentence_scores[sentence] = sentence_score
        
        top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences]
        return "\n".join(top_sentences)
    except Exception as e:
        return f"Error summarizing content: {str(e)}"

def extract_base_info(soup, url):
    """Extract basic information from a webpage"""
    domain = urlparse(url).netloc
    
    # Get title - improved handling of potential None values
    title = "No title found"
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    
    # Extract meta description
    meta_desc = "No description found"
    meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    if meta_tag and meta_tag.get("content"):
        meta_desc = meta_tag["content"].strip()
    
    # Count paragraphs, links, images
    paragraphs = len(soup.find_all('p'))
    
    # Extract actual links
    links = soup.find_all('a', href=True)
    link_count = len(links)
    found_links = []
    for link in links:
        href = link['href']
        if href.startswith('http'):
            found_links.append(href)
        elif href.startswith('/'):
            base_url = urlparse(url)
            found_links.append(f"{base_url.scheme}://{base_url.netloc}{href}")
    
    # Extract actual images
    images = soup.find_all('img')
    image_count = len(images)
    found_images = []
    for img in images:
        if img.get('src'):
            img_src = img['src']
            if img_src.startswith('http'):
                found_images.append(img_src)
            elif img_src.startswith('/'):
                base_url = urlparse(url)
                found_images.append(f"{base_url.scheme}://{base_url.netloc}{img_src}")
    
    try:
        # Get main content and summary
        main_text = extract_main_content(soup)
        content_summary = generate_nlp_summary(main_text)
        summarized_content = summarize_content(main_text)
    except Exception as e:
        main_text = f"Error extracting content: {str(e)}"
        content_summary = "Error generating summary"
        summarized_content = "Error summarizing content"
    
    return {
        "domain": domain,
        "title": title,
        "description": meta_desc,
        "paragraph_count": paragraphs,
        "link_count": link_count,
        "image_count": image_count,
        "found_links": found_links,
        "found_images": found_images,
        "main_content": main_text[:1500] + "..." if len(main_text) > 1500 else main_text,
        "content_summary": content_summary,
        "summarized_content": summarized_content
    }

def extract_main_content(soup):
    """Extract main content text from a webpage using a more sophisticated approach"""
    # First try to find common main content containers
    main_containers = soup.select('main, article, .content, .main-content, #content, #main-content, .post-content, .entry-content')
    
    if main_containers:
        container = main_containers[0]
        paragraphs = container.find_all('p')
    else:
        # If no main containers found, use all paragraphs
        paragraphs = soup.find_all('p')
    
    # Filter out short paragraphs, navigation text, and ads
    meaningful_paragraphs = []
    for p in paragraphs:
        text = p.text.strip()
        if len(text) > 50 and not is_boilerplate_text(text):
            meaningful_paragraphs.append(text)
    
    if not meaningful_paragraphs:
        # As a backup, try to get any text with at least 100 characters
        all_text = [t.strip() for t in soup.stripped_strings if len(t.strip()) > 100]
        if all_text:
            return "\n\n".join(all_text[:5])  # Take first 5 long text segments
        return "Could not extract main content"
    
    return "\n\n".join(meaningful_paragraphs)

def is_boilerplate_text(text):
    """Detect if text is likely boilerplate (navigation, ads, etc.) rather than content"""
    boilerplate_terms = [
        'menu', 'navigation', 'search', 'login', 'sign in', 'register', 
        'home', 'about', 'contact', 'privacy policy', 'terms', 'copyright',
        'all rights reserved', 'cookie', 'newsletter', 'subscribe',
        'advertisement', 'sponsored', 'click here', 'read more'
    ]
    
    text_lower = text.lower()
    # Check if text contains boilerplate terms and is relatively short
    if len(text) < 150:
        for term in boilerplate_terms:
            if term in text_lower:
                return True
    
    return False

def generate_nlp_summary(text, num_sentences=3):
    """Generate a summary of the text using NLP techniques"""
    if text == "Could not extract main content" or len(text) < 100:
        return "No meaningful content to summarize."
    
    try:
        # Try spaCy-based summarization if available
        if nlp:
            return generate_spacy_summary(text, num_sentences)
        else:
            # Fallback to simpler NLTK-based approach
            return generate_basic_summary(text, num_sentences)
    except Exception as e:
        print(f"Error in summarization: {e}")
        print(traceback.format_exc())
        return "Error generating summary: " + str(e)

def generate_spacy_summary(text, num_sentences=3):
    """Generate summary using spaCy for better NLP processing"""
    # Process text with spaCy
    doc = nlp(text)
    
    # Score sentences based on word importance
    word_frequencies = {}
    for token in doc:
        if not token.is_stop and not token.is_punct and token.text.lower() not in stopwords.words('english'):
            if token.text.lower() not in word_frequencies:
                word_frequencies[token.text.lower()] = 1
            else:
                word_frequencies[token.text.lower()] += 1
    
    # Normalize frequencies
    max_frequency = max(word_frequencies.values()) if word_frequencies else 1
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_frequency
    
    # Score sentences
    sentence_scores = {}
    sentences = [sent.text for sent in doc.sents]
    
    for i, sentence in enumerate(sentences):
        for word in nlp(sentence):
            if word.text.lower() in word_frequencies:
                if i not in sentence_scores:
                    sentence_scores[i] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[i] += word_frequencies[word.text.lower()]
    
    # Get top sentences
    top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
    top_sentences = sorted(top_sentences, key=lambda x: x[0])  # Sort by original position
    
    # Combine sentences with improved formatting
    summary = "📌 " + "\n\n📌 ".join([sentences[i] for i, _ in top_sentences])
    
    # Extract main topic/keywords (simple approximation)
    keywords = sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)[:5]
    keywords_str = ", ".join([word for word, _ in keywords])
    
    return f"Key topics: {keywords_str}\n\nSummary:\n{summary}"

def generate_basic_summary(text, num_sentences=3):
    """Generate summary using basic NLTK techniques as fallback"""
    # Tokenize text into sentences
    sentences = sent_tokenize(text)
    
    if len(sentences) <= num_sentences:
        return text
    
    # Compute word frequencies
    stop_words = set(stopwords.words('english'))
    word_frequencies = {}
    
    for sentence in sentences:
        for word in nltk.word_tokenize(sentence.lower()):
            if word not in stop_words and word.isalnum():
                if word not in word_frequencies:
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1
    
    # Score sentences based on word frequencies
    sentence_scores = {}
    for i, sentence in enumerate(sentences):
        for word in nltk.word_tokenize(sentence.lower()):
            if word in word_frequencies:
                if i not in sentence_scores:
                    sentence_scores[i] = word_frequencies[word]
                else:
                    sentence_scores[i] += word_frequencies[word]
    
    # Get top sentences
    top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
    top_sentences = sorted(top_sentences, key=lambda x: x[0])  # Sort by original position
    
    # Combine sentences with improved formatting
    summary = "📌 " + "\n\n📌 ".join([sentences[i] for i, _ in top_sentences])
    
    return f"Summary:\n{summary}"

def extract_contact_info(soup):
    """Extract contact information from a webpage"""
    # Email pattern
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = set()
    
    # Search in text content
    for text in soup.stripped_strings:
        found_emails = re.findall(email_pattern, text)
        emails.update(found_emails)
    
    # Search in href attributes of anchor tags
    for a_tag in soup.find_all('a', href=True):
        if a_tag['href'].startswith('mailto:'):
            email = a_tag['href'].replace('mailto:', '').split('?')[0]
            emails.add(email)
    
    # Phone pattern (improved)
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = set()
    
    for text in soup.stripped_strings:
        found_phones = re.findall(phone_pattern, text)
        phones.update(found_phones)
    
    # Social media handles (improved detection)
    social_media = {}
    
    social_platforms = {
        'facebook': r'facebook\.com/([A-Za-z0-9.]+)',
        'twitter': r'twitter\.com/([A-Za-z0-9_]+)',
        'x': r'x\.com/([A-Za-z0-9_]+)',  # Adding X (formerly Twitter)
        'instagram': r'instagram\.com/([A-Za-z0-9_.]+)',
        'linkedin': r'linkedin\.com/(?:company|in)/([A-Za-z0-9_-]+)',
        'youtube': r'youtube\.com/(?:user|channel)/([A-Za-z0-9_-]+)',
        'tiktok': r'tiktok\.com/@([A-Za-z0-9_.]+)',
        'pinterest': r'pinterest\.com/([A-Za-z0-9_]+)'
    }
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        for platform, pattern in social_platforms.items():
            match = re.search(pattern, href)
            if match:
                social_media[platform] = match.group(1)
    
    return {
        "emails": list(emails),
        "phones": list(phones),
        "social_media": social_media
    }