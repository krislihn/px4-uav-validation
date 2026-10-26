# PX4 无人机自主飞行与自动化测试平台

基于 **PX4 SITL + Gazebo** 的无人机仿真自主飞行与自动化测试平台：用 MAVSDK-Python 执行自主飞行、记录遥测定频数据，并用一套可重复执行的测试用例验证飞行结果。

## 结果速览（真实数据）

| 指标 | 数值 |
| --- | --- |
| 测试用例 | 7 项 × 连续 3 轮 = 21 次判定，**21/21 PASS** |
| 悬停高度 | 2.38–2.47 m（目标 2.5 m） |
| 悬停水平漂移 | ≤ 0.07 m |
| 航点水平误差 | 0.92–0.93 m |
| 航点高度误差 | ≤ 0.08 m |
| 单次飞行最大高度 | 2.47 m |
| 定频采样间隔 | 1.000 s（min = max） |
| 遥测样本 | 199 条 / 4 份文件 |

数据与图表摘要：[`analysis/PX4_项目数据与图表.pdf`](analysis/PX4_项目数据与图表.pdf)

## 系统架构

![architecture](docs/architecture.png)

- Gazebo：仿真世界、物理与传感器
- PX4 SITL：飞控（状态估计、控制、混控）
- MAVSDK-Python：脚本控制与遥测采集（UDP 14580 ↔ 14540）
- QGroundControl：地面站监控（可选，UDP 14550）

详见 [`docs/architecture.md`](docs/architecture.md)。

## 目录结构

```
scripts/        connection_check.py / telemetry_logger.py / waypoint_mission.py
                run_test_suite.py / alt_probe.py / draw_architecture.py
analysis/       analyze_logs.py / make_report.py / summary.csv / suite_summary.csv
logs/           原始数据与测试运行结果（按日期时间命名）
docs/           environment.md / architecture.md / test_cases.csv
                technical_report.md / summary_en.md / data_dictionary.md / known_issues.md
progress.md     进度记录（阶段、验收结果、下一步）
```

## 环境

Ubuntu 22.04.5、PX4 main `v1.18.0-beta1-1012-gf16f99d4b5`、Gazebo Sim 8.15.0、
QGroundControl 5.1.4、Python 3.10.12、mavsdk 1.4.8。
完整版本与确认方式见 [`docs/environment.md`](docs/environment.md)。

## 快速开始

```bash
# 终端 1：启动仿真（等待出现 pxh>）
cd ~/PX4-Autopilot
make px4_sitl gz_x500

# 终端 2：记录 60 秒遥测
cd ~/px4-uav-validation
python3 -u scripts/telemetry_logger.py

# 终端 2：运行测试套件（约 1 分钟，自动判定 PASS/FAIL）
python3 -u scripts/run_test_suite.py

# 数据分析与图表
python3 analysis/analyze_logs.py
python3 analysis/make_report.py
```

注意：同一时间只能运行一个 MAVSDK 程序（都会占用 UDP 14540）。仿真请在前台运行，
不要用 `nohup ... > /tmp/xxx.log` 长时间后台运行。

## 测试与数据

- 用例定义：[`docs/test_cases.csv`](docs/test_cases.csv)
- 用例说明与技术报告：[`docs/technical_report.md`](docs/technical_report.md)
- 每次运行的判定结果与日志：`logs/test_runs/<时间>_suite.csv` / `.log`
- 遥测字段说明：[`docs/data_dictionary.md`](docs/data_dictionary.md)
- 已知问题：[`docs/known_issues.md`](docs/known_issues.md)

## 已知限制

- 全部结果为 SITL 仿真，未包含 HITL 或真机实验。
- 航点水平误差稳定在约 0.93 m，疑为飞控「到位接受半径」，尚未验证。
- 首次连接偶发挂起，需要先清理残留 `mavsdk_server` 再运行。
- 部分旧采集数据存在采样空档，不可用于统计（已在报告中标注）。

## 开发方式说明

项目方案、测试设计与结论由作者确定并验证；部分代码使用 AI 辅助生成，
每一部分均可在 `docs/technical_report.md` 与 `docs/known_issues.md` 中追溯。
