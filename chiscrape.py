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


def url_to_soup(url):
    '''
    Takes a url and returns a BeautifulSoup object.

    Input:
        - url (string) the url for which html will be stored

    Returns: soup (bs4 object) the html soup
    '''
    request = util.get_request(url)
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
        words = word_tokenize(text)
        stopWords = set(stopwords.words('english'))
        for w in words:
              if w not in stopWords and (re.match(alpha, w) is not None):
                  cleaned_words.append(w)

        return cleaned_words

    else:
        return 'No text found'




def clean_and_queue_urls(soup, current_url, limiting_domain, 
    outside_domain, queue, url_tracker, limiting_path = None, 
                                                class_ = None):
    '''
    Takes a list of urls from the current page being visited and adds 
    them to the queue of urls to be visited by the scraper if they 
    have not been visited already.

    Inputs:
        - urls: (list of strings) list of urls from the current page.
        - current_url: (string) url of the page currently being visited.
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
    for url in urls:
        url = util.remove_fragment(url)
        if url == '':
            continue
        if not util.is_absolute_url(url):
            url = util.convert_if_relative_url(current_url, url)
            full_urls.append(url)
        if util.is_outside_domain(url, limiting_domain, return_ = True):
            outside_domain.append((current_url,url))
            outside.append(url)
        if util.is_url_ok_to_follow(url, limiting_domain, limiting_path):
            if url not in queue.queue:
                if url not in url_tracker:
                    queue.put(url)

    return outside, full_urls

def count_pdfs(urls):
    pdf_urls = []
    for url in urls:
        parsed_url = urllib.parse.urlparse(url)
        filename, ext = os.path.splitext(parsed_url.path)
        if ext == '.pdf':
            pdf_urls.append(url)

    return pdf_urls, len(pdf_urls)


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
    limiting_path = '/city/en/depts/cpd/'
    soup_part = 'container-fluid container-body'
    url_queue = queue.Queue()
    url_tracker = {}
    outside_domain = []
    failed_reads = []
    description_words_all = []
    url_num_reference = {}

    while visit_counter < num_pages_to_crawl:
        
        if visit_counter == 0:
            current_url = starting_url
        else:
            current_url = url_queue.get()

        print(current_url)

        soup = url_to_soup(current_url)

        try:
            outside, urls = clean_and_queue_urls(soup, current_url, limiting_domain, 
                outside_domain, url_queue, url_tracker,
                limiting_path = limiting_path, class_ = soup_part)
        except:
            failed_reads.append(current_url)
            visit_counter += 1
            continue

        pdf_urls, pdf_count = count_pdfs(urls)
        page_title = soup.title.text[24:-1]
        description_words = scrape_description_text(soup)
        if type(description_words) != str:
            description_words_all += description_words


        visit_counter += 1
        url_tracker[visit_counter] = ((page_title, current_url, pdf_count, pdf_urls, outside, description_words))
        url_num_reference[current_url] = visit_counter

        if url_queue.qsize() == 0:
            break

        #time.sleep(.5)
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
    Total Time: {} min, {} sec
    Failed Reads: {}
    Outside Domain URLs: {}
    Total Words: {}
    URLs in Queue: {}
    '''.format(num_pages_to_crawl,
               len(url_tracker),
               minutes,
               seconds,
               len(failed_reads),
               len(outside_domain),
               len(description_words_all),
               url_queue.qsize())

    print(diagnostic)

    return url_tracker, outside_domain, failed_reads, description_words_all, url_num_reference, diagnostic

if __name__ == "__main__":
	go(num_pages_to_crawl)

#url_tracker, outside_domain, failed_reads, description_words_all, url_num_reference, diagnostic = chiscrape.go(200)




