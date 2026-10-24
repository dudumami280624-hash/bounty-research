# TDD + Triage 组合层

## Purpose

在仓库内处理代码、数据管线和投资研究自动化的故障时，先分流和定位，再用测试驱动修复。这个组合不用于直接修改投资结论。

## Triage first

1. 判断问题是真实故障、回归、设计行为还是功能请求。
2. 检查重复问题和已有证据。
3. 保留工作树和原始日志，不在定位过程中偷偷修复。
4. 追踪根因、影响范围、严重性和证据置信度。
5. 输出一个可执行的修复简报。

## TDD repair loop

1. RED：先写一个能复现真实错误行为的失败测试。
2. GREEN：写最小改动使测试通过。
3. REFACTOR：在测试持续通过的情况下清理实现。
4. 运行聚焦测试，再运行完整测试套件。
5. 保留失败证据、修复差异、测试命令和结果。

## Investment-project use

适用于：

- PDF 文本转化失败
- 市场数据源中断或字段变化
- 估值计算错误
- 回测数据泄漏
- 样本外验证流程错误
- Skill 读取或路由错误
- GitHub Actions 归档和报告失败

不适用于：

- 用测试通过证明策略盈利
- 用回测结果保证未来收益
- 自动提交交易或修改真实持仓

## Evidence labels

- TRIAGE: 目前对问题的分类和置信度。
- REPRO: 可复现步骤和失败输出。
- TEST: 先行失败测试。
- FIX: 最小修复。
- REGRESSION: 完整测试结果。
- UNKNOWN: 证据不足，不猜根因。

## Reference projects

- addyosmani/agent-skills — test-driven-development
- terminal-skills/triage-issue — TDD-based bug triage

