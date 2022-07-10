from typing import Optional

import feedparser

from .models import Feed, FeedConnection


def find_feeds(url: str) -> list[Feed]:
    """
    Function that finds RSS and Atom feeds from a given URL.

    Args:
        url (str): URL to search feeds at.

    Returns:
        list[Feed]: List of found feeds.
    """
    try:
        feed = Feed.objects.get(url=url)
        return [feed]
    except Feed.DoesNotExist:
        data = feedparser.parse(url)
        if data.feed.get("title", None):
            return [
                Feed.objects.create(
                    url=url,
                    title=data.feed.get("title", None),
                    description=data.feed.get("description", None),
                )
            ]

    connections = FeedConnection.objects.filter(url=url)
    if connections.exists():
        ids = connections.values_list("feed_id", flat=True)
        return list(Feed.objects.filter(id__in=ids))

    feeds: list[Feed] = []
    feed_links = data.feed.get("links", [])
    for feed_link in feed_links:
        feed_type = feed_link.get("type", None)
        feed_href = feed_link.get("href", None)
        feed_obj: Optional[Feed] = None
        try:
            feed_obj = Feed.objects.get(url=feed_href)
        except Feed.DoesNotExist:
            if feed_type.endswith("rss+xml") and feed_href:
                new_feed_data = feedparser.parse(feed_href)
                new_feed_title = new_feed_data.feed.get("title", None)
                new_feed_description = new_feed_data.feed.get("description", None)
                feed_obj = Feed.objects.create(
                    url=feed_href,
                    title=new_feed_title,
                    description=new_feed_description,
                )

        if feed_obj:
            feeds.append(feed_obj)
            FeedConnection.objects.create(url=url, feed=feed_obj)

    return feeds
