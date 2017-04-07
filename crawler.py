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

    def _struct_wolker(self, struct_key, soup):
        """
        Parse text
        struct_key: ключ искомой структуры
        """
        out = []
        node = self._struct.get(struct_key)
        soup = soup

        for inst in soup.body.findAll(node.get('tag')):
            cls_attr = inst.get('class')
            if len(inst.get('class')) !=0:
                if inst.pop() == node.get('cls_attr'):
                    out.append(node.get('target'))                    

        return out

    def get_one_page_data(self, url):
        """
        get one page generator
        """
        one_page_data = []
        next_url = None
        resp = requests.get(url)
        if resp.status_code != 200:
            msg = 'url - is not available, status code {}'.format(\
                resp.status_code)
            raise IOError(msg)

        node = self._struct.get('items')
        soup = BeautifulSoup(resp.text, 'html.parser')

        for inst in soup.body.findAll(node.get('tag')):
            cls_attr = inst.get('class')

            if len(cls_attr) !=0:
                cls_attr = cls_attr.pop()


                if cls_attr == node.get('cls_attr'):
                    if node.get('text') is None:
                        one_page_data.append(node.get('target'))                    
                    if node.get('text') == inst.get('text'):
                        next_url = inst.get(node.get('target'))


        yield one_page_data, next_url


    def get_all_pages_data(self):
        """
        Get all data from target url by installed struct
        """
        all_data = []
        soup = BeautifulSoup(resp.text, 'html.parser')

        urls = [self.target_url]
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

    class TestCrawler(unittest.TestCase):
        """
        Test for crawler
        """
        @responses.activate
        def setUp(self):
            """
            setup test data
            """
            struct_node = lambda tag, cls_attr, target, text:\
                {'tag':tag, 'class':cls_attr, 'target':target, 'text':text}

            self._struct_json = json.dumps({'items':\
                struct_node('a', 'item_title_desription', 'title', None),\
                'next_page':struct_node('a', 'pagination-nav js-pagination-next',\
                    'herf', 'Следующая страница')})

#            self._struct_json = '{' + '"item_folder":{0}, "item":{1}, "next_page":{2}'.format(\
#                    struct_node("body", "null", "null", "null",\
#                        struct_node("div", "first_level", "null", "null",\
#                                struct_node("div", "second_level", "text", "null", "null")\
#                            )\
#                        ),\
#                    struct_node("div", "item", "null", "null",\
#                        struct_node("h3", "item_title", "null", "null",\
#                            struct_node("a", "item_title_desription", "title", "null", "null")\
#                        )\
#                    ),\
#                    struct_node("div", "pagination js-pages", "null", "null",\
#                        struct_node("div", "pagination-nav clearfix", "null", "null",\
#                            struct_node("a", "pagination-nav js-pagination-next",\
#                                "herf", "Следующая страница", "null")\
#                        )\
#                    )\
#            ) + '}'

            self._first_url = 'http://test.com/catalog/1'
            self._second_url = 'http://test.com/catalog/2'

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
                    html_node('a', 'class', 'item_title_desription', '1_p SECOND ITEM')))

            body = html_node('body', 'class', ' ',\
                html_node('div', 'class', 'first_level',\
                     html_node('div', 'class', 'second_level', (first_item + second_item)\
                    )\
                ) +\
                html_node('div', 'class', 'pagination js-pages',\
                    html_node('div', 'class', 'pagination-nav clearfix',\
                        html_a_node('a', 'pagination-nav js-pagination-next', self._second_url,\
                         'Следующая страница →'))\
                )\
            )

            self._first_html = head + body

            first_item = html_node('div', 'class', 'item',\
                 html_node('h3', 'class', 'item_title',\
                    html_node('a', 'class', 'item_title_desription', '2_p FIRST ITEM')))

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
                        html_a_node('a', 'pagination-nav js-pagination-next', self._first_url,\
                         '← Предыдущая'))\
                )\
            )
            self._second_html = head + body

            responses.add(responses.GET, self._first_url, self._first_html, status=200)
            responses.add(responses.GET, self._second_url, self._second_html, status=200)

        def test_get_html_from_url(self):
            """
            test get html
            """
            crawler = Crawler(target_url=self._first_url)
            crawler._struct = json.loads(self._struct_json)
#            crawler.get_one_page()

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
