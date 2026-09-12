"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class ICollectiveBliccaFooterblocksLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer.

    A plain layer: it must not extend plone.pageletlayout's, or installing
    this add-on alone on a stock site would switch on every one of
    pageletlayout's layer-bound registrations without its profile.
    """
