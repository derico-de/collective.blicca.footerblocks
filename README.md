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
- **A tab in the editor.** People allowed to edit the footer's carrier get a
  **Footer** tab on top of the Aurora edit area, after **Blocks** and
  **Content**. It opens the editor on the inherited footer; full-bleed block
  widths are allowed because a footer is a full-width band.
- **Inherited down the tree.** The footer of the nearest ancestor that has
  the editable-footer behavior is shown. Enable the behavior on a folder type
  to give a section its own footer.
- **One footer per language.** An opt-in profile makes every
  plone.app.multilingual language root folder a footer carrier, so `/de` and
  `/en` each edit and render their own.
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
`plone.app.multilingual` is not a dependency; it is only needed for the
opt-in per-language footers profile, on a site that already has it.

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
2. Open any page in the Aurora editor and pick the **Footer** tab on top of
   the edit area. The tab is there before the first footer block is authored.
3. Compose the footer in the Aurora editor and save. You are taken back to
   the page, footer on display.

The footer surface starts directly with footer content: it does not show the
carrier site's or folder's document title, because that metadata is not part
of the published footer.

The editor can also be opened directly at `<carrier>/@@edit-footer`, where
the carrier is the site root or a folder with the editable-footer behavior.

## Per-language footers

On a multilingual site the language root folders (`LRF`) are not footer
carriers out of the box: `collective.volto.footer` puts the editable-footer
behavior on the Plone Site type and nothing else. `/de` and `/en` therefore
have no `@@edit-footer`, and the **Footer** tab of a page below them opens
the site-wide footer instead.

Apply the `collective.blicca.footerblocks:multilingual` profile to change
that. It adds the behavior to the `LRF` type, and from then on every language
folder edits and renders a footer of its own. The existing language folders
become carriers immediately — a Dexterity object provides its behaviors'
marker interfaces the moment the type names them, so no content is migrated.
The profile requires plone.app.multilingual, and it is opt-in on purpose: a
multilingual site that wants one shared footer for all languages simply does
not apply it.

Extra profiles are not listed in the Add-ons control panel. Apply this one
from `portal_setup` → **Import**, choosing *Collective Blicca Footerblocks:
per-language footers* as the profile.

Mind the nearest-carrier rule when you do: a language folder that carries the
behavior but has never had its footer authored shows **no** footer, it does
not fall back to the site root's. To keep the published site unchanged, copy
the inherited footer into each language once:

```python
from collective.blicca.footerblocks.multilingual import seed_language_footers

seed_language_footers(portal)
```

It seeds only language folders that have no footer yet, so running it twice
is harmless. Each language then owns its copy and can be edited on its own.

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
</footer>
```

The element is emitted only when the footer has blocks, and it is suppressed
on the `@@edit-footer` surface so the content being edited is not repeated
below the editor. Visitors to a site without an authored footer get no
`<footer>` element.

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
- **Editing.** An ``IEditSurfaceTab`` subscriber resolves the nearest footer
  carrier and puts a **Footer** tab in the Aurora editor's tab strip when the
  current user may modify that carrier. The `@@edit-footer` page mounts the Aurora editor on its footer
  field, a `PATCH` to `@footerblocks` saves the container after running the
  block deserialization transformers, and a browser `GET` on `@footerblocks`
  redirects to the carrier after save or cancel.
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
