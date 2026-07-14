# G-perturb — read-aloud script (voiceover only)

~427 words · ~2:51 at 150 wpm · inside the 3:00 cap. Read the lines aloud; emphasis marks (`*word*`, `**number**`) are stress cues, and the bracketed headers are pacing markers, not spoken.

---

**[0:00–0:20 · Problem]**

Perturb-seq screens rank drug targets by how strongly a perturbation changes gene expression. But a hit that shows up in just one guide, or one donor, might be measurement noise. Pick that as a drug target, and you've bet on an artifact.

**[0:20–0:40 · Approach]**

G-perturb re-ranks CD4 T-cell targets by whether the readout is *dependable* — using generalizability theory, a measurement framework from psychometrics. It asks one question: would this effect hold up with another guide, another donor, another cell state?

**[0:40–1:20 · The process]**

Here's what makes it trustworthy. Every scientific decision — which estimator, which threshold, and why — I filed as a GitHub issue, using an issue-driven-development workflow I built and open-sourced as a Claude Code plugin. That auditable ledger became the input to a red-team: I handed it to a *competing* frontier model, GPT-5.6 Sol. Sol didn't rubber-stamp it — it **blocked** the design and found *eleven* real methodological holes, three critical. I worked through each one with Claude, then cross-verified across models. One workflow: decide and document, get torn apart, repair.

**[1:20–1:50 · Signal under noise]**

And the payoff is a real finding. The raw decomposition says only **forty** genes carry reliable target signal. But that's an artifact — pseudobulk built from a handful of cells inflates the noise. Estimate that noise from the non-targeting controls, subtract it, and the true count is **seven thousand six hundred** — forty-two percent of the genome. The dependable hits were hidden under measurement noise.

**[1:50–2:08 · Guide-limited]**

A D-study also tells you how to make the readouts *better*. The bottleneck is guides, not donors — with two guides per gene you can never reach seventy-percent reliability, no matter how many donors you add. To improve a screen: add guides.

**[2:08–2:33 · The ranking reshuffles]**

And the ranking itself is the deliverable. Rank each target by effect times a dependability coefficient — combining guide and donor reproducibility the *right* way, errors adding. **Fifty of the top hundred** targets by raw effect drop out once you weight by dependability. A reproducible target like RPS3 climbs from seventy-ninth to fourth. That reshuffle is the whole point.

**[2:33–2:52 · Reliable only when activated]**

And here's the sharpest test. Slice dependability by activation state, and the method recovers biology it was never told: the T-cell-receptor module — the CD3 complex, ZAP70, LAT — is reliably measurable *only* in activated cells. No gene labels went in; the pathway came out.

**[2:52–3:00 · Close]**

G-perturb: re-ranking drug targets by measurement dependability — a frozen, cross-model-audited analysis you can rerun end to end, now submitted to bioRxiv. Built with Claude.
