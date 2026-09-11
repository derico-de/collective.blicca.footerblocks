"""The footer editing surface: view, save service, redirect, and chrome policy.

The field-surface machinery itself (slate adoption, transformer pipeline)
is pinned in plone.blicca.auroraeditor's promised-API tests; here we pin
this package's concrete registrations and the footer policies that ride
on them (ADR 0015).
"""

import json

import pytest
from AccessControl import Unauthorized
from Acquisition import aq_base
from plone import api
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_ID
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_TYPE
from plone.blicca.auroraeditor.interfaces import IPloneBliccaAuroraeditorLayer
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import Interface

from collective.blicca.footerblocks.interfaces import ICollectiveBliccaFooterblocksLayer


def somersault_footer(value):
    return {
        "blocks": {
            SOMERSAULT_BLOCK_ID: {
                "@type": SOMERSAULT_BLOCK_TYPE,
                "value": value,
            }
        },
        "blocks_layout": {"items": [SOMERSAULT_BLOCK_ID]},
    }


class EditingBase:
    @pytest.fixture(autouse=True)
    def _setup(self, integration):
        self.portal = integration["portal"]
        self.request = integration["request"]
        alsoProvides(self.request, ICollectiveBliccaFooterblocksLayer)
        alsoProvides(self.request, IPloneBliccaAuroraeditorLayer)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        login(self.portal, TEST_USER_NAME)

    def _called_view(self):
        view = getMultiAdapter((self.portal, self.request), name="edit-footer")
        view()
        return view


class TestEditFooterView(EditingBase):
    def test_traversal_requires_modify_permission(self):
        logout()
        with pytest.raises(Unauthorized):
            self.portal.restrictedTraverse("@@edit-footer")()

    def test_the_save_is_rebound_to_the_footer_service(self):
        view = self._called_view()
        config = view.config()
        assert config["contentUrl"] == f"{self.portal.absolute_url()}/@footerblocks"
        assert config["unlockUrl"] == f"{self.portal.absolute_url()}/@lock"

    def test_the_save_url_remembers_the_page_the_author_came_from(self):
        page = api.content.create(
            container=self.portal, type="Document", id="page", title="Page"
        )
        self.request.form["origin"] = "/plone/page"
        try:
            config = self._called_view().config()
        finally:
            del self.request.form["origin"]
        assert (
            config["contentUrl"]
            == f"{self.portal.absolute_url()}/@footerblocks?origin=/plone/page"
        )
        assert config["unlockUrl"] == f"{self.portal.absolute_url()}/@lock"
        assert page.absolute_url() not in config["unlockUrl"]

    def test_the_footer_has_no_document_title_block(self):
        view = self._called_view()
        assert view.config()["showTitle"] is False

    def test_text_blocks_may_go_full_bleed_on_the_footer(self):
        """A footer is a full-bleed band, so its text blocks get `full`.

        The base surface deliberately withholds it — a body paragraph on
        a content page should not break out of the page grid. The footer
        opts in; the server renderer already honours `full`.
        """
        view = self._called_view()
        assert view.config()["blockWidths"] == [
            "narrow",
            "default",
            "layout",
            "full",
        ]

    def test_the_surface_is_the_strips_footer_tab(self):
        assert self._called_view().surface_id == "footer"

    def test_page_mounts_the_editor_host(self):
        view = getMultiAdapter((self.portal, self.request), name="edit-footer")
        markup = view()
        assert "pat-auroraeditor" in markup
        assert "@footerblocks" in markup
        # the same edit-area strip the blocks canvas renders, Footer lit
        assert "aurora-edit-tabs" in markup
        assert 'aria-current="page"' in markup

    def test_authored_footer_feeds_the_editor(self):
        self.portal.footer = somersault_footer(
            [{"type": "p", "children": [{"text": "footer words"}]}]
        )
        view = self._called_view()
        data = view.config()["data"]
        value = data["blocks"][SOMERSAULT_BLOCK_ID]["value"]
        assert value == [{"type": "p", "children": [{"text": "footer words"}]}]
        assert data["blocks_layout"] == {"items": [SOMERSAULT_BLOCK_ID]}

    def test_resolveuid_links_resolve_for_the_editor(self):
        """The serialization transformers run over the footer container —
        restapi's own field serializer would skip them (field != blocks)."""
        page = api.content.create(
            container=self.portal, type="Document", id="imprint", title="Imprint"
        )
        uid = api.content.get_uuid(page)
        self.portal.footer = somersault_footer(
            [
                {
                    "type": "p",
                    "children": [
                        {
                            "type": "link",
                            "data": {"url": f"../resolveuid/{uid}"},
                            "children": [{"text": "imprint"}],
                        }
                    ],
                }
            ]
        )
        view = self._called_view()
        url = view.config()["data"]["blocks"][SOMERSAULT_BLOCK_ID]["value"][0][
            "children"
        ][0]["data"]["url"]
        assert "resolveuid" not in url
        assert url.endswith("/imprint")

    def test_unauthored_footer_opens_empty(self):
        """Never the behavior schema's slate "Edit" seed — the surface
        opens as empty as the public page renders."""
        view = self._called_view()
        data = view.config()["data"]
        assert data["blocks"] == {}
        assert data["blocks_layout"] == {"items": []}

    def test_volto_authored_slate_footer_is_adopted(self):
        self.portal.footer = {
            "blocks": {
                "abc": {
                    "@type": "slate",
                    "value": [{"type": "p", "children": [{"text": "from volto"}]}],
                }
            },
            "blocks_layout": {"items": ["abc"]},
        }
        view = self._called_view()
        data = view.config()["data"]
        assert list(data["blocks"]) == [SOMERSAULT_BLOCK_ID]
        assert data["blocks"][SOMERSAULT_BLOCK_ID]["value"] == [
            {"type": "p", "children": [{"text": "from volto"}]}
        ]


class TestFooterSaveService(EditingBase):
    def _service(self, body):
        """The registered service, not the bare factory: plone.rest's ZCML
        directive is what mixes BrowserView into it."""
        self.request["BODY"] = json.dumps(body).encode()
        return getMultiAdapter(
            (self.portal, self.request),
            Interface,
            name="PATCH_application_json_@footerblocks",
        )

    def _save_body(self, value, title="ignored"):
        return {"title": title, **somersault_footer(value)}

    def test_the_service_is_registered_for_json_patch(self):
        """plone.rest dispatch: PATCH + Accept application/json on the
        carrier resolves to this package's service."""
        assert (
            queryMultiAdapter(
                (self.portal, self.request),
                Interface,
                name="PATCH_application_json_@footerblocks",
            )
            is not None
        )

    def test_save_stores_the_container_in_the_footer_field(self):
        value = [{"type": "p", "children": [{"text": "saved words"}]}]
        self._service(self._save_body(value)).reply()
        assert self.portal.footer["blocks"][SOMERSAULT_BLOCK_ID]["value"] == value
        assert self.portal.footer["blocks_layout"] == {
            "items": [SOMERSAULT_BLOCK_ID]
        }
        assert self.request.response.getStatus() == 204

    def test_save_never_touches_the_site_title(self):
        before = self.portal.title
        self._service(
            self._save_body(
                [{"type": "p", "children": [{"text": "words"}]}],
                title="not the site title",
            )
        ).reply()
        assert self.portal.title == before

    def test_absolute_links_are_stored_as_resolveuid(self):
        page = api.content.create(
            container=self.portal, type="Document", id="imprint", title="Imprint"
        )
        value = [
            {
                "type": "p",
                "children": [
                    {
                        "type": "link",
                        "data": {"url": page.absolute_url()},
                        "children": [{"text": "imprint"}],
                    }
                ],
            }
        ]
        self._service(self._save_body(value)).reply()
        stored = self.portal.footer["blocks"][SOMERSAULT_BLOCK_ID]["value"]
        assert "resolveuid/" in stored[0]["children"][0]["data"]["url"]

    def test_a_foreign_lock_forbids_saving(self):
        from plone.locking.interfaces import ILockable

        api.user.create(
            email="other@example.org", username="other", password="secret123",  # noqa: S106 - test fixture user
        )
        setRoles(self.portal, "other", ["Manager"])
        login(self.portal, "other")
        ILockable(self.portal).lock()
        login(self.portal, TEST_USER_NAME)

        result = self._service(
            self._save_body([{"type": "p", "children": [{"text": "words"}]}])
        ).reply()
        assert self.request.response.getStatus() == 403
        assert result["error"]["type"] == "Forbidden"
        # The instance dict, not getattr: Dexterity serves the behavior
        # schema's slate seed for a never-set field.
        assert "footer" not in vars(aq_base(self.portal))

    def test_a_malformed_body_is_rejected(self):
        result = self._service({"title": "no blocks here"}).reply()
        assert self.request.response.getStatus() == 400
        assert result["error"]["type"] == "BadRequest"


class TestSaveUrlRedirect(EditingBase):
    def test_browser_get_on_the_save_url_lands_on_the_carrier(self):
        view = self.portal.restrictedTraverse("@footerblocks")
        assert view() == ""
        response = self.request.response
        assert response.getStatus() == 302
        assert response.getHeader("Location") == self.portal.absolute_url()

    def test_browser_get_on_the_save_url_lands_on_the_page_the_author_came_from(
        self,
    ):
        page = api.content.create(
            container=self.portal, type="Document", id="page", title="Page"
        )
        self.request.form["origin"] = "/plone/page"
        try:
            view = self.portal.restrictedTraverse("@footerblocks")
            assert view() == ""
        finally:
            del self.request.form["origin"]
        assert self.request.response.getHeader("Location") == page.absolute_url()


class TestFooterChromePolicy(EditingBase):
    def _render(self, context):
        from collective.blicca.footerblocks.pagelets import FooterBlocksChromePagelet

        pagelet = FooterBlocksChromePagelet(context, self.request)
        pagelet.update()
        return pagelet.render()

    def test_unauthored_footer_adds_no_empty_band_for_editors(self):
        """The toolbar action is now the way into an unauthored footer."""
        assert self._render(self.portal).strip() == ""

    def test_authored_footer_has_no_inline_edit_link(self):
        self.portal.footer = somersault_footer(
            [{"type": "p", "children": [{"text": "footer words"}]}]
        )
        markup = self._render(self.portal)
        assert "footer words" in markup
        assert "element-footerblocks-edit" not in markup
        assert "@@edit-footer" not in markup

    def test_footer_is_hidden_on_its_editing_surface(self):
        self.portal.footer = somersault_footer(
            [{"type": "p", "children": [{"text": "words being edited"}]}]
        )
        self.request["ACTUAL_URL"] = f"{self.portal.absolute_url()}/@@edit-footer"
        assert self._render(self.portal).strip() == ""

    def test_visitors_still_see_an_authored_footer(self):
        self.portal.footer = somersault_footer(
            [{"type": "p", "children": [{"text": "public words"}]}]
        )
        logout()
        markup = self._render(self.portal)
        assert "public words" in markup
        assert "@@edit-footer" not in markup
