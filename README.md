# Virtual columns in a pandas DataFrame

My solution for the Cloudfide recruitment task. `solution.py` has the `add_virtual_column` function, and `pipeline.py` uses it to clean `sales.csv` and write `revenue_by_region.csv`.

## Running it

I used Python 3.14 with pandas 3.1, but anything 3.10+ should work.

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas pytest

python pipeline.py
python -m pytest
```

The pipeline finds `sales.csv` relative to its own location, so it doesn't matter which directory you run it from. It writes `revenue_by_region.csv` in the same place. Pytest picks up the supplied `test_virtual_column.py` along with my `test_solution.py` and `test_pipeline.py`.

## Assumptions I made

- Discount is an amount off the whole line, not a percentage, so revenue is `quantity * unit_price - discount`. An empty discount means zero.
- Every product has a single price in this file, so a missing price was filled from the other rows for that product (21.00 for Printer paper, 89.00 for Keyboard).
- `"59,00"` means 59.00, and `1 762` means 1762 units. Comma is the decimal separator; space is the thousands separator.
- The six negative quantities look like returns, so I kept them and let them produce negative revenue. The `TOTAL` footer includes them as-is, and there's no return-specific field in the file.
- Duplicate order IDs are export duplicates. I kept the first copy of each.
- Region names only differ by casing or stray whitespace, so I trimmed them and used title case.
- Dates are all valid and in the same format. I left them as strings since they aren't used in the calculation.

## What was wrong with `sales.csv`

There are 1505 real order rows, plus a header repeated at line 753 and a `TOTAL` footer at the end. The issues I found:

- The `Quantity ` header has a trailing space. I stripped all column names.
- The repeated header and the footer aren't orders, so both were removed.
- 15 region values needed fixing: 8 had stray spaces (`west  `, ` North`, `Central `), 7 were wrong case (`north`, `EAST`, `south`). After trimming and title-casing there are five regions.
- 7 unit prices use a comma decimal (`"59,00"`), and 4 are empty. Commas became dots; the empty ones were filled per product.
- 4 quantities use spaces as thousands separators: `1 762`, `1 745`, `1 371`, `1 427`.
- 963 discounts are empty (959 after deduplication). Those became 0.00.
- 6 quantities are negative: -2, -4, -5, -3, -3, -2. Kept as returns, as above.
- 5 rows are exact duplicates (SO-10305, SO-10822, SO-10966, SO-11240, SO-11405). I dropped the extra copy, leaving 1500 unique orders.

I didn't find any invalid dates, unknown products, negative discounts, or discounts larger than the line value. After cleaning, the numeric columns have no missing values.
