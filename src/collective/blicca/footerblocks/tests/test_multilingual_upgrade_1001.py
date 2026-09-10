"""Upgrade 1000 -> 1001 of the ``multilingual`` profile: seed the footers.

Version 1000 of the profile imported ``types/LRF.xml`` and nothing else, so
a site that applied it has language root folders carrying the
editable-footer behavior with no footer of their own — and since the
renderer stops at the nearest carrier, those languages publish no footer at
all. 1001 seeds them from the profile's post_handler; this step repairs a
site that is already past that point.
"""

import pytest
from plone import api
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_ID
from zope.interface import alsoProvides

from collective.blicca.footerblocks.interfaces import ICollectiveBliccaFooterblocksLayer
from collective.blicca.footerblocks.multilingual import language_root_folders
from collective.blicca.footerblocks.pagelets import FooterBlocksChromePagelet
from collective.blicca.footerblocks.tests.test_multilingual import footer_container
from collective.blicca.footerblocks.tests.test_multilingual import make_multilingual
from collective.blicca.footerblocks.upgrades.multilingual_v1001 import upgrade


PROFILE = "collective.blicca.footerblocks:multilingual"


class TestMultilingualUpgrade1001:

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, ICollectiveBliccaFooterblocksLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)
        self.setup_tool = self.portal.portal_setup
        make_multilingual(self.portal)
        self.portal.footer = footer_container("Site footer")
        applyProfile(self.portal, PROFILE)
        self.folders = language_root_folders(self.portal)

    def _rewind_to_1000(self):
        """Put a site back into the state this upgrade has to repair.

        What 1000 left behind: the behavior on the type, no footer on any
        language folder.
        """
        for folder in self.folders:
            if "footer" in vars(folder):
                del folder.footer
        self.setup_tool.setLastVersionForProfile(PROFILE, ("1000",))

    def test_the_upgrade_step_is_registered_on_the_multilingual_profile(self):
        steps = self.setup_tool.listUpgrades(PROFILE, show_old=True)
        flat = []
        for step in steps:
            flat.extend(step if isinstance(step, list) else [step])
        assert any(
            step["ssource"] == "1000" and step["sdest"] == "1001" for step in flat
        )

    def test_a_fresh_apply_is_already_at_this_version(self):
        (version,) = self.setup_tool.getLastVersionForProfile(PROFILE)
        assert int(version) == 1001

    def test_a_site_left_at_1000_has_the_upgrade_pending(self):
        self._rewind_to_1000()
        assert self.setup_tool.listUpgrades(PROFILE)

    def test_it_seeds_the_language_folders_that_1000_left_empty(self):
        self._rewind_to_1000()

        seeded = upgrade(self.setup_tool)

        assert len(seeded) == len(self.folders)
        for folder in self.folders:
            assert folder.footer == self.portal.footer

    def test_the_published_footer_comes_back(self):
        self._rewind_to_1000()
        page = api.content.create(
            container=self.folders[0], type="Document", id="page", title="Page"
        )
        assert self._rendered(page) == ""

        upgrade(self.setup_tool)

        assert "Site footer" in self._rendered(page)

    def test_it_leaves_an_authored_language_footer_alone(self):
        self._rewind_to_1000()
        folder = self.folders[0]
        folder.footer = footer_container("Authored by hand")

        upgrade(self.setup_tool)

        value = folder.footer["blocks"][SOMERSAULT_BLOCK_ID]["value"]
        assert value == [{"type": "p", "children": [{"text": "Authored by hand"}]}]

    def test_running_it_on_an_already_seeded_site_changes_nothing(self):
        """The sandbox case: seeded by hand before the step existed."""
        assert upgrade(self.setup_tool) == []

    def _rendered(self, context):
        pagelet = FooterBlocksChromePagelet(context, self.request)
        pagelet.update()
        return pagelet.blocks_html
