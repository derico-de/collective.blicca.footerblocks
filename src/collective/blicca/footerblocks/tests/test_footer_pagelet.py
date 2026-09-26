"""The plone.pageletlayout frame.

On the pageletlayout fixture the site has pageletlayout's profile applied,
so a request carrying its layer renders the slot layout, whose footer
landmark renders plone.portalfooter — and with it the stock footer viewlet.
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
from collective.blicca.footerblocks.pagelets import FooterStylesChromePagelet
from collective.blicca.footerblocks.tests.test_footer_rendering import footer_value


VIEWLET = "collective.blicca.footerblocks.footerblocks"
MANAGER = "plone.portalfooter"
ELEMENT = '<div class="element-footerblocks">'
BLOCKS_CSS = "++resource++plone.blicca.auroraeditor.blocks.css"


class TestPlacement:
    """The stock viewlet's place in plone.portalfooter, the slot the
    pageletlayout frame renders in its footer landmark."""

    @pytest.fixture(autouse=True)
    def _setup(self, pageletlayout_integration):
        storage = getUtility(IViewletSettingsStorage)
        self.order = list(storage.getOrder(MANAGER, "Plone Default"))

    def test_it_comes_before_the_footer_portlets(self):
        assert self.order.index(VIEWLET) < self.order.index("plone.footer")

    def test_it_comes_before_every_footer_row(self):
        for row in (
            "plone.pageletlayout.copyright",
            "plone.pageletlayout.colophon",
            "plone.pageletlayout.siteactions",
        ):
            assert self.order.index(VIEWLET) < self.order.index(row)


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


class TestPageletPage(PageletPageBase):
    def test_the_frame_is_the_pagelet_layout(self):
        html = self._page()
        assert 'class="plone-layout"' in html
        assert "visual-portal-wrapper" not in html

    def test_the_footer_renders_exactly_once(self):
        self.portal.footer = footer_value("layout words")
        html = self._page()
        assert html.count(ELEMENT) == 1
        assert html.count("layout words") == 1

    def test_it_renders_in_the_footer_landmark(self):
        self.portal.footer = footer_value("layout words")
        html = self._page()
        footer = html.index('id="portal-footer-wrapper"')
        assert footer < html.index(ELEMENT) < html.index("element-copyright")

    def test_the_viewlet_renders_inside_the_scope_root(self):
        self.portal.footer = footer_value("footer words")
        html = self._page()
        element = html[html.index(ELEMENT):]
        assert element.index("aurora-blocks-view") < element.index("footer words")

    def test_an_unauthored_footer_renders_no_element(self):
        assert "element-footerblocks" not in self._page()

    def test_the_footer_stays_off_its_editing_surface(self):
        self.portal.footer = footer_value("words being edited")
        self.request["ACTUAL_URL"] = f"{self.portal.absolute_url()}/@@edit-footer"
        assert "element-footerblocks" not in self._page(self.portal, "@@edit-footer")

    def test_the_footer_stays_off_the_blocks_canvas(self):
        self.portal.footer = footer_value("footer words")
        page = self.portal.somewhere
        self.request["ACTUAL_URL"] = f"{page.absolute_url()}/@@aurora-edit"
        html = self._page(page, "@@aurora-edit")
        assert "pat-auroraeditor" in html
        assert "element-footerblocks" not in html


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
