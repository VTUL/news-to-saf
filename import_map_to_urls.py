#!/usr/bin/python3
import logging, pathlib, csv, lxml.etree
from collections import namedtuple

# Get the URL from a xml link.
def get_link_text(xml_link):
    return xml_link.text.strip()

# Represents a line from the map file.
Line = namedtuple('Line', ['item_name', 'handle'])

class MapDriver():
    def __init__(self, years, path=None, log_level=logging.DEBUG):
        # Set base path if it doesn't exist.
        if path is not None and pathlib.Path(path).expanduser().exists():
            self.base_path = pathlib.Path(path).expanduser()
            if not self.base_path.is_absolute():
                self.base_path = self.base_path.resolve()
        else:
            self.base_path = pathlib.Path(__file__).parent

        # Set up logging
        self.log_level = log_level
        log_path = self.base_path / 'vt_news_map.log'
        logging.basicConfig(filename=str(log_path), level=log_level)

        # Map item names/handles to URLs.
        self.map_years(years)

    def map_years(self, years, output='vt-news-map'):
        for year in years:
            logging.debug('Mapping {}'.format(year))
            map_path = self.base_path / 'vt-news-saf-{}.map'.format(year)
            xml_path = self.base_path / '{}.xml'.format(year)
            output_path = self.base_path / '{}.csv'.format(output)
            logging.debug('Files: {} {} {}'.format(str(map_path), str(xml_path), str(output_path)))

            self.map_handles(map_path, xml_path, output_path)

    def map_handles(self, map_path, xml_path, output_path):
        with map_path.open() as map_file, output_path.open('a') as output_file:
            output_writer = csv.writer(output_file)
            xml_file = lxml.etree.parse(str(xml_path))
            links = [link for link in map(get_link_text, xml_file.findall('.//item/link'))]
            logging.debug('{} links in the xml.'.format(len(links)))

            for line in map_file:
                line = Line(*line.strip().split())

                original_url = self.find_original_url(line.item_name, links)
                if original_url is not None:
                    links.remove(original_url) # Remove found link to speed up subsequent searches.
                vtw_url = 'https://vtechworks.lib.vt.edu/handle/{}'.format(line.handle)
                handle_url = 'http://hdl.handle.net/{}'.format(line.handle)

                output_writer.writerow((original_url, vtw_url, handle_url))

    def find_original_url(self, link_fragment, links):
        for link in links:
            if link.endswith('{}.html'.format(link_fragment)):
                return link

        logging.error('No link found for `{}`'.format(link_fragment))
        return None

if __name__ == '__main__':
    # Prior to running this, I combined the vt-news-saf-2010-1.map and vt-news=saf-2010-2.map files
    MapDriver(['2006', '2007', '2008', '2009', '2010'])
