import argparse

from feeds.utils import find_feeds

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str)
    args = parser.parse_args()
    possible_feeds = find_feeds(args.url)

    if possible_feeds:
        print("Feeds found:")
        for feed in possible_feeds:
            print(f"URL: {feed.url} | Title: {feed.title or 'Unknown'}")
