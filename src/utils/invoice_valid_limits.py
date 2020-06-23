from decimal import Decimal, DecimalException
from typing import Optional, Union

from src.utils.constants import INVOICE_LIMIT, MAX_INVOICE_VALUE, MIN_INVOICE_VALUE


def parse_to_decimal(value: Union[Decimal, float, int, str]) -> Decimal:
    """Function to make sure values are always in Decimal format, for clarity. Put inside
    this function since it is being called in many places, ensure that it is always the same.

    Args:
        value (Union[Decimal, float, int, str]): Given value to be parsed

    Returns (Decimal): If already Decimal, do nothing, else convert int or float to Decimal

    """
    try:
        return Decimal(value) if isinstance(value, (float, int, str)) else value

    except DecimalException as decimal_exception:
        raise decimal_exception


def valid_max_invoice_val(max_invoice_value: Optional[Union[Decimal, float]]) -> Decimal:
    """Function to validate the max invoice value, constraint is that it can never be more
    than MAX_INVOICE_VALUE set in `.env`.

    Args:
        max_invoice_value (Optional[Union[Decimal, float]]): Given max_invoice_value

    Returns (Decimal): Given max_invoice_value, if null then MAX_INVOICE_VALUE, if max_invoice_value
        is greater than MAX_INVOICE_VALUE (200 million), or greater than or equal to
        MIN_INVOICE_VALUE (1) oterwise return new max_invoice_value

    """
    if max_invoice_value is None:
        return MAX_INVOICE_VALUE

    max_invoice_value = parse_to_decimal(value=max_invoice_value)

    return (
        max_invoice_value
        if MAX_INVOICE_VALUE >= max_invoice_value >= MIN_INVOICE_VALUE
        else MAX_INVOICE_VALUE
    )


def valid_min_invoice_val(min_invoice_value: Optional[Union[Decimal, float]]) -> Decimal:
    """Function to validate the min invoice value, constraint is that it can never be less
    than MIN_INVOICE_VALUE set in `.env`.

    Args:
        min_invoice_value (Optional[Union[Decimal, float]]): Given min_invoice_value

    Returns (Decimal): Given max_invoice_value, if null then MAX_INVOICE_VALUE, if max_invoice_value
        is greater than MAX_INVOICE_VALUE (200 million), or greater than or equal to
        MIN_INVOICE_VALUE (1) oterwise return new max_invoice_value

    """

    if min_invoice_value is None:
        return MIN_INVOICE_VALUE

    min_invoice_value = parse_to_decimal(value=min_invoice_value)

    return (
        min_invoice_value
        if MIN_INVOICE_VALUE <= min_invoice_value <= MAX_INVOICE_VALUE
        else MIN_INVOICE_VALUE
    )


def valid_invoice_limit(invoice_limit: Optional[Union[Decimal, int]]) -> Decimal:
    """Function to validate the limit value, constraint is that it can never be greater than
    the INVOICE_LIMIT (20 million invoices) and it needs to be greater than 1, meaning there must be
    at least 1 invoice.

    Args:
        invoice_limit (Optional[Union[Decimal, int]]): Given invoice_limit

    Returns (Decimal): Given invoice_limit, if the limit is invalid or None, it will revert to the
        default value.

    """
    if invoice_limit is None:
        return INVOICE_LIMIT

    invoice_limit = parse_to_decimal(value=invoice_limit)
    return invoice_limit if INVOICE_LIMIT >= invoice_limit > 0 else INVOICE_LIMIT
