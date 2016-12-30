import csv
import sys
import requests
import logging
import argparse
from bs4 import BeautifulSoup, SoupStrainer


class Extractor(object):

    def __init__(self, url):
        self.url = url
        self.setup_logging()
        self._download_page()
        
    def setup_logging(self, level=logging.INFO):
        self.logger = logging.getLogger('tbl_extract')
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)

    def log(self, *message):
        self.logger.log(logging.INFO, ' '.join(str(mssg) for mssg in message))

    def _download_page(self):
        self.log('downloading webpage')
        req = requests.get(self.url)
        self.source = req.content

    def extract_tables_from_page(self):
        soup = BeautifulSoup(self.source, 'html.parser', parse_only = SoupStrainer('table'))
        #self.log('downloading tables')
        tables = soup.findAll('table')
        if tables:
            self.log(len(tables), 'tables', 'found')
            return tables
        self.log('no tables on site', '\n', 'exiting')
        sys.exit(1)

    def _get_table_row(self, table):

        self.log('extracting table data')
        
        rows = table.findAll('tr')
        # more than likely the headers are the first row in a table
        headers = [i.text for i in rows[0].findAll('th')]
        # while the rows are till infinity :D
        rough = [i.findAll('td') for i in rows[1:]]

        clean_rows = []

        for row in rough:
            field = []
            for element in row:
                field.append(element.text)
            clean_rows.append(field)

        return headers, clean_rows

    def _write_headers(self, item):
        self.csv_writer.writerow(item)

    def export_item(self, data, file):
    	headers, rows  = data
        self.log('writing files to', file)
        file_ = open(file, 'wb')
        self.csv_writer = csv.writer(file_)
        
        self._write_headers(headers)
        for row in rows:
            self.csv_writer.writerow(row)
        file_.close()

    def extract_tables(self):
        tables = self.extract_tables_from_page()
        for no, table in enumerate(tables):
            self.log('extracting', 'table {}'.format(no+1))
            data = self._get_table_row(table)
            self.export_item(data, 'table{}.csv'.format(no+1))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'tbl_extract')
    parser.add_argument('url', help='url to extract table from')

    args = parser.parse_args()
    url = args.url

    #test_url = 'http://www.w3schools.com/html/html_tables.asp'
    table = Extractor(url)
    table.extract_tables()

