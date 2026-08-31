# collective.blicca.footerblocks

Blicca rendering of editable footer blocks, in a pagelet chrome.

The footer's **content** is ordinary editable blocks, stored the way the
Volto ecosystem stores an editable footer:
[`collective.volto.footer`](https://github.com/collective/collective.volto.footer)'s
`footer` JSONField (behavior `collective.volto.footer.editable`, enabled on
the Plone Site type by that add-on's profile). Volto frontends read the field
through plone.restapi's `@inherit` expander; this add-on is the **Blicca**
half of the same data: a chrome pagelet walks the acquisition chain for the
nearest object carrying the behavior and renders its blocks server-side
through `plone.blicca.auroraeditor`'s promised `render_blocks` pipeline.

The footer's **place** is a [`plone.pageletlayout`](https://github.com/plone/plone.pageletlayout)
chrome pagelet in the whole-body layout, inserted directly before the
`plone.pageletlayout` footer rows (copyright / colophon / site actions).

## What installing does

- pulls `collective.volto.footer:default` (the behavior on the Plone Site
  type), `plone.pageletlayout:default` and `plone.blicca.auroraeditor:default`;
- registers the `collective.blicca.footerblocks.footerblocks` chrome pagelet
  and orders it before `plone.pageletlayout.copyright`;
- overrides the `plone.pageletlayout.styles` provider on its own browser
  layer so **every** page's head carries the shared blocks stylesheet and the
  registered block add-ons' stylesheets — the footer renders blocks on pages
  that are not blocks pages.

## Markup

```html
<footer class="element-footerblocks">
  <div class="aurora-blocks-view">…rendered blocks…</div>
</footer>
```

`.aurora-blocks-view` is the public scope root of the shared blocks CSS and
of every block add-on's `@scope`-wrapped CSS (block add-on contract §6.1),
so footer blocks are styled by exactly the sheets that style them in a page
body. No footer up the chain, a never-authored one, or an empty container
renders nothing.

A language folder or subsite overrides the site-wide footer by enabling the
`collective.volto.footer.editable` behavior on its type and authoring its
own `footer` value — nearest ancestor wins, exactly like `@inherit`.

## Aurora only — no slate

The footer is an **Aurora (Plate) container**: one somersault block whose
tree carries the text (paragraphs, marks, links, lists) plus any registered
block add-on's `ploneBlock` nodes — all dispatched by the very pipeline
that renders a page body, so every installed aurora block works in the
footer. Volto `slate` blocks are deliberately unsupported (there is no
`aurora-block-slate` renderer).

Only an **authored** footer renders: Dexterity serves the behavior schema's
default (`collective.volto.footer`'s slate "Edit" seed) for a never-set
field, and the pagelet reads only the persisted value — a fresh site shows
no footer element at all instead of invisible slate placeholders.

## Current limits

- The Aurora **editing surface** for the footer field (the JS half, to be
  published as `aurora-footerblocks`) is not part of this release; author
  the `footer` field over the REST API meanwhile.

## Development

```shell
uv run pytest src/collective/blicca/footerblocks/tests
```
