"""Per-language footers: the opt-in profile and its seeding migration.

Without the profile a language root folder is not a footer carrier, so
``@@edit-footer`` is not registered there and the editor's Footer tab sends
authors to the site root — the bug this profile fixes. With it, each
language folder edits and renders its own footer, and the migration keeps
the published footer from disappearing on the way.

The multilingual setup happens inside the tests rather than in a layer of
its own: sibling PloneSandboxLayers share one storage stack under pytest,
so a second layer's LRF type would leak into every other test in the
package. The integration layer's per-test rollback contains it here.
"""

import pytest
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_ID
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_TYPE
from plone.blicca.auroraeditor.interfaces import IEditSurfaceTab
from plone.blicca.auroraeditor.interfaces import IPloneBliccaAuroraeditorLayer
from plone.restapi.behaviors import IBlocks
from zope.component import getMultiAdapter
from zope.component import subscribers
from zope.interface import alsoProvides

from collective.blicca.footerblocks.interfaces import ICollectiveBliccaFooterblocksLayer
from collective.blicca.footerblocks.multilingual import language_root_folders
from collective.blicca.footerblocks.multilingual import seed_language_footers
from collective.blicca.footerblocks.pagelets import FooterBlocksChromePagelet
from collective.volto.footer.behaviors.footer import IEditableFooterMarker


LANGUAGES = ("en", "de")


def make_multilingual(portal):
    """A two-language site: plone.app.multilingual creates /en and /de.

    Its install handler only builds the language root folders when more
    than one language is supported, so the second one is added first.
    """
    language_tool = api.portal.get_tool("portal_languages")
    for code in LANGUAGES:
        language_tool.addSupportedLanguage(code)
    applyProfile(portal, "plone.app.multilingual:default")


def footer_container(text):
    """A minimal authored footer: one somersault carrying one paragraph."""
    return {
        "blocks": {
            SOMERSAULT_BLOCK_ID: {
                "@type": SOMERSAULT_BLOCK_TYPE,
                "value": [{"type": "p", "children": [{"text": text}]}],
            }
        },
        "blocks_layout": {"items": [SOMERSAULT_BLOCK_ID]},
    }


class TestWithoutTheProfile:
    """The bug: a language folder is nobody's footer carrier."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, ICollectiveBliccaFooterblocksLayer)
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        make_multilingual(self.portal)
        self.folders = language_root_folders(self.portal)

    def test_the_site_has_language_root_folders(self):
        assert sorted(folder.getId() for folder in self.folders) == sorted(LANGUAGES)

    def test_the_language_folders_carry_no_footer(self):
        """collective.volto.footer marks the Plone Site type and nothing else."""
        assert IEditableFooterMarker.providedBy(self.portal)
        for folder in self.folders:
            assert not IEditableFooterMarker.providedBy(folder)

    def test_the_footer_tab_escapes_to_the_site_root(self):
        tab = self._footer_tab(self.folders[0])
        assert tab.url == f"{self.portal.absolute_url()}/@@edit-footer"

    def test_edit_footer_is_not_registered_on_a_language_folder(self):
        with pytest.raises(Exception):  # noqa: B017 - ComponentLookupError
            getMultiAdapter((self.folders[0], self.request), name="edit-footer")

    def _footer_tab(self, context):
        (tab,) = [
            tab
            for tab in subscribers((context, self.request), IEditSurfaceTab)
            if tab.id == "footer"
        ]
        return tab


class TestMultilingualProfile:
    """With the profile applied, every language root folder is a carrier."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, ICollectiveBliccaFooterblocksLayer)
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        make_multilingual(self.portal)
        applyProfile(self.portal, "collective.blicca.footerblocks:multilingual")
        self.folders = language_root_folders(self.portal)

    def test_the_behavior_is_on_the_lrf_type(self):
        fti = self.portal.portal_types["LRF"]
        assert "collective.volto.footer.editable" in fti.behaviors

    def test_the_other_lrf_behaviors_survive(self):
        """purge="false": the type keeps what plone.app.multilingual set."""
        fti = self.portal.portal_types["LRF"]
        assert "plone.navigationroot" in fti.behaviors
        assert "plone.translatable" in fti.behaviors

    def test_existing_language_folders_become_carriers(self):
        """No content migration: Dexterity reads markers off the FTI."""
        for folder in self.folders:
            assert IEditableFooterMarker.providedBy(folder)

    def test_edit_footer_is_available_on_a_language_folder(self):
        for folder in self.folders:
            view = getMultiAdapter((folder, self.request), name="edit-footer")
            view()
            assert view.field_name == "footer"
            assert view.config()["contentUrl"] == (
                f"{folder.absolute_url()}/@footerblocks"
            )

    def test_the_save_target_redirect_is_available_too(self):
        folder = self.folders[0]
        getMultiAdapter((folder, self.request), name="@footerblocks")()
        assert self.request.response.getHeader("Location") == folder.absolute_url()

    def test_the_footer_tab_of_a_page_points_at_its_language_folder(self):
        folder = self.folders[0]
        page = api.content.create(
            container=folder, type="Document", id="page", title="Page"
        )
        alsoProvides(page, IBlocks)
        (tab,) = [
            tab
            for tab in subscribers((page, self.request), IEditSurfaceTab)
            if tab.id == "footer"
        ]
        assert tab.available is True
        assert tab.url == f"{folder.absolute_url()}/@@edit-footer"

    def test_each_language_renders_its_own_footer(self):
        first, *rest = self.folders
        self.portal.footer = footer_container("Site footer")
        first.footer = footer_container("Language footer")

        assert "Language footer" in self._rendered(first)
        for folder in rest:
            # Nearest carrier wins and does not fall through: an unauthored
            # language folder shows nothing, not the site footer.
            assert self._rendered(folder) == ""

    def _rendered(self, context):
        pagelet = FooterBlocksChromePagelet(context, self.request)
        pagelet.update()
        return pagelet.blocks_html


class TestSeedLanguageFooters:
    """The migration that keeps the published footer from vanishing."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        make_multilingual(self.portal)
        applyProfile(self.portal, "collective.blicca.footerblocks:multilingual")
        self.folders = language_root_folders(self.portal)

    def test_it_copies_the_inherited_footer_into_every_language(self):
        self.portal.footer = footer_container("Site footer")

        seeded = seed_language_footers(self.portal)

        assert len(seeded) == len(self.folders)
        for folder in self.folders:
            assert folder.footer == self.portal.footer

    def test_the_copy_is_independent_of_the_site_footer(self):
        self.portal.footer = footer_container("Site footer")
        seed_language_footers(self.portal)

        self.folders[0].footer["blocks"][SOMERSAULT_BLOCK_ID]["value"] = [
            {"type": "p", "children": [{"text": "Edited"}]}
        ]

        site_value = self.portal.footer["blocks"][SOMERSAULT_BLOCK_ID]["value"]
        assert site_value == [{"type": "p", "children": [{"text": "Site footer"}]}]

    def test_an_authored_language_footer_is_left_alone(self):
        self.portal.footer = footer_container("Site footer")
        folder = self.folders[0]
        folder.footer = footer_container("Already authored")

        seeded = seed_language_footers(self.portal)

        assert "/".join(folder.getPhysicalPath()) not in seeded
        value = folder.footer["blocks"][SOMERSAULT_BLOCK_ID]["value"]
        assert value == [{"type": "p", "children": [{"text": "Already authored"}]}]

    def test_running_it_twice_changes_nothing(self):
        self.portal.footer = footer_container("Site footer")
        seed_language_footers(self.portal)

        assert seed_language_footers(self.portal) == []

    def test_an_unauthored_site_seeds_nothing(self):
        """The behavior's slate "Edit" seed is not a footer to copy."""
        assert seed_language_footers(self.portal) == []
        for folder in self.folders:
            assert "footer" not in vars(folder)
