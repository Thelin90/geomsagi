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
    "random_invoices, expected_mean, expected_median",
    [
        (
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
def test_mean_and_median_of_invoices(random_invoices, expected_mean, expected_median):
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

    # Validate that mean and median is correct
    LOGGER.info(
        f"{invoice_stats.invoice_stats.values.tolist()[0]} == {[expected_mean, expected_median]}"
    )
    assert invoice_stats.invoice_stats.values.tolist()[0] == [expected_mean, expected_median]
