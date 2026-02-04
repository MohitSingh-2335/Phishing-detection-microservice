import re
from urllib.parse import urlparse
import math
from collections import Counter

def calculate_entropy(text):
    if not text : return 0
    entropy = 0
    total = len(text)
    for count in Counter(text).values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

def extract_features(url):
    """
    Converts a URL into numerical features for ML models.
    Logic: 1 = Risky/Bad, 0 = Safe/Good
    """

    #Ensuring URL starting with HTTPS
    if not url.startswith(("http://", "https://")):
        url = 'https://' + url

    # Parse URL
    try:
        parsed = urlparse(url)
    except:
        return [0] * 12

    # 1. URL length
    url_length = len(url)

    # 2. Dot count
    dot_count = url.count('.')

    # 3. HTTPS check (correct way)
    is_not_https = 0 if parsed.scheme == "https" else 1

    # 4. IP address in domain
    has_ip = 1 if re.search(
        r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', parsed.netloc
    ) else 0

    # 5.Digit Count
    digit_count = sum(c.isdigit() for c in url)

    # 6.Sensitive character count
    at_count = url.count('@')
    dash_count = url.count('-')
    double_slash = url.count('//')

    # 7.Subdomain count
    subdomains = parsed.netloc.split('.')
    subdomain_count = len(subdomains)

    # 8.Directory depth
    dir_depth = parsed.path.count('/')

    # 9.Shannon entropy
    entropy = calculate_entropy(parsed.netloc)

    # 10.Shortening Service Check
    shorteners = ['bit.ly', 'goo.gl', 'shorte.st', 'tinyurl.com', 'tr.im', 'is.gd', 'cli.gs']
    is_shortened = 1 if any(s in parsed.netloc for s in shorteners) else 0

    # 11. Suspicious keywords
    suspicious_words = [
        'login', 'secure', 'account', 'update',
        'verify', 'bank', 'signin', 'confirm',
        'wallet', 'crypto', 'free'
    ]
    has_sus_word = 1 if any(w in url.lower() for w in suspicious_words) else 0

    return [
        url_length, 
        dot_count, 
        is_not_https, 
        digit_count, 
        at_count, 
        dash_count, 
        double_slash, 
        subdomain_count, 
        dir_depth, 
        entropy,
        is_shortened,
        has_sus_word
    ]
