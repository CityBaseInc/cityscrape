import urllib.parse
import requests
import os
import bs4
import csv
import queue
from src2.scrapeutil import *
import time
import sys
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import re
import traceback
import pandas as pd
from datetime import datetime

OMIT_WORDS = ['chicago', 'city','department', 'spec', 'council', 'please']

class WebScrape(object):
    def __init__(self, starting_url, limiting_domain = '', limiting_path = '',
                 urls_from_class = '', text_from_class = ''):
        self.starting_url = starting_url
        self.limiting_domain = limiting_domain
        self.limiting_path = limiting_path
        self.scraped_data = None
        self.dead_links = None
        self.diagnostic = None
        self.failed_reads = None


    def scrape(self, num_pages_to_crawl, ignore=['blah']):
        '''
        '''
        starting_url = self.starting_url
        limiting_domain = self.limiting_domain
        limiting_path = self.limiting_path
        start = time.time()
        soup_part = None
        page_id = 0
        visited = set()
        queue_set = set()
        url_queue = queue.Queue()
        url_queue.put((0, starting_url))
        soup_part = None
        failed_reads = []
        scrape_file = os.path.join('./data/scrapes/','scrape_data' + current_time_str() + '.csv')
        links = os.path.join('./data/scrapes/','links_' + current_time_str() + '.csv')
        # pdfs = os.path.join('./data/scrapes/','pdfs_' + current_time_str() + '.csv')
        dead_links = os.path.join('./data/scrapes/','dead_links' + current_time_str() + '.csv')
        failed = os.path.join('./data/scrapes/','failed_' + current_time_str() + '.csv')


        with open(scrape_file, "w", newline='\n') as f,\
             open(links, "w", newline='\n') as g,\
             open(dead_links, "w", newline='\n') as i,\
             open(failed, "w", newline='\n') as j:
            writer_f = csv.writer(f, delimiter = '`')
            writer_g = csv.writer(g, delimiter = '`')
            writer_i = csv.writer(i, delimiter = '`')
            writer_j = csv.writer(j, delimiter = '`')

            writer_f.writerow(['pdf_id','pdf_url','dl_status','scrape_status',
    							 'num_pages','num_pages_scraped','is_fillable',
    							 'text'])
            while page_id < num_pages_to_crawl:
                try:
                    if page_id != 0 and url_queue.qsize() == 0:
                        break
                    else:
                        next_url = url_queue.get()
                    # print("NEXT:", next_url)
                    from_page, current_url = next_url[0], next_url[1]
                    # print("current_url", current_url)
                    request = get_request(current_url)
                    try:
                        true_url = get_request_url(request)
                    except Exception as e:
                        print(e)
                        writer_i.writerow([from_page, current_url])
                        continue

                    if "//".join(true_url.split('//')[1:]) in visited:
                        print(current_url)
                        print('VISITED!')
                        continue
                    time_print(start, url_queue, true_url, num_pages_to_crawl,
                                                                      page_id)
                    soup = request_to_soup(request)

                    try:
                        clean_and_queue_urls(soup, page_id, true_url, limiting_domain,queue_set, url_queue, visited ,writer_g, ignore,
                            limiting_path = limiting_path, class_ = soup_part)
                    except Exception as e:
                        print (e)
                        writer_j.writerow([page_id, true_url, e])
                        traceback.print_exc()
                        continue

                    page_title = soup.title.text.strip()
                    text = scrape_text(soup)
                    visited.add("//".join(true_url.split('//')[1:]))
                    visited.add("//".join(current_url.split('//')[1:]))
                    writer_f.writerow([page_id, page_title, current_url,
                                       true_url, text])
                    page_id += 1
                    # time.sleep()

                except Exception as e:
                    print('FAILED:', e)
                    writer_j.writerow([page_id, true_url, e])
            total_seconds = time.time() - start
            minutes, seconds = convert_seconds_to_min_sec(total_seconds, True)
            diagnostic = '''
            Pages to Crawl: {}
            Pages Visited: {}
            Total Time: {} min, {} sec
            URLs in Queue: {}
            '''.format(num_pages_to_crawl,
                      len(visited),
                       minutes,
                       seconds,
                       url_queue.qsize())
            print(diagnostic)


    def __repr__(self):
        return self.diagnostic


if __name__ == "__main__":
    if sys.argv[2] and sys.argv[3]:
        start(int(sys.arg[1], str(sys.argv[2]), str(sys.argv[3])))
    else:
        start(int(sys.argv[1]))


#url_tracker, outside_domain, failed_reads, description_words_all, url_num_reference, diagnostic = chiscrape.go(200)
