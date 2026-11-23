import pandas as pd

from solution import add_virtual_column


def test_multiplication_has_precedence():
    df = pd.DataFrame(
        {"first_column": [2, 3], "second_column": [4, 5], "third_column": [10, 20]}
    )
    expected = pd.DataFrame(
        {
            "first_column": [2, 3],
            "second_column": [4, 5],
            "third_column": [10, 20],
            "result": [42, 103],
        }
    )
    assert add_virtual_column(
        df, "first_column + second_column * third_column", "result"
    ).equals(expected)


def test_chained_multiplication_and_subtraction():
    df = pd.DataFrame({"a": [2], "b": [3], "c": [4], "d": [5]})
    result = add_virtual_column(df, "a * b * c - d", "result")
    assert result["result"].tolist() == [19]


def test_does_not_modify_original_frame():
    df = pd.DataFrame({"a": [1], "b": [2]})
    add_virtual_column(df, "a + b", "result")
    assert list(df.columns) == ["a", "b"]


def test_invalid_expressions_return_empty_frame():
    df = pd.DataFrame({"a": [1], "b": [2]})
    for role in [
        "a +",
        "a + 1",
        "a / b",
        "a + missing",
        "a * * b",
        "a b",
        "",
    ]:
        assert add_virtual_column(df, role, "result").empty


def test_invalid_labels_return_empty_frame():
    df = pd.DataFrame({"a": [1], "b": [2]})
    assert add_virtual_column(df, "a + b", "result_1").empty
    assert add_virtual_column(df, "a + b", "bad-label").empty

    invalid_columns = pd.DataFrame([[1]], columns=["bad-label"])
    assert add_virtual_column(invalid_columns, "bad-label", "result").empty

    duplicate_columns = pd.DataFrame([[1, 2]], columns=["a", "a"])
    assert add_virtual_column(duplicate_columns, "a", "result").empty
