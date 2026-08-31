"""The footer editing surface: Aurora mounted on the ``footer`` field.

The field-surface pattern of plone.blicca.auroraeditor's ADR 0015, applied
to ``collective.volto.footer``'s JSONField. Three registrations against the
behavior's marker (configure.zcml), all subclassing the promised
``plone.blicca.auroraeditor.editing`` surface:

- ``@@edit-footer`` — the edit page: the unchanged editor remote, mounted
  on the carrier's *authored* footer container (never the behavior's slate
  "Edit" seed, mirroring the renderer), with Volto-authored slate blocks
  adopted into a somersault in memory;
- ``PATCH <carrier>/@footerblocks`` — the save target the mount config's
  ``contentUrl`` points at: standard save body in, deserialization
  transformers run, container stored in ``footer``, the body's ``title``
  dropped (the site title is not the footer's to edit);
- ``GET <carrier>/@footerblocks`` — where the host pattern's post-save and
  post-cancel navigation lands (text/html, so plone.rest stays out of the
  way): a redirect to the carrier, footer on display.
"""

from plone.blicca.auroraeditor.editing import AuroraFieldEditView
from plone.blicca.auroraeditor.editing import FieldBlocksPatch


class FooterEditView(AuroraFieldEditView):
    """@@edit-footer — the Aurora surface of the inherited site footer."""

    field_name = "footer"
    save_service = "@footerblocks"


class FooterBlocksPatch(FieldBlocksPatch):
    """PATCH @footerblocks — the footer's save target."""

    field_name = "footer"
