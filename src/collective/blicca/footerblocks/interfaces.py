"""Module where all interfaces, events and exceptions live."""

from plone.pageletlayout.interfaces import IPlonePageletlayoutLayer


class ICollectiveBliccaFooterblocksLayer(IPlonePageletlayoutLayer):
    """Marker interface that defines a browser layer.

    Extends the pagelet-layout layer so this add-on's chrome-pagelet
    override (the ``plone.pageletlayout.styles`` provider, same name, this
    layer) is unambiguously more specific than the base registration — the
    plonetheme.clara precedent.
    """
