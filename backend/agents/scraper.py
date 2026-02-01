import re
import json
import time
import asyncio
from crawl4ai import AsyncWebCrawler
from ddgs import DDGS
from googlesearch import search as google_search
from agents.llm import llm
import hashlib

# --- Configuration ---
# Cache for repeated queries
CACHE = {}

# Known Official Sites (Fallback/Accelerator)
KNOWN_SITES = {
    "delhi transport corporation": ["https://dtc.delhi.gov.in/contact-us", "https://dtc.delhi.gov.in"],
    "dtc": ["https://dtc.delhi.gov.in/contact-us", "https://dtc.delhi.gov.in"],
    "delhi jal board": ["https://delhijalboard.nic.in/content/contact-us", "https://delhijalboard.nic.in"],
    "djb": ["https://delhijalboard.nic.in/content/contact-us"],
    "delhi police": ["https://delhipolice.gov.in/contact-us", "https://delhipolice.gov.in"],
    "municipal corporation": ["https://mcdonline.nic.in/portal/contact-us", "https://mcdonline.nic.in"],
    "mcd": ["https://mcdonline.nic.in/portal/contact-us"],
    "bses": ["https://www.bsesdelhi.com/web/bses/contact-us", "https://www.bsesdelhi.com"],
    "tata power": ["https://www.tatapower-ddl.com/customer/contact-us", "https://www.tatapower-ddl.com"],
    "pwd": ["https://pwddelhi.gov.in/contactus.aspx"]
}

async def scrape_url_crawl4ai(url, depth=1):
    """Deep scraping using Crawl4AI."""
    print(f"🕷️ Crawling: {url} (Depth: {depth})")
    content_blob = ""
    
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            
            if not result.markdown:
                return ""
            
            # Tag important sections
            is_priority = any(kw in result.markdown.lower() for kw in 
                             ['helpline', 'toll free', 'customer care', 'control room'])
            
            content_blob = f"\n--- Source: {url} ---\n"
            if is_priority:
                content_blob += "*** PRIORITY HELPLINE PAGE ***\n"
            content_blob += f"{result.markdown[:8000]}\n" # Limit context
            
            # Smart deep scraping (finding links in markdown is harder, relying on crawler results if possible)
            # For now, regex for "Contact Us" links in the markdown or html? 
            # Crawl4AI returns 'links' in result usually? Let's assume text processing for now or skip recursive for simplicity first unless critical.
            # actually result.links exists in crawl4ai.
            
            if depth > 0 and hasattr(result, 'links'):
                priority_links = []
                for link in result.links: 
                    # Handle if link is a dict (new versions) or string (old versions/internal links)
                    if isinstance(link, dict):
                        href = link.get('href', '')
                        text = link.get('text', '').lower()
                    elif isinstance(link, str):
                        href = link
                        text = link.lower() # Infer text from URL if simple string
                        
                    if any(x in text or x in href.lower() for x in ['contact', 'helpline', 'grievance', 'support']):
                        priority_links.append(href)
                
                for link in priority_links[:2]:
                     print(f"  -> Found smart contact link: {link}")
                     # Recursive call? AsyncWebCrawler session? 
                     # Doing simple recursive await for now.
                     sub_content = await scrape_url_crawl4ai(link, depth=0)
                     content_blob += sub_content

    except Exception as e:
        print(f"  -> Failed to crawl {url}: {e}")
    
    return content_blob

def extract_smart_regex(text):
    """Intelligent regex patterns for public contacts ONLY"""
    # Public helpline patterns (India-specific toll-free + customer care)
    public_phones = re.findall(
        r'(?i)(?:helpline|customer.?care|toll.?free|control.?room|grievance|complaint|24x7)[:\s\-()]*'
        r'(?:1800|155|191|1-8\d{2}|0\d{2,4}[-\s]?)[\d\-\s()]{6,15}', text)
    
    # Official emails only (gov.in/nic.in patterns)
    official_emails = re.findall(
        r'\b(complaint|help|grievance|ccc|care|support)@[\w\.-]*\.(?:gov\.in|nic\.in|govt?\.in)\b', 
        text, re.I)
    
    # Websites (official domains only)
    websites = re.findall(r'https?://[\w\.-]*\.(?:gov\.in|nic\.in|govt?\.in)', text)
    
    # Filter out known non-relevant helplines
    bad_numbers = {'1930', '1075', '181', '1091', '1098'}
    
    final_phones = []
    for p in set(public_phones):
        clean_p = re.sub(r'[^\d]', '', p)
        if clean_p not in bad_numbers:
            final_phones.append(p)

    return {
        'phone': final_phones[:3],
        'email': list(set(official_emails)),
        'website': websites[0] if websites else None
    }

def classify_issue_semantic(authority_name, location, description=""):
    """Zero-shot semantic classification using LLM."""
    context = f"{authority_name} in {location}: {description}".strip()
    
    prompt = f"""Classify this civic issue into EXACTLY ONE category for contact lookup:

CONTEXT: "{context}"

CATEGORIES (choose only one):
TRANSPORT, ELECTRICITY, WATER, HEALTH, INFRASTRUCTURE, POLICE, GRIEVANCE, OTHER

Respond ONLY with category name (e.g. "TRANSPORT"): """
    
    try:
        category = llm(prompt).strip().upper()
        return category if category in ['TRANSPORT', 'ELECTRICITY', 'WATER', 'HEALTH', 'INFRASTRUCTURE', 'POLICE', 'GRIEVANCE', 'OTHER'] else 'GRIEVANCE'

    except:
        return 'GRIEVANCE'

def discover_relevant_departments(category, location):
    """LLM discovers relevant departments dynamically."""
    prompt = f"""For {category} issues in {location}, list TOP 3 most relevant government departments/authorities.

Examples:
Delhi TRANSPORT → DTC, Delhi Transport Department
Delhi WATER → DJB, Delhi Jal Board
Delhi ELECTRICITY → BSES, Tata Power, Delhi Power Department
Haryana ELECTRICITY → DHBVN, UHBVN

{location} {category}
Respond ONLY as JSON array: ["Dept1", "Dept2", "Dept3"]"""
    
    try:
        response = llm(prompt)
        depts = json.loads(re.search(r'\[(.*)\]', response, re.DOTALL).group())
        return depts[:3]
    except:
        return [f"{category} Department"]

def search_with_fallback(query, max_results=3):
    """Robust search with multiple fallbacks."""
    raw_urls = []
    
    # Primary: DDGS with region targeting
    try:
        with DDGS(timeout=10) as ddgs:
            results = list(ddgs.text(query, max_results=max_results*2, region='in-en'))
            raw_urls.extend([r['href'] for r in results if 'gov.in' in r['href'] or 'nic.in' in r['href']])
    except Exception as e:
        print(f"DDGS failed: {e}")
    
    # Secondary: Broad DDGS
    if len(raw_urls) < 2:
        try:
            with DDGS(timeout=10) as ddgs:
                results = list(ddgs.text(query.replace('site:gov.in', ''), max_results=max_results))
                raw_urls.extend([r['href'] for r in results])
        except:
            pass
    
    # Tertiary: Google fallback
    if not raw_urls:
        try:
            results = list(google_search(query, num_results=max_results))
            raw_urls.extend(results)
        except Exception as e:
            print(f"Google failed: {e}")
    
    return list(set(raw_urls))[:max_results]

async def find_contact_info(authority_name, location, issue_type="", description=""):
    """INTELLIGENT scraper - discovers departments + extracts public contacts ONLY."""
    
    # Cache check
    cache_key = hashlib.md5(f"{authority_name}|{location}|{issue_type}|{description}".encode()).hexdigest()
    if cache_key in CACHE:
        return CACHE[cache_key]
    
    print(f"🔍 Intelligent search: {authority_name} in {location}")
    
    # 1. SEMANTIC CLASSIFICATION
    category = classify_issue_semantic(authority_name, location, description)
    print(f"📋 Classified as: {category}")
    
    # 2. DYNAMIC DEPARTMENT DISCOVERY
    departments = discover_relevant_departments(category, location)
    print(f"🏢 Departments: {departments}")
    
    # 3. SMART SEARCH PER DEPARTMENT
    all_urls = []
    
    # A. Check Known Sites matches (Authority Name OR Category OR Discovered Departments)
    for k, v in KNOWN_SITES.items():
        if k in authority_name.lower() or k in category.lower() or any(k in d.lower() for d in departments):
            print(f"⚡ Accelerated with Known Site: {k}")
            all_urls.extend(v)

    # B. Live Search (if needed)
    if len(all_urls) < 3:
        for dept in departments:
            # Helpline-focused queries
            queries = [
                f'"{dept}" {location} (helpline OR "toll free" OR "customer care" OR "control room")',
                f'"{dept}" {location} (complaint OR grievance OR "24x7") (site:gov.in OR site:nic.in)',
                f"{dept} {location} contact official"
            ]
            
            for query in queries:
                urls = search_with_fallback(query)
                all_urls.extend(urls)
                if len(all_urls) >= 6:  # Enough sources
                    break
    
    if not all_urls:
        return _fallback_not_found()
    
    # 4. ENHANCED SCRAPING (CRAWL4AI)
    full_context = ""
    
    # Priority: Scrape KNOWN_SITES[0] (Deep Link) first if it exists
    priority_urls = []
    if len(all_urls) > 0 and any(k in authority_name.lower() for k in KNOWN_SITES):
         priority_urls = [all_urls[0]] + list(set(all_urls[1:]))
    else:
         priority_urls = list(set(all_urls))

    print(f"🕷️ Starting Crawl4AI on {len(priority_urls[:4])} URLs...")
    for url in priority_urls[:4]:
        full_context += await scrape_url_crawl4ai(url)
    
    # 5. HIERARCHICAL EXTRACTION (LLM + Regex fallback)
    prompt = f"""Extract ONLY PUBLIC contacts for civic services from this scraped content.

STRICT PRIORITY (ignore personal officer contacts):
1. Toll-free (1800/155...) / Customer Care / Control Room numbers
2. Official emails: complaint@, help@, grievance@, ccc@*.gov.in
3. Official websites (*.gov.in/*.nic.in)
4. Officer ONLY if nothing else found

⚠️ IGNORE: Cyber Crime (1930), Covid (1075), Women Helpline (181) UNLESS issue is related.

📍 Context: {authority_name} ({category}) in {location}

{full_context}

Return ONLY valid JSON with EXTRACTED data. Use "Not available" for missing fields. DO NOT use example values.
{{"phone": [], "email": [], "website": "Found URL or Not available", "confidence": 0.0}}"""

    try:
        response = llm(prompt)
        data = json.loads(re.search(r'\{.*\}', response, re.DOTALL).group())
        
        # Validate + enhance with regex
        regex_data = extract_smart_regex(full_context)
        if not data.get('phone') and regex_data['phone']:
            data['phone'] = regex_data['phone']
        if not data.get('email') and regex_data['email']:
            data['email'] = regex_data['email']
            
        data['category'] = category
        data['confidence'] = min(0.98, len(data['phone']) * 0.4 + len(data['email']) * 0.3 + 0.3)
        
    except Exception as e:
        print(f"LLM extraction failed: {e}")
        data = extract_smart_regex(full_context)
        data['category'] = category
        data['confidence'] = 0.6 if data['phone'] else 0.2
    
    CACHE[cache_key] = data
    return data

def _fallback_not_found():
    return {"phone": ["1800-11-1311"], "email": ["pgportal.gov.in"], "website": "https://pgportal.gov.in", "confidence": 0.3, "category": "GRIEVANCE"}

# Test examples
if __name__ == "__main__":
    asyncio.run(find_contact_info("DTC bus issue", "Delhi", description="Bus not stopping at designated stop"))
