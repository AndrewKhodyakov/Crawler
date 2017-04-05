#!/usr/bin/env python
"""
    Crawler - parse html and get target info.
    html struct in struct.json
"""
import os
import sys
import json
import csv
import uuid

from bs4 import BeautifulSoup
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
        self._raw_html_page = None
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
        self._struct = json.loads(open(path_to_struct, 'rt').read())

    def _set_target_url(self, target_url):
        """
        set target url
        target_url: target url
        """
        if  target_url.split('://')[0] != 'http':
            msg = 'Check target url {}'.format(target_url)
            raise SyntaxError(msg)

        self._target_url = target_url

    def _struct_wolker(self, next_tag, soup):
        """
        Parse text
        target_folder: key with next node
        """
        target_data = None
        node = self._struct.get(next_tag)
        soup = soup

        while node.get(next_tag) is not None:
#            #TODO тут берем данные из супа
#            soup.get(node.get(marker_tag))
#            #тут делаем шаг вниз в иерархии
#            soup.make_a_step_down()
#            node = node.get(next_tag)
            pass

        return target_data


    def get_one_page(self):
        """
        get one page generator
        """
        one_page_data = []
        resp = requests.get(self._target_url)
        if resp.status_code != 200:
            msg = 'url - is not available, status code {}'.format(\
                resp.status_code)
            raise IOError(msg)

        #находим структуру со списком
        self._struct_wolker('next', BeautifulSoup(resp.text))
        #перем данные для каждого элемента
        self._struct_wolker('next', BeautifulSoup(resp.text))
        #чекаем есть ли следующая страница - идем туда

        yield one_page_data

    def get_all_data(self):
        """
        Get all data from target url by installed struct
        """
        all_data = []
        for one_page_data in self.get_one_page():
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
            struct_node = lambda tag, cls_attr, target, text, next_node:\
                '{' + '"tag":"{0}", "class":"{1}", "target":"{2}", "text":"{3}", "next":"{4}"'.\
                format(tag, cls_attr, target, text, next_node) + '}'

            struct = '{' + '"item_folder":{0}, "item":{1}, "next_page":{2}'.format(\
                    struct_node("body", "null", "null", "null",\
                        struct_node("div", "first_level", "null", "null",\
                                struct_node("div", "second_level", "text", "null", "null")\
                            )\
                        ),\
                    struct_node("div", "item", "null", "null",\
                        struct_node("h3", "item_title", "null", "null",\
                            struct_node("a", "item_title_desription", "title", "null", "null")\
                        )\
                    ),\
                    struct_node("div", "pagination js-pages", "null", "null",\
                        struct_node("div", "pagination-nav clearfix", "null", "null",\
                            struct_node("a", "pagination-nav js-pagination-next",\
                                "herf", "Следующая страница", "null")\
                        )\
                    )\
            ) + '}'
            print('\n', struct, '\n')
            self.struct_json = StringIO(struct)

            self.first_url = 'http://test.com/catalog/1'
            self.second_url = 'http://test.com/catalog/2'

            head = '<html><head><title>Page title</title></head>'
            html_node = lambda tag, attr, attr_value, text: '<{0} {1}="{2}">{3}</{0}>'.\
                format(tag, attr, attr_value, text)
            html_a_node = lambda tag, cls_value, herf_val, text:\
                '<{0} class="{1}" herf={2}>{3}</{0}>'.format(tag, cls_value, herf_val, text)

            first_item = html_node('div', 'class', 'item',\
                 html_node('h3', 'class', 'item_title',\
                    html_node('a', 'class', 'item_title_desription', '1_p FIRST ITEM')))

            second_item = html_node('div', 'class', 'item',\
                 html_node('h3', 'class', 'item_title',\
                    html_node('a', 'class', 'item_title_desription', '2_p SECOND ITEM')))

            body = html_node('body', 'class', ' ',\
                html_node('div', 'class', 'first_level',\
                     html_node('div', 'class', 'second_level', (first_item + second_item)\
                    )\
                ) +\
                html_node('div', 'class', 'pagination js-pages',\
                    html_node('div', 'class', 'pagination-nav clearfix',\
                        html_a_node('a', 'pagination-nav js-pagination-next', self.second_url,\
                         'Следующая страница →'))\
                )\
            )

            self.first_html = head + body

            print('\n', self.first_html, '\n')

            self.second_html = None

            responses.add(responses.GET, self.first_url, self.first_html, status=200)
            responses.add(responses.GET, self.second_url, self.second_html, status=200)

        def test_get_html_from_url(self):
            """
            test get html
            """
            print(2)

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

    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestCrawler))
    unittest.TextTestRunner().run(suite)

def _read_args_and_run():
    """
    Set execute mode
    """
    arg = sys.argv
    n_arg = len(arg)

    help_msg = 'Input next arguments:\n' +\
        '\t' + '--run_self_test - for run unittests;\n' +\
        '\t' + '--get_data url_to_html - for read from url.\n'

    if (n_arg > 1) & (n_arg <= 3):

        if (n_arg == 2) & ('--run_self_test' in arg[1]):
            _run_unittests()

        elif (n_arg == 4) & ('--get_data' in arg[1]):
            _get_mode(arg[2], arg[3])

        else:
            print(help_msg)

    else:
        print(help_msg)


if __name__ == "__main__":
    _read_args_and_run()
