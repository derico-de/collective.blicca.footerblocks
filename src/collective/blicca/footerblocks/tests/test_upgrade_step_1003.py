"""Tests for upgrade step 1002 -> 1003: the retired layout entry, dropped."""

import pytest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from zope.component import getUtility

from collective.blicca.footerblocks.setuphandlers import HiddenProfiles
from collective.blicca.footerblocks.upgrades.v1003 import upgrade


VIEWLET = "collective.blicca.footerblocks.footerblocks"
RETIRED = "plone.pageletlayout.layout"
SKIN = "Plone Default"


class TestUpgrade1003:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        self.storage = getUtility(IViewletSettingsStorage)

    def test_the_retired_entry_is_dropped(self):
        self.storage.setOrder(RETIRED, SKIN, ("plone.pageletlayout.body", VIEWLET))
        upgrade(self.setup_tool)
        assert self.storage.getOrder(RETIRED, SKIN) == ("plone.pageletlayout.body",)

    def test_the_stock_footer_order_is_left_alone(self):
        before = self.storage.getOrder("plone.portalfooter", SKIN)
        upgrade(self.setup_tool)
        assert self.storage.getOrder("plone.portalfooter", SKIN) == before

    def test_a_site_without_the_entry_is_fine(self):
        upgrade(self.setup_tool)
        assert VIEWLET not in self.storage.getOrder(RETIRED, SKIN)

    def test_a_fresh_install_is_already_at_this_version(self):
        (version,) = self.setup_tool.getLastVersionForProfile(
            "collective.blicca.footerblocks:default"
        )
        assert int(version) == 1003

    def test_no_upgrade_profile_is_offered(self):
        assert not any("1003" in p for p in HiddenProfiles().getNonInstallableProfiles())
