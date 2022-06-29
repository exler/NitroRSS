from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup as bs4


@dataclass
class PossibleFeed:
    title: Optional[str]
    url: str

    def __hash__(self) -> int:
        return hash((self.url, self.title))


def find_feeds(url: str) -> frozenset[PossibleFeed]:
    """
    Function that finds possible RSS and Atom feeds from a given URL.

    TODO POSSIBLE IMPROVEMENTS:
    - Parse the feed using feedparser, obtain the description and other details.
    - Add the feed to the database and link it with the supplied URL to speed up future requests.

    Args:
        url (str): URL to search feeds at.

    Returns:
        frozenset[PossibleFeed]: Set of possible feeds.
    """
    response = requests.get(url)
    html = bs4(response.text, "lxml")

    possible_feeds: list[PossibleFeed] = []

    feed_urls = html.find_all("link", rel="alternate")
    for feed in feed_urls:
        if (t := feed.get("type", None)) and t.endswith("rss+xml"):
            if href := feed.get("href", None):
                possible_feeds.append(PossibleFeed(url=href, title=feed.get("title", None)))

    return frozenset(possible_feeds)
