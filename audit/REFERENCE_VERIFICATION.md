# REFERENCE_VERIFICATION.md

Date: 2026-10-28. Source: REFS list in scripts/07_manuscript.py (67 entries;
the docx prints all of them under "References").

## DOI check
63 of 67 entries carry a DOI. Each was resolved against the Crossref API
(https://api.crossref.org/works/{doi}); all 63 returned 200 with matching
titles. Spot-checked title correspondence on the returned records — all
consistent (e.g. 10.1016/j.icarus.2015.07.039 -> "A new lunar digital
elevation model from LOLA and SELENE Terrain Camera").

## Entries without DOI (4) — verified as legitimate non-DOI publications
- Bonham-Carter, Agterberg & Wright (1990), GSC Paper 89-9 — book chapter, no DOI. OK.
- Fergason, Hare & Mayer (2017), HRSC-MOLA blended DEM — USGS product page. OK.
- Fortezzo, Spudis & Harrel (2020), Release of the digital Unified Geologic
  Map of the Moon — USGS SIM 3464, product pages carry DOIs for the SIM
  itself; the release citation is the correct grey-literature form. OK.
- McCuaig & Hronsky (2010), mineral-systems chapter — Geological Survey of
  Western Australia Report 113. OK.

## Bidirectional citation check (docx body vs References)
Programmatic scan of manuscript_final_clean.docx: every "(Author ...)" in-body
citation resolves to a reference-list entry; every reference-list first author
appears at least once in the body.
- Initially 6 reference entries were uncited (Connelly, Diez, El Maarry,
  Khan, Page, Spohn) -> FIXED 2026-10-28: cited at their natural points
  (Spohn 1991 with Hauck & Phillips; Diez/El Maarry/Page with the Odyssey GRS
  analyses in Section 3.2; Khan 2004 and Connelly et al. 2022 with the
  lunar thermal-evolution sentence). Post-fix scan: zero uncited references,
  zero dangling citations.

VERDICT: PASS.
