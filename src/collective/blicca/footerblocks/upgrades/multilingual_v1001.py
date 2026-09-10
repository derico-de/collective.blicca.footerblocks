"""Seed the per-language footers (``multilingual`` profile, 1000 -> 1001)."""
import logging

from collective.blicca.footerblocks.multilingual import seed_language_footers_handler


logger = logging.getLogger(__name__)


def upgrade(context):
    """Give every unauthored language root folder the footer it inherited.

    Profile version 1000 imported ``types/LRF.xml`` and stopped there, so a
    site that applied it has language folders that carry the editable-footer
    behavior but have no footer of their own — and the renderer stops at the
    nearest carrier, so those languages publish no footer at all. 1001 seeds
    them from the profile's ``post_handler``; this step does the same for a
    site that is already past that point.

    No import step to run: nothing in ``profiles/multilingual/`` changed.
    Idempotent — a language folder that has been authored, or seeded by hand
    before this step existed, is left alone.
    """
    logger.info("Running upgrade step: Seed the per-language footers")
    seeded = seed_language_footers_handler(context)
    logger.info("Seeded %s language footer(s).", len(seeded))
    return seeded
