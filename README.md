# 赏金猎人｜Bounty Research

**正式执行计划与验收标准：** [PLAN.md](PLAN.md)（**最终验收：2026-10-12，今天**；不得延期）。

**当前系统：** 免费 GitHub Actions + Slither + Foundry/forge-std + 官方公开赏金候选目录；HackerOne 仅只读状态连接。定时触发每小时一次属于 GitHub 的尽力调度，不能保证 24/7 不间断执行。

**真实成果口径：** 扫描警报不是漏洞；模拟 PoC 通过不是可报告的生产漏洞；草稿不是已提交报告；奖金须有官方确认。参见 [状态](status/audit_status.json) 与 [GitHub Actions](../../actions)。

**直接查看：**
- [正式执行计划（六阶段、期限、验收及防死循环规则）](PLAN.md)
- [机器运行状态（含六阶段验收）](status/audit_status.json)
- [六阶段 PASS/FAIL 生成器](acceptance.py)
- [审计工作流](.github/workflows/audit.yml)
- [奖励范围记录](scope_horizen.json)

**硬约束：** 仅授权范围内的源码及本地隔离测试；不新增付费服务；报告实际提交需要用户对该份报告明确授权；不能保证找到漏洞或获得奖金。
