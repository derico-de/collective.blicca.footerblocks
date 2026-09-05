# Changelog

## 1.0.0a1 (unreleased)

- Offer `full` (full-bleed) as a block width on the footer editing surface.
  A footer is a full-bleed band, so `@@edit-footer` widens the editor's
  text-block width allowlist for its own surface only, through
  `AuroraEditView.text_block_widths` (auroraeditor 1.0.0a2). Body text on a
  content page keeps the page grid. Existing footers are untouched: only the
  allowed list moves, the default width does not.
- Add the footer editing surface: `@@edit-footer` mounts the Aurora editor on
  the carrier's `footer` field, `PATCH <carrier>/@footerblocks` saves it, and
  a browser GET on that same URL redirects back to the carrier (where the
  host pattern navigates after save/cancel). Volto-authored `slate` footers
  are adopted into a somersault on open. Built on
  `plone.blicca.auroraeditor.editing` (auroraeditor ADR 0015).

  The way in is a **Footer** tab on top of the Aurora edit area, after Blocks
  and Content: an `IEditSurfaceTab` subscriber that resolves the nearest
  carrier and is offered only to someone who may modify it. The rendered
  footer element carries no edit chrome of its own, and is suppressed on
  `@@edit-footer` so the content being edited is not repeated below the
  editor.
- Render only an authored (persisted) footer, never the behavior schema's
  slate "Edit" seed: the footer is an Aurora (Plate) container — somersault
  tree plus registered block add-ons' `ploneBlock` nodes — and slate is
  deliberately unsupported.
- Initial release: the footer-blocks chrome pagelet (renders the nearest
  ancestor's `collective.volto.footer` blocks via
  `plone.blicca.auroraeditor.rendering.render_blocks`, ordered before the
  plone.pageletlayout footer rows) and the site-wide blocks-CSS delivery via
  a `plone.pageletlayout.styles` override.
