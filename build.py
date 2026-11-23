"""Build a publication from the Markdown files intentionally placed in posts/."""
from datetime import date
from html import escape
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist"
CONFIG = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))
MARKDOWN = "markdown-raw_html-raw_attribute-raw_tex-fenced_divs-bracketed_spans"
BASE_URL = (os.environ.get("SITE_BASE_URL") or "").rstrip("/")
BASE = urlsplit(BASE_URL).path.rstrip("/")
if BASE_URL and (urlsplit(BASE_URL).scheme not in {"https", "http"} or not urlsplit(BASE_URL).netloc):
    raise SystemExit("SITE_BASE_URL must be an absolute HTTP(S) URL, including any site path.")


def e(text):
    return escape(str(text), quote=True)


def pandoc(text, *options):
    p = subprocess.run(["pandoc", "--from", MARKDOWN, *options],
                       input=text, text=True, encoding="utf-8", capture_output=True, check=True)
    return p.stdout


def meta_text(meta, name, default=""):
    value = meta.get(name)
    if not value:
        return default
    if value["t"] == "MetaString":
        return value["c"]
    if value["t"] == "MetaInlines":
        return pandoc(json.dumps({"pandoc-api-version": AST_VERSION,
                                  "meta": {}, "blocks": [{"t": "Plain", "c": value["c"]}]}),
                      "--from", "json", "--to", "plain").strip()
    raise ValueError(f"{name} must be text")


def page(title, content, description="", path="/"):
    sitename = CONFIG["title"]
    display_title = f"{title} · {sitename}" if title != sitename else title
    canonical = f'<link rel="canonical" href="{e(BASE_URL + path)}">' if BASE_URL else ""
    return f"""<!doctype html>
<html lang="{e(CONFIG.get("language", "en"))}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{e(description or CONFIG["description"])}">
<title>{e(display_title)}</title>
{canonical}
<link rel="stylesheet" href="{e(BASE)}/style.css">
</head>
<body>
<header><div class="frame"><a class="brand" href="{e(BASE)}/">{e(sitename)}</a></div></header>
<main class="frame" id="main">{content}</main>
</body>
</html>
"""


def post_date(d):
    return f'<time datetime="{d.isoformat()}">{d.strftime("%B")} {d.day}, {d.year}</time>'


posts = []
for source in sorted((ROOT / "posts").glob("*.md")):
    if source.is_symlink() or not source.is_file():
        continue
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", source.stem):
        raise SystemExit(f"{source.name}: use a lowercase hyphenated filename")
    ast = json.loads(pandoc(source.read_text(encoding="utf-8"), "--to", "json"))
    AST_VERSION = ast["pandoc-api-version"]
    meta = ast["meta"]
    if meta.get("draft", {}).get("c") is True:
        raise SystemExit(f"{source.name}: draft is in posts/. Move it outside posts/ before publishing.")
    try:
        title = meta_text(meta, "title")
        if not title:
            raise ValueError("title is required")
        term = date.fromisoformat(meta_text(meta, "date"))
    except (ValueError, TypeError) as exc:
        raise SystemExit(f"{source.name}: expected a title and date (YYYY-MM-DD): {exc}") from exc
    ast["meta"] = {}
    article = pandoc(json.dumps(ast, ensure_ascii=False), "--from", "json", "--to", "html5", "--no-highlight")
    posts.append((term, source.stem, title, meta_text(meta, "description"), article))

if OUT.is_symlink():
    raise SystemExit("dist/ must not be a symlink")
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
shutil.copyfile(ROOT / "style.css", OUT / "style.css")
(OUT / ".nojekyll").touch()
entries = []
for term, slug, title, description, article in sorted(posts, reverse=True):
    path = f"/posts/{slug}/"
    folder = OUT / path.lstrip("/")
    folder.mkdir(parents=True)
    content = f'<article><h1>{e(title)}</h1>{post_date(term)}<div class="prose">{article}</div></article>'
    (folder / "index.html").write_text(page(title, content, description, path), encoding="utf-8")
    entries.append(f'<li><a href="{e(BASE + path)}">{e(title)}</a>{post_date(term)}</li>')
listing = '<ul class="entries">' + "".join(entries) + "</ul>" if entries else "<p>No posts yet.</p>"
description = f'<p>{e(CONFIG["description"])}</p>' if CONFIG["description"] else ""
home = f'<h1>{e(CONFIG["title"])}</h1>{description}{listing}'
(OUT / "index.html").write_text(page(CONFIG["title"], home), encoding="utf-8")
print(f"Built {len(posts)} post(s).")
