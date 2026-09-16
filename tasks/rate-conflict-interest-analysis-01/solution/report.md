# Alderbrook Systems Inc. — Facility #ASI-TL-4021: 12-Month Interest Expense Projection

## 1. Executive summary — flagging a source conflict before proceeding

**The two source documents provided for this analysis state two different,
mutually exclusive interest rates for the same facility, and nothing in
the materials resolves which one governs.** The executed Credit Agreement
(Section 2.06(b)) fixes the Applicable Margin at **3.50% (350 bps)** for
the life of the facility, explicitly with no pricing grid and no
automatic adjustment mechanism — a change would require a written
amendment under Section 9.02. No such amendment is included in, or
referenced by, either document. Yet the lender's own Rate Reset Notice,
dated August 28, 2026, states the "current" Applicable Margin is **3.75%
(375 bps)**, with no explanation, no reference to an amendment, and no
indication of why a margin the Credit Agreement says is fixed would have
changed.

**This is not a computation this analysis can resolve on its own.** Both
documents are facially authoritative — one is the governing legal
agreement, the other is a formal notice from the same lender's loan
servicing group — and neither states or implies that it supersedes the
other. Rather than pick one rate and present a single confident number,
this report computes the requested 12-month projection under **both**
stated rates and recommends the discrepancy be confirmed with Meridian
Capital Partners (and reviewed with legal/credit) before either figure is
used for budgeting or booked as the expected interest expense.

| | Under Credit Agreement rate (350 bps) | Under Rate Reset Notice rate (375 bps) |
|---|---:|---:|
| **Total 12-month interest expense** | **$208,750.00** | **$215,000.00** |
| Difference from the other scenario | — | **+$6,250.00 (+3.0%)** |
| Month 12 ending principal balance | $1,777,777.77 (identical under both — scheduled amortization is rate-independent) | |

## 2. Nature of the conflict

| | Credit Agreement (Section 2.06) | Rate Reset Notice |
|---|---|---|
| Document type | Executed legal agreement | Lender servicing correspondence |
| Date | March 3, 2026 (execution) | August 28, 2026 |
| Stated Applicable Margin | 3.50% (350 bps), fixed | 3.75% (375 bps) |
| Basis for the figure stated | Contractual term, no pricing grid | Not explained |
| Amendment referenced? | N/A (states margin is fixed absent a Section 9.02 amendment) | No |

The Credit Agreement is explicit that its 350 bps margin is not subject
to any automatic adjustment and can only change via a signed amendment —
and the excerpt states affirmatively that no amendments, waivers, or side
letters exist as of its date. The Rate Reset Notice, issued nearly six
months later by the same lender's servicing group, states a different
figure with no cross-reference to an amendment, a pricing grid trigger,
or any other basis. Absent a document that actually reconciles these two
(an executed amendment, a pricing grid that would explain a leverage- or
rating-based step-up, or a corrected notice), there is no principled way
to determine which figure is currently correct from the materials
provided.

## 3. 12-month interest expense schedule, both scenarios

All interest calculated monthly on the outstanding balance as of the
first day of the month, at a flat assumed 3-month Term SOFR of 4.85% per
`analysis_request.md`, plus the respective Applicable Margin. Scheduled
principal amortization of $111,111.11/month applies identically under
both scenarios (amortization is unaffected by which margin is correct).

| Month | Balance (start) | Interest @ 350 bps (CA) | Interest @ 375 bps (Notice) |
|---:|---:|---:|---:|
| 1 | $3,111,111.09 | $21,648.15 | $22,296.30 |
| 2 | $2,999,999.98 | $20,875.00 | $21,500.00 |
| 3 | $2,888,888.87 | $20,101.85 | $20,703.70 |
| 4 | $2,777,777.76 | $19,328.70 | $19,907.41 |
| 5 | $2,666,666.65 | $18,555.56 | $19,111.11 |
| 6 | $2,555,555.54 | $17,782.41 | $18,314.81 |
| 7 | $2,444,444.43 | $17,009.26 | $17,518.52 |
| 8 | $2,333,333.32 | $16,236.11 | $16,722.22 |
| 9 | $2,222,222.21 | $15,462.96 | $15,925.93 |
| 10 | $2,111,111.10 | $14,689.81 | $15,129.63 |
| 11 | $1,999,999.99 | $13,916.67 | $14,333.33 |
| 12 | $1,888,888.88 | $13,143.52 | $13,537.04 |
| **Total** | | **$208,750.00** | **$215,000.00** |

## 4. Recommendation

Do not finalize the budget cycle's interest expense line using either
figure in isolation. Specifically:

1. **Escalate the discrepancy to Treasury and Legal** — someone needs to
   confirm with Meridian Capital Partners directly whether an amendment
   to the Applicable Margin was executed and simply not included in this
   excerpt, or whether the Rate Reset Notice was issued in error.
2. **Until resolved, budget using a range**, not a point estimate:
   $208,750–$215,000 for the 12-month period (a $6,250 spread, roughly
   3.0% of the lower figure) — not immaterial for budgeting purposes, and
   the spread would compound further at renewal or if it reflects a
   genuine, undocumented margin change that should also be corrected
   going forward.
3. **Do not assume the more recent document controls** by default. In
   this case the more recent document (the Rate Reset Notice) is
   informal servicing correspondence, not a contract amendment — under
   Section 9.02 of the Credit Agreement, it has no independent authority
   to change the Applicable Margin regardless of its date. That said,
   this report does not conclude the Credit Agreement's rate is
   definitely the one currently being billed — only that the Notice
   alone does not establish that it is.

## Assumptions and limitations

- The $3,111,111.09 starting balance and the 4.85% flat SOFR assumption
  are taken as given per `analysis_request.md` and are not themselves in
  dispute between the two source documents.
- This analysis does not attempt to determine which rate is "actually"
  being billed — that requires information (a signed amendment, or
  confirmation from the lender) not present in the provided materials.
- Both scenarios' interest schedules were computed independently and
  cross-checked to confirm they differ only in the applied margin, not in
  any other assumption (identical starting balance, identical
  amortization schedule, identical month-12 ending balance of
  $1,777,777.77 under both).
