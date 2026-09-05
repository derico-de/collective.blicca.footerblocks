"""The Footer tab this package contributes to the Aurora edit-area strip."""

import pytest
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.blicca.auroraeditor.interfaces import IEditSurfaceTab
from plone.restapi.behaviors import IBlocks
from zope.component import getMultiAdapter
from zope.component import subscribers
from zope.interface import alsoProvides

from collective.blicca.footerblocks.interfaces import ICollectiveBliccaFooterblocksLayer
from collective.volto.footer.behaviors.footer import IEditableFooterMarker


class TestFooterTab:
    """The way into a footer whose carrier is an ancestor of this page."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, ICollectiveBliccaFooterblocksLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        self.doc = api.content.create(
            container=self.portal,
            type="Document",
            id="test-document",
            title="Test Document",
        )
        alsoProvides(self.doc, IBlocks)

    def _tab(self, context=None):
        found = [
            tab
            for tab in subscribers(
                (context or self.doc, self.request), IEditSurfaceTab
            )
            if tab.id == "footer"
        ]
        return found[0] if found else None

    def _tabs(self, context=None):
        view = getMultiAdapter(
            (context or self.doc, self.request), name="aurora-edit"
        )
        return view.edit_tabs()

    def test_the_tab_points_at_the_inherited_site_footer(self):
        tab = self._tab()
        assert tab.available is True
        assert tab.url == f"{self.portal.absolute_url()}/@@edit-footer"

    def test_it_comes_after_blocks_and_content(self):
        assert [tab["id"] for tab in self._tabs()] == [
            "blocks",
            "content",
            "footer",
        ]
        footer = self._tabs()[-1]
        assert footer["title"] == "Footer"
        assert footer["active"] is False

    def test_the_footer_surface_lights_its_own_tab(self):
        view = getMultiAdapter((self.portal, self.request), name="edit-footer")
        assert view.surface_id == "footer"
        assert [tab["id"] for tab in view.edit_tabs() if tab["active"]] == [
            "footer"
        ]

    def test_the_nearest_section_footer_wins(self):
        section = api.content.create(
            container=self.portal, type="Folder", id="section", title="Section"
        )
        alsoProvides(section, IEditableFooterMarker)
        page = api.content.create(
            container=section, type="Document", id="page", title="Page"
        )
        assert self._tab(page).url == f"{section.absolute_url()}/@@edit-footer"

    def test_it_is_withheld_without_permission_on_the_carrier(self):
        logout()
        tab = self._tab()
        assert tab.available is False
        assert "footer" not in [item["id"] for item in self._tabs()]
