"""Drop the footer element twin of the retired whole-body layout."""
import logging

from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from zope.component import getUtility


logger = logging.getLogger(__name__)

VIEWLET = "collective.blicca.footerblocks.footerblocks"
RETIRED_MANAGER = "plone.pageletlayout.layout"
SKIN = "Plone Default"


def upgrade(context):
    """Upgrade from profile version 1002 to 1003.

    plone.pageletlayout renders plone.portalfooter in its slot layout, where
    the stock viewlet already has its place, so the footer's entry in the
    retired whole-body manager's order is dead.
    """
    storage = getUtility(IViewletSettingsStorage)
    order = storage.getOrder(RETIRED_MANAGER, SKIN)
    if VIEWLET in order:
        storage.setOrder(RETIRED_MANAGER, SKIN, tuple(n for n in order if n != VIEWLET))
        logger.info("Dropped %s from %s", VIEWLET, RETIRED_MANAGER)
