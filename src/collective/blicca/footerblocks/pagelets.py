"""The footer-blocks chrome pagelet, and the stylesheet plumbing it needs.

The footer's *content* is editable blocks, stored the way the Volto
ecosystem stores an editable footer: ``collective.volto.footer``'s
``footer`` JSONField (behavior ``collective.volto.footer.editable``,
enabled on the Plone Site type by that add-on's profile). Volto frontends
read the field through plone.restapi's ``@inherit`` expander — the nearest
ancestor carrying the behavior wins, so a language folder or subsite can
override the site-wide footer by enabling the behavior on its type.
:class:`FooterBlocksChromePagelet` is the Blicca half: the same
nearest-ancestor lookup, walked directly over the acquisition chain, and
the blocks rendered server-side through the promised
:func:`~plone.blicca.auroraeditor.rendering.render_blocks` pipeline.

The footer's *place* is a chrome pagelet in the whole-body layout, inserted
before the plone.pageletlayout footer rows (profiles/default/viewlets.xml) —
the way a theme adds a new element to Clara's page tail. plonetheme.derico's
hard-coded contact band was the precedent, and is the thing this replaces:
the same closing call to action, authored rather than compiled in.
"""

from Acquisition import aq_base
from Acquisition import aq_chain
from Acquisition import aq_inner
from plone.blicca.auroraeditor.rendering import blocks_css_urls
from plone.blicca.auroraeditor.rendering import render_blocks
from plone.pageletlayout.chrome import ChromePagelet
from plone.pageletlayout.pagelets.head import StylesChromePagelet

from collective.volto.footer.behaviors.footer import IEditableFooterMarker


def footer_carrier(context):
    """Return the nearest ancestor that owns an editable footer."""
    for obj in aq_chain(aq_inner(context)):
        if IEditableFooterMarker.providedBy(obj):
            return obj
    return None


def authored_footer(carrier):
    """The persisted footer value of ``carrier``, or ``{}``.

    Never the schema default: Dexterity serves ``collective.volto.footer``'s
    slate "Edit" seed for a never-set field, so ``getattr`` alone cannot tell
    an authored footer from the seed; the instance dict can.

    Nearest-marker semantics stay mirrored to ``@inherit``: an ancestor
    carrying the behavior but never authored yields an empty footer, it does
    not fall through to a grandparent Volto would never consult.
    """
    if carrier is None:
        return {}
    return vars(aq_base(carrier)).get("footer") or {}


class FooterBlocksChromePagelet(ChromePagelet):
    """Render the inherited footer blocks at the tail of every page.

    The template wraps the markup in ``.aurora-blocks-view`` — the public
    scope root of the shared blocks stylesheet and of every block add-on's
    ``@scope``-wrapped CSS (block add-on contract §6.1), so footer blocks
    are styled by exactly the sheets that style them in a page body.

    The footer is an **Aurora (Plate) container**: a somersault block whose
    tree carries the text plus any registered block add-on's ``ploneBlock``
    nodes, all dispatched by the same pipeline that renders a page body.
    Volto ``slate`` blocks are not supported — there is no
    ``aurora-block-slate`` renderer, deliberately.

    Only a footer that was actually **authored** renders. Dexterity serves
    the behavior schema's *default* (``collective.volto.footer``'s slate
    "Edit" seed) for a never-set field, so ``getattr`` alone cannot tell an
    authored footer from the seed; the instance dict can. No footer up the
    chain, a never-authored one, or an empty container renders nothing:
    the element disappears rather than shipping an empty band.
    """

    def update(self):
        self.blocks_html = ""
        if self._is_footer_editor():
            return

        carrier = self._carrier()
        footer = authored_footer(carrier)
        if carrier is not None and footer.get("blocks"):
            self.blocks_html = render_blocks(
                carrier,
                self.request,
                footer.get("blocks"),
                footer.get("blocks_layout"),
            )

    def _is_footer_editor(self):
        """Keep the published footer out of its own editing surface."""
        for key in ("ACTUAL_URL", "URL"):
            url = self.request.get(key, "")
            if url.rstrip("/").endswith("/@@edit-footer"):
                return True
        return False

    def _carrier(self):
        """The nearest ancestor carrying the editable-footer behavior."""
        return footer_carrier(self.context)


class FooterStylesChromePagelet(StylesChromePagelet):
    """The head styles provider, plus the blocks stylesheets.

    ``blocks_view.pt`` emits the shared blocks CSS and the block add-ons'
    CSS in its head slot — on blocks pages only. The footer renders blocks
    on *every* page, so this override appends the same links (same busted
    URLs, same order, contract §6.3) after the resource-registry output.
    On a blocks page the links then appear twice; the URLs are identical,
    so the browser fetches once and the idempotent rules apply once
    effectively.
    """

    def render(self):
        links = "".join(
            f'<link rel="stylesheet" href="{url}" />' for url in blocks_css_urls(self.context)
        )
        return super().render() + links
