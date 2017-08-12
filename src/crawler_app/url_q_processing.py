# coding=utf-8
"""
    Queue module for processing urls and create an CRAWLER_CACHE
"""


class UrlQueueProcessing(object):
    """
    Q class
    """

    def __init__(self):
        """
        Constructor
        """
        self.__queue = []

    @property
    def queue(self):
        """
        Return the Q
        :return: 
        """
        return self.__queue

    def is_in_q(self, url):
        """
        Check if the url is in Q
        :param url: 
        :return: 
        """
        if url in self.__queue:
            return True
        else:
            return False

    def add(self, url):
        """
        Add a new url to explore
        :param url: The URL that you want to add
        :return: 
        """
        if not self.is_in_q(url):
            self.__queue.append(url)
        else:
            print "(URL: {}) already in Queue".format(url)

    def delete(self, url):
        """
        Remove an item from que
        :return: 
        """
        if self.is_in_q(url):
            self.__queue.remove(url)
