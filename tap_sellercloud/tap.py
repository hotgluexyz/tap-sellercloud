"""Sellercloud tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_sellercloud.streams import (
    PurchaseOrdersStream,
)

STREAM_TYPES = [
    PurchaseOrdersStream,
]


class TapSellercloud(Tap):
    """Sellercloud tap class."""

    name = "tap-sellercloud"

    config_jsonschema = th.PropertiesList(
        th.Property("server_id", th.StringType, required=True),
        th.Property("username", th.StringType, required=True),
        th.Property("password", th.StringType, required=True),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapSellercloud.cli()
