import argparse
import datetime
import json
import logging
import random
import re
import sys
import time
import requests
from urllib3.exceptions import LocationParseError
from urllib.parse import urljoin, urlparse
from threading import Thread
from queue import Queue
from requests import Session

URL_PATTERN = re.compile(r"href=[\"'](?!#)(.*?)[\"']", re.DOTALL)

class Crawler:
    class CrawlerTimedOut(Exception):
        """
        Raised when the specified timeout is exceeded
        """
        pass

    def __init__(self):
        """
        Initializes the Crawl class
        """
        self._config = {}
        self._links = set()  
        self._blacklisted_links = set()  # Separated blacklisted links for efficiency
        self._start_time = None
        self.session = Session()  # Use session to improve connection reuse

    def load_config_file(self, file_path):
        """
        Loads and decodes a JSON config file, sets the config of the crawler instance
        to the loaded one
        :param file_path: path of the config file
        """
        with open(file_path, 'r') as config_file:
            self.set_config(json.load(config_file))

    def set_config(self, config):
        """
        Sets the config of the crawler instance to the provided dict
        :param config: dict of configuration options, for example:
        {
            "root_urls": [],
            "blacklisted_urls": [],
            "click_depth": 5
            ...
        }
        """
        self._config = config

    def set_option(self, option, value):
        """
        Sets a specific key in the config dict
        :param option: the option key in the config, for example: "max_depth"
        :param value: value for the option
        """
        self._config[option] = value

    def _request(self, url):
        """
        Sends a GET requests using a random user agent
        :param url: the url to visit
        :return: the response Requests object
        """
        random_user_agent = random.choice(self._config["user_agents"])
        headers = {'user-agent': random_user_agent}

        response = requests.get(url, headers=headers, timeout=5)

        return response.content

    @staticmethod
    def _normalize_link(link, root_url):
        """
        Normalizes links extracted from the DOM by making them all absolute, so
        we can request them, for example, turns a "/images" link extracted from https://imgur.com
        to "https://imgur.com/images"
        :param link: link found in the DOM
        :param root_url: the URL the DOM was loaded from
        :return: absolute link
        """
        parsed_root_url = urlparse(root_url)

        # '//' means keep the current protocol used to access this URL
        if link.startswith("//"):
            return "{}:{}".format(parsed_root_url.scheme, link)

        # possibly a relative path
        if not urlparse(link).scheme:
            return urljoin(root_url, link)

        return link

    def _is_valid_url(self, url):
        """
        Determines whether a URL is valid, for example:
        'https://example.com/path' is valid
        '/path' is not valid
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def _is_blacklisted(self, url):
        """
        Checks if a URL is blacklisted
        :param url: full URL
        :return: boolean indicating whether a URL is blacklisted or not
        """
        return url in self._blacklisted_links


    def _should_accept_url(self, url):
        """
        Filters url if it is blacklisted or not valid, we put filtering logic here
        :param url: full url to be checked
        :return: boolean of whether or not the url should be accepted and potentially visited
        """
        return url and self._is_valid_url(url) and not self._is_blacklisted(url)

    def _extract_urls(self, body, root_url):
        """
        Extracts URLs from a HTML page
        :param body: the HTML page
        :param root_url: the root URL of the page
        :return: list of extracted URLs
        """
        urls = re.findall(URL_PATTERN, str(body))
        for url in urls:
            normalized_url = self._normalize_link(url, root_url)
            if self._should_accept_url(normalized_url):
                self._links.add(normalized_url)

    def _remove_and_blacklist(self, link):
        """
        Adds a link to the blacklist
        :param link: link to blacklist
        """
        self._blacklisted_links.add(link)

    def _browse_from_links(self):
        depth = 0
        while depth < self._config['max_depth'] and not self._is_timeout_reached():
            if not self._links:
                logging.debug("Hit a dead end, moving to the next root URL")
                return
            random_link = random.sample(list(self._links), 1)[0]
            try:
                logging.info("Visiting {}".format(random_link))
                sub_page = self._request(random_link)
                self._extract_urls(sub_page, random_link) 
                time.sleep(random.uniform(self._config["min_sleep"], self._config["max_sleep"]) / 1000)  # Sleep in milliseconds

                if random_link not in self._links:  # Check if the link is still in the set
                    self._remove_and_blacklist(random_link)
                depth += 1
            except requests.exceptions.RequestException:
                logging.debug("Exception on URL: %s, removing from list and trying again!" % random_link)
                self._remove_and_blacklist(random_link)


        if self._is_timeout_reached():
            raise self.CrawlerTimedOut


    def _is_timeout_reached(self):
        """
        Determines whether the specified timeout has reached, if no timeout
        is specified then return false
        :return: boolean indicating whether the timeout has reached
        """
        is_timeout_set = self._config["timeout"] is not False  # False is set when no timeout is desired
        end_time = self._start_time + datetime.timedelta(seconds=self._config["timeout"])
        is_timed_out = datetime.datetime.now() >= end_time

        return is_timeout_set and is_timed_out

    def crawl(self):
        """
        Collects links from our root urls, stores them and then calls
        `_browse_from_links` to browse them
        """
        self._start_time = datetime.datetime.now()

        while True:
            url = random.choice(self._config["root_urls"])
            try:
                body = self._request(url)
                self._extract_urls(body, url)
                logging.debug("found {} links".format(len(self._links)))
                self._browse_from_links()

            except requests.exceptions.RequestException:
                logging.warning("Error connecting to root url: {}".format(url))

            except MemoryError:
                logging.warning("Error: content at url: {} is exhausting the memory".format(url))

            except LocationParseError:
                logging.warning("Error encountered during parsing of: {}".format(url))

            except self.CrawlerTimedOut:
                logging.info("Timeout has exceeded, exiting")
                return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log', metavar='-l', type=str, help='logging level', default='info')
    parser.add_argument('--config', metavar='-c', type=str, help='config file', default="config.json")
    parser.add_argument('--timeout', metavar='-t', required=False, type=int,
                        help='for how long the crawler should be running, in seconds', default=False)
    args = parser.parse_args()

    level = getattr(logging, args.log.upper())
    logging.basicConfig(level=level)

    crawler = Crawler()
    crawler.load_config_file(args.config)

    if args.timeout:
        crawler.set_option('timeout', args.timeout)

    try:
        crawler.crawl()
    except Exception as e:
        logging.error("An error occurred during the crawl: {}".format(e))
        raise


if __name__ == '__main__':
    main()
