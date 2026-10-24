"""Publish a mobile catalog from the desktop catalog without Windows downloads."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PC_URL = 'https://flamecard.github.io/kimagure-no-yakata/garakuta/'


def article(page, key):
    match = re.search(r'<article\b[^>]*\bid="' + re.escape(key) + r'"[^>]*>.*?</article>', page, re.S)
    if not match:
        raise ValueError('Missing catalog entry: ' + key)
    return match.group()


def decorate(page, mobile=False):
    page = re.sub(r'  <script>\s*// Keep accidental phone visits.*?</script>\s*', '', page, flags=re.S)
    page = re.sub(r'\s*<script\b[^>]*catalog-device\.js[^>]*></script>', '', page)
    page = re.sub(r'\s*<link rel="(?:canonical|alternate)"[^>]*>', '', page)
    page = re.sub(r'\s*<nav class="catalog-versions".*?</nav>', '', page, flags=re.S)
    page = re.sub(r'<title>.*?</title>', '<title>ガラクタ置き場｜' + ('スマホ版' if mobile else 'PC版') + '｜気まぐれの館</title>', page)
    prefix = '../../' if mobile else '../'
    catalog = '../' if mobile else './'
    head = f'\n  <link rel="canonical" href="{PC_URL}">\n'
    if not mobile:
        head += f'  <link rel="alternate" media="only screen and (max-width: 768px)" href="{PC_URL}mobile/">\n'
    head += f'  <script src="{prefix}assets/js/catalog-device.js?v=20261024" data-catalog="{catalog}"></script>\n'
    page = page.replace('</head>', head + '</head>')
    pc_href = '../?view=pc' if mobile else '?view=pc'
    mobile_href = '?view=mobile' if mobile else 'mobile/?view=mobile'
    nav = '<nav class="catalog-versions" aria-label="表示する版">'
    nav += f'<a href="{pc_href}"' + ('' if mobile else ' aria-current="page"') + '>PC版</a>'
    nav += f'<a href="{mobile_href}"' + (' aria-current="page"' if mobile else '') + '>スマホ版</a></nav>'
    page = page.replace('<h1>ガラクタ置き場</h1>', '<h1>ガラクタ置き場</h1>' + nav)
    page = re.sub(r'garakuta\.css\?[^"\s]+', 'garakuta.css?v=20261024-background', page)
    return page


def main():
    path = ROOT / 'garakuta/index.html'
    desktop = decorate(path.read_text(encoding='utf-8'))
    tournament = article(desktop, 'tournament')
    qr = (ROOT / 'garakuta/mobile-qr.html').read_text(encoding='utf-8').strip()
    # Retain the desktop shell and authored phrase boundaries; only replace catalog contents.
    mobile = re.sub(r'<div class="software-grid">.*?</article></div>', '<div class="software-grid">' + tournament + '\n' + qr + '</div>', desktop, flags=re.S)
    mobile = re.sub(r'<nav class="software-nav".*?</nav>', '<nav class="software-nav" aria-label="掲載ソフト"><a href="#tournament">気まぐれの大会室</a><a href="#qr">気まぐれQR</a></nav>', mobile, flags=re.S)
    mobile = re.sub(r'<meta name="description"[^>]*>', '<meta name="description" content="ガラクタ置き場のスマホ版．iPhone・Android向けに，大会運営ツール「気まぐれの大会室」と「気まぐれQR」を紹介します．">', mobile)
    mobile = re.sub(r'<section class="guide-board usage-notes".*?</section>', '<section class="guide-board usage-notes"><h2>ご利用について</h2><p><span class="copy-phrase">各ツールの利用方法・</span><span class="copy-phrase">公開状況をご確認ください．</span><br class="punctuation-break"><span class="copy-phrase">大会室の利用には</span><span class="copy-phrase">インターネット接続が必要です．</span></p></section>', mobile, flags=re.S)
    mobile = mobile.replace('href="../', 'href="../../').replace('src="../', 'src="../../')
    mobile = decorate(mobile, mobile=True)
    path.write_text(desktop, encoding='utf-8')
    target = ROOT / 'garakuta/mobile/index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(mobile, encoding='utf-8')


if __name__ == '__main__':
    main()
