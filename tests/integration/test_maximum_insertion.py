import logging
import random
import string
from decimal import Decimal
from time import process_time

import pytest

from src.invoice_stats import InvoiceStats
from src.utils.constants import INVOICE_LIMIT, MAX_INVOICE_VALUE, MIN_INVOICE_VALUE

LOGGER = logging.getLogger(__name__)

LOGGER.info(
    "Please note this integration test takes a little bit of time in the beginning to initialise "
    "all 20 million rows!\n"
    "Loading..."
)


@pytest.mark.parametrize(
    "random_invoices",
    [
        [
            # TODO: this should be a invoices.json preferably, but OK for now
            {
                "invoice_name": f"company_{x}",
                "invoice_value": Decimal(random.randrange(MIN_INVOICE_VALUE, MAX_INVOICE_VALUE)),  # type: ignore
            }
            for x in [
                "".join(random.choice(string.ascii_letters)) for _ in range(0, int(INVOICE_LIMIT))
            ]
        ]
    ],
)
def test_20_million_insert_of_invoices(random_invoices):
    invoice_stats = InvoiceStats()
    t_insert_20_million_rows = process_time()
    invoice_stats.add_invoices(invoices=random_invoices)
    elapsed_time_insert_20_million_rows = process_time() - t_insert_20_million_rows

    LOGGER.info(
        f"elapsed_time_insert_20_million_rows: {elapsed_time_insert_20_million_rows} seconds"
    )

    invoice_stats.invoice_schema.validate(invoice_stats.invoices)

    t_get_median_20_million_rows = process_time()
    invoice_stats.get_median()
    elapsed_time_get_median_20_million_rows = process_time() - t_get_median_20_million_rows

    LOGGER.info(
        f"elapsed_time_get_median_20_million_rows: {elapsed_time_get_median_20_million_rows} seconds"
    )

    t_get_mean_20_million_rows = process_time()
    invoice_stats.get_mean()
    elapsed_time_get_mean_20_million_rows = process_time() - t_get_mean_20_million_rows

    LOGGER.info(f"elapsed_time_get_mean_20_million_rows: {elapsed_time_get_mean_20_million_rows}")

    LOGGER.info(f"\n{invoice_stats.invoice_stats.to_string()}\n")

    # Check dimension of stats table
    assert invoice_stats.invoice_stats.shape[0] == 1
    assert invoice_stats.invoice_stats.shape[1] == 2

    # Check dimension of invoices
    assert invoice_stats.invoices.shape[0] == INVOICE_LIMIT
    assert invoice_stats.invoices.shape[1] == 2
