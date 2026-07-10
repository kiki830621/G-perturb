# G-perturb：Sol Pass B 對抗性統計審查

## 1. Provenance

| 欄位 | 值 |
|---|---|
| pass | B |
| current UTC timestamp | 2026-07-09T18:45:10Z |
| model | gpt-5.6-sol |
| reasoning_effort | max |
| evidence_manifest | EB-2026-07-10-v1.1 |
| base commit | bf1cf09d91e1c77a528a46d5bff456f717105ebf |
| repository base | G-perturb repo root (local absolute path redacted) |
| evidence integrity | E02、E03 依第 3.2 節 canonicalisation 重算後雜湊相符；E04–E21 全部通過 manifest SHA-256 |
| blind-review boundary | 未查看 Pass A、Pass C、方法文件第 1–2 與第 4–16 節、其他儲存庫檔案或未封存外部內容；X01–X04 僅視為識別碼 |

本審查採證據驗證框架，把「凍結證據直接顯示的事實」與「由該事實導出的統計推論」分開。E19–E21 視為擬議升級契約；E04–E18 視為其要取代的舊契約。已由 E19–E21 明確修正的方向，例如 guide nested within target、condition 為 fixed domain、無 identical-spec replicate 時 floor=not_identifiable、CCC/Pearson 僅為 diagnostics，不重複列為新 finding。

## 2. Executive assessment

**初步判定：blocked。不選定候選方法。**

擬議計畫的方向正確，但仍有三個 P0：

1. 44.6 GB joint pseudobulk 不在凍結證據包中，無法實證檢查 target-level grid、缺格、NTC coverage 或設計矩陣秩。
2. kernel/distance 的「分量」尚未取得可加總 variance-component 詮釋；任意 1 − CCC 不得直接改稱變異占比。
3. E12 的 run 配置使 run 在完整 donor×condition 交互作用模型中共線；R2 三條件共同支撐只剩兩位 donor。

因此三類 profile 候選均只能進入 synthetic recovery，不能先宣告 primary。

## 3. Coverage matrix

| 審查領域 | 凍結證據 | 審查結果 | 對應 finding |
|---|---|---|---|
| 可交換性與受限制隨機化 | E12 analysis/data/raw/sample_metadata.suppl_table.csv；E13 analysis/data/raw/sgrna_library_metadata.suppl_table.csv；E20–E21 | 已要求 restricted permutation，但沒有逐 estimand 的 null、交換單位、block、殘差交換條件或有限置換解析度 | B-004 |
| matched-NTC 與 measurement error | E11 analysis/data/raw/data_sharing_readme.md；E14 analysis/data/raw/guide_kd_efficiency.suppl_table.csv；E09 analysis/data/CODEBOOK.json | E14 的 NTC 是 condition-wide pool，不能代替 donor×condition×run matched NTC；共享 NTC 所誘發的 contrast covariance 尚未定義 | B-005 |
| 高維基因相依 | E09 顯示既有 DE profiles 約 10,282 genes；E11 顯示 pseudobulk 18,129 genes | 計畫承認基因相關，但尚未指定 covariance operator、正則化、target-blind basis 或 distance-concentration 診斷 | B-006 |
| selection、贏家詛咒與 FDR | E05 docs/design.md；E11；E20–E21 | 舊設計曾依顯著基因算 agreement；新契約要求 atlas-wide 與 stage-wise FDR，但未定義檢定家族、screening hypothesis 或 selective procedure | B-008 |
| validation leakage | E05；E08 analysis/data/DATA_AND_ASSUMPTIONS.md；E21 | 舊設計擬用同一 validation 校準權重與宣稱預測能力；新契約禁止重複使用，但 bundle 缺 validation target overlap 與 frozen split | B-010 |
| 計算可行性 | E02 Issue #9；E03 Diagnosis；E09 | 已禁止 densify 與 target² distance matrix，但沒有候選方法的 pilot benchmark、記憶體、暫存空間或 wall-clock gate | B-011 |
| additive 與 non-Euclidean 詮釋 | E16–E17；E20–E21 | 新契約撤回 CCC 的預設分解地位是正確方向；但 kernel/distance component 的數學定義及 PSD、位置與離散度分離仍未完成 | B-002 |
| 稀疏 facet、shrinkage 與負分量 | E12–E13；E08；E16 | 2-guide/4-donor 資訊量極低，Fay–Herriot direct variance、linking model、boundary inference 與負分量政策均未操作化 | B-007 |
| missing cells 與 common support | E11–E13 | sample-level run 結構已知，但 target×guide 層級缺格未知；不得補零或假定 missing at random | B-001、B-003 |
| gene-wise 與 pathway 次層 | E02；E20–E21 | 兩階段 effect-plus-covariance 與 CAMERA/ROAST/FRY 的方向已列出，操作層契約仍不足 | B-005、B-008、B-009 |

## 4. Findings

| ID | pass | severity | finding | evidence | affected claim | proposed correction | disposition | verification |
|---|---|---|---|---|---|---|---|---|
| B-001 | B | P0 | **additional-evidence：joint pseudobulk 未在 bundle，完整 crossed programme 尚不能通過實證 identifiability gate。** | **直接：**E02 Issue #9 明列尚未下載 GWCD4i.pseudobulk_merged.h5ad；E11 analysis/data/raw/data_sharing_readme.md 只提供 schema；E20 openspec/changes/audit-complete-methodology/design.md 把下載列為 non-goal。**推論：**無法確認 row uniqueness、實際 targeting/NTC grid、缺格機制或逐 target rank。 | 完整 target×guide×donor×condition profile decomposition；任何 estimator selection | 建立新版 manifest，封存 object checksum、shape、CSR/count audit、所有必要 .obs 欄位、逐 block NTC 數量、逐 target coverage 與設計秩輸出；依 frozen-evidence policy 重跑受影響 blind pass。 | blocked | 新 manifest 必須證明 counts 非負整數、row key 唯一、guide→target 一致、每個使用中的 donor×condition×run block 有 NTC，並逐 target 列出 estimable columns、rank、condition number、缺格與 reason code；在此之前只能標 design-specified。 |
| B-002 | B | P0 | **尚未建立 non-Euclidean distance shares 與可加總 variance components 的等價性。** | **直接：**E16 openspec/changes/generalizability-decomposition/design.md 曾鎖定 1 − CCC；E17 要求非負 shares 加總為 total dispersion；E21 只要求比較 kernel/distance 且把 CCC 降為 diagnostic。**推論：**1 − CCC 的 pair-specific denominator 並未被證明產生 squared-Euclidean distance；double-centred Gram matrix 可能非 PSD。PERMANOVA 亦可能混合中心位置與群內離散度。 | headline facet variance shares、additivity、D-study | 分開定義 Euclidean/Hilbert trace components、RKHS sums of squares、純 diagnostic distances。Kernel 必須預先固定且證明 PSD；不平衡設計固定 marginal 而非順序型 partition；另做 PERMDISP。無證明時只能稱 distance-based attribution，不能稱 variance component。 | blocked | 形式證明或數值 gate：所有測試矩陣的最小特徵值不得低於總 trace 的 −1e−8；已知 Euclidean component truth 的絕對 bias 須通過 recovery gate；純 dispersion-null 情境不得產生位置效應。 |
| B-003 | B | P0 | **run、donor×condition interaction 與共同支撐無法同時由現有 sample layout 分離。** | **直接：**E12 有 12 個 donor×condition samples；Rest／Stim8hr 的 D1、D2 在 R1，D3、D4 在 R2；Stim48hr 全在 R2。**重算：**additive donor+condition+run 為 rank 7/7，但 donor×condition+run 為 rank 12/13；加入 run 沒有新增秩。R2 三條件共同支撐只有 CE0008678、CE0006864 六個 cells。 | donor heterogeneity、condition effects、run component、完整四 donor fixed-domain average | 每個 estimand 明列允許的 interaction 與支撐族群。四 donor 分析只能在明確 additive restriction 下進行；三條件 common-support sensitivity 固定為 R2 的兩 donor，並標示 two-donor panel。缺格不得補零；需另做 selection/MNAR sensitivity。 | blocked | 對每個 target 的實際 pseudobulk 設計矩陣做 rank 與共線診斷；任何宣稱的 component 必須有新增秩。完整結果與 R2-common-support 結果均需輸出，超出支撐的 condition claim 必須 fail closed。 |
| B-004 | B | P1 | **restricted permutation 只有名稱，沒有可審計的交換群。** | **直接：**E13 證明 guide nested within target 且 guide 數不平衡；E12 證明 run block 不平衡；E20–E21 要求 restricted permutation，但未指定每個 null 的可交換單位、strata、殘差化方法或 heteroskedasticity 條件。 | kernel/distance p-values、component tests、NTC null、stage-wise screening | 為每個 estimand 定義 sharp/weak null、交換單位與交換群。禁止跨 target、run 或 donor×condition block 換標籤；若使用 Freedman–Lane，需證明 reduced-model residual 可交換，否則改用 block/cluster wild bootstrap。 | blocked | 列出每個檢定的 admissible permutation 數與最小可達 p-value；在 E12-like confounding、缺格、異變異及共享 NTC null 下，type-I error 通過定量 gate。置換數不足時使用 exact p-value 並揭露解析度。 |
| B-005 | B | P1 | **matched-NTC effect 與第一階段 measurement-error covariance 未操作化，gene-wise 第二階段因此可能把估計值當成獨立真值。** | **直接：**E11 說 pseudobulk 有 count、run、guide_type；E14 的 ntc_n 在每個 condition 只有一個全域值，且 E11 定義它為 across-all-samples NTC；E09／E11 的 marginal products 只有 lfcSE，沒有跨 guide、gene、target 或 condition covariance。**推論：**共用同一 NTC reference 的 contrasts 必然共享誤差。 | profile precision weighting；gene-wise two-stage model；CI、sign probability、false-sign control | 在 donor×condition×run 內聯合建模 targeting 與 NTC counts，保留 library offset、overdispersion 與 contrasts。輸出 effect vector 及完整或經驗證的 low-rank covariance，包含共享 NTC 項。第二階段以 GLS／measurement-error likelihood 使用該 covariance，不得只用對角 lfcSE²。 | blocked | 每個 block 有足夠 NTC，否則 reason code；analytic covariance 與 block bootstrap covariance 一致；NTC-vs-NTC、95% coverage、type-I error 通過定量 gate。 |
| B-006 | B | P1 | **高維基因相依尚無可執行契約；三種候選都可能在不同方式下失效。** | **直接：**E09 顯示現有 profile 約 10,282 genes；E11 顯示 joint pseudobulk 18,129 genes；E08 已承認 co-expression 使有效自由度遠低於 gene count。E20 僅列出比較準則。 | profile norm、precision weights、kernel bandwidth、functional basis、uncertainty | 先凍結 target-blind expression/technical universe；由 NTC 或 cross-fit training data 估計 shrinkage covariance／factor basis。禁止 naïve gene permutation、未正則化的全 p×p covariance 或依 DE significance 選 features。每個候選都需報有效秩與 distance concentration。 | blocked | 在獨立、latent-factor、block-correlated、稀疏 pathway 與 dense signal 情境分層驗證 type-I、bias 與 coverage；feature/basis 改變不得導致未揭露的 component reversal。 |
| B-007 | B | P1 | **2 guides／4 donors 下，target-level shrinkage 可能由 linking assumption 主導；負分量政策亦未解決。** | **直接：**E13 解析得到 163 targets 有 1 guide、12,440 有 2、50 有 3、1 有 4；E12 只有 4 donors。E08 明列 cross-target exchangeability 是 partial-pooling 假設；E16 曾規定負 moment component 截為零。E20 仍把 direct estimate 與 covariance 來源列為 open question。 | target-level R_dep,t、Fay–Herriot、CI、D-study、single-guide outputs | 預先定義 direct estimator、抽樣 variance/covariance、bounded link 與 linking model；允許 target-class mixture 或 robust prior，並做 prior sensitivity。Hyperparameters 在 guide/target cross-fit 外估計。保留 unconstrained negative estimate 作診斷；constrained fit 使用明訂 estimator 與 boundary-aware bootstrap，不得事後截零再重新正規化。 | blocked | zero、near-zero、heterogeneous target classes、single-guide 與 heavy-tail simulations 均達 coverage gate；高 sampling variance 必須單調增加 shrinkage；D-study 僅對可識別且非負的分量輸出，曲線必須單調。 |
| B-008 | B | P1 | **selection、贏家詛咒、atlas-wide 與 stage-wise/selective FDR 尚未形成單一檢定樹。** | **直接：**E05 建議以至少一 guide 顯著的 genes 算 agreement；E11 確認存在 guide_correlation_signif；E21 改要求 target-blind universe、atlas-wide 後 stage-wise error control，但未指定 screening null、families、weights 或 selective procedure。 | top-target ranking、gene-wise discoveries、condition contrasts、pathway claims | 凍結 expression/QC-only gene universe 與所有權重。先定義 atlas omnibus family，再定義 target screen 與 selected target 內的 gene/condition family；使用事先指定的 stage-wise 或 selective-FDR 方法。Per-target BH 僅 exploratory。Ranking CI 與 validation 必須由 guide cross-fit 或獨立 holdout 估計。 | blocked | 全域 null、稀疏 alternative、效果導向 missingness 與 top-k selection simulations 通過 FDR、false-sign 及 held-out calibration gates；完整 family tree 與 adjusted p-value 來源可重現。 |
| B-009 | B | P1 | **CAMERA 與 ROAST/FRY 雖已分開命名，兩種 null、輸入與 multiplicity 契約仍不完整。** | **直接：**E20–E21 要求 Hallmark primary、CAMERA competitive、ROAST/FRY self-contained，但未固定 gene-set release、ID mapping 結果、contrast、rotation unit、重疊 pathway 家族或兩層結果的允許措辭。 | pathway secondary interpretation | CAMERA 明列 competitive null：「set 內 genes 不比 set 外更相關」；ROAST/FRY 明列 self-contained null：「set 內無整體效應」。兩者使用相同 target-blind universe 與預先指定 contrast，但分開 FDR family 與報告，不合併 p-values。Rotation 必須沿獨立 pseudobulk/block 單位，不得旋轉 genes。 | blocked | 合成情境至少包含「全 transcriptome 同幅位移」與「僅 pathway-specific 位移」：前者可使 self-contained 顯著但 competitive 不顯著；後者才容許兩者同時有力。若兩方法被解讀為同一假設則驗證失敗。 |
| B-010 | B | P1 | **additional-evidence：無法證明 external validation 不洩漏，且目前只有 K562 transportability 的可用敘述。** | **直接：**E05 擬用 validation outcomes 校準 domain weights 與 threshold，並同時宣稱預測 independent replication；E08 說 Th1Th2 table 不可得、K562-only 且 partial；K562 與任何 T-cell validation records 均未列入 E01–E21。E21 只規定 nested holdout 原則。 | reliability→replication、外部驗證、threshold tuning | 新 manifest 封存 validation data、target overlap、批次、donor、endpoint 與 checksum。任何調參、method selection 或 threshold calibration 只能使用 tuning targets；untouched validation 以 target 為分割單位，樣本不足時使用 nested cross-validation 並放棄「獨立」措辭。 | blocked | Frozen split hash 證明同一 target 不跨 tuning/test；報告有效樣本數與 CI。K562 只能標 cross-cell-type transportability；獨立 T-cell perturbation 才能標 same-cell-type replication；arrayed assay 與 biological relevance 分開。 |
| B-011 | B | P2 | **44.6 GB joint pseudobulk 與 1.6 TB fallback 沒有候選別的 benchmark gate。** | **直接：**E02／E03 記錄約 44.57 GB pseudobulk 與約 1.6 TB cell-level fallback；E09 顯示既有 16.79、29.42、16.87 GB H5 products。E02 只規定 backed/chunked 及禁止全域 target² matrix，沒有可驗收 budget。 | pipeline feasibility、候選方法公平比較、cell-level fallback | 三候選均以相同 1% 與 10% shard benchmark；只准 backed sparse I/O、block sufficient statistics、low-rank covariance 或線上 kernel aggregation。禁止 densify、p×p covariance 及 n_target² matrix。Cell-level rebuild 維持條件式 fallback。 | blocked | 固定硬體後，peak RSS 小於 70% 可用 RAM、scratch 小於 2 倍 input、1%→10% scaling exponent 不大於 1.2，且 full-run extrapolation 落在預先登錄 wall-clock budget；中斷可續跑且 checksum 一致。 |

## 5. 候選 profile 方法：失效模式與暴露情境

**本 pass 不選 winner。**候選方法只能依預先登錄的 synthetic loss function 排序；不得用 K562 或其他 external validation 表現事後挑選。

| 候選 | 可合理支持的詮釋 | 主要失效模式 | 能暴露失效的 synthetic scenario | 必要通過條件 |
|---|---|---|---|---|
| **(i) precision-weighted multivariate linear decomposition** | 在 full-rank、Euclidean/Hilbert response、已知或一致估計 measurement covariance 下，可用 trace 建立 additive components | p 遠大於 n 時 covariance 奇異；只用 diagonal precision 會重複計算相關 genes；共享 NTC covariance 遺漏；heavy tails／稀疏 outliers 破壞估計；完整 interactions 在 E12-like layout 不可識別 | 18k genes 由 20 個 latent factors 驅動，加上共享 NTC、t3 tails、guide-specific scale、E12 run layout、MNAR missing cells | component bias、coverage、type-I 均過 gate；low-rank approximation 改變不造成 component reversal；rank gate 逐 target 通過 |
| **(ii) kernel/distance-based restricted permutation** | 若 kernel PSD 且交換群有效，可支持 RKHS location attribution 與受限制檢定；未經證明不等於 classical variance components | 非 Euclidean distance 產生負 eigenvalues；PERMANOVA 混淆中心位置與離散度；不平衡資料產生順序依賴；有效 permutation 太少；高維 distance concentration | 真正 centroid 完全相同但 guide 群離散度不同；另加入 1−CCC indefinite Gram、single-guide、run confounding 與缺格 | PSD/eigen gate、PERMDISP、marginal partition 與 null calibration 全數通過；若只偵測 dispersion，不得回報 location component |
| **(iii) robust hierarchical functional modelling** | 可聯合處理 heavy tails、measurement error、target shrinkage 及 functional covariance，並輸出完整不確定性 | 2 guides／4 donors 下 prior 主導；target population 多峰時 exchangeability 失敗；basis truncation 漏掉稀疏 pathway signal；MCMC/VI coverage 不準；計算成本最高 | target 分為 dense-factor、sparse-pathway 與 null 三類；t3 errors、outliers、single-guide、弱 KD、E12 confounding 與 informative missingness | 分層 prior sensitivity、simulation-based calibration、held-out predictive calibration 及 compute gate 通過；不得以 posterior 平滑掩蓋 rank deficiency |

CCC 與 Pearson 只保留作 agreement diagnostics。若要升格為 factorial decomposition，必須另提供可加總性、identifiability、measurement-error correction 與 synthetic recovery 的形式或實證證明。

## 6. Secondary-layer audit

### Gene-wise two-stage effect-plus-covariance

可接受的最低契約是：

1. **第一階段：**在 donor×condition×run block 內，以 NB quasi-likelihood 或 voom/limma 對 targeting 與 matched NTC counts 建模，產生每個 target×guide×donor×condition×outcome-gene 的 effect、直接 condition contrast 及 covariance。
2. **Covariance：**至少包含共享 NTC、同 pseudobulk normalization、跨 condition donor，以及 outcome-gene correlation。若無法保存完整矩陣，low-rank/block approximation 必須由 synthetic coverage 證明足夠。
3. **第二階段：**把第一階段 effect 視為帶已知估計誤差的 response，而非原始觀測；guide nested within target；跨 target／outcome gene partial pooling 的 linking assumptions 需預先登錄。
4. **Dependability：**使用預先權重的 summed signal／summed error；禁止平均逐 gene reliability ratios。
5. **Multiplicity：**先 atlas-wide omnibus，再對被選 targets 做 stage-wise/selective FDR；一個 condition 顯著、另一個不顯著不得取代直接 contrast。

現行 bundle 未提供完成此契約的 covariance 或 actual joint grid，因此狀態仍是 design-specified。

### Pathway CAMERA 與 ROAST/FRY

- **CAMERA：**競爭型 secondary hypothesis；比較 gene set 與背景 universe，須估計 inter-gene correlation。
- **ROAST／FRY：**自足型 secondary hypothesis；檢定 gene set 內是否有整體方向性效應。
- Hallmark release、gene ID mapping、重複 ID、方向、contrast、universe 及重疊 pathway 處理必須凍結。
- 兩者不得被描述為同一 null 的互相驗證，也不得把同一 CD4 資料所得 pathway 結果稱為 independent validation。

## 7. 必須預先凍結的 falsification gates

以下是本 reviewer 建議的**最低定量門檻**；必須在查看真實 target 結果前凍結。若團隊採不同數值，需先給出理由並留存版本，不能結果出來後調整。

| Gate | 最低要求 |
|---|---|
| Monte Carlo 規模 | 每個 global-null scenario 至少 5,000 replicates；每個 non-null／adversarial scenario 至少 2,000 |
| Type-I error | 在 alpha=0.05 時 point estimate 介於 0.04–0.06，且 95% Monte Carlo binomial interval 包含 0.05 |
| FDR／false-sign rate | 目標 q=0.05 時 point estimate 不大於 0.06，95% Monte Carlo upper bound 不大於 0.07 |
| 95% interval coverage | 整體及預先指定的 support、guide-count、effect-size strata 均介於 0.93–0.97 |
| Component recovery | 真實 share 不小於 0.05 時 absolute bias 不大於 0.02、RMSE 不大於 0.05；真實 zero component 的 median estimate 不大於 0.01 並通過 type-I gate |
| 贏家詛咒 | held-out top-decile effects 的 calibration slope 介於 0.9–1.1；不得使用 training effect 重新定義 top decile |
| D-study | 每條已報告 point curve 隨 guides 或 donors 增加皆不得下降；投影 coverage 同樣達 0.93–0.97 |
| 候選分歧 | 任兩候選 central share 差異大於 0.05 或超過兩倍 combined Monte Carlo SE 時，強制輸出 disagreement diagnosis，不得挑較漂亮結果 |
| Compute | 1% 與 10% pilot 符合 B-011；任何 densification、全 p×p covariance 或 target² matrix 立即 fail |

合成資料至少需交叉涵蓋：global null、已知 additive components、zero/boundary components、latent-factor 與 block-correlated genes、heavy tails、zero inflation、低 counts、弱 KD、1–4 guides、4 donors、single-guide、E12 run layout、shared NTC、缺格、MNAR viability loss 及 significance-based feature selection。

## 8. 必做 controls 與不洩漏 validation

- **NTC-vs-NTC：**在每個 donor×condition×run 內，把 NTC cells／guides 分成互斥 pseudo-target 與 reference pools，匹配 targeting 的 cell-count 與 library-size 分布，執行完整 pipeline。不得讓同一 NTC observation 同時出現在兩側。

- **Guide cross-fit：**兩 guide targets 以 guide A 做 feature selection、tuning 與 hyperparameter estimation，guide B 只做評估，再交換；3–4 guide targets 做預先固定 folds。Single-guide targets 保留於最終輸出，但不能當 cross-fit 成功證據。

- **Leave-one-donor-out：**進行四次完整 refit，每次連 shrinkage hyperparameters 都只用其餘三 donor 估計。報告 component shift、rank shift、hit-call flip 與 CI，不得把四 donor 敏感度外推為人口 generalizability。

- **Common-support sensitivity：**以 R2 中具有三條件的 CE0008678、CE0006864 作固定 sensitivity population。差異容許界線應在 target 分析前由 NTC-vs-NTC distance 分布凍結；超過界線即標 run/support-sensitive。

- **External evidence taxonomy：**
  - 獨立 T-cell perturbation、獨立 targets／批次：same-cell-type replication
  - T-cell arrayed bulk／flow 且 endpoint 不同：assay translation
  - K562：cross-cell-type transportability
  - pathway、疾病關聯或文獻：biological relevance
  - 同一 CD4 dataset 的 gene/pathway 分析：internal sensitivity/interpretation

任何資料一旦參與 metric、prior、threshold、gene universe 或候選方法選擇，就屬 tuning data；只有 target-level 隔離且從未參與上述步驟的部分可稱 untouched validation。

## 9. Final verdict

# blocked

理由：

1. B-001、B-002、B-003 為未解除的 P0：actual joint grid/rank 缺席、non-Euclidean component 詮釋未成立、run 與 donor×condition interactions 仍不可分。
2. B-004 至 B-010 的 P1 會直接改變 type-I error、coverage、FDR、target shrinkage、pathway 措辭與 validation claim。
3. synthetic recovery、NTC controls、guide cross-fit、leave-one-donor-out 及 common-support sensitivity 均尚未執行。
4. 三種 profile candidates 都有可被目前設計觸發的失效模式；目前沒有證據支持提前指定 winner。
5. 解除 additional-evidence findings 必須建立新版 manifest 並重跑受影響 blind pass，不能把新證據併入本次 EB-2026-07-10-v1.1 後沿用 Pass B 結論。
