# DOCUMENT_MARKUP_AUDIT.md

Scanned manuscript_final_clean.docx and manuscript_final_inline_figures.docx
for residue: "**", "__", "TODO", "XXX", "PLACEHOLDER", "Figure S", "Table S",
"Supplement", bracketed comments, tracked-changes markers (w:ins/w:del in
document.xml), comments.xml — none found.
- No raw internal column names in prose or tables: E_h2o, frac_sed,
  p_top5_mean, rank_abs_med, u_ppm, th_ppm all absent (TESTLBL/LBL label maps
  in 07_manuscript.py rename them to reader-facing names, e.g. "leave out
  layer: WEH").
VERDICT: PASS.
