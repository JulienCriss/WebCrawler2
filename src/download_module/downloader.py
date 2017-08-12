# coding=utf-8
"""
    Download module
    
    This module will download the resources and will save them on disk
"""
import os
from src.http_requests_module.http_requests import HttpRequest


class WebDownloader(HttpRequest):
    """
    Download resources
    """

    def __init__(self):
        super(WebDownloader, self).__init__()

        self.url = None
        self._file_content = None
        self._current_working_directory = os.getcwd().split('\\')[:-1]
        self._current_working_directory.append('work_dir')

    def get_resource(self, url):
        """
        Get a resource from site if is available
        :param url: 
        :return: 
        """
        self.url = url
        self._file_content = self.get(self.url)

        if self._file_content:
            self.__save_resource()

    def __save_resource(self):
        """
        Save the resource on disk
        :return: 
        """
        temp_list = self.url.split('/')
        temp_list = [item for item in temp_list if item != '']

        # remove first item which is the protocol
        temp_list = temp_list[1:]

        # we have just the domain in list, the page will be index.html
        if len(temp_list) == 1:
            temp_list.append("index.html")

            tree_directory = os.path.join('\\'.join(self._current_working_directory))

            # create tree directories
            for item in temp_list[:-1]:
                tree_directory = os.path.join(tree_directory, item)

                if not os.path.exists(tree_directory):
                    print "Creating {} ...".format(tree_directory)
                    os.makedirs(tree_directory)
            file_to_save = os.path.join(tree_directory, temp_list[-1])

            # save the file
            with open(file_to_save, 'w') as file_handler:
                file_handler.write(self._file_content)
        else:

            tree_directory = os.path.join('\\'.join(self._current_working_directory))

            # create tree directories
            for item in temp_list[:-1]:
                tree_directory = os.path.join(tree_directory, item)

                if not os.path.exists(tree_directory):
                    print "Creating {} ...".format(tree_directory)
                    os.makedirs(tree_directory)

            file_to_save = os.path.join(tree_directory, temp_list[-1])

            # save the file
            with open("{}.html".format(file_to_save), 'w') as file_handler:
                file_handler.write(self._file_content)


if __name__ == "__main__":
    a = WebDownloader()
    a.get_resource("http://www.tuiasi.ro")  # "http://www.tuiasi.ro/admitere/media-pack"
    a.get_resource("http://www.tuiasi.ro/admitere/media-pack")
