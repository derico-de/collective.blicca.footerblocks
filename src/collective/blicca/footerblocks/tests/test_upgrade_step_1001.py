"""Upgrade 1000 -> 1001: the footer edit object action goes away.

The action's ``available_expr`` traversed ``@@footer-edit-action``, a view
this package no longer registers, so a site that imported it raises
AttributeError on every page that renders Plone's toolbar. Sites that never
had the action must be left alone.
"""

import pytest
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFCore.ActionInformation import Action

from collective.blicca.footerblocks.upgrades.v1001 import upgrade


ACTION = "footer_edit"
PROFILE = "collective.blicca.footerblocks.upgrades:1001"


def hidden_profiles():
    """Every profile the add-ons panel is told to hide.

    Read from the utility registry rather than from `HiddenProfiles()`: the
    panel and `GET /@addons` only ever see the class through the
    `INonInstallable` utility registered in configure.zcml, so a test that
    instantiates it passes with no registration at all — which is how these
    profiles came to be offered as installable add-ons in the first place.
    """
    from plone.base.interfaces import INonInstallable
    from zope.component import getAllUtilitiesRegisteredFor

    return [
        name
        for utility in getAllUtilitiesRegisteredFor(INonInstallable)
        for name in getattr(utility, "getNonInstallableProfiles", list)()
    ]


class TestUpgrade1001:

    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.setup_tool = self.portal.portal_setup
        self.category = self.portal.portal_actions.object

    def _readd_action(self):
        """Put a site back into the state this upgrade has to repair."""
        action = Action(
            ACTION,
            title="Edit footer",
            url_expr=(
                "python:object.restrictedTraverse('@@footer-edit-action')()"
            ),
            available_expr=(
                "python:object is not None and "
                "bool(object.restrictedTraverse('@@footer-edit-action')())"
            ),
            permissions=("View",),
            visible=True,
        )
        self.category._setObject(ACTION, action)
        assert ACTION in self.category.objectIds()

    def test_upgrade_step_registered(self):
        steps = self.setup_tool.listUpgrades(
            "collective.blicca.footerblocks:default", show_old=True
        )
        flat = []
        for step in steps:
            flat.extend(step if isinstance(step, list) else [step])
        assert any(
            step["ssource"] == "1000" and step["sdest"] == "1001"
            for step in flat
        )

    def test_upgrade_profile_is_hidden(self):
        assert PROFILE in hidden_profiles()

    def test_upgrade_removes_the_action(self):
        self._readd_action()
        upgrade(self.setup_tool)
        assert ACTION not in self.category.objectIds()

    def test_a_site_that_never_had_the_action_is_untouched(self):
        before = self.category.objectIds()
        upgrade(self.setup_tool)
        assert self.category.objectIds() == before

    def test_the_other_object_actions_survive(self):
        """The step imports `actions` from a profile carrying one removal —
        it must not take the metadata action, or any of Plone's, with it."""
        self._readd_action()
        others = [i for i in self.category.objectIds() if i != ACTION]
        upgrade(self.setup_tool)
        assert self.category.objectIds() == others
