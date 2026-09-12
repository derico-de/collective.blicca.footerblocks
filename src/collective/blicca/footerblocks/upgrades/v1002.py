"""Place the footer element in the stock footer manager."""

import logging


logger = logging.getLogger(__name__)

PROFILE = "profile-collective.blicca.footerblocks.upgrades:1002"


def upgrade(context):
    """Give the footer-blocks viewlet its place in ``plone.portalfooter``.

    Upgrade from profile version 1001 to 1002. Only the ``viewlets`` step of
    the upgrade profile is run: it carries the one new order entry, and
    reloading the whole default profile would re-import the catalog and the
    layout order on top of whatever the site has made of them.
    """
    logger.info("Running upgrade step: Place the footer element in the stock footer manager")
    context.runImportStepFromProfile(PROFILE, "viewlets")
