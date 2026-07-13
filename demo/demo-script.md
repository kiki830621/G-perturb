# G-perturb — 3-minute demo voiceover (read-aloud script)

> **How to use:** record screen-capture of the on-screen items (figures / web demo / a live terminal run)
> and read the **VOICEOVER** lines verbatim. Pacing is calibrated to ~150 words/min; the whole script is
> ~425 words ≈ 2:50, leaving ~10 s of breathing room under the 3:00 cap.
>
> **Honesty rule (binding):** say Sol *blocked* the design and I *worked through* the holes — never
> "withstood Sol" or "certified / approved." The repo shows the blocked verdict and the resolutions; the
> claim and the evidence must match.
>
> **Attribution (say it right):** issue-driven development (IDD) and parallel-ai-agents are *my own*
> open-source Claude Code plugins, not built-in features.

---

### 0:00–0:20 · Problem  (~48 words)

**ON SCREEN:** a Perturb-seq volcano plot; zoom on a "top hit" flagged as coming from a single guide/donor.

**VOICEOVER:**
> "Perturb-seq screens rank drug targets by how strongly a perturbation changes gene expression. But a hit
> that shows up in just one guide, or one donor, might be measurement noise. Pick that as a drug target,
> and you've bet on an artifact."

---

### 0:20–0:40 · Approach  (~44 words)

**ON SCREEN:** the crossed design Target × Guide × Donor × Condition; the phrase "dependability, not effect size."

**VOICEOVER:**
> "G-perturb re-ranks CD4 T-cell targets by whether the readout is *dependable* — using generalizability
> theory, a measurement framework from psychometrics. It asks one question: would this effect hold up with
> another guide, another donor, another cell state?"

---

### 0:40–1:20 · The process — why you can trust it  (~95 words) ← the memorable beat; hold it a touch longer

**ON SCREEN:** a GitHub issue list (each issue a scientific decision) → the GPT-5.6 Sol verdict card reading **BLOCKED** + 11 findings (3 P0) → resolution issues ticking off. (Fig 5.)

**VOICEOVER:**
> "Here's what makes it trustworthy. Every scientific decision — which estimator, which threshold, and why —
> I filed as a GitHub issue, using an issue-driven-development workflow I built and open-sourced as a Claude
> Code plugin. That auditable ledger became the input to a red-team: I handed it to a *competing* frontier
> model, GPT-5.6 Sol. Sol didn't rubber-stamp it — it **blocked** the design and found *eleven* real
> methodological holes, three critical. I worked through each one with Claude, then cross-verified across
> models. One workflow: decide and document, get torn apart, repair."

---

### 1:20–1:50 · Signal under noise  (~66 words)

**ON SCREEN:** before/after bar "40 genes → 7,674 genes"; caption "measurement noise removed via NTC controls." (Fig 1.)

**VOICEOVER:**
> "And the payoff is a real finding. The raw decomposition says only **forty** genes carry reliable target
> signal. But that's an artifact — pseudobulk built from a handful of cells inflates the noise. Estimate
> that noise from the non-targeting controls, subtract it, and the true count is **seven thousand six
> hundred** — forty-two percent of the genome. The dependable hits were hidden under measurement noise."

---

### 1:50–2:08 · Guide-limited  (~44 words)

**ON SCREEN:** the Eρ² surface (guides × donors); callout "2 guides cap at 0.53 — add guides, not donors." (Fig 2.)

**VOICEOVER:**
> "A D-study also tells you how to make the readouts *better*. The bottleneck is guides, not donors — with
> two guides per gene you can never reach seventy-percent reliability, no matter how many donors you add. To
> improve a screen: add guides."

---

### 2:08–2:33 · The ranking reshuffles  (~60 words)

**ON SCREEN:** two ranked lists (effect-only vs dependability-weighted) with arrows; RPS3 jumping #79 → #4. (Fig 3.)

**VOICEOVER:**
> "And the ranking itself is the deliverable. Rank each target by effect times a dependability coefficient —
> combining guide and donor reproducibility the *right* way, errors adding. **Fifty of the top hundred**
> targets by raw effect drop out once you weight by dependability. A reproducible target like RPS3 climbs
> from seventy-ninth to fourth. That reshuffle is the whole point."

---

### 2:33–2:52 · Reliable only when activated  (~45 words) ← the biology climax

**ON SCREEN:** per-state R_dep bars for CD3D / CD3G / CD247 / ZAP70 — near-zero at Rest, tall at Stim. (Fig 4.)

**VOICEOVER:**
> "And here's the sharpest test. Slice dependability by activation state, and the method recovers biology it
> was never told: the T-cell-receptor module — the CD3 complex, ZAP70, LAT — is reliably measurable *only*
> in activated cells. No gene labels went in; the pathway came out."

---

### 2:52–3:00 · Close  (~21 words)

**ON SCREEN:** the ranked target table; repo (Apache-2.0, reproducible) + the bioRxiv "submitted" status; "Built with Claude."

**VOICEOVER:**
> "G-perturb: re-ranking drug targets by measurement dependability — a frozen, cross-model-audited analysis
> you can rerun end to end, now submitted to bioRxiv. Built with Claude."

---

## Production notes

- **Show it working (one live moment).** At the **close (2:52–3:00)**, instead of a static table, screen-record
  the terminal actually running `python analysis/resolution/realdata/per_target_ranking.py` and the ranking
  regenerating, then cut to the table — 3–5 s that prove the pipeline is real, not slideware. (Or live-scroll
  the web demo page.)
- **Keep the Sol panel (0:40–1:20) on screen a beat longer** — it is the memorable, surprising part.
- **Total ≈ 2:50 at 150 wpm.** If a beat runs long, trim the D-study line first (it is the most compressible);
  never cut the honesty framing in the Sol beat.
- **Word counts per beat** (for re-timing): 48 / 44 / 95 / 66 / 44 / 60 / 45 / 25 ≈ 427 words (~2:51 at 150 wpm — still inside the 3:00 cap).
