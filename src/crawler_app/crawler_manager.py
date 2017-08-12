# coding=utf-8
"""
    Crawler Manger
"""
import urlparse
from BeautifulSoup import BeautifulSoup

from src.dns_module.dns_look_up import DNSLookUp
from src.http_requests_module.http_requests import HttpRequest
from src.download_module.downloader import WebDownloader

CRAWLER_CACHE = {}


class CrawlerManager(object):
    """
    Crawler manager class
    """

    def __init__(self, url, user_agent_name='ClientRIW', dns_server_ip="81.12.151.210"):  # 81.180.223.1
        """
        Constructor
        The URl must by like this e.g.: www.something.ro, without protocol in front
        
        :param url: The URL that you want to take the IP from DNS 
        :param dns_server_ip: 
        """
        self._url = urlparse.urlparse(url)
        self._path = self._url.path
        self._host = self._url.netloc
        self._port = self._url.port if self._url.port else 80

        if self._path == "":
            self._path = "/"

        self._url = url

        self._robots_path = None
        self._ip_from_dns = []
        self._dns_reply = None
        self._new_url_ip = None
        self._user_agent = user_agent_name

        # if the url is in cache, take IP from cache
        if self._host not in CRAWLER_CACHE:

            #     self._ip_from_dns = CRAWLER_CACHE[self._host]['IP']
            #     self._new_url_ip = "http://{}/".format(self._ip_from_dns)
            #     self._robots_path = "{}robots.txt".format(self._new_url_ip)
            #
            # else:
            # if the URL is for the first time explored
            # make request to DNS Server to take the IP, then cache it
            self.__dns_object = DNSLookUp(dns_server_ip, self._host)
            self.__dns_message = self.__dns_object.create_dns_message()
            self.__dns_object.dns_look_up(self.__dns_message)
            self._dns_reply = self.__dns_object.dns_reply

            if len(self._dns_reply.keys()) > 0:

                for answer in self._dns_reply:

                    if 'IP' in self._dns_reply[answer]:

                        self._ip_from_dns.append(self._dns_reply[answer]['IP'])

                        # create robots.txt path
                        self._robots_path = "{}/robots.txt".format(self._url)

                        # cache the url
                        CRAWLER_CACHE[self._host] = {"ROBOTS_PATH": self._robots_path}

                        CRAWLER_CACHE[self._host].update(self._dns_reply[answer])

                        temp_dict = self.__explore_robots_resource()

                        CRAWLER_CACHE[self._host]['ROBOTS_CONTENT'] = temp_dict

                    else:
                        pass
                        # raise Exception("No IP from DNS Server.")

                CRAWLER_CACHE[self._host]['IP'] = self._ip_from_dns

            else:
                raise Exception("No response from DNS server => 0 Answers.")

    def __explore_robots_resource(self):
        """
        Explore robots.txt file for url
        :return: 
        """

        if self._robots_path:

            request_obj = HttpRequest()
            request_obj.get(self._robots_path)

            robots_content = request_obj.content
            result_data_set = {"Disallowed": [], "Allowed": [], 'User-agents': []}

            if isinstance(robots_content, str):
                lines = robots_content.replace('\r', '').split('\n')

                for line in lines:
                    if line.startswith('Allow'):
                        result_data_set["Allowed"].append(line.split(': ')[1].split(' ')[0])

                    elif line.startswith('Disallow'):
                        result_data_set["Disallowed"].append(line.split(': ')[1].split(' ')[0])

                    elif line.startswith('User-agent'):  # this is for disallowed url
                        result_data_set["User-agents"].append(line.split(': ')[1].split(' ')[0])

                return result_data_set
            else:
                result_data_set = {"Disallowed": ['ClientRIW'], "Allowed": [], 'User-agents': []}
                return result_data_set

        else:
            raise Exception("No robots.txt file for this domain: {}".format(self._url))

    def get_resource_from_url(self):
        """
        Get the resource from URL
        :return: 
        """
        next_links = []
        flag_download = True

        user_agent_list = CRAWLER_CACHE[self._host]['ROBOTS_CONTENT']["User-agents"]
        disallowed_list = CRAWLER_CACHE[self._host]['ROBOTS_CONTENT']["Disallowed"]

        # check if our user agent name is in domain name user-agents
        if self._user_agent in user_agent_list or '*' in user_agent_list:

            if self._path in disallowed_list:
                return next_links

            else:
                request_obj = HttpRequest()
                request_obj.get(self._url)

                content = request_obj.content
                soup_object = BeautifulSoup(content)

                # iterate the tags of document
                for tag in soup_object.findAll():

                    if tag.name == 'meta':
                        if ('name', 'robots') in tag.attrs:
                            if ('content', 'noindex, nofollow') in tag.attrs or ('content', 'index, nofollow') in tag.attrs:
                                flag_download = False
                                break

                            if ('content', 'NOINDEX, NOFOLLOW') in tag.attrs or ('content', 'INDEX, NOFOLLOW') in tag.attrs:
                                flag_download = False
                                break

                    elif tag.name == 'a':
                        link = str(tag.attrs[0][1])
                        if 'http' in link or 'https' in link:
                            next_links.append(link)

                if flag_download:
                    downloader_object = WebDownloader()
                    downloader_object.get_resource(self._url)

        return next_links
