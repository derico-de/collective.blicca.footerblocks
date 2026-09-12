"""Pytest configuration for collective.blicca.footerblocks tests."""

import pytest
from plone.app.testing import applyProfile
from pytest_plone import fixtures_factory

from collective.blicca.footerblocks.testing import ACCEPTANCE_TESTING
from collective.blicca.footerblocks.testing import FUNCTIONAL_TESTING
from collective.blicca.footerblocks.testing import INTEGRATION_TESTING


globals().update(
    fixtures_factory((
        (INTEGRATION_TESTING, "integration"),
        (FUNCTIONAL_TESTING, "functional"),
        (ACCEPTANCE_TESTING, "acceptance"),
    ))
)


@pytest.fixture
def pageletlayout_integration(integration):
    """The stock site with plone.pageletlayout installed, per test.

    Inside the integration transaction, which the layer rolls back — see
    testing.py for why this is not a second sandbox layer. pageletlayout's
    profile restates the layout order, which pushes every foreign element
    to the front, so this add-on's ``viewlets`` step runs again afterwards:
    the repair pageletlayout documents for exactly that order of
    installation.
    """
    portal = integration["portal"]
    applyProfile(portal, "plone.pageletlayout:default")
    portal.portal_setup.runImportStepFromProfile(
        "profile-collective.blicca.footerblocks:default", "viewlets"
    )
    return integration
