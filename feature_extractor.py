import re
from urllib.parse import urlparse

def extract_features(url):
    """
    Converts a URL into numerical features for ML models.
    Logic: 1 = Risky/Bad, 0 = Safe/Good
    """

    #Ensuring URL starting with HTTPS
    if not url.startswith(("http://", "https://")):
        url = 'http://' + url

    # Parse URL
    parsed = urlparse(url)

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

    # 5. Suspicious keywords
    suspicious_words = [
        'login', 'secure', 'account', 'update',
        'verify', 'bank', 'signin', 'confirm',
        'wallet', 'crypto', 'free'
    ]
    suspicious_count = sum(
        1 for word in suspicious_words if word in url.lower()
    )

    return [
        url_length,
        dot_count,
        is_not_https,
        has_ip,
        suspicious_count
    ]
