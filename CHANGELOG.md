# Changelog

## 1.0.0a1 (unreleased)

- Render only an authored (persisted) footer, never the behavior schema's
  slate "Edit" seed: the footer is an Aurora (Plate) container — somersault
  tree plus registered block add-ons' `ploneBlock` nodes — and slate is
  deliberately unsupported.
- Initial release: the footer-blocks chrome pagelet (renders the nearest
  ancestor's `collective.volto.footer` blocks via
  `plone.blicca.auroraeditor.rendering.render_blocks`, ordered before the
  plone.pageletlayout footer rows) and the site-wide blocks-CSS delivery via
  a `plone.pageletlayout.styles` override.
