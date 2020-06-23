import os
from decimal import Decimal
from typing import Dict, Union

MAX_INVOICE_VALUE = Decimal(os.getenv("MAX_INVOICE_VALUE", 200000000.00))
MIN_INVOICE_VALUE = Decimal(os.getenv("MIN_INVOICE_VALUE", 1))
INVOICE_LIMIT = Decimal(os.getenv("INVOICE_LIMIT", 20000000))

INVOICE_COLUMN_NAMES: Dict[str, str] = {
    "invoice_name": "invoice_name",
    "invoice_value": "invoice_value",
}
INVOICE_STATS_COLUMN_NAMES: Dict[str, str] = {
    "invoice_mean": "invoice_mean",
    "invoice_median": "invoice_median",
}

INVOICE_ROW_DATA_INPUT_TYPE = Dict[str, Union[str, int, float, Decimal]]
