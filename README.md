# ICU AND YOU

Teaching material for the intensive care education programme at Coffs Harbour
Health Campus. Published with GitHub Pages.

## Getting it online (once only)

1. Create a free account at github.com
2. New repository, named `icu-and-you`, set to **Public**, then Create
3. Settings -> Pages -> Source: "Deploy from a branch", Branch: `main`, Folder: `/ (root)`, Save
4. Back on the Code tab: Add file -> Upload files, drag in everything from this
   folder (index.html, README.md and the four folders), then Commit changes
5. Wait a minute. The site is live at `https://YOURNAME.github.io/icu-and-you/`

## Adding next week's piece

1. Code tab -> open the right folder (`mind-maps`, `aphorisms`, `superpuzzles`,
   `mnemonics`) -> Add file -> Upload files -> drag the new HTML in -> Commit
2. Code tab -> click `index.html` -> pencil icon to edit
3. Copy one of the existing list blocks, paste it at the top
   of the list, and change the colour class, `data-series`, badge label and
   number, title, description, and link `href`. There is a comment in the file
   explaining exactly this.
4. Commit changes. Live within a minute.

## File naming

Lowercase, hyphens, no spaces:

    mind-maps/mind-map-31-topic.html
    aphorisms/aphorism-35-topic.html
    superpuzzles/superpuzzle-48-topic.html
    superpuzzles/superpuzzle-48-topic-fillable.html
    mnemonics/mnemonic-53-topic.html

Keeping the number in the filename means the folders sort themselves.

## Before you publish: two things

**The site is public.** On the free plan, anything uploaded is visible to anyone
with the address, even from a private repository. That is fine for teaching
material. It means: never upload an answer key, and never upload anything with a
patient detail in it.

**The reply address will be harvested.** Every file here contains a `mailto:`
link. Public pages get crawled by address-collecting bots, and spam follows
within months. Set up a dedicated forwarding address — something like
`icuandyou@…` — and swap it into the files before the first upload. If it is
ever swamped you retire that address and your personal mail is untouched.

To swap it later: open each file with the pencil icon, use the browser's
find-and-replace, or ask for the files to be regenerated with the new address.

## What is here

    index.html                  the landing page
    mind-maps/                  the mind map series
    aphorisms/                  the aphorism series
    superpuzzles/               the crossword series (printable + fillable)
    mnemonics/                  the mnemonic series
