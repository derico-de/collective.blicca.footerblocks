"""Upgrade 1001 -> 1002: the footer viewlet gets its stock-frame place.

A site at 1001 has the layout-manager order entry and nothing for
``plone.portalfooter``; on stock Plone its footer would render at the very
end of the manager, after the footer portlets. The step imports the one
new order entry and nothing else.
"""

import pytest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from zope.component import getUtility

from collective.blicca.footerblocks.tests.test_upgrade_step_1001 import hidden_profiles
from collective.blicca.footerblocks.upgrades.v1002 import upgrade


VIEWLET = "collective.blicca.footerblocks.footerblocks"
STOCK = "plone.portalfooter"
LAYOUT = "plone.pageletlayout.layout"
SKIN = "Plone Default"
PROFILE = "collective.blicca.footerblocks.upgrades:1002"


class TestUpgrade1002:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        self.storage = getUtility(IViewletSettingsStorage)

    def _order(self, manager):
        return list(self.storage.getOrder(manager, SKIN))

    def _downgrade(self):
        """Put the site into the 1001 state: no stock-footer entry."""
        order = [name for name in self._order(STOCK) if name != VIEWLET]
        self.storage.setOrder(STOCK, SKIN, tuple(order))
        assert VIEWLET not in self._order(STOCK)

    def test_upgrade_step_registered(self):
        steps = self.setup_tool.listUpgrades(
            "collective.blicca.footerblocks:default", show_old=True
        )
        flat = []
        for step in steps:
            flat.extend(step if isinstance(step, list) else [step])
        assert any(step["ssource"] == "1001" and step["sdest"] == "1002" for step in flat)

    def test_upgrade_profile_is_hidden(self):
        assert PROFILE in hidden_profiles()

    def test_upgrade_places_the_viewlet_before_the_footer_portlets(self):
        self._downgrade()
        upgrade(self.setup_tool)
        order = self._order(STOCK)
        assert order.index(VIEWLET) < order.index("plone.footer")

    def test_upgrade_is_idempotent(self):
        before = self._order(STOCK)
        upgrade(self.setup_tool)
        assert self._order(STOCK) == before

    def test_the_layout_order_is_left_alone(self):
        before = self._order(LAYOUT)
        upgrade(self.setup_tool)
        assert self._order(LAYOUT) == before

    def test_a_fresh_install_is_already_at_this_version(self):
        (version,) = self.setup_tool.getLastVersionForProfile(
            "collective.blicca.footerblocks:default"
        )
        assert int(version) == 1002
