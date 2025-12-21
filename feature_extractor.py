import re
from urllib.parse import urlparse

def extract_features(url):
    """
    Converts a URL into numerical features for ML models.
    """

    # Parse URL
    parsed = urlparse(url)

    # 1. URL length
    url_length = len(url)

    # 2. Dot count
    dot_count = url.count('.')

    # 3. HTTPS check (correct way)
    is_https = 1 if parsed.scheme == "https" else 0

    # 4. IP address in domain
    has_ip = 1 if re.fullmatch(
        r'(\d{1,3}\.){3}\d{1,3}', parsed.netloc
    ) else 0

    # 5. Suspicious keywords
    suspicious_words = [
        'login', 'secure', 'account', 'update',
        'verify', 'bank', 'signin', 'confirm'
    ]
    suspicious_count = sum(
        1 for word in suspicious_words if word in url.lower()
    )

    return [
        url_length,
        dot_count,
        is_https,
        has_ip,
        suspicious_count
    ]
