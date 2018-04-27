import urllib.parse
import requests
import os
import bs4

def request_to_soup(request, url):
    '''
    Takes a request and returns a BeautifulSoup object.

    Input:
        - request (req object) the request for which html will be stored

    Returns: soup (bs4 object) the html soup
    '''

    html = read_request(request, url)
    soup = bs4.BeautifulSoup(html, 'html5lib')
    return soup

def get_urls(soup, limit_to_section = None):
    '''
    Takes an html page's soup and returns all anchor links on the page.

    Input:
        - soup (bs4 object): the page to be scraped
        - limit_to_section (string): if you wish to limit the scrape to a
        subsection of the page, set limit_to_section to the appropriate
        html class of the div tag type. 

    Returns: urls (list of strings) all url strings on the page
    '''
    if limit_to_section:
        try:
            soup = soup.find_all('div', class_ = limit_to_section)[0]
        except:
            pass

    url_soup = soup.find_all('a')
    urls = []
    for url in url_soup:
        try:
            urls.append(url['href'])
        except:
            continue

    return urls

def convert_seconds_to_min_sec(total_seconds, text_output = False):
    '''
    Takes seconds and converts to _ min, _ sec format. 
    Inputs:
        - total_seconds (float): number of seconds
        - text_output (boolean): Default, False. 
    Output:
        - If text_output is False, function returns minutes and 
        seconds in integer form. If True, function returns in a
        string in "_ min, _ sec" format.
    '''
    total = total_seconds
    minutes = int(total // 60)

    if minutes == 0:
        seconds = int(total)
    else:
        seconds = int(total % (minutes*60))
    if text_output:
        return minutes, seconds

    return str(minutes) + " min, " + str(seconds) + " sec"

def request_to_soup(request, url):
    '''
    Takes a request and returns a BeautifulSoup object.

    Input:
        - request (req object) the request for which html will be stored

    Returns: soup (bs4 object) the html soup
    '''

    html = util.read_request(request, url)
    soup = bs4.BeautifulSoup(html, 'html5lib')
    return soup

def get_request(url):
    '''
    Open a connection to the specified URL and if successful
    read the data.

    Inputs:
        url: must be an absolute URL

    Outputs:
        request object or None

    Examples:
        get_request("http://www.cs.uchicago.edu")
    '''

    if is_absolute_url(url):
        try:
            r = requests.get(url)
            if r.status_code == 404 or r.status_code == 403:
                r = None
        except Exception:
            # fail on any kind of error
            r = None
    else:
        r = None

    return r


def read_request(request, url):
    '''
    Return data from request object.  Returns result or "" if the read
    fails..
    '''

    try:
        return request.text.encode('utf8')
    except:
        if request == None:
            print("***request failed: " + url)
            return ""
        elif request.url:
            print("***read failed: " + request.url)
            return ""
        else:
            print("***request failed: " + url)
            return ""


def get_request_url(request):
    '''
    Extract true URL from the request
    '''
    return request.url


def is_absolute_url(url):
    '''
    Is url an absolute URL?
    '''
    if url == "":
        return False
    return urllib.parse.urlparse(url).netloc != ""


def remove_fragment(url):
    '''remove the fragment from a url'''

    (url, frag) = urllib.parse.urldefrag(url)
    return url


def convert_if_relative_url(current_url, new_url):
    '''
    Attempt to determine whether new_url is a relative URL and if so,
    use current_url to determine the path and create a new absolute
    URL.  Will add the protocol, if that is all that is missing.

    Inputs:
        current_url: absolute URL
        new_url:

    Outputs:
        new absolute URL or None, if cannot determine that
        new_url is a relative URL.

    Examples:
        convert_if_relative_url("http://cs.uchicago.edu", "pa/pa1.html") yields
            'http://cs.uchicago.edu/pa/pa.html'

        convert_if_relative_url("http://cs.uchicago.edu", "foo.edu/pa.html")
            yields 'http://foo.edu/pa.html'
    '''
    if new_url == "" or not is_absolute_url(current_url):
        return None
    if is_absolute_url(new_url):
        return new_url

    parsed_url = urllib.parse.urlparse(new_url)
    path_parts = parsed_url.path.split("/")

    if len(path_parts) == 0:
        return None
    ext = path_parts[0][-4:]
    if ext in [".edu", ".org", ".com", ".net"]:
        return "http://" + new_url
    elif new_url[:3] == "www":
        return "http://" + new_path
    else:
        return urllib.parse.urljoin(current_url, new_url)


def is_url_ok_to_follow(url, limiting_domain, limiting_path = None, ignore = None):
    '''
    Inputs:
        url: absolute URL
        limiting domain: domain name

    Outputs:
        Returns True if the protocol for the URL is HTTP, the domain
        is in the limiting domain, and the path is either a directory
        or a file that has no extension or ends in .html. URLs
        that include an "@" are not OK to follow.

    Examples:
        is_url_ok_to_follow("http://cs.uchicago.edu/pa/pa1", "cs.uchicago.edu")
            yields True

        is_url_ok_to_follow("http://cs.cornell.edu/pa/pa1", "cs.uchicago.edu")
            yields False
    '''
    
    if url_checks(url):

        if is_outside_domain(url, limiting_domain):
            return False

        if ignore:
            for word in ignore:
                if word in url:
                    return False

        if limiting_path not in url:
            return False

        # does it have the right extension
        parsed_url = urllib.parse.urlparse(url)
        (filename, ext) = os.path.splitext(parsed_url.path)
        return (ext == "" or ext == ".html" or ext == '.aspx')

def url_checks(url):
    if "mailto:" in url:
        return False

    if "@" in url:
        return False

    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme != "http" and parsed_url.scheme != "https":
        return False

    if parsed_url.netloc == "":
        return False

    if parsed_url.fragment != "":
        return False

    return True


def is_outside_domain(url, limiting_domain, return_ = False):
    if url_checks(url):
        parsed_url = urllib.parse.urlparse(url)
        loc = parsed_url.netloc
        ld = len(limiting_domain)
        trunc_loc = loc[-(ld+1):]
        if not return_:
            if not (limiting_domain == loc or (trunc_loc == "." + limiting_domain)):
                return True
        else:
            if not (limiting_domain == loc or (trunc_loc == "." + limiting_domain)):
                return url

def top_words(description_words, top_num):
    word_dict = {}
    for word in description_words:
        if word not in word_dict:
            word_dict[word] = 1
        else:
            word_dict[word] += 1

    for word, count in word_dict.items():
        word_counts = [(word_dict[word], word) for word in word_dict]

    word_counts.sort()
    word_counts.reverse()

    return word_counts[:top_num]
