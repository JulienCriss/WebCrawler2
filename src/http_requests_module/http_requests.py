# coding=utf-8
"""
    Client HTTP Requests
"""
import socket
import urllib2
import urlparse


class HttpRequest(object):
    """
    Make HTTP request
    """

    def __init__(self):
        self._socket_connection = None
        self._url = None
        self._path = None
        self._port = 80
        self._host = None
        self._http_headers = ""
        self._response_headers = None
        self._response_items = {}

        self.__file_content = None

    @property
    def host(self):
        """
        Get Hostname
        :return: 
        """
        return self._url.netloc

    @property
    def content(self):
        """
        Return the content of file collected via request
        :return: 
        """
        return self.__file_content

    def get(self, url):
        """
        Make GET request
        :param url: 
        :return: 
        """
        self._socket_connection = socket.socket()
        self._socket_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self._url = urlparse.urlparse(url)
        self._path = self._url.path
        self._host = self.host
        self._port = self._url.port if self._url.port else 80

        if self._path == "":
            self._path = "/"

        # create the headers for request
        self._http_headers = "GET {} HTTP/1.1\r\n" \
                             "Host: {}\r\n" \
                             "User-Agent: {}\r\n" \
                             "Connection: close\r\n" \
                             "\r\n".format(self._path, self._host, "ClientRIW")

        # create the connection
        self._socket_connection.connect((self._host, self._port))
        self._socket_connection.send(self._http_headers)

        self._response_headers = (self._socket_connection.recv(1024))

        # parse the response headers
        self.__parse_response()

        # close socket connection
        self._socket_connection.shutdown(1)
        self._socket_connection.close()

        # check status code and get the resource from
        if self._response_items['status_code'] == '200':
            return self.__get_resource(url)

        # if we have redirect, take the location from redirect
        elif self._response_items['status_code'] == '301':
            if 'Location' in self._response_items:
                url = self._response_items['Location']

                return self.__get_resource(url)
            else:
                raise Exception("Redirect was found but 'Location' is missing from headers.")
        elif self._response_items['status_code'] == '404':
            return 0
        else:
            raise Exception("Error: status code '{}' is not handled. ".format(self._response_items['status_code']))

    def __parse_response(self):
        """
        Parse the response and create a dictionary with the elements from response
        :return: 
        """
        lines = self._response_headers.split("\r\n")
        self._response_items["http_version"], self._response_items['status_code'], self._response_items['status_message'] = lines[0].split(' ', 2)

        for line in lines[1:]:
            if line == '<html>':
                break
            if line != '' and line != 'b2':
                key, value = line.split(':', 1)
                self._response_items[key] = value.strip()

    def __get_resource(self, url):
        """
        Get a resource from a domain with GET method
        :param url: The url that you want to retrieve
        :return: 
        """
        self._url = urlparse.urlparse(url)
        self._path = self._url.path
        self._host = self.host
        self._port = self._url.port if self._url.port else 80

        if self._path == "":
            self._path = "/"

        self._http_headers = {"GET": "{} HTTP/1.1\r\n".format(self._path),
                              "Host": "{}\r\n".format(self._host),
                              "User-Agent": "{}\r\n".format("ClientRIW\r\n"),
                              "Connection": "close\r\n"}

        try:
            request = urllib2.Request(url, headers=self._http_headers)
            temp_response = urllib2.urlopen(request)

            self._response_headers = {"status_code": temp_response.code, "status_message": temp_response.msg}

            for header in temp_response.info().headers:

                key, value = header.split(':', 1)
                if key == 'Set-Cookie':
                    if key not in self._response_headers:
                        self._response_headers[key] = [value.strip()]
                    else:
                        self._response_headers[key].append(value.strip())
                else:
                    self._response_headers.update({key: value.strip()})

            # get resource content
            self.__file_content = temp_response.read()
            return self.__file_content

        except urllib2.HTTPError as exc:
            print exc
