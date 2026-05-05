# FTL_STG

一个基于《FTL 回合制电子桌游版最小可玩规则文档 v0.2》的 Python 命令行战斗原型。

## 环境
- Python 3.11+

## 运行
```bash
python -m src.main
```

## 测试
```bash
python -m pytest -q
```

## 项目结构
- `src/models.py`：核心数据模型（房间、格子、船员、建筑、舰船）
- `src/game_state.py`：游戏状态与初始配置
- `src/actions.py`：行动数据结构
- `src/resolver.py`：回合执行与规则结算
- `src/enemy_ai.py`：敌方预告与简单 AI
- `src/cli_view.py`：命令行显示与玩家输入
- `src/main.py`：主循环入口
- `tests/test_combat.py`：核心规则单元测试
