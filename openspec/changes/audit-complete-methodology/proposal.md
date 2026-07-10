## Why

現有完整 generalizability decomposition 計畫在確認 joint observation design、可識別性與真正 replication 結構前，已先鎖定邊際 h5mu、`1 − CCC`、Fay–Herriot 與 replication floor。Issue #9 要求以 GPT-5.6 Sol 做可稽核的多輪紅隊審查，先把 profile-level 主方法與 gene-wise／pathway-level 敏感度分析寫成無重大漏洞的 durable methodology spec，再恢復 #8 的統計實作。

## What Changes

- 新增一套可重現的 GPT-5.6 Sol 方法審查流程：三個隔離 pass、固定模型識別、保存 prompt／設定／findings，並以 P0/P1 resolution gate 控制是否可核准。
- 新增完整方法升級文件，明確列出 claim→data→estimand crosswalk、資料需求、可識別性、profile-level 主模型、gene/pathway 敏感度、推論、模擬、驗證、降級規則與後續檔案修正表。
- 把 joint pseudobulk 設為完整方法的最低資料單位；邊際 `by_guide.h5mu`／`by_donors.h5mu` 僅作比較與降級輸出。
- 要求 guide nested within target、condition fixed domain、4-donor panel scope、matched NTC、run confounding 與缺格設計都進入明確契約。
- 只有 identical-spec replicate 存在時才允許估計 replication floor；否則必須回報 `not_identifiable`，並合併不可拆的最高階 interaction 與 sampling residual。
- **BREAKING**：在本審查文件核准並產出 #8 ingest crosswalk 前，`generalizability-decomposition` 的 2.x／3.x／4.1／5.x 統計核心不得繼續套用原 h5mu-only 契約。
- Pass B 已回傳 **blocked**（3 P0 + 7 P1；`docs/reviews/sol-pass-b-adversarial-statistical-review.md`）。依 `CLAUDE.md` 的 paper-grade 標準，`blocked` **不是終態**：所有 P0/P1 必須經一個 follow-on empirical programme（下載 joint pseudobulk + 凍結新 manifest + 三候選 synthetic recovery + 全部 §8 controls，通過全部 §7 gates）解除，方法才能宣告 primary。§7 gates 與 §8 controls 在本 change 內 pin 成 machine-checkable unblock-conditions。

## Non-Goals

- 不在此 change 下載大型資料、執行完整模型、產生排名或 demo。（本 change 仍是純審查；但依 paper-grade 標準，這些是 follow-on resolution change 的**必做**工作，非可省略——見 design 「Paper-grade resolution is mandatory」決策。）
- 不在此 change 直接改寫 #8 的 OpenSpec artifacts；先產出可審查 crosswalk，核准後再 ingest。
- 不以方法複雜度代替證據完整度；資料不可識別的 quantity 必須降級、改名或列為 blocked。

## Capabilities

### New Capabilities

- `methodology-audit`: 以可重現的 GPT-5.6 Sol 紅隊審查建立完整雙層方法規格，並以資料可識別性、模擬校準與 P0/P1 resolution gate 決定能否交付 #8。

### Modified Capabilities

(none)

## Impact

- Affected specs: `methodology-audit`
- Affected code:
  - New: `docs/complete-methodology-review-and-upgrade-plan.md`
  - Modified: `docs/README.md`
  - Removed: (none)
- Downstream coordination:
  - `openspec/changes/generalizability-decomposition/` 在本 change 核准後依 crosswalk ingest，不由本 change 直接修改。
  - GitHub issues #2、#3、#5、#7、#8 依核准後的 claim boundary 重新對齊。
