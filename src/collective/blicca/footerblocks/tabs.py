"""The Footer tab of the Aurora edit-area strip.

The footer's carrier is an *ancestor* of the page being edited (usually the
site root), so its own edit chrome is nowhere near the page an author is
working on. This tab is the way in: registered as an ``IEditSurfaceTab``
subscriber, it appears alongside Blocks and Content at the top of every
Aurora edit surface, resolving the nearest carrier the same way the
renderer does — a page beneath a language folder edits that folder's
footer, not the site root's.
"""

from AccessControl import getSecurityManager
from plone.blicca.auroraeditor.editing import EditSurfaceTab
from Products.CMFCore.permissions import ModifyPortalContent

from collective.blicca.footerblocks.i18n import _
from collective.blicca.footerblocks.pagelets import footer_carrier


class FooterTab(EditSurfaceTab):
    """Edit the inherited footer, wherever the strip is rendered."""

    id = "footer"
    title = _("Footer")
    order = 30
    view_name = "edit-footer"

    @property
    def carrier(self):
        """The nearest footer owner in the context's acquisition chain."""
        return footer_carrier(self.context)

    @property
    def available(self):
        """Offered only to someone who may author that carrier's footer.

        The permission is checked on the carrier, not on the page: editing
        a page one is allowed to edit says nothing about the site-wide
        footer, and ``@@edit-footer`` is registered on the carrier.
        """
        carrier = self.carrier
        return bool(
            carrier is not None
            and getSecurityManager().checkPermission(ModifyPortalContent, carrier)
        )

    @property
    def url(self):
        return f"{self.carrier.absolute_url()}/@@{self.view_name}"
