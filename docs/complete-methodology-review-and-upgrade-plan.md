# 完整方法學審查與升級計畫

> **狀態：blocked**  
> **審查日期：2026-07-10（Asia/Taipei）**  
> **Evidence manifest：`EB-2026-07-10-v1.1`**  
> **適用 change：`audit-complete-methodology`；下游 change：`generalizability-decomposition`（#8）**

本文件是 #8 統計核心恢復實作前的方法學契約。`blocked` 目前表示三輪指定模型審查與實證資料 gate 尚未完成，不表示以替代模型或未檢查的資料假裝通過。除非本文件最後達到 `approved`，#8 的統計核心維持暫停。

## 1. Executive decision summary

方法方向固定為：joint pseudobulk 是完整設計的最低主要輸入；profile-level 是主要分析；gene-wise 與 pathway-level 分別是敏感度分析與生物學解釋。邊際 h5mu 只可作降級比較，不可重建 joint guide-by-donor interaction。若沒有 identical-spec replicate，replication floor 必須標為 `not_identifiable`。

本文件只有兩種最終狀態：

- `approved`：三個獨立 `gpt-5.6-sol`／`max` pass 均有效，全部 P0/P1 finding 已驗證為 `resolved` 或 `rejected-with-evidence`，16 章與資料、推論、驗證契約互相一致。
- `blocked`：指定模型無法執行、任一 pass provenance 不完整、任一 P0/P1 仍為 `blocked`、或必要資料 gate 尚未能支持對應主張。阻擋時仍可交付文件，但不得恢復 #8 統計核心。

## 2. Current-plan audit

Issue #9 Diagnosis 的根本原因是現有計畫在確認 observation-level measurement design 與可識別性之前，先鎖定 estimator、輸入檔與交付主張。最重要的既有風險是：

1. `by_guide.h5mu` 與 `by_donors.h5mu` 是分別邊際化的 DE products，不能取代 joint guide×donor observations。
2. guide nested within target，不是可與 target 完全 crossed 的 facet。
3. guide pair 或 donor split-half 不是 identical-spec replicate，不能識別 assumption-free residual floor。
4. run 與 donor／condition 部分混淆；目前 metadata 沒有相同 target、guide、donor、condition specification 的獨立 run replicate。
5. CCC／Pearson 是 agreement diagnostics；未經額外證明，不具可加總 factorial decomposition 的解釋。

以上是A／B red-team均要求修正的起始主張；本文件已把修正寫入normative contract，但actual joint data、simulation與validation gates仍未實證通過。

## 3. Data and provenance

### 3.1 Frozen evidence policy

Pass A 與 Pass B 只能使用同一份 `EB-2026-07-10-v1.1`。各 reviewer 可以指出缺少證據，但只能新增 `additional-evidence` finding，不得自行瀏覽其他 repo 檔案、網路內容或改變原 pass 輸入。新增證據若獲准，必須建立新 manifest 版本並重新執行受影響的 blind pass；不得沿用舊 pass 冒充相同輸入。

Manifest 的 repository base 是 `<repo root>`；Git remote 是 `git@github.com:kiki830621/G-perturb.git`；base commit 為 `bf1cf09d91e1c77a528a46d5bff456f717105ebf`。`tracked@commit` 表示可由該 commit 重建；`working-tree@base` 與 `gitignored-local@base` 另以 SHA-256 固定內容。

### 3.2 Evidence manifest `EB-2026-07-10-v1.1`

版本 `v1.1` 沒有改變任何 evidence body 或 repo file；它補上可重做的 Issue body canonicalization，並明訂 reviewer 只能從本文件讀取第 3 節 manifest，不能把仍在整合的其他章節當成 blind-pass evidence。E02／E03 的 SHA-256 是下列 `gh --jq` stdout bytes（UTF-8 body 加上 `gh` 輸出的一個結尾 LF），不是去除結尾 LF 後的 body bytes：

```bash
gh issue view 9 --json body --jq .body | shasum -a 256
gh issue view 9 --json comments --jq '.comments[] | select(.url=="https://github.com/kiki830621/G-perturb/issues/9#issuecomment-4928187622") | .body' | shasum -a 256
```

| ID | 類型／版本狀態 | Repo path 或穩定識別 | SHA-256／識別資訊 | 審查用途 |
|---|---|---|---|---|
| E01 | Git snapshot | repository base | `bf1cf09d91e1c77a528a46d5bff456f717105ebf` | 所有 tracked evidence 的共同版本 |
| E02 | Issue body | [GitHub Issue #9](https://github.com/kiki830621/G-perturb/issues/9) | body SHA-256 `c47f2b8e72bc0b6f8aaf10e4a3a8a26d60cb414b22ba523a46395ee3fc83a420`，擷取日 `2026-07-10` | owner 目標、範圍、驗收條件 |
| E03 | Issue comment | [#9 Diagnosis comment](https://github.com/kiki830621/G-perturb/issues/9#issuecomment-4928187622) | comment ID `4928187622`；created `2026-07-09T18:14:16Z`；body SHA-256 `2e7fdc0d2fa90374ef9abc3220b56f40f9e953d7cad8960a5174bede31999600` | root cause、evidence list、風險與策略 |
| E04 | tracked@commit | `README.md` | `021368e209efaf315b0d4cb5b23d500b852409f5fcd7d29eb9ac516a2f725090` | 專案主張與輸出邊界 |
| E05 | tracked@commit | `docs/design.md` | `54ca28c4ecc13d2f849247c6adac1d51c82df6a23bdd21f1046f5f18279fcadc` | 現有模型、facet 與 validation 設計 |
| E06 | tracked@commit | `docs/README.md` | `8b65db8cee58345e19c6f60bfb8be3a2ece9f238f4aeb8c8c640d9ad726b97f2` | 文件入口與現況敘述 |
| E07 | tracked@commit | `analysis/data/README.md` | `860fd3b4b2d54895b3bb8e2a6ffa5d0e94562e9e3f28108a0fd6f99266b387a9` | released artifacts、來源與既有 facet mapping |
| E08 | tracked@commit | `analysis/data/DATA_AND_ASSUMPTIONS.md` | `8920a08262c4111e02624923dd3cd290128fc79617e3e1322f4886afd30032ee` | 既有 data-scope 決策與假設 |
| E09 | tracked@commit | `analysis/data/CODEBOOK.json` | `313225ef35fbb1d1cc5704f86e74fc6530906d38afc6d448bfbb6de8b4d2b817` | 欄位、modality 與已知 coverage |
| E10 | tracked@commit | `analysis/data/fetch_data.sh` | `6dfa95193d318bedc1e73ff9d3221229091fdfe541f84c3b8f915803b103cbcc` | released data URL 與下載範圍 |
| E11 | gitignored-local@base | `analysis/data/raw/data_sharing_readme.md` | `9275bad99701534e109691f2ce6ff8c474dacb3912e9a6f22cbaa009237ceab7` | joint pseudobulk 與 marginal h5mu schema 說明 |
| E12 | gitignored-local@base | `analysis/data/raw/sample_metadata.suppl_table.csv` | `175a70bef0aca270d49cac278fc1ce02f18c43afb18791a6c13574fba51bad07` | donor×condition×run support 與 replicate audit |
| E13 | gitignored-local@base | `analysis/data/raw/sgrna_library_metadata.suppl_table.csv` | `00a1bec2afc2082fc79765531696d7e22672a8ba904ea54c035858f425a657a8` | guide→target nesting與 targeting／NTC metadata |
| E14 | gitignored-local@base | `analysis/data/raw/guide_kd_efficiency.suppl_table.csv` | `75929bef741f87a944838fe3638fe3eaeef881c14a6653bab96f4b5df899aee3` | KD efficiency covariate與 data-contract drift |
| E15 | tracked@commit | `openspec/changes/generalizability-decomposition/proposal.md` | `c79a943fdef6f91bdbb05fab238d5ed3b0927afab79d403af1168103281dd5b4` | #8 scope 與既有承諾 |
| E16 | tracked@commit | `openspec/changes/generalizability-decomposition/design.md` | `2e81271cc38f9adb5d336ed2bfea49abd24c926e3668086c3c8e48ec561a16d3` | #8 方法決策與 apply checkpoint |
| E17 | tracked@commit | `openspec/changes/generalizability-decomposition/specs/generalizability-decomposition/spec.md` | `155a71f70fd7ca4049a51fea0bfacbbc6295566c3f5b78e9a4fef5586fc7b541` | #8 normative requirements |
| E18 | tracked@commit | `openspec/changes/generalizability-decomposition/tasks.md` | `db782bcba4be13c86223305503f6db90a3fae2f56db1406d8c9b39776e97050c` | #8 已完成、暫停與待修正工作 |
| E19 | working-tree@base | `openspec/changes/audit-complete-methodology/proposal.md` | `d172bcdd2f939cf86b4f70fd76d5943dda6917fbd5b30f6c8ac1f25ca768a1db` | 本次 audit scope |
| E20 | working-tree@base | `openspec/changes/audit-complete-methodology/design.md` | `7d3b12dee25ca2e548cd5ae0ac3e13fa07ada14db7e735a887680011b47e1f73` | 三輪審查與 16 章契約 |
| E21 | working-tree@base | `openspec/changes/audit-complete-methodology/specs/methodology-audit/spec.md` | `d7828ae95df68df54dc62aedeab7fc9d6108e0c6dc5207561c6682032b4de70c` | 可驗收 scenarios |

### 3.3 Dataset metadata 與外部來源識別

以下 URL 是 provenance identifier；reviewer 不得把未封存的即時網頁內容當成 `EB-2026-07-10-v1.1` 證據。若必須引用網頁內容，應提出 additional-evidence finding 並要求下一版 manifest 封存內容與 checksum。

| ID | 來源 | 固定用途 |
|---|---|---|
| X01 | `s3://genome-scale-tcell-perturb-seq/marson2025_data/` | released data bucket identifier |
| X02 | `https://genome-scale-tcell-perturb-seq.s3.amazonaws.com/marson2025_data/` | `fetch_data.sh` 使用的 HTTPS mirror |
| X03 | `https://www.biorxiv.org/content/10.1101/2025.12.23.696273v1` | Zhu et al. preprint identifier；本 bundle 未封存全文 |
| X04 | `https://github.com/emdann/GWT_perturbseq_analysis_2025` | companion analysis repository identifier；本 bundle 只含已下載且有 checksum 的 E14 |

### 3.4 Diagnosis evidence completeness check

Issue #9 Diagnosis 的 evidence list 已逐項映射：現有 README／design（E04–E06）、data-sharing readme（E11）、data assumptions 與 codebook（E08–E09）、sample metadata（E12）、guide metadata 與 KD efficiency drift（E13–E14）、#8 proposal／design／spec／tasks（E15–E18），以及本 audit 的 normative contract（E19–E21）。因此 A／B 不會因輸入清單不同而產生假性共識。尚未下載的 44.6 GB joint pseudobulk 與 lane-level artifact 明確不在 bundle；其 schema、rank 或 replicate 結論只能標為待執行 gate。

### 3.5 Additional-data acquisition priority

Owner已允許在方法需要時增加資料；追加原則是先說明哪個不可識別quantity會因此取得新variation，再下載或請求資料。優先順序如下：

| Priority | Additional artifact | Information gained | If unavailable | Provenance／review consequence |
|---|---|---|---|---|
| P0 core | `GWCD4i.pseudobulk_merged.h5ad`約44.6 GB | joint guide×D4×C3×run counts、matched NTC與actual grid/rank | 只能`marginal-only`，不執行完整profile／gene／pathway | 固定URL、ETag、bytes、SHA-256、schema output；建立新manifest並重跑A/B受影響pass |
| P0 conditional floor | 作者提供的lane／library／biological-repeat level pseudobulk與lineage | identical-spec replicate variation與scope-specific floor | floor維持`not-identifiable`；不阻止其他可識別claims | 需independence audit；約1.6 TB cell-level rebuild只在作者artifact不可得且information gain明確時啟動 |
| P1 external | actual K562、獨立T-cell與arrayed assay target-level tables | transportability、same-cell-type replication或assay translation | 各external estimand=`not-identifiable` | 固定endpoint、eligibility、split與checksum；任何tuning exposure需揭露 |
| P1 guide extrapolation | 新增獨立guides或可重建的guide-design selection frame、KD／off-target covariates | `E-GUIDE-UNIVERSE` out-of-sample calibration | 只報observed-guide consistency | 新guide不能參與method selection；target／guide holdout先凍結 |
| P1 donor population | 更多且有sampling frame的獨立donors／batches | human-donor population estimand | 僅D4 finite-panel wording | 建立新的population estimand；不得把便利樣本直接稱代表性樣本 |
| P2 condition expansion | 額外且有明確domain measure的biological states | 新condition-domain estimand | C3維持fixed domain | 新增state會改estimand ID與weights，不能事後併入C3 score |
| P2 provenance | X04 companion commit／path與immutable KD source | E14 clean-room reproduction | KD只留本地hash-fixed sensitivity，A-013維持blocked | 更新fetch、codebook與environment manifest |

資料增加不能解除設計本身的alias，除非新增observation真正交叉所需facets；例如同一R2下載更多cells不會自動識別R1/R2 target×run effect。任何additional artifact先進quarantine schema audit，不得先查看target結果再決定是否納入。

## 4. Estimands and decision universes

### 4.1 凍結順序與共通集合

Estimator selection 必須晚於本 registry；方法比較不得因結果較漂亮而改寫 object、support、權重或 threshold。任何改動都建立新的 `estimand_id` 與文件版本，不能覆寫既有定義。

- Fixed condition domain：`C3={Rest, Stim8hr, Stim48hr}`；primary fixed-domain weights 固定為 `(1/3, 1/3, 1/3)`。Condition 不代表隨機抽取的未觀測情境。
- Observed donor panel：`D4={CE0008162, CE0010866, CE0008678, CE0006864}`。主要用語只及於這四位 donor；R2 common-support 兩位 donor 另用 `D2_R2={CE0008678, CE0006864}`，不得沿用 D4 estimand ID。
- Profile gene universe：`G_profile` 由 joint pseudobulk 上 target-blind 的 expressed-gene／technical-QC 規則一次固定；不得讀取任何 target 的 DE p-value、effect 或 validation outcome。若 projection／kernel／basis 是學得的，須以 target-level cross-fitting 產生。Gene-wise universe預設固定為`G_gene=G_profile`；若因可重做的count／mapping QC必須另立`G_gene`，就建立新的gene-wise estimand ID與checksum，不可在同一ID下任意切換。
- Primary target decision universe：`U_full` 是通過 joint pseudobulk schema/rank gate、至少兩條可用 targeting guides、D4×C3 必要 cells 與 block-matched NTC 支援的 targets。實際名單與 checksum 必須在資料 gate 後凍結。
- Partial-evidence universe：`U_partial` 收納 single-guide、缺格或只有邊際 evidence 的 targets；它有獨立輸出 tier，不得和 `U_full` 用同一尺度排名。
- Effect direction：第一階段 profile 一律是 `targeting − matched NTC` 的 log-expression effect；正值代表 targeting 後 expression 較 matched NTC 高。Dependability／consistency 分數越高代表跨指定 facets 越穩定，而不是 effect 越大。
- Missingness：禁止補零、以邊際 summary 補 joint cell、或無聲 complete-case。缺格先輸出 reason code；若 restriction 改變 donor、condition、guide 或 gene support，就建立新 estimand ID。
- Uncertainty：每個 estimand 都保留第一階段 shared-NTC sampling covariance；目標層輸出 point estimate、95% interval／simultaneous interval（適用時）、rank uncertainty 與 gate status，不把 sampling uncertainty 當成 facet variance。

### 4.2 Estimand registry

| Estimand ID | Object | Observational unit | Target population／decision universe | Facet status | Aggregation weights | Missingness policy | Uncertainty target | Allowed claim wording |
|---|---|---|---|---|---|---|---|---|
| `E-CS-PROFILE` | Target `t` 在 condition `c∈C3` 的 matched-NTC genome-wide effect profile `θ_tc` | joint pseudobulk target-guide-donor-condition cell；matched NTC 在同 donor×condition×run block 建構 | `U_full`；D4 observed panel；固定 `G_profile` | guide nested within target；donor=D4 fixed panel；condition=fixed named state；run=nuisance；gene=fixed universe | donor 先等權 `1/4`；guide 依預先固定的 precision rule，若 precision gate 失敗則等權且標示 | 任一必要 block／NTC／rank 失敗則該 `t,c` 不估；不得由 h5mu 補值 | `θ_tc` 的聯合 sampling covariance、gene-wise simultaneous coverage 與 profile norm uncertainty | 「在四位已觀測 donor、condition c 與 observed-run 配置下的 target effect profile」；不得稱人口平均、跨 condition 或 replication |
| `E-FD-PROFILE` | Target `t` 在 C3 fixed domain 的平均 profile `θ̄_t=(θ_t,Rest+θ_t,Stim8+θ_t,Stim48)/3` | `E-CS-PROFILE` 的三個 condition vector | `U_full`；D4；C3 等權固定域 | condition=fixed domain；其餘同 `E-CS-PROFILE` | condition=`1/3`；donor=`1/4`；gene weights 在看結果前固定 | 三個 condition 任一不通過即不產 primary fixed-domain estimate；R2-only 另用 `E-FD-PROFILE-R2` | 跨 condition／gene 的完整 covariance與 95% interval | 「三個預先指定 condition 的等權 fixed-domain average」；不得寫成對新 condition 的 generalization |
| `E-FD-PROFILE-R2` | R2 common-support 下的 C3 fixed-domain平均 profile | R2 的兩位 donor×三 condition joint cells | 僅 `D2_R2`；`U_full_R2` | donor=固定兩位 panel；condition=fixed；run=R2 fixed | condition=`1/3`；donor=`1/2` | 缺任一 R2 block即不估 | 與 `E-FD-PROFILE` 相同，但以兩 donor support計算 | 「R2 兩位 donor 的 common-support sensitivity」；不得冒充 D4 replication或主要結果 |
| `E-RANK-REL` | `U_full` 內 target 的相對 dependability排序；latent quantity 是固定域 generalizability functional `R_t^FD` | 每 target 由同一 `E-FD-PROFILE` 與相同 facet design產生一個 estimate | 僅 `U_full`，名單在資料 gate 前後各留版本；排名只在相同 design tier 內比較 | target=fixed decision units；guide=observed nested facets；donor=D4 panel；condition=C3 fixed | 與 `E-FD-PROFILE` 相同；不得依 validation outcome調權 | 任一 target 欠缺共同 design 即不進排名；保留 unranked row與 reason code | rank interval、pairwise `P(R_t>R_s)`、top-k inclusion probability、winner's-curse corrected held-out calibration | 「在同一 U_full、D4、C3 measurement design 內的相對排序」；不得稱絕對可靠或人口排名 |
| `E-HIT-ABS` | 絕對 high-dependability indicator `I(R_t^FD≥0.70)` | 與 `E-RANK-REL` 相同 | `U_full`；threshold `0.70` 在看 target結果前固定；`0.60/0.80` 僅為標示清楚的 sensitivity | 同 `E-RANK-REL` | 同 `E-FD-PROFILE` | 欠缺共同 design 或 interval calibration失敗即 `not_called`，不是 negative | 決策規則固定為 `P(R_t^FD≥0.70)≥0.95`；另報 false-sign／false-call calibration | 「在預先 threshold 與本 measurement design 下通過 high-dependability call」；不得稱跨研究 validated hit |
| `E-DONOR-PANEL` | 每 target 的 D4 donor-panel consistency／heterogeneity | target-guide-donor-condition joint cells | D4 observed panel；可 condition-specific 或 C3 fixed average，須引用 `E-CS-PROFILE`／`E-FD-PROFILE` | donor=四個固定 levels，非 human population random sample；guide nested；condition fixed | D4 等權；C3 等權（若 fixed average） | donor cell 缺失即 target-condition 不通過 primary gate；LODO 是 sensitivity，不重定義主要 estimate | donor contrast／dispersion與 LODO shift 的 interval | 「四位已觀測 donor 間的一致性」；不得稱 human-donor population generalizability |
| `E-GUIDE-OBS` | 同一 target 的 observed-guide consistency | target 內兩條以上 targeting guide 的 matched-NTC profiles | `U_full` 的實際 guides；single-guide target 狀態=`not_identifiable` | guide nested within target；不是 crossed target×guide；KD只作 sensitivity | primary 等權或經預先校準 precision weighting；不得按 agreement結果調權 | 少於兩條有效 guide 就不估 guide consistency，也不以 donor score補替 | cross-fit guide prediction error、consistency interval與 guide-count stratum coverage | 「已觀測 guides 間的一致性」；不得稱 future-guide reliability |
| `E-GUIDE-UNIVERSE` | 從設計機制產生之未觀測 future guides 的 model-based generalization | target 內 observed guides，加上預先定義的 guide design covariates | guide-design universe；目前沒有 probability-sampling／獨立 guide evidence，狀態=`design-specified`且 approval blocker | guide nested random extrapolation；selection／KD／off-target model需明訂 | 依 guide-design population measure；在取得證據前不給數值 | single-guide或無 held-out guide 時不估；不可從 `E-GUIDE-OBS`自動外推 | held-out guide predictive coverage與 calibration slope | 僅在 gate 通過後可稱「對指定 guide-design universe 的 model-based extrapolation」；目前只能稱未識別 |
| `E-REPL-FLOOR` | 相同完整 specification 下獨立 measurement 的 irreducible replication floor | 同 target、guide、donor、condition、run/block specification 的獨立 lane/library units | 只在 identical-spec replicate artifact存在時；目前 merged pseudobulk 無此 dimension | replicate=random measurement units；其他 facets全部固定相同 | replicate等權或依 library precision預先指定 | 無 lane-level replicate時 status=`not_identifiable`；guide pair、donor halves、NTC split均不合格 | replicate residual與最高階 interaction分離後的 interval | 只有 lane gate通過才可稱「identical-spec replication floor」；否則只報 combined highest-order interaction + sampling residual |
| `E-GENE-CS` | 每 target×outcome-gene 的 condition-specific effect與直接 condition contrast | joint pseudobulk counts第一階段 effect+covariance；第二階段measurement-error model | 唯一target-blind `G_gene`及其checksum；`U_full`；D4 | guide nested；donor=D4 fixed；condition=fixed contrast；gene=fixed hypothesis family | 不跨 gene平均 ratio；跨 gene summary使用預先指定 summed signal／summed error weights | 缺格按 hypothesis family reason code；禁止只保留顯著 genes | effect interval、contrast interval、local sign probability、atlas-wide與stage-wise FDR | 「gene-wise sensitivity」；同一 CD4資料不得稱 independent validation |
| `E-PATH-COMP` | CAMERA competitive pathway contrast：set內 genes 的差異訊號是否比固定背景 universe 更強；inter-gene correlation 是須校正的 nuisance structure | `E-GENE-CS` 的全基因 signed moderated statistic | pinned Hallmark primary；Reactome／GO secondary；固定 gene mapping與全分析 universe | pathway=fixed sets；genes相關；condition=fixed contrast | library與 mapping凍結；不依結果刪除背景 genes | mapping／universe不足即 pathway不估並輸出 reason code | pathway effect方向、competitive p-value與該 library內 FDR | 「competitive pathway interpretation」；不得等同 self-contained或外部驗證 |
| `E-PATH-SELF` | ROAST／FRY self-contained pathway contrast：set內整體effect是否為零 | 同 `E-PATH-COMP`，rotation沿獨立 pseudobulk/block units | 同一 pinned libraries，但與 competitive hypotheses分開成 family | 同上 | 同上 | 同上 | directional self-contained p-value與獨立 FDR family | 「self-contained pathway interpretation」；不得與 CAMERA p-value合併或互稱 replication |
| `E-TCELL-REP` | 獨立 T-cell perturbation中，預先對齊 target／endpoint 的 replication estimand | 完全未參與 tuning 的獨立 T-cell targets、donors、batches與 assay observations | 預先凍結的 shared-target universe；目前 actual table不在 bundle，狀態=`not_identifiable` | study／assay為 external facets；target-level split防 leakage | weights依預先 endpoint與study品質規則，不按結果調整 | 無相容獨立T-cell資料即不估；arrayed不同endpoint另列 assay translation | external effect concordance、calibration與 CI | gate通過後可稱「same-cell-type T-cell replication」；目前不得宣稱已驗證 |
| `E-XCELL-TRANSPORT` | CD4→K562 的 cross-cell-type transportability | untouched K562 target-level effects，與 CD4 fixed-domain summary對齊 | 預先共享 targets；K562資料不得參與method／threshold選擇；actual table目前不在 bundle | cell type=external fixed contrast；不是T-cell replicate | shared-target等權或預先 precision weights | join失敗、tuning contamination或endpoint不相容即不估 | transport calibration、rank concordance與 interval | 只能稱「cross-cell-type transportability」；不得稱 T-cell replication或一般 biological validation |

### 4.3 Profile component與dependability functional

為避免不同候選各自發明score，`E-RANK-REL`與`E-HIT-ABS`共用下列latent functional。令`θ_thdc`為target `t`、observed guide `h`、D4 donor `d`、C3 condition `c`在固定`G_profile`與metric `W`下的true matched-NTC profile；primary grid採預先權重形成grand mean`θ_bar_t`。在完整且通過rank gate的grid上，以固定投影／weighted Hilbert ANOVA定義可識別的finite-domain squared-deviation components `A_tk`，其中`k`只含observed-guide、D4 donor、fixed-C3及通過component-basis rank的interactions。

- Signal：`S_t=||θ_bar_t||_W²`。
- Fixed-design instability：`H_t=Σ_{k∈K_FD} A_tk`；`A_t,C`是三個命名conditions的weighted dispersion，不是random-condition variance；guide項只描述observed guides。
- Measurement contribution：`M_t=tr(W P_t V_t P_tᵀ)`，其中`P_t`是同一measurement design的預先投影、`V_t`是含shared NTC的first-stage covariance。Facet heterogeneity不得塞進`M_t`。
- Fixed-domain dependability：`R_t^FD=S_t/(S_t+H_t+M_t)`。分母為0或任一必要component不可識別時，score=`null`而非1；`E-HIT-ABS`再套用§4.2的0.70 decision rule。
- Component display share：`Q_tk=A_tk/(S_t+H_t)`，只在分母正且`A_tk`可識別時輸出；它是本finite grid／Hilbert metric下的descriptive share，不是未觀測population variance。

Unconstrained direct estimators可因sampling correction為負，必須和§9的constrained likelihood結果並列。Atlas summary採ratio of sums：`R_atlas=Σ_t S_t / Σ_t(S_t+H_t+M_t)`，target預設等權；禁止平均`R_t`或逐gene ratios。Condition-specific stability若排除condition dispersion，是不同estimand，須另立ID，不能沿用`E-RANK-REL`。

### 4.4 Estimator linkage 與 claim boundary

後續章節中的 estimator 必須引用上表 ID：profile 候選只估 `E-CS-PROFILE`、`E-FD-PROFILE`、`E-RANK-REL` 或 `E-HIT-ABS`；gene-wise model只估 `E-GENE-CS`；CAMERA與ROAST/FRY分別估 `E-PATH-COMP`、`E-PATH-SELF`。CCC／Pearson只附屬於對應 estimand的 diagnostic欄位，沒有自己的 variance-component claim。

任何輸出若改用 R2-only donor、single-guide、邊際 h5mu、不同 gene universe、不同 condition weights或 validation-tuned threshold，都必須改用新的 `estimand_id`／tier；不得保留原 ID 造成看似可直接比較的結果。

## 5. Identifiability and design-rank audit

### 5.1 Status vocabulary

- `design-specified`：觀測單位、必要變異、檢查與失敗路徑已固定，但 actual analytic object 尚未通過檢查。
- `empirically-passed`：指定版本的 actual object、程式、輸出與 checksum 均存在且 gate 成功。本文件只對 E12 sample layout、E13 guide nesting／guide-count metadata 與 evidence checksum使用此字；沒有任何 joint pseudobulk component 取得此狀態。
- `marginal-only`：證據只支援已邊際化的 agreement／diagnostic；不可寫成 joint crossed component。
- `not-identifiable`：現有 measurement design 缺必要 variation，或 gate 已知無法區分主張中的 quantity；追加資料或限縮 estimand 才能解除。

### 5.2 Fail-closed data gates

Joint pseudobulk 是完整方法的最低輸入。正式實作依序執行，前一 gate 失敗即停止該 target／claim：

1. **Identity／provenance gate**：保存 source URL、ETag、size、SHA-256、object shape、sparse format、software version與 extraction command；bytes或schema漂移就建立新版本。
2. **Schema gate**：必要欄位至少為 target、guide、guide_type（targeting／NTC）、donor、condition、`10xrun_id`、library／lane identifier（若有）、cell count、library size／offset及 outcome-gene count matrix；count必須是非負整數、gene IDs唯一且 mapping可重做。
3. **Key／nesting gate**：`target×guide×donor×condition×run×lane`（依實際可用粒度）唯一；每條 targeting guide只映射一個target；guide nested within target；NTC 不被偽造為 target level。
4. **Matched-control gate**：每個使用中的 donor×condition×run block必須有足夠NTC；targeting與NTC採相同QC及offset。共用NTC產生的contrast covariance必須保存，不能只留下對角 `lfcSE²`。
5. **Coverage／missingness gate**：逐 target輸出 guides、donors、conditions、runs、lanes與完整／缺失cells；禁止補零。至少兩條有效guide才能估 `E-GUIDE-OBS`；primary `U_full` 需 D4×C3與共同NTC支援。
6. **Fixed-effect rank gate**：對每個 estimand建立實際設計矩陣，輸出 columns、rank、condition number、aliased terms與common-support subset。E12-like full donor×condition cell加run模型不得宣稱獨立run component。
7. **Variance-component／kernel gate**：投影掉fixed effects後，檢查component covariance bases／Fisher information／Jacobian rank；kernel須PSD（容許數值誤差下最小eigenvalue不低於總trace的`−1e−8`），distance attribution須固定marginal partition且不依term order。一般fixed-effect full rank不代表variance shares可識別。
8. **Inference gate**：每個null固定exchange unit、strata、admissible permutations與最小p-value；有限交換或異變異不允許時，改用明訂的cluster／wild bootstrap。任何target-specific shrinkage都先取得可驗證的direct sampling covariance。

### 5.3 Claim-to-data identifiability crosswalk

| Claim | Estimand | Observation unit | Required variation | Available evidence | Schema／rank gate | Assumptions | Status | Allowed wording |
|---|---|---|---|---|---|---|---|---|
| Condition-specific matched-NTC profile | `E-CS-PROFILE` | joint target-guide-donor-condition pseudobulk＋同block NTC | target內guides、D4、指定condition；matched block NTC | E11只描述schema；actual merged object未納入bundle | gates 1–7逐target通過；第一階段covariance可重做 | NB／voom mean-variance適當；target×run effect若無法估須限縮 | `design-specified` | 「D4、指定condition、observed-run conditional profile」 |
| C3 fixed-domain average profile | `E-FD-PROFILE` | 三個`E-CS-PROFILE` vectors | 三condition均可估、共同gene／donor support | E12證明D4×C3 samples存在但run不交叉；joint target grid未知 | 三個condition各自通過，再檢查跨condition covariance | weights固定1/3；不外推到新condition | `design-specified` | 「三個預先指定condition的等權fixed-domain average」 |
| R2 common-support average | `E-FD-PROFILE-R2` | R2兩donor×三condition cells | D2_R2在C3均有資料 | E12 metadata已實證確認兩位R2 donors | 與primary相同，但另建兩donor design與ID | 只及於D2_R2；不是四donor結果 | `design-specified` | 「R2兩位donor common-support sensitivity」 |
| Observed-guide consistency／guide component | `E-GUIDE-OBS` | 同target至少兩條guide的joint profiles | target內≥2 guides、D4×C3、共同gene scale | E13 guide nesting與不平衡guide count已通過；actual joint effects未檢查 | nesting、coverage、component-basis rank、cross-fit gate | guides是observed levels；不主張probability sample | `design-specified` | 「已觀測guides間的一致性」 |
| Future-guide generalization | `E-GUIDE-UNIVERSE` | observed與獨立held-out／新增guides | guide-design population與out-of-sample guides | E13無probability selection機制；沒有獨立future-guide set | held-out guide calibration與selection-model gate | exchangeability需依KD／off-target等covariates成立 | `not-identifiable` | 目前只能寫「future-guide generalization未識別」 |
| D4 donor-panel consistency／donor component | `E-DONOR-PANEL` | target-guide-donor-condition joint profiles | 四donors在共同condition／guide support | E12 sample panel已確認；joint target grid未檢查 | donor contrast與component-basis rank；LODO refit | donors是固定observed panel | `design-specified` | 「四位已觀測donor間的一致性」 |
| Human-donor population generalization | 無；需新增population estimand | probability／broad donor sample | 足夠且具代表性的獨立donors | 只有D4；無sampling frame | population model、selection與external calibration gate | D4可交換且具代表性目前無證據 | `not-identifiable` | 不得聲稱human population generalizability |
| Target×condition heterogeneity | `E-CS-PROFILE` vector／`E-FD-PROFILE` | joint target-guide-donor-condition cells | C3各state、共同D4／gene support | E12 layout已知；joint object未檢查 | fixed contrasts與covariance-basis rank | condition是fixed states；run interaction受限制 | `design-specified` | 「C3命名states間的固定contrast／加權heterogeneity」 |
| Random condition variance或新condition projection | 無 | 未觀測condition sample | 從明確condition population抽取更多levels | 只有三個fixed conditions | 需新增condition data與sampling frame | conditions隨機抽樣目前不成立 | `not-identifiable` | 不得使用random `σ²_C`或外推新condition |
| Target×donor heterogeneity | `E-DONOR-PANEL` | joint target-guide-donor-condition cells | D4在共同conditions與guides | E12提供sample support；actual grid未知 | fixed-effect與component-basis rank | target×run可忽略或被common-support限制 | `design-specified` | 「D4 panel內target-specific donor heterogeneity」 |
| Joint guide×donor／更高階interaction | `E-CS-PROFILE`／candidate-specific component | 同一target的guide×donor×condition joint cells | joint而非marginal observations；足夠cells與component-basis rank | merged pseudobulk schema可提供；actual object未檢查 | gates 2–7；缺格時逐target fail closed | component mapping與additivity由synthetic recovery支持 | `design-specified`；若只有h5mu則`not-identifiable` | Gate通過前不得稱完整crossed interaction |
| Guide marginal agreement atlas | `E-GUIDE-OBS` diagnostic | `by_guide.h5mu`各modality的target×condition profiles | 兩個guide modalities與共同target×condition | E09／E11及本地h5mu已固定，但未在本change重跑分析 | modality、target key與gene universe對齊 | 只描述跨donor彙整後agreement | `marginal-only` | 「marginal observed-guide agreement diagnostic」 |
| Donor-pair marginal agreement atlas | `E-DONOR-PANEL` diagnostic | `by_donors.h5mu`六個donor-pair modalities | donor-pair marginal profiles | E09／E11及本地h5mu已固定 | modality、target key與gene universe對齊 | 每modality已跨guide彙整 | `marginal-only` | 「marginal donor-pair agreement diagnostic」 |
| `1−CCC`／Pearson factorial share | 無；diagnostic附屬欄位 | pairwise marginal profiles | 可加總Euclidean／Hilbert geometry與joint design | E16曾鎖定；A-003／B-002指出未證明 | PSD、additivity、term-order invariance與recovery gate | CCC denominator與SNR不混淆，目前無證據 | `not-identifiable` | 只能稱agreement diagnostic，不能稱variance share |
| Precision-weighted Euclidean／multivariate profile components | `E-CS-PROFILE`、`E-FD-PROFILE` | joint profiles＋full sampling covariance | full-rank component bases；regularized gene covariance | 只有設計契約；actual joint effects與covariance缺席 | gates 1–8；low-rank approximation recovery | Hilbert geometry、covariance estimator與first-stage model校準 | `design-specified` | synthetic與actual gates通過後才可稱additive profile components |
| Kernel／distance attribution | `E-CS-PROFILE`或明訂RKHS estimand | joint profiles與restricted exchange blocks | PSD kernel、有效exchange group、location／dispersion可分 | 只有候選契約 | kernel eigen、PERMDISP、marginal partition、permutation gate | kernel在分析前固定；不把dispersion當location | `design-specified` | 未證明等價前只稱distance／RKHS attribution |
| Robust hierarchical functional components | `E-CS-PROFILE`、`E-FD-PROFILE` | joint effects＋sampling covariance |足夠targets作pooling、facet rank、basis support | 只有候選契約 | prior／basis sensitivity、simulation-based calibration、actual rank | cross-target exchangeability與basis adequacy | `design-specified` | 只可稱model-based component，並揭露prior sensitivity |
| Relative target ranking | `E-RANK-REL` | 每target同一design tier的一個profile functional | 共同U_full、facet design、gene universe與calibrated uncertainty | 無actual score；A-001／A-008列為blocker | 每target資料gate＋ranking bootstrap／cross-fit | targets可在同estimand下比較；selection bias已校正 | `design-specified` | 「U_full同design內的相對排序」 |
| Absolute high-dependability hit | `E-HIT-ABS` | `R_t^FD`與其sampling distribution | 固定0.70 threshold、校準interval／posterior、同U_full | threshold已在§4凍結；無actual calibration | data、method、coverage、FDR／false-call gate | decision rule在看結果前固定 | `design-specified` | Gate通過後稱「本design下的high-dependability call」 |
| Single-guide guide reliability | `E-GUIDE-OBS` | 只有一條targeting guide | 至少第二條獨立guide | E13證明存在163個single-guide targets | guide-count gate直接失敗 | donor evidence不能替代guide variation | `not-identifiable` | 「guide facet不可識別」；可保留partial-evidence tier |
| Target-level shrinkage／Fay–Herriot | `E-RANK-REL`／`E-HIT-ABS` | target direct estimate＋sampling covariance | 可識別direct estimate、已校準sampling variance、targets間linking model | 現有bundle沒有direct covariance；E16舊做法未操作化 | direct variance來源、prior/link、boundary bootstrap與cross-fit | cross-target exchangeability與link正確 | `design-specified` | 只可稱model-based shrunken estimate，需揭露unshrunken值與prior sensitivity |
| D-study guides／donors projection | `E-GUIDE-UNIVERSE`或`E-DONOR-PANEL` | 已識別非負components與sampling covariance | 可識別component、明確projection population | guide-universe未識別；donor僅D4 panel | component recovery、monotonicity與projection coverage | 只增加已定義facet levels；condition不作random projection | guide=`not-identifiable`；donor=`design-specified` | Gate通過前不提供future-guide或population-donor曲線 |
| Identical-spec replication floor | `E-REPL-FLOOR` | 同target-guide-donor-condition及其他specification的獨立lane/library | 每spec≥2真正獨立measurement units | E11／E12顯示merged pseudobulk無此dimension | lane identity、independence、rank與residual separation | lanes未共享不可分技術來源 | `not-identifiable` | 「floor不可識別；最高階interaction＋sampling residual合併」 |
| Gene-wise condition effects／contrasts | `E-GENE-CS` | count-derived effect＋full／validated low-rank covariance | target-blindgenes、nested guides、D4×C3與直接contrasts | 只有schema與契約；actual joint fit未執行 | gates 1–8＋atlas／stage-wise family gate | first-stage covariance足夠；pooling model校準 | `design-specified` | 「gene-wise sensitivity」；不得稱獨立validation |
| CAMERA competitive pathway | `E-PATH-COMP` | 全基因signed moderated stats＋inter-gene correlation | pinned sets、完整universe、condition contrast | actual pathway inputs／library checksum未納入 | mapping、universe、correlation與library-FDR gate | competitive null與背景定義固定 | `design-specified` | 「competitive biological interpretation」 |
| ROAST／FRY self-contained pathway | `E-PATH-SELF` | 全基因stats；rotation沿獨立block units | pinned sets、有效rotation units | actual inputs未納入 | mapping、rotation、direction與獨立FDR gate | rotation respects blocks；不旋轉genes | `design-specified` | 「self-contained biological interpretation」 |
| NTC-vs-NTC negative control calibration | `E-CS-PROFILE` pipeline control | 同block互斥NTC pseudo-target／reference pools | 每block足夠NTC、互斥split、完整pipeline | actual joint NTC counts未納入 | matched-control、exchange／bootstrap與null calibration gate | NTC pools可代表technical null | `design-specified` | 只稱internal falsification，不稱replication |
| K562 transportability | `E-XCELL-TRANSPORT` | untouched K562 target-level effect與CD4對齊 | frozen shared targets、endpoint與holdout split | E08只描述partial K562；actual table不在bundle | join coverage、target split、calibration與CI gate | K562未參與tuning | `not-identifiable` | 目前只能寫「K562 transportability尚未實證」；不得稱T-cell replication |
| Same-cell-type T-cell replication | `E-TCELL-REP` | 獨立T-cell perturbation targets／donors／batches | 相容endpoint、完全untouched targets | Th1Th2／獨立T-cell table不可得 | provenance、join、target-level holdout與calibration gate | study／target selection可解釋 | `not-identifiable` | 不得宣稱已完成T-cell replication |
| Assay translation／biological relevance | 需依endpoint新增ID | arrayed bulk／flow或外部文獻／disease evidence | 相容target與預先endpoint | bundle未含actual values | 每類獨立provenance、multiplicity與no-leakage gate | 不同evidence類型不合併成單一criterion | `not-identifiable` | 分別稱assay translation或biological relevance，不稱replication |

### 5.4 Gate consequence

本 change 沒有檢查 44.6 GB actual joint pseudobulk，因此上表任何 joint claim均不得標為 `empirically-passed`。後續一旦加入 actual pseudobulk、lane或external validation資料，必須建立新 evidence manifest，保存每個 gate輸出與checksum，並依 frozen-evidence規則重跑受影響的blind pass；不能在現有A／B結果上直接追加證據。

## 6. Profile-level primary model

Profile-level 是主要科學分析層，但本文件不在 empirical gates 之前指定 winner。三個候選共用同一 first-stage response、gene-space measure、estimand 與 decision universe；若候選改變 quantity，只能另立 `estimand_id`，不能用表現較佳作為更換 estimand 的理由。

### 6.1 共用 response 與幾何

令 `t`、`h`、`d`、`c`、`r`、`j` 分別表示 target、target 內 guide、donor、condition、run 與 outcome gene。Joint pseudobulk 的 count model在 donor×condition×run block內建立 targeting-minus-matched-NTC effect `δ_hat_thdc`，並輸出 sampling covariance `V_hat_t`。Condition contrast不在單一 block內製造；第一階段先保留 block-specific effects及其 joint covariance，第二階段才用固定 contrast matrix `L` 形成 `E-CS-PROFILE` 與 `E-FD-PROFILE`。

所有候選使用同一個 target-blind `G_profile` 與固定 PSD metric `W`。`W` 只可由 NTC、baseline expression／technical QC 或 target-level cross-fit training folds估計；不得使用 target DE、agreement、ranking或external validation。高維 covariance採 `D + LLᵀ`、block或其他稀疏近似，禁止形成 dense `gene×gene` 或 `target×target` matrix。近似需在 §11 達到 explained trace `≥95%`、relative Frobenius error `≤10%`，且相較可計算的完整 covariance，95% coverage差異不超過1個百分點。

共同 profile outputs 至少包含：`estimand_id`、`method_id`、target／condition support、unconstrained與constrained component estimate、sampling covariance、95% interval、rank interval、effective gene-space rank、gate status與reason codes。CCC與Pearson只作 `by_guide.h5mu`／`by_donors.h5mu` 的 marginal agreement diagnostics，不參與 component估計或method selection。

### 6.2 三個候選 estimator

| Method ID | Operational model | Identifiability／additivity | Gene dependence與sampling uncertainty | Exchangeability／inference | Compute contract | Synthetic failure modes與allowed claim |
|---|---|---|---|---|---|---|
| `M-LIN` precision-weighted multivariate linear decomposition | Reference estimator固定為measurement-error GLS＋trace／MINQUE式quadratic equations：先用`V_hat_t`擬合fixed grand mean，再對預先component bases解unconstrained additive traces；nonnegative constrained fit另行輸出。Gaussian REML只作sensitivity，不與reference混名 | 投影 fixed effects後，component covariance bases、Jacobian／information matrix須逐target full rank；只對線性獨立bases產生additive trace components；condition只能是fixed-domain contrast／dispersion | `W`與low-rank basis target-blind；quadratic-form bias correction明確扣除shared-NTC sampling trace；報有效秩與regularization sensitivity | boundary component以parametric／wild bootstrap；不得把四donors或observed guides當population sample | backed sparse I/O與block sufficient statistics；不得densify | latent-factor genes、shared NTC、heavy tails、sparse pathway、E12-like run alias會暴露失效；通過後可稱Hilbert-space additive profile components |
| `M-KERN` PSD-kernel restricted attribution | Primary kernel候選固定為對 whitened profile的linear PSD kernel；RBF只作非線性sensitivity。以投影後、marginal而非sequential的component subspace attribution與restricted randomisation估計 | 每個Gram matrix最小eigenvalue須不低於total trace的`−1e−8`；位置與dispersion以PERMDISP型diagnostic分開；term order改變不得改變headline quantity。未有formal equivalence時不稱classical variance component | whitening與bandwidth只用training／NTC；shared-NTC covariance進入kernel；報distance concentration與effective rank | 每個null先固定exchange group；不得跨target、run或donor×condition block換標籤；可交換性不成立或解析度不足時改用§9分支 | 只准online／block kernel aggregation，禁止全域`target²` Gram matrix | indefinite distance、equal-centroid/different-dispersion、不平衡缺格與少量permutations會暴露失效；通過後最多稱RKHS／distance attribution |
| `M-FUNC` robust hierarchical functional model | 在target-blind functional／factor basis中聯合建模first-stage covariance、guide-within-target與D4/C3 effects；working residual採Student-t或明訂robust mixture | actual rank gate仍是hard gate，prior不得補出不存在的variation；basis truncation、target-class mixture與linking assumptions須註冊 | joint likelihood傳遞`V_hat_t`；basis、prior與hyperparameters在target／guide cross-fit外估；同報unpooled、shrunken與prior sensitivity | 以simulation-based calibration、posterior predictive checks與held-out guide calibration驗證；不得用external endpoint選prior | chunked sufficient statistics；通過1%／10% benchmark及convergence diagnostics | 2 guides／4 donors prior dominance、多峰target classes、t3 tails與稀疏pathway signal會暴露失效；通過後只能稱model-based functional component |

三個候選都必須映射至同一個 `E-CS-PROFILE`／`E-FD-PROFILE` component或明確標成不同的RKHS sensitivity。若 `M-KERN` 只通過RKHS gate，就不能把其輸出改名為variance share；若 `M-FUNC` 的prior補足rank deficiency，該結果直接失敗而非取得較寬interval。

Candidate freeze另固定：`M-KERN`只有在線性kernel下、投影後component subspaces可形成唯一order-invariant additive partition時才能競逐primary；否則只報各term的marginal RKHS test與overlap，不能硬分shares。RBF bandwidth只由training fold的pairwise-distance分布決定。`M-FUNC`的basis rank由NTC／training-fold reconstruction固定，Student-t degrees-of-freedom與target-class mixture只在inner training folds依predictive criterion估計。所有hyperparameter grids、tie handling與convergence thresholds寫入simulation config hash；未列入grid的模型不得在看真實結果後加入競賽。

### 6.3 預先固定的 selection rule

Selection只使用frozen synthetic scenarios、NTC controls與operability benchmark；真實target effect、K562、T-cell、pathway結果與最終ranking完全不可參與。

1. **Hard-gate screen**：§5 data/rank gates、§9 inference contract、§11 type-I/FDR/coverage/component-recovery及compute gates全部通過。任一P0 gate失敗就移除候選，不以平均分數抵銷。
2. **Estimand fidelity**：候選須估同一object。只產生RKHS attribution或prior-defined functional的候選留作sensitivity，不和Hilbert additive component直接競逐同一名稱。
3. **Worst-case calibrated loss**：對每個候選計算預先註冊的 `L_m=max_s{absolute_bias/0.02, RMSE/0.05, |coverage−0.95|/0.02, max(0,type_I−0.06)/0.01}`；`s`涵蓋§11所有核心與adversarial strata。選擇通過hard gates且`L_m`最小者。
4. **簡約 tie-break**：若兩方法的worst-case loss差異不超過兩倍combined Monte Carlo SE，依可識別component較多、假設較少、compute較低的順序決定；三者同量時選`M-LIN`。這不是事後偏好，而是預先固定的tie rule。
5. **No-winner branch**：沒有候選通過時，profile primary status=`blocked`、estimate=`null`、reason code至少包含失敗gate；只輸出已通過的marginal diagnostics，不可挑「相對最好」者。

任兩個保留候選的central share差異`>0.05`或超過兩倍combined Monte Carlo SE時，即使winner已選，也必須輸出`METHOD_DISAGREEMENT` diagnosis、逐scenario差異與claim降級；不得隱藏discordant sensitivity。

### 6.4 Primary interpretation boundary

Profile headline回答的是共同measurement design內的整體效果與穩定性：`E-CS-PROFILE`、`E-FD-PROFILE`、`E-RANK-REL`及`E-HIT-ABS`。Observed-guide與D4 donor-panel只能描述已觀測facets；future-guide、human population與independent replication仍受§5 gate限制。Gene-wise與pathway outputs用於找出驅動profile結果的genes／processes與檢查結論是否依賴aggregation，不會被稱為獨立replication。

## 7. Gene-wise sensitivity model

Gene-wise 是`E-GENE-CS`的敏感度與機制定位層，不構成與profile primary獨立的replication。它必須和profile層共用target eligibility、D4／C3定義、matched-NTC方向與target-blind universe policy；如因gene-level QC改用不同`G_gene`，輸出須使用新的estimand ID並揭露與`G_profile`的交集。

### 7.1 第一階段：count-to-effect與covariance

分析單位是joint pseudobulk，cell只貢獻counts，不是獨立replicate。Primary first-stage為robust NB quasi-likelihood count model；voom/limma是預先指定的sensitivity／fallback。兩者只依§11的null calibration、coverage與§11 compute gate比較：NB通過即維持primary；NB失敗而voom通過才切換並記錄`FIRST_STAGE_METHOD_FALLBACK`；兩者都失敗則gene-wise status=`blocked`。

對每個block `b=(d,c,r)`，以相同QC、normalization與library-size offset的互斥targeting和matched NTC pseudobulks估計guide-specific effect：

`δ_hat_thbcj = μ_hat_thbcj − μ_hat_NTC,bcj`。

`n_cells`預設只進precision／quality weight；只有target-blind NTC diagnostics顯示它在offset後仍與mean／variance系統性相關，才依預先凍結函數加入mean model。第一階段不得在單一condition block內製造跨condition contrast，而是輸出所有guide×donor×condition effects及joint sampling covariance。每列另保存dispersion、offset、normalization、NTC pool identity、block support與gate結果。

Covariance分兩層保存：

- 對每個outcome gene，保存target／guide／donor／condition contrasts間的covariance及可加總的shared-NTC low-rank term；同一NTC reference造成的誤差不得被當成獨立。
- 對profile／pathway aggregation，保存target-blind regularized cross-gene covariance operator。禁止建立不可行的dense `target×gene×target×gene` matrix。
- 若採`V=D+LLᵀ`或block approximation，需通過§11的trace、Frobenius error與coverage差異門檻；否則輸出`FIRST_STAGE_COVARIANCE_UNAVAILABLE`並停止第二階段。

### 7.2 第二階段：measurement-error model

對每個target×outcome-gene，以第一階段effect作帶已知估計誤差的response，而非當成真值：

`δ_hat_tj | δ_tj ~ N(δ_tj, V_hat_tj^(1))`,

`δ_thdcj = β_tjc + a_thcj + b_tdcj + h_thdcj`。

`β_tjc`是D4 observed-panel、condition `c`下的target effect；`a_thcj`是guide-within-target deviation；`b_tdcj`是D4 donor-panel deviation；在沒有identical-spec replicate時，`h_thdcj`保留為不可再拆的最高階heterogeneity加sampling residual。Guide沒有跨targets的global main effect，donor也不是human-population random sample。

兩guides／四donors不足以逐target×gene無池化估計所有分量；允許的pooling只可跨target×outcome-gene，使用預先註冊的robust／heavy-tailed mixture與target classes。Hyperparameters必須在held-out target／guide fold外估計；每列同時輸出unpooled direct estimate、shrunken estimate與prior sensitivity。Single-guide row保留，但guide component=`not-identifiable`，不得以donor consistency補替。

Condition quantities一律在第二階段由contrast matrix直接估計：三個condition-specific effects、`H0: β_Rest=β_Stim8=β_Stim48=0` any-condition omnibus、`H0: β_Rest=β_Stim8=β_Stim48` condition-heterogeneity omnibus，以及`Stim8−Rest`、`Stim48−Rest`、`Stim48−Stim8`三個pairwise contrasts。「一個condition顯著、另一個不顯著」不是difference evidence。

跨基因summary使用與profile相容的固定PSD metric `W`：`S_tc=β_tcᵀWβ_tc`、`E_tc^(k)=tr(WΣ_tc^(k))`，若報gene-aggregated dependability，定義為`S_tc/(S_tc+Σ_k E_tc^(k))`。這是summed signal除以summed signal+error；禁止平均逐gene ratios，也禁止依DE p-value設定`W`。

### 7.3 Confirmatory testing tree與輸出

在看target結果前把confirmatory error budget固定為兩棵互不混稱的tree，各自`q=0.025`，合計名目budget `0.05`：

1. **Effect／condition tree**：screening family是全部eligible `U_full×G_gene`，screen null為三個condition effects皆零。通過screen後，以固定版本並鎖入environment manifest的stage-wise OFDR procedure確認三個condition effects、condition-heterogeneity omnibus與三個direct contrasts；保存screen與confirmation adjusted p-values。
2. **Facet-heterogeneity tree**：在全部eligible `U_full×G_gene`另檢定無guide／D4-donor heterogeneity的omnibus，通過後才確認guide與donor來源。不得只對已顯著DE pairs檢定後聲稱atlas-wide error control。

Stage-wise程序必須在shared-NTC dependence的simulation通過§11 FDR gate；若其依賴假設失敗，預先降級至BY或resampling-calibrated branch，並使用不同`method_id`。Per-target BH只可標`within-target exploratory FDR`，不得升格為atlas-wide confirmatory result。方向性claim需同時通過相應adjusted p-value與`local false sign rate≤0.05`。

每個target×gene×contrast row至少輸出effect、SE、95% interval、`P(effect>0)`、local false sign rate、raw／adjusted p-value、guide／donor heterogeneity、support、`estimand_id`、`method_id`、status與reason codes。Atlas規模的BH／OFDR須用deterministic blockwise或external-sort實作，排序tie、NA與floating-point policy固定並測試。

## 8. Pathway-level interpretation model

Pathway-level 是`E-PATH-COMP`與`E-PATH-SELF`的生物學解釋層；同一CD4資料的結果不得標為independent validation。Pathway membership、mapping、universe、contrast與method都在讀取target結果前凍結。

### 8.1 Pinned release、mapping與families

本版本固定Human [MSigDB `v2026.1.Hs`](https://www.gsea-msigdb.org/gsea/msigdb)：Hallmark H collection是confirmatory primary；同版本C2:CP:REACTOME以及C5的GO BP／CC／MF各自是secondary libraries。執行前的provenance gate必須保存原始GMT檔名、collection identifier、release、source URL、下載日期、license、bytes與SHA-256；任何release或byte變更都建立新的analysis version，不能沿用adjusted p-values。

Outcome genes以joint object的Ensembl ID作canonical key，保存Ensembl version stripping規則與Ensembl→HGNC／Entrez mapping table及SHA-256。固定處理順序為：移除無法一對一映射者；一對多對應不複製test statistic；多個Ensembl IDs映射同一symbol時，以target-blind的最高baseline expression保留一個，tie依lexicographic Ensembl ID；舊alias只依凍結mapping table處理。每個set與`G_gene`交集後需有15–500 genes；Hallmark mapping coverage低於80%即不估並輸出`PATHWAY_MAPPING_INSUFFICIENT`。

Pathway overlap只影響展示：以凍結membership的Jaccard `≥0.5`建立cluster，保留所有原始hypotheses與adjusted p-values，不以overlap或結果刪除sets。每個method×library各自形成FDR family；Hallmark與Reactome／GO不共享confirmatory措辭。

### 8.2 Competitive CAMERA contract

CAMERA的competitive null是：對target `t`、pathway `p`與direct contrast `l`，`p`內genes的差異訊號distribution不比固定背景`G_gene\p`更強。Inter-gene correlation是必須校正的nuisance structure，不是null本身。

輸入為`G_gene`每一gene的signed moderated statistic；禁止DE-hit list、p-value threshold或pathway-specific re-filtering。Sample-level CAMERA使用與§7相同的design、quality weights與direct contrast估計residual inter-gene correlation。即使gene-wise primary選到NB QL，pathway branch仍須另跑並校準同estimand的voom/limma fit；若voom/limma未通過pathway-specific type-I／coverage gate，`E-PATH-COMP`即blocked。若只有pre-ranked NB statistics可用，只能用不同`method_id`標為`cameraPR` sensitivity，不能取代sample-level CAMERA或與其混稱。輸出set size、mapping coverage、effect direction、correlation adjustment、raw p-value與library-specific adjusted p-value。

### 8.3 Self-contained ROAST／FRY contract

ROAST／FRY的self-contained null是pathway內所有gene effects均為零。FRY作全atlas的scalable self-contained test；ROAST／mROAST只在預先固定、target-independent shard上驗證FRY近似。兩者共用上段已通過gate的voom/limma residual space；該branch失敗時self-contained layer也blocked，不由NB gene-wise顯著性補替。Rotation保留donor×condition×run block、quality weight與gene correlation；不是旋轉genes，也不跨不具交換性的blocks。

Directional輸出分為`up`、`down`與`mixed`；相反方向不得平均抵銷。CAMERA與ROAST／FRY使用不同FDR families，p-values不合併、不投票，也不稱彼此replication。Dense transcriptome-wide同幅shift應容許self-contained顯著但competitive維持null；pathway-specific shift才期待兩者同時有power，兩情境都列入§11。

### 8.4 Pathway multiplicity與allowed interpretation

對每個method×library，screening unit是全部eligible `U_full×pathway`的any-condition omnibus；只有screen通過者才以與§7相同且經simulation校準的stage-wise程序確認三condition、condition-heterogeneity與三direct contrasts。CAMERA family、FRY family與ROAST shard-validation各自保存family ID、screen denominator與adjustment lineage。

Pathway結果只可解釋profile/gene結果可能涉及的process。若profile顯著而gene/pathway不穩定，標為`aggregation-sensitive`；若pathway顯著但profile null，先檢查稀疏訊號被profile metric稀釋，不能自動推翻profile primary。任何跨層一致或分歧都需用§11預先模擬的pattern解釋，不能把同一CD4資料稱為外部佐證。

## 9. Uncertainty, permutation, bootstrap and shrinkage

推論從count-level measurement error開始，不能以within-target disagreement或permutation null冒充target-specific sampling variance。每個interval／p-value／posterior欄位都必須連到一個`uncertainty_method_id`、resampling unit、seed、replicate數、admissible exchange count與gate結果。

### 9.1 Covariance propagation

第一階段以count likelihood／quasi-likelihood的contrast covariance為起點，另保存shared-NTC low-rank covariance與normalization-induced covariance。Analytic covariance需和保留同一NTC sharing structure的parametric count bootstrap比較；對角`lfcSE²`、different-guide dispersion或different-target permutation distribution都不是替代品。

Profile component、norm、dependability與condition contrast透過joint delta method、influence function或parametric bootstrap傳遞`V_hat`；所選方法必須在§11通過overall及support／guide-count／effect-size strata coverage。Rank uncertainty使用target-level cross-fit estimates的joint bootstrap，輸出pairwise exceedance、top-k inclusion與rank interval；同一bootstrap replicate內必須共同重估normalization、basis、first-stage effects、component model與shrinkage。

### 9.2 Null與exchange-group registry

| Inference target | Null | Exchange／resampling unit | Forbidden move | Fail-closed branch |
|---|---|---|---|---|
| NTC-vs-NTC pipeline control | 互斥pseudo-target與reference NTC沒有targeting effect | NTC guide identity為整體單位；在所有donor／condition rows維持同一側，並於每個donor×condition×run block匹配cell count、library size與QC | 同一NTC observation出現在兩側；跨block任意換標籤 | block支援不足即`INSUFFICIENT_NTC_SUPPORT`，不產null p-value |
| Observed-guide prediction | held-out guide effect可由另一guide／training folds預測 | 完整guide identity，所有D4×C3 rows一起切fold | 把rows隨機分散到train/test；跨target交換guides | single-guide=`SINGLE_GUIDE_FACET_UNIDENTIFIABLE`；兩guide只有cross-fit，不宣稱permutation精確檢定 |
| Fixed condition contrast | 預先contrast為零 | model-based contrast；必要時以保持block的residual／wild bootstrap | 交換Rest／Stim8／Stim48 labels，或跨R1/R2 | E12-like alias時同報D4 observed-run與D2_R2；無共同支援即`RUN_DONOR_CONDITION_ALIASED` |
| D4 donor-panel sensitivity | 某位observed donor不驅動結果 | 四次leave-one-donor-out完整refit；可另作明訂multiway wild-bootstrap sensitivity | 將四donors當human-population random permutation sample | 只報finite-panel shift與predictive check，不給population p-value |
| `M-KERN` component test | reduced model下指定RKHS location term為零 | 只有在reduced-model residual於target內、預先strata中可交換時採Freedman–Lane；exchange blocks與whole-vector move明列 | 跨target、run、donor×condition block或逐gene permutation | exchangeability simulation失敗即改用校準的parametric／cluster-wild branch；仍失敗則`PERMUTATION_GROUP_INVALID` |
| Boundary variance／dependability | component=0或位於0／1 boundary | 從fitted count＋component model做parametric bootstrap，保留missingness與shared NTC | 以普通Wald常態近似或事後截零 | calibration失敗即`BOUNDARY_COMPONENT_UNRESOLVED` |

所有permutation採`p=(1+#更極端)/(1+B)`；完整列舉時使用exact randomisation p-value。先輸出admissible permutation數與minimum attainable p；若解析度不足以檢定預設`α`，設定`PERMUTATION_RESOLUTION_INSUFFICIENT`，p-value只作descriptive，不以增加重複抽樣次數假裝增加獨立排列。Freedman–Lane只有在reduced-model residual exchangeability經E12-like null simulation通過時可用；否則採已校準bootstrap。

### 9.3 Bootstrap與small-facet policy

Primary parametric bootstrap以fitted pseudobulk count model產生counts，保留library offsets、guide nesting、D4×C3×run layout、shared NTC、missing cells與gene factor structure。Nonparametric sensitivity只可重抽真正獨立單位：whole guide identity、whole donor或identical-spec lane；不得逐cell重抽後把同一pseudobulk中的cells當獨立實驗。

四donor cluster bootstrap與兩guide bootstrap本身太稀疏，不能單獨支撐nominal 95% claim；因此LODO是deterministic influence sensitivity，guide A/B cross-fit是predictive sensitivity，正式coverage由parametric／wild procedure在相同small-facet design的simulation驗證。Atlas aggregation與cross-target linking sensitivity可重抽完整target identity（其所有guides、donors、conditions一起進出），但這只表示`U_full`內algorithm stability，不外推到未觀測targets；per-target rank uncertainty則用所有targets共同的parametric draws，不以刪除target的cluster bootstrap計算。Outcome genes不被naïve獨立重抽；cross-gene dependence由frozen factor／block generator或residual operator保留。

### 9.4 Target-level shrinkage與boundary policy

Shrinkage輸入必須是同一estimand下的direct estimate `R_tilde_t`及其sampling covariance；facet disagreement不得被當sampling variance。Primary bounded model在預先固定link上建模`R_t∈[0,1]`，linking distribution使用robust heavy-tailed／target-class mixture；covariates只能是analysis前凍結的guide-design與technical features。Hyperparameters以target-level folds估計，所有同target rows保持同fold，external outcomes完全不可參與。

每個target同時輸出：unconstrained component estimates、明訂constrained likelihood estimate、direct `R_tilde_t`、shrunken `R_hat_t`、sampling variance、shrinkage weight、95% interval、prior-class probability與prior sensitivity。Unconstrained negative components是diagnostic，不得截為零後重新正規化；constrained estimate由完整nonnegative likelihood／estimating equation產生，boundary interval以§9.2 bootstrap或test inversion計算。

只有在direct sampling covariance、link adequacy、zero／near-zero／heavy-tail／mixture coverage及「sampling variance越高，shrinkage不減少」gate都通過時，才可使用Fay–Herriot或model-based dependability措辭。Single-guide target的guide facet保持`null`；shrinkage不能創造觀測設計沒有的guide variation。

D-study只對可識別、非負且有明確sampling population的facets輸出。C3是fixed domain，不作增加condition數的曲線；目前future-guide與human-donor population都未識別，故相關projection=`null`。若日後新增獨立guide／donor sampling frame或identical-spec lanes，需建立新estimand與manifest，並驗證point curve隨真正replicate數增加不下降且projection coverage達§11門檻。

## 10. Missingness, QC and degradation rules

### 10.1 Identical-spec replicate定義

`E-REPL-FLOOR`只接受在同一scope下，除replicate identity外分析規格完全相同的獨立measurement units。共通specification key至少包含`target_id, guide_id, donor_id, condition, biological_sample, perturbation_assignment, matched_NTC_definition, assay_protocol, preprocessing_spec, G_profile_version`；run／lane／library欄位依floor scope拆解如下：

| `floor_scope` | 必須相同 | 唯一允許改變的replicate identity | 可支持的措辭 |
|---|---|---|---|
| `technical_lane` | 同一biological sample、cell pool、library prep、run preparation與完整分析規格 | 真正獨立的sequencing lane／read acquisition | 同一library的technical-lane repeatability floor |
| `library` | 同一biological sample、cell pool與perturbation／assay規格 | 獨立library preparation ID | library-preparation repeatability floor |
| `biological_experiment` | 同一donor、condition、target、guide與protocol specification | 預先定義的獨立biological-repeat ID | 同一donor／condition設計下的biological-repeat floor |

三個scope各自使用不同`estimand_id`，不能合併成單一「irreducible floor」。同一aggregate的複製列、同一reads檔重匯入、重複barcode pool或只改檔名都不是replicate。Guide pairs改變guide；donor split-halves改變donor support；不同NTC pools只形成negative control；三者均不符合identical-spec replicate，也不可當floor下界。

### 10.2 Lane／replicate artifact unavailable branch（目前狀態）

E11／E12的merged joint pseudobulk與sample metadata沒有identical-spec replicate dimension；因此目前強制輸出：

```json
{
  "estimand_id": "E-REPL-FLOOR",
  "floor_status": "not-identifiable",
  "floor_estimate": null,
  "floor_scope": null,
  "component_id": "highest_order_plus_sampling_residual",
  "reason_codes": [
    "NO_IDENTICAL_SPEC_REPLICATE",
    "HIGHEST_ORDER_RESIDUAL_ALIASED"
  ]
}
```

`null`代表不可識別，不是0。若actual joint pseudobulk通過其他gate，可估可識別的guide／D4／C3 quantities，但最高階interaction與sampling residual保持合併；不得由`10xrun_id`虛構replicate，因E12每個donor×condition只有一個sample。若連joint pseudobulk都沒有，整體只保留h5ad／h5mu的`marginal-only` diagnostics。Single-guide target保留row但`guide_status=not-identifiable`，不進`U_full`共同ranking。

### 10.3 Lane／replicate artifact available branch

作者提供的lane-level pseudobulk是首選；約1.6 TB cell-level rebuild只是條件式fallback。取得artifact後依序通過下列gate，任一步失敗即回到§10.2，且不可把「已取得檔案」寫成「floor已識別」：

1. **Provenance**：固定source、產生流程、bytes、SHA-256、shape、sparse encoding、lane／library／biological-repeat定義及replicate-generation code。
2. **Scope-key equality**：逐replicate set證明§10.1對應的specification fields完全相同，只有該scope允許的replicate identity不同；輸出field-by-field diff。
3. **Multiplicity**：每個可用spec至少兩個獨立units；target-specific floor若支援不足只能估design-level pooled floor並標明pooling population。
4. **No duplicate aggregate**：驗證source read／cell/barcode lineage；technical lane可共享cell pool但不得共享同一read observation，library／biological scope須符合更高獨立性。
5. **Matched control**：每個replicate unit都需有同scope、同donor×condition×run／lane可追溯的matched NTC；共用control covariance明列。
6. **Rank／confounding**：重做fixed-effect及component-basis rank；replicate identity不得與batch、library chemistry或condition完全alias。
7. **Calibration**：NTC null、known-floor simulation、boundary interval與scope-specific coverage通過§11；技術lane不得被寫成完整實驗replication。
8. **Promotion rule**：artifact與上述gate outputs皆有checksum後，`design-specified`才升為`empirically-passed`；每個estimate保留scope、n_replicate_sets、support distribution與CI。

### 10.4 General missingness與QC policy

QC rules只使用provenance、count depth、cell count、baseline expression、mapping與target-blind technical diagnostics；不得依target effect、agreement、rank、pathway或external outcome改門檻。每次run輸出原始與通過後的target×guide×donor×condition×run grid、matched-NTC counts、gene universe、排除原因及checksum。

Missing cell不可補零或以h5mu marginal summary填回。每個缺格先分類為structural、QC-driven、MCAR-plausible、MAR-plausible或MNAR-plausible；分類依可觀測metadata與機制，不依結果好壞。Primary complete-design `U_full`採預先規則；inverse-probability weighting／multiple imputation只有在overlap、missingness model、weight truncation與MNAR stress test通過時，才用新的estimand ID作sensitivity，不取代primary。

固定降級矩陣如下：

| Available evidence | Allowed output | Prohibited output | Required status／reason |
|---|---|---|---|
| joint pseudobulk通過schema/rank，無replicate | 可識別profile／gene／pathway與合併最高階residual | replication floor scalar | `floor=not-identifiable`; `NO_IDENTICAL_SPEC_REPLICATE` |
| joint pseudobulk但target缺必要cells／NTC／rank | 保留target row與partial support diagnostics | 對該estimand給數值或混入common ranking | `TARGET_GRID_INCOMPLETE`／`MATCHED_NTC_MISSING`／`DESIGN_MATRIX_RANK_DEFICIENT` |
| 只有`by_guide.h5mu`／`by_donors.h5mu` | CCC／Pearson、marginal agreement與schema cross-check | joint interactions、variance shares、joint ranking、floor | `marginal-only`; `MARGINAL_INPUT_ONLY` |
| single-guide target | condition／donor partial evidence（若各自通過） | guide reliability、future-guide projection、common-design ranking | `SINGLE_GUIDE_FACET_UNIDENTIFIABLE` |
| external table缺失／受tuning污染 | internal results與missing-evidence record | replication／transportability claim | `VALIDATION_INPUT_MISSING`／`VALIDATION_LEAKAGE` |
| compute gate失敗 | 已完成audit artifacts與可重跑checkpoint | 以densification或未驗證shortcut取得headline | `COMPUTE_BUDGET_EXCEEDED` |

任何非`empirically-passed`輸出至少一個machine-readable reason code；`not-identifiable` quantity的estimate必須是`null`，不能以0、NA未註解或shrunken prediction掩蓋。

## 11. Simulation recovery and falsification plan

Simulation不是展示性附錄，而是method selection、claim wording與release的hard gate。所有scenario YAML、generator code、seed registry、truth table、software lock與expected output schema在讀取真實target results前凍結；從actual資料估nuisance parameters時只能使用NTC或training folds，並在manifest記錄來源。

### 11.1 Generator與scenario matrix

Count-level generator重現joint pseudobulk的NB mean–variance、library offset、n_cells、shared matched NTC、guide nested within target、D4×C3×run layout、target-blindcross-gene factor／block correlation與缺格。每個scenario同時保存truth在count、effect、profile component、gene contrast、pathway與decision layers的映射；若truth無法映射同一estimand，該simulation不可用於候選比較。

最低scenario set如下，每個主軸另含零／近零／中度／強effect strata：

1. global null＋shared matched NTC；
2. 已知additive Hilbert components與zero／boundary components；
3. 三condition同效應、單一condition效應及三個direct contrasts；
4. 兩guides同向但scale不同、反向、off-target outlier與1／2／3／4-guide support；
5. 單一donor驅動、均勻D4 effect與leave-one-donor influence；
6. centroid相同但guide／donor dispersion不同，用於拆解location與dispersion；
7. E12-like run layout，分別注入0與非0 target×run effect；
8. independent、block-correlated、latent-factor outcome genes與distance concentration；
9. dense transcriptome-wide shift、sparse pathway-only shift及pathway內up/down各半；
10. low counts、zero inflation、弱／近零KD、異變異、outliers與Student-t3 tails；
11. MCAR、metadata-driven MAR與viability-driven MNAR缺格；
12. target-blind feature universe對照significance-selected／target-specific universe；
13. unimodal、multimodal與heavy-tailedtarget classes，含single-guide shrinkage trap；
14. overlapping pathways、duplicate／one-to-many ID mapping及mapping coverage failure；
15. identical-spec replicate存在、只存在duplicate aggregate、以及replicate完全缺席；
16. external target split正確、target-row leakage與validation-assisted method selection；
17. 1%／10% shard、interrupted-resume與forbidden densification。

每個global-null scenario至少5,000 Monte Carlo replicates；每個non-null／adversarial scenario至少2,000。可使用保留相同facet geometry的target／gene shards，但每個方法另需至少200次atlas-like end-to-end shard runs；若為節省計算改在effect／sufficient-statistic layer模擬，需以至少1,000次count-level bridge runs證明關鍵error rates與coverage差異不超過1個百分點。

### 11.2 Quantitative gates

以下門檻在真實target結果前固定；任何變更都建立新protocol version並重跑全部候選，不可只重跑有利方法。

| Gate | Release threshold |
|---|---|
| Type-I validity | `α=0.05`時one-sided 95% Monte Carlo upper bound `≤0.06`；若宣稱nominally calibrated，point estimate須在`0.04–0.06`且two-sided 95% MC interval包含`0.05` |
| FDR／OFDR／false-sign | target `q=0.05`時point `≤0.06`且95% MC upper bound `≤0.07`；§7每棵`q=0.025` tree另要求point `≤0.035`、upper bound `≤0.045` |
| 95% interval／predictive coverage | overall及預先support、guide-count、effect-size、missingness strata均在`0.93–0.97` |
| Interval efficiency | mean width不超過相同estimand oracle的`1.25×`；避免以無限寬interval通過coverage |
| Effect recovery | standardized absolute bias `≤0.10`，RMSE不超過oracle的`1.10×` |
| Component recovery | true share `≥0.05`時absolute bias `≤0.02`、RMSE `≤0.05`；true zero component的median constrained estimate `≤0.01`且type-I通過 |
| Moderate-signal power | 預先固定`0.5` residual-SD effect中power `≥0.80`且不比oracle低超過10個百分點；避免「永不拒絕」方法通過error gate |
| Winner's curse／ranking | untouched held-out top-decile effect calibration slope`0.90–1.10`；top-decile不得用training effect重定義；rank interval coverage通過上述coverage gate |
| Covariance approximation | explained trace `≥95%`、relative Frobenius error `≤10%`、相較full covariance的coverage差`≤1`百分點 |
| Pathway global shift | self-contained FRY power `≥0.80`，CAMERA維持type-I gate |
| Pathway-specific shift | CAMERA與FRY power各`≥0.80`；mixed-direction test power`≥0.80`且directional false-sign通過 |
| Shrinkage | higher sampling variance不得降低shrinkage；zero／near-zero／mixture strata coverage通過；direct與shrunken均保存 |
| D-study | 每條允許輸出的point curve隨真正replicate數增加不得下降，projection coverage`0.93–0.97` |
| Candidate disagreement | 任兩候選central share差`>0.05`或`>2×`combined MC SE，強制`METHOD_DISAGREEMENT` diagnosis，不得以平均或挑較漂亮結果消除 |
| Compute／resume | 固定hardware上peak RSS `<70%` available RAM、scratch `<2×`input、1%→10% scaling exponent `≤1.2`；resume與clean run checksum一致；任何dense full `gene²`／`target²` object直接失敗 |

### 11.3 Claim-to-falsification map

| Core claim | Minimum falsification test | Failure consequence |
|---|---|---|
| matched-NTC effect與first-stage covariance | global-null＋shared-NTC count simulation；analytic對parametric-bootstrap covariance | `FIRST_STAGE_COVARIANCE_UNAVAILABLE`; profile／gene／pathway停止 |
| Hilbert additive profile components | known components、boundary、latent-factor genes、incomplete grid | `COVARIANCE_BASIS_RANK_DEFICIENT`或component claim blocked |
| RKHS／distance attribution | indefinite-kernel、equal-centroid/different-dispersion、term-order與restricted-null scenarios | `KERNEL_NOT_PSD`／`DISPERSION_LOCATION_CONFOUNDED`；只留diagnostic |
| Robust functional component | multimodal targets、basis-truncated sparse pathway、t3 tails、prior-dominant two-guide case | `SHRINKAGE_CALIBRATION_FAILED`; 不得用posterior補rank |
| D4 condition／donor wording | E12 run layout＋target×run injection；single-donor driver；R2 common support | `RUN_DONOR_CONDITION_ALIASED`或`run/support-sensitive` |
| observed-guide consistency／single-guide | guide scale／sign／outlier與1–4 guides；whole-guide cross-fit | single guide=`not-identifiable`; predictive coverage失敗即guide claim blocked |
| relative rank／absolute hit | sparse alternative、top-k selection、threshold boundary與held-out calibration | rank／hit outputs不release；不得改threshold |
| gene-wise discoveries | global null、sparse effects、shared-NTC dependence、MNAR與target-specific selection | effect tree或facet tree blocked；per-target exploratory另列 |
| CAMERA／ROAST-FRY | global transcriptome shift、pathway-specific shift、mixed direction、overlap與mapping failure | method-specific pathway family blocked；兩種null不互換 |
| replication floor | true identical-spec repeats、duplicate aggregate與no-replicate scenarios | 缺replicate時estimate=`null`; scope誤判即blocked |
| external replication／transport | target-level split、leakage sentinel、tuning-assisted selection與endpoint mismatch | `VALIDATION_LEAKAGE`／`VALIDATION_ENDPOINT_OUT_OF_SCOPE` |
| operability | 1%／10% shard、resume、checksum與memory sentinel | `COMPUTE_BUDGET_EXCEEDED`; 不准未驗證shortcut |

### 11.4 Gate adjudication

Hard gate逐claim判定，不以跨scenario平均或secondary method成功抵銷primary failure。每次simulation輸出config hash、truth hash、method version、replicate count、Monte Carlo SE／interval、observed threshold、pass/fail及failure code。只有三個profile candidates在同一frozen suite跑完後才執行§6.3 selection；gene/pathway、shrinkage與validation各自也必須通過對應列。Failing method可保留研究用artifact，但不得進headline、ranking或demo export。

## 12. Internal and external validation

Internal controls用來嘗試推翻pipeline；external evidence用來評估預先凍結的transport／replication estimand。兩者都不能因結果「看起來合理」而補過schema、rank、coverage或no-leakage gate。

### 12.1 NTC-vs-NTC negative control

在每個donor×condition×run block，以完整NTC guide identity建立互斥pseudo-target／reference pools；同一NTC guide的所有D4×C3 rows固定在同一側，避免identity leakage。Pools匹配`n_cells`、library size與target-blind QC，至少執行500個預先seeded splits，並走完整normalization、feature/basis learning、first-stage、profile、gene、pathway、shrinkage與ranking pipeline。

要求對應null rejection／FDR通過§11，Wald-statistic inflation factor介於`0.90–1.10`，且pseudo-target ranking無系統性block／library-size梯度。任一失敗會阻擋受影響claim；不得只移除不好看的NTC split。NTC-vs-NTC是internal falsification，不是targeting-profile replicate或replication floor。

### 12.2 Whole-guide cross-fit

兩-guide targets執行A-train／B-test後交換；3–4-guide targets用預先固定folds。Fold unit是完整guide identity，其所有donor／condition／run rows同進同出。Feature universe、basis、metric、weights、prior、hyperparameters、threshold與winner selection都不得讀取held-out guide。輸出held-out profile prediction、95% predictive coverage、calibration slope、rank shift與sign concordance；coverage需`0.93–0.97`。Single-guide targets不算cross-fit成功證據，也不取得guide reliability。

### 12.3 Leave-one-donor-out與R2 common support

LODO執行四次完整refit，每次移除一位donor的所有targeting與NTC rows，並在剩餘三位重新估normalization、basis、component model、shrinkage hyperparameters與threshold；held-out donor只用自己的matched NTC建立test effect。報component shift、rank Spearman、top-decile Jaccard、top-k inclusion、hit-call flips與predictive coverage。

任一central share shift`>0.05`或`>2×`combined SE、rank Spearman`<0.80`、top-decile Jaccard`<0.60`、或predictive coverage不在`0.93–0.97`，結果標`donor-sensitive`並列出targets；這是D4 finite-panel sensitivity，不得外推成人口generalizability。

R2 common-support固定為`D2_R2={CE0008678, CE0006864}`的C3六個cells，使用和D4 primary相同的gene universe與target eligibility交集，但estimand固定為`E-FD-PROFILE-R2`。若central share差`>0.05`或`>2×`combined SE、rank Spearman`<0.80`或top-decile Jaccard`<0.60`，標`run/support-sensitive`。D2_R2不能取代D4 observed-run primary，也不能解除target×run alias。

### 12.4 Marginal-product cross-check

由通過gate的joint effects依release定義重新聚合，對hash-fixed h5ad、`by_guide.h5mu`與`by_donors.h5mu`比較key coverage、effect direction、CCC／Pearson與difference distribution。差異超過NTC凍結容許帶就輸出`MARGINAL_RECONCILIATION_FAILED`並追查aggregation；一致只能證明reconstruction可重做，不能把marginal products升格為joint evidence。

### 12.5 External evidence taxonomy

| Evidence class | Minimum observation design | Allowed wording | Current bundle status |
|---|---|---|---|
| `same-cell-type replication`／`E-TCELL-REP` | 獨立T-cell Perturb-seq，獨立donors／batch／targets或預先shared targets，相容endpoint且完全untouched | same-cell-type T-cell replication | actual table不在E01–E21；`not-identifiable` |
| `assay translation` | T-cell arrayed bulk、flow或其他預先endpoint，study與assay獨立 | assay translation for the named endpoint | actual table未封存；`not-identifiable` |
| `cross-cell-type transportability`／`E-XCELL-TRANSPORT` | untouched K562 target-level effects與CD4 estimate對齊 | CD4→K562 cross-cell-type transportability | E08只有partial描述，actual values不在bundle；`not-identifiable` |
| `biological relevance` | pathway、disease association、mechanistic literature或非對齊endpoint | biological relevance／hypothesis support | 依來源個別評估；永不改稱replication |
| `internal sensitivity/interpretation` | 同一CD4資料的gene-wise／pathway outputs | internal sensitivity或biological interpretation | `design-specified`，不是external validation |

K562不論correlation多高都不稱T-cell replication；相同CD4資料的gene/pathway concordance也不稱independent validation。獨立性按target、study、donor、batch、assay與tuning exposure逐欄記錄，不以資料集名稱判定。

### 12.6 No-leakage protocol

任何external observation只要參與candidate／first-stage method選擇、prior／hyperparameter、gene universe、pathway release、QC／missingness rule、metric／domain weight、threshold、feature selection或stopping decision，就標為`tuning`，不得再稱untouched validation。

Split以完整target identity為group；同target所有conditions、endpoints與rows固定在同一fold。執行前保存source checksum、eligible target list、endpoint、split seed、tuning／test target lists與split SHA-256。若樣本不足以保留untouched test，採target-level nested cross-validation並稱`cross-validated external prediction`，不稱independent validation。Method selection只在inner folds；outer fold只使用一次並完整保存predictions。

External結果至少報shared-target join numerator／denominator、missingness pattern、signed CCC、sign concordance、calibration intercept／slope、pre-specified endpoint effect與target-cluster bootstrap CI；Pearson／CCC不能單獨支撐replication claim。Threshold、direction與success criterion在解封test set前固定。Join coverage不足、endpoint不相容或split污染時estimate=`null`，分別輸出`VALIDATION_INPUT_MISSING`、`VALIDATION_ENDPOINT_OUT_OF_SCOPE`或`VALIDATION_LEAKAGE`。

### 12.7 Cross-layer interpretation matrix

| Profile primary | Gene/pathway secondary | External evidence | Interpretation |
|---|---|---|---|
| passes | concordant | untouched class-specific test passes | 對相應estimand的最強支持；仍不超出D4/C3與external class wording |
| passes | unstable／discordant | any | `aggregation-sensitive`，先查gene metric、sparse signal與FDR；不隱藏secondary discordance |
| null／blocked | pathway-specific signal | any | 可能是稀疏signal被global metric稀釋；維持profile status並另報secondary，不把pathway升為primary |
| passes | concordant | missing／leaked | internal evidence only；external claim=`not-identifiable` |
| passes | concordant | external fails with adequate power | `transport/replication-sensitive`，保留internal estimate但不得宣稱external generalization |

每個cell的解釋須先通過§11對應scenario；沒有falsification map支持的事後故事不進confirmatory conclusion。

## 13. Reproducible pipeline, modules and output schemas

Pipeline是後續#8的實作契約；本#9 change不建立分析程式。所有module以immutable input checksum、config hash與upstream artifact hash作cache key，採backed／chunked sparse I/O，支援中斷續跑；失敗row保留，不靜默刪除。

### 13.1 Module DAG與責任

| Module | Responsibility | Required output |
|---|---|---|
| `provenance_lock` | 固定source URL、size、ETag／checksum、schema、config、seed、Git與Python/R environment | `run_manifest.json` |
| `audit_joint_schema` | H5／AnnData shape、CSR、integer counts、required fields、unique keys、guide→target與targeting／NTC | `input_schema_audit.json` |
| `audit_design_support` | 逐target NTC、grid、missingness、fixed-effect rank、component-basis rank、run alias與common support | `design_support.parquet` |
| `build_matched_ntc_effects` | block內NB QL primary／voom sensitivity、offset、quality weight與targeting-minus-NTC effects | `first_stage_effects.parquet` |
| `estimate_effect_covariance` | contrast covariance、shared NTC、normalization與cross-gene regularized operator | `covariance_manifest.json`＋chunked matrices |
| `simulate_and_falsify` | §11 frozen scenarios、truth、calibration與claim gates | `simulation_summary.parquet`＋scenario artifacts |
| `benchmark_profile_candidates` | 三候選同一1%／10% shards的accuracy、memory、scratch、wall time與resume | `candidate_benchmark.parquet` |
| `select_profile_method` | 只執行§6.3 hard gates／loss／tie rule | `method_selection.json` |
| `fit_profile_primary` | 僅執行已選且通過gate的方法；保留candidate sensitivities | `profile_components.parquet` |
| `fit_gene_sensitivity` | two-stage measurement-error model、contrasts、OFDR與false-sign outputs | `gene_results.parquet` |
| `fit_pathway_interpretation` | pinned mapping、CAMERA與FRY／ROAST分開的families | `pathway_results.parquet` |
| `fit_target_dependability` | direct estimate、bounded shrinkage、boundary-aware interval與rank uncertainty | `target_dependability.parquet`＋`ranking.parquet` |
| `estimate_replication_floor` | §10 scope gates；無replicate時輸出nullable floor | `replication_floor.json` |
| `run_internal_controls` | NTC splits、whole-guide cross-fit、LODO、R2 common-support | `internal_controls.parquet` |
| `run_external_validation` | frozen target split與evidence taxonomy | `validation_results.parquet` |
| `crosscheck_marginals` | joint aggregation對h5ad／h5mu，僅作reconstruction diagnostic | `marginal_crosscheck.parquet` |
| `export_results` | deterministic Parquet＋demo JSON／SVG，只取verified rows | `results/`＋`export_manifest.json` |
| `validate_outputs` | JSON Schema、column／lineage／nullability／ranking invariants與checksums | `verification_summary.json` |

Module不得繞過upstream status：例如`fit_profile_primary`只有在schema、rank、first-stage covariance、simulation、benchmark與selection artifacts全為pass時可執行；`export_results`不會把`design-specified`改寫成numeric success。

### 13.2 Machine-readable status與reason codes

共通`status`只允許`design-specified`、`empirically-passed`、`marginal-only`、`not-identifiable`、`blocked`。Reason-code registry固定如下；新增code需更新schema、negative fixture與文件。

| Category | Allowed reason codes |
|---|---|
| Input／schema | `JOINT_INPUT_NOT_INSPECTED`, `JOINT_INPUT_MISSING`, `MARGINAL_INPUT_ONLY`, `SCHEMA_MISMATCH`, `NONINTEGER_COUNTS`, `DUPLICATE_OBSERVATION_KEY`, `GUIDE_TARGET_MAPPING_CONFLICT` |
| Support／rank | `MATCHED_NTC_MISSING`, `INSUFFICIENT_NTC_SUPPORT`, `TARGET_GRID_INCOMPLETE`, `DESIGN_MATRIX_RANK_DEFICIENT`, `COVARIANCE_BASIS_RANK_DEFICIENT`, `RUN_DONOR_CONDITION_ALIASED`, `NO_COMMON_SUPPORT` |
| Replication／facet | `SINGLE_GUIDE_FACET_UNIDENTIFIABLE`, `NO_IDENTICAL_SPEC_REPLICATE`, `REPLICATE_INDEPENDENCE_UNVERIFIED`, `HIGHEST_ORDER_RESIDUAL_ALIASED` |
| Estimator／inference | `KERNEL_NOT_PSD`, `TERM_ORDER_DEPENDENT`, `DISPERSION_LOCATION_CONFOUNDED`, `PERMUTATION_GROUP_INVALID`, `PERMUTATION_RESOLUTION_INSUFFICIENT`, `FIRST_STAGE_METHOD_FALLBACK`, `METHOD_DISAGREEMENT` |
| Covariance／shrinkage | `FIRST_STAGE_COVARIANCE_UNAVAILABLE`, `SHARED_NTC_COVARIANCE_UNMODELED`, `SHRINKAGE_CALIBRATION_FAILED`, `BOUNDARY_COMPONENT_UNRESOLVED` |
| Selection／multiplicity | `TARGET_BLIND_UNIVERSE_VIOLATION`, `FDR_CALIBRATION_FAILED`, `SIMULATION_GATE_FAILED`, `MNAR_SENSITIVITY_FAILED` |
| Pathway／cross-check | `PATHWAY_MAPPING_INSUFFICIENT`, `MARGINAL_RECONCILIATION_FAILED` |
| Validation | `VALIDATION_INPUT_MISSING`, `VALIDATION_LEAKAGE`, `VALIDATION_ENDPOINT_OUT_OF_SCOPE` |
| Operability／output | `COMPUTE_BUDGET_EXCEEDED`, `OUTPUT_SCHEMA_INVALID` |

Common nullable row example：

```json
{
  "estimand_id": "E-REPL-FLOOR",
  "measurement_design_id": "joint_merged_pseudobulk",
  "status": "not-identifiable",
  "estimate": null,
  "reason_codes": [
    "NO_IDENTICAL_SPEC_REPLICATE",
    "HIGHEST_ORDER_RESIDUAL_ALIASED"
  ],
  "evidence_manifest": "EB-2026-07-10-v1.1",
  "gate_results": [],
  "verified_at": null,
  "verification_command": null
}
```

### 13.3 Output schemas

| Artifact | Minimum fields／structure |
|---|---|
| `run_manifest.json` | Git commit、evidence manifest、input SHA-256／ETag、config hash、seed registry、Python/R lock hashes、hardware、start/end UTC、module versions |
| `input_schema_audit.json` | shape、dtype、sparse format、required columns、count validity、unique-key／mapping results、overall status與reason codes |
| `design_support.parquet` | `estimand_id,target_id,n_guides,n_donors,n_conditions,n_blocks,n_ntc,rank,expected_rank,condition_number,aliased_terms,estimable_components,status,reason_codes` |
| `first_stage_effects.parquet` | target／guide／donor／condition／run／gene key、effect、SE、dispersion、offset、NTC pool、method、support、status |
| `covariance_manifest.json` | block matrix paths／hashes、shared-NTC factors、cross-gene operator、rank、trace/Frobenius validation、lineage |
| `component_estimates.parquet` | `estimand_id,method_id,target_id,component_id,estimate_unconstrained,estimate_constrained,se,ci_low,ci_high,n_support,status,reason_codes` |
| `gene_results.parquet` | target×gene×hypothesis key、effect／SE／CI、sign probability、lfsr、raw／adjusted p、family lineage、heterogeneity、status |
| `pathway_results.parquet` | target×method×library×set×contrast key、release／mapping hash、set size、direction、correlation adjustment、p／FDR、status |
| `target_dependability.parquet` | `estimand_id,measurement_design_id,target_id,guide_status,direct_estimate,sampling_variance,shrunken_estimate,shrinkage_weight,ci,rank_interval,evidence_tier,status` |
| `ranking.parquet` | 同一estimand／measurement design內的rank、rank interval、top-k probability與held-out calibration；跨tier不共排名 |
| `replication_floor.json` | nullable estimate、scope、replicate key、n replicate sets、support distribution、CI、status與reason codes |
| `internal_controls.parquet` | control ID、fold／split、estimand、metric、threshold、observed value、CI、pass／fail與artifact hash |
| `validation_results.parquet` | evidence class、endpoint、split hash、n eligible／joined、tuning exposure、estimate／CI、calibration、status／reasons |
| `candidate_benchmark.parquet` | shard hash、method、accuracy gates、peak RSS、scratch、wall time、scaling exponent、resume checksum、status |
| `verification_summary.json` | 每個gate的owner、command、exit code、input／output hashes、threshold、observed value、status與timestamp |

### 13.4 Schema invariants

1. `status=not-identifiable`時所有該quantity numeric estimates必須為`null`且`reason_codes`非空；0只表示估計為0。
2. `status=empirically-passed`需有non-null input／output checksums、verification command、exit code 0、verified timestamp與全部upstream gates。
3. `status=marginal-only`不得含joint component ID、joint rank、floor或common-design ranking。
4. Ranking rows的`estimand_id`與`measurement_design_id`必須一致；single-guide／R2／marginal tier不可混入`U_full`。
5. Constrained與unconstrained components同時存在；禁止只保留截零後值。所有p-values連回唯一family與adjustment procedure。
6. External row需有evidence class、endpoint與split hash；`tuning_used=true`時不得標untouched／independent。
7. Every export row可由lineage追到source checksum、config、seed、module version與gate result；validator遇孤兒row即`OUTPUT_SCHEMA_INVALID`。

## 14. Staged implementation order and verification commands

本#9 change只交付可稽核方法文件、Sol records與#8 ingest crosswalk；不下載大型資料、不實作分析程式，也不產生ranking。以下階段只有在owner審查本文件並執行`spectra-ingest`更新#8後才開始；未核准時#8 statistical core持續暫停。

### 14.1 Downstream stage gates

| Stage | Work | Exit artifact／gate | Stop condition |
|---|---|---|---|
| 0. Owner ingest | 核准或修訂本文件；把§16逐檔決策ingest回#8 | 更新後#8 proposal/design/spec/tasks與新base hash | 本文件`blocked`或owner未核准 |
| 1. Environment／provenance | 建立Python/R locks、seed registry、hardware budget；修復E14 KD取得流程 | `run_manifest.json`；clean-room KD checksum一致 | 來源、license、checksum或environment不可重建 |
| 2. Acquire／audit data | 下載約44.6 GB joint pseudobulk；lane artifact另行查詢，不預設存在 | `input_schema_audit.json`＋hash-fixed grid report | schema/count/key／matched-NTC gate失敗 |
| 3. Design support | 逐target fixed rank、component-basis rank、run alias、U_full與D2_R2 support | `design_support.parquet` | 受影響component不可識別；只降級對應row，不改假設硬算 |
| 4. Freeze simulation | 實作§11 generator／fixtures，凍結scenario config與truth | simulation fixture checksums與CI tests | truth不對應estimand或coverage／error gates失敗 |
| 5. First-stage effects | NB QL primary、voom sensitivity與shared-NTC covariance | effects＋covariance manifest | covariance、NTC null或compute失敗 |
| 6. Candidate benchmark／selection | 三profile methods同跑1%／10% shards與完整synthetic suite | benchmark＋`method_selection.json` | 無候選通過hard gates則primary=`blocked` |
| 7. Analysis layers | 依序fit profile primary、gene-wise、pathway；方法／library不得看結果後更換 | component／gene／pathway artifacts | 任一layer只阻擋自身claim，不互相冒充替代 |
| 8. Dependability／controls | boundary shrinkage、ranking uncertainty、NTC、guide cross-fit、LODO、R2、marginal cross-check | dependability／ranking／control artifacts | coverage、disagreement或common-support gate失敗 |
| 9. Replication／external | floor依lane availability；external依frozen target split與taxonomy | floor＋validation artifacts | 缺資料即nullable／not-identifiable，不製造criterion |
| 10. Validate／export | schema invariants、lineage、demo-safe static outputs與full rerun／resume check | `verification_summary.json`與export manifest | Critical invariant、checksum drift或unresolvedP0/P1 |

### 14.2 Proposed downstream commands（#8 ingest後）

這些command是後續implementation contract，目前module尚未建立，不能拿「command尚不可跑」誤判為本文件placeholder；#8每個對應task必須先實作module與tests，再以相同CLI驗收。

```bash
uv run python -m gperturb.provenance_lock \
  --config analysis/config/full.yaml \
  --out results/audit/run_manifest.json

uv run python -m gperturb.audit_joint_schema \
  --config analysis/config/full.yaml \
  --out results/audit/input_schema_audit.json

uv run python -m gperturb.audit_design_support \
  --config analysis/config/full.yaml \
  --out results/audit/design_support.parquet

Rscript -e 'targets::tar_make(names = c("simulation_recovery", "first_stage_effects", "effect_covariance", "candidate_benchmarks", "internal_controls"))'

uv run pytest -q tests/unit tests/schema tests/integration tests/synthetic
Rscript -e 'testthat::test_dir("tests/testthat")'

uv run python -m gperturb.validate_outputs \
  --schema-dir analysis/schemas \
  --results-dir results \
  --out results/verification_summary.json

spectra analyze generalizability-decomposition --json
spectra validate generalizability-decomposition
```

1%／10% benchmark的target IDs、gene shards與row groups由seed registry決定並保存checksum；不得人工挑較乾淨shard。Full run只在兩個shards的memory、scratch、scaling與resume gates全數通過後排程。Cell-level rebuild不是預設command；只有joint object不能提供已核准claim且新增資料有明確information gain時另立task。

### 14.3 Current audit-change verification

```bash
rg -n 'T[B]D|TO[D]O|PLACEH[O]LDER|待[填]|待[補]|之後[填]' \
  docs/complete-methodology-review-and-upgrade-plan.md

spectra analyze audit-complete-methodology --json
spectra validate audit-complete-methodology
git diff -- openspec/changes/generalizability-decomposition
```

第一個command須無match；最後一個command須無輸出。`blocked` findings若有具體reason、owner artifact與verification condition，不是placeholder。Current change的allowlist是`docs/complete-methodology-review-and-upgrade-plan.md`、`docs/README.md`及`openspec/changes/audit-complete-methodology/tasks.md` tracking update；不得修改#8 artifacts。

### 14.4 Issue #9 acceptance traceability

| Acceptance criterion | Normative location | Verification | Current document state |
|---|---|---|---|
| Durable doc存在且無placeholder | 本文件§1–§16 | §14.3 placeholder scan與16-heading count | contract complete後pass；empirical claims仍可blocked |
| Joint pseudobulk primary、marginal h5mu comparator | §1、§3、§5、§10 | data-branch／schema tests；h5mu rows不得有joint IDs | specified |
| Profile primary；gene／pathway distinct | §6–§8 | candidate table、two-stage/FDR與distinct null schema | specified |
| 每個component有observable unit與rank check | §4–§5 | identifiability crosswalk＋`design_support.parquet` | specified；actual gate blocked |
| Guide nesting、fixed C3、D4、run、matched NTC explicit | §4、§5、§7、§9、§12 | metadata audit、rank report、covariance manifest | specified；actual joint gate blocked |
| Permutation、bootstrap、shrinkage、multiplicity可測 | §7–§9、§11 | exchange registry＋synthetic thresholds | specified；execution blocked |
| Strict replication floor與honest null path | §4、§5、§10 | lane available／unavailable fixtures與nullable schema | specified；current floor not-identifiable |
| Null／adversarial simulation與quantitative gates | §11 | frozen scenario suite＋Monte Carlo summary | specified；not executed |
| K562不與T-cell replication混稱 | §4、§5、§12 | validation taxonomy／endpoint／split schema | specified；actual external data absent |
| Three Sol passes；P0/P1 gate | §15 | pass provenance、nine-column ledger、approval rule | A/B complete；C須在full draft後執行 |
| File-by-file crosswalk；不在#9實作code | §14、§16 | changed-file allowlist與#8 empty diff | specified |
| Final cross-layer self-review無矛盾 | §12.7、§15 Pass C、最終requirement matrix | Pass C＋`spectra analyze/validate` | pending Pass C，故document仍blocked |

## 15. GPT-5.6 Sol review log and finding ledger

### 15.1 Fixed model and isolation contract

三個 pass 都必須是新的 Codex task，設定完全相同：model=`gpt-5.6-sol`、reasoning effort=`max`。Pass A 與 B 互盲且只使用 `EB-2026-07-10-v1.1`；Pass C 是另一個新 task，只在完整 draft 與 A／B finding table 固定後執行。若指定模型無法執行，文件維持 `blocked`，不得以其他模型替代。

每個有效 pass 記錄：task identifier、timestamp（含 timezone）、model、reasoning effort、evidence manifest version、exact prompt 與完整 findings。Pass A／B 若要求其他資料，原 bundle 不變，finding 應指出 affected claim 與解除阻擋所需證據。

### 15.2 Severity 與 disposition

| 等級 | 定義 | Approval effect |
|---|---|---|
| P0 | 核心主張無效、不可識別，或設計使主要結論無法成立 | 未驗證處置即阻擋 |
| P1 | 會實質改變推論、ranking、error control 或 claim boundary 的偏誤／缺漏 | 未驗證處置即阻擋 |
| P2 | robustness、operability、效能或可重現性缺口 | 可列 residue，但須有 owner 與驗證時點 |
| P3 | 表達、文件導覽或可維護性問題 | 可列 residue，但須有 owner 與驗證時點 |

Finding schema 固定為九欄：`ID`、`pass`、`severity`、`finding`、`evidence`、`affected claim`、`proposed correction`、`disposition`、`verification`。Disposition 只能是：

- `resolved`：修正已寫入契約，且 verification 指向可重做的檢查或直接證據。
- `blocked`：目前無足夠證據或權限完成；verification 必須寫明解除條件。
- `rejected-with-evidence`：不採納 finding，verification 必須引用直接資料、simulation、primary literature 或 formal argument；不得只寫 owner preference。

### 15.3 Exact prompt — Pass A architecture／identifiability

```text
You are Sol Pass A, an independent architecture and identifiability red-team reviewer for G-perturb. This is a fresh review task. Use model gpt-5.6-sol with reasoning effort max. Do not ask for or inspect Pass B or Pass C output.

Repository base: <repo root>
Frozen evidence manifest: EB-2026-07-10-v1.1, source IDs E01-E21 and provenance identifiers X01-X04 exactly as listed in docs/complete-methodology-review-and-upgrade-plan.md section 3. In that manifest document, section 3 alone is authorised for manifest lookup; sections 1-2 and 4-16 are dynamic audit output and are outside this blind pass. You may read only section 3, the E01-E21 local evidence paths, and the two hash-verified GitHub records E02-E03. For E02-E03 use the canonicalisation commands printed in section 3.2. Do not inspect any other repository file or live external content. If evidence is missing, create an additional-evidence finding; do not expand the bundle.

Goal: challenge whether the proposed complete methodology can identify every stated variance, reliability, ranking, floor, validation, and transportability claim from the stated observation units. Audit the order estimand -> data variation -> rank/schema gate -> estimator -> uncertainty -> allowed wording. Pay special attention to guide nested within target, fixed conditions, four-donor scope, donor/condition/run confounding, matched NTC construction, marginal h5mu versus joint pseudobulk, identical-spec replication, incomplete grids, first-stage effect uncertainty, and whether a degradation branch changes the estimand.

Treat profile-level as the intended primary layer and gene-wise/pathway-level as secondary sensitivity/interpretation, but challenge that choice if it creates circular or unidentified claims. Do not select a final estimator on elegance alone. Distinguish design-specified from empirically-passed gates. Do not treat lack of downloaded pseudobulk as evidence that a gate passed.

Return one self-contained Markdown review containing:
1. Provenance: pass=A; current UTC timestamp; model=gpt-5.6-sol; reasoning_effort=max; evidence_manifest=EB-2026-07-10-v1.1.
2. Coverage matrix for claim architecture, observation units, estimands, rank/schema gates, uncertainty, degradation, validation boundaries, and handoff durability.
3. A finding table with exactly these nine columns: ID | pass | severity | finding | evidence | affected claim | proposed correction | disposition | verification. IDs use A-001 onward; severity is P0/P1/P2/P3; disposition is resolved/blocked/rejected-with-evidence. At review time use blocked unless the frozen evidence itself verifies a correction; state a concrete verification condition.
4. A concise list of claims that are identifiable now, design-specified only, marginal-only, or not-identifiable.
5. A final verdict of eligible-for-integration or blocked, with reasons.

Report only substantiated defects. Cite evidence by E-ID plus repo path or immutable issue URL, and distinguish direct evidence from inference. Do not invent findings to appear thorough.
```

### 15.4 Exact prompt — Pass B adversarial statistics

```text
You are Sol Pass B, an independent adversarial statistical reviewer for G-perturb. This is a fresh blind review task. Use model gpt-5.6-sol with reasoning effort max. Do not ask for or inspect Pass A or Pass C output.

Repository base: <repo root>
Frozen evidence manifest: EB-2026-07-10-v1.1, source IDs E01-E21 and provenance identifiers X01-X04 exactly as listed in docs/complete-methodology-review-and-upgrade-plan.md section 3. In that manifest document, section 3 alone is authorised for manifest lookup; sections 1-2 and 4-16 are dynamic audit output and are outside this blind pass. You may read only section 3, the E01-E21 local evidence paths, and the two hash-verified GitHub records E02-E03. For E02-E03 use the canonicalisation commands printed in section 3.2. Do not inspect any other repository file or live external content. If evidence is missing, create an additional-evidence finding; do not expand the bundle.

Goal: adversarially test the proposed statistical programme before estimator selection. Evaluate at minimum exchangeability and restricted randomisation, matched-NTC effect construction and measurement-error covariance, high-dimensional gene dependence, additive versus non-Euclidean component interpretation, sparse-facet bias with two guides/four donors, selection and winner's curse, atlas-wide plus stage-wise/selective FDR, pathway competitive versus self-contained hypotheses, validation leakage, target-level shrinkage assumptions, uncertainty propagation, missing cells, common support under run confounding, negative components, and computational feasibility for approximately 44.6 GB joint pseudobulk with a 1.6 TB cell-level fallback.

Compare these profile candidates without declaring a winner before synthetic recovery: (i) precision-weighted multivariate linear decomposition, (ii) kernel/distance-based restricted permutation, and (iii) robust hierarchical functional modelling. Treat CCC and Pearson as diagnostics unless formal evidence supports factorial decomposition. Audit gene-wise two-stage effect-plus-covariance modelling and pathway CAMERA versus ROAST/FRY as distinct secondary layers. Demand pre-specified null and adversarial simulation thresholds, NTC controls, guide cross-fit, leave-one-donor-out, common-support sensitivity, and non-leaking external validation taxonomy.

Return one self-contained Markdown review containing:
1. Provenance: pass=B; current UTC timestamp; model=gpt-5.6-sol; reasoning_effort=max; evidence_manifest=EB-2026-07-10-v1.1.
2. Coverage matrix explicitly covering exchangeability, measurement error, high-dimensional dependence, selection/FDR, validation leakage, and compute.
3. A finding table with exactly these nine columns: ID | pass | severity | finding | evidence | affected claim | proposed correction | disposition | verification. IDs use B-001 onward; severity is P0/P1/P2/P3; disposition is resolved/blocked/rejected-with-evidence. At review time use blocked unless the frozen evidence itself verifies a correction; state a concrete verification condition.
4. Candidate-method failure modes and the synthetic scenario that would expose each one.
5. A final verdict of eligible-for-integration or blocked, with reasons.

Report only substantiated defects. Cite evidence by E-ID plus repo path or immutable issue URL, and distinguish direct evidence from inference. Do not invent findings to appear thorough.
```

### 15.5 Exact prompt — Pass C integration／handoff

```text
You are Sol Pass C, the independent integration and handoff auditor for G-perturb. This is a fresh review task. Use model gpt-5.6-sol with reasoning effort max. You are not re-voting Pass A or B. You are checking whether the reconciled methodology faithfully resolves or explicitly blocks their findings without introducing cross-layer contradictions.

Repository base: <repo root>
Frozen evidence manifest: EB-2026-07-10-v1.1, source IDs E01-E21 and provenance identifiers X01-X04 in docs/complete-methodology-review-and-upgrade-plan.md section 3. Additional authorised inputs are the complete current draft of that document and the archived Pass A and Pass B records embedded in section 15. Do not inspect any other repository file or live external content. If more evidence is needed, create an additional-evidence finding rather than changing the bundle.

Audit every A/B finding and every conflict between them. Check consistency across: estimand registry; claim-to-data identifiability crosswalk; profile primary model; gene-wise sensitivity; pathway interpretation; uncertainty/permutation/bootstrap/shrinkage; missingness/QC/degradation; synthetic falsification thresholds; internal/external validation; pipeline schemas; implementation order; approval gate; and the file-by-file #8 ingest crosswalk. Verify that actual pseudobulk gates not yet run remain design-specified, marginal h5mu is not promoted to joint evidence, K562 is only transportability evidence, and absence of identical-spec replicates yields floor=not_identifiable.

Return one self-contained Markdown review containing:
1. Provenance: pass=C; current UTC timestamp; model=gpt-5.6-sol; reasoning_effort=max; evidence_manifest=EB-2026-07-10-v1.1.
2. One adjudication row for every A/B finding and every detected A/B conflict.
3. A finding table with exactly these nine columns: ID | pass | severity | finding | evidence | affected claim | proposed correction | disposition | verification. IDs use C-001 onward; severity is P0/P1/P2/P3; disposition is resolved/blocked/rejected-with-evidence.
4. A requirement-by-requirement completeness matrix for all 16 chapters and approval conditions.
5. A final verdict: approved only if no P0/P1 is blocked or unverified; otherwise blocked with each release condition stated.

Report only substantiated defects. Cite evidence by E-ID, A/B finding ID, and exact draft heading. Distinguish direct evidence from inference. Do not invent findings to appear thorough.
```

### 15.6 Pass records

Pass records將在各指定模型 task 完成後原樣封存，再由主文件另作 finding adjudication；未執行的 pass 不會建立假紀錄。

下列 preflight tasks 不算三個有效 pass，也不會把其 findings 納入 ledger：

| Task identifier | Intended pass | Manifest | Invalid reason |
|---|---|---|---|
| `019f4826-a0e8-7762-bc86-0745f7b86c01` | A | `EB-2026-07-10-v1` | reviewer 讀取 manifest 文件第 4–14 章的動態 draft，超出 frozen evidence boundary |
| `019f4826-9e47-77f0-b33f-fd75e5dbf165` | B | `EB-2026-07-10-v1` | 為確保 A／B 使用完全相同、已補 canonicalization 的 manifest 與 isolation wording，與 A 一併重跑 |

### 15.7 Valid Pass A record

- Task identifier：`019f482b-263c-71d2-adce-f990a37819c8`
- Model／effort：`gpt-5.6-sol`／`max`
- Evidence：`EB-2026-07-10-v1.1`
- Exact prompt：第 15.3 節
- Isolation：task 未收到 Pass B／C output 或其他 follow-up prompt；只讀第 3 節 manifest 與 E01–E21

#### Archived reviewer output（verbatim；下列 `>` 是 Markdown 引文標記，不屬於 reviewer 文字）

> # G-perturb — Sol Pass A 架構與可識別性紅隊審查
> 
> ## 1. Provenance
> 
> - `pass=A`
> - `timestamp_utc=2026-07-09T18:45:53Z`
> - `model=gpt-5.6-sol`
> - `reasoning_effort=max`
> - `evidence_manifest=EB-2026-07-10-v1.1`
> - E02、E03 依第 3.2 節正規化指令重新核對，SHA-256 均吻合。
> - E01、E04–E21 的 commit／檔案雜湊均重新核對通過。
> - X01–X04 僅作 provenance identifier；未讀取即時外部內容。
> - 未查看文件第 1–2、4–16 節、其他 repo 檔案或 Pass B／C 輸出。
> 
> ## 2. Coverage matrix
> 
> | Area | Frozen evidence coverage | Status | Integration implication |
> |---|---|---|---|
> | Claim architecture | E19–E21 已要求先定 estimand，再檢查資料與估計量；但 frozen evidence 只有 registry 契約，沒有已實例化的 registry。 | design-specified／blocked | 未定義 profile universe score、權重、threshold 與 relative／absolute decision 前，不得選 primary estimator。 |
> | Observation units | E11 直接定義 joint pseudobulk 為 guide×donor×condition，並含 run；E09/E11 顯示 h5mu 僅為分別邊際化的 target×condition DE。 | schema documented；joint object not inspected | h5mu 只能支援 marginal agreement；完整 crossed decomposition 尚未通過資料 gate。 |
> | Estimands | Fixed conditions、four-donor panel、relative ranking、absolute hit call、transportability 等名稱已列出。 | design-specified | 尚缺明確 object、gene-space measure、condition weights、missingness policy、threshold 與允許措辭。 |
> | Rank/schema gates | 必要欄位、唯一鍵、NTC、缺格與設計矩陣秩已列入契約。 | not empirically passed | 還須檢查 variance-component covariance-basis identifiability，以及 distance/kernel 的可加總性；一般固定效果矩陣滿秩並不足夠。 |
> | Uncertainty | E20 要求第一階段 sampling uncertainty、restricted permutation、bootstrap 與 shrinkage。 | incomplete／blocked | Shared matched NTC 所誘發的共變異、target-specific sampling variance 來源及 FH 權重仍未定義。 |
> | Degradation | `marginal_only` 與無 replicate 時 `not_identifiable` 的邊界正確。 | partly adequate | R2-only、single-guide fallback 與 target-specific complete-case selection會改變 estimand，必須另設 `estimand_id`，不能沿用同一排名。 |
> | Validation boundaries | E20–E21 正確區分 T-cell replication、assay translation 與 K562 transportability。 | design-specified only | Bundle 沒有實際 K562／T-cell validation values，無法檢查共同支援、選擇機制或 tuning/holdout 分離。 |
> | Handoff durability | Manifest 本身可重做且雜湊吻合。 | partial | E09 仍把 E14 列為未下載，E10 也無法重建 E14；companion source 尚未固定到 immutable commit/path。 |
> 
> ## 3. Findings
> 
> | ID | pass | severity | finding | evidence | affected claim | proposed correction | disposition | verification |
> |---|---|---|---|---|---|---|---|---|
> | A-001 | A | P1 | Frozen evidence 只有「必須建立 estimand registry」的要求，尚無可供估計量共同對照的實際 registry；目前的 profile norm、distance、latent effect 與 `P(τ_t > c)` 並非自動估計同一 quantity。 | Direct: E05 · `docs/design.md` 同時提出 per-gene、scalar、profile distance 與未定義的 `τ_t,c`；E20 · `openspec/changes/audit-complete-methodology/design.md` 僅要求後續建立 registry。Inference: estimator comparison 目前缺共同 estimand。 | 所有 variance、reliability、relative ranking 與 absolute hit-call claim | 先建立帶唯一 `estimand_id` 的 registry，固定 object、observation unit、gene-space measure、condition weights、decision universe、threshold、missingness 與 uncertainty target；候選估計量逐一映射至同一 ID。 | blocked | Registry 完整，且每個 estimator/output 只引用一個明確 estimand 或明確定義的 estimand vector；改變 weights、support 或 threshold 會產生新 ID。 |
> | A-002 | A | P0 | **additional-evidence:** 實際 joint pseudobulk 不在 bundle；schema 說明不能證明 composite-key coverage、matched NTC、缺格、秩或 component identifiability 已通過。 | Direct: E11 · `analysis/data/raw/data_sharing_readme.md` 只描述 schema；[E03 · Diagnosis](https://github.com/kiki830621/G-perturb/issues/9#issuecomment-4928187622) 明載 actual grid/rank 尚未驗證。 | 完整 guide-within-target、donor、condition 與 interaction profile decomposition | 保持所有完整 component 為 `design-specified`；下一版 manifest 納入 hash-fixed pseudobulk schema/grid report，逐 target 與整體檢查必要欄位、count validity、唯一鍵、NTC coverage、缺格與 candidate-specific rank。 | blocked | 新 manifest 提供可重做的 grid/rank 輸出，所有必要 gate 通過，且受影響 blind pass 依新 manifest 重跑；否則只能輸出 `marginal_only`。 |
> | A-003 | A | P1 | 一般 design-matrix rank gate 不足以識別 variance components；對 nested、缺格設計，必須檢查投影後 component covariance bases 是否線性獨立。Distance/kernel 方法另須證明 kernel 合法、share 可加總且不依 term order。 | Direct: E16 · `openspec/changes/generalizability-decomposition/design.md` 曾鎖定 `1−CCC`；E20–E21 只概括要求 rank、additivity 與 synthetic recovery。Inference: fixed-effect full rank 不保證 covariance parameters 或 PERMANOVA shares 唯一。 | Facet variance shares、interaction shares、primary estimator 選擇 | 對每個候選方法建立 estimability gate：固定效果投影後檢查 component-basis／Fisher-information／Jacobian rank；distance 方法檢查 negative type 或 kernel PSD、非平衡設計的 share 定義與 term-order invariance。 | blocked | 在實際 support 與 synthetic incomplete grids 上，每個保留 component 具唯一映射、足夠秩與預設 recovery threshold；不同合法 term order 不改變所稱 estimand。 |
> | A-004 | A | P1 | Run 與 donor×condition cell 未交叉。四 donor 的 biological condition contrast只能描述 observed-run 配置；R2-only common-support sensitivity 僅剩兩位 donor，因而改變 donor-panel estimand。 | Direct: E12 · `analysis/data/raw/sample_metadata.suppl_table.csv` 顯示 Rest／Stim8hr 的兩位 donor 在 R1、另兩位在 R2，Stim48hr 全在 R2，每個 donor×condition 只有一個 sample。Inference: 加法式模型可估 run main effect，但保留完整 donor×condition cell 後 run 與 cell pattern alias。 | Condition effects、target×donor／target×condition shares、run component、four-donor ranking | 分開註冊「四 donor、observed-run conditional」與「R2、兩 donor common-support」estimands；不得估獨立 target×run component；matched NTC 只能消除共同 run main effect，target×run 無交互作用必須列為假設。 | blocked | Rank report 明示哪些 run terms aliased；主要與 R2 sensitivity 使用不同 `estimand_id`、donor count 與 allowed wording；模擬注入 target×run effect 時不誤歸為 donor／condition。 |
> | A-005 | A | P1 | Condition 雖被宣告為 fixed domain，舊設計仍以 `σ²_C` 與可變 `n_c` D-study 表示。固定三條件可有描述性加權 dispersion／contrast，但不能當未觀測 condition population 的 random variance。 | Direct: E05 · `docs/design.md` 同時寫 condition fixed，卻在 D-study 公式使用 `σ²_TC/n_c`；E19–E20 要求 fixed-domain 修正，但尚未驗證下游 crosswalk 已移除舊語意。 | Condition variance share、global dependability、D-study condition projection | 將 condition 主效應與 target×condition 定義為三個命名狀態上的固定 contrast／加權異質性；刪除對未觀測 condition 的 generalization。只有預先指定的有限域 subset／weight projection 可稱 D-study sensitivity。 | blocked | Registry 與 #8 crosswalk 不再出現 random `σ²_C` 或「新增 conditions」人口推論；所有 condition outputs 均列出三個狀態及固定 weights。 |
> | A-006 | A | P1 | Matched NTC 的構造與共同控制共變異未完整定義；permutation null 或 within-target disagreement 也不是 target-specific measurement sampling variance，不能直接作 Fay–Herriot 權重。 | Direct: E11 · `analysis/data/raw/data_sharing_readme.md` 顯示 effect 必須由 count-level pseudobulk 建立；E16 · `openspec/changes/generalizability-decomposition/design.md` 建議由 permutation null／within-target dispersion取得 sampling variance；E20 將其列為未解問題。Inference: 共用 NTC 會使 guide、target contrasts 相關，而 guide/donor disagreement包含真實 facet variation。 | 第一階段 profile uncertainty、variance shares、target-level shrinkage、CI 與排名 | 明定 block 內 NTC pooling、offset、最低 NTC 支援與 contrast estimand；由 count likelihood／voom/NB fit 取得含 shared-control covariance 的聯合第一階段 covariance，再以 delta method 或 parametric bootstrap 傳至 profile statistic。 | blocked | Synthetic counts 中的第一階段 covariance、FH interval coverage 與 shrinkage weights通過預設門檻；更換 NTC split 不造成未解釋的 component 偏移。 |
> | A-007 | A | P1 | Guide nested within target 可由資料支持，但「guide-universe generalization」還需未被證據提供的 guide 選取／exchangeability 假設；兩條設計 guide 只能直接支持 observed-guide consistency。 | Direct: E13 · `analysis/data/raw/sgrna_library_metadata.suppl_table.csv` 有 12,440 targets 各 2 guides、163 targets 僅 1 guide，少數 3–4 guides，且未記錄機率抽樣機制；E05 將 guide 視為 random universe。 | Guide variance、future-guide reliability、guide D-study | 主要用語限於 observed-guide consistency；若保留 guide-universe claim，須定義 guide-design universe、selection mechanism、exchangeability 與 KD/off-target conditional model，並把它標為 model-based extrapolation。 | blocked | 新的獨立 guides 或嚴格 held-out guide prediction 通過預設校準；否則 output schema 只能使用 `observed_guide_consistency`。 |
> | A-008 | A | P1 | Single-guide 的 donor fallback 或依可用 facets 重新加權，會把不同 estimand 混進同一 `R_dep` 排名；非零分數不代表 guide reliability 已識別。 | Direct: E08 · `analysis/data/DATA_AND_ASSUMPTIONS.md` 記載 guide_2 少 7,410 個 target×condition rows；E17 · `openspec/changes/generalizability-decomposition/specs/generalizability-decomposition/spec.md` 要求 donor fallback。Inference: complete-case 與 fallback scores不具共同 measurement design。 | Target-level dependability、relative ranking、single-guide輸出 | Single-guide 保留於資料表，但 guide facet 設為 `not_identifiable`；完整 ranking、partial-evidence tier 與 model-predicted missing-facet ranking分開。若預測缺失 facet，必須維持相同 estimand並加入 prediction uncertainty。 | blocked | 測試確認 single-guide 不會以 donor score冒充 guide score；共同排名中的 targets 使用同一 estimand，或明確標示 predictive tier 與較寬 uncertainty。 |
> | A-009 | A | P1 | Profile primary 尚未明定 target-blind outcome-gene universe；依「任一 guide 的 DE hits」或 per-target hit subset計算距離會循環選擇、使每個 target 使用不同量尺，並破壞 null calibration。 | Direct: E05 · `docs/design.md` 提議限制到至少一條 guide 顯著的 genes；E16 · `openspec/changes/generalizability-decomposition/design.md` 以 hit-gene subset 作運算降級；E20–E21 的 target-blind規則主要寫在 gene-wise layer。 | Primary profile reliability、ranking、profile/gene/pathway一致性 | Profile layer 同樣固定 target-blind expressed/technical-QC gene universe及權重；若學習 projection、kernel或降維，須跨 target cross-fit，且特徵選擇不讀取該 target 的 DE 結果。 | blocked | 程式測試證明 profile feature set不依 target p-value／DE status；null simulation的 type-I error與排名偏差通過門檻。 |
> | A-010 | A | P1 | E14 只能提供 guide×condition 的邊際 KD，沒有 donor/run，且 NTC 量為 condition-wide aggregate；它不能識別 donor/run-specific KD，也不能無條件把 joint profile轉成「每單位 KD」或 fully normalized effect。 | Direct: E14 · `analysis/data/raw/guide_kd_efficiency.suppl_table.csv` 無 donor/run 欄位，三個 condition 各有單一 `ntc_n`；E05 要求 effect per unit KD。Inference: division或covariate adjustment需要額外同質性、measurement-error與近零分母假設。 | KD-adjusted effect、quality-adjusted ranking、guide variance解釋 | Raw CRISPRi intent-to-treat profile作 primary；E14 只作 guide×condition QC／sensitivity。若另估 per-unit-KD estimand，須限制適用範圍、模型化 KD uncertainty、禁止近零 ratio，且不得宣稱 donor-specific校正。 | blocked | Raw與KD-sensitive estimands各自有 ID；simulation含弱／零 KD 時維持 coverage與有限估計；held-out guide結果顯示校正改善而非放大偏差。 |
> | A-011 | A | P1 | **additional-evidence:** 現有 pseudobulk 描述沒有 identical-spec replicate dimension；不同 guides、donor halves 或 NTC splits不能識別 targeting-profile replication floor。 | Direct: E11 · `analysis/data/raw/data_sharing_readme.md` 指 pseudobulk 已聚合至 guide×donor×condition，cell-level lanes亦已合併；E12 每 donor×condition 只有一個 library；E20 明訂 identical-spec規則。 | Distribution-free replication floor、sampling residual與最高階 interaction分離 | 目前固定輸出 `floor_status=not_identifiable`，並合併 highest-order interaction與sampling residual。只有新增相同 target、guide、donor、condition下的獨立 lane/library資料後才重新啟用。 | blocked | 無追加資料時，schema含 combined-residual reason code且沒有 floor數值；若新增 lane artifact，須以新 manifest 固定、至少每規格兩個獨立 units，重做 rank/confounding audit與受影響 blind pass。 |
> | A-012 | A | P1 | **additional-evidence:** Bundle 沒有實際 K562或same-cell-type validation values，故無法查核 common support、selection bias、threshold tuning或 untouched holdout；目前只能規定 wording，不能驗證 validation/transportability claim。 | Direct: E08 · `analysis/data/DATA_AND_ASSUMPTIONS.md` 記載 Th1Th2 table unavailable；E11 · `analysis/data/raw/data_sharing_readme.md` 只提供 K562／Th1Th2 schema敘述；E20 正確限制 K562為transportability。 | Independent validation、K562 transportability、T-cell replication、reliability→replication curve | 下一版 manifest 固定實際 validation tables、eligibility/join report與 tuning/holdout assignment。K562只稱 cross-cell-type transportability；沒有獨立 T-cell資料時，T-cell replication=`not_identifiable`。 | blocked | 新 manifest 可重做地顯示 join coverage、預先指定 endpoint與完全分離的 tuning/test；若使用同一資料調參，僅報 nested holdout結果。 |
> | A-013 | A | P2 | **additional-evidence／handoff:** KD artifact 的 provenance 無法由現行 repo契約重建：E09仍列為未下載，E10不會抓取它，而 E14僅以本機雜湊固定，X04未固定 companion commit/path。 | Direct: E09 · `analysis/data/CODEBOOK.json` 將 guide KD列在 `products_not_downloaded`；E10 · `analysis/data/fetch_data.sh` 不抓取 companion檔；E14 · `analysis/data/raw/guide_kd_efficiency.suppl_table.csv` 實際存在且已固定雜湊。 | Reproducibility、KD sensitivity、後續agent handoff | 固定 companion repository commit、精確path與immutable raw URL；更新 fetch流程、CODEBOOK與provenance，使乾淨環境可取得同一 bytes。 | blocked | 從空的 `raw/` 執行文件化流程後得到與 E14 相同 SHA-256，且 codebook不再宣稱該檔未下載。 |
> 
> ## 4. Claim identifiability summary
> 
> ### Identifiable now
> 
> - Manifest 完整性與 E02／E03 正規化雜湊。
> - 4 donors × 3 conditions 的 12 個 sample，以及 run 配置和 R2 的兩-donor共同支援；E12 · `analysis/data/raw/sample_metadata.suppl_table.csv`。
> - Guide→target nesting、guide-count分布與 NTC／flagged-guide metadata；E13 · `analysis/data/raw/sgrna_library_metadata.suppl_table.csv`。
> - KD資料僅到 guide×condition、缺 donor/run 的事實；E14 · `analysis/data/raw/guide_kd_efficiency.suppl_table.csv`。
> - Joint pseudobulk與marginal h5mu的schema／grain差異；E09 · `analysis/data/CODEBOOK.json`、E11 · `analysis/data/raw/data_sharing_readme.md`。
> 
> ### Design-specified only
> 
> - Matched-NTC genome-wide profile estimand及其聯合sampling covariance。
> - 三個fixed conditions的預先加權平均、relative ranking與absolute hit call。
> - Joint profile variance components、target-level shrinkage、D-study與machine-readable degradation。
> - Gene-wise／pathway sensitivity、simulation thresholds及validation protocols。
> 
> ### Marginal-only
> 
> - `by_guide.h5mu` 的observed cross-guide agreement。
> - `by_donors.h5mu` 的donor-pair／split-half agreement。
> - Aggregate target×condition effect與預先計算的Pearson diagnostics。
> - 以上不得拼接成joint guide×donor interaction或完整crossed decomposition。
> 
> ### Not-identifiable from the frozen bundle
> 
> - 實證通過的joint component shares或primary profile estimator。
> - Saturated donor×condition structure之外的獨立target×run component。
> - 無identical-spec replicate時的replication floor，以及最高階interaction與sampling residual的拆分。
> - Single-guide target的guide reliability。
> - 對未觀測conditions或human donor population的generalization。
> - 由E14得到的donor/run-specific KD-normalized effect。
> - Independent T-cell replication；實證K562 transportability也因actual table不在bundle而尚未驗證。
> 
> ## 5. Final verdict
> 
> **blocked**
> 
> 理由：
> 
> 1. A-002 是 P0：joint pseudobulk grid、matched NTC coverage及component rank均未實證通過。
> 2. Primary estimator仍缺共同estimand、candidate-specific covariance-rank／additivity gate及可校準的第一階段uncertainty。
> 3. Run配置、fixed-condition語意、single-guide與R2-only branches尚未保證維持相同estimand。
> 4. Replication floor、T-cell replication及實證transportability目前均缺必要觀測或凍結證據。
> 5. A-001–A-012 的 P0/P1 findings 全為 `blocked`；依E20–E21 approval gate，不符合 `eligible-for-integration`。

### 15.8 Valid Pass B record

- Task identifier：`019f482b-2960-7b10-b5ba-6f52a863adab`
- Model／effort：`gpt-5.6-sol`／`max`
- Evidence：`EB-2026-07-10-v1.1`
- Exact prompt：第 15.4 節
- Isolation：task 在 Pass A output 尚未提供前獨立完成；沒有收到 A／C output 或其他 follow-up prompt

#### Archived reviewer output（verbatim；下列 `>` 是 Markdown 引文標記，不屬於 reviewer 文字）

> # G-perturb：Sol Pass B 對抗性統計審查
> 
> ## 1. Provenance
> 
> | 欄位 | 值 |
> |---|---|
> | pass | `B` |
> | current UTC timestamp | `2026-07-09T18:45:10Z` |
> | model | `gpt-5.6-sol` |
> | reasoning_effort | `max` |
> | evidence_manifest | `EB-2026-07-10-v1.1` |
> | base commit | `bf1cf09d91e1c77a528a46d5bff456f717105ebf` |
> | repository base | [<repo root>](<repo root>) |
> | evidence integrity | E02、E03 依第 3.2 節 canonicalisation 重算後雜湊相符；E04–E21 全部通過 manifest SHA-256 |
> | blind-review boundary | 未查看 Pass A、Pass C、方法文件第 1–2 與第 4–16 節、其他儲存庫檔案或未封存外部內容；X01–X04 僅視為識別碼 |
> 
> 本審查採證據驗證框架，把「凍結證據直接顯示的事實」與「由該事實導出的統計推論」分開。E19–E21 視為擬議升級契約；E04–E18 視為其要取代的舊契約。已由 E19–E21 明確修正的方向，例如 guide nested within target、condition 為 fixed domain、無 identical-spec replicate 時 floor=`not_identifiable`、CCC/Pearson 僅為 diagnostics，不重複列為新 finding。
> 
> ## 2. Executive assessment
> 
> **初步判定：`blocked`。不選定候選方法。**
> 
> 擬議計畫的方向正確，但仍有三個 P0：
> 
> 1. 44.6 GB joint pseudobulk 不在凍結證據包中，無法實證檢查 target-level grid、缺格、NTC coverage 或設計矩陣秩。
> 2. kernel/distance 的「分量」尚未取得可加總 variance-component 詮釋；任意 `1 − CCC` 不得直接改稱變異占比。
> 3. E12 的 run 配置使 run 在完整 donor×condition 交互作用模型中共線；R2 三條件共同支撐只剩兩位 donor。
> 
> 因此三類 profile 候選均只能進入 synthetic recovery，不能先宣告 primary。
> 
> ## 3. Coverage matrix
> 
> | 審查領域 | 凍結證據 | 審查結果 | 對應 finding |
> |---|---|---|---|
> | 可交換性與受限制隨機化 | E12 `analysis/data/raw/sample_metadata.suppl_table.csv`；E13 `analysis/data/raw/sgrna_library_metadata.suppl_table.csv`；E20–E21 | 已要求 restricted permutation，但沒有逐 estimand 的 null、交換單位、block、殘差交換條件或有限置換解析度 | B-004 |
> | matched-NTC 與 measurement error | E11 `analysis/data/raw/data_sharing_readme.md`；E14 `analysis/data/raw/guide_kd_efficiency.suppl_table.csv`；E09 `analysis/data/CODEBOOK.json` | E14 的 NTC 是 condition-wide pool，不能代替 donor×condition×run matched NTC；共享 NTC 所誘發的 contrast covariance 尚未定義 | B-005 |
> | 高維基因相依 | E09 顯示既有 DE profiles 約 10,282 genes；E11 顯示 pseudobulk 18,129 genes | 計畫承認基因相關，但尚未指定 covariance operator、正則化、target-blind basis 或 distance-concentration 診斷 | B-006 |
> | selection、贏家詛咒與 FDR | E05 `docs/design.md`；E11；E20–E21 | 舊設計曾依顯著基因算 agreement；新契約要求 atlas-wide 與 stage-wise FDR，但未定義檢定家族、screening hypothesis 或 selective procedure | B-008 |
> | validation leakage | E05；E08 `analysis/data/DATA_AND_ASSUMPTIONS.md`；E21 | 舊設計擬用同一 validation 校準權重與宣稱預測能力；新契約禁止重複使用，但 bundle 缺 validation target overlap 與 frozen split | B-010 |
> | 計算可行性 | [E02 Issue #9](https://github.com/kiki830621/G-perturb/issues/9)；[E03 Diagnosis](https://github.com/kiki830621/G-perturb/issues/9#issuecomment-4928187622)；E09 | 已禁止 densify 與 target² distance matrix，但沒有候選方法的 pilot benchmark、記憶體、暫存空間或 wall-clock gate | B-011 |
> | additive 與 non-Euclidean 詮釋 | E16–E17；E20–E21 | 新契約撤回 CCC 的預設分解地位是正確方向；但 kernel/distance component 的數學定義及 PSD、位置與離散度分離仍未完成 | B-002 |
> | 稀疏 facet、shrinkage 與負分量 | E12–E13；E08；E16 | 2-guide/4-donor 資訊量極低，Fay–Herriot direct variance、linking model、boundary inference 與負分量政策均未操作化 | B-007 |
> | missing cells 與 common support | E11–E13 | sample-level run 結構已知，但 target×guide 層級缺格未知；不得補零或假定 missing at random | B-001、B-003 |
> | gene-wise 與 pathway 次層 | E02；E20–E21 | 兩階段 effect-plus-covariance 與 CAMERA/ROAST/FRY 的方向已列出，操作層契約仍不足 | B-005、B-008、B-009 |
> 
> ## 4. Findings
> 
> | ID | pass | severity | finding | evidence | affected claim | proposed correction | disposition | verification |
> |---|---|---|---|---|---|---|---|---|
> | B-001 | B | P0 | **`additional-evidence`：joint pseudobulk 未在 bundle，完整 crossed programme 尚不能通過實證 identifiability gate。** | **直接：**E02 [Issue #9](https://github.com/kiki830621/G-perturb/issues/9) 明列尚未下載 `GWCD4i.pseudobulk_merged.h5ad`；E11 `analysis/data/raw/data_sharing_readme.md` 只提供 schema；E20 `openspec/changes/audit-complete-methodology/design.md` 把下載列為 non-goal。**推論：**無法確認 row uniqueness、實際 targeting/NTC grid、缺格機制或逐 target rank。 | 完整 target×guide×donor×condition profile decomposition；任何 estimator selection | 建立新版 manifest，封存 object checksum、shape、CSR/count audit、所有必要 `.obs` 欄位、逐 block NTC 數量、逐 target coverage 與設計秩輸出；依 frozen-evidence policy 重跑受影響 blind pass。 | blocked | 新 manifest 必須證明 counts 非負整數、row key 唯一、guide→target 一致、每個使用中的 donor×condition×run block 有 NTC，並逐 target 列出 estimable columns、rank、condition number、缺格與 reason code；在此之前只能標 `design-specified`。 |
> | B-002 | B | P0 | **尚未建立 non-Euclidean distance shares 與可加總 variance components 的等價性。** | **直接：**E16 `openspec/changes/generalizability-decomposition/design.md` 曾鎖定 `1 − CCC`；E17 要求非負 shares 加總為 total dispersion；E21 只要求比較 kernel/distance 且把 CCC 降為 diagnostic。**推論：**`1 − CCC` 的 pair-specific denominator 並未被證明產生 squared-Euclidean distance；double-centred Gram matrix 可能非 PSD。PERMANOVA 亦可能混合中心位置與群內離散度。 | headline facet variance shares、additivity、D-study | 分開定義：Euclidean/Hilbert trace components、RKHS sums of squares、純 diagnostic distances。Kernel 必須預先固定且證明 PSD；不平衡設計固定 marginal而非順序型 partition；另做 PERMDISP。無證明時只能稱 distance-based attribution，不能稱 variance component。 | blocked | 形式證明或數值 gate：所有測試矩陣的最小特徵值不得低於總 trace 的 `−1e−8`；已知 Euclidean component truth 的絕對 bias 須通過下述 recovery gate；純 dispersion-null 情境不得產生位置效應。 |
> | B-003 | B | P0 | **run、donor×condition interaction 與共同支撐無法同時由現有 sample layout 分離。** | **直接：**E12 有 12 個 donor×condition samples；Rest／Stim8hr 的 D1、D2 在 R1，D3、D4 在 R2；Stim48hr 全在 R2。**重算：**additive `donor+condition+run` 為 rank 7/7，但 `donor×condition+run` 為 rank 12/13；加入 run 沒有新增秩。R2 三條件共同支撐只有 CE0008678、CE0006864 六個 cells。 | donor heterogeneity、condition effects、run component、完整四 donor fixed-domain average | 每個 estimand 明列允許的 interaction 與支撐族群。四 donor 分析只能在明確 additive restriction 下進行；三條件 common-support sensitivity 固定為 R2 的兩 donor，並標示 two-donor panel。缺格不得補零；需另做 selection/MNAR sensitivity。 | blocked | 對每個 target 的實際 pseudobulk 設計矩陣做 rank 與共線診斷；任何宣稱的 component 必須有新增秩。完整結果與 R2-common-support 結果均需輸出，超出支撐的 condition claim 必須 fail closed。 |
> | B-004 | B | P1 | **restricted permutation 只有名稱，沒有可審計的交換群。** | **直接：**E13 證明 guide nested within target 且 guide 數不平衡；E12 證明 run block 不平衡；E20–E21 要求 restricted permutation，但未指定每個 null 的可交換單位、strata、殘差化方法或 heteroskedasticity 條件。 | kernel/distance p-values、component tests、NTC null、stage-wise screening | 為每個 estimand 定義 sharp/weak null、交換單位與交換群。禁止跨 target、run 或 donor×condition block 換標籤；若使用 Freedman–Lane，需證明 reduced-model residual 可交換，否則改用 block/cluster wild bootstrap。 | blocked | 列出每個檢定的 admissible permutation 數與最小可達 p-value；在 E12-like confounding、缺格、異變異及共享 NTC null 下，type-I error 通過定量 gate。置換數不足時使用 exact p-value 並揭露解析度。 |
> | B-005 | B | P1 | **matched-NTC effect 與第一階段 measurement-error covariance 未操作化，gene-wise 第二階段因此可能把估計值當成獨立真值。** | **直接：**E11 說 pseudobulk 有 count、run、guide_type；E14 的 `ntc_n` 在每個 condition 只有一個全域值，且 E11 定義它為 across-all-samples NTC；E09／E11 的 marginal products只有 `lfcSE`，沒有跨 guide、gene、target 或 condition covariance。**推論：**共用同一 NTC reference 的 contrasts 必然共享誤差。 | profile precision weighting；gene-wise two-stage model；CI、sign probability、false-sign control | 在 donor×condition×run 內聯合建模 targeting 與 NTC counts，保留 library offset、overdispersion 與 contrasts。輸出 effect vector 及完整或經驗證的 low-rank covariance，包含共享 NTC 項。第二階段以 GLS／measurement-error likelihood 使用該 covariance，不得只用對角 `lfcSE²`。 | blocked | 每個 block 有足夠 NTC，否則 reason code；analytic covariance 與 block bootstrap covariance 一致；NTC-vs-NTC、95% coverage、type-I error 通過定量 gate。 |
> | B-006 | B | P1 | **高維基因相依尚無可執行契約；三種候選都可能在不同方式下失效。** | **直接：**E09 顯示現有 profile 約 10,282 genes；E11 顯示 joint pseudobulk 18,129 genes；E08 已承認 co-expression 使有效自由度遠低於 gene count。E20 僅列出比較準則。 | profile norm、precision weights、kernel bandwidth、functional basis、uncertainty | 先凍結 target-blind expression/technical universe；由 NTC 或 cross-fit training data 估計 shrinkage covariance／factor basis。禁止 naïve gene permutation、未正則化的全 `p×p` covariance 或依 DE significance 選 features。每個候選都需報有效秩與 distance concentration。 | blocked | 在獨立、latent-factor、block-correlated、稀疏 pathway 與 dense signal 情境分層驗證 type-I、bias 與 coverage；feature/basis 改變不得導致未揭露的 component reversal。 |
> | B-007 | B | P1 | **2 guides／4 donors 下，target-level shrinkage 可能由 linking assumption 主導；負分量政策亦未解決。** | **直接：**E13 解析得到 163 targets 有 1 guide、12,440 有 2、50 有 3、1 有 4；E12 只有 4 donors。E08 明列 cross-target exchangeability 是 partial-pooling 假設；E16 曾規定負 moment component 截為零。E20 仍把 direct estimate 與 covariance 來源列為 open question。 | target-level `R_dep,t`、Fay–Herriot、CI、D-study、single-guide outputs | 預先定義 direct estimator、抽樣 variance/covariance、bounded link 與 linking model；允許 target-class mixture 或 robust prior，並做 prior sensitivity。Hyperparameters 在 guide/target cross-fit 外估計。保留 unconstrained negative estimate 作診斷；constrained fit 使用明訂 estimator 與 boundary-aware bootstrap，不得事後截零再重新正規化。 | blocked | zero、near-zero、heterogeneous target classes、single-guide 與 heavy-tail simulations 均達 coverage gate；高 sampling variance 必須單調增加 shrinkage；D-study 僅對可識別且非負的分量輸出，曲線必須單調。 |
> | B-008 | B | P1 | **selection、贏家詛咒、atlas-wide 與 stage-wise/selective FDR 尚未形成單一檢定樹。** | **直接：**E05 建議以「至少一 guide 顯著」的 genes 算 agreement；E11 確認存在 `guide_correlation_signif`；E21 改要求 target-blind universe、atlas-wide 後 stage-wise error control，但未指定 screening null、families、weights 或 selective procedure。 | top-target ranking、gene-wise discoveries、condition contrasts、pathway claims | 凍結 expression/QC-only gene universe與所有權重。先定義 atlas omnibus family，再定義 target screen 與 selected target 內的 gene/condition family；使用事先指定的 stage-wise 或 selective-FDR 方法。Per-target BH 僅 exploratory。Ranking CI 與 validation 必須由 guide cross-fit或獨立 holdout 估計。 | blocked | 全域 null、稀疏 alternative、效果導向 missingness 與 top-k selection simulations通過 FDR、false-sign及 held-out calibration gates；完整 family tree 與 adjusted p-value來源可重現。 |
> | B-009 | B | P1 | **CAMERA 與 ROAST/FRY 雖已分開命名，兩種 null、輸入與 multiplicity 契約仍不完整。** | **直接：**E20–E21 要求 Hallmark primary、CAMERA competitive、ROAST/FRY self-contained，但未固定 gene-set release、ID mapping 結果、contrast、rotation unit、重疊 pathway 家族或兩層結果的允許措辭。 | pathway secondary interpretation | CAMERA 明列 competitive null：「set 內 genes 不比 set 外更相關」；ROAST/FRY 明列 self-contained null：「set 內無整體效應」。兩者使用相同 target-blind universe與預先指定 contrast，但分開 FDR family與報告，不合併 p-values。Rotation 必須沿獨立 pseudobulk/block 單位，不得旋轉 genes。 | blocked | 合成情境至少包含「全 transcriptome 同幅位移」與「僅 pathway-specific 位移」：前者可使 self-contained 顯著但 competitive 不顯著；後者才容許兩者同時有力。若兩方法被解讀為同一假設則驗證失敗。 |
> | B-010 | B | P1 | **`additional-evidence`：無法證明 external validation 不洩漏，且目前只有 K562 transportability 的可用敘述。** | **直接：**E05 擬用 validation outcomes 校準 domain weights 與 threshold，並同時宣稱預測 independent replication；E08 說 Th1Th2 table 不可得、K562-only 且 partial；K562 與任何 T-cell validation records 均未列入 E01–E21。E21 只規定 nested holdout 原則。 | reliability→replication、外部驗證、threshold tuning | 新 manifest 封存 validation data、target overlap、批次、donor、endpoint與 checksum。任何調參、method selection 或 threshold calibration 只能使用 tuning targets；untouched validation 以 target 為分割單位，樣本不足時使用 nested cross-validation 並放棄「獨立」措辭。 | blocked | Frozen split hash 證明同一 target 不跨 tuning/test；報告有效樣本數與 CI。K562 只能標 cross-cell-type transportability；獨立 T-cell perturbation 才能標 same-cell-type replication；arrayed assay與 biological relevance 分開。 |
> | B-011 | B | P2 | **44.6 GB joint pseudobulk 與 1.6 TB fallback 沒有候選別的 benchmark gate。** | **直接：**E02／E03 記錄約 44.57 GB pseudobulk 與約 1.6 TB cell-level fallback；E09 顯示既有 16.79、29.42、16.87 GB H5 products。E02 只規定 backed/chunked 及禁止全域 target² matrix，沒有可驗收 budget。 | pipeline feasibility、候選方法公平比較、cell-level fallback | 三候選均以相同 1% 與 10% shard benchmark；只准 backed sparse I/O、block sufficient statistics、low-rank covariance或線上 kernel aggregation。禁止 densify、`p×p` covariance及 `n_target²` matrix。Cell-level rebuild 維持條件式 fallback。 | blocked | 固定硬體後，peak RSS `<70%` 可用 RAM、scratch `<2×` input、1%→10% scaling exponent `≤1.2`，且 full-run extrapolation落在預先登錄 wall-clock budget；中斷可續跑且 checksum一致。 |
> 
> ## 5. 候選 profile 方法：失效模式與暴露情境
> 
> **本 pass 不選 winner。**候選方法只能依預先登錄的 synthetic loss function 排序；不得用 K562 或其他 external validation 表現事後挑選。
> 
> | 候選 | 可合理支持的詮釋 | 主要失效模式 | 能暴露失效的 synthetic scenario | 必要通過條件 |
> |---|---|---|---|---|
> | **(i) precision-weighted multivariate linear decomposition** | 在 full-rank、Euclidean/Hilbert response、已知或一致估計 measurement covariance 下，可用 trace 建立 additive components | `p≫n` covariance 奇異；只用 diagonal precision 會重複計算相關 genes；共享 NTC covariance 遺漏；heavy tails／稀疏 outliers 破壞估計；完整 interactions 在 E12-like layout 不可識別 | 18k genes 由 20 個 latent factors 驅動，加上共享 NTC、t3 tails、guide-specific scale、E12 run layout、MNAR missing cells | component bias、coverage、type-I 均過 gate；low-rank approximation 改變不造成 component reversal；rank gate逐 target通過 |
> | **(ii) kernel/distance-based restricted permutation** | 若 kernel PSD 且交換群有效，可支持 RKHS location attribution與受限制檢定；未經證明不等於 classical variance components | 非 Euclidean distance產生負 eigenvalues；PERMANOVA 混淆中心位置與離散度；不平衡資料產生順序依賴；有效 permutation 太少；高維 distance concentration | 真正 centroid完全相同但 guide群離散度不同；另加入 `1−CCC` indefinite Gram、single-guide、run confounding與缺格 | PSD/eigen gate、PERMDISP、marginal partition與 null calibration全數通過；若只偵測 dispersion，不得回報 location component |
> | **(iii) robust hierarchical functional modelling** | 可聯合處理 heavy tails、measurement error、target shrinkage及 functional covariance，並輸出完整不確定性 | 2 guides／4 donors下 prior主導；target population多峰時 exchangeability失敗；basis truncation漏掉稀疏 pathway signal；MCMC/VI coverage不準；計算成本最高 | target分為 dense-factor、sparse-pathway與null三類；t3 errors、outliers、single-guide、弱 KD、E12 confounding與 informative missingness | 分層 prior sensitivity、simulation-based calibration、held-out predictive calibration及 compute gate通過；不得以 posterior平滑掩蓋 rank deficiency |
> 
> CCC 與 Pearson 只保留作 agreement diagnostics。若要升格為 factorial decomposition，必須另提供可加總性、identifiability、measurement-error correction與 synthetic recovery 的形式或實證證明。
> 
> ## 6. Secondary-layer audit
> 
> ### Gene-wise two-stage effect-plus-covariance
> 
> 可接受的最低契約是：
> 
> 1. **第一階段：**在 donor×condition×run block 內，以 NB quasi-likelihood 或 voom/limma 對 targeting 與 matched NTC counts 建模，產生每個 target×guide×donor×condition×outcome-gene 的 effect、直接 condition contrast 及 covariance。
> 2. **Covariance：**至少包含共享 NTC、同 pseudobulk normalization、跨 condition donor，以及 outcome-gene correlation。若無法保存完整矩陣，low-rank/block approximation 必須由 synthetic coverage 證明足夠。
> 3. **第二階段：**把第一階段 effect 視為帶已知估計誤差的 response，而非原始觀測；guide nested within target；跨 target／outcome gene partial pooling 的 linking assumptions需預先登錄。
> 4. **Dependability：**使用預先權重的 summed signal／summed error；禁止平均逐 gene reliability ratios。
> 5. **Multiplicity：**先 atlas-wide omnibus，再對被選 targets 做 stage-wise/selective FDR；「一個 condition 顯著、另一個不顯著」不得取代直接 contrast。
> 
> 現行 bundle 未提供完成此契約的 covariance 或 actual joint grid，因此狀態仍是 `design-specified`。
> 
> ### Pathway CAMERA 與 ROAST/FRY
> 
> - **CAMERA：**競爭型 secondary hypothesis；比較 gene set 與背景 universe，須估計 inter-gene correlation。
> - **ROAST／FRY：**自足型 secondary hypothesis；檢定 gene set 內是否有整體方向性效應。
> - Hallmark release、gene ID mapping、重複 ID、方向、contrast、universe及重疊 pathway處理必須凍結。
> - 兩者不得被描述為同一 null 的「互相驗證」，也不得把同一 CD4 資料所得 pathway結果稱為 independent validation。
> 
> ## 7. 必須預先凍結的 falsification gates
> 
> 以下是本 reviewer 建議的**最低定量門檻**；必須在查看真實 target 結果前凍結。若團隊採不同數值，需先給出理由並留存版本，不能結果出來後調整。
> 
> | Gate | 最低要求 |
> |---|---|
> | Monte Carlo 規模 | 每個 global-null scenario 至少 5,000 replicates；每個 non-null／adversarial scenario 至少 2,000 |
> | Type-I error | 在 `α=0.05` 時 point estimate介於 `0.04–0.06`，且 95% Monte Carlo binomial interval包含 `0.05` |
> | FDR／false-sign rate | 目標 `q=0.05` 時 point estimate `≤0.06`，95% Monte Carlo upper bound `≤0.07` |
> | 95% interval coverage | 整體及預先指定的 support、guide-count、effect-size strata均介於 `0.93–0.97` |
> | Component recovery | 真實 share `≥0.05` 時 absolute bias `≤0.02`、RMSE `≤0.05`；真實 zero component 的 median estimate `≤0.01` 並通過 type-I gate |
> | 贏家詛咒 | held-out top-decile effects 的 calibration slope介於 `0.9–1.1`；不得使用 training effect重新定義 top decile |
> | D-study | 每條已報告 point curve隨 guides或donors增加皆不得下降；投影 coverage同樣達 `0.93–0.97` |
> | 候選分歧 | 任兩候選 central share差異 `>0.05` 或超過兩倍 combined Monte Carlo SE 時，強制輸出 disagreement diagnosis，不得挑較漂亮結果 |
> | Compute | 1% 與10% pilot符合 B-011；任何 densification、全 `p×p` covariance或 target² matrix立即 fail |
> 
> 合成資料至少需交叉涵蓋：global null、已知 additive components、zero/boundary components、latent-factor與block-correlated genes、heavy tails、zero inflation、低 counts、弱 KD、1–4 guides、4 donors、single-guide、E12 run layout、shared NTC、缺格、MNAR viability loss及 significance-based feature selection。
> 
> ## 8. 必做 controls 與不洩漏 validation
> 
> - **NTC-vs-NTC：**在每個 donor×condition×run 內，把 NTC cells／guides分成互斥 pseudo-target與 reference pools，匹配 targeting 的 cell-count與library-size分布，執行完整 pipeline。不得讓同一 NTC observation同時出現在兩側。
> 
> - **Guide cross-fit：**兩 guide targets以 guide A 做 feature selection、tuning與hyperparameter estimation，guide B只做評估，再交換；3–4 guide targets做預先固定 folds。Single-guide targets保留於最終輸出，但不能當 cross-fit成功證據。
> 
> - **Leave-one-donor-out：**進行四次完整 refit，每次連 shrinkage hyperparameters 都只用其餘三 donor估計。報告 component shift、rank shift、hit-call flip與CI，不得把四 donor敏感度外推為人口 generalizability。
> 
> - **Common-support sensitivity：**以 R2 中具有三條件的 CE0008678、CE0006864 作固定 sensitivity population。差異容許界線應在 target分析前由 NTC-vs-NTC distance分布凍結；超過界線即標 run/support-sensitive。
> 
> - **External evidence taxonomy：**
>   - 獨立 T-cell perturbation、獨立 targets／批次：`same-cell-type replication`
>   - T-cell arrayed bulk／flow 且 endpoint不同：`assay translation`
>   - K562：`cross-cell-type transportability`
>   - pathway、疾病關聯或文獻：`biological relevance`
>   - 同一 CD4 dataset 的 gene/pathway分析：`internal sensitivity/interpretation`
> 
> 任何資料一旦參與 metric、prior、threshold、gene universe或候選方法選擇，就屬 tuning data；只有 target-level隔離且從未參與上述步驟的部分可稱 untouched validation。
> 
> ## 9. Final verdict
> 
> # `blocked`
> 
> 理由：
> 
> 1. B-001、B-002、B-003 為未解除的 P0：actual joint grid/rank缺席、non-Euclidean component詮釋未成立、run與 donor×condition interactions仍不可分。
> 2. B-004 至 B-010 的 P1 會直接改變 type-I error、coverage、FDR、target shrinkage、pathway措辭與 validation claim。
> 3. synthetic recovery、NTC controls、guide cross-fit、leave-one-donor-out及 common-support sensitivity均尚未執行。
> 4. 三種 profile candidates 都有可被目前設計觸發的失效模式；目前沒有證據支持提前指定 winner。
> 5. 解除 additional-evidence findings 必須建立新版 manifest並重跑受影響 blind pass，不能把新證據併入本次 `EB-2026-07-10-v1.1` 後沿用 Pass B 結論。

### 15.9 A／B integration notes

A與B沒有對同一實證問題作相反判決：兩者都判定actual joint object、first-stage covariance、simulation、replicate與external evidence尚未通過。下列四個表面張力已在normative chapters明確收斂，Pass C仍須逐項檢查：

| Conflict ID | A-side／B-side tension | Reconciliation | Verification |
|---|---|---|---|
| `AB-C01` | A-007要求future-guide universe有獨立證據；B的whole-guide cross-fit可被誤讀成future-guide驗證 | §4／§12把cross-fit限於observed-guide prediction；`E-GUIDE-UNIVERSE`仍not-identifiable | schema與wording test不得把cross-fit升為future-guide sampling claim |
| `AB-C02` | A-005固定C3 domain；B的component／D-study語彙可能被讀為random condition variance | §4／§9只允許fixed contrasts與weights；禁止condition-count projection | 搜尋random `σ²_C`／新增condition generalization不得出現在normative contract |
| `AB-C03` | A-011判定無replicate floor；B要求D-study與component recovery | §10 floor=`null`；§9 D-study只對已識別、有sampling population的facet | no-lane fixture必須輸出兩個floor reason codes |
| `AB-C04` | B-009 proposed correction把CAMERA null寫成「set內genes不比set外更相關」，混入correlation nuisance | §4／§8改為「差異訊號不比固定背景更強」；inter-gene correlation只作校正 | pathway schema分開competitive effect null與correlation estimate |

### 15.10 Integrated finding ledger before Pass C

本表不是把未執行的empirical gate文字化消除。`resolved`只表示原本的contract／wording缺口已由可檢查章節修正；需要actual data、simulation、benchmark或external table的finding仍為`blocked`。Pass C可將任何row退回`blocked`，不能在沒有證據時升級。

| ID | pass | severity | finding | evidence | affected claim | proposed correction | disposition | verification |
|---|---|---|---|---|---|---|---|---|
| A-001 | A | P1 | 缺實例化estimand registry | A-001；E05／E20 | 全部variance、rank、hit | 以唯一ID固定object、support、weights、threshold與wording | resolved | §4 registry逐一連到§6–§8 estimator；ID-change rule存在 |
| A-002 | A | P0 | Actual joint pseudobulk不在bundle | A-002；E11／E03 | joint profile decomposition | 取得hash-fixed object並跑schema／grid／rank | blocked | 新manifest＋§5 gates全部通過並重跑受影響blind pass |
| A-003 | A | P1 | Fixed rank不足以保證component rank／kernel additivity | A-003；E16 | component shares與method selection | candidate-specific basis／Jacobian／PSD／term-order gates | blocked | Actual support與§11 recovery都通過；目前僅design-specified |
| A-004 | A | P1 | Run與donor×condition alias；R2改變estimand | A-004；E12 | condition、donor、run claims | D4 observed-run與D2_R2分ID；不估independent run | resolved | §4 IDs、§5 crosswalk、§12 common support與metadata IDs一致 |
| A-005 | A | P1 | Fixed C3被寫成random condition variance／projection | A-005；E05 | condition share與D-study | C3固定weights與direct contrasts；禁止新condition外推 | resolved | §4、§9與§16均移除random-condition claim |
| A-006 | A | P1 | Matched NTC與shared-control covariance未操作化 | A-006；E11／E16 | uncertainty、shrinkage、CI | count-level effect＋joint covariance＋bootstrap | blocked | `covariance_manifest.json`與§11 coverage／NTC gates通過 |
| A-007 | A | P1 | Observed guides不足以推future-guide universe | A-007；E13 | guide reliability／D-study | 限定observed-guide wording；future universe保留null | resolved | §4／§5／§12明列`E-GUIDE-UNIVERSE` not-identifiable |
| A-008 | A | P1 | Single-guide fallback混入共同ranking | A-008；E08／E17 | target dependability | single-guide分partial tier且guide estimate=null | resolved | §4、§10與§13 ranking invariant禁止跨tier |
| A-009 | A | P1 | Profile gene universe可能循環選擇 | A-009；E05／E16 | profile reliability／ranking | 固定target-blind `G_profile`並cross-fit learned basis | resolved | §4／§6與`TARGET_BLIND_UNIVERSE_VIOLATION` test |
| A-010 | A | P1 | KD只有guide×condition，不能作donor/run校正 | A-010；E14 | KD-normalized effects | raw intent-to-treat primary；KD只作另ID sensitivity | resolved | §4 claim boundary與§11 weak／zero-KD scenario；不得有donor-specific KD欄 |
| A-011 | A | P1 | 無identical-spec replicate，floor不可識別 | A-011；E11／E12 | replication floor | lane分支；無lane時nullable floor與combined residual | blocked | 現況`floor=null`；只有新manifest lane gates通過才解除 |
| A-012 | A | P1 | Actual K562／T-cell validation values缺席 | A-012；E08／E11 | replication／transport | 固定tables、join、endpoint與target-level split | blocked | 新manifest、split hash、no-leakage與CI gates通過 |
| A-013 | A | P2 | KD artifact無法clean-room重建 | A-013；E09／E10／E14 | provenance／KD sensitivity | 固定companion commit/path並更新fetch／codebook | blocked | 空raw目錄重建E14 SHA-256一致 |
| B-001 | B | P0 | Actual joint grid／NTC／rank未驗證 | B-001；E11／E03 | 所有joint outputs | schema與support audit fail closed | blocked | 同A-002；`input_schema_audit`與`design_support` checksums |
| B-002 | B | P0 | Non-Euclidean distance未證明等同additive variance | B-002；E16 | profile shares | 移除`1−CCC` primary；linear PSD／RKHS分名，PERMDISP與PSD gates | resolved | §6不再宣稱equivalence；RKHS仍須empirical gate才可輸出 |
| B-003 | B | P0 | Run、donor×condition與common support不可同時分離 | B-003；E12 | run／condition／D4 claims | 不估independent run；D4與D2_R2分開 | resolved | §5 rank consequence與§12 sensitivity；actual targets仍受B-001阻擋 |
| B-004 | B | P1 | Restricted permutation沒有exchange groups | B-004；E12／E13 | kernel p-values／nulls | 逐null固定whole-unit moves、strata與fail branch | resolved | §9 exchange registry＋permutation-resolution schema |
| B-005 | B | P1 | First-stage covariance遺漏shared NTC | B-005；E11／E14 | profile／gene CI | effect-plus-covariance與validated low-rank operator | blocked | 同A-006；analytic對bootstrap與coverage通過 |
| B-006 | B | P1 | 高維gene dependence契約缺席 | B-006；E09／E11 | metric、kernel、functional model | target-blind regularized operator、effective rank與approximation gates | resolved | §6／§7／§11有trace、Frobenius、coverage與distance scenarios |
| B-007 | B | P1 | Sparse facets下shrinkage／negative components未校準 | B-007；E12／E13／E16 | target dependability／D-study | direct＋bounded robust model；保留unconstrained值與boundary bootstrap | blocked | §11 zero／mixture／coverage／monotonic shrinkage gates實際通過 |
| B-008 | B | P1 | Selection、winner's curse與FDR tree未定 | B-008；E05／E11 | ranking／gene claims | target-blind universe、兩棵OFDR tree與held-out ranking | resolved | §7 tree、§11 held-out calibration與§13 family lineage |
| B-009 | B | P1 | CAMERA／ROAST-FRY null與families不完整 | B-009；E20／E21 | pathway interpretation | pinned release／mapping；competitive signal null與self-contained null分開 | resolved | §8 method×library families、no p-value merge及mapping gates |
| B-010 | B | P1 | External validation資料缺席且有leakage風險 | B-010；E05／E08 | replication／transport | target-level untouched split與evidence taxonomy | blocked | 同A-012；actual split hash、join、endpoint與calibration |
| B-011 | B | P2 | 44.6 GB／1.6 TB沒有benchmark budget | B-011；E02／E03／E09 | operability | 同shard 1%／10% benchmark、RSS／scratch／scaling／resume gates | blocked | `candidate_benchmark.parquet`實際通過§11 thresholds |

## 16. Crosswalk of exact downstream changes

本章只描述後續`spectra-ingest`如何更新#8與相關文件，不直接修改`openspec/changes/generalizability-decomposition/`。Owner核准前，#8已完成tasks保留為歷史紀錄，統計核心維持暫停；ingest不得把本文件的`design-specified`誤寫成已實證結果。

### 16.1 Project documentation與data contract

| File | Action | Existing item | Exact downstream change | Verification |
|---|---|---|---|---|
| `README.md` | replace | 完整decomposition／validation若被寫成可直接交付 | 改為joint pseudobulk gate後才可產生profile primary；gene/pathway為secondary；目前外部與floor可nullable | README claims逐一連回estimand/status |
| `README.md` | add | 缺方法狀態入口 | 連到本文件與#8，顯示`blocked`／ingest狀態及marginal comparator邊界 | link check＋status與docs一致 |
| `docs/design.md` | keep | profile作主要科學object、target-specific view與謹慎用語 | 保留高層問題與D4/C3背景 | 不與§4 registry衝突 |
| `docs/design.md` | replace | `1−CCC` distance primary、Gaussian comparator、Fay–Herriot來源、donor split-half primary | 改成§6三候選hard-gate selection、count-level shared-NTC covariance、calibrated shrinkage與joint D4 panel | candidate IDs與output IDs一致 |
| `docs/design.md` | remove | DE-hit gene subset、random condition／guide universe暗示、donor fallback共同ranking、事後截負值、assumption-free floor | 刪除或標historical superseded；CCC／Pearson只留diagnostic | wording／invariant tests |
| `docs/design.md` | add | estimand、rank、exchange、missingness、validation taxonomy與no-winner branch | 引用本文件§4–§12，加入machine-readable degradation | 每個claim有ID／gate／wording |
| `docs/README.md` | add-now | 缺本audit文件入口 | 在本change加入「blocked — #8 statistical core paused」連結；owner ingest後更新狀態而非刪除歷史 | local link存在 |
| `analysis/data/README.md` | replace | h5ad／h5mu facet mapping可被讀為core input | joint merged pseudobulk列minimum primary input；h5mu列marginal cross-check | product-to-claim matrix無joint誤用 |
| `analysis/data/README.md` | add | 大型／lane／external artifact狀態不清 | 記錄44.6 GB object、optional cell-level fallback、lane availability unknown、validation table status與checksum流程 | clean download／status audit |
| `analysis/data/DATA_AND_ASSUMPTIONS.md` | replace | guide／donor split、condition／run與floor假設 | guide nested within target、D4 finite panel、C3 fixed、E12 run alias、no-lane floor=null | assumption IDs對§5／§10 |
| `analysis/data/CODEBOOK.json` | replace | E14仍列未下載，joint／marginal capability未明 | 修正KD product provenance；每artifact新增grain、claim capability、download state、checksum與schema version | JSON schema＋E14 clean-room hash |
| `analysis/data/fetch_data.sh` | add | 未取得joint object與E14不可重建 | 加explicit opt-in／resume／checksum的joint pseudobulk target及immutable KD source；大型檔不在預設small download偷偷啟動 | dry-run、resume與checksum test |
| `analysis/data/raw/data_sharing_readme.md` | keep-external | upstream schema說明 | 不改upstream artifact；在repo data docs寫本地interpretation與hash | raw checksum不變 |

### 16.2 `generalizability-decomposition/proposal.md`

| Action | Existing content | Ingested change | Verification |
|---|---|---|---|
| keep | profile層是headline、scalar ranking是次層、用語不宣稱distribution-free | 保留研究目標與non-goal | proposal headline對§1 |
| replace | h5ad＋兩個h5mu足以完整分解；distance／FH／donor split已鎖定；floor必交 | joint pseudobulk為最低輸入；三候選待gate；target shrinkage待covariance／recovery；floor conditional | 每個replacement連到§5／§6／§10 |
| remove | guide pair／donor halves形成identical-spec floor；邊際summary可完成joint G-study | 明確刪除這兩個資料與claim捷徑 | 搜尋不得把guide／donor halves稱replicate |
| add | identifiability、matched NTC、fixed C3、D4、run alias、validation taxonomy缺口 | 加四狀態、no-winner、additional-data與failure policy | proposal與new spec requirements對應 |

### 16.3 `generalizability-decomposition/design.md`

| Action | Existing content | Ingested change | Verification |
|---|---|---|---|
| keep | design-level與target-level區分、K562缺失時誠實降級、用語節制 | 保留為架構原則 | crosswalk標出仍有效decisions |
| replace | `1−CCC` primary與Gaussian scalar baseline | §6 `M-LIN`／`M-KERN`／`M-FUNC`同estimand比較；CCC／Pearson diagnostic | PSD、PERMDISP、basis-rank、selection rule可定位 |
| replace | permutation／within-target dispersion作FH sampling variance | §7／§9 count-level matched-NTC covariance與direct-estimate shrinkage | shared-control covariance test |
| replace | donor只能split-half、condition random-style components | joint D4 finite-panel與C3 fixed contrasts；D2_R2另ID | 不出現human-population或new-condition claim |
| replace | input／floor／negative component implementation contract | pseudobulk primary、marginal cross-check、nullable floor、unconstrained＋constrained values | schemas接受null＋reasons |
| remove | donor fallback補single-guide並混共同`R_dep`；post-hoc truncation／renormalization | single-guide partial tier；完整boundary estimator | invariant fixtures |
| add | candidate-specific rank、exchange registry、first-stage covariance、target-blind universes、FDR trees、benchmark與no-winner | 以§5–§14作design decisions | A/B finding IDs逐項映射 |

### 16.4 `generalizability-decomposition/specs/generalizability-decomposition/spec.md`

| Action | Existing requirement／scenario | Ingested requirement | Verification |
|---|---|---|---|
| keep | static export與缺criterion時不捏造 | 延伸為nullable＋lineage export | demo fixture可renderblocked row |
| replace | marginal files即可產生完整nonnegative shares | joint schema／NTC／component-rank hard gate；只輸出可識別quantity | h5mu-only=`marginal-only` fixture |
| replace | guide pair／donor split作floor | §10 lane available／unavailable branches | no-lane=`null`＋兩reason codes |
| replace | distance primary | estimator不可在formal＋synthetic gate前鎖定；RKHS與Hilbert claims分開 | three-candidate/no-winner scenarios |
| replace | Fay–Herriot與donor fallback強制 | direct covariance、robust bounded link、cross-fit、prior sensitivity與single-guide null | shrinkage／single-guide fixtures |
| replace | donor只可split-half | joint D4 panel primary；split-half僅marginal comparator | joint／marginal outputs分schema |
| remove | 靜默補零、截負值、跨tier排名、無actual replicate仍需floor | 對應行為改成hard fail／nullable | negative scenarios全部有code |
| add | registry、rank、run support、target-blind genes、two-stage gene/FDR、pinned pathways、falsification、no leakage、benchmark | 每項至少一個positive與negative scenario | `spectra analyze`無coverage warning |

### 16.5 `generalizability-decomposition/tasks.md`

| Action | Existing tasks | Ingested change | Verification |
|---|---|---|---|
| keep-history | 已完成1.1、1.2、6.1、6.2 | 保留checkbox與原意，1.2註記`historical; superseded by joint-input task` | 不改寫完成歷史 |
| replace | pending 2.1–2.3依h5mu／distance執行 | joint acquisition／schema／rank；matched NTC＋covariance；三候選simulation／benchmark／selection；profile fit | 每task有artifact與gate |
| replace | pending 3.1–3.3 donor split／固定FH | joint D4 panel、calibrated shrinkage、single-guide partial tier | 不再fallback混ranking |
| replace | 4.1 independent replication wording | K562=`cross-cell-type transportability`；T-cell／assay各自data gate | endpoint taxonomy＋split hash |
| replace | 5.1預設floor scalar存在 | demo schema接受nullable floor、status與reason codes | no-lane fixture可render |
| remove | 任何要求在identifiability／simulation前跑headline model的依賴順序 | 改為§14 gate DAG | dependency audit |
| add | environment lock、joint audit、simulation、NTC、guide cross-fit、LODO、R2、gene、pathway、marginal cross-check、1%／10% benchmark、schema validation | 逐module拆成可獨立驗收tasks | 每task一個owner、output、command、threshold |

### 16.6 Proposed ingest sequence and boundary

1. Owner先審閱本文件與Pass C；若仍`blocked`，只可修訂本change，不得啟動#8 analysis。
2. 核准後以`spectra-ingest`把§16.2–§16.5轉成#8 proposal／design／spec／tasks；保留completed history與新base commit。
3. 同一ingest更新§16.1的project/data docs tasks，但大型下載與code implementation仍留在#8 apply，不在#9執行。
4. 先跑`git diff -- openspec/changes/generalizability-decomposition`確認本#9 apply期間為空；ingest後則以新的reviewed diff為準。
5. #8依§14.1順序執行；每次method或data scope改變都更新manifest並重跑受影響simulation／review，不沿用舊approval。

Ingest完成的definition of done是：#8四個artifacts與project/data docs均能逐項回指本文件的estimand、gate、status、reason code與verification；沒有任何task把未下載、未驗證或不可識別的quantity寫成已承諾數值。

### 16.7 Follow-on empirical resolution programme（`resolve-methodology-blockers`, #10）

依`CLAUDE.md`的paper-grade標準，本文件的`blocked`**不是可交付的最終狀態**——它觸發一個follow-on empirical change：**`resolve-methodology-blockers`**（OpenSpec change，capability `methodology-resolution`，Refs #9／#10）。該change是解除B-001…B-011的唯一合法路徑：下載真實~44.6 GB joint pseudobulk並凍結新evidence manifest → fail-closed可識別性實測 → 三候選pre-registered synthetic recovery（滿足全部凍結§7 gates與§8 controls）→ 只由synthetic loss選定primary method → 產出本§16 crosswalk的實測gate結果。

| Crosswalk 行 | 對象 | 狀態 |
|---|---|---|
| **follow-on resolution** | `openspec/changes/resolve-methodology-blockers/`（`methodology-resolution`）| 解除 P0/P1 的必經 change；通過全部 §7 gates 前，#8 統計核心維持 paused |

該follow-on **supersede 本 audit change（`audit-complete-methodology`）的 data／simulation Non-Goals**：audit 明訂「不下載大型資料、不跑完整模型、不做 synthetic recovery」，這些在 follow-on 內反轉為**必做**工作。唯有 follow-on 的 gate 逐項通過（或誠實回報 `not_identifiable`），本文件才可由 `blocked` 轉 `approved`、#8 統計核心才可恢復。
