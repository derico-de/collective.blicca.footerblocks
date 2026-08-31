"""Pytest configuration for collective.blicca.footerblocks tests."""

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
