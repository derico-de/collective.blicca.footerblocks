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
body. No footer up the chain, or an empty container, renders nothing.

A language folder or subsite overrides the site-wide footer by enabling the
`collective.volto.footer.editable` behavior on its type and authoring its
own `footer` value — nearest ancestor wins, exactly like `@inherit`.

## Current limits

- The footer is expected to be **authored through Aurora** (a somersault
  container). A Volto-authored footer of top-level `slate` blocks renders as
  invisible `block-unrendered` placeholders until an `aurora-block-slate`
  renderer exists — including `collective.volto.footer`'s default "Edit"
  seed on a never-authored site.
- The Aurora **editing surface** for the footer field (the JS half, to be
  published as `aurora-footerblocks`) is not part of this release.

## Development

```shell
uv run pytest src/collective/blicca/footerblocks/tests
```
