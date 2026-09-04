# korczakaustralia.github.io

Website of the Janusz Korczak Association Australia — https://korczakaustralia.com.au

The site was originally built with Mobirise (AMP export). It has been converted to plain,
hand-editable HTML/CSS/JS with the same look. Nothing depends on Mobirise or the AMP runtime
any more, and no external fonts or scripts are loaded.

## Layout

```
index.html, news.html, about.html …   one file per page, named after its content
page1.html … page47.html              redirect stubs so the old Mobirise URLs keep working (safe to delete later)
assets/css/site.css                   fonts + base rules + the theme rules shared by every page
assets/css/pages/<page>.css           the rules that only that page uses (one file per page)
assets/js/site.js                     menu, accordion, slider, image viewer, contact form
assets/images/                        all site images, compressed (WebP)
assets/images/updates/                images pulled from the Google Doc by the news sync
assets/files/                         downloadable documents (PDF)
fonts/                                Reem Kufi and Roboto, self-hosted (woff2)
scripts/sync_news.py                  Google Doc -> news.html converter
.github/workflows/sync-news.yml       runs the converter every 30 minutes
CNAME                                 custom domain for GitHub Pages
```

## Pages

| File | Page |
|---|---|
| index.html | Home |
| korczak.html | Korczak |
| about.html | About |
| stories.html | Stories |
| news.html | News (Latest Updates + news cards) |
| events.html | Events |
| activities.html | Activities |
| childrens-rights.html | Children's Rights |
| contact.html | Contact |
| other *.html | individual news/event articles, named after their title |

Pages that nothing linked to (old drafts and duplicates) have been removed.

## News: automatic updates from Google Docs

The "Latest Updates" block at the top of `news.html` is generated from the published Google Doc
"Website Updates". Whatever is in that document is shown on the public site, so keep the
document to things meant for publication.

* `scripts/sync_news.py` downloads the published document, converts headings, paragraphs,
  bold/italic, links, lists, tables and images into the site's own markup, saves any images into
  `assets/images/updates/`, and rewrites the block between `<!-- news:start -->` and
  `<!-- news:end -->` in `news.html`. Never edit between those two markers by hand.
* `.github/workflows/sync-news.yml` runs the script every 30 minutes (GitHub's schedule is
  best-effort, so allow up to an hour) and commits only when the content actually changed.
  You can also run it immediately from the repository's **Actions** tab → *Sync news from
  Google Doc* → *Run workflow*.
* One-time setup on GitHub: *Settings → Actions → General → Workflow permissions* must allow
  **Read and write permissions**, otherwise the commit step cannot push.
* Formatting in the doc: use *Heading 1* for the title of an update and *Heading 2* for
  sub-headings; the document's *Title* style is ignored. Links, bold and italic come through.

## Editing

* Text and links: edit the HTML directly. Each page is a series of `<section class="… cid-XXXX">`
  blocks; the `cid-…` class ties a section to its styles in `assets/css/pages/<page>.css`.
* Images: `<div class="amp-img" style="--ratio: 75%"><img src="…"></div>`. `--ratio` is
  height ÷ width as a percentage and fixes the box shape so the page does not jump while
  images load. Add new images to `assets/images/` (WebP or JPEG/PNG both work).
* Menu: the navigation appears twice in every page — once in the `<aside id="sidebar">`
  (mobile off-canvas menu) and once in `<section class="menu">` (desktop bar). Update both.
* Behaviours are driven by data attributes: `data-sidebar`, `data-accordion`,
  `data-carousel`, `data-lightbox`, `data-form`. See `assets/js/site.js`.
* Contact form (contact.html) posts to Formoid, the service the Mobirise form used.
