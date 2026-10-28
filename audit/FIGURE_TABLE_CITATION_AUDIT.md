# FIGURE_TABLE_CITATION_AUDIT.md

Scanned manuscript_final_clean.docx programmatically.

First-citation positions (character offsets in body text):
- Figures 1-7: [12808, 21394, 22002, 22977, 23315, 24529, 25117] -> strictly
  increasing, PASS.
- Tables 1-5 + A1: [13557, 16334, 22968, 24369, 25766, 25888] -> increasing, PASS.
- Figure A1 cited in Section 3.6 ("Appendix A (Table A1, Figure A1)") and in
  the Figure 7 caption — PASS.
- Every figure/table is cited at least once in text: PASS (no orphans).
- Issue found and fixed during audit: "Figure 3f" (knowledge-completeness
  panel) was first cited in Section 2.11 before Figure 2 (Section 3.1) ->
  moved to Section 3.2 on 2026-10-28; order now correct.
VERDICT: PASS.
