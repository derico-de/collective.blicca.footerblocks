"""Per-language footers: the migration that goes with the profile.

The ``multilingual`` GenericSetup profile puts the editable-footer behavior
on plone.app.multilingual's ``LRF`` type, which is all it takes for
``@@edit-footer`` and the editor's **Footer** tab to work on ``/de`` and
``/en``: a Dexterity object provides its behaviors' marker interfaces the
moment the FTI names them, so the existing language folders become carriers
without being touched.

What the profile cannot do on its own is keep the published site looking the
same. Renderer and tab both stop at the *nearest* carrier — Volto's
``@inherit`` semantics, deliberately mirrored — so a language folder that
carries the behavior but has never had its footer authored shows no footer
at all, rather than falling back to the site root's. Turning the profile on
therefore blanks the footer under every language until each one is authored.

:func:`seed_language_footers` is the one-shot answer: copy the footer those
pages were already showing into each language folder, so nothing disappears
and every language starts from the same content, independently editable
from there. It is a migration, not part of the profile — a site that wants
its languages to start empty just does not run it.
"""

import logging
from copy import deepcopy

from Acquisition import aq_inner
from Acquisition import aq_parent
from zope.lifecycleevent import modified

from collective.blicca.footerblocks.pagelets import authored_footer
from collective.blicca.footerblocks.pagelets import footer_carrier
from collective.volto.footer.behaviors.footer import IEditableFooterMarker


logger = logging.getLogger(__name__)

LANGUAGE_ROOT_TYPE = "LRF"


def language_root_folders(portal):
    """The site's language root folders, in the order they were created."""
    return [
        obj
        for obj in portal.objectValues()
        if getattr(obj, "portal_type", None) == LANGUAGE_ROOT_TYPE
    ]


def seed_language_footers(portal):
    """Give every unauthored language folder the footer it used to inherit.

    For each language root folder that carries the behavior but has no
    authored footer of its own, copy the footer of the nearest carrier
    *above* it — the site root, in a normal setup. Idempotent: a language
    folder that already has a footer is left alone, and so is one whose
    ancestors have nothing authored to copy.

    Returns the paths of the folders that were seeded.
    """
    seeded = []
    for folder in language_root_folders(portal):
        if not IEditableFooterMarker.providedBy(folder):
            logger.info(
                "%s does not carry the editable-footer behavior; apply the "
                "collective.blicca.footerblocks:multilingual profile first.",
                "/".join(folder.getPhysicalPath()),
            )
            continue
        if authored_footer(folder).get("blocks"):
            continue

        inherited = authored_footer(footer_carrier(aq_parent(aq_inner(folder))))
        if not inherited.get("blocks"):
            continue

        folder.footer = deepcopy(inherited)
        modified(folder)
        path = "/".join(folder.getPhysicalPath())
        seeded.append(path)
        logger.info("Seeded the footer of %s from the inherited one.", path)

    return seeded
