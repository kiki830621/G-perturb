# G-perturb — 3-minute demo voiceover (read-aloud script)

> **How to use:** advance the 1920×1080 deck (`demo/slides.html`) beat by beat and read the VOICEOVER lines. Pacing is ~150 words/min; about 440 words ≈ 2:55, just inside the 3:00 cap. Read it plainly, the way you would explain the work to a colleague. No word needs stress.
>
> **Honesty rule (binding):** say Sol *blocked* the design and I *worked through* the issues. Never "withstood Sol" or "certified / approved." The repo shows the blocked verdict and the fixes; the claim and the evidence must match.
>
> **Attribution:** issue-driven development (IDD) is my own open-source Claude Code plugin, not a built-in feature.

---

### 0:00–0:22 · Intro and the problem  (slides 1–2)

**ON SCREEN:** the title slide (name and affiliation), then "Dependability, not effect size."

**VOICEOVER:**
> "I'm Che Cheng, from the Institute of Statistical Science at Academia Sinica, and this is G-perturb. Perturb-seq screens usually rank drug targets by how strongly a perturbation shifts gene expression. But a large effect seen in a single guide, or a single donor, can be measurement noise rather than real biology, and a target picked on that basis may not reproduce."

### 0:20–0:48 · The method  (slide 3)

**ON SCREEN:** the crossed-design chips and the R_dep formula.

**VOICEOVER:**
> "G-perturb ranks targets by whether the readout is dependable, not just by how large it is. I treat each effect as a measurement and borrow generalizability theory, a framework from psychometrics, to ask one question for every target: would this effect hold up with a different guide, a different donor, a different cell state? Combining the guide and donor reliability gives each target a single dependability coefficient."

### 0:48–1:23 · The process  (slide 4)

**ON SCREEN:** the IDD → Sol BLOCKED → resolved cards.

**VOICEOVER:**
> "I also wanted the analysis to be checkable, so every methodological decision, which estimator and which threshold, is recorded as a GitHub issue, through an issue-driven workflow I built as an open-source Claude Code plugin. I gave that record to a different model, GPT-5.6 Sol, and asked it to find problems. It blocked the design and raised eleven issues, three of them critical, which I then worked through with Claude and cross-checked across models."

### 1:23–1:48 · Ranking, RQ1  (slide 5)

**ON SCREEN:** the ranking reshuffle plot, with RPS3 circled at #79 → #4.

**VOICEOVER:**
> "The first question is whether ranking by dependability actually changes the shortlist. It does. Once you weight effect size by the dependability coefficient, fifty of the top hundred targets by raw effect drop out of the top hundred by dependability. Reproducible targets that effect size underrates move up; RPS3, for one, goes from seventy-ninth to fourth."

### 1:48–2:12 · Context, RQ2  (slide 6)

**ON SCREEN:** the per-state dependability bars for the TCR module.

**VOICEOVER:**
> "The second question is about context. Analysed within each activation state, dependability picks out the T-cell-receptor module, the CD3 complex with ZAP70 and LAT, as reliably measurable only in activated cells. The method was given no gene labels, so recovering a known pathway this way is a good sign it is tracking real biology."

### 2:12–2:32 · Overall dependability, RQ3  (slide 7)

**ON SCREEN:** the Eρ² ≈ .44 number slide.

**VOICEOVER:**
> "The third question is how dependable the screen is overall. On the representative genes the generalizability coefficient is about 0.44. Read as a reliability, that is the correlation you would expect between this screen and an independent repeat of it. Enough to rank targets, but not enough to trust any single one on its own."

### 2:32–2:50 · The design, RQ4  (slide 8)

**ON SCREEN:** the D-study surface; two guides cap near 0.53.

**VOICEOVER:**
> "The last question is how to do better. A design study shows the limit is the number of guides, not donors: with two guides per gene the coefficient stays near 0.53, and adding donors barely helps. So a future screen should add guides."

### 2:50–3:00 · Close  (slide 9)

**ON SCREEN:** the conclusion slide; submitted to bioRxiv, Built with Claude.

**VOICEOVER:**
> "In short, for a screen you want to reproduce, the thing to rank on is dependability, not effect size. The analysis runs end to end from the released data, and it is now submitted to bioRxiv. Built with Claude."

---

## Production notes

- **Read it flat.** It should sound like a person explaining their work, not a launch video.
- **Hold the process slide (0:48–1:23) a little longer** — it is the part reviewers find least expected.
- **If a beat runs long, trim RQ3 or RQ4 first.** Do not cut the honesty framing in the process beat.
- **Total ≈ 2:55 at 150 wpm.** Rough word counts per beat: 42 / 72 / 78 / 60 / 55 / 52 / 45 / 42.
