"""The stock-Plone frame: viewlets in Plone's own managers.

On a stock Plone 6 site (Barceloneta, or any Diazo theme) ``main_template``
renders ``IPortalFooter`` inside ``<footer id="portal-footer-wrapper">``,
full width, so the footer blocks land there — before ``plone.footer`` (the
footer portlets), by the ``plone.portalfooter`` order in
profiles/default/viewlets.xml. The blocks stylesheets reach ``<head>``
through ``IHtmlHead``.

Both viewlets are also the twin of a plone.pageletlayout registration
(pagelets.py): on a pagelet page the layout renders the element under the
same name and pageletlayout's bridge skips the stock twin, and its head is
composed from wrapped renderers, so ``plone.htmlhead`` is never rendered
there at all. Nothing doubles up on either frame.
"""

from plone.app.layout.viewlets import ViewletBase

from collective.blicca.footerblocks.footer import footer_blocks_html
from collective.blicca.footerblocks.footer import stylesheet_links


class FooterBlocksViewlet(ViewletBase):
    """The footer blocks in ``IPortalFooter``; markup from footerblocks.pt."""

    def update(self):
        self.blocks_html = footer_blocks_html(self.context, self.request)


class FooterBlocksStylesViewlet(ViewletBase):
    """The blocks stylesheets in ``IHtmlHead``."""

    def update(self):
        pass

    def render(self):
        return stylesheet_links(self.context)
