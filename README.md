# ÇAHSPAR website

Quarto website for https://cahspar.org.tr.

## Language

The source language is British English (`en-GB`). Write new page content, navigation labels, announcements, alternative text and interface messages in British English. Retain personal names, registered names, postal addresses and exact publication titles.

TR, FR and ES use Google Translate with English as the source language and preserve the current page URL. These are automatic translations rather than separately maintained language editions.

Research group pages use British English banner graphics (`assets/*-en.png`), including headings, taglines and the detailed labels in the youth and education banner. The original Turkish images are retained as source assets. The logo explanation is now accessible English text. The official ÇAHSPAR logo is retained as a brand asset.

The membership page links to `assets/membership-application-form.pdf`, an English translation of the original blank application form. The original Turkish form is also available as a separate download on the membership page. Embedded podcast audio, third-party forms and linked external publications retain their original languages.

## Build

Install Quarto and Python 3.11 or later, then run:

```sh
python3 scripts/build_rss_feed.py
quarto render
```

The rendered website is written to `_site/`. The RSS collector uses English discovery queries and omits headlines detected as untranslated Turkish. Original source URLs and Turkish keyword matching are retained. The homepage displays only items from the past 30 days; older cached items are not displayed.

## Deployment

`.github/workflows/quarto-pages.yml` regenerates the publication feed, renders all pages and deploys `_site/` to GitHub Pages when changes reach `main`.

Existing Turkish URL slugs are deliberately preserved to maintain incoming links.
