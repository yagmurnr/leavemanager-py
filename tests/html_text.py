"""Read what a user sees on a page: visible text, table rows and <option> labels (spec 0002).

Tests compare what is shown, not the HTML shape, so moving markup into templates stays invisible
to them. Entities are decoded, so "IT&#39;ye" and "IT'ye" read the same.
"""

from html.parser import HTMLParser


class _Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.rows = []
        self.options = []
        self.styled = []  # (style attribute, text inside the element)
        self._row = None
        self._cell = None
        self._option = None
        self._style_stack = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("style", "script"):
            self._skip += 1
        elif tag == "tr":
            self._row = []
        elif tag in ("td", "th"):
            self._cell = []
        elif tag == "option":
            self._option = []
        self._style_stack.append((tag, attrs.get("style"), []))

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self._skip -= 1
        elif tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append("".join(self._cell).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None
        elif tag == "option" and self._option is not None:
            self.options.append("".join(self._option).strip())
            self._option = None
        while self._style_stack:
            open_tag, style, parts = self._style_stack.pop()
            if style:
                self.styled.append((style, "".join(parts).strip()))
            if open_tag == tag:
                break

    def handle_data(self, data):
        if self._skip:
            return
        self.text.append(data)
        for buf in (self._cell, self._option):
            if buf is not None:
                buf.append(data)
        for _, _, parts in self._style_stack:
            parts.append(data)


def parse(html):
    c = _Collector()
    c.feed(html)
    c.close()
    return c


def visible_text(html):
    return " ".join("".join(parse(html).text).split())


def table_rows(html):
    return parse(html).rows


def option_labels(html):
    return parse(html).options


def styled_texts(html):
    return parse(html).styled
