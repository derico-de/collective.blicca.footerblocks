"""Remove the footer edit object action."""
import logging


logger = logging.getLogger(__name__)

PROFILE = "profile-collective.blicca.footerblocks.upgrades:1001"


def upgrade(context):
    """Drop the object action the editor's Footer tab replaced.

    Upgrade from profile version 1000 to 1001. Only the ``actions`` step of
    the upgrade profile is run: nothing else about an installed site
    changed, and reloading the whole default profile would re-import the
    viewlet order and the catalog on top of whatever the site has made of
    them.
    """
    logger.info("Running upgrade step: Remove the footer edit object action")
    context.runImportStepFromProfile(PROFILE, "actions")
