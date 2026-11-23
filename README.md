# Dharma

A small, text-first blog with warm paper tones, Georgia typography, and no tracking or external fonts. The design is Ink-inspired.

## Write in Obsidian

Clone this repository. Open its `posts/` folder as a separate Obsidian vault for finished, public posts. If the folder is missing, create it first. Keep private notes and drafts in a different vault; this repository and its Git history are public.

1. Create a Markdown note in `posts/`, such as `first-essay.md`. Use lowercase letters, digits, and hyphens in filenames.
2. Copy the properties from [POST-TEMPLATE.md](POST-TEMPLATE.md). Only `title` and `date` (YYYY-MM-DD) are required.
3. Use standard Markdown links, not Obsidian wiki links or embeds.
4. Commit and push to `main`. The **Publish blog** workflow automatically rebuilds the site. Saving locally does not publish.

## Preview and hosting

Install Python 3 and Pandoc, run `python3 build.py`, then `python3 -m http.server --bind 127.0.0.1 --directory dist 8000`. Open http://localhost:8000.

The site uses free GitHub Pages. The intended custom domain is `nalanda.hu`. Configure it under **Settings → Pages** after verifying DNS ownership, then rerun **Publish blog** after the domain is active. See the [GitHub Pages custom-domain guide](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).

Edit `site.json` to change the blog title or description.
