# Changelog

## 1.0.0a1 (unreleased)

- The Footer tab sends the page it sits on along as the `origin` request
  parameter, and `@@edit-footer` renders that page's tab strip instead of
  the carrier's. The carrier's strip had no Content tab (a site root has no
  metadata form) and a Blocks tab into `<site>/@@aurora-edit`, where the
  editor failed on an object without blocks. Save and cancel now land back
  on the page the author came from rather than on the carrier. Needs the
  plone.blicca.auroraeditor that ships `EditSurfaceTab.surface_url`.

- The uninstall and upgrade profiles are out of the Add-ons control panel
  again. `HiddenProfiles` named them all along, but the `INonInstallable`
  utility was never registered in `configure.zcml` — and the panel (and
  `GET /@addons`) only ever sees the class through that registration, so the
  list was inert and `collective.blicca.footerblocks.upgrades` was offered as an installable
  add-on of its own. Installing an upgrade profile by hand imports its XML
  without moving the recorded profile version, leaving the site behind what it
  actually has. The test reads the list out of the utility registry now,
  where the control panel reads it, instead of instantiating the class — which
  is why it stayed green through all of this.

- Add the opt-in `multilingual` profile: per-language footers. Language root
  folders (`LRF`) of plone.app.multilingual are not footer carriers out of the
  box — collective.volto.footer marks the Plone Site type only — so
  `@@edit-footer` was not registered on `/de` or `/en` and the editor's Footer
  tab sent authors to the site root. Applying
  `collective.blicca.footerblocks:multilingual` puts the editable-footer
  behavior on the `LRF` type, after which each language edits and renders a
  footer of its own. Existing language folders become carriers without a
  content migration; the site-wide footer is untouched, and a multilingual
  site that wants one shared footer simply does not apply the profile.

  Because renderer and tab both stop at the *nearest* carrier (Volto
  `@inherit` semantics), a language folder that carries the behavior but has
  no footer of its own shows none — it does not fall back to the site root's.
  The profile therefore seeds itself: its `post_handler` copies the inherited
  footer into every unauthored language folder, in the same transaction as
  the type import, so applying the profile is one action and the published
  footer is never missing in between. Seeding is idempotent — a language
  folder that has a footer of its own is left alone, and re-importing the
  profile changes nothing.

- Upgrade the `multilingual` profile 1000 → 1001. Version 1000 imported the
  type and stopped there, leaving each language publishing no footer until
  someone called `seed_language_footers()` by hand. The step runs that
  seeding, so a site that applied the profile at 1000 reaches the same state
  a fresh apply now produces. It touches no import step and is idempotent, so
  it is a no-op on a site that was seeded by hand already.

- Hide the carrier site's or folder's document title from the Aurora footer
  canvas. It is metadata for the carrier, not publishable footer content;
  existing title nodes are omitted and Title is not offered in the slash menu.

- Remove the `footer_edit` object action on upgrade to profile version 1001.
  An earlier build reached the footer through a Plone object action whose
  `available_expr` traversed `@@footer-edit-action`; the Footer tab in the
  Aurora editor replaced both, and a site that had imported the action raises
  `AttributeError` on every page that renders the toolbar until it is gone.
  Sites that never had it are untouched — GenericSetup skips a `remove` for an
  id that is not there — and a fresh install is stamped 1001 already.

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

  The way in is a **Footer** tab on top of the Aurora edit area, between
  Blocks and Content: an `IEditSurfaceTab` subscriber that resolves the nearest
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
