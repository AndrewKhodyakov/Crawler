#!/usr/bin/env python
"""
    Crawler - parse html and get target info.
    html struct in struct.json
"""
import os
import sys
import time
import json
import csv
import pandas as pd
from itertools import count

from bs4 import BeautifulSoup
import requests

def _get_data_by_struct(struct, soup, marker=None,add_text=False):
    """
    """
    out = []
    for inst in soup.body.findAll(struct.get('tag'),\
        class_=struct.get('class'), string=marker):
        target = struct.get('target')

        if add_text:
            data = [inst.get(target), getattr(inst,'text')]
        else:
            data = inst.get(target)
        out.append(data)

    if len(out) == 0:
        msg = 'cant find struct {} in html'.format(struct)
        raise SyntaxError(msg)

    return out

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

    def set_struct(self, struct_dict):
        """
        """
        self._struct = struct_dict

    def _set_target_url(self, target_url):
        """
        set target url
        target_url: target url
        """
        split_url = target_url.split('/')
        if  'http' not in split_url[0]:
            msg = 'Check target url {}'.format(target_url)
            raise SyntaxError(msg)

        self._base_url = '{0}//{1}'.format(split_url[0], split_url[2])
        self._target_url = target_url


    def get_one_page_data(self, url):
        """
        get one page generator
        """
        print('\t','-'*10)
        print('Sent requests to url: {}'.format(url))

        time.sleep(1)
        resp = requests.get(url)
        if resp.status_code != 200:
            msg = 'url - is not available, status code {}'.format(\
                resp.status_code)
            raise IOError(msg)

        soup = BeautifulSoup(resp.text, 'html.parser')
        one_page_data = _get_data_by_struct(self._struct.get('items'), soup)

        next_url = _get_data_by_struct(self._struct.get('next_page'),\
             soup, marker=self._struct.get('text'), add_text=True)
        next_url = next_url.pop()

        return one_page_data, next_url


    def get_all_pages_data(self, save_to_file=False):
        """
        Get all data from target url by installed struct
        """
        all_data = []
        page_marker = None
        next_url = [self._target_url]
        _count = count()
        while next_url is not None:
            one_page_data, next_url = self.get_one_page_data(next_url[0])

            if save_to_file:
                self._save_to_file(('./' + str(next(_count)) + '.csv'), one_page_data)

            all_data = all_data + one_page_data
            if not page_marker:
                page_marker = next_url[1]

            next_url[0] = self._base_url + next_url[0]
            if  page_marker != next_url[1]:
                next_url = None

        self._save_to_file(('./all_data.csv'), all_data)
        return all_data

    def _save_to_file(self, f_name, data):
        """
        save data
        """
        with open(f_name, 'wt') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerows([data])

    def __repr__(self):
        """
        print instance
        """
        print('Crowler, config: {}, url in_work: {}'.format(\
            self._config_path, self._target_url))

def _run(struct_path, url):
    """
    Get data from url
    """
    crawler = Crawler(struct_path, url)
    data = crawler.get_all_pages_data(save_to_file=True)

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

            self._first_url = 'http://test.com/catalog/1'
            self._second_url = 'http://test.com/catalog/2'

            head = '<html><head><title>Page title</title></head>'
            html_node = lambda tag, attr, attr_value, text: '<{0} {1}="{2}">{3}</{0}>'.\
                format(tag, attr, attr_value, text)

            html_a_item_node = lambda tag, cls_value, title_val, text:\
                '<{0} class="{1}" title={2}>{3}</{0}>'.format(tag, cls_value, title_val, text)
            html_a_link_node = lambda tag, cls_value, herf_val, text:\
                '<{0} class="{1}" herf={2}>{3}</{0}>'.format(tag, cls_value, herf_val, text)

            first_item = html_node('div', 'class', 'item',\
                 html_node('h3', 'class', 'item_title',\
                    html_a_item_node('a', 'item_title_desription', '"1_p FIRST ITEM"', '1_p FIRST ITEM')))

            second_item = html_node('div', 'class', 'item',\
                 html_node('h3', 'class', 'item_title',\
                    html_a_item_node('a', 'item_title_desription', '"1_p SECOND ITEM"', '1_p SECOND ITEM')))

            body = html_node('body', 'class', ' ',\
                html_node('div', 'class', 'first_level',\
                     html_node('div', 'class', 'second_level', (first_item + second_item)\
                    )\
                ) +\
                html_node('div', 'class', 'pagination js-pages',\
                    html_node('div', 'class', 'pagination-nav clearfix',\
                        html_a_link_node('a', 'pagination-nav js-pagination-next', '/catalog/2',\
                         'Следующая страница →'))\
                )\
            )
            self._first_html = head + body

            first_item = html_node('div', 'class', 'item',\
                 html_node('h3', 'class', 'item_title',\
                    html_a_item_node('a', 'item_title_desription', '"2_p FIRST ITEM"', '2_p FIRST ITEM')))

            second_item = html_node('div', 'class', 'item',\
                 html_node('h3', 'class', 'item_title',\
                    html_a_item_node('a', 'item_title_desription', '"2_p SECOND ITEM"', '2_p SECOND ITEM')))

            body = html_node('body', 'class', ' ',\
                html_node('div', 'class', 'first_level',\
                     html_node('div', 'class', 'second_level', (first_item + second_item)\
                    )\
                ) +\
                html_node('div', 'class', 'pagination js-pages',\
                    html_node('div', 'class', 'pagination-nav clearfix',\
                        html_a_link_node('a', 'pagination-nav js-pagination-next', '/catalog/1',\
                         '← Предыдущая'))\
                )\
            )
            self._second_html = head + body


        @responses.activate
        def test_get_html_from_url(self):
            """
            test get html
            """
            responses.add(responses.GET, self._first_url, self._first_html, status=200)

            crawler = Crawler(target_url=self._first_url)
            crawler.set_struct(json.loads(self._struct_json))
            data, url = crawler.get_one_page_data(crawler._target_url)
            self.assertListEqual(data, ['1_p FIRST ITEM', '1_p SECOND ITEM'])
            self.assertEqual(url[0], '/catalog/2')

        @responses.activate
        def test_get_next_page(self):
            """
            test get html
            """
            responses.add(responses.GET, self._first_url, self._first_html, status=200)
            responses.add(responses.GET, self._second_url, self._second_html, status=200)

            crawler = Crawler(target_url=self._first_url)
            crawler.set_struct(json.loads(self._struct_json))
            data = crawler.get_all_pages_data()
            self.assertListEqual(data, ['1_p FIRST ITEM', '1_p SECOND ITEM', '2_p FIRST ITEM', '2_p SECOND ITEM'])

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

    if (n_arg > 1) & (n_arg <= 4):

        if (n_arg == 2) & ('--run_self_test' in arg[1]):
            _run_unittests()

        elif (n_arg == 4) & ('--get_data' in arg[1]):
            _run(arg[2], arg[3])

        else:
            print(help_msg)

    else:
        print(help_msg)


if __name__ == "__main__":
    _read_args_and_run()
