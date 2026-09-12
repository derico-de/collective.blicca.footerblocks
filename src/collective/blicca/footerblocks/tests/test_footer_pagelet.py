"""The plone.pageletlayout frame: the footer element (pagelets.py).

On the pageletlayout fixture the site has pageletlayout's profile applied,
so a request carrying its layer renders the whole-body layout — with the
footer as a layout element, and the stock twin skipped by the bridge.
"""

import pytest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.blicca.auroraeditor.interfaces import IPloneBliccaAuroraeditorLayer
from plone.pageletlayout.interfaces import IPlonePageletlayoutLayer
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import alsoProvides
from zope.interface import noLongerProvides

from collective.blicca.footerblocks.interfaces import ICollectiveBliccaFooterblocksLayer
from collective.blicca.footerblocks.pagelets import FooterBlocksChromePagelet
from collective.blicca.footerblocks.pagelets import FooterStylesChromePagelet
from collective.blicca.footerblocks.tests.test_footer_rendering import footer_value


VIEWLET = "collective.blicca.footerblocks.footerblocks"
MANAGER = "plone.pageletlayout.layout"
ELEMENT = '<div class="element-footerblocks">'
BLOCKS_CSS = "++resource++plone.blicca.auroraeditor.blocks.css"


class TestPlacement:
    """The stored layout order, not the registration."""

    @pytest.fixture(autouse=True)
    def _setup(self, pageletlayout_integration):
        storage = getUtility(IViewletSettingsStorage)
        self.order = list(storage.getOrder(MANAGER, "Plone Default"))

    def test_the_element_is_in_the_layout_order(self):
        assert VIEWLET in self.order

    def test_it_comes_after_the_page_body(self):
        assert self.order.index(VIEWLET) > self.order.index("plone.pageletlayout.body")

    def test_it_comes_before_every_footer_row(self):
        for row in (
            "plone.pageletlayout.copyright",
            "plone.pageletlayout.colophon",
            "plone.pageletlayout.siteactions",
        ):
            assert self.order.index(VIEWLET) < self.order.index(row), row


class PageletPageBase:
    @pytest.fixture(autouse=True)
    def _setup(self, pageletlayout_integration):
        self.portal = pageletlayout_integration["portal"]
        self.request = pageletlayout_integration["request"]
        alsoProvides(self.request, IPlonePageletlayoutLayer)
        alsoProvides(self.request, ICollectiveBliccaFooterblocksLayer)
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Document", "somewhere", title="Somewhere")

    def _page(self, context=None, name="pagelet_view"):
        return (context or self.portal.somewhere).restrictedTraverse(name)()

    def _provider(self, name):
        view = self.portal.restrictedTraverse("@@plone")
        provider = getMultiAdapter(
            (self.portal.somewhere, self.request, view), IContentProvider, name=name
        )
        provider.update()
        return provider


class TestElement(PageletPageBase):
    def test_it_is_registered_under_the_name_the_layout_asks_for(self):
        self.portal.footer = footer_value("registered words")
        provider = self._provider(VIEWLET)
        assert isinstance(provider, FooterBlocksChromePagelet)
        assert "element-footerblocks" in provider.render()

    def test_the_pagelet_renders_inside_the_scope_root(self):
        self.portal.footer = footer_value("footer words")
        markup = self._provider(VIEWLET).render()
        assert ELEMENT in markup
        assert "aurora-blocks-view" in markup
        assert "footer words" in markup

    def test_an_unauthored_footer_renders_no_element(self):
        assert "element-footerblocks" not in self._provider(VIEWLET).render()


class TestPageletPage(PageletPageBase):
    def test_the_frame_is_the_pagelet_layout(self):
        html = self._page()
        assert "element-portalfooter" in html
        assert 'id="portal-footer-wrapper"' not in html

    def test_the_footer_renders_exactly_once(self):
        self.portal.footer = footer_value("layout words")
        html = self._page()
        assert html.count(ELEMENT) == 1
        assert html.count("layout words") == 1

    def test_the_element_renders_and_the_bridge_skips_the_twin(self):
        # The one occurrence is the layout element, before the footer rows
        # — not the stock viewlet riding the portalfooter bridge.
        self.portal.footer = footer_value("layout words")
        html = self._page()
        bridge = html.index("element-portalfooter")
        bridge_end = html.index("element-", bridge + 1)
        assert "element-footerblocks" not in html[bridge:bridge_end]
        assert html.index(ELEMENT) < html.index("element-copyright")

    def test_the_footer_stays_off_its_editing_surface(self):
        self.portal.footer = footer_value("words being edited")
        self.request["ACTUAL_URL"] = f"{self.portal.absolute_url()}/@@edit-footer"
        assert "element-footerblocks" not in self._page(self.portal, "@@edit-footer")


class TestStyles(PageletPageBase):
    """The overridden styles provider ships the blocks stylesheets."""

    def test_the_override_replaced_the_base_provider(self):
        assert isinstance(self._provider("plone.pageletlayout.styles"), FooterStylesChromePagelet)

    def test_every_page_head_gets_the_blocks_css_once(self):
        html = self._page()
        head = html[: html.index("</head>")]
        assert head.count(BLOCKS_CSS) == 1

    def test_a_pageletlayout_request_without_the_addon_gets_the_base_output(self):
        # A second site in the same instance, pageletlayout but no
        # footerblocks: the override is registered on pageletlayout's layer
        # and must behave like the stanza it replaced.
        noLongerProvides(self.request, ICollectiveBliccaFooterblocksLayer)
        provider = self._provider("plone.pageletlayout.styles")
        markup = provider.render()
        assert BLOCKS_CSS not in markup
        assert "stylesheet" in markup
