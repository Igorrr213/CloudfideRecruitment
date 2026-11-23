import pandas as pd
import pytest

import pipeline
from solution import add_virtual_column

EXPECTED_TOTALS = {
    "Central": 515824.67,
    "East": 442219.91,
    "North": 665897.52,
    "South": 504036.04,
    "West": 442268.89,
}


@pytest.fixture(scope="module")
def sales():
    return pipeline.clean_sales(pipeline.load_sales())


def test_header_whitespace_is_handled(sales):
    raw = pipeline.load_sales()
    assert "Quantity " in raw.columns
    assert "quantity" in sales.columns


def test_header_footer_and_duplicates_are_removed(sales):
    assert len(sales) == 1500
    assert not sales["order_id"].str.startswith("TOTAL").any()
    assert sales["order_id"].is_unique


def test_region_values_are_normalized(sales):
    assert set(sales["region"].unique()) == {
        "North",
        "South",
        "East",
        "West",
        "Central",
    }
    by_id = sales.set_index("order_id")["region"]
    assert by_id["SO-10058"] == "West"
    assert by_id["SO-10476"] == "North"
    assert by_id["SO-10640"] == "East"
    assert by_id["SO-10845"] == "South"
    assert by_id["SO-11022"] == "Central"


def test_numbers_are_parsed(sales):
    by_id = sales.set_index("order_id")
    assert by_id.loc["SO-10251", "quantity"] == 1762
    assert by_id.loc["SO-10137", "unit_price"] == 59.00
    assert by_id.loc["SO-10610", "unit_price"] == 21.00
    assert by_id.loc["SO-11099", "unit_price"] == 21.00
    assert by_id.loc["SO-11350", "unit_price"] == 89.00
    assert by_id.loc["SO-11477", "unit_price"] == 89.00
    assert by_id.loc["SO-10001", "discount"] == 398.40
    assert by_id.loc["SO-10002", "discount"] == 0.00
    assert sales.isna().sum().sum() == 0


def test_negative_quantities_are_kept(sales):
    assert sales.set_index("order_id").loc["SO-10421", "quantity"] == -2


def test_revenue_uses_add_virtual_column():
    df = pd.DataFrame({"quantity": [2], "unit_price": [10.0], "discount": [5.0]})
    expected = add_virtual_column(df, "quantity * unit_price - discount", "revenue")
    pd.testing.assert_frame_equal(pipeline.add_revenue(df), expected)


def test_summarize_revenue_groups_by_region():
    df = pd.DataFrame(
        {
            "region": ["West", "East", "West"],
            "revenue": [10.0, 20.0, 5.0],
        }
    )
    result = pipeline.summarize_revenue(df)
    assert result.to_dict("records") == [
        {"region": "East", "revenue": 20.0},
        {"region": "West", "revenue": 15.0},
    ]


def test_run_pipeline_writes_expected_csv(tmp_path):
    output = tmp_path / "revenue_by_region.csv"
    summary = pipeline.run_pipeline(output_path=output)
    written = pd.read_csv(output)

    pd.testing.assert_frame_equal(written, summary.round(2))
    assert dict(zip(written["region"], written["revenue"])) == EXPECTED_TOTALS


def test_committed_output_matches_pipeline():
    written = pd.read_csv(pipeline.REVENUE_PATH)
    assert dict(zip(written["region"], written["revenue"])) == EXPECTED_TOTALS
