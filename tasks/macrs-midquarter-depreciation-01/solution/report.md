# Meridian Fabrication Works LLC — 2027 Fixed Asset Depreciation Analysis

## 1. Executive summary

Meridian placed five pieces of 5-year MACRS property in service during tax
year 2027, totaling **$250,000** of depreciable basis. Because **52.00%**
of that basis ($130,000 of $250,000) was placed in service in the fourth
quarter — above the IRS's 40% threshold — **the mid-quarter convention
applies to all five assets for tax year 2027**, not the default half-year
convention. Under mid-quarter, each asset uses the percentage table for
the specific calendar quarter it was placed in service, for every year of
its six-year recovery period (not only its first year).

- **Total Year 1 (2027) depreciation: $38,500.00.**
- **Total Year 2 (2028) depreciation: $84,600.00.**
- **Total depreciation over the full six-year recovery period: $250,000.00**
  — exactly equal to the aggregate cost basis, as it must be.

## 2. Why the mid-quarter convention applies

| Asset | Placed in service | Quarter | Cost basis |
|---|---|:---:|---:|
| EQ-101 | 2027-02-14 | Q1 | $50,000 |
| EQ-102 | 2027-05-22 | Q2 | $40,000 |
| EQ-103 | 2027-08-09 | Q3 | $30,000 |
| EQ-104 | 2027-11-03 | Q4 | $90,000 |
| EQ-105 | 2027-12-18 | Q4 | $40,000 |
| **Total** | | | **$250,000** |

Q4 basis = $90,000 + $40,000 = **$130,000**. $130,000 / $250,000 =
**52.00%**, which exceeds the IRS's 40% threshold (IRC §168(d)(3);
Publication 946). Because this test is measured against the *aggregate*
basis of all personal property placed in service during the year, it
applies to **every** asset placed in service in 2027 — including EQ-101,
EQ-102, and EQ-103, which were placed in service well before Q4 and, in
isolation, would look like ordinary half-year-convention candidates.

## 3. Depreciation by asset

Regular MACRS, GDS, 200% declining balance, 5-year recovery period, no
Section 179 election, no bonus depreciation. Under mid-quarter, each
asset's own placed-in-service quarter determines which percentage table
governs **all six years** of its recovery — not just Year 1.

| Asset | Quarter | Year 1 % | Year 1 $ | Year 2 % | Year 2 $ |
|---|:---:|---:|---:|---:|---:|
| EQ-101 | Q1 | 35.00% | $17,500.00 | 26.00% | $13,000.00 |
| EQ-102 | Q2 | 25.00% | $10,000.00 | 30.00% | $12,000.00 |
| EQ-103 | Q3 | 15.00% | $4,500.00 | 34.00% | $10,200.00 |
| EQ-104 | Q4 | 5.00% | $4,500.00 | 38.00% | $34,200.00 |
| EQ-105 | Q4 | 5.00% | $2,000.00 | 38.00% | $15,200.00 |
| **Total** | | | **$38,500.00** | | **$84,600.00** |

Note the reversal for the two Q4 assets: they receive the *smallest*
first-year percentage (5.00%, reflecting only 1.5 months of deemed
service under the mid-quarter averaging convention) but the *largest*
second-year percentage (38.00%) of any quarter, since more of their
depreciable basis remains to be recovered going into Year 2. A solver who
correctly applies the mid-quarter *timing* concept but reverts to the
half-year table for Year 2 (treating mid-quarter as a first-year-only
adjustment) would understate Q4 assets' Year 2 depreciation and misstate
the portfolio total by $4,600.

## 4. Validation

- Every one of the four IRS percentage tables used (half-year Table A-1,
  and mid-quarter Tables A-2 through A-5, all for 5-year property) was
  cross-checked to confirm its six stated percentages sum to exactly
  100.00% — a necessary property of any correctly transcribed MACRS
  table, since the asset must be fully depreciated over its stub recovery
  period. All four pass this check.
- The reported `total_six_year_depreciation_usd` ($250,000.00) equals the
  sum of all five assets' cost bases exactly, confirming no arithmetic
  leakage across the six-year computation.
- Rerunning `solution/solve.py` reproduces `answer.json` byte-for-byte.

## Assumptions and limitations

- All five assets are treated as ordinary 5-year MACRS property (no
  listed-property restrictions, no short tax year, no mid-month
  convention applicable — mid-month applies only to real property, not
  the personal property described here).
- No asset was disposed of during the years covered by this analysis, so
  no mid-year disposal adjustment applies to any year's depreciation.
- Meridian is assumed not to have any other 2027 property acquisitions
  outside the five listed in `asset_register.csv` — the 40% test is
  computed only over the assets actually described in the source data,
  consistent with the stated fact that Meridian made no other 2027
  acquisitions or dispositions.
