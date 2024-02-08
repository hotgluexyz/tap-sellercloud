"""Stream type classes for tap-sellercloud."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_sellercloud.client import SellercloudStream


class PurchaseOrdersStream(SellercloudStream):
    """Define custom stream."""

    name = "purchase_orders"
    path = "/PurchaseOrders"
    primary_keys = ["ID"]
    replication_key = "LastRevisedOn"

    schema = th.PropertiesList(
        th.Property("ID", th.NumberType),
        th.Property("EmailSentCount", th.NumberType),
        th.Property("DisableInventoryCount", th.BooleanType),
        th.Property("POType", th.NumberType),
        th.Property("CancelledPOID", th.NumberType),
        th.Property("TotalBalance", th.NumberType),
        th.Property("TotalBalanceNotReceivedGood", th.NumberType),
        th.Property("VendorID", th.NumberType),
        th.Property("PurchaseTitle", th.StringType),
        th.Property("CreatedOn", th.DateTimeType),
        th.Property("CreatedBy", th.NumberType),
        th.Property("OrderTotal", th.NumberType),
        th.Property("TaxTotal", th.NumberType),
        th.Property("ShippingTotal", th.NumberType),
        th.Property("GrandTotal", th.NumberType),
        th.Property("DateOrdered", th.DateTimeType),
        th.Property("LastRevisedOn", th.DateTimeType),
        th.Property("RevisedBy", th.NumberType),
        th.Property("PurchaseOrderStatus", th.NumberType),
        th.Property("PaymentStatus", th.NumberType),
        th.Property("ExtraCharges", th.NumberType),
        th.Property("TotalRefunded", th.NumberType),
        th.Property("PurchaseOrdersShippingStatus", th.NumberType),
        th.Property("TrackingNumber", th.StringType),
        th.Property("TrackingNumbers", th.CustomType({"type": ["array", "string"]})),
        th.Property("ShippedOn", th.StringType),
        th.Property("CourierService", th.StringType),
        th.Property("PurchaseOrdersPriority", th.NumberType),
        th.Property("ReceivingStatus", th.NumberType),
        th.Property("CompanyID", th.NumberType),
        th.Property("PurchaseOrdersApproved", th.BooleanType),
        th.Property("DropShipOrderNumber", th.NumberType),
        th.Property("VendorInvoiceNumber", th.StringType),
        th.Property("VendorInvoiceFileName", th.StringType),
        th.Property("VendorInvoiceFileNameOriginal", th.StringType),
        th.Property("Invoices", th.CustomType({"type": ["array", "string"]})),
        th.Property("Memo", th.StringType),
        th.Property("ExpectedDeliveryDate", th.DateTimeType),
        th.Property("DiscountTotal", th.NumberType),
        th.Property("bExported", th.BooleanType),
        th.Property("DisplayName", th.StringType),
        th.Property("CM", th.NumberType),
        th.Property("NotesCount", th.NumberType),
        th.Property("PaidOn", th.StringType),
        th.Property("UnitCounts", th.NumberType),
        th.Property("PurchaseOrderCreditMemo", th.BooleanType),
        th.Property("WarehouseID", th.NumberType),
        th.Property("Items", th.CustomType({"type": ["array", "string"]})),
        th.Property("RequestedShippingCarrier", th.StringType),
        th.Property("RequestedShippingService", th.StringType),
        th.Property("ShipToAddress", th.CustomType({"type": ["object", "string"]})),
    ).to_dict()
