# Actions 查询修正

2026-11-24：研究分支过滤查询返回0条，但仓库级查询确认教材提取工作流在 main 触发。不得将研究分支无运行记录解释为停机。

- 查询仓库级 `/actions/runs`，按工作流名称筛选，再通过 integration/actions-run-locator.json 对齐实际 run ID；核对 `/actions/runs/{id}/jobs`。
- 已核实 45373770237、45372453416、45370776714 均 completed/success，head_branch=main。45373770237 的实际提取、视觉扫描、OCR回归、研究索引及元数据提交步骤均成功。
- 这仅修正运行核验口径，不代表新增教材OCR或语义验收。继续按26份蜡烛图优先及逐页断点推进，不重复已成功页面。
