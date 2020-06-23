import logging
from decimal import Decimal

import pytest
from pandera.errors import SchemaError

from src.invoice_stats import InvoiceStats
from src.utils.constants import MAX_INVOICE_VALUE

LOGGER = logging.getLogger(__name__)

LOGGER.info(
    "Testing that pandera schema check fails when we try to insert a invoice value that is "
    "incorrect, given:"
    "\npa.Check.less_than_or_equal_to(max_invoice_value)\n"
    "pa.Check.greater_than_or_equal_to(min_invoice_value)\n"
    "Loading..."
)


@pytest.mark.parametrize(
    "incorrect_invoices",
    [
        [
            # TODO: this should be a invoices.json preferably, but OK for now
            {
                "invoice_name": f"company_fail",
                "invoice_value": Decimal(MAX_INVOICE_VALUE + 1),  # type: ignore
            },
            {
                "invoice_name": f"company_fail",
                "invoice_value": Decimal(MAX_INVOICE_VALUE + 100),  # type: ignore
            },
            {
                "invoice_name": f"company_fail",
                "invoice_value": Decimal(-1000000),  # type: ignore
            },
        ]
    ],
)
def test_insert_failure(incorrect_invoices):
    invoice_stats = InvoiceStats()
    with pytest.raises(SchemaError):
        invoice_stats.add_invoices(invoices=incorrect_invoices)


@pytest.mark.parametrize(
    "incorrect_invoice",
    [
        # TODO: this should be a invoices.json preferably, but OK for now
        {
            "invoice_name": f"company_fail",
            "invoice_value": 123.0,  # type: ignore
        }
    ],
)
def test_get_median_failure(incorrect_invoice):
    invoice_stats = InvoiceStats()
    invoice_stats.add_invoice(incorrect_invoice)

    # force wrong value
    invoice_stats.invoices["invoice_value"] = "abc"

    with pytest.raises(Exception):
        invoice_stats.get_median()


@pytest.mark.parametrize(
    "incorrect_invoice",
    [
        # TODO: this should be a invoices.json preferably, but OK for now
        {
            "invoice_name": f"company_fail",
            "invoice_value": 123.0,  # type: ignore
        }
    ],
)
def test_get_mean_failure(incorrect_invoice):
    invoice_stats = InvoiceStats()
    invoice_stats.add_invoice(incorrect_invoice)

    # force wrong value
    invoice_stats.invoices["invoice_value"] = "abc"

    with pytest.raises(Exception):
        invoice_stats.get_mean()


@pytest.mark.parametrize(
    "incorrect_invoice",
    [
        # TODO: this should be a invoices.json preferably, but OK for now
        {
            "invoice_name": f"company_fail",
            "invoice_value": 123.0,  # type: ignore
        }
    ],
)
def test_set_agg_value_invoice_values_failure(incorrect_invoice):
    invoice_stats = InvoiceStats()

    invoice_stats.add_invoice(invoice=incorrect_invoice)

    # force wrong value
    invoice_stats.invoices["invoice_value"] = "abc"

    with pytest.raises(Exception):
        invoice_stats._set_agg_value_invoice_values(row=0, column="asdasd", agg_type="mean")
