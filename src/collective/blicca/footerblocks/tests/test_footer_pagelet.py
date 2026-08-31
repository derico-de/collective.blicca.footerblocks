"""The footer-blocks element: placement, inheritance, markup, stylesheets."""

import pytest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_ID
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_TYPE
from plone.blicca.auroraeditor.interfaces import IPloneBliccaAuroraeditorLayer
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import alsoProvides

from collective.blicca.footerblocks.interfaces import ICollectiveBliccaFooterblocksLayer
from collective.blicca.footerblocks.pagelets import FooterBlocksChromePagelet


VIEWLET = "collective.blicca.footerblocks.footerblocks"
MANAGER = "plone.pageletlayout.layout"


def footer_value(text):
    """A footer container the way Aurora saves one: a somersault block."""
    return {
        "blocks": {
            SOMERSAULT_BLOCK_ID: {
                "@type": SOMERSAULT_BLOCK_TYPE,
                "value": [{"type": "p", "children": [{"text": text}]}],
            }
        },
        "blocks_layout": {"items": [SOMERSAULT_BLOCK_ID]},
    }


class TestPlacement:
    """The stored layout order, not the registration."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
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


class RenderingBase:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, ICollectiveBliccaFooterblocksLayer)
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Document", "somewhere", title="Somewhere")

    def _render(self, context):
        pagelet = FooterBlocksChromePagelet(context, self.request)
        pagelet.update()
        return pagelet.render()


class TestRendering(RenderingBase):
    def test_it_is_registered_under_the_name_the_layout_asks_for(self):
        self.portal.footer = footer_value("registered words")
        view = self.portal.restrictedTraverse("@@plone")
        pagelet = getMultiAdapter(
            (self.portal.somewhere, self.request, view),
            IContentProvider,
            name=VIEWLET,
        )
        pagelet.update()
        assert "element-footerblocks" in pagelet.render()

    def test_footer_blocks_render_inside_the_scope_root(self):
        self.portal.footer = footer_value("footer words")
        markup = self._render(self.portal.somewhere)
        assert "element-footerblocks" in markup
        assert "aurora-blocks-view" in markup
        assert "footer words" in markup

    def test_the_footer_is_inherited_from_the_site_root(self):
        """A page deep in the tree shows the nearest ancestor's footer."""
        self.portal.somewhere.invokeFactory("Document", "deeper")
        self.portal.footer = footer_value("inherited words")
        assert "inherited words" in self._render(self.portal.somewhere.deeper)

    def test_unauthored_footer_renders_only_invisible_placeholders(self):
        """A never-authored site serves the behavior's default seed — the
        same value ``@inherit`` hands a Volto frontend. Its ``slate`` block
        has no aurora renderer, so it dispatches to the invisible
        ``block-unrendered`` placeholder: nothing visible, by design."""
        markup = self._render(self.portal.somewhere)
        assert "block-unrendered" in markup
        assert 'data-block-type="slate"' in markup

    def test_empty_footer_container_renders_nothing(self):
        self.portal.footer = {"blocks": {}, "blocks_layout": {"items": []}}
        assert self._render(self.portal.somewhere).strip() == ""


class TestStyles(RenderingBase):
    """The overridden styles provider ships the blocks stylesheets."""

    def test_every_page_head_gets_the_blocks_css(self):
        view = self.portal.restrictedTraverse("@@plone")
        provider = getMultiAdapter(
            (self.portal.somewhere, self.request, view),
            IContentProvider,
            name="plone.pageletlayout.styles",
        )
        provider.update()
        markup = provider.render()
        assert "++resource++plone.blicca.auroraeditor.blocks.css" in markup
