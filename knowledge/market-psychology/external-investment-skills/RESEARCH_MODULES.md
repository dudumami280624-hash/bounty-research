# 投资研究模块扩展

已核对并加入候选模块：

- `tech-earnings-deepdive`：Day1Global-Skills；16 个科技股财报深度分析模块、6 个投资视角、6 类估值方法，并包含偏差控制和 pre-mortem。MIT 许可来源：star23/Day1Global-Skills。
- `longbridge fundamentals`：Longbridge Skills 的基本面和市场数据能力，覆盖美股、港股、A股和新加坡市场；需要 Longbridge 数据连接才可运行实时查询。
- `earnings-analysis`：财报、业绩会、预期差、利润率和管理层表述分析模块。
- `dcf-valuation`：DCF、反向 DCF、WACC、终值敏感性和情景分析模块。
- `diversification`：持仓集中度、相关性、行业重叠、币种暴露和组合风险模块。
- `stockmarket portfolio`：市场环境与投资组合审查模块；未启用自动交易。

## 接入规则

这些模块接入 The Market Mind 的研究层，输出必须标注 DATA / MODEL / HISTORY / PSYCHOLOGY / ADAPTATION / UNVERIFIED。

- Earnings Analysis 先读取财报和业绩会原文，再判断预期差。
- DCF Valuation 必须展示假设、敏感性和 Bull/Base/Bear，不能只给单一目标价。
- Diversification 必须基于真实持仓、仓位、行业和相关性数据；没有持仓数据时只提供模板。
- Longbridge 模块需要连接和权限；当前只登记兼容性，不声称已连接。
- 所有输出仍然服务于 The Market Mind 的双语教育内容，不自动荐股或下单。

来源：
- https://github.com/star23/Day1Global-Skills
- https://github.com/longbridge/skills
- https://github.com/himself65/finance-skills
