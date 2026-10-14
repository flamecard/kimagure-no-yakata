"""Build a static catalog; verify configured GitHub Release assets before linking."""
import html
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def text(value):
    return re.sub(r"([，．])", r'\1<br class="punctuation-break">', html.escape(value))


def download(software):
    release = software.get("release")
    if release is None:
        return '<p class="release-pending">' + text(software["status"]) + '</p><p class="release-note">インストーラーはまだ公開していません．<br class="punctuation-break"></p>'
    repo, tag, filename = (release[key] for key in ("repository", "tag", "asset"))
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo):
        raise ValueError("Invalid repository")
    if not filename.lower().endswith((".exe", ".msi")):
        raise ValueError("A Windows installer is required")
    from urllib.parse import quote
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/releases/tags/{quote(tag, safe='')}",
        headers={"User-Agent": "kimagure-catalog", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    if data.get("draft") or data.get("prerelease"):
        raise ValueError("Only published stable releases can be linked")
    asset = next((a for a in data["assets"] if a["name"] == filename and a["size"] > 0 and a["state"] == "uploaded"), None)
    if not asset:
        raise ValueError("Installer not found; page was not updated")
    if not all(software.get(key) for key in ("version", "updated", "history")) or software["license"] in ("未定", "公開時に掲載"):
        raise ValueError("Complete version, date, history and license before publishing")
    url = asset["browser_download_url"]
    if not url.startswith(f"https://github.com/{repo}/releases/download/"):
        raise ValueError("Unexpected asset URL")
    return f'<a class="guide-button" href="{html.escape(url, quote=True)}">Windows用をダウンロード</a>'


def card(item):
    info = [("対応OS", item["os"]), ("ライセンス", item["license"]), ("最新バージョン", item["version"] or "未公開"), ("更新日", item["updated"] or "未公開")]
    details = ''.join(f'<div><dt>{key}</dt><dd>{text(value)}</dd></div>' for key, value in info)
    features = ''.join(f'<li>{text(value)}</li>' for value in item["features"])
    history = ''.join(f'<li>{text(value)}</li>' for value in item["history"]) or '<li>公開後に掲載します．<br class="punctuation-break"></li>'
    screenshot = '<p class="screenshot-pending">スクリーンショットは公開準備中</p>'
    if item.get("screenshot"):
        path = item["screenshot"]
        resolved = (ROOT / path).resolve()
        if not resolved.is_relative_to(ROOT) or not resolved.is_file():
            raise ValueError("Screenshot must exist in the repository")
        screenshot = f'<img class="software-screenshot" src="../{html.escape(path, quote=True)}" alt="{html.escape(item["name"], quote=True)}の画面" loading="lazy">'
    return f'''<article class="guide-board software-card" id="{html.escape(item['id'], quote=True)}">
      <span class="software-status">{text(item['status'])}</span>
      <h2>{text(item['name'])}</h2>
      <p>{text(item['summary'])}</p>
      {screenshot}
      <h3>主な機能</h3><ul>{features}</ul>
      <dl class="software-details">{details}</dl>
      <div class="download-area">{download(item)}</div>
      <h3>更新履歴</h3><ul>{history}</ul>
    </article>'''


def main():
    items = json.loads((ROOT / "garakuta/software.json").read_text(encoding="utf-8"))
    cards = '\n'.join(card(item) for item in items)
    page = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="気まぐれの館のガラクタ置き場．自作のサムネイル作成ソフトと動画編集ソフトの紹介・配布情報．">
  <title>ガラクタ置き場｜気まぐれの館</title>
  <link rel="stylesheet" href="../assets/css/guide.css">
  <link rel="stylesheet" href="../assets/css/mobile.css?v=20261007">
  <link rel="stylesheet" href="../assets/css/logo-links.css?v=20261009">
  <link rel="stylesheet" href="../assets/css/garakuta.css?v=20261014">
</head>
<body class="garakuta-page">
  <main class="guide-container">
    <div class="guide-logo"><a href="../" class="home-logo-link" aria-label="気まぐれの館 トップページへ戻る"><img src="../assets/images/logo/kimagure-logo.png" alt="気まぐれの館"></a></div>
    <header class="guide-board garakuta-intro">
      <p class="room-label">気まぐれにつくったものを置く部屋</p>
      <h1>ガラクタ置き場</h1>
      <p>自作ソフトを紹介する小さな置き場です．<br class="punctuation-break">完成したものから，<br class="punctuation-break">少しずつ公開していきます．<br class="punctuation-break"></p>
      <nav class="software-nav" aria-label="掲載ソフト">{''.join(f'<a href="#{html.escape(item["id"], quote=True)}">{text(item["name"])}</a>' for item in items)}</nav>
    </header>
    <div class="software-grid">{cards}</div>
    <section class="guide-board usage-notes" aria-labelledby="usage-title">
      <h2 id="usage-title">利用規約・注意事項</h2>
      <p>配布ファイルはGitHub Releasesで公開します．<br class="punctuation-break">実際のインストーラーが用意できるまでは，<br class="punctuation-break">ダウンロードリンクを掲載しません．<br class="punctuation-break">各ソフトの利用条件・ライセンス・詳しい動作環境は，<br class="punctuation-break">公開時に掲載します．<br class="punctuation-break">ダウンロード前に各ソフトの案内をご確認ください．<br class="punctuation-break"></p>
      <a href="https://github.com/flamecard/kimagure-no-yakata/releases">配布先のGitHub Releasesを見る</a>
    </section>
    <nav class="garakuta-navigation" aria-label="館内ナビゲーション"><a class="guide-button" href="../">ロビーへ戻る</a><a class="guide-button" href="../guide/">館内案内へ</a></nav>
    <footer class="garakuta-footer"><a href="../policy/">利用ガイドライン</a><a href="../privacy/">プライバシーポリシー</a><p>© 2026 気まぐれの館</p></footer>
  </main>
</body>
</html>
'''
    (ROOT / "garakuta/index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
