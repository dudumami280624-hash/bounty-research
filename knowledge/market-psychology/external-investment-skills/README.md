# 外部投资 Skill 接入记录

已接入研究范围：

- `himself65/finance-skills`：Agent Skills 开放规范；市场分析、公司估值、财报、ETF、期权和数据提供器。
- `tradermonty/claude-trading-skills`：技术分析、市场环境、美国市场泡沫检测和交易研究。

来源：
- https://github.com/himself65/finance-skills
- https://github.com/tradermonty/claude-trading-skills

本仓库使用 `.agents/skills/market-psychology-western-writing` 作为主写作层，并用下面的本地适配层吸收外部研究流程：
- `external-investment-research-adapter/SKILL.md`

状态：
- 研究流程已接入。
- 不代表已连接 yfinance、TradingView、FMP、CBOE、券商或付费数据 API。
- 任何当前价格、财报、估值和泡沫评分都必须先取得实时数据并保留来源。
- 外部 Skill 的投资结论只作为研究输入，不自动生成荐股或交易指令。
