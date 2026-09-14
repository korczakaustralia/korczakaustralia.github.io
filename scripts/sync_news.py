#!/usr/bin/env python3
"""Refresh the "Latest Updates" block on news.html from a published Google Doc.

Usage:  python3 scripts/sync_news.py            (fetches the doc)
        python3 scripts/sync_news.py saved.html (uses a saved copy, for testing)

The block between <!-- news:start --> and <!-- news:end --> in news.html is replaced with
the document's content, converted to the site's own markup (Reem Kufi display classes).
Images in the doc are downloaded into assets/images/updates/ so the site never depends on
Google's image URLs. Exit code 0 always; prints "changed" or "unchanged".
"""
import hashlib, os, re, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from bs4 import BeautifulSoup, NavigableString

DOC_URL = ('https://docs.google.com/document/d/e/'
           '2PACX-1vRTtNvswhI3sYeYQ-33kGnWT1EeMh_l4gJJEXNNNKeJbHa4XSn7PNzM3yOv-V1hjfFP9Ynr6ncFy_uZ/pub')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWS_PAGE = os.path.join(ROOT, 'news.html')
IMG_DIR = os.path.join(ROOT, 'assets', 'images', 'updates')
START, END = '<!-- news:start', '<!-- news:end -->'
UA = {'User-Agent': 'Mozilla/5.0 (compatible; korczakaustralia-news-sync)'}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def style_classes(soup):
    """Google Docs expresses bold/italic/underline through generated CSS classes; map them back."""
    css = ' '.join(s.get_text() for s in soup.find_all('style'))
    flags = {}
    for sel, body in re.findall(r'\.([\w-]+)\{([^}]*)\}', css):
        f = set()
        if re.search(r'font-weight:\s*(700|bold)', body): f.add('b')
        if 'font-style:italic' in body.replace(' ', ''): f.add('i')
        if 'text-decoration:underline' in body.replace(' ', ''): f.add('u')
        if f:
            flags[sel] = f
    return flags


def real_href(href):
    """Unwrap Google's redirect links (https://www.google.com/url?q=...)."""
    p = urllib.parse.urlparse(href)
    if p.netloc == 'www.google.com' and p.path == '/url':
        q = urllib.parse.parse_qs(p.query).get('q')
        if q:
            return q[0]
    return href


def save_image(src, keep):
    os.makedirs(IMG_DIR, exist_ok=True)
    data = fetch(src)
    ext = {b'\x89PNG': '.png', b'GIF8': '.gif', b'RIFF': '.webp'}.get(data[:4], '.jpg')
    name = hashlib.sha1(data).hexdigest()[:16] + ext
    path = os.path.join(IMG_DIR, name)
    if not os.path.exists(path):
        open(path, 'wb').write(data)
    keep.add(name)
    return 'assets/images/updates/' + name


def convert(doc_html, download_images=True):
    src = BeautifulSoup(doc_html, 'html.parser')
    flags = style_classes(src)
    body = src.find(id='contents') or src.body or src
    out = BeautifulSoup('', 'html.parser')
    keep = set()

    def inline(node, dest):
        """Copy inline content, turning styled spans into <strong>/<em>/<u> and fixing links."""
        for child in node.children:
            if isinstance(child, NavigableString):
                if str(child):
                    dest.append(NavigableString(str(child)))
                continue
            if child.name == 'br':
                dest.append(out.new_tag('br')); continue
            if child.name == 'img':
                if not child.get('src'):
                    continue
                img = out.new_tag('img', alt=child.get('alt', ''), loading='lazy')
                img['src'] = save_image(child['src'], keep) if download_images else child['src']
                dest.append(img); continue
            if child.name == 'a' and child.get('href'):
                a = out.new_tag('a', href=real_href(child['href']))
                if a['href'].startswith('http'):
                    a['target'] = '_blank'; a['rel'] = 'noopener'
                inline(child, a); dest.append(a); continue
            f = set()
            for c in child.get('class', []):
                f |= flags.get(c, set())
            if child.name in ('b', 'strong'): f.add('b')
            if child.name in ('i', 'em'): f.add('i')
            wrap = dest
            for flag, tag in (('b', 'strong'), ('i', 'em'), ('u', 'u')):
                if flag in f:
                    t = out.new_tag(tag); wrap.append(t); wrap = t
            inline(child, wrap)

    def text_of(el):
        return el.get_text(' ', strip=True)

    for el in body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'table'], recursive=True):
        if el.find_parent(['li', 'table']) and el.name != 'table':
            continue  # handled with its list / table
        cls = el.get('class', [])
        if 'title' in cls or 'subtitle' in cls:
            continue  # the document title is not part of the news
        if el.name.startswith('h'):
            if not text_of(el):
                continue
            level = int(el.name[1])
            h = out.new_tag('h3' if level == 1 else 'h4')
            h['class'] = 'mbr-fonts-style mbr-bold ' + ('display-5' if level == 1 else 'display-6')
            inline(el, h); out.append(h)
        elif el.name == 'p':
            if not text_of(el) and not el.find('img'):
                continue
            if text_of(el).lower().startswith('updated automatically every'):
                continue
            p = out.new_tag('p', **{'class': 'mbr-text mbr-fonts-style display-7'})
            inline(el, p); out.append(p)
        elif el.name in ('ul', 'ol'):
            lst = out.new_tag(el.name, **{'class': 'mbr-text mbr-fonts-style display-7'})
            for li in el.find_all('li', recursive=False):
                item = out.new_tag('li'); inline(li, item); lst.append(item)
            if lst.contents:
                out.append(lst)
        elif el.name == 'table':
            tbl = out.new_tag('table', **{'class': 'mbr-text mbr-fonts-style display-7'})
            for tr in el.find_all('tr'):
                row = out.new_tag('tr')
                for td in tr.find_all(['td', 'th']):
                    cell = out.new_tag(td.name); inline(td, cell); row.append(cell)
                tbl.append(row)
            out.append(tbl)

    if not out.contents:
        return None, keep
    html = ''.join(str(c) for c in out.contents)
    stamp = datetime.now(timezone.utc).astimezone().strftime('%-d %B %Y')
    return (f'<div class="news-update">\n{html}\n'
            f'<p class="news-update-meta mbr-fonts-style display-7">Last updated {stamp}</p>\n</div>'), keep


def main():
    doc_html = open(sys.argv[1], 'rb').read() if len(sys.argv) > 1 else fetch(DOC_URL)
    block, keep = convert(doc_html, download_images=len(sys.argv) == 1)
    if block is None:
        print('document is empty; leaving news.html unchanged'); return
    page = open(NEWS_PAGE, encoding='utf-8').read()
    i, j = page.index(START), page.index(END)
    i = page.index('-->', i) + 3
    new_page = page[:i] + '\n' + block + '\n' + page[j:]
    # only the date stamp changed? then keep the old file so we don't commit every run
    strip = lambda s: re.sub(r'Last updated [^<]*', '', s)
    if strip(new_page) == strip(page):
        print('unchanged'); return
    open(NEWS_PAGE, 'w', encoding='utf-8').write(new_page)
    if len(sys.argv) == 1 and os.path.isdir(IMG_DIR):  # drop images the doc no longer uses
        for f in os.listdir(IMG_DIR):
            if f not in keep and f.rsplit('.', 1)[0] not in new_page:
                os.remove(os.path.join(IMG_DIR, f))
    print('changed')


if __name__ == '__main__':
    main()
