# 新增投资工具与验证层

## 已核对项目

- Vibe-Trading：个人交易代理，支持自然语言策略、回测和多智能体研究。MIT。
- Kronos：金融 K 线基础模型，用于价格/波动率序列预测和合成数据；模型研究，不等于可靠交易信号。
- OpenBB：金融数据与研究终端/工具链，适合作为数据检索和分析入口。
- Freqtrade：加密货币策略、回测、模拟盘和实盘框架；本项目保持实盘关闭。
- daily-stock-analysis：每日股票分析和定时报告类项目；待锁定准确仓库后再复制源码。
- TDD triage：名称不明确，可能指测试驱动开发的故障分流，也可能是某个投资项目；未找到足够证据，不擅自安装。

## 放置位置

- 研究与数据：external-investment-research-adapter
- 预测模型：market-history-validation / Kronos 研究记录
- 回测：Freqtrade/Qlib 隔离环境
- 写作：market-psychology-western-writing
- 审问：grill-with-docs

## 强制验证

Kronos、Vibe-Trading 或任何模型输出必须经过滚动样本外测试，与随机游走、买入并持有和简单基准比较；不把 README、论文回测或短周期演示当作实盘盈利证据。

OpenBB、Freqtrade、CCXT、vn.py 等可能需要数据源、交易所或账户权限；当前只登记接入，不启用真实下单。

来源：
- https://github.com/HKUDS/Vibe-Trading
- https://github.com/shiyu-coder/Kronos
- https://github.com/OpenBB-finance/OpenBB
- https://github.com/freqtrade/freqtrade
