# G-perturb — read-aloud script

About 450 words, roughly 2:58 at a normal speaking pace, inside the 3-minute limit. The bracketed headers are pacing markers, not spoken. Read it plainly, the way you would explain the work to a colleague; there is no need to hit any word hard.

---

[0:00 · Intro and the problem]

I'm Che Cheng, from the Institute of Statistical Science at Academia Sinica, and this is G-perturb. Perturb-seq screens usually rank drug targets by how strongly a perturbation shifts gene expression. But a large effect seen in a single guide, or a single donor, can be measurement noise rather than real biology, and a target picked on that basis may not reproduce.

[0:20 · The method]

G-perturb ranks targets by whether the readout is dependable, not just by how large it is. I treat each effect as a measurement and borrow generalizability theory, a framework from psychometrics, to ask one question for every target: would this effect hold up with a different guide, a different donor, a different cell state? Combining the guide and donor reliability gives each target a single dependability coefficient.

[0:48 · The process]

I also wanted the analysis to be checkable, so every methodological decision, which estimator and which threshold, is recorded as a GitHub issue, through an issue-driven workflow I built as an open-source Claude Code plugin. I gave that record to a different model, GPT-5.6 Sol, and asked it to find problems. It blocked the design and raised eleven issues, three of them critical, which I then worked through with Claude and cross-checked across models.

[1:23 · Ranking (RQ1)]

The first question is whether ranking by dependability actually changes the shortlist. It does. Once you weight effect size by the dependability coefficient, fifty of the top hundred targets by raw effect drop out of the top hundred by dependability. Reproducible targets that effect size underrates move up; RPS3, for one, goes from seventy-ninth to fourth.

[1:48 · Context (RQ2)]

The second question is about context. Analysed within each activation state, dependability picks out the T-cell-receptor module, the CD3 complex with ZAP70 and LAT, as reliably measurable only in activated cells. The method was given no gene labels, so recovering a known pathway this way is a good sign it is tracking real biology.

[2:12 · Overall dependability (RQ3)]

The third question is how dependable the screen is overall. On the representative genes the generalizability coefficient is about 0.44. Read as a reliability, that is the correlation you would expect between this screen and an independent repeat of it. Enough to rank targets, but not enough to trust any single one on its own.

[2:32 · The design (RQ4)]

The last question is how to do better. A design study shows the limit is the number of guides, not donors: with two guides per gene the coefficient stays near 0.53, and adding donors barely helps. So a future screen should add guides.

[2:50 · Close]

In short, for a screen you want to reproduce, the thing to rank on is dependability, not effect size. The analysis runs end to end from the released data, and it is now submitted to bioRxiv. Built with Claude.
