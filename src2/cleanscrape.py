import urllib.parse
import requests
import os
import bs4
import queue
from util import *
import time
import sys
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import re
import pandas as pd
from datetime import datetime

OMIT_WORDS = ['chicago', 'city','department', 'spec', 'council', 'please']

class dataset(object):
    def __init__(self, output):
        self.scraped_data = output[0]
        self.outside_domain = output[1]
        self.dead_links = output[2]
        self.description_words_all = output[3]
        self.url_num_reference = output[4]
        self.diagnostic = output[5]
        self.num_visits = len(self.scraped_data)
        self.unique_domains = output[7]
        self.failed_reads = output[8]
        self.queued_urls = output[9]

    def __repr__(self):
        return self.diagnostic

def scrape_description_text(soup):
    '''
    Scrapes text from body of a City of Chicago web page, tokenizes, filters
    out characters that are not words stopwords. Returns all words in a list.
    Inputs:
        - soup (bs4 Object): soup from a web html page
    Outputs:
        - cleaned_words (list of strings): list of all tokenized words
    '''
    try:
        text_tags = soup.find_all('p')
        text = ''
        for text_tag in text_tags:
            text += text_tag.text + '\n'
    except Exception as e:
        print(e)

    return text

def tokenize_words(text):
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
    '''
    '''
    parsed_url = urllib.parse.urlparse(url)
    loc = parsed_url.netloc
    loc_len = len(loc) - 4
    lim_len = len(limiting_domain)
    if (limiting_domain in loc) and (loc_len != lim_len):

        return url


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
        - scraped_data: (dict of lists) list of urls that have been visited.

    Returns: None - the function will add to the any url not visited before.
    '''
    urls = get_urls(soup, class_)
    outside = []
    full_urls = []
    ignore = ['press_room', 'data.', 'test311','311api.c', '311request.', 'news','node', 'PhoneBook', 'https://www.cityofchicago.org/city/en/depts/mopd/auto_generated.html']
    email_addresses = []
    for url in urls:
        url = remove_fragment(url)
        if url == '':
            continue
        if 'mailto' in url:
            email_addresses.append(url)
        if not is_absolute_url(url):
            url = convert_if_relative_url(true_url, url)
            full_urls.append(url)
        if is_outside_domain(url, limiting_domain, return_ = True):
            outside_domain.append(url)
            outside.append(url)
        if site_prefix(url, limiting_domain):
            if 'mailto' not in url:
                    outside_domain.append(url)
                    outside.append(url)
        if is_url_ok_to_follow(url, limiting_domain, limiting_path, ignore):
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





def unique_url_domains(outside):
    unique_domains = set() 
    for url in outside:
        parsed_url = urllib.parse.urlparse(url)
        netloc = parsed_url.netloc
        if 'www' in netloc:
            netloc = netloc[4:]
        unique_domains.add(netloc)
    return unique_domains


def dataset_to_dataframe(dataset, columns = None):
    columns = ['dept', 'title', 'url', 'button', 'i_want_to',
           'nav', 'num_email_addresses', 'email_addresses',
           'pdf_count', 'pdf_urls', 'ext_link_count', 'ext_links', 
           'outside_domain', 'description_words']
    data_rows = dataset.scraped_data
    df = pd.DataFrame(columns = columns)
    for page, data in data_rows.items():
        df.loc[page] = [data[0], data[1], data[2],
                        data[3], data[4], data[5], data[6],
                        "; ".join(data[7]), data[8],
                        "; ".join(data[9]), data[10],
                        "; ".join(data[11]), "; ".join(data[12]),
                        "; ".join(data[13])]

    return df


def load_queued(filename, queue, visited, ignore=None):
    queue_df = pd.read_csv(filename)
    queued_urls = list(queue_df['0'])
    if ignore:
        for url in queued_urls:
            if ignore not in url and url not in visited:
                queue.put(url)
    else:
        for url in queued_urls and url not in visited:
            if url not in visited:
                queue.put(url)

def load_visited(filename, visited):
    visited_df = pd.read_csv(filename, encoding='iso-8859-1', index_col = 0)
    visited_urls = list(visited_df.url)
    for url in visited_urls:
        visited.add(url)


def go(num_pages_to_crawl, starting_url, limiting_domain= None, already_visited_file = None, queue_up_file = None):
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
    limiting_path =  ""#'svcs' #'/city/en/depts/fin/'
    soup_part = 'container-fluid container-body'
    visited = set()
    if already_visited_file:
        load_visited(already_visited_file, visited)
    url_queue = queue.Queue()
    if queue_up_file:
        load_queued(queue_up_file, url_queue, visited, 'PhoneBook')
    scraped_data = {}
    outside_domain = []
    failed_reads = []
    dead_links = []
    description_words_all = []
    url_num_reference = {}

    while visit_counter < num_pages_to_crawl:
        
        try:
            if visit_counter != 0 and url_queue.qsize() == 0:
                break
            if visit_counter == 0 and not queue_up_file:
                current_url = starting_url
            else:
                current_url = url_queue.get()
            request = get_request(current_url)
            try:
                true_url = get_request_url(request)
            except:
                dead_links.append((visit_counter, current_url))
                continue

            if true_url in visited:
                print(current_url)
                print('VISITED!')
                continue

            time_elapsed = round(time.time() - start,2)
            est_time_elapsed = convert_seconds_to_min_sec(time_elapsed)
            time_remaining = (time_elapsed/(visit_counter+1)) * (num_pages_to_crawl - visit_counter)
            est_time_remaining = convert_seconds_to_min_sec(time_remaining)
            print(visit_counter, "--- Time Elapsed: ", est_time_elapsed , "---- Est. Time Remaining: ", est_time_remaining, '---Q Size: ', url_queue.qsize(), '\n', "-", true_url)
            
            soup = request_to_soup(request, true_url)

            try:
                outside, email_addresses, urls = clean_and_queue_urls(soup, true_url, limiting_domain, 
                    outside_domain, url_queue, visited,
                    limiting_path = limiting_path, class_ = soup_part)
            except:
                failed_reads.append(true_url)
                continue

            pdf_urls, pdf_count = count_pdfs(urls)
            page_title = soup.title.text.strip()
            description_words = scrape_description_text(soup)
            if type(description_words) != str:
                description_words_all += description_words

        
            unique_domains = unique_url_domains(outside)

            visit_counter += 1
            visited.add(true_url)
            scraped_data[visit_counter] = ((dept, page_title, true_url, 
                                         button, i_want_to, nav, len(email_addresses), 
                                         email_addresses, pdf_count, pdf_urls, len(outside), 
                                         outside, unique_domains, description_words))
            url_num_reference[true_url] = visit_counter
        
        except:
            failed_reads.append(true_url)


        #time.sleep(1)
    end = time.time()
    total_seconds = end - start
    minutes, seconds = convert_seconds_to_min_sec(total_seconds, True)

    unique_domains_all = unique_url_domains(outside_domain)

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
               len(scraped_data),
               minutes,
               seconds,
               len(dead_links),
               len(outside_domain),
               len(description_words_all),
               url_queue.qsize())

    print(diagnostic)

    return (scraped_data, 
            outside_domain,
            dead_links,
            description_words_all,
            url_num_reference,
            diagnostic,
            visited,
            unique_domains_all,
            failed_reads,
            list(url_queue.queue))

def start(num_pages_to_crawl, starting_url, limiting_domain= None, already_visited_file = None, queue_up_file = None, filename = 'data_output_'):
    output = go(num_pages_to_crawl, starting_url, limiting_domain= None, already_visited_file, queue_up_file)
    data = dataset(output)
    dead_links = data.dead_links
    df_dead_links = pd.DataFrame(dead_links)
    df = dataset_to_dataframe(data)
    df.to_csv(filename + current_time_str() + '.csv')
    df_dead_links.to_csv('dead_links_' + current_time() + '.csv')
    queued = pd.DataFrame(data.queued_urls)
    queued.to_csv('queued_' + current_time() + '.csv')
    return data


if __name__ == "__main__":
    if sys.argv[2] and sys.argv[3]:
        start(int(sys.arg[1], str(sys.argv[2]), str(sys.argv[3])))
    else:
        start(int(sys.argv[1]))

def current_time_str():
    current_time_list = []
    current_time_list.append(str(datetime.now().month))
    current_time_list.append(str(datetime.now().day))
    current_time_list.append(str(datetime.now().hour))
    current_time_list.append(str(datetime.now().minute))
    current_time = '_'.join(current_time_list)
    return current_time


#url_tracker, outside_domain, failed_reads, description_words_all, url_num_reference, diagnostic = chiscrape.go(200)




