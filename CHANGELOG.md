# Changelog

## 1.0.0a1 (unreleased)

- Add the footer editing surface: `@@edit-footer` mounts the Aurora editor on
  the carrier's `footer` field, `PATCH <carrier>/@footerblocks` saves it, and
  a browser GET on that same URL redirects back to the carrier (where the
  host pattern navigates after save/cancel). Volto-authored `slate` footers
  are adopted into a somersault on open, and the footer element carries an
  "Edit footer" link for anyone allowed to author it. Built on
  `plone.blicca.auroraeditor.editing` (auroraeditor ADR 0015).
- Render only an authored (persisted) footer, never the behavior schema's
  slate "Edit" seed: the footer is an Aurora (Plate) container — somersault
  tree plus registered block add-ons' `ploneBlock` nodes — and slate is
  deliberately unsupported.
- Initial release: the footer-blocks chrome pagelet (renders the nearest
  ancestor's `collective.volto.footer` blocks via
  `plone.blicca.auroraeditor.rendering.render_blocks`, ordered before the
  plone.pageletlayout footer rows) and the site-wide blocks-CSS delivery via
  a `plone.pageletlayout.styles` override.
