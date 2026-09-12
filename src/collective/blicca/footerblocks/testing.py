"""Testing setup for collective.blicca.footerblocks.

Mirrors the collective.fragmentsblock fixture: plone.volto's ZCML is loaded
(the volto.* metadata behaviors and serializer utilities, as z3c.autoinclude
would in a real site) but its GS profile is never applied. The add-on's own
profile pulls its metadata.xml dependencies — collective.volto.footer (the
footer behavior on the Plone Site type) and plone.blicca.auroraeditor (the
block rendering pipeline).

The fixture site is the **stock** frame: plone.pageletlayout's ZCML is
loaded (importable, so the conditional registrations exist — the production
shape of "installed in the instance, not on this site") but its profile is
not applied, and Barceloneta's main_template renders. The pageletlayout
frame is not a second sandbox layer: pytest-plone keeps every layer set up
for the whole session, and plone.testing's resource stacks then resolve a
base layer's ``zodbDB`` to the *last* sandbox stacked on it — a second
PloneSandboxLayer, sibling or child, leaks its profiles into every test.
``tests/conftest.py`` applies ``plone.pageletlayout:default`` inside the
test transaction instead (``pageletlayout_integration``), the way the
per-language tests apply theirs.

plone.app.multilingual is loaded the same way — ZCML only. Two sibling
PloneSandboxLayers do not isolate from each other under pytest, so the
per-language footer tests apply its profile (and this package's opt-in
``multilingual`` one) inside the test, where the integration layer's
transaction rollback contains them.
"""

import os

import plone.app.multilingual
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
        self.loadZCML(name="testing.zcml", package=plone.app.multilingual)
        self.loadZCML(package=plone.pageletlayout)
        self.loadZCML(package=plone.blicca.auroraeditor)
        self.loadZCML(package=collective.volto.footer)
        self.loadZCML(package=collective.blicca.footerblocks)
        # Plone loads plugin overrides.zcml through plone.autoinclude; the
        # sandbox loads it as a plain file after the base, the way
        # plone.app.testing's own fixture loads Plone's overrides (each
        # loadZCML executes its actions at once, so a later registration
        # replaces an earlier one and there is no conflict to resolve).
        # That the file is a real override — same discriminator as the base
        # stanza — is pinned separately, in tests/test_overrides.py.
        self.loadZCML(name="overrides.zcml", package=collective.blicca.footerblocks)

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
