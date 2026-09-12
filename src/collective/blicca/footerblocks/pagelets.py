"""The plone.pageletlayout frame: the footer element and the head styles.

Loaded only under ``zcml:condition="installed plone.pageletlayout"``
(pageletlayout.zcml, overrides.zcml) — every pageletlayout import lives in
this module and nothing frame-neutral does, so a stock site never imports
it. The footer logic itself is footer.py.

The footer's *place* is a chrome pagelet in the whole-body layout, inserted
before the plone.pageletlayout footer rows (profiles/default/viewlets.xml) —
the way a theme adds a new element to Clara's page tail. plonetheme.derico's
hard-coded contact band was the precedent, and is the thing this replaces:
the same closing call to action, authored rather than compiled in.

The element is registered under the same name as the stock viewlet
(viewlets.py): a dual registration, pageletlayout's documented porting path.
The layout renders this element, the bridge skips the stock twin.
"""

from plone.pageletlayout.chrome import ChromePagelet
from plone.pageletlayout.pagelets.head import StylesChromePagelet

from collective.blicca.footerblocks.footer import footer_blocks_html
from collective.blicca.footerblocks.footer import stylesheet_links
from collective.blicca.footerblocks.interfaces import ICollectiveBliccaFooterblocksLayer


class FooterBlocksChromePagelet(ChromePagelet):
    """Render the inherited footer blocks at the tail of every page.

    The template wraps the markup in ``.aurora-blocks-view`` — the public
    scope root of the shared blocks stylesheet and of every block add-on's
    ``@scope``-wrapped CSS (block add-on contract §6.1), so footer blocks
    are styled by exactly the sheets that style them in a page body.
    """

    def update(self):
        self.blocks_html = footer_blocks_html(self.context, self.request)


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
