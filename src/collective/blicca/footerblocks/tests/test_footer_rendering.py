"""The footer blocks, rendered — frame-neutral (footer.py).

Inheritance, the authored-only rule, block add-on dispatch: everything both
frames share. Where the markup lands is test_footer_viewlet.py (stock) and
test_footer_pagelet.py (plone.pageletlayout).
"""

import pytest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_ID
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_TYPE
from plone.blicca.auroraeditor.interfaces import IPloneBliccaAuroraeditorLayer
from zope.interface import alsoProvides

from collective.blicca.footerblocks.footer import footer_blocks_html
from collective.blicca.footerblocks.interfaces import ICollectiveBliccaFooterblocksLayer


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


class TestRendering:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, ICollectiveBliccaFooterblocksLayer)
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Document", "somewhere", title="Somewhere")

    def _render(self, context):
        return footer_blocks_html(context, self.request)

    def test_footer_blocks_render(self):
        self.portal.footer = footer_value("footer words")
        assert "footer words" in self._render(self.portal.somewhere)

    def test_the_footer_is_inherited_from_the_site_root(self):
        """A page deep in the tree shows the nearest ancestor's footer."""
        self.portal.somewhere.invokeFactory("Document", "deeper")
        self.portal.footer = footer_value("inherited words")
        assert "inherited words" in self._render(self.portal.somewhere.deeper)

    def test_unauthored_footer_renders_nothing(self):
        """Dexterity serves the behavior schema's default (the slate "Edit"
        seed) for a never-set field; only the persisted value counts, so a
        never-authored footer contributes nothing at all — no invisible
        slate placeholders."""
        assert self._render(self.portal.somewhere) == ""

    def test_empty_footer_container_renders_nothing(self):
        self.portal.footer = {"blocks": {}, "blocks_layout": {"items": []}}
        assert self._render(self.portal.somewhere) == ""

    def test_the_footer_stays_out_of_its_own_editing_surface(self):
        self.portal.footer = footer_value("words being edited")
        self.request["ACTUAL_URL"] = f"{self.portal.absolute_url()}/@@edit-footer"
        assert self._render(self.portal) == ""

    def test_block_addon_nodes_dispatch_to_their_renderer(self):
        """ "Our blocks" work in the footer: a ``ploneBlock`` node inside the
        somersault tree dispatches to its ``aurora-block-<@type>`` view,
        exactly as in a page body."""
        from plone.blicca.auroraeditor.rendering import BaseBlockView
        from zope.component import getGlobalSiteManager
        from zope.interface import Interface

        class TestBlockView(BaseBlockView):
            def __call__(self):
                return '<div class="block-testblock">from the footer</div>'

        gsm = getGlobalSiteManager()
        gsm.registerAdapter(
            TestBlockView,
            (Interface, Interface),
            Interface,
            name="aurora-block-testblock",
        )
        try:
            self.portal.footer = {
                "blocks": {
                    SOMERSAULT_BLOCK_ID: {
                        "@type": SOMERSAULT_BLOCK_TYPE,
                        "value": [
                            {"type": "p", "children": [{"text": "before"}]},
                            {
                                "type": "ploneBlock",
                                "@type": "testblock",
                                "children": [{"text": ""}],
                            },
                        ],
                    }
                },
                "blocks_layout": {"items": [SOMERSAULT_BLOCK_ID]},
            }
            markup = self._render(self.portal.somewhere)
        finally:
            gsm.unregisterAdapter(
                TestBlockView,
                (Interface, Interface),
                Interface,
                name="aurora-block-testblock",
            )
        assert "block-testblock" in markup
        assert "from the footer" in markup
        assert "before" in markup

    def test_the_footer_is_rendered_once_per_request(self, monkeypatch):
        """Both frames ask on a pagelet page (the bridge updates the stock
        twin before dropping it); the pipeline must run once."""
        from collective.blicca.footerblocks import footer

        calls = []
        real = footer.render_blocks
        monkeypatch.setattr(
            footer, "render_blocks", lambda *args: calls.append(args) or real(*args)
        )
        self.portal.footer = footer_value("once")
        first = self._render(self.portal.somewhere)
        second = self._render(self.portal.somewhere)
        assert first == second
        assert "once" in first
        assert len(calls) == 1

    def test_a_changed_footer_is_not_served_from_the_memo(self):
        self.portal.footer = footer_value("first words")
        assert "first words" in self._render(self.portal.somewhere)
        self.portal.footer = footer_value("second words")
        assert "second words" in self._render(self.portal.somewhere)
