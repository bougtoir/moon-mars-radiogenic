# FINAL_HOSTILE_REVIEW.md

20-line hostile review of the final integrated manuscript (2026-10-28).

1. "Mars ranking is unstable because Th is a weak U proxy." — Addressed:
   stated as the central asymmetry (abstract, 2.4, 4.3); claims scoped to
   prospectivity ranking, not deposits.
2. "Geometric mean is arbitrary." — Battery tests additive, rank-sum,
   bottleneck (Tables 5/A1); ordering survives except under the deliberately
   degenerate bottleneck (declared: J5~0.04 Moon).
3. "Spatial autocorrelation inflates significance." — No inferential tests
   used; Moran I reported descriptively (2.11); rationale stated.
4. "WEH is present-day hydrogen, not Noachian evidence." — Reframed as
   hydrologic-context layer; exclusion sensitivity shown (rho 0.839, J5 0.554):
   weakening reported, Mars>Moon ordering persists.
5. "Missing-data handling is silent." — 2.11 quantifies missingness
   (2 lunar cells; 124 Th / 17 K Mars) and states "unobserved contributes no
   evidence".
6. "Grid resolution is arbitrary." — 10-deg pass reproduces rho within 0.005
   (Table 5); pseudo-resolution critique addressed in intro and 4.4.
7. "Candidate regions look like deposit claims." — Language audited: only
   "candidate regions / prioritisation inputs / exploration priority"; no
   deposit/reserve/mineability/economic language anywhere.
8. "Top-decile ISRU shift is a model artifact." — Framed as magnitude of the
   accessibility question (4.5); flagged as proxy, not engineering model.
9. "Moon result is trivial (PKT recovery)." — Presented explicitly as a
   sanity anchor/validation, not a novel finding (3.4, abstract).
10. "MC weights are Dirichlet-arbitrary." — Stated as model-uncertainty
    propagation, not probability of occurrence (2.10, Fig 7 caption).
11. "Uncited references / dangling cites." — Audit: all 67 refs cited; all
    in-text cites resolve (REFERENCE_VERIFICATION).
12. "Figure/table citation order." — Verified strictly increasing; Fig 3f
    cite relocated to fix order (FIGURE_TABLE_CITATION_AUDIT).
13. "Hardcoded numbers." — Full audit; three hardcoded result literals found
    and converted to computed f-strings (FINAL_HARDCODE_AUDIT).
14. "Supplement orphaning." — No supplement remains; crosswalk complete
    (SUPPLEMENT_INTEGRATION_AUDIT); all S-numbered references removed.
15. "Reproducibility claim unverifiable." — Clean public-clone reproduction
    run performed; all headline outputs identical
    (PUBLIC_CODE_REPRODUCTION).
16. "Robustness CSV rows duplicated." — Defect found in 03_models.py concat
    idiom; fixed; canonical 39-row file unaffected.
17. "J5 nondeterminism." — Two J5 values differ <=0.014 across platforms via
    top-5% boundary ties; declared in reproduction report; rho identical.
18. "No source URLs for data." — DATA_ACQUISITION.md ledger written with all
    URLs; ODY server-side re-issue documented.
19. "Negative results buried." — Bottleneck collapse and leave-S-out
    rho=0.169 explicitly reported in 3.6 prose and Tables 5/A1.
20. "Manuscript hygiene." — OMML math only, no Unicode superscripts, no
    markup residue, 30 clean PDF pages, 6 readable tables, figure-first-
    citation order valid.

VERDICT: SUBMIT.
