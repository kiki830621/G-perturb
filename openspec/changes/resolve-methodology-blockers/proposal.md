## Why

`audit-complete-methodology` 的 GPT-5.6 Sol 紅隊審查回傳 **blocked**（3 P0 + 7 P1，B-001…B-011；`docs/reviews/sol-pass-b-adversarial-statistical-review.md`）。依 `CLAUDE.md`「Methodology standard — paper-grade, no compromise」，`blocked` **不是終態**：它觸發一個 follow-on empirical resolution programme。本 change 就是那個 programme——把每條 P0/P1 從「文件上寫好的契約」推進到「在真實 joint pseudobulk 上實測通過的 machine-checkable gate」，直到任一 profile method 能被誠實宣告為 primary。

audit change 的 Non-Goals（不下載大型資料、不跑完整模型、不做 synthetic recovery）在本 change **反轉為必做工作**：這些正是解除 blocker 唯一的合法路徑，不是可省略的加分項。

## What Changes

- **凍結新證據 manifest（B-001）**：下載 ~44.6 GB joint pseudobulk，實測 target×guide×donor×condition grid、缺格、NTC coverage、design-matrix rank 與 per-cell counts，產出版本化 + checksummed manifest。marginal `by_guide.h5mu`／`by_donors.h5mu` 僅作 comparison／degraded 輸出。
- **可識別性實測 fail-closed（B-002／B-003）**：對每個 variance／reliability／floor／ranking claim 跑 design-rank gate 與 run／interaction separability gate；rank 不足或無 identical-spec replicate 者一律回報 `not_identifiable`，不 zero-fill、不改名。
- **推論契約落地（B-004…B-007）**：實作 permutation exchange groups、matched-NTC measurement-error covariance → GLS 第二階段、high-dimensional gene basis、與 shrinkage／negative-component 處理，全部先在 synthetic 上校準。
- **selective-FDR test tree 與 pathway null（B-008／B-009）**：single atlas-wide → stage-wise error control；competitive（CAMERA）與 self-contained（ROAST／FRY）假設分離，pin gene-set 版本。
- **leak-free validation manifest（B-010）**：凍結 validation split，任何調參來源不得再標 untouched validation；external-evidence taxonomy 誠實分類（T-cell replication／assay translation／cross-cell-type transportability／biological relevance）。
- **compute benchmark（B-011）**：先在 1%／10% shard 量 wall-time 與 peak memory，backed-sparse、不 densify、不 oversubscribe。
- **凍結 §7 falsification gates 與 §8 controls，再看任何真實結果**：對三個候選（precision-weighted multivariate／kernel-distance permutational／robust-hierarchical functional）跑 pre-registered synthetic recovery；**只由 synthetic loss 選 winner**，不由 K562 或任何 external validation 選。
- **解除後回寫**：產出 #8 ingest crosswalk，並把 `audit-complete-methodology` 由 `blocked` 翻成 `approved` 的條件逐項對齊；未全數通過前 #8 統計核心維持 paused。

## Non-Goals

- 不撰寫最終 manuscript 正文、不做 demo／視覺化（那是解除 blocker 後的下游）。
- 不擴張 biological interpretation 超出 pathway 契約允許的 claim boundary。
- 不以「跑得動」代替「gate 通過」：任一 §7 gate 未過，對應方法就**不得**宣告 primary，而非降格照用。
- 不改寫 `audit-complete-methodology` 的既有 artifacts；本 change 是它 crosswalk 指向的 follow-on，核准後再由 `/spectra-ingest` 對 #8 落地。

## Capabilities

### New Capabilities

- `methodology-resolution`: 在真實 joint pseudobulk 上，以凍結證據 manifest、fail-closed 可識別性、pre-registered synthetic recovery（滿足全部凍結 falsification gates 與 controls）解除 audit 的 P0/P1 blockers，並只由 synthetic loss 選定 primary profile method，最後產出 #8 crosswalk。

### Modified Capabilities

(none)

## Impact

- Affected specs: `methodology-resolution`
- Affected code:
  - New: `analysis/resolution/`（manifest builder、identifiability gate、synthetic-recovery suite、三候選 estimator、§8 controls harness、§7 gate harness）、`analysis/resolution/results/`
  - Modified（解除後）: `docs/complete-methodology-review-and-upgrade-plan.md`（填入實測 gate 結果、status → approved 的條件）、`openspec/changes/audit-complete-methodology/`（狀態對齊，經 ingest，非本 change 直接改）
  - Removed: (none)
- Downstream coordination:
  - `openspec/changes/generalizability-decomposition/`（#8）在本 change 通過全部 gates 後，依產出的 crosswalk ingest；本 change 不直接修改它。
  - 計算資源走中研院統計所 PC Cluster（`hmque` 大 RAM node / synthetic 用 `mulque` 多核；見 `CLAUDE.md` global），非本機硬撐。
