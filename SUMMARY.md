# G-perturb — summary

*Reliability-weighted drug-target ranking for CD4+ T-cell Perturb-seq, via generalizability theory.*

G-perturb re-ranks drug targets from a genome-scale CD4+ T-cell Perturb-seq screen by whether each effect is dependable, not just by how large it is. A large transcriptional effect seen in a single guide or a single donor can be measurement noise, and each false lead costs a validation experiment. I treat every perturbation effect as a measurement in a crossed guide-by-donor-by-condition design and use generalizability theory, a framework from psychometrics, to give each target one dependability coefficient, then rank by effect size weighted by dependability.

On the released 44.6 GB pseudobulk this reorders the shortlist: 50 of the top 100 targets by raw effect drop out of the top 100 by dependability. Read within activation states, the coefficient reconstructs the T-cell-receptor module (CD3 complex, ZAP70, LAT) as reliable only in activated cells, with no gene labels supplied. A design study shows the screen is limited by the number of guides, not donors. Every methodological decision was recorded and adversarially red-teamed by a competing model before any result was seen; the analysis regenerates end to end.

## Read more

- **Full paper (PDF):** [`manuscript/main.pdf`](./manuscript/main.pdf) — submitted to bioRxiv (`BIORXIV/2026/738312`, under screening), CC-BY 4.0.
- **Code:** this repository, Apache-2.0. The whole pipeline regenerates every number from one re-run.
- **3-minute demo video:** <https://youtu.be/zBD30nhal64> (slides in [`demo/slides.html`](./demo/slides.html), read-aloud voiceover in [`demo/read-aloud.md`](./demo/read-aloud.md)).
