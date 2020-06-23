import logging
import math
from decimal import Decimal
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd

from src.utils.constants import (
    INVOICE_COLUMN_NAMES,
    INVOICE_ROW_DATA_INPUT_TYPE,
    INVOICE_STATS_COLUMN_NAMES,
)
from src.utils.invoice_valid_limits import (
    valid_invoice_limit,
    valid_max_invoice_val,
    valid_min_invoice_val,
)
from src.utils.schemas.invoice import create_invoice_schema, create_invoice_stats_schema

LOGGER = logging.getLogger(__name__)


class InvoiceStats:
    """InvoiceStats class"""

    def __init__(
        self,
        max_invoice_value: Optional[Union[Decimal, float]] = None,
        min_invoice_value: Optional[Union[Decimal, float]] = None,
        invoice_limit: Optional[Union[Decimal, int]] = None,
    ) -> None:
        """InvoiceStats constructor.

        By default the valid invoices values follow: 0 < value < $200,000,000.00. This can also
        be configurable and changed by this constructor, within these limits.

        Args:
            max_invoice_value (Optional[Union[Decimal, float]]): max value for an invoice, by
                default 200000000.00
            min_invoice_value (Optional[Union[Decimal, float]]): min value for an invoice, by
                default 1
            invoice_limit (Optional[Union[Decimal, int]]): number of invoices limit, by
                default 20000000

        """
        # Set column names
        self.invoices = pd.DataFrame(columns=list(INVOICE_COLUMN_NAMES.values()))
        self.invoice_stats = pd.DataFrame(columns=list(INVOICE_STATS_COLUMN_NAMES.values()))
        self.median_col_name = INVOICE_STATS_COLUMN_NAMES.get("invoice_median")
        self.mean_col_name = INVOICE_STATS_COLUMN_NAMES.get("invoice_mean")

        # Set the limits for min, max invoice value and total number of accepted invoices,
        # to be used for checking each invoice(s) that gets added to the invoice_holder list
        self.min_invoice_value = valid_min_invoice_val(min_invoice_value=min_invoice_value)
        self.max_invoice_value = valid_max_invoice_val(max_invoice_value=max_invoice_value)
        self.invoice_limit = valid_invoice_limit(invoice_limit=invoice_limit)

        self.invoice_schema = create_invoice_schema(
            max_invoice_value=self.max_invoice_value, min_invoice_value=self.min_invoice_value,
        )
        self.invoice_stats_schema = create_invoice_stats_schema()

    def add_invoices(self, invoices: List[INVOICE_ROW_DATA_INPUT_TYPE]) -> None:
        """Method to add invoices, due to the size limit up to 20000000.

        Args:
            invoices (List[INVOICE_ROW_DATA_INPUT_TYPE]): A list of invoices

        """
        self.add_invoice(invoice=pd.DataFrame(invoices, columns=self.invoices.columns))

    def add_invoice(
        self,
        invoice: Union[INVOICE_ROW_DATA_INPUT_TYPE, pd.DataFrame],
        ignore_index_flag: bool = True,
    ) -> None:
        """Method to add a single invoice(s) to the invoice pd.DataFrame.

        Args:
            invoice (INVOICE_ROW_DATA_INPUT_TYPE): Data to insert
            ignore_index_flag (bool): If the index_flag should be ignored or not, dataframe creation

        Notes:
            If add_invoices invokes this method, it means that a list of invoices will perform
            UNION on the existing pd.DataFrame.

        """
        try:
            invoice_row_count = self.invoices.shape[0]

            if invoice_row_count < self.invoice_limit:

                if isinstance(invoice, Dict):
                    self.invoices.loc[len(self.invoices)] = invoice

                else:
                    self.invoices = pd.concat(
                        [invoice, self.invoices], ignore_index=ignore_index_flag,
                    )

                self.invoice_schema.validate(self.invoices)
            else:
                LOGGER.warning(
                    f"Maximal limit of invoices reached, please clear invoices and try again\n"
                    f"invoice length < self.invoice_limit: {invoice_row_count < self.invoice_limit}"
                )

        except Exception as insert_error:
            raise insert_error

    def clear(self, inplace: bool = True) -> None:
        """Method to drop all rows in tables related to invoice data

        Args:
            inplace (bool): Determine if it should delete one or more columns in-place

        """
        invoices_row_count = self.invoices.shape[0]
        invoice_stats_row_count = self.invoice_stats.shape[0]

        if invoices_row_count > 0 and invoice_stats_row_count > 0:
            self.invoices.drop(self.invoices.index, inplace=inplace)
            self.invoice_stats.drop(self.invoice_stats.index, inplace=inplace)
        else:
            LOGGER.warning(f"Warning! There is no data to delete!")

    def get_median(self, row: int = 0) -> None:
        """Method to get the median value from the invoice values, and assign it to the median
        invoice stats column.

        Args:
            row (int): Given row to fetch

        """
        try:
            if self.median_col_name is not None:

                self._set_agg_value_invoice_values(
                    row=row, column=self.median_col_name, agg_type="median",
                )

                self._round_down(column=self.median_col_name)
                self.invoice_stats_schema.validate(self.invoice_stats)
            else:
                LOGGER.warning(f"Warning, self.median_col_name={self.median_col_name}")

        except Exception as get_median_error:
            raise get_median_error

    def get_mean(self, row: int = 0) -> None:
        """Method to get the mean value from the invoice values, and assign it to the mean
        invoice stats column.

        Args:
            row (int): Given row to fetch

        """
        try:
            if self.mean_col_name is not None:

                self._set_agg_value_invoice_values(
                    row=row, column=self.mean_col_name, agg_type="mean",
                )

                self._round_down(column=self.mean_col_name)
                self.invoice_stats_schema.validate(self.invoice_stats)

            else:
                LOGGER.warning(f"Warning, self.mean_col_name={self.mean_col_name}")

        except Exception as get_mean_error:
            raise get_mean_error

    def _round_down(self, column: str, round_up_limit: float = 0.5):
        """Method to round down column values based on np.floor

        Args:
            column (str): Given column name, where the values need to be rounded up if col1 value
            > 0.5, else round down.
            round_up_limit (float): Limit to determine ceil or floor

        Examples:

            col1    ->  col1
            3.5     ->  3.0
            3.5     ->  3.0
            3.6     ->  4.0

        Notes:
            math.modf(x)[0] returns the fractional value -> 3.5 -> 0.5

        """
        self.invoice_stats[column] = self.invoice_stats[column].apply(
            lambda x: np.ceil(x) if math.modf(x)[0] > round_up_limit else np.floor(x)
        )

    def _set_agg_value_invoice_values(self, row: int, column: str, agg_type: str) -> None:
        """Simple private method to set the given agg_type column value from the invoice_values,
        in memory.

        Args:
            row ():
            column (str):
            agg_type (str):

        Notes:
            Utilises pd.at[row_index, col_name] to access a single value for a row/column label
            pair (https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.at.html)

        """
        try:

            if agg_type == "mean":
                self.invoice_stats.at[row, column] = self.invoices[
                    INVOICE_COLUMN_NAMES.get("invoice_value")
                ].mean()

            elif agg_type == "median":
                self.invoice_stats.at[row, column] = self.invoices[
                    INVOICE_COLUMN_NAMES.get("invoice_value")
                ].median()

            else:
                LOGGER.warning(f"Warning! agg_type not supported: {agg_type}")

        except Exception as agg_warning:
            raise agg_warning
