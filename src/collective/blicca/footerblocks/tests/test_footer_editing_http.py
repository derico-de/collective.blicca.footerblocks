"""The footer surface over real HTTP — the round trip the editor makes.

The unit tests drive views and services directly, which cannot see the two
things that only exist in the publisher: plone.rest's content negotiation
(is a ``PATCH .../@footerblocks`` routed to the service, and is a browser
``GET`` on the same URL left to the redirect view?) and the lock the mount
config hands the remote (does a save with that token get through, and one
without it not?).
"""

import html
import json
import re

import pytest
import requests
import transaction
from Acquisition import aq_base
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_ID
from plone.blicca.auroraeditor import SOMERSAULT_BLOCK_TYPE


BROWSER_ACCEPT = (
    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
)
# The test server is in-process; a request that hangs is a bug, not a slow
# network, so fail fast rather than wedging the suite.
TIMEOUT = 30


def save_body(text):
    return {
        "title": "ignored by the service",
        "blocks": {
            SOMERSAULT_BLOCK_ID: {
                "@type": SOMERSAULT_BLOCK_TYPE,
                "value": [{"type": "p", "children": [{"text": text}]}],
            }
        },
        "blocks_layout": {"items": [SOMERSAULT_BLOCK_ID]},
    }


class TestFooterSurfaceOverHttp:
    @pytest.fixture(autouse=True)
    def _setup(self, acceptance):
        self.portal = acceptance["portal"]
        self.base = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        transaction.commit()

    def _auth(self):
        return (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def _mount_config(self):
        """The mount options the editor page hands the remote."""
        response = requests.get(
            f"{self.base}/@@edit-footer",
            auth=self._auth(),
            headers={"Accept": BROWSER_ACCEPT},
            timeout=TIMEOUT,
        )
        assert response.status_code == 200
        # Chameleon picks the attribute delimiter to suit the JSON, so
        # match whichever quote it chose.
        match = re.search(
            r"data-pat-auroraeditor=([\"'])(.*?)\1", response.text, re.S
        )
        assert match, "the edit page did not inject the mount config"
        return json.loads(html.unescape(match.group(2)))

    def test_the_edit_page_hands_over_a_real_lock(self):
        config = self._mount_config()
        assert config["contentUrl"] == f"{self.base}/@footerblocks"
        assert config["lockToken"], "no lock token was minted for the carrier"
        assert config["token"].count(".") == 2

    def test_the_save_round_trip_reaches_the_footer_field(self):
        config = self._mount_config()
        response = requests.patch(
            config["contentUrl"],
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config['token']}",
                "Lock-Token": config["lockToken"],
            },
            timeout=TIMEOUT,
            json=save_body("saved over http"),
        )
        assert response.status_code == 204

        transaction.begin()
        stored = self.portal.footer["blocks"][SOMERSAULT_BLOCK_ID]["value"]
        assert stored == [{"type": "p", "children": [{"text": "saved over http"}]}]

    def test_the_saved_footer_shows_up_on_a_page(self):
        """The whole point: what the editor saves is what every page's
        tail renders, through the pagelet."""
        config = self._mount_config()
        requests.patch(
            config["contentUrl"],
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config['token']}",
                "Lock-Token": config["lockToken"],
            },
            timeout=TIMEOUT,
            json=save_body("published footer words"),
        )
        transaction.begin()
        api.content.create(
            container=self.portal, type="Document", id="a-page", title="A page"
        )
        transaction.commit()

        page = requests.get(
            f"{self.base}/a-page",
            headers={"Accept": BROWSER_ACCEPT},
            timeout=TIMEOUT,
        )
        assert "published footer words" in page.text
        assert "element-footerblocks" in page.text

    def test_a_save_without_the_lock_token_is_refused(self):
        config = self._mount_config()
        response = requests.patch(
            config["contentUrl"],
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config['token']}",
            },
            timeout=TIMEOUT,
            json=save_body("no lock token"),
        )
        assert response.status_code == 403

    def test_the_representation_reply_reflects_the_stored_container(self):
        """The remote always sends Prefer: return=representation, so the
        reply must be the re-read container, not the submitted body:
        links come back resolved for the still-mounted editor."""
        page = api.content.create(
            container=self.portal, type="Document", id="imprint", title="Imprint"
        )
        transaction.commit()
        config = self._mount_config()
        body = save_body("x")
        body["blocks"][SOMERSAULT_BLOCK_ID]["value"] = [
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
        response = requests.patch(
            config["contentUrl"],
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config['token']}",
                "Lock-Token": config["lockToken"],
                "Prefer": "return=representation",
            },
            timeout=TIMEOUT,
            json=body,
        )
        assert response.status_code == 200
        returned = response.json()
        url = returned["blocks"][SOMERSAULT_BLOCK_ID]["value"][0]["children"][0][
            "data"
        ]["url"]
        # Stored as resolveuid, handed back resolved.
        assert "resolveuid" not in url
        assert url.endswith("/imprint")

    def test_an_anonymous_save_is_refused(self):
        """The service carries cmf.ModifyPortalContent; without
        credentials the publisher must not let a write through."""
        response = requests.patch(
            f"{self.base}/@footerblocks",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=TIMEOUT,
            json=save_body("anonymous words"),
        )
        assert response.status_code in (401, 403)
        transaction.begin()
        assert "footer" not in vars(aq_base(self.portal))

    def test_a_browser_get_on_the_save_url_lands_on_the_site(self):
        """Post-save and post-cancel the host pattern navigates to
        contentUrl; plone.rest leaves a multi-media-type browser GET
        alone, so the same-named redirect view answers it."""
        response = requests.get(
            f"{self.base}/@footerblocks",
            auth=self._auth(),
            headers={"Accept": BROWSER_ACCEPT},
            allow_redirects=False,
            timeout=TIMEOUT,
        )
        assert response.status_code == 302
        assert response.headers["Location"] == self.base
