# Design — resolve-methodology-blockers

## Context

`audit-complete-methodology` 交付了一份 status `blocked` 的雙層方法契約：模型規格本身通過三輪 Sol 審查，但 Pass B 找到 3 P0 + 7 P1（B-001…B-011），且所有 identifiability／validation gate 目前是 `design-specified`（紙上），不是 `empirically-passed`（實測）。依 `CLAUDE.md` paper-grade 標準，這個 `blocked` 觸發本 resolution programme。

關鍵資料事實（來自 #7 characterization）：目前本機只材化了 marginal 產物——`DE_stats.h5ad`（16.79 GB，aggregate over guide／donor）、`by_guide.h5mu`（29.42 GB，兩個 guide modality）、`by_donors.h5mu`（16.87 GB，6 個 C(4,2) donor-pair modality）。**joint target×guide×donor×condition pseudobulk（~44.6 GB）尚未下載**。沒有它，crossed variance component（σ²_TG、σ²_TD、σ²_TGD）在結構上不可識別——這正是 B-001 的核心。因此本 programme 的第一步必然是把 joint 觀測設計實測出來。

paper-grade 的判準不是「模型多複雜」而是「證據多完整」：任一 quantity 若在真實觀測設計下不可識別，就回報 `not_identifiable`，不捏造、不 zero-fill、不改名。

## Goals / Non-Goals

**Goals**
- 把 B-001…B-011 每一條從 `design-specified` 推進到 `empirically-passed` 或誠實的 `not_identifiable`。
- 凍結 §7 falsification gates 與 §8 controls，**在看任何真實 target 結果之前**。
- 對三個 profile 候選跑 pre-registered synthetic recovery，**只由 synthetic loss 選 winner**。
- 產出 #8 ingest crosswalk，並列出 `audit-complete-methodology` → `approved` 的逐項解除條件。

**Non-Goals**
- 最終 manuscript 正文、demo、超出 pathway 契約的生物詮釋。
- 用 external validation（K562／arrayed）選方法或調參——那是 leakage，明確禁止。
- 把「跑得動」當成「gate 通過」；未過 gate 的方法不得宣告 primary。

## Decisions

### Decision 1: 凍結新證據 manifest 是一切建模的前置（B-001）

下載 ~44.6 GB joint pseudobulk 後，先產出一份版本化 + checksummed 的 evidence manifest，列每個 target×guide×donor×condition cell 是否存在、其 per-cell library size／n_cells、NTC coverage、以及 design-matrix rank。任何模型步驟**不得**在 manifest 凍結前執行。marginal h5mu 只作 comparison／degraded 輸出，永不充當 joint 的替身。這條把 B-001 從「假設 joint 存在」變成「實測 joint 長什麼樣」。

### Decision 2: 可識別性是實測硬門檻，fail-closed（B-002／B-003）

每個 variance／reliability／floor／ranking claim 進模型前先過兩道實測 gate：(a) **design-rank gate**——把 claim 對應的 design matrix 建出來，數值檢查其 rank 是否足以分離該 component；(b) **run／interaction separability gate**——檢查 confounding（如 run 與 donor 完全共線）。任一 gate 失敗 → 該 quantity status = `not_identifiable`，最高階不可拆 interaction 與 sampling residual 合併回報，**不 zero-fill、不改名**。replication floor 僅在存在 identical-spec replicate（target／guide／donor／condition 全同、僅 lane 不同）時才估；否則 floor = `not_identifiable`。

### Decision 3: measurement-error covariance 驅動 GLS 第二階段，推論契約先在 synthetic 校準（B-004／B-005／B-006／B-007）

pseudobulk 的 per-target effect 帶已知 measurement error（來自有限 cell 數）。以 matched-NTC 估其 covariance，餵進 precision-weighted GLS 第二階段，而非把 point estimate 當無誤差輸入。permutation 的 exchange group 須尊重 nested／crossed 結構（guide nested within target；donor crossed），不可全域打散。high-dimensional gene 依賴以低維 basis 或 shrinkage 處理；出現 negative variance component 時走 boundary-aware 估計（REML／non-negative）而非直接截零改變 estimand。以上每條先在已知 ground-truth 的 synthetic 上驗證校準，才套真實資料。

### Decision 4: 單一 selective-FDR test tree；competitive 與 self-contained pathway null 分離（B-008／B-009）

gene-wise 用 target-blind gene universe，atlas-wide 單一 FDR 控制後再 stage-wise，不對每個 target 各跑一次 FDR（避免 selection 不受控）。pathway 用 signed all-gene 統計：competitive 問題用 CAMERA、self-contained 問題用 ROAST／FRY，兩者分開回報、pin gene-set 版本，不以 DE-hit-list hypergeometric 當唯一證據。

### Decision 5: leak-free validation manifest 與誠實 external-evidence taxonomy（B-010）

凍結一份 validation manifest：明列哪些觀測用於 tuning、哪些保留作 holdout；任何進過 tuning 的資料不得標 untouched validation。external evidence 依 taxonomy 分類且措辭受限——K562 = cross-cell-type transportability（非 independent replication）；同 CD4 pathway = internal sensitivity（非 validation）；arrayed bulk／flow = assay translation。

### Decision 6: pre-registered synthetic recovery 選定 primary method；gates 在看真實結果前凍結（§7／§8）

在 `results/gates.frozen.json` 凍結全部數值門檻：MC 規模（null ≥ 5000、power ≥ 2000）、type-I ∈ [0.04, 0.06]、FDR ≤ 0.06、interval coverage ∈ [0.93, 0.97]、component bias ≤ 0.02／RMSE ≤ 0.05、winner's-curse slope ∈ [0.9, 1.1]、D-study monotonicity、candidate-disagreement > 0.05 觸發診斷、compute 上限。凍結後才對三候選跑 synthetic recovery，**winner 由 synthetic loss 決定**，K562／arrayed 只作事後 transportability 佐證、不進 selection。凍結檔一旦寫入即 checksummed，事後更改留 audit trail。

### Decision 7: compute discipline — backed-sparse、先 benchmark、不 densify（B-011）

先在 1%／10% shard 量 wall-time 與 peak memory，外推全量可行性；permutation／bootstrap／synthetic 的大 fan-out 走中研院統計所 PC Cluster（大 RAM 用 `hmque`、多核 synthetic 用 `mulque`，job 內取 `$PBS_NP` 不用 `$(nproc)`）。全程 backed／sparse，不 densify 10k-gene × 34k-target 矩陣。

## Implementation Contract

**Observable outputs**
- `analysis/resolution/manifest/evidence.manifest.json` + `.sha256`：joint grid、缺格、NTC coverage、design rank（凍結、版本化）。
- `analysis/resolution/results/identifiability.json`：每個 claim 的 status ∈ {`empirically-passed`, `marginal-only`, `not_identifiable`}。
- `analysis/resolution/results/gates.frozen.json` + `.sha256`：§7／§8 全部數值門檻（在任何真實結果前凍結）。
- `analysis/resolution/results/synthetic_recovery/<candidate>.json`：三候選各自對每個 gate 的 pass/fail + 數值。
- `analysis/resolution/results/controls/*.json`：NTC-vs-NTC、guide cross-fit、leave-one-donor-out、common-support。
- `docs/complete-methodology-review-and-upgrade-plan.md` 的 finding ledger 每條 P0/P1 標記解除狀態；#8 crosswalk。

**Failure modes**
- 任一 §7 gate 失敗 → 對應候選**不得**宣告 primary；三候選皆失敗 → 誠實回報「no method qualifies」而非降格照用。
- 任一 quantity 不可識別 → `not_identifiable`，不 fabricate。
- external validation 表現**永不**改變 method selection。

**Acceptance**
- 選定的 primary method 對每條 central claim 都有一個通過的凍結 gate。
- 全部 §8 controls 通過（NTC null 校準、cross-fit 穩定、donor 泛化、common support 充分）。
- `audit-complete-methodology` 的解除條件逐項對到本 change 的 gate 結果；未全通過前 #8 統計核心維持 paused。

**Scope boundary**
- 本 change 產出 gate 結果 + crosswalk；**不**直接改寫 #8 artifacts，也不寫 manuscript／demo。

## Risks / Trade-offs

- **Compute**：joint 44.6 GB + ≥5000×3-candidate synthetic 是重運算。緩解：shard benchmark 先行、走統計所 cluster、backed-sparse。
- **結構性不可識別**：joint 設計可能仍缺某些 cell（真實缺格），使部分 crossed component 不可識別。緩解：這正是 fail-closed 要誠實回報的——`not_identifiable` 勝過假數字。
- **三候選全數失敗**：可能沒有方法能過全部 gate。緩解：這是合法且誠實的結論（「no method qualifies under frozen gates」），觸發重新設計而非放水。
- **Timeline**：這是方法論文級工程，不吻合 7/13 hackathon 截止。已知取捨：paper-grade 標準明訂 deadline 不降低 bar；hackathon 交付與 paper 解除是兩條時間線。

## Migration & Open Questions

- **下載來源／頻寬**：joint pseudobulk 的確切 URL 與檔案切分待 B-001 執行時確認（companion repo `emdann/GWT_perturbseq_analysis_2025` 或原始 GEO/Zenodo）。
- **Cluster 佈署細節**：R（lme4／vegan）vs Python（h5py extraction）在 cluster 上的環境版本，待 compute benchmark 階段定。
- **gate 門檻微調**：§7 數值門檻沿用 review §7；若 synthetic 顯示某門檻不合理，須留 audit trail 修改凍結檔，不得事後無紀錄放寬。
