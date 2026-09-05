# collective.blicca.footerblocks

An **editable site footer** for classic Plone 6, built from Aurora blocks.

Editors compose the footer in the Aurora block editor, the same way they
compose a page: text, links, lists, and any installed Aurora block add-on.
The footer is stored once, usually on the site root, and rendered
server-side at the bottom of every page. A language folder or subsite can
carry its own footer, which then replaces the site-wide one below that
point.

The footer content is stored in the `footer` field that
[collective.volto.footer](https://github.com/collective/collective.volto.footer)
defines, so a Volto frontend and a classic Plone site can share one footer.
This package is the classic-Plone half: it renders that field through
[plone.blicca.auroraeditor](https://github.com/derico-de/plone.blicca.auroraeditor)
and mounts the Aurora editor on it.

## Features

- **Blocks in the footer.** Paragraphs, links, lists, and every Aurora block
  add-on installed on the site, for example an actions block for the site
  actions or a promo block for a closing call to action.
- **Edit in place.** People allowed to edit the footer's carrier see an
  "Edit footer" link in the footer that opens the Aurora editor on the footer
  content. Full-bleed block widths are allowed there, since a footer is a
  full-width band.
- **Inherited down the tree.** The footer of the nearest ancestor that has
  the editable-footer behavior is shown. Enable the behavior on a folder type
  to give a section or a language its own footer.
- **Shared with Volto.** The storage is `collective.volto.footer`'s field, so
  the footer is readable by Volto's `@inherit` expander as well.
- **Styled like page content.** The footer's blocks are wrapped in the same
  scope root as a page body, so the shared blocks stylesheet and every block
  add-on's stylesheet apply unchanged.
- **Invisible until authored.** A site without an authored footer renders no
  footer element at all. No empty band, no placeholder text.

## Requirements

- Plone 6.0 or later
- `plone.blicca.auroraeditor` 1.0.0a2 or later
- `plone.pageletlayout`, the layout this package adds its footer element to
- `collective.volto.footer`, for the storage behavior
- `plone.rest`

All of these are declared as dependencies and pulled in on install.

## Installation

Add the package to your project's dependencies:

```toml
# pyproject.toml
dependencies = [
    "collective.blicca.footerblocks",
]
```

Then install **Collective Blicca Footerblocks** from Plone's Add-ons control
panel, or apply the `collective.blicca.footerblocks:default` GenericSetup
profile. Installing it:

- installs `collective.volto.footer`, `plone.pageletlayout` and
  `plone.blicca.auroraeditor` if they are not installed yet, which enables
  the editable-footer behavior on the Plone Site type;
- adds the footer element to the page layout, directly above the
  copyright, colophon and site-actions rows of `plone.pageletlayout`;
- makes every page load the blocks stylesheets, so footer blocks are styled
  on pages that are not block pages themselves.

## Editing the footer

1. Log in with a role that may edit the site root (or the folder that
   carries the footer).
2. Scroll to the bottom of any page and click **Edit footer**. On a fresh
   site there is no footer yet, so the link is all you see there.
3. Compose the footer in the Aurora editor and save. You are taken back to
   the page, footer on display.

The editor can also be opened directly at `<carrier>/@@edit-footer`, where
the carrier is the site root or a folder with the editable-footer behavior.

To give a section its own footer, enable the
`collective.volto.footer.editable` behavior on that section's content type
in the Dexterity control panel, then edit the footer on that object. Pages
below it show that footer; pages elsewhere keep the site-wide one. An
ancestor that carries the behavior but has never had its footer authored
shows no footer, it does not fall back to the footer above it. This mirrors
how Volto's `@inherit` expander resolves the field.

Footers created in Volto with `slate` text blocks are converted to Aurora
text when opened in the editor. They are not rendered before that: this
package renders Aurora blocks only and has no renderer for Volto's `slate`
block.

## Rendered markup

```html
<footer class="element-footerblocks">
  <div class="aurora-blocks-view">…rendered blocks…</div>
  <a class="element-footerblocks-edit" href="…/@@edit-footer">Edit footer</a>
</footer>
```

The blocks container is emitted only when the footer has blocks. The edit
link is emitted only for users who may edit the carrier. Visitors to a site
without an authored footer get no `<footer>` element.

`.aurora-blocks-view` is the public scope root of the shared blocks CSS and
of every block add-on's scoped stylesheet, so a theme styles footer blocks
exactly as it styles blocks in a page body. Theme the footer band itself
through `.element-footerblocks`.

## How it works

- **Storage.** The footer is the `footer` JSON field of the
  `collective.volto.footer.editable` behavior. It holds one Aurora container
  block whose tree carries the text and any block add-on's nodes.
- **Rendering.** A `plone.pageletlayout` chrome pagelet walks up the
  acquisition chain from the current page to the nearest object with the
  behavior, reads its persisted footer value, and renders the blocks through
  the same pipeline that renders a page body. Only a persisted value counts;
  the behavior's schema default is ignored, which is what keeps an
  unauthored footer invisible.
- **Editing.** Three registrations on the behavior's marker interface form
  the editing surface: the `@@edit-footer` page mounts the Aurora editor on
  the footer field, a `PATCH` to `@footerblocks` saves the container back
  into the field after running the block deserialization transformers, and a
  browser `GET` on `@footerblocks` redirects to the carrier, which is where
  the editor navigates after save or cancel. Editing requires the Modify
  portal content permission on the carrier.
- **Stylesheets.** The package overrides the `plone.pageletlayout.styles`
  head provider on its own browser layer and appends the blocks stylesheets
  after the resource registry output. On block pages the same links are then
  present twice with identical URLs, which the browser fetches once.

## Development

```shell
uv run pytest
```

The tests cover the pagelet, the editing surface (including an HTTP-level
test through an in-process ZServer), and the installed profile.

Every change to a GenericSetup profile XML file needs an upgrade step, even
in an alpha release. Scaffold it with `plonecli add upgrade_step`.

## License

GPL-2.0-or-later

## Author

Maik Derstappen, [derico](https://derico.de), <md@derico.de>
