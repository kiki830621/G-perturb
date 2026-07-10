## Context

Issue #8 已把專案重心從 `E × R × Q` 排名改為 distribution-light generalizability decomposition，並在 apply checkpoint 鎖定邊際 h5mu、`1 − CCC`、per-target distance aggregation、Fay–Herriot shrinkage 與 replication floor。Issue #9 的 Diagnosis 證明這些決策早於 observation-level design 與 identifiability audit：guide 是 nested within target；兩份 h5mu 是分別邊際化的 DE products；merged pseudobulk 才保留 guide×donor×condition joint cells；sample metadata 又顯示 run 與 donor／condition 部分混淆且沒有 identical-spec run replicate。

本 change 不直接選擇或實作最終 estimator。它建立一個可重現的 GPT-5.6 Sol 紅隊審查程序，產出 `docs/complete-methodology-review-and-upgrade-plan.md`，讓後續 #8 ingest 只採用已通過資料可識別性、統計推論與 falsification gate 的方法契約。

利害關係人包括專案 owner、後續 Sol/Codex reviewer、#8 實作者與評閱研究方法的讀者。主要限制是 2 guides、4 donors、3 fixed conditions、run confounding、高維且相關的 outcome genes，以及目前沒有 identical-spec pseudobulk replicate。

## Goals / Non-Goals

**Goals:**

- 以三個具追溯性的 `gpt-5.6-sol` pass 找出並處置現有計畫的 P0–P3 方法問題。
- 先固定 evidence、estimands、decision universes 與 claim boundaries，再比較 estimator。
- 建立 claim→data→estimand→identifiability crosswalk，讓每一項 variance、reliability、floor 與 validation 主張都有觀測單位及失敗路徑。
- 定義 profile-level primary、gene-wise sensitivity 與 pathway interpretation 三層彼此不循環的分析契約。
- 定義 simulation、negative controls、internal/external validation、selection/FDR 與 machine-readable degradation rules。
- 產出可逐檔 ingest 回 #8 的修正 crosswalk，並保留 #8 已完成工作的歷史。

**Non-Goals:**

- 不下載 44.6 GB pseudobulk 或 1.6 TB cell-level data。
- 不執行 DE、variance decomposition、ranking、圖表或 demo。
- 不直接修改 `openspec/changes/generalizability-decomposition/`。
- 不宣稱 Sol review 等同實證校準；需要 actual data 或 simulation 才能驗證的項目必須標為 blocked gate。

## Decisions

### Evidence bundle is frozen before review

在 Pass A 開始前建立 evidence manifest，至少包含 issue #9 body/Diagnosis、`README.md`、`docs/design.md`、`docs/README.md`、資料 codebook 與 data-sharing readme、sample metadata，以及 #8 的 proposal/design/spec/tasks。Manifest 記錄檔案 path、Git commit、來源 URL 或 issue comment URL；每個 reviewer 使用同一份 frozen evidence，避免不同輸入造成表面共識。

替代方案是讓每個 reviewer 自由探索整個 repo。這會增加 coverage，但無法區分 reviewer 判斷差異與輸入差異，因此只允許在 finding 內提出 additional-evidence request，不直接改變該 pass 的 frozen input。

### Sol review uses three isolated passes and fixed adjudication

Pass A 是 architecture/identifiability review；Pass B 是 adversarial statistical review。兩者使用新的 Codex task、模型 `gpt-5.6-sol`、reasoning effort `max`，互相看不到輸出。Pass C 是 integration/handoff review，使用第三個新 task，輸入為 frozen evidence、已整合的 draft 以及 A/B finding table；它不重新投票，而是檢查修正是否完整且一致。

每個 pass 在最終文件記錄 task/thread identifier、模型、effort、時間、exact prompt、evidence manifest version 與完整 finding table。若指定模型不可用，流程停止並標示 blocked，不以其他模型靜默替代。

Finding schema 固定為 `ID / pass / severity / evidence / affected claim / proposed correction / disposition / verification`。P0 代表核心主張無效或不可識別；P1 代表會實質改變推論的偏誤或缺漏；P2 是 robustness/operability；P3 是表達與可維護性。每項 disposition 只能是 resolved、blocked 或 rejected-with-evidence。

### Estimands precede estimators

方法文件先建立 estimand registry，至少區分：condition-specific universe score、三個 fixed conditions 的預先加權平均、relative ranking decision、absolute hit-call decision、donor-panel consistency、guide-universe generalization、cross-cell-type transportability 與 T-cell replication。

每個 estimand 記錄 object、unit、target population、facet status、aggregation weights、missingness policy、effect direction、uncertainty target 與允許用語。Estimator comparison 只能在 registry 凍結後進行，防止依結果改寫研究問題。

### Data identifiability is a hard gate

Joint pseudobulk 是完整方法的最低 observation-level input。文件必須要求 actual apply/implementation 執行 schema、coverage 與 design-rank gate：必要 obs fields、guide→target mapping、targeting/NTC、matched donor×condition×run controls、完整/缺失 cells、設計矩陣 rank 與共線性。

本 change 不下載資料，因此區分兩種狀態：`design-specified` 表示 gate 定義完整；`empirically-passed` 只在 actual pseudobulk 檢查結果存在時使用。不得把前者寫成後者。

資料分支固定如下：

- joint pseudobulk 可識別所需 component：允許進入完整 profile estimator 評估；
- joint pseudobulk 存在但無 identical-spec replicate：最高階 interaction 與 sampling residual 合併，replication floor=`not_identifiable`；
- 可取得 lane-level pseudobulk：重新檢查是否能拆 batch/run 與 replicate residual；
- 僅有邊際 h5mu：只允許 `marginal_only` agreement atlas，不能宣稱完整 crossed decomposition。

### Profile primary and gene/pathway secondary are distinct

Profile-level 是主要方法，response 是 matched-NTC、帶 sampling uncertainty 的 genome-wide effect profile。Sol review 必須比較至少三類候選：precision-weighted Euclidean/multivariate linear decomposition、kernel/distance-based permutation method、robust hierarchical functional model。比較準則包括 identifiability、additivity、非 Euclidean behavior、高維基因相關、第一階段 measurement error、restricted permutation、compute 與 synthetic recovery。CCC/Pearson 預設為 diagnostics，除非 finding resolution 提供可加總與可識別的獨立證明。

Gene-wise 是 sensitivity layer：target-blind gene universe、兩階段 effect+covariance model、guide nested within target、直接 condition contrasts、跨 target/outcome-gene pooling，以及 atlas-wide omnibus 後的 stage-wise/selective FDR。逐基因 ratio 不直接平均；跨基因 dependability 使用預先指定權重的 summed signal/error aggregation。

Pathway-level 是 biological interpretation layer：固定 gene-set release 與 mapping；Hallmark primary、Reactome/GO secondary；全基因 signed moderated statistics；competitive CAMERA 與 self-contained ROAST/FRY 分開。使用同一 CD4 資料得到的 pathway 結果不得稱 independent validation。

### Replication floor requires identical-spec replicates

Replication floor 的必要條件是相同 target、guide、donor、condition 與其他 specification 下的獨立 lane/library/run measurement。兩條 guides、兩組 donor halves 或 NTC-vs-target 都不符合。

若資料未提供 identical-spec replicate，文件必須撤回 distribution-free floor，將不可拆部分命名為 combined highest-order interaction + sampling residual，並輸出 `not_identifiable` reason。取得 lane-level pseudobulk 是優先追加資料；1.6 TB cell-level rebuild 只在作者無法提供 lane-level artifact 且方法價值足以負擔成本時列為 fallback。

### Validation uses falsification and no leakage

文件必須規定 synthetic data 注入已知 facet components、confounding、missingness、single-guide、low counts、KD efficiency、heavy tails 與 correlated genes，並預先定義 bias、coverage、type-I error/FDR、false-sign rate、component recovery 與 D-study monotonicity threshold。

Internal validation 包含 NTC-vs-NTC negative controls、guide cross-fit、leave-one-donor-out 與 common-support/R2-only sensitivity。External evidence 必須分成 same-cell-type replication、assay translation、cross-cell-type transportability 與 biological relevance；K562 只能支持 transportability。任何 validation source 不得同時調參又宣稱 untouched validation，除非使用 nested holdout。

### Approval gate rejects unresolved P0/P1 findings

Final document 狀態只有 approved 或 blocked。Approved 要求三個 pass 完整、所有 P0/P1 finding resolved 或 rejected-with-evidence、所有 16 個必要章節齊全、無 placeholders，且 claim/data/estimand、method/inference、validation/claim boundary 互相一致。

若任一 P0/P1 finding blocked，文件仍可完成並被提交，但狀態必須是 blocked，列出解除條件，且 #8 statistical core 維持 paused。P2/P3 可進 residue，但要有 owner 與驗證時點。

### Handoff is a crosswalk, not a direct #8 rewrite

本 change 的 apply 只建立新方法文件並在 `docs/README.md` 加入連結。文件最後以表格列出每項 #8 proposal/design/spec/task 的 keep、replace、remove 或 add 決策、理由、驗證與目標 artifact。Owner 核准後另走 `spectra-ingest` 更新 `generalizability-decomposition`；本 change 不直接競寫該 change。

### Paper-grade resolution is mandatory — a blocked audit triggers a resolution programme, not project completion (2026-07, CLAUDE.md, #10)

Pass B returned **blocked** (3 P0 + 7 P1; `docs/reviews/sol-pass-b-adversarial-statistical-review.md`). The `CLAUDE.md` standard "Methodology standard — paper-grade, no compromise" makes the terminal disposition binding: a published `blocked` audit is the correct *audit* outcome, but it is **not** an acceptable project end state. Every P0/P1 finding MUST be resolved before any profile method is declared primary. Resolution requires exactly the empirical work this change lists as Non-Goals — download the ~44.6 GB joint pseudobulk, freeze a new evidence manifest with the actual target×guide×donor×condition grid / rank / NTC / missing-cell audit (B-001), and run pre-registered synthetic recovery for all three candidate families plus every §8 control, meeting every §7 falsification gate. That resolution is a **follow-on empirical change** (the methods-paper implementation) which supersedes this change's data/simulation Non-Goals; this audit change's remaining job (tasks 3.x, 4.x) is to formalize the blocked verdict + the 11-finding ledger, pin the gates as machine-checkable unblock-conditions, and hand the resolution programme + the #8 crosswalk to that follow-on. Deadline does not lower the bar; a non-identifiable quantity (e.g. B-003 run vs donor×condition) is reported `not_identifiable`, never fabricated to satisfy a gate.

Pinned unblock-conditions, frozen before any real target result:

- **§7 falsification gates** — Monte Carlo ≥ 5,000 null / ≥ 2,000 non-null per scenario; type-I ∈ [0.04, 0.06]; FDR ≤ 0.06 (95% upper ≤ 0.07); coverage ∈ [0.93, 0.97] overall + support / guide-count / effect-size strata; component recovery bias ≤ 0.02, RMSE ≤ 0.05, zero-component median ≤ 0.01; winner's-curse calibration slope ∈ [0.9, 1.1]; D-study curves monotone non-decreasing; candidate central-share disagreement > 0.05 → forced disagreement diagnosis; compute gates per B-011.
- **§8 controls** — NTC-vs-NTC; guide cross-fit; leave-one-donor-out (refit all hyperparameters on 3 donors); common-support sensitivity fixed to the R2 two-donor panel; external-evidence taxonomy (K562 = cross-cell-type transportability only).

## Implementation Contract

**Observable behavior**

完成 apply 後，讀者可從 `docs/README.md` 開啟一份單一、可稽核的方法升級文件。文件開頭顯示 approved/blocked 狀態與日期；內含三個 Sol pass 的識別與 finding ledger、16 個規定章節、claim/data/estimand crosswalk、方法候選評比、驗證與降級契約，以及 #8 file-by-file ingest crosswalk。

**Document shape**

文件章節固定為：Executive decision summary；current-plan audit；data/provenance；estimands；identifiability；profile model；gene-wise model；pathway model；uncertainty/permutation/bootstrap/shrinkage；missingness/QC/degradation；simulation/falsification；internal/external validation；pipeline/modules/output schemas；implementation order/verification；Sol review log；#8 change crosswalk。

Finding ledger 每列包含九個固定欄位；claim crosswalk 每列至少包含 claim、estimand、observation unit、required variation、available evidence、rank/gate、assumptions、status 與 allowed wording。

**Failure modes**

- 指定 Sol model 不可用：停止並標 blocked，不建立假裝完成的 review pass。
- pass 缺 prompt/config/evidence version：該 pass invalid，approval gate 失敗。
- actual pseudobulk 未檢查：相關 gate 只能標 `design-specified`，不得標 `empirically-passed`。
- A/B findings 衝突：Pass C 必須逐項 adjudicate；未處置衝突視為 P1 unresolved。
- 無 identical-spec replicate：floor=`not_identifiable`，不得以 marginal agreement 代替。
- 文件或 crosswalk 有 placeholder、未列的 claim 或無驗證的 P0/P1：狀態 blocked。

**Acceptance criteria**

- Spectra capability scenarios 全部可由文件內容直接核對。
- 三個 pass 各有 task identifier、`gpt-5.6-sol`、effort、timestamp、prompt、evidence version 與 findings。
- 文件具完整 16 章、finding ledger、claim crosswalk、candidate-method comparison、quantitative falsification thresholds 與 #8 ingest crosswalk。
- `docs/README.md` 連結存在且說明文件狀態。
- 自我審查與 `spectra analyze` 無 Critical/Warning；`spectra validate audit-complete-methodology` 通過。

**Scope boundaries**

In scope 是 Sol review、方法文件、discoverability link 與後續 ingest crosswalk。Out of scope 是資料下載、分析程式、模型執行、結果、圖表、demo、#8 artifact 修改與 GitHub issue 關閉。

## Risks / Trade-offs

- [Sol review 變成形式審查] → 隔離 A/B、保存 exact inputs、固定 severity/disposition，P0/P1 具有阻擋權。
- [不下載 pseudobulk 無法實證 rank] → 嚴格區分 `design-specified` 與 `empirically-passed`，把後者列為 #8 ingest 後的首要 gate。
- [單一文件過長] → 以表格、固定章節與 concise finding ledger維持可讀性；完整性優先，不拆散審計軌跡。
- [新 change 與 #8 重疊] → 本 change 僅產出 crosswalk，不直接修改 #8。
- [Reviewer 對候選方法意見不一致] → Pass C 依預先比較準則 adjudicate，無證據時保留 blocker。
- [新增 lane/cell data 擴大成本] → lane-level artifact 優先，cell-level rebuild 保持條件式 fallback。

## Migration Plan

1. Apply 本 change，建立方法文件與 docs index 連結。
2. Owner 審閱 approved/blocked 狀態與 P0/P1 disposition。
3. Owner 核准後執行 `spectra-ingest`，把 crosswalk 加入 `generalizability-decomposition`，保留原完成 tasks 並新增 supersession tasks。
4. 重新 analyze/validate #8 change，再恢復統計實作。
5. 若本 change 需要回復，移除 docs index 連結並刪除新文件；#8 維持原狀但不得把未審查契約視為已核准。

## Open Questions

以下不是留白；它們是 Sol review 必須給出 resolved 或 blocked disposition 的審查問題：

1. 哪一個 profile estimator 在 actual design 下同時具可識別、可加總與校準良好的 uncertainty？
2. lane-level pseudobulk 是否可取得，且是否真的形成 identical-spec replicates？
3. run×donor×condition confounding 下，哪些 condition effects 具有共同支持？
4. confirmatory target/gene universe 與 incomplete-grid policy 為何？
5. target-level shrinkage 的 direct estimate 與 sampling covariance 從何而來？
6. profile、gene 與 pathway 三層何種一致／分歧模式構成支持、敏感或失敗？
7. #9 只定義 empirical gate，或需在核准前實際檢查 pseudobulk schema/rank？
