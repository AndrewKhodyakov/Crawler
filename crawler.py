#!/usr/bin/env python
"""
    Crawler - parse html and get target info.
    html struct in struct.json
"""
import os
import sys
import json
import csv
import uuid.uuid4

import bs4
import requests


class  Crawler:
    """
    crawler
    """
    def __init__(self, path_to_struct=None, target_url=None):
        """
        Initialization
        path_to_struct: path to struct.json
        target_url: url for request
        """
        self._config_path = None
        self._struct = None
        self._target_url = None

        if target_url:
            self._set_target_url(target_url)

        if path_to_struct:
            self.load_struct(path_to_struct)

    def load_struct(self, path_to_struct):
        """
        load struct from file
        path_to_struct: path to struct.json
        """
        if os.path.exists(path_to_struct) is False:
            msg = 'Check path {}'.format(path_to_struct)
            raise FileNotFoundError(msg)

        self._config_path = path_to_struct
        self._struct = json.loaddata(open(path_to_struct, 'rt').read())

    def _set_target_url(self, target_url):
        """
        set target url
        target_url: target url
        """
        if  target_url.split('://')[0] != 'http':
            msg = 'Check target url {}'.format(target_url)
            raise SyntaxError(msg)

        self._target_url = target_url

    def get_one_page(self):
        """
        get one page generator
        """
        one_page_data = []
        resp = requests.get(self.target_url)
        if resp.status_code != 200:
            msg = 'url - is not available, status code {}'.format(\
                resp.status_code)
            raise IOError(msg)

        soup = bs4(resp.text)
            
        yield one_page_data

    def get_all_data(self):
        """
        Get all data from target url by installed struct
        """
        all_data = [] 
        for one_page_data in get_one_page():
            all_data = all_data + one_page_data

        return all_data


    def __repr__(self):
        """
        print instance
        """
        print('Crowler, config: {}, url in_work: {}'.format(\
            self._config_path, self._target_url))

def _get_mode(struct_path, url):
    """
    Get data from url
    """
    crawler = Crawler()

def _run_unittests():
    """
    Run unittest
    """
    import responses
    import unittest
    from io import StringIO

    class TestCrawler(unittest.TestCase):
        """
        Test for crawler
        """
        @responses.activate
        def setUp(self):
            """
            setup test data
            """
            self.struct_json = StringIO("""
                {
                    "item_folder":{
                       "tag": "body",
                       "class": null,
                       "next":{
                            "tag": "div",
                            "class":"first_level",
                            "next" :{
                                "tag": "div",
                                "class":"second_level",
                                "next" :null
                            }
                        }
                    },

                    "item":{
                            "tag": "div",
                            "class": "target_folder",
                            "target":null,
                            "next" :{
                                "tag": "h3",
                                "class": "Target_folder_title",
                                "target":null,
                                "next" :{
                                    "tag": "a",
                                    "class": "Target_folder_title_description",
                                    "target":"title",
                                    "next" :null
                                    }
                            }
                    },

                    "next_page":{
                            "tag": "div",
                            "class": "pagination js-pages",
                            "target":null,
                            "next" :
                                {
                                "tag": "div",
                                "class": "pagination-nav clearfix",
                                "target":null,
                                "next" :
                                [
                                    {
                                    "tag": "a",
                                    "class": "pagination-nav
js-pagination-next",
                                    "target":"herf",
                                    "text": "Следующая страница →",
                                    "next" :null
                                    },
                                    {
                                    "tag": "a",
                                    "class": "pagination-nav
js-pagination-next",
                                    "target":"herf",
                                    "text": "Последняя",
                                    "next" :null
                                    }
                                ] 
                            }
                }
            """)

            self.first_html = '<html><head><title>Page title</title></head>'
            self.second_html = ''

            self.first_url = 'http://test.com/catalog/'
            self.second_url = 'http://test.com/catalog/'
            responses.add(responses.GET, self.first_url, self.first_html,
status=200)
            responses.add(responses.GET, self.second_url, self.second_html,
status=200)

        def test_get_html_from_url(self):
            """
            test get html
            """
            pass

        def test_get_next_page(self):
            """
            test get html
            """
            pass

        def test_save_data(self):
            """
            test get html
            """
            pass

def _read_args_and_run():
    """
    Set execute mode
    """
    arg = sys.argv
    n_arg = len(arg)

    help_msg = 'Input next arguments:\n'
    help_msg = help_msg + '\t' + '--run_self_test - for run unittests;\n'
    help_msg = help_msg + '\t' + '--get_data url_to_html - for read from url.\n'

    if (n_arg > 1) & (n_arg <= 3):

        if (n_arg == 2) & ('--run_self_test' in arg[1]):
            _run_unittests()

        elif (n_arg == 3) & ('--get_data' in arg[1]):
            _get_mode(arg[2])

        else:
            print(help_msg)

    else:
        print(help_msg)


if __name__ == "__main__":
    _read_args_and_run()
