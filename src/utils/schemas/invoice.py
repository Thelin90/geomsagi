from decimal import Decimal

import pandera as pa

from src.utils.constants import INVOICE_COLUMN_NAMES, INVOICE_STATS_COLUMN_NAMES


def create_invoice_schema(
    max_invoice_value: Decimal,
    min_invoice_value: Decimal,
    coerce: bool = True,
    strict: bool = True,
    nullable: bool = False,
):
    """Function to validate that invoice schema is correct, it also does value checks in runtime
    (really nice stuff, right here).

    Args:
        max_invoice_value (Decimal): Given max invoice value
        min_invoice_value (Decimal): Given min invoice value
        coerce (bool): Flag given to determine whether to coerce series to specified type
        strict (bool): Flag given to determine whether or not to accept columns in the
            dataframe that are not in the DataFrame
        nullable (bool): If columns should be nullable or not

    Returns: A pandas DataFrame schema that validates that the types are correct, and that the
    values inserted are correct. If a row is inserted that does not follow:

    0 < invoice_value < 200000000.00

    An error will be thrown in runtime.

    """
    return pa.DataFrameSchema(
        {
            INVOICE_COLUMN_NAMES.get("invoice_name"): pa.Column(pa.String, nullable=nullable),
            INVOICE_COLUMN_NAMES.get("invoice_value"): pa.Column(
                pa.Float64,
                checks=[
                    pa.Check.less_than_or_equal_to(max_invoice_value),
                    pa.Check.greater_than_or_equal_to(min_invoice_value),
                ],
                nullable=nullable,
            ),
        },
        index=pa.Index(pa.Int),
        strict=strict,
        coerce=coerce,
    )


def create_invoice_stats_schema(coerce: bool = True, strict: bool = True, nullable: bool = True):
    """Function to validate that invoice stats schema is correct, it also does value checks in
    runtime (really nice stuff, right here).

    Args:
        coerce (bool): Flag given to determine whether to coerce series to specified type
        strict (bool): Flag given to determine whether or not to accept columns in the
            dataframe that are not in the DataFrame
        nullable (bool): If columns should be nullable or not

    Returns: A pandas DataFrame schema that validates that the types are correct

    """
    return pa.DataFrameSchema(
        {
            INVOICE_STATS_COLUMN_NAMES.get("invoice_median"): pa.Column(
                pa.Float64, nullable=nullable
            ),
            INVOICE_STATS_COLUMN_NAMES.get("invoice_mean"): pa.Column(
                pa.Float64, nullable=nullable
            ),
        },
        index=pa.Index(pa.Int),
        strict=strict,
        coerce=coerce,
    )
