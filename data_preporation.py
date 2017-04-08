#!/usr/bin/env python
import os
import pandas as pd

def join_data():
    """
    Join all data
    """
    print('\n', '-'*50)
    print('\tJoin all csv in one...')
    df = None
    for one_csv in os.listdir():
        if 'csv' in one_csv:
            tmp = pd.read_csv('./' + one_csv, header=None)
            tmp = tmp.T
            if df is None:
                df = tmp
            else:
                df = df.append(tmp, ignore_index=True)
                
    df.to_csv('./all_data.csv', columns=[0], header=None)
    print('\tAll data csv name: ./all_data.csv')

def count_all():
    """
    Count all
    """
    print('\n', '-'*50)
    frame = pd.read_csv('./all_data.csv', index_col=0, header=None)
    with_out_year = frame[1][\
            frame[1].str.findall(\
            '[1-2][0-9][0-9][0-9]').apply(len) == 0]
    with_year = frame[1][\
            frame[1].str.findall(\
            '[1-2][0-9][0-9][0-9]').apply(len) > 0]

    print('\ttotal: ', frame[1].count())
    print('\twith out year: ', with_out_year.count())
    print('\twith year: ', with_year.count())

    print('\n', '-'*50)

    before = with_year[\
        with_year.str.findall('[1-2][0-9][0-9][0-9]').\
        apply(lambda x: min([int(i) for i in x])) < 2000].count()

    after = with_year[\
        with_year.str.findall('[1-2][0-9][0-9][0-9]').\
        apply(lambda x: min([int(i) for i in x])) >= 2000].count()

    result = before/after
    print('\tcount before 2000: ', before)
    print('\tcount after 2000: ', after)
    print('\tbefore/after: ', result)

if __name__ == "__main__":
    join_data()
    count_all()
