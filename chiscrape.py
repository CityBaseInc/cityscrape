import urllib.parse
import requests
import os
import bs4
import queue
import util
import time
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import re
import pandas as pd


OMIT_WORDS = ['chicago', 'city','department', 'spec', 'council', 'please']

class dataset(object):
    def __init__(self, output):
        self.visited_urls = output[0]
        self.outside_domain = output[1]
        self.failed_reads = output[2]
        self.description_words_all = output[3]
        self.url_num_reference = output[4]
        self.diagnostic = output[5]
        self.num_visits = len(self.visited_urls)

    def __repr__(self):
        return self.diagnostic

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

def get_urls(soup, class_ = None):
    '''
    Takes an html page's soup and returns all anchor links on the page.

    Input:
        - soup (bs4 object) the page to be scraped

    Returns: urls (list of strings) all url strings on the page
    '''
    if class_:
        soup = soup.find_all('div', 
                    class_ = class_)[0]

    url_soup = soup.find_all('a')
    urls = []
    for url in url_soup:
        try:
            urls.append(url['href'])
        except:
            continue

    return urls

def has_i_want_to(soup):
    panels = [text.text for text in soup.find_all('div', 
            class_ = 'panel-heading')]
    for text in panels:
        if "I Want To" in text:
            return True
            break
        else:
            return False

    

def has_new_nav(soup):
    if soup.find_all('div', class_ = 'container-fluid container-header'):
        return True
    else:
        return False


def scrape_description_text(soup):
    if soup.find('div', 'container-fluid page-full-description'):
        text = soup.find('div', 'container-fluid page-full-description').text
    elif soup.find('div', 'container-fluid page-full-description-above'):
        text = soup.find('div', 'container-fluid page-full-description-above').text
    else:
        text = None
    if text:
        cleaned_words = []
        alpha = re.compile(r'^[a-zA-Z]')
        words = word_tokenize(text.lower())
        stopWords = set(stopwords.words('english'))
        for w in words:
              if (w not in stopWords) and (re.match(alpha, w) is not None) and (w not in OMIT_WORDS):
                  cleaned_words.append(w)

        return cleaned_words

    else:
        return ['No text found']

def site_prefix(url, limiting_domain):
    parsed_url = urllib.parse.urlparse(url)
    loc = parsed_url.netloc
    loc_len = len(loc) - 4
    lim_len = len(limiting_domain)
    if (limiting_domain in loc) and (loc_len != lim_len):
        # domain_prefix = loc[:-lim_len]

        return url

def get_department(url):
    parsed_url = urllib.parse.urlparse(url)
    path = parsed_url.path
    if path and 'depts' in path:
        path = path[23:]
        dept = path.split('/')[0]
        return dept


def clean_and_queue_urls(soup, true_url, limiting_domain, 
    outside_domain, queue, visited, limiting_path = None, 
                                                class_ = None):
    '''
    Takes a list of urls from the current page being visited and adds 
    them to the queue of urls to be visited by the scraper if they 
    have not been visited already.

    Inputs:
        - urls: (list of strings) list of urls from the current page.
        - true_url: (string) url of the page currently being visited.
        - limiting_domain: (string) domain to filter out urls not belonging
        to the same domain.
        - queue: (Queue object) queue holding urls to visit in first-in-first
        out order.
        - url_tracker: (list of strings) list of urls that have been visited.

    Returns: None - the function will add to the any url not visited before.
    '''
    urls = get_urls(soup, class_)
    outside = []
    full_urls = []
    email_addresses = []
    for url in urls:
        url = util.remove_fragment(url)
        if url == '':
            continue
        if 'mailto' in url:
            email_addresses.append(url)
        if not util.is_absolute_url(url):
            url = util.convert_if_relative_url(true_url, url)
            full_urls.append(url)
        if util.is_outside_domain(url, limiting_domain, return_ = True):
            outside_domain.append((true_url,url))
            outside.append(url)
        if site_prefix(url, limiting_domain):
            outside_domain.append((true_url,site_prefix(url, limiting_domain)))
            outside.append(site_prefix(url, limiting_domain))
        if util.is_url_ok_to_follow(url, limiting_domain, limiting_path):
            if url not in queue.queue:
                if url not in visited:
                    queue.put(url)

    return outside, email_addresses, full_urls

def count_pdfs(urls):
    pdf_urls = []
    for url in urls:
        parsed_url = urllib.parse.urlparse(url)
        filename, ext = os.path.splitext(parsed_url.path)
        if ext == '.pdf':
            pdf_urls.append(url)

    return pdf_urls, len(pdf_urls)



def has_botton(soup):
    if soup.find_all('a', class_='btn btn-primary'):
        return True
    else:
        return False


def dataset_to_dataframe(dataset, columns = None):
    columns = ['dept', 'title', 'url', 'button', 'i_want_to',
           'nav', 'num_email_addresses', 'email_addresses',
           'pdf_count', 'pdf_urls', 'ext_link_count','ext_links', 'description_words']
    data_rows = dataset.visited_urls
    df = pd.DataFrame(columns = columns)
    for page, data in data_rows.items():
        df.loc[page] = [data[0], data[1], data[2],
                        data[3], data[4], data[5], data[6],
                        "; ".join(data[7]), data[8],
                        "; ".join(data[9]), data[10],
                        "; ".join(data[11]),
                        "; ".join(data[12])]

    return df


def go(num_pages_to_crawl):
    '''
    Crawl the college catalog and generates a CSV file with an index.

    Inputs:
        num_pages_to_crawl: the number of pages to process during the crawl
        course_map_filename: the name of a JSON file that contains the mapping
          course codes to course identifiers
        index_filename: the name for the CSV of the index.

    Outputs:
        CSV file of the index.
    '''
    start = time.time()
    visit_counter = 0
    starting_url = 'https://www.cityofchicago.org/city/en.html'
    limiting_domain = "cityofchicago.org"
    limiting_path =  'svcs' #'/city/en/depts/fin/'
    soup_part = 'container-fluid container-body'
    url_queue = queue.Queue()
    url_tracker = {}
    visited = set()
    outside_domain = []
    dead_links = []
    description_words_all = []
    url_num_reference = {}

    while visit_counter < num_pages_to_crawl:
        
        if visit_counter == 0:
            current_url = starting_url
        else:
            current_url = url_queue.get()


        request = util.get_request(current_url)

        try:
            true_url = util.get_request_url(request)
        except:
            dead_links.append(current_url)
            continue

        if true_url in visited:
            continue

        print(visit_counter, "--------", true_url)

        soup = request_to_soup(request, true_url)

        try:
            outside, email_addresses, urls = clean_and_queue_urls(soup, true_url, limiting_domain, 
                outside_domain, url_queue, visited,
                limiting_path = limiting_path, class_ = soup_part)
        except:
            failed_reads.append(true_url)
            visit_counter += 1
            continue

        pdf_urls, pdf_count = count_pdfs(urls)
        page_title = soup.title.text[24:-1]
        description_words = scrape_description_text(soup)
        if type(description_words) != str:
            description_words_all += description_words

        button = has_botton(soup)
        i_want_to = has_i_want_to(soup)
        nav = has_new_nav(soup)
        dept = get_department(true_url)


        visit_counter += 1
        visited.add(true_url)
        url_tracker[visit_counter] = ((dept, page_title, true_url, 
                                     button, i_want_to, nav, len(email_addresses), 
                                     email_addresses, pdf_count, pdf_urls, len(outside), 
                                     outside, description_words))
        url_num_reference[true_url] = visit_counter

        if url_queue.qsize() == 0:
            break

        # time.sleep(2)
    end = time.time()

    total_seconds = end - start

    minutes = int(total_seconds // 60)

    if minutes == 0:
        seconds = int(total_seconds)
    else:
        seconds = int(total_seconds % minutes)

    diagnostic = '''
    Pages to Crawl: {}
    Pages Visited: {}
    Pages Scraped: {}
    Total Time: {} min, {} sec
    Dead Links: {}
    Outside Domain URLs: {}
    Total Words: {}
    URLs in Queue: {}
    '''.format(num_pages_to_crawl,
               len(visited),
               len(url_tracker),
               minutes,
               seconds,
               len(dead_links),
               len(outside_domain),
               len(description_words_all),
               url_queue.qsize())

    print(diagnostic)

    return (url_tracker, 
            outside_domain,
            dead_links,
            description_words_all,
            url_num_reference,
            diagnostic,
            visited)

if __name__ == "__main__":
	go(num_pages_to_crawl)

#url_tracker, outside_domain, failed_reads, description_words_all, url_num_reference, diagnostic = chiscrape.go(200)




