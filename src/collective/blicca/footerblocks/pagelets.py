"""The plone.pageletlayout frame: the head styles.

Loaded only under ``zcml:condition="installed plone.pageletlayout"``
(overrides.zcml) — every pageletlayout import lives in this module and
nothing frame-neutral does, so a stock site never imports it. The footer
itself is the stock viewlet (viewlets.py): pageletlayout's slot layout
renders plone.portalfooter.
"""

from plone.pageletlayout.pagelets.head import StylesChromePagelet

from collective.blicca.footerblocks.footer import stylesheet_links
from collective.blicca.footerblocks.interfaces import ICollectiveBliccaFooterblocksLayer


class FooterStylesChromePagelet(StylesChromePagelet):
    """The head styles provider, plus the blocks stylesheets.

    Registered in overrides.zcml for pageletlayout's own layer — the same
    discriminator as the base stanza, which is what replaces it. The links
    are appended only when this add-on's layer is on the request: a second
    site in the same instance with pageletlayout but without footerblocks
    must get the base output, untouched.
    """

    def render(self):
        markup = super().render()
        if ICollectiveBliccaFooterblocksLayer.providedBy(self.request):
            markup += stylesheet_links(self.context)
        return markup
