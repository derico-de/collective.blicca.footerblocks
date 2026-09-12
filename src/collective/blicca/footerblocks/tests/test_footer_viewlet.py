"""The stock frame: the footer blocks on a Barceloneta page (viewlets.py).

The fixture site has plone.pageletlayout importable but not installed, so
Plone's own main_template renders — with the add-on's viewlets in
IPortalFooter and IHtmlHead, and none of pageletlayout's layer-bound
registrations switched on.
"""

import pytest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.blicca.auroraeditor.interfaces import IPloneBliccaAuroraeditorLayer
from plone.pageletlayout.interfaces import IPlonePageletlayoutLayer
from zope.component import getUtility
from zope.interface import alsoProvides

from collective.blicca.footerblocks.interfaces import ICollectiveBliccaFooterblocksLayer
from collective.blicca.footerblocks.tests.test_footer_rendering import footer_value


VIEWLET = "collective.blicca.footerblocks.footerblocks"
MANAGER = "plone.portalfooter"
ELEMENT = '<div class="element-footerblocks">'
BLOCKS_CSS = "++resource++plone.blicca.auroraeditor.blocks.css"


class TestPlacement:
    """The stored stock order, not the registration."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        storage = getUtility(IViewletSettingsStorage)
        self.order = list(storage.getOrder(MANAGER, "Plone Default"))

    def test_the_viewlet_is_in_the_footer_order(self):
        assert VIEWLET in self.order

    def test_it_comes_before_the_footer_portlets(self):
        assert self.order.index(VIEWLET) < self.order.index("plone.footer")


class StockPageBase:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, ICollectiveBliccaFooterblocksLayer)
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Document", "somewhere", title="Somewhere")

    def _page(self, context=None, name="document_view"):
        return (context or self.portal.somewhere).restrictedTraverse(name)()


class TestStockPage(StockPageBase):
    def test_the_frame_is_stock_plone(self):
        # The layer fix (spec §4): footerblocks alone must not switch on
        # pageletlayout's main_template bridge.
        assert not IPlonePageletlayoutLayer.providedBy(self.request)
        html = self._page()
        assert 'id="portal-footer-wrapper"' in html
        assert "element-portalfooter" not in html

    def test_the_footer_renders_inside_the_stock_footer_wrapper(self):
        self.portal.footer = footer_value("stock words")
        html = self._page()
        wrapper = html.index('id="portal-footer-wrapper"')
        assert html.count(ELEMENT) == 1
        assert html.index(ELEMENT) > wrapper
        assert "stock words" in html
        assert "aurora-blocks-view" in html

    def test_the_footer_comes_before_the_footer_portlets(self):
        self.portal.footer = footer_value("stock words")
        html = self._page()
        assert html.index(ELEMENT) < html.index("portletWrapper")

    def test_an_unauthored_footer_renders_no_element(self):
        assert "element-footerblocks" not in self._page()

    def test_the_footer_stays_off_its_editing_surface(self):
        self.portal.footer = footer_value("words being edited")
        self.request["ACTUAL_URL"] = f"{self.portal.absolute_url()}/@@edit-footer"
        assert "element-footerblocks" not in self._page(self.portal, "@@edit-footer")

    def test_a_visitor_sees_the_footer(self):
        from plone import api
        from plone.app.testing import logout

        self.portal.footer = footer_value("public words")
        api.content.transition(self.portal.somewhere, "publish")
        logout()
        assert "public words" in self._page()


class TestStockHead(StockPageBase):
    def test_every_page_head_carries_the_blocks_css_once(self):
        html = self._page()
        head = html[: html.index("</head>")]
        assert head.count(BLOCKS_CSS) == 1

    def test_the_links_are_there_without_an_authored_footer(self):
        # The sheets are per page, not per footer: a page can carry blocks
        # of its own, and the head must not flicker with the footer.
        assert BLOCKS_CSS in self._page()
