"""Testing setup for collective.blicca.footerblocks.

Mirrors the collective.fragmentsblock fixture: plone.volto's ZCML is loaded
(the volto.* metadata behaviors and serializer utilities, as z3c.autoinclude
would in a real site) but its GS profile is never applied. The add-on's own
profile pulls its metadata.xml dependencies — collective.volto.footer (the
footer behavior on the Plone Site type), plone.pageletlayout (the frame) and
plone.blicca.auroraeditor (the block rendering pipeline).
"""

import os

import plone.blicca.auroraeditor
import plone.pageletlayout
import plone.restapi
import plone.volto
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.zope import WSGI_SERVER_FIXTURE

import collective.blicca.footerblocks
import collective.volto.footer


class CollectiveBliccaFooterblocksLayer(PloneSandboxLayer):
    """Custom testing layer for collective.blicca.footerblocks."""

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Compile .po -> .mo so add-on translations load during tests.
        os.environ.setdefault("zope_i18n_compile_mo_files", "true")
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=plone.volto)
        self.loadZCML(package=plone.pageletlayout)
        self.loadZCML(package=plone.blicca.auroraeditor)
        self.loadZCML(package=collective.volto.footer)
        self.loadZCML(package=collective.blicca.footerblocks)

    def setUpPloneSite(self, portal):
        """Set up Plone site."""
        self.applyProfile(portal, "plone.restapi:default")
        self.applyProfile(portal, "collective.blicca.footerblocks:default")


FIXTURE = CollectiveBliccaFooterblocksLayer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="CollectiveBliccaFooterblocksLayer:IntegrationTesting",
)

FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name="CollectiveBliccaFooterblocksLayer:FunctionalTesting",
)

ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="CollectiveBliccaFooterblocksLayer:AcceptanceTesting",
)


# Test credentials
TEST_USER_ID = "testuser"
TEST_USER_NAME = "testuser"
SITE_OWNER_NAME = SITE_OWNER_NAME
SITE_OWNER_PASSWORD = SITE_OWNER_PASSWORD
