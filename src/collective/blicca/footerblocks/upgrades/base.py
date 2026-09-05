"""Shared upgrade step utilities for collective.blicca.footerblocks."""
from plone.app.upgrade.utils import loadMigrationProfile


def reload_gs_profile(context):
    """Reload the default GenericSetup profile."""
    loadMigrationProfile(context, "profile-collective.blicca.footerblocks:default")
