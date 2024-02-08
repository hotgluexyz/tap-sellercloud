"""REST client handling, including SellercloudStream base class."""

import requests
from typing import Any, Dict, Optional
from singer_sdk.streams import RESTStream
from datetime import timedelta, datetime
import requests


class SellercloudStream(RESTStream):
    """Sellercloud stream class."""

    access_token = None
    expires_at = None

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        if self.config.get("api_url"):
            return self.config["api_url"]
        return f"https://{self.config['server_id']}.api.sellercloud.com/rest/api"

    records_jsonpath = "$.Items[*]"

    def get_new_access_token(self):
        url = f"{self.url_base}/token"
        data = {
            "username": self.config["username"],
            "password": self.config["password"],
        }
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()["access_token"]

    def get_access_token(self):
        if self.access_token is None or self.expires_at < datetime.now():
            self.access_token = self.get_new_access_token()
            self.expires_at = datetime.now() + timedelta(hours=1)
        return self.access_token

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        headers["Authorization"] = f"Bearer {self.get_access_token()}"
        return headers

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        data = response.json()
        data = data.get("Items", [])
        if len(data) == 0:
            return None
        if not previous_token:
            return 2  # First page already fetched
        next_page_token = previous_token + 1
        return next_page_token

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        start_date = self.get_starting_timestamp(context) or datetime(2000, 1, 1)
        params["model.pageSize"] = self._page_size
        if next_page_token:
            params["model.pageNumber"] = next_page_token
        if self.replication_key:
            if isinstance(start_date, datetime):
                start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
            params["model.updatedDateFrom"] = start_date
        return params
