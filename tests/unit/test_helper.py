from decimal import Decimal, DecimalException

import pytest

from src.utils.constants import INVOICE_LIMIT, MAX_INVOICE_VALUE, MIN_INVOICE_VALUE
from src.utils.invoice_valid_limits import (
    parse_to_decimal,
    valid_invoice_limit,
    valid_max_invoice_val,
    valid_min_invoice_val,
)


@pytest.mark.parametrize(
    "value",
    [1234, 12391239319.0000, MAX_INVOICE_VALUE, 1, 292929, "123123", "-123", -12312341.0123123],
)
def test_parse_to_decimal_success(value):
    parsed_decimal = parse_to_decimal(value=value)
    assert parsed_decimal == Decimal(value)


@pytest.mark.parametrize("value", ["abc",])
def test_parse_to_decimal_failure(value):
    with pytest.raises(DecimalException):
        parse_to_decimal(value=value)


@pytest.mark.parametrize("max_invoice_value", [MAX_INVOICE_VALUE, 123.0, Decimal(123000000)])
def test_valid_max_invoice_val(max_invoice_value):
    max_value = valid_max_invoice_val(max_invoice_value=max_invoice_value)
    assert max_value == max_invoice_value


@pytest.mark.parametrize("max_invoice_value", [0, -123.0, Decimal(-123000000), "0", None])
def test_invalid_max_invoice_val_revert_to_default(max_invoice_value):
    max_value = valid_max_invoice_val(max_invoice_value=max_invoice_value)
    assert max_value == MAX_INVOICE_VALUE


@pytest.mark.parametrize("min_invoice_value", [MIN_INVOICE_VALUE, 1, Decimal(1000000)])
def test_valid_min_invoice_val(min_invoice_value):
    min_value = valid_min_invoice_val(min_invoice_value=min_invoice_value)
    assert min_value == min_invoice_value


@pytest.mark.parametrize("min_invoice_value", [-23423424, Decimal(-123000000), "0", None])
def test_invalid_min_invoice_val_revert_to_default(min_invoice_value):
    min_value = valid_min_invoice_val(min_invoice_value=min_invoice_value)
    assert min_value == MIN_INVOICE_VALUE


@pytest.mark.parametrize("invoice_limit", [Decimal(12345), INVOICE_LIMIT, 19000000, 1.0])
def test_valid_invoice_limit(invoice_limit):
    limit_value = valid_invoice_limit(invoice_limit=invoice_limit)
    assert limit_value == invoice_limit


@pytest.mark.parametrize("invoice_limit", [-23423424, Decimal(-123000000), "0", None])
def test_invalid_invoice_limit_val_revert_to_default(invoice_limit):
    limit_value = valid_invoice_limit(invoice_limit=invoice_limit)
    assert limit_value == INVOICE_LIMIT
