# AI Child — WorkBuddy + Skill 协同升级（试验性）

本方案是**增强现有系统，不替换 Qwen/llama.cpp、Foundry、知识库和 GitHub 工作流**。

## 来源与边界

- WorkBuddy Skill Atlas: https://github.com/sandbaseai/workbuddy-skill — 公开的第三方索引；**不自动安装任何 Skill**。
- 腾讯朱雀 Skill Scanner 示例: https://github.com/infometa/workbuddyskills/blob/main/skills/skill-scanner/SKILL.md — 借鉴其静态检查与供应链审查思路；本仓库的初步扫描器**并非**朱雀 A.I.G 引擎，不能视作完整安全审计。
- 腾讯 WorkBuddy 的 Skill 机制提供设计参考；这不意味着已安装或运行 WorkBuddy。

## 已新增

- `student_skill_registry.py`：有限白名单调度两个现有教学能力，拒绝任意外部命令和未知 Skill。
- `python student_skill_registry.py --list`：列出可运行的本地技能。
- `python student_skill_registry.py --scan path/to/SKILL.md`：对文本进行离线静态**预筛**，生成带 SHA256 的记录，始终禁止自动授权执行。
- `python student_skill_registry.py --skill solidity-repair --lesson reentrancy-01 --model /tmp/child-model.gguf --output child-evidence/independent-patch.json`：在已有隔离教学靶场上执行本地推理及 Foundry 测试（需要真实模型和 forge）。
- `python -m unittest -v test_student_skill_registry`：运行路由器回归测试。

## 不得混淆的验收门槛

1. 静态预筛通过 **≠** 第三方 Skill 安全。
2. 找到 Skill 索引 **≠** 已安装 21,000 个 Skill。
3. 模型真正调用、生成候选合约、Foundry 运行和测试通过分别记录；不得虚构。
4. 教学靶场通过 **≠** 真实未知漏洞或奖金平台认可。
5. 执行外部授权目标前，必须有单独确认的合法范围；此路由器不提供任意网络扫描或外部命令执行。
