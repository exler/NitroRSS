import html
import re


class HTMLCleaner:
    html_tags_pattern = re.compile(r"<[^>]*>")

    def clean(self, text: str) -> str:
        text = self.strip_html_tags(text)
        text = self.unescape_html_entities(text)
        return text

    @classmethod
    def strip_html_tags(cls, text: str) -> str:
        return cls.html_tags_pattern.sub("", text)

    @classmethod
    def unescape_html_entities(cls, text: str) -> str:
        return html.unescape(text)


def smart_truncate(text: str, length: int, suffix: str = "...") -> str:
    """
    Truncates a string to a given length, without cutting words in half.

    Args:
        text (str): Text to truncate
        length (int): Length to truncate to
        suffix (str, optional): Replace the truncated text with this suffix. Defaults to "...".

    Returns:
        str: Truncated text
    """
    return text[:length].rsplit(" ", 1)[0] + suffix
