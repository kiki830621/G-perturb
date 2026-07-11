## 1. 凍結新證據 manifest（B-001）

- [x] 1.1 下載 joint target×guide×donor×condition pseudobulk（~44.6 GB），走中研院統計所 cluster 儲存；驗證方式為 checksum 與來源 URL 記錄齊全，且確認非 marginal `by_guide`／`by_donors` 的替身。
- [x] 1.2 交付 `Frozen empirical evidence manifest over the joint pseudobulk`：產出版本化 + checksummed `evidence.manifest.json`，逐 cell 記錄存在與否、per-cell library size／n_cells、NTC coverage 與 design-matrix rank；驗證方式為任何 modeling step 前 manifest 已凍結，缺格 cell 記錄而非 impute。

## 2. 可識別性實測 fail-closed（B-002／B-003）

- [x] 2.1 交付 `Empirical identifiability is a fail-closed gate` 的 design-rank gate 與 run／interaction separability gate：對每個 variance／reliability／ranking claim 用真實 design matrix 數值檢查 rank 與 confounding；驗證方式為 rank 不足者 status = `not_identifiable`、最高階不可拆 interaction 與 sampling residual 合併、不 zero-fill 不改名。
- [x] 2.2 落實 replication floor 僅在 identical-spec replicate 存在時估：檢查 manifest 是否有 target／guide／donor／condition 全同僅 lane 不同的 replicate；驗證方式為無 replicate 時 floor status = `not_identifiable`，不報 distribution-free floor。

## 3. 推論契約在 synthetic 上先校準（B-004…B-007）

- [ ] 3.1 交付 `Measurement-error covariance drives a precision-weighted second stage`：以 matched-NTC 估 per-target effect 的 measurement-error covariance，餵進 precision-weighted GLS 第二階段，permutation exchange group 尊重 guide-nested-within-target 與 donor-crossed 結構；驗證方式為在已知 ground-truth synthetic 上 component bias ≤ 0.02、coverage ∈ [0.93, 0.97]。
- [ ] 3.2 落實 high-dimensional gene 依賴的 low-dimensional basis／shrinkage 與 negative variance component 的 boundary-aware 估計；驗證方式為 negative-component 情境不以截零 silently 改變 estimand，且 synthetic recovery 的 RMSE ≤ 0.05。

## 4. selective-FDR test tree 與 pathway null（B-008／B-009）

- [x] 4.1 交付 `Single selective-FDR test tree and separated pathway nulls`：gene-wise 用 target-blind atlas-wide 單一 FDR + stage-wise，不對每 target 各跑 FDR；pathway 用 signed all-gene 統計，competitive（CAMERA）與 self-contained（ROAST／FRY）分開、pin gene-set 版本；驗證方式為 synthetic 下 FDR ≤ 0.06、false-sign 受控，且 DE-hit-list hypergeometric 非唯一證據。

## 5. leak-free validation 與誠實 taxonomy（B-010）

- [x] 5.1 落實設計決策「leak-free validation manifest 與誠實 external-evidence taxonomy（B-010）」，交付 `Leak-free validation manifest and honest external-evidence taxonomy`：凍結 validation manifest 分離 tuning 與 holdout，external evidence 依 taxonomy 分類且措辭受限；驗證方式為任何調參來源不標 untouched validation，K562 僅標 cross-cell-type transportability、非 independent replication。

## 6. 凍結 gates、synthetic recovery 選方法（§7／§8）

- [x] 6.1 落實設計決策「gates 在看真實結果前凍結（§7／§8）」，交付 `Falsification gates are frozen before any real result`：寫入 checksummed `gates.frozen.json`，列全部 §7 門檻（MC null ≥ 5000／power ≥ 2000、type-I ∈ [0.04, 0.06]、FDR ≤ 0.06、coverage ∈ [0.93, 0.97]、component bias ≤ 0.02／RMSE ≤ 0.05、winner's-curse slope ∈ [0.9, 1.1]、D-study monotonicity、candidate-disagreement > 0.05、compute 上限）；驗證方式為任何真實 target 結果被檢視前 gate 檔已存在，且門檻與 `docs/reviews/sol-pass-b-adversarial-statistical-review.md` §7 一致。
- [x] 6.2 落實設計決策「pre-registered synthetic recovery 選定 primary method」，交付 `Method selection uses synthetic recovery only`：對三候選（precision-weighted multivariate／kernel-distance permutational／robust-hierarchical functional）跑 pre-registered synthetic recovery，只由 synthetic loss 選 winner；驗證方式為 external-validation 表現不進 selection，三候選皆未過全部 gate 時回報「no method qualifies」、不宣告降格 primary。
- [ ] 6.3 執行 §8 controls：NTC-vs-NTC null 校準、guide cross-fit、leave-one-donor-out、R2 common-support sensitivity；驗證方式為每個 control 產出 `results/controls/*.json` 且通過對應數值門檻（NTC null 落在 type-I band 內、cross-fit 穩定、donor 泛化、common support 充分）。

## 7. compute discipline（B-011）

- [x] 7.1 落實設計決策「compute discipline — backed-sparse、先 benchmark、不 densify（B-011）」，交付 `Compute is benchmarked and backed-sparse`：在 1%／10% shard 量 wall-time 與 peak memory 再外推全量，permutation／synthetic 大 fan-out 走統計所 cluster（`hmque`／`mulque`，job 內取 `$PBS_NP`）；驗證方式為全量 run 前有 shard benchmark、全程不 densify 10k-gene×34k-target 矩陣。

## 8. 解除條件與 #8 交接

- [ ] 8.1 產出 #8 ingest crosswalk：列 `generalizability-decomposition` 每個 proposal／design／spec／task 的 keep／replace／remove／add，對到本 change 的 gate 結果；驗證方式為 crosswalk 每列都指向一個通過的凍結 gate 或一個 `not_identifiable` 誠實降級，且本 change 不直接改 #8 artifacts。
- [ ] 8.2 對齊 `audit-complete-methodology` 的解除條件：把每條 P0/P1 的 machine-checkable unblock-condition 對到本 change 的實測結果，列出 audit → `approved` 的逐項條件；驗證方式為未全數通過前 #8 統計核心維持 paused，文件不得把 `blocked` 描述為可交付的最終狀態。
