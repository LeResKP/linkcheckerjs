from urlparse import urlparse


def standardize_url(url):
    """Standardisation of the given url to match phantomjs returned url
    """
    if not url:
        return url
    o = urlparse(url)
    if not o.path:
        return url + '/'
    return url
