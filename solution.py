import operator
import re
from functools import reduce

import pandas as pd

_LABEL_PATTERN = re.compile(r"[A-Za-z_]+")
_TOKEN_PATTERN = re.compile(r"[A-Za-z_]+|[+\-*]")
_ALLOWED_ROLE_CHARACTERS = re.compile(r"[A-Za-z_+\-*\s]*")


def _is_valid_label(label: object) -> bool:
    return isinstance(label, str) and _LABEL_PATTERN.fullmatch(label) is not None


def _parse_role(role: object, columns: pd.Index) -> list[str] | None:
    if not isinstance(role, str) or _ALLOWED_ROLE_CHARACTERS.fullmatch(role) is None:
        return None

    tokens = _TOKEN_PATTERN.findall(role)
    if not tokens or len(tokens) % 2 == 0:
        return None

    if "".join(tokens) != re.sub(r"\s+", "", role):
        return None

    for position, token in enumerate(tokens):
        if position % 2 == 0:
            if token not in columns:
                return None
        elif token not in {"+", "-", "*"}:
            return None

    return tokens


def _multiply(factors: list[pd.Series]) -> pd.Series:
    return reduce(operator.mul, factors)


def _evaluate(tokens: list[str], df: pd.DataFrame) -> pd.Series:
    result = None
    sign = 1
    factors = [df[tokens[0]]]

    for position in range(1, len(tokens), 2):
        op = tokens[position]
        column = df[tokens[position + 1]]
        if op == "*":
            factors.append(column)
            continue

        term = _multiply(factors)
        if result is None:
            result = term if sign == 1 else -term
        else:
            result = result + term if sign == 1 else result - term
        sign = 1 if op == "+" else -1
        factors = [column]

    term = _multiply(factors)
    if result is None:
        return term if sign == 1 else -term
    return result + term if sign == 1 else result - term


def add_virtual_column(
    df: pd.DataFrame, role: str, new_column: str
) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        return pd.DataFrame()
    if not _is_valid_label(new_column):
        return pd.DataFrame()
    if not all(_is_valid_label(column) for column in df.columns):
        return pd.DataFrame()
    if not df.columns.is_unique:
        return pd.DataFrame()

    tokens = _parse_role(role, df.columns)
    if tokens is None:
        return pd.DataFrame()

    result = df.copy()
    result[new_column] = _evaluate(tokens, df)
    return result
