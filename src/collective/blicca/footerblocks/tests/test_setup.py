"""Test collective.blicca.footerblocks installation."""

import pytest
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class TestSetup:
    """Test installation and setup."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]

    def test_addon_installed(self):
        """Test addon is installed."""
        installer = api.addon.get_installer(self.portal)
        assert installer.is_product_installed("collective.blicca.footerblocks")

    def test_browserlayer(self):
        """Test browserlayer is registered."""
        from plone.browserlayer import utils

        from collective.blicca.footerblocks.interfaces import ICollectiveBliccaFooterblocksLayer

        assert ICollectiveBliccaFooterblocksLayer in utils.registered_layers()

    def test_browserlayer_is_not_pageletlayouts(self):
        """Installing this add-on alone must not switch pageletlayout on."""
        from plone.pageletlayout.interfaces import IPlonePageletlayoutLayer

        from collective.blicca.footerblocks.interfaces import ICollectiveBliccaFooterblocksLayer

        assert not ICollectiveBliccaFooterblocksLayer.extends(IPlonePageletlayoutLayer)

    def test_pageletlayout_is_not_pulled_in(self):
        """Stock Plone works out of the box; pageletlayout is optional."""
        installer = api.addon.get_installer(self.portal)
        assert not installer.is_product_installed("plone.pageletlayout")

    def test_footer_behavior_available(self):
        """The dependency profile enabled the behavior on the site type."""
        from collective.volto.footer.behaviors.footer import IEditableFooterMarker

        assert IEditableFooterMarker.providedBy(self.portal)


class TestUninstall:
    """Test uninstallation."""

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer = api.addon.get_installer(self.portal)
        self.installer.uninstall_product("collective.blicca.footerblocks")

    def test_addon_uninstalled(self):
        """Test addon is uninstalled."""
        assert not self.installer.is_product_installed("collective.blicca.footerblocks")
