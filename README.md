# korczakaustralia.github.io

Website of the Janusz Korczak Association Australia — https://korczakaustralia.com.au

The site was originally built with Mobirise (AMP export). It has been converted to plain,
hand-editable HTML/CSS/JS with the same look. Nothing depends on Mobirise or the AMP runtime
any more, and no external fonts or scripts are loaded.

## Layout

```
index.html, about.html, events.html … one file per page, named after its content
page1.html … page47.html              redirect stubs so the old Mobirise URLs keep working (safe to delete later)
assets/css/site.css                   fonts + base rules + the theme rules shared by every page
assets/css/pages/<page>.css           the rules that only that page uses (one file per page)
assets/js/site.js                     menu, accordion, slider, image viewer, contact form
assets/images/                        all site images, compressed (WebP)
assets/files/                         downloadable documents (PDF)
fonts/                                Reem Kufi and Roboto, self-hosted (woff2)
CNAME                                 custom domain for GitHub Pages
```

## Pages

| File | Page |
|---|---|
| index.html | Home |
| korczak.html | Korczak |
| about.html | About |
| stories.html | Stories |
| events.html | Events |
| activities.html | Activities |
| childrens-rights.html | Children's Rights |
| contact.html | Contact |
| other *.html | individual event/article pages linked from Home, Events or Activities, named after their title |

The News section and the article pages only it linked to have been removed, as have old drafts and duplicates nothing linked to.

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
