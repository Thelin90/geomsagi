import logging
from decimal import Decimal

import pytest

from src.invoice_stats import InvoiceStats

LOGGER = logging.getLogger(__name__)

LOGGER.info(
    "Please note this integration test takes a little bit of time in the beginning to initialise "
    "all 20 million rows!\n"
    "Loading..."
)


@pytest.mark.parametrize(
    "random_invoice, random_invoices, expected_mean, expected_median",
    [
        (
            {"invoice_name": f"company_single", "invoice_value": Decimal(999)},
            [
                {"invoice_name": f"company_a", "invoice_value": Decimal(11)},
                {"invoice_name": f"company_b", "invoice_value": Decimal(123333.123)},
                {"invoice_name": f"company_c", "invoice_value": Decimal(100000200.23)},
                {"invoice_name": f"company_d", "invoice_value": Decimal(200000000.00)},
            ],
            75030886.0,  # 75030886.08825 -> 75030886.0
            50061767.0,  # 50061766.6765 -> 50061767.0
        )
    ],
)
def test_add_remove_add(random_invoice, random_invoices, expected_mean, expected_median):
    invoice_stats = InvoiceStats()

    invoice_stats.add_invoices(invoices=random_invoices)

    # Check dimension of invoices
    assert invoice_stats.invoices.shape[0] == len(random_invoices)
    assert invoice_stats.invoices.shape[1] == 2

    invoice_stats.get_mean()
    invoice_stats.get_median()

    # Check dimension of stats table
    assert invoice_stats.invoice_stats.shape[0] == 1
    assert invoice_stats.invoice_stats.shape[1] == 2

    invoice_stats.add_invoice(invoice=random_invoice)

    # Check dimension of invoices
    assert invoice_stats.invoices.shape[0] == len(random_invoices) + 1
    assert invoice_stats.invoices.shape[1] == 2

    invoice_stats.clear()

    # Check dimension of invoices
    assert invoice_stats.invoices.empty
    assert invoice_stats.invoices.empty

    # Check dimension of stats table
    assert invoice_stats.invoice_stats.empty
    assert invoice_stats.invoice_stats.empty

    invoice_stats.add_invoice(invoice=random_invoice)

    # Check dimension of invoices
    assert invoice_stats.invoices.shape[0] == 1
    assert invoice_stats.invoices.shape[1] == 2

    # Check dimension of stats table
    assert invoice_stats.invoice_stats.empty
    assert invoice_stats.invoice_stats.empty

    invoice_stats.get_mean()
    invoice_stats.get_median()

    assert invoice_stats.invoice_stats.values.tolist()[0] == [999.0, 999.0]
