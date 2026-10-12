# 赏金猎人｜HANDOFF

> 用途：任何新的 ChatGPT / GPT / 新对话接管本项目时，**先读本文件，再读机器状态**。  
> 本文件不是成果证明；真实状态始终以 GitHub Actions、状态 JSON、官方平台回执为准。

## 1. 项目目标

在**零新增付费、授权范围内、可重复运行**的前提下，构建漏洞赏金研究闭环：

1. 官方开放赏金目标核验
2. 源码自动分析
3. 真实目标漏洞验证
4. 有效漏洞报告生成
5. 用户授权后提交并取得官方回执
6. 官方报告状态与奖金追踪

**严禁：**
- 把扫描警报当真实漏洞
- 把模拟 PoC 当真实生产漏洞
- 把绿色 GitHub Actions 当业务完成
- 把草稿当已提交报告
- 把 API 连通当官方报告/奖金
- 为了“6/6”伪造漏洞、提交、回执或奖金

## 2. 仓库

- GitHub 私有仓库：`dudumami280624-hash/bounty-research`
- 主分支：`main`
- 正式计划：`PLAN.md`
- 最新机器状态：`status/audit_status.json`
- 工作流：`.github/workflows/audit.yml`
- 验收程序：`acceptance.py`
- 当前主要目标：Horizen / Immunefi
- 固定源码：`HorizenOfficial/staker`
- 固定 commit：`ab92502e9da98784dfe3bd3ef933d4e9345ff628`

## 3. 最新真实状态

截至机器状态时间：

- workflow run：**38237157117**
- workflow SHA：`53e65a910e856165be898becba95cfe340c39943`
- 状态时间：`2026-10-12T10:37:18.316737+00:00`
- 六阶段：**2/6 PASS**
- 真实漏洞：**0**
- 实际提交：**0**
- 官方确认奖金：**USD 0**

### 六阶段

| 阶段 | 状态 | 当前证据 / 阻塞 |
| --- | --- | --- |
| 1. 官方开放赏金目标核验 | PASS | Horizen / Immunefi 官方范围、现金赏金、提交入口已核验 |
| 2. 源码自动分析 | PASS | 固定源码已获取，Slither 分析成功 |
| 3. 真实目标漏洞验证 | FAIL | 尚无真实可复现漏洞与独立影响证据 |
| 4. 有效漏洞报告生成 | FAIL | 没有真实已验证漏洞，因此没有正式可提交报告 |
| 5. 经授权提交与官方回执 | FAIL | 没有可提交报告；实际提交 0；必须对具体报告取得用户授权 |
| 6. 官方状态与奖金追踪 | FAIL | HackerOne 只读状态同步已跑通但报告数为 0；当前目标实际平台是 Immunefi，尚无真实报告/奖金记录 |

## 4. 已验证的技术能力

### 官方范围核验
- `official_scope_status.json`
- 当前 `verified_count = 1`
- Horizen 官方 scope 已核验
- **仅允许本地/隔离研究，不将其解释为允许生产攻击**

### 静态分析
- Solidity 文件：76
- Slither alerts：12
- High：2
- Medium：10
- **12 条全部仍是 leads，不是已验证漏洞**

### Foundry 模拟 PoC
- `specific_poc_results.json`
- 6/6 通过
- `conditional_simulation_only = true`
- `real_world_exploit_verified = false`
- 不能作为真实漏洞提交

### 真实部署状态只读分叉验证
- `deployment_fork_results.json`
- execution：passed
- 5/5 测试通过
- `real_deployment_state_checked = true`
- `real_world_exploit_verified = false`
- `any_public_chain_transaction_broadcast = false`
- 当前 5 项实际结论：
  - 官方合约有运行时代码
  - stake/reward token 关系已核对
  - 未知账户不能通知 reward
  - reward window 不能提前绕过
  - 实际 token principal 未通过 withdraw 路径被窃取
- 这些结果更偏向**排除风险**，不是漏洞证明

### 前端范围
- `frontend_scope_results.json`
- repo：`HorizenOfficial/staker-services`
- pinned commit：`a404746a693adca207c8c31f3e21fc3762fbb7b8`
- install / typecheck / lint / test：全部通过
- 已验证安全漏洞：0
- 可提交报告：0

### 报告生成器
- `build_verified_reports.py`
- 已将“生成报告”和“用户批准提交”解耦
- 只有真实验证证据齐全时才生成正式报告
- 模拟 PoC、缺失证据、错误源码版本、危险 finding ID 均会被拒绝

### 端到端安全夹具
- `test_business_pipeline.py`
- 已证明：验证 → 报告 → 授权门禁 → 官方状态解析，可以在隔离 fixture 中串通
- fixture 绝不能计入真实业务验收

### HackerOne
- `status/hackerone_connection.json`
- API：connected = true
- HTTP 200
- `status/hackerone_reports.json`
- 只读报告状态同步：success
- reports_seen：0
- coverage：complete
- payouts_verified_usd：0
- **注意：当前 Horizen 目标属于 Immunefi，不要把 HackerOne 连通当作当前目标的提交闭环**

## 5. 当前 12 条 leads

不要重新陷入“12 条警报循环”。

- `df03bce1714d` arbitrary-send-erc20 — scope not established
- `be1c1609e7b5` uninitialized-state — inherited impact must be proven
- `12ec614578dc` divide-before-multiply — direct in-scope；已有 finding-specific arithmetic property，仍未证明漏洞
- `1429588799f6` reentrancy-no-eth — direct in-scope
- `8e48c2a2804a` reentrancy-no-eth — direct in-scope；sandbox test 不是 finding-specific real proof
- `20f0b85eac0b` divide-before-multiply — inherited
- `98fdd9e27146` divide-before-multiply — inherited
- `00f846e1adf2` erc20-interface — scope not established
- `b241ec50cd2c` incorrect-equality — inherited
- `016430194a14` reentrancy-no-eth — scope not established
- `d51386d2891a` reentrancy-no-eth — inherited
- `9d74cbad990c` unused-return — inherited

**调度原则：**
- 同一疑点没有新增证据，不要重复扫描冒充进度
- 两轮无新增证据应标记 blocked 并切目标
- 优先真实部署条件、真实 token 行为、真实影响
- 不成立就排除，不要强行证明

## 6. 当前真正的技术阻塞

### 阶段 3：真实漏洞验证
要通过，必须至少有 1 个：
- 与当前官方 scope 对齐
- 对固定 source/deployment 可复现
- 有 finding-specific PoC
- 有控制组
- 有实际安全影响
- 非已知问题 / 非重复问题
- 不依赖纯模拟恶意 token 条件
- 不需要对生产环境广播攻击交易

当前最大事实：
- RewardAccumulator 回调重入只在模拟恶意 token 下成立
- 真实 ZEN token 尚未证明具备该回调条件
- 实际部署分叉 5 项检查目前没有发现可利用影响

### 阶段 4：正式报告
只有阶段 3 真通过后：
- `build_verified_reports.py` 才应输出 `verified_reports_generated > 0`
- 报告必须包含：版本、组件、影响、复现步骤、证据、预期/实际结果、修复建议

### 阶段 5：授权提交
- **必须由用户对具体真实报告明确批准**
- 不能把“用户说开始项目”当每份报告的自动提交授权
- 需要官方 report ID / receipt 才算 PASS
- 当前实际提交：0

### 阶段 6：官方状态/奖金
- 必须基于真实 report ID
- 区分：submitted / triaged / accepted / bounty approved / paid
- 奖金不能从报告状态推断
- 只有官方奖励证据或付款证据才能计入金额

## 7. Immunefi 接管注意事项

用户已确认：
- Immunefi 账户正常可用
- 不需要 Codex Security 插件
- 不要让用户提供密码或验证码

浏览器自动化曾创建 profile：
- 名称：`Immunefi bounty reporting`

但是：
- 远程登录窗口对用户很卡
- 不应把远程浏览器登录作为主阻塞
- 用户可在本机浏览器正常登录
- 最终实际提交前，应先准备好完整真实报告，再让用户完成必要登录/授权动作

## 8. 新 GPT 接管后立即执行

**不要先写长篇总结。先执行。**

1. 读取：
   - `HANDOFF.md`
   - `PLAN.md`
   - `status/audit_status.json`
   - `status/hackerone_reports.json`
   - 最新 GitHub Actions
2. 检查最新 workflow run 是否晚于本文件记录
3. 若有新状态，以机器状态覆盖本文件中的数字
4. 不重复跑无变化的 12 条 Slither leads
5. 优先解决阶段 3：
   - 深挖直接 in-scope 的真实部署行为
   - 验证真实 ZEN token / notifier / access-control / accounting / reward schedule 条件
   - 使用 Foundry fork 只读/本地状态，不广播生产攻击交易
   - 不成立则排除并切换官方授权新目标
6. 一旦出现真实 verified vulnerability：
   - 生成正式报告
   - 检查 known issues / duplicate risk
   - 向用户展示完整报告和证据
   - **取得该份报告明确提交授权后**才执行官方提交
7. 提交后：
   - 保存官方 report ID / receipt
   - 启用只读状态跟踪
   - 奖金只按官方记录计入

## 9. 对用户的沟通要求

用户不想看：
- PPT 式长篇解释
- 重复状态表
- 扫描次数炫耀
- “工作流绿色所以成功”
- 一直围绕同一批 12 条警报打转
- 没有结果的延期

用户要的是：
- 实际修复
- 可运行
- 可复现
- 有证据
- 有真实漏洞时能形成报告并提交
- 没有漏洞时快速排除并切换，不死循环

回复应：
- 先做再说
- 简短
- 只报告新增、可验证结果
- 不保证一定找到漏洞或拿到奖金
- 不伪造通过

## 10. 新对话第一条推荐指令

复制下面这段给新的 GPT：

```
继续我的“赏金猎人”项目。
GitHub 私有仓库：dudumami280624-hash/bounty-research

先读取 HANDOFF.md、PLAN.md、status/audit_status.json、status/hackerone_reports.json，并检查最新 GitHub Actions。
不要重新解释项目历史，直接执行。

目标：完成六阶段真实业务闭环。
当前以机器状态为准，不允许把模拟 PoC、扫描警报、绿色工作流或 fixture 当真实成果。
不要重复陷入现有 12 条 Slither leads 的死循环；没有新增证据就排除/轮换目标。
优先解决阶段 3 真实漏洞验证；真实漏洞成立后才进入报告、授权提交和官方状态/奖金追踪。
任何实际提交都必须先取得我对该份具体报告的明确授权。
不增加付费服务，不攻击未授权生产环境，不伪造回执或奖金。
```

---

**最后更新依据：** `status/audit_status.json` workflow run **38237157117**。  
若仓库已有更新运行，新的 GPT 必须以最新机器状态覆盖本文件。
