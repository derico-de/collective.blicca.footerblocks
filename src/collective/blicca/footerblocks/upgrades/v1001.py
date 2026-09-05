"""Remove the footer edit object action."""
import logging

from .base import reload_gs_profile

logger = logging.getLogger(__name__)


def upgrade(context):
    """A custom upgrade step

    Upgrade from profile version 1000 to 1001.
    """
    logger.info("Running upgrade step: Remove the footer edit object action")
    reload_gs_profile(context)
