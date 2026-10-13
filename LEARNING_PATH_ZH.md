# 学习路线｜知识库优先，靶场其次

目标：理解原理、能解释漏洞、在**本地或明确授权**的环境复现、修复并回归测试。**不涉及真实目标探测、资金操作或赏金提交。**

## 第 1 单元：重入漏洞（入门）
- 知识：EVM 外部调用、状态变更、Checks-Effects-Interactions（CEI）、重入锁。
- 阅读：[Solidity Security Considerations](https://docs.soliditylang.org/en/latest/security-considerations.html#reentrancy)；[OpenZeppelin ReentrancyGuard](https://docs.openzeppelin.com/contracts/5.x/api/utils#ReentrancyGuard)。
- 靶场：[Ethernaut Reentrance](https://ethernaut.openzeppelin.com/)；先在本地复现，不使用真实资产。
- 实验步骤：阅读脆弱合约 → 画出外部调用与状态更新顺序 → 在隔离测试中触发重复提款 → 改为先更新状态再外部调用 → 重跑同一测试。
- 学生提交：根因说明、失败测试、修复差异、修复后测试日志、是否存在误报及原因。

## 第 2 单元：访问控制
- 知识：onlyOwner、角色权限、初始化、升级权限。
- 阅读：[OpenZeppelin Access Control](https://docs.openzeppelin.com/contracts/5.x/access-control)。
- 靶场：Ethernaut 的 Ownership / Delegation 等教学关卡。
- 学生提交：权限矩阵、未授权操作的失败测试、修复后回归。

## 第 3 单元：整数精度与奖励分配
- 知识：整数除法截断、先乘后除、边界值、奖励不变量。
- 靶场：本地构造奖励分配合约，覆盖 0、1、最大值和时间边界。
- 学生提交：不变量、最小反例、修复前后差异。

## 验收规则
1. 仅看扫描器提示不算通过；必须用自己的话解释根因。
2. 每题保留**修复前可复现、修复后不可复现**的证据。
3. 盲测题不得直接重复已练习样本；记录 TP/FP/TN/FN。
4. 记录学习时间、提示次数与独立完成比例；不能用 CI 绿色代替学习能力。
5. 每单元需完成知识问答、实验、修复、回归四项，全部完成才进入下一单元。

## 当前自动化边界
- `.github/workflows/monthly-knowledge.yml`：每天两次收集公开安全资料。
- `.github/workflows/major-knowledge-update.yml`：每月 30 日（2 月最后一天）知识更新。
- `.github/workflows/real-scanner-blind-lab.yml`：真实扫描器的样本识别评估；**不等于学生独立完成**。
- 未来衔接 Immunefi 需要单独审核授权范围、平台资格和家长同意；不属于当前学习验收。
