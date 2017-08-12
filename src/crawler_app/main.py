# coding=utf-8
"""
    Main Test App
"""
import os
from url_q_processing import UrlQueueProcessing
from crawler_manager import CrawlerManager

if __name__ == "__main__":
    q = UrlQueueProcessing()
    q.add('http://www.tuiasi.ro')

    for url in q.queue:
        temp_object = CrawlerManager(url)
        next_links = temp_object.get_resource_from_url()

        for link in next_links:
            q.add(link)

        # q.delete(url)

    print 'Done ...'
