import urllib.parse
import requests
import os
import bs4
import queue
import util
import time



def url_to_soup(url):
    '''
    Takes a url and returns a BeautifulSoup object.

    Input:
        - url (string) the url for which html will be stored

    Returns: soup (bs4 object) the html soup
    '''
    request = util.get_request(url)
    html = util.read_request(request)
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
    for url in urls:
        url = util.remove_fragment(url)
        if url == '':
            continue
        if not util.is_absolute_url(url):
            url = util.convert_if_relative_url(current_url, url)
        if util.is_outside_domain(url, limiting_domain, return_ = True):
            outside_domain.append((current_url,url))
        if util.is_url_ok_to_follow(url, limiting_domain, limiting_path):
            if url not in queue.queue:
                if url not in url_tracker:
                    queue.put(url)


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
    limiting_path = '/city/en/depts/fin/'
    soup_part = 'container-fluid container-body'
    url_queue = queue.Queue()
    url_tracker = []
    outside_domain = []

    while visit_counter < num_pages_to_crawl:
        
        if visit_counter == 0:
            current_url = starting_url
        else:
            current_url = url_queue.get()

        print(current_url)

        soup = url_to_soup(current_url)

        clean_and_queue_urls(soup, current_url, limiting_domain, 
            outside_domain, url_queue, url_tracker,
            limiting_path = limiting_path, class_ = soup_part)

        visit_counter += 1
        url_tracker.append(current_url)

        if url_queue.qsize() == 0:
            break

        # time.sleep(2)
    print(url_queue.qsize())
    end = time.time()
    print(end - start)
    return url_tracker, len(url_tracker), outside_domain


if __name__ == "__main__":
	go(num_pages_to_crawl)




