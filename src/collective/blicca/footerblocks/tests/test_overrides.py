"""overrides.zcml is an override, not a second registration that happens
to win.

The styles provider of every plone.pageletlayout page is replaced by
registering ``plone:chromepagelet name="plone.pageletlayout.styles"`` for
pageletlayout's own layer — the base stanza's exact discriminator. Loaded
as an ordinary include that is a configuration conflict; loaded through
``includeOverrides`` (what Plone's ``autoIncludePluginsOverrides`` does for
a plugin's overrides.zcml) it replaces the base. Both halves are pinned on
a configuration machine of their own, so the proof does not depend on the
order the fixture happened to load files in. The base stanza is loaded as
a nested include, as chrome.zcml is in a real site: an override wins by
having the *shorter* include path, so a base at the top level could never
be overridden by anything.
"""

import plone.pageletlayout
import pytest
from plone.pageletlayout.interfaces import IPlonePageletlayoutLayer
from zope.component import getGlobalSiteManager
from zope.configuration import xmlconfig
from zope.configuration.config import ConfigurationConflictError
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView

import collective.blicca.footerblocks
from collective.blicca.footerblocks.pagelets import FooterStylesChromePagelet


NAME = "plone.pageletlayout.styles"

#: plone.pageletlayout's own stanza (pagelets/chrome.zcml), verbatim.
BASE = """\
<configure xmlns:plone="http://namespaces.plone.org/plone">
  <include package="plone.pageletlayout" file="meta.zcml" />
  <plone:chromepagelet
      name="plone.pageletlayout.styles"
      class="plone.pageletlayout.pagelets.head.StylesChromePagelet"
      layer="plone.pageletlayout.interfaces.IPlonePageletlayoutLayer"
      />
</configure>
"""


def machine(tmp_path):
    base = tmp_path / "chrome.zcml"
    base.write_text(BASE)
    context = xmlconfig.ConfigurationMachine()
    xmlconfig.registerCommonDirectives(context)
    xmlconfig.include(context, str(base))
    return context


def registered_styles_class():
    return getGlobalSiteManager().adapters.lookup(
        (Interface, IPlonePageletlayoutLayer, IBrowserView), IContentProvider, name=NAME
    )


class TestOverride:
    @pytest.fixture(autouse=True)
    def _setup(self, integration, tmp_path):
        """The registry is the fixture's; whichever stanza executes below
        re-registers the class the fixture already holds."""
        self.tmp_path = tmp_path

    def test_as_a_plain_include_the_stanza_conflicts_with_the_base(self):
        context = machine(self.tmp_path)
        xmlconfig.include(context, "overrides.zcml", package=collective.blicca.footerblocks)
        with pytest.raises(ConfigurationConflictError) as excinfo:
            context.execute_actions()
        assert NAME in str(excinfo.value)

    def test_as_an_override_the_stanza_replaces_the_base(self):
        context = machine(self.tmp_path)
        xmlconfig.includeOverrides(
            context, "overrides.zcml", package=collective.blicca.footerblocks
        )
        context.execute_actions()
        assert issubclass(registered_styles_class(), FooterStylesChromePagelet)

    def test_the_fixture_holds_the_override(self):
        assert issubclass(registered_styles_class(), FooterStylesChromePagelet)
        assert plone.pageletlayout  # the frame is importable, so the file loads
