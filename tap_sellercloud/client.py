"""REST client handling, including SellercloudStream base class."""

import requests
from typing import Any, Dict, Optional
from singer_sdk.streams import RESTStream
from datetime import timedelta, datetime
import requests
from datetime import datetime, timedelta, timezone
import typing as t
from singer_sdk.exceptions import RetriableAPIError
import pytz

class SellercloudStream(RESTStream):
    """Sellercloud stream class."""

    access_token = None
    expires_at = None
    replication_key_field = None
    secondary_replication_key_field = None
    today = None
    is_performing_secondary_replication_check = False
    

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
        self.logger.info(f"Access token response: {response.json()}")
        return response.json()["access_token"], response.json()["expires_in"]

    def get_access_token(self):
        if self.access_token is None or self.expires_at < datetime.now():
            self.access_token, expires_in = self.get_new_access_token()
            self.expires_at = datetime.now() + timedelta(seconds=expires_in) - timedelta(minutes=3)
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
        self.logger.info(f"Total records for stream '{self.name}' is {data.get('TotalResults')}")
        data = data.get("Items", [])
        if len(data) == 0:
            return None
        if not previous_token:
            return 2  # First page already fetched
        next_page_token = previous_token + 1
        return next_page_token
    
    def _get_time_intervals(self, start_date: datetime, end_date: datetime, interval_length_days) -> t.List[t.Tuple[datetime, datetime]]:
        """Build a list of time intervals between start_date and end_date"""
        """Built backwards so that recent date gets a full interval"""
        intervals = []
        interval_start_date = end_date
        while interval_start_date > start_date:
            interval_end_date = interval_start_date
            interval_start_date = interval_end_date - timedelta(days=interval_length_days)
            if interval_start_date < start_date:
                interval_start_date = start_date
            intervals.append((interval_start_date, interval_end_date))
        return intervals[::-1]

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        
        start_date = context["interval_start_date"]
        end_date = context["interval_end_date"]

        
        params["model.pageSize"] = self._page_size
        if next_page_token:
            params["model.pageNumber"] = next_page_token
        
        if self.replication_key and not self.is_performing_secondary_replication_check:
            params[f"{self.replication_key_field}From"] = start_date
            params[f"{self.replication_key_field}To"] = end_date
        elif self.secondary_replication_key_field and self.is_performing_secondary_replication_check:
            params[f"{self.secondary_replication_key_field}From"] = start_date
            params[f"{self.secondary_replication_key_field}To"] = end_date
            # To avoid duplicates, we need to filter out records that were already fetched
            params[f"{self.replication_key_field}To"] = start_date
        self.logger.info(f"request params {params}")
        return params
    
    def get_records(self, context: Optional[dict]) -> t.Iterable[Dict[str, Any]]:
        # end date utc time
        config_start_date = (self.get_starting_timestamp(context) or datetime(2000, 1, 1)).replace(tzinfo=pytz.utc)
        time_intervals = self._get_time_intervals(
            config_start_date,
            datetime.now().replace(tzinfo=pytz.utc),
            7,
        )
        self.is_performing_secondary_replication_check = False
        context = context or {}
        for start_date, end_date in time_intervals:
            self.logger.info(f"Fetching data from {start_date} to {end_date}")
            if isinstance(start_date, datetime):
                start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
            if isinstance(end_date, datetime):
                end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")
            context["interval_start_date"] = start_date
            context["interval_end_date"] = end_date
            for record in super().get_records(context):
                yield record

        if self.secondary_replication_key_field:
            self.logger.info("Beginning secondary replication check")
            self.is_performing_secondary_replication_check = True
            context["interval_start_date"] = config_start_date.strftime("%Y-%m-%dT%H:%M:%S")
            context["interval_end_date"] = datetime.now().replace(tzinfo=pytz.utc).strftime("%Y-%m-%dT%H:%M:%S")
            for record in super().get_records(context):
                yield record
            self.is_performing_secondary_replication_check = False


    def validate_response(self, response: requests.Response) -> None:
        # Reset token if received Invalid token response
        if (
            response.status_code == 401 and "Invalid token" in response.reason
        ):
            msg = self.response_error_message(response)
            self.access_token = None
            self.access_token = self.get_access_token()
            response.request.headers["Authorization"] = f"Bearer {self.get_access_token()}"
            raise RetriableAPIError(msg, response)

        super().validate_response(response)


    def backoff_max_tries(self) -> int:
        return 12
