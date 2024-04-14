import os
import signal
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


class HitlerCrawler:
    def __init__(self, start_article, end_article, max_depth, max_workers):
        self.root = "https://en.wikipedia.org/wiki/"
        self.start_article = start_article
        self.end_article = end_article
        self.max_depth = max_depth
        self.max_workers = max_workers
        self.visited_urls = set()
        self.links_dictionary = {}
        self.hitler_paths = []
        self.skip_prefixes = (
            "Main_Page",
            "Wikipedia:",
            "Portal:",
            "Template:",
            "Template_talk:",
            "Special:",
            "Help:",
            "Category:",
            "Talk:",
            "File:",
        )
        self.counter = 0
        self.cache = {}
        self.shutdown_requested = False

    def fetch_url(self, url):
        response = requests.get(url)
        return response.text

    def get_links_from_page(self, url):
        if url in self.cache:
            return self.cache[url]
        html = self.fetch_url(url)
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for link in soup.find_all("a"):
            href = link.get("href")
            if (
                href
                and href.startswith("/wiki/")
                and not any(
                    href.lstrip("/wiki/").startswith(prefix)
                    for prefix in self.skip_prefixes
                )
            ):
                links.append(href)
        self.cache[url] = links
        return links

    def pretty_print_crawl(self, url, depth):
        self.counter += 1
        width = os.get_terminal_size().columns
        s = f"\r#{self.counter} Crawling {url} at depth {depth}"
        print(s.ljust(width), end="", flush=True)

    def pretty_print_result(self):
        if self.hitler_paths:
            print(
                f"\nHitler found!\nA path to {self.end_article} from {self.start_article}:"
            )
            for path in self.hitler_paths:
                print(" -> ".join(path))
        else:
            print("Hitler not found!")
        os._exit(1)

    def crawl_url(self, url, path):
        if self.shutdown_requested:
            return
        depth = len(path)
        if depth >= self.max_depth:
            return
        if url in self.visited_urls:
            return
        self.pretty_print_crawl(url, depth)
        self.visited_urls.add(url)
        links = self.get_links_from_page(url)
        self.links_dictionary[url] = path + [url]
        if any(self.end_article in link for link in links):
            self.hitler_paths.append(path + [url])
            self.pretty_print_result()
            return
        urls_to_crawl = [
            (self.root + link.lstrip("wiki/"), path + [url]) for link in links
        ]
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(
                self.crawl_url,
                [url for url, _ in urls_to_crawl],
                [path for _, path in urls_to_crawl],
            )

    def start_crawl_threaded(self):
        self.crawl_url(self.root + self.start_article, [])

    def stop(self):
        self.shutdown_requested = True


start_article = input("Enter the start (Tomato):") or "Tomato"
end_article = input("Enter the end (Adolf_Hitler):") or "Adolf_Hitler"
max_depth = 6
max_workers = 50

crawler = HitlerCrawler(start_article, end_article, max_depth, max_workers)
crawler.start_crawl_threaded()

if not crawler.hitler_paths:
    print("\nHitler not found.")
