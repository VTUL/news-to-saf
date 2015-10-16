#/usr/bin/python3
import logging, pathlib, lxml.etree, lxml.html
from collections import Counter
from datetime import datetime
from zipfile import ZipFile
from shutil import copy2

class SafDriver:
    def __init__(self, input_files, path=None, log_level=logging.DEBUG):
        # Set base path if it doesn't exist.
        if path is not None and pathlib.Path(path).expanduser().exists():
            self.base_path = pathlib.Path(path).expanduser()
            if not self.base_path.is_absolute():
                self.base_path = self.base_path.resolve()
        else:
            self.base_path = pathlib.Path(__file__).parent

        # Set up logging
        self.log_level = log_level
        log_path = self.base_path / 'vt_news.log'
        logging.basicConfig(filename=str(log_path), level=log_level)

        # Create package
        self.create_saf_package(input_files)

    def create_saf_package(self, input_files):
        author_counter, spatial_counter = Counter(), Counter()

        for rss_file in input_files:
            logging.debug('Parsing {}'.format(rss_file))
            feed = lxml.etree.parse(str(self.base_path / rss_file))
            for item in self.find_items(feed):
                news_item = NewsItem(item, self.base_path)
                author_counter[news_item.author] += 1
                spatial_counter[news_item.spatial_coverage] += 1
                news_item.create_saf_item()
                logging.info('')

        if self.log_level <= logging.DEBUG:
            logging.debug('Instrumentation: Authors: {}'.format(author_counter))
            logging.debug('Instrumentation: Spatial: {}'.format(spatial_counter))

    def find_items(self, feed):
        items = feed.findall('.//item')
        # Return all items, unless we're below debug mode. Then, return first, middle, and last.
        if self.log_level < logging.DEBUG:
            return [items[0], items[len(items)//2], items[-1]]
        return items

class NewsItem:
    __slots__ = ['author', 'spatial_coverage', 'date_issued', 'description', 'title', 'feed_url',
            'image_urls', 'keywords', 'error_urls', 'base_path', 'directory']

    def __getattr__(self, name):
        return None

    def __init__(self, item=None, path=None):
        self.keywords = set()
        self.image_urls = set()
        self.error_urls = set()

        # Set base path if it doesn't exist.
        if path is not None and pathlib.Path(path).expanduser().exists():
            self.base_path = pathlib.Path(path).expanduser()
            if not self.base_path.is_absolute():
                self.base_path = self.base_path.resolve()
        else:
            self.base_path = pathlib.Path(__file__).parent

        # Parse the item, if given.
        if item is not None:
            self.parse(item)

    def parse(self, item):
        self.parse_atom(item)
        if self.feed_url is not None:
            self.parse_html(self.feed_url)

    def parse_atom(self, item):
        # Find and add metadata.
        self.title = item.find('./title').text
        logging.debug('Title: {}'.format(self.title))
        self.feed_url = item.find('./link').text
        logging.debug('Feed Url: {}'.format(self.feed_url))
        self.description = item.find('./description').text
        logging.debug('Description: {}'.format(self.description))

        self.date_issued = item.find('./pubDate').text
        self.date_issued = datetime.strptime(self.date_issued, '%a, %d %b %Y %H:%M:%S %z')
        logging.debug('Date Issued: {}'.format(self.date_issued.strftime('%Y-%m-%d')))

        for keyword in item.iterfind('./category'):
            self.keywords.add(item.find('./category').text)
        if len(self.keywords) > 0:
            logging.debug('Keywords: {}'.format(self.keywords))

        for enclosure in item.iterfind('./enclosure'):
            self.image_urls.add(enclosure.get('url'))
        if len(self.image_urls) > 0:
            logging.debug('Images from feed: {}'.format(self.image_urls))

    def parse_html(self, url):
        page = url.split('articles/')[-1]
        if self.base_path.joinpath(page).exists():
            html = lxml.html.parse(page)
            logging.info('HTML page `{}` exists, and parses.'.format(url))

            # Dateline is in the first p, unless that is an image, then it is in the third.
            dateline = html.find('.//{*}p')
            if dateline.text is None:
                dateline = html.findall('.//{*}p')[2]
            if 'BLACKSBURG, Va.' in dateline.text:
                self.spatial_coverage = 'Blacksburg, Va.'
            else:
                date_issued = self.date_issued.strftime(', %b')
                self.spatial_coverage = dateline.text.split(date_issued)[0].title()
            if len(self.spatial_coverage) > 25 or '\n' in self.spatial_coverage or ' ' == self.spatial_coverage:
                # Sanity check: These are symptoms of errors. Change them to Blacksburg.
                self.spatial_coverage = 'Blacksburg, Va.'
            logging.debug('Spatial Coverage: {}'.format(self.spatial_coverage))

            # Author is in the first li of the last ul, or the one before that, if it exists.
            html_lists = html.findall('.//{*}ul')
            author = html_lists[-1].find('./{*}li').text
            if author is None:
                try:
                    author = html_lists[-2].find('./{*}li').text
                except IndexError as e:
                    logging.error('No author found.')
            if author is not None:
                author = ' '.join(author.split())
            self.author = author
            logging.debug('Author: {}'.format(self.author))

            # Any img tag is a related file.
            for image in html.iterfind('.//{*}img'):
                self.image_urls.add(image.get('src'))
            if len(self.image_urls) > 0:
                logging.debug('All image urls: {}'.format(self.image_urls))
        else:
            logging.error('Url `{}` does not map to an HTML file in the archive.'.format(url))
            self.error_urls.add(url)

    def create_saf_item(self):
        if self.feed_url not in self.error_urls:
            # Create needed directories
            self.directory = self.base_path / 'vt-news-saf' / pathlib.Path(self.feed_url).stem
            self.directory.mkdir(parents=True, exist_ok=True)
            logging.debug('Created a directory: {}'.format(self.directory))

            # Add files to directory
            html_path = self.base_path / self.feed_url.split('articles/')[-1]
            copy2(str(html_path), str(self.directory))
            self.copy_images()
            logging.debug('All files copied')
            if len(self.error_urls) > 0:
                logging.info('Urls that created errors: {}'.format(self.error_urls))

            # Write the contents file and the DC metadata file.
            self.write_contents()
            self.write_metadata()
            logging.info('Created SAF item.')

            # Add all files to the zipped package.
            self.add_to_package()
            logging.info('Added item to zipped package.')
        else:
            logging.error('No valid HTML page was found for this item! Cannot create SAF package.')

    def copy_images(self):
        # Deduplicate and standardize self.image_urls
        image_path_partials = set()
        for image_url in self.image_urls:
            image_path_partial = None
            if 'articles/' in image_url:
                image_path_partial = image_url.split('articles/')[-1]
            else:
                if 'http' not in image_url:
                    date_issued = self.date_issued.strftime('%Y/%m')
                    image_path_partial = '{}/{}'.format(date_issued, image_url)
                else:
                    logging.error('Image url `{}` not in news archive. Skipped.'.format(image_url))
            if image_path_partial is not None:
                image_path_partials.add(image_path_partial)
        if len(image_path_partials) > 0:
            logging.debug('Canonical image urls: {}'.format(image_path_partials))

        # Add images to SAF location.
        for image_path_partial in image_path_partials:
            image_path = self.base_path / image_path_partial
            if image_path.exists():
                copy2(str(image_path), str(self.directory))
            else:
                logging.error('No file found at `{}`. Expected an image.'.format(image_path))
                self.error_urls.add(image_path)

    def write_contents(self):
        # Add all files that are not the contents file to the contents file, each on a line.
        with self.directory.joinpath('contents').open(mode='wt', encoding='utf-8') as contents:
            for item in self.directory.iterdir():
                if item.is_file() and item.name != 'contents':
                    contents.write('{}\n'.format(item.name))

    def write_metadata(self):
        # Create the XML structure
        dc_root = lxml.etree.Element('dublin_core')
        dc_root.append(DCValue('title', value=self.title))
        dc_root.append(DCValue('description', qualifier='abstract', value=self.description))
        dc_root.append(DCValue('contributor', qualifier='author', value=self.author))
        dc_root.append(DCValue('publisher', value='Virginia Tech. University Relations'))
        date_issued = self.date_issued.strftime('%Y-%m-%d')
        dc_root.append(DCValue('date', qualifier='issued', value=date_issued))
        dc_root.append(DCValue('coverage', qualifier='spatial', value=self.spatial_coverage))
        for keyword in self.keywords:
            dc_root.append(DCValue('subject', value=keyword))

        # Write it to dublin_core.xml
        with self.directory.joinpath('dublin_core.xml').open(mode='wt', encoding='utf-8') as dc_file:
            dc_file.write(lxml.etree.tostring(dc_root, encoding=str, pretty_print=True))

    def add_to_package(self):
        zip_path = self.base_path / 'vt-news-saf.zip'

        with ZipFile(str(zip_path), 'a') as zip_file:
            for item in self.directory.iterdir():
                zip_file.write(str(item), str(item.relative_to(self.base_path)))

def DCValue(element, qualifier='none', value=None, language='en_US'):
    # Return an dcvalue element, with it's text and attributes set.
    element = lxml.etree.Element('dcvalue', element=element, qualifier=qualifier)
    element.text = value
    if language is not None:
        element.set('language', language)

    return element

if __name__ == '__main__':
    SafDriver(['2006.xml', '2007.xml', '2008.xml', '2009.xml', '2010.xml'])
