"""Setup handlers for collective.blicca.footerblocks."""

from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

from collective.blicca.footerblocks.multilingual import seed_language_footers_handler


@implementer(INonInstallable)
class HiddenProfiles:
    """Hidden profiles from the Plone add-ons control panel."""

    def getNonInstallableProfiles(self):
        """Return list of profiles that should not be available for install."""
        return [
            "collective.blicca.footerblocks:uninstall",
            "collective.blicca.footerblocks.upgrades:1001",
        ]


def post_multilingual_install(context):
    """Seed the language footers as part of applying the profile.

    The profile makes every language root folder a footer carrier, and the
    renderer stops at the nearest carrier: from the moment types.xml is in,
    a language folder without a footer of its own renders none rather than
    the site root's. Seeding here, in the same transaction, is what keeps
    the published footer from disappearing — there is no window between
    the two for a visitor to land in.

    Idempotent, so re-importing the profile is safe.
    """
    seed_language_footers_handler(context)


def uninstall(context):
    """Uninstall script."""
    # Do something on uninstall if needed
    pass
