# 全球投资与量化项目接入清单

## Agent / AI 研究层

- TradingAgents — 多智能体研究、基本面、情绪、技术、交易和风险讨论框架。
- daily_stock_analysis — 每日股票分析与定时报告类项目；具体仓库需锁定准确来源后再接入。
- ai-hedge-fund — 多角色投研/投资委员会类框架；只用于研究和模拟。
- Vibe-Trading — 自然语言生成策略、回测和交易代理；MIT，需审查依赖和执行权限。

## 数据与交易基础设施

- CCXT — 加密货币交易所统一 API；可接行情和模拟环境，真实下单必须单独授权。
- Freqtrade — 加密货币策略、回测、模拟盘和实盘框架；默认隔离在 paper trading。
- Qlib — 微软开源量化研究平台，偏数据、因子、模型和回测。
- vn.py — 国内量化交易框架，偏行情、策略、回测和券商/交易接口。
- FinceptTerminal — 金融终端和市场研究工具，需单独核对数据源和许可。

## 当前接入策略

1. The Market Mind 只调用研究层，不自动连接券商或自动下单。
2. 先把这些项目的研究方法吸收进 external-investment-research-adapter。
3. 数据层按需接入 FRED、SEC、BLS、CBOE、交易所和公开行情源。
4. 回测必须保存数据时间范围、手续费、滑点、样本外结果和失败记录。
5. Freqtrade、CCXT、vn.py 真实交易功能保持关闭；只允许研究、回测和模拟盘。
6. 任何声称“收益更高”的项目都必须独立复核，不能把 GitHub README 或回测截图当作真实盈利证明。

## 初步优先级

A. TradingAgents + Vibe-Trading：吸收多智能体研究和自然语言策略结构。
B. Qlib + Freqtrade：分别用于股票量化研究和加密策略回测。
C. CCXT + vn.py：作为数据/执行适配层，暂不启用真实下单。
D. FinceptTerminal + daily_stock_analysis + ai-hedge-fund：核对准确仓库、许可、依赖和数据来源后再接入。
