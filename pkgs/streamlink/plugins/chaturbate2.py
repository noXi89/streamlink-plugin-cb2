import logging
import re
import uuid

from streamlink.plugin import Plugin, pluginmatcher
from streamlink.plugin.api import validate
from streamlink.stream.hls import HLSStream

log = logging.getLogger(__name__)

API_HLS = "https://chaturbate.com/get_edge_hls_url_ajax/"

_url_re = re.compile(r"https?://(\w+\.)?chaturbate\.com/(?P<username>\w+)")

_post_schema = validate.Schema(
    {
        "url": validate.text,
        "room_status": validate.text,
        "success": int
    }
)

@pluginmatcher(_url_re)
class Chaturbate(Plugin):
    #@classmethod
    #def can_handle_url(cls, url):
    #    return _url_re.match(url)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __init_3_(self, session, account_id, player_id="default_default"):
        self.session = session
        self.account_id = account_id
        self.player_id = player_id
        self.title = None
        log.debug(f"Creating player for account {account_id} (player_id={player_id})")

    def _get_streams(self):
        match = _url_re.match(self.url)
        username = match.group("username")

        CSRFToken = str(uuid.uuid4().hex.upper()[0:32])

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": CSRFToken,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.url,
        }

        cookies = {
            "csrftoken": CSRFToken,
        }

        post_data = "room_slug={0}&bandwidth=high".format(username)

        res = self.session.http.post(API_HLS, headers=headers, cookies=cookies, data=post_data)
        data = self.session.http.json(res, schema=_post_schema)

        if data["success"] is True and data["room_status"] == "public":
            for s in HLSStream.parse_variant_playlist(self.session, data["url"]).items():
                yield s

__plugin__ = Chaturbate
