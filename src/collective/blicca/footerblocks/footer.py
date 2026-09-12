"""The footer blocks, rendered: frame-neutral, shared by both frames.

The footer's *content* is editable blocks, stored the way the Volto
ecosystem stores an editable footer: ``collective.volto.footer``'s
``footer`` JSONField (behavior ``collective.volto.footer.editable``,
enabled on the Plone Site type by that add-on's profile). Volto frontends
read the field through plone.restapi's ``@inherit`` expander — the nearest
ancestor carrying the behavior wins, so a language folder or subsite can
override the site-wide footer by enabling the behavior on its type.
:func:`footer_blocks_html` is the Blicca half: the same nearest-ancestor
lookup, walked directly over the acquisition chain, and the blocks rendered
server-side through the promised
:func:`~plone.blicca.auroraeditor.rendering.render_blocks` pipeline.

Where that markup *lands* is a frame question, and this module does not
know the answer: the stock viewlet (viewlets.py, ``IPortalFooter``) and the
plone.pageletlayout element (pagelets.py, ``ILayoutManager``) both call
:func:`footer_blocks_html` and hand the result to the one shared template.

The footer is an **Aurora (Plate) container**: a somersault block whose
tree carries the text plus any registered block add-on's ``ploneBlock``
nodes, all dispatched by the same pipeline that renders a page body. Volto
``slate`` blocks are not supported — there is no ``aurora-block-slate``
renderer, deliberately.

Only a footer that was actually **authored** renders. Dexterity serves the
behavior schema's *default* (``collective.volto.footer``'s slate "Edit"
seed) for a never-set field, so ``getattr`` alone cannot tell an authored
footer from the seed; the instance dict can. No footer up the chain, a
never-authored one, or an empty container renders nothing: the element
disappears rather than shipping an empty band.
"""

from Acquisition import aq_base
from Acquisition import aq_chain
from Acquisition import aq_inner
from plone.blicca.auroraeditor.rendering import render_blocks

from collective.volto.footer.behaviors.footer import IEditableFooterMarker


#: The view name of the footer's own editing surface (editing.py).
EDIT_SURFACE = "@@edit-footer"


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


def is_footer_editor(request):
    """Whether ``request`` is the footer's own editing surface."""
    for key in ("ACTUAL_URL", "URL"):
        url = request.get(key, "")
        if url.rstrip("/").endswith("/" + EDIT_SURFACE):
            return True
    return False


def footer_blocks_html(context, request):
    """The inherited footer blocks of ``context``, rendered — or ``""``.

    Empty on the footer's own editing surface (the published footer stays
    out of the editor), with no carrier up the chain, and for an unauthored
    or empty footer.
    """
    if is_footer_editor(request):
        return ""
    carrier = footer_carrier(context)
    footer = authored_footer(carrier)
    if carrier is None or not footer.get("blocks"):
        return ""
    return render_blocks(
        carrier,
        request,
        footer.get("blocks"),
        footer.get("blocks_layout"),
    )
