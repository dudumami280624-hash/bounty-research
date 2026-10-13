# 孩子靶场训练入口（离线第一阶段）

此入口是**本地教学问答和人工验收准备**，不是完整的 Solidity 执行靶场；不要求钱包、不访问真实合约、不收集孩子个人信息。

## 开始
需要 Python 3.9+。下载仓库后在根目录运行：

```bash
python student_lab.py --list
python student_lab.py --lesson reentrancy-01
```

在自己的电脑上新建 `answer.txt`，用中文回答问题，然后运行：

```bash
python student_lab.py --lesson reentrancy-01 --answer-file answer.txt --output progress.json
python -m unittest -v test_student_lab
```

`progress.json` 仅写在本地，**不要上传孩子的个人资料或答案到公开仓库**。反馈状态为 `review_required`，不是自动通过；需要结合实验复现、修复和回归证据人工验收。

## 后续真实执行靶场
Ethernaut: https://ethernaut.openzeppelin.com/
Damn Vulnerable DeFi: https://github.com/theredguild/damn-vulnerable-defi

以上是公开教学靶场；尚未为孩子配置个人账户或隔离 EVM 运行环境。接入真正的代码执行训练前，必须验证本地隔离环境、题目运行与成绩回传。
