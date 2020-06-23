from decimal import Decimal
from typing import Generator
from unittest.mock import MagicMock, call, patch

import pandas as pd
import pytest

from src.invoice_stats import InvoiceStats
from src.utils.constants import INVOICE_STATS_COLUMN_NAMES
from tests.constants import INVOICE_STATS_PATH, LIMIT, MAX_VALUE, MIN_VALUE


@pytest.fixture(autouse=True)
def mock_numpy() -> Generator[MagicMock, None, None]:
    with patch(f"{INVOICE_STATS_PATH}.np") as mock_numpy:
        yield mock_numpy


@pytest.fixture(autouse=True)
def mock_math() -> Generator[MagicMock, None, None]:
    with patch(f"{INVOICE_STATS_PATH}.math") as mock_math:
        yield mock_math


@pytest.fixture(autouse=True)
def mock_logging() -> Generator[MagicMock, None, None]:
    with patch(f"{INVOICE_STATS_PATH}.LOGGER") as mock_logging:
        mock_logging.warning = MagicMock()
        yield mock_logging


@pytest.fixture(autouse=True)
def mock_pandas() -> Generator[MagicMock, None, None]:
    with patch(f"{INVOICE_STATS_PATH}.pd", spec=pd) as mock_pandas:
        yield mock_pandas


@pytest.fixture(autouse=True)
def mock_valid_min_invoice_val() -> Generator[MagicMock, None, None]:
    with patch(f"{INVOICE_STATS_PATH}.valid_min_invoice_val") as mock_valid_min_invoice_val:
        mock_valid_min_invoice_val.return_value = MIN_VALUE
        yield mock_valid_min_invoice_val


@pytest.fixture(autouse=True)
def mock_valid_max_invoice_val() -> Generator[MagicMock, None, None]:
    with patch(f"{INVOICE_STATS_PATH}.valid_max_invoice_val") as mock_valid_max_invoice_val:
        mock_valid_max_invoice_val.return_value = MAX_VALUE
        yield mock_valid_max_invoice_val


@pytest.fixture(autouse=True)
def mock_valid_invoice_limit() -> Generator[MagicMock, None, None]:
    with patch(f"{INVOICE_STATS_PATH}.valid_invoice_limit") as mock_valid_invoice_limit:
        mock_valid_invoice_limit.return_value = LIMIT
        yield mock_valid_invoice_limit


@pytest.fixture(autouse=True)
def mock_create_invoice_schema() -> Generator[MagicMock, None, None]:
    with patch(f"{INVOICE_STATS_PATH}.create_invoice_schema") as mock_create_invoice_schema:
        yield mock_create_invoice_schema


@pytest.fixture(autouse=True)
def mock_create_invoice_stats_schema() -> Generator[MagicMock, None, None]:
    with patch(
        f"{INVOICE_STATS_PATH}.create_invoice_stats_schema"
    ) as mock_create_invoice_stats_schema:
        yield mock_create_invoice_stats_schema


@pytest.fixture(autouse=True)
def invoice_instance(
    mock_pandas,
    mock_valid_min_invoice_val,
    mock_valid_max_invoice_val,
    mock_valid_invoice_limit,
    mock_create_invoice_schema,
    mock_create_invoice_stats_schema,
) -> Generator[InvoiceStats, None, None]:
    """PyTest fixture to create invoice instance to use in tests"""
    invoice_stats: InvoiceStats = InvoiceStats(
        max_invoice_value=MAX_VALUE, min_invoice_value=MIN_VALUE, invoice_limit=LIMIT,
    )

    yield invoice_stats


class TestInvoiceStats:
    def test_constructor_call(
        self,
        invoice_instance,
        mock_pandas,
        mock_valid_min_invoice_val,
        mock_valid_max_invoice_val,
        mock_valid_invoice_limit,
        mock_create_invoice_schema,
        mock_create_invoice_stats_schema,
    ):
        # Check Pandas DF logic
        assert mock_pandas.DataFrame.call_count == 2
        assert mock_pandas.DataFrame.call_args_list == [
            call(columns=["invoice_name", "invoice_value"]),
            call(columns=["invoice_mean", "invoice_median"]),
        ]

        # Column names for median and mean
        assert invoice_instance.median_col_name == INVOICE_STATS_COLUMN_NAMES.get("invoice_median")
        assert invoice_instance.mean_col_name == INVOICE_STATS_COLUMN_NAMES.get("invoice_mean")

        # Check valid_min_invoice_val logic
        assert mock_valid_min_invoice_val.call_count == 1
        assert mock_valid_min_invoice_val.call_args_list == [call(min_invoice_value=MIN_VALUE)]

        # Check valid_max_invoice_val logic
        assert mock_valid_max_invoice_val.call_count == 1
        assert mock_valid_max_invoice_val.call_args_list == [call(max_invoice_value=MAX_VALUE)]

        # Check valid_invoice_limit logic
        assert mock_valid_invoice_limit.call_count == 1
        assert mock_valid_invoice_limit.call_args_list == [call(invoice_limit=LIMIT)]

        # Check create_invoice_schema logic
        assert mock_create_invoice_schema.call_count == 1
        assert mock_create_invoice_schema.call_args_list == [
            call(
                max_invoice_value=invoice_instance.max_invoice_value,
                min_invoice_value=invoice_instance.min_invoice_value,
            )
        ]

        # Check create_invoice_stats_schema logic
        assert mock_create_invoice_stats_schema.call_count == 1
        assert mock_create_invoice_stats_schema.call_args_list == [call()]

    @pytest.mark.parametrize(
        "invoices",
        [
            (
                [
                    {"invoice_name": f"company_a", "invoice_value": Decimal(MAX_VALUE / 2)},
                    {"invoice_name": f"company_b", "invoice_value": Decimal(MAX_VALUE - 1)},
                    {"invoice_name": f"company_c", "invoice_value": Decimal(MAX_VALUE // 2)},
                ]
            )
        ],
    )
    def test_add_invoices(self, invoices, invoice_instance, mock_pandas):
        # Reset pandas mock to validate inner calls
        mock_pandas.reset_mock()

        # Mock inner call
        mock_add_invoice = MagicMock()
        invoice_instance.add_invoice = mock_add_invoice

        # Make call
        invoice_instance.add_invoices(invoices=invoices)

        # Check add_invoices logic
        assert mock_add_invoice.call_count == 1
        assert mock_add_invoice.call_args_list == [call(invoice=mock_pandas.DataFrame.return_value)]

        # Check Pandas DF logic
        assert mock_pandas.DataFrame.call_count == 1
        assert mock_pandas.DataFrame.call_args_list == [
            call(invoices, columns=invoice_instance.invoices.columns)
        ]

    @pytest.mark.parametrize(
        "invoices, ignore_index",
        [
            (
                [
                    {"invoice_name": f"company_a", "invoice_value": Decimal(MAX_VALUE / 2)},
                    {"invoice_name": f"company_b", "invoice_value": Decimal(MAX_VALUE - 2)},
                ],
                True,
            )
        ],
    )
    def test_add_multiple_invoices(
        self, invoices, ignore_index, invoice_instance, mock_pandas,
    ):
        # Reset pandas mock to validate inner calls
        mock_pandas.reset_mock()

        # Set shape and loc logic
        invoice_instance.invoices.shape.__getitem__.return_value = MIN_VALUE
        invoice_instance.invoices.loc.__getitem__.return_value = invoices
        mock_pd = invoice_instance.invoices

        # Make call
        invoice_instance.add_invoice(invoice=invoices)

        # Concat logic when only 1 row insert
        assert mock_pandas.concat.call_count == 1
        assert mock_pandas.concat.call_args_list == [
            call([invoices, mock_pd], ignore_index=ignore_index,)
        ]

        # Check mock_create_invoice_schema logic
        assert invoice_instance.invoice_schema.validate.call_count == 1
        assert invoice_instance.invoice_schema.validate.call_args_list == [
            call(invoice_instance.invoices)
        ]

    @pytest.mark.parametrize(
        "invoice", [({"invoice_name": f"company_a", "invoice_value": Decimal(MAX_VALUE / 2)})],
    )
    def test_add_single_invoice(self, invoice, invoice_instance, mock_pandas):
        # Reset pandas mock to validate inner calls
        mock_pandas.reset_mock()

        # Set shape and loc logic
        invoice_instance.invoices.shape.__getitem__.return_value = MIN_VALUE
        invoice_instance.invoices.loc.__getitem__.return_value = invoice

        # Make call
        invoice_instance.add_invoice(invoice=invoice)

        # Concat logic when only 1 row insert
        assert mock_pandas.concat.call_count == 0

        # Check mock_create_invoice_schema logic
        assert invoice_instance.invoice_schema.validate.call_count == 1
        assert invoice_instance.invoice_schema.validate.call_args_list == [
            call(invoice_instance.invoices)
        ]

    @pytest.mark.parametrize(
        "warning_msg",
        [
            [
                call(
                    "Maximal limit of invoices reached, please clear invoices and try again\ninvoice length < self.invoice_limit: False"
                )
            ]
        ],
    )
    def test_add_invoice_warning(self, warning_msg, invoice_instance, mock_logging):
        # Set shape and loc logic
        invoice_instance.invoices.shape.__getitem__.return_value = LIMIT + 1

        # Make call
        invoice_instance.add_invoice(invoice={"a": 0})

        # Check mock_logging logic
        assert mock_logging.warning.call_count == 1
        assert mock_logging.warning.call_args_list == warning_msg

    def test_clear(self, invoice_instance):
        invoice_instance.invoices = MagicMock(spec=pd.DataFrame)
        invoice_instance.invoice_stats = MagicMock(spec=pd.DataFrame)

        # Set shape and loc logic
        invoice_instance.invoices.shape.__getitem__.return_value = MIN_VALUE
        invoice_instance.invoice_stats.shape.__getitem__.return_value = MIN_VALUE

        # Make call
        invoice_instance.clear()

        # Check drop logic
        assert invoice_instance.invoices.drop.call_count == 1
        assert invoice_instance.invoices.drop.call_args_list == [
            call(invoice_instance.invoices.index, inplace=True)
        ]
        assert invoice_instance.invoice_stats.drop.call_count == 1
        assert invoice_instance.invoice_stats.drop.call_args_list == [
            call(invoice_instance.invoice_stats.index, inplace=True)
        ]

    @pytest.mark.parametrize("warning_msg", [[call("Warning! There is no data to delete!")]])
    def test_clear_warning(self, warning_msg, invoice_instance, mock_logging):
        # Set shape and loc logic
        invoice_instance.invoices.shape.__getitem__.return_value = 0
        invoice_instance.invoice_stats.shape.__getitem__.return_value = 0

        # Make call
        invoice_instance.clear()

        # Check mock_logging logic
        assert mock_logging.warning.call_count == 1
        assert mock_logging.warning.call_args_list == warning_msg

    @pytest.mark.parametrize(
        "expected_agg_input, expected_round_down_input",
        [([call(agg_type="mean", column="invoice_mean", row=0)], [call(column="invoice_mean")],)],
    )
    def test_get_mean(self, expected_agg_input, expected_round_down_input, invoice_instance):
        invoice_instance._set_agg_value_invoice_values = MagicMock()
        invoice_instance._round_down = MagicMock()

        invoice_instance.get_mean()

        # Check _set_agg_value_invoice_values logic
        assert invoice_instance._set_agg_value_invoice_values.call_count == 1
        assert invoice_instance._set_agg_value_invoice_values.call_args_list == expected_agg_input

        # Check _round_down logic
        assert invoice_instance._round_down.call_count == 1
        assert invoice_instance._round_down.call_args_list == expected_round_down_input

        # Check stats schema
        assert invoice_instance.invoice_stats_schema.validate.call_count == 1
        assert invoice_instance.invoice_stats_schema.validate.call_args_list == [
            call(invoice_instance.invoice_stats)
        ]

    @pytest.mark.parametrize(
        "expected_agg_input, expected_round_down_input",
        [
            (
                [call(agg_type="median", column="invoice_median", row=0)],
                [call(column="invoice_median")],
            )
        ],
    )
    def test_get_median(self, expected_agg_input, expected_round_down_input, invoice_instance):
        invoice_instance._set_agg_value_invoice_values = MagicMock()
        invoice_instance._round_down = MagicMock()

        invoice_instance.get_median()

        # Check _set_agg_value_invoice_values logic
        assert invoice_instance._set_agg_value_invoice_values.call_count == 1
        assert invoice_instance._set_agg_value_invoice_values.call_args_list == expected_agg_input

        # Check _round_down logic
        assert invoice_instance._round_down.call_count == 1
        assert invoice_instance._round_down.call_args_list == expected_round_down_input

        # Check stats schema
        assert invoice_instance.invoice_stats_schema.validate.call_count == 1
        assert invoice_instance.invoice_stats_schema.validate.call_args_list == [
            call(invoice_instance.invoice_stats)
        ]

    def test_round_down(self, invoice_instance, mock_numpy, mock_math):
        invoice_instance._round_down(column=invoice_instance.mean_col_name)
        assert invoice_instance.invoice_stats[invoice_instance.mean_col_name].apply.call_count == 1

    @pytest.mark.parametrize(
        "row, column, agg_type", [(0, "col1", "mean"), (0, "col2", "median"), (0, "col2", "max")]
    )
    def test_set_agg_value_invoice_values(
        self, invoice_instance, row, column, agg_type, mock_logging
    ):
        invoice_instance._set_agg_value_invoice_values(row=row, column=column, agg_type=agg_type)

        if agg_type == "mean":
            # Check mean logic
            assert invoice_instance.invoices["invoice_value"].mean.call_count == 1
            assert invoice_instance.invoices["invoice_value"].median.call_count == 0

        elif agg_type == "median":
            # Check median logic
            assert invoice_instance.invoices["invoice_value"].median.call_count == 1
            assert invoice_instance.invoices["invoice_value"].mean.call_count == 0
        else:
            warning_message = [call("Warning! agg_type not supported: max")]
            # Check with not supported agg_type
            assert mock_logging.warning.call_count == 1
            assert mock_logging.warning.call_args_list == warning_message
