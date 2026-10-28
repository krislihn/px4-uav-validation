# 项目交接文档（给任何 AI）

> 用途：新对话、换模型或 API 断线后，把本文件全文粘贴给 AI，即可立即接上项目。
> 最后更新：2026-10-28

## 1. 项目是什么

PX4 无人机自主飞行与自动化测试平台。基于 PX4 SITL + Gazebo，用 MAVSDK-Python
执行自主起飞/悬停/航点/降落，按 1.000 s 定频记录遥测，并用自动判定的测试套件验证结果。

仓库：https://github.com/krislihn/px4-uav-validation （main 分支）
作者：krislihn（大二，目标外企/外派岗位）

## 2. 当前进度

| 阶段 | 状态 |
| --- | --- |
| 0 环境与架构 | 完成（版本记录、架构图、数据流） |
| 1 遥测采集 | 完成（定频 1.000 s，9 字段，时间戳命名） |
| 2 自主飞行 | 完成（起飞/悬停/航点/降落） |
| 3 自动化测试 | 完成（7 用例 × 连续 3 轮 = 21/21） |
| 4 数据分析 | 完成（summary.csv、suite_summary.csv、两张图） |
| 5 项目包装 | 进行中（README/技术报告/英文摘要/两份 PDF 已完成；演示视频未录） |

## 3. 关键数字（真实数据）

- 测试用例：7 项 × 3 轮 = 21 次判定，21/21 PASS
- 悬停高度：2.38–2.47 m（目标 2.5 m），水平漂移 ≤ 0.07 m
- 航点水平误差：0.92–0.93 m；高度误差 ≤ 0.08 m
- 定频采样：1.000 s（min = max）
- 遥测样本：199 条 / 4 份文件；单次飞行最大高度 2.47 m

## 4. 环境

Ubuntu 22.04.5（VirtualBox，虚拟机 10.0.2.15，宿主在虚拟机里是 10.0.2.2）；
PX4 main v1.18.0-beta1-1012-gf16f99d4b5；Gazebo Sim 8.15.0；QGroundControl 5.1.4；
Python 3.10.12；mavsdk 1.4.8；pandas 2.3.3；numpy 2.2.6。

## 5. 文件地图

- scripts/：connection_check.py、telemetry_logger.py、waypoint_mission.py、run_test_suite.py、alt_probe.py、draw_architecture.py
- analysis/：analyze_logs.py、make_report.py、make_docs_pdf.py、summary.csv、suite_summary.csv、figures/
- docs/：environment.md、architecture.md/png、test_cases.csv、data_dictionary.md、technical_report.md、summary_en.md、known_issues.md
- logs/test_runs/：遥测 CSV、套件结果 CSV 与 log
- progress.md：阶段、验收结果、下一步
- 桌面 zm/：数据摘要 PDF、完整文档 PDF、两张图、备份 zip、录制台本、旁白稿

## 6. 怎么运行

```bash
# 终端 1：启动仿真（需图形桌面时加 DISPLAY=:0）
cd ~/PX4-Autopilot && make px4_sitl gz_x500

# 终端 2：定频遥测
cd ~/px4-uav-validation && python3 -u scripts/telemetry_logger.py

# 终端 2：测试套件
cd ~/px4-uav-validation && python3 -u scripts/run_test_suite.py

# 分析
python3 analysis/analyze_logs.py
python3 analysis/make_report.py
```

规则：同一时间只能运行一个 MAVSDK 程序（都占 UDP 14540）；仿真请在前台运行，
不要 nohup 重定向到文件长期后台跑（会写出 GB 级日志）。

## 7. 未决问题（见 docs/known_issues.md）

1.10 首次连接偶发挂起，需先 pkill -f mavsdk_server 再跑。
1.13 航点水平误差稳定在 0.92–0.93 m，疑为飞控「到位接受半径」，未验证。
1.14 2026-10-25 一份旧遥测有 68 秒采样空档，不可用于统计。
未做：HITL / 真机实验；演示视频。

## 8. 下一步

1. 录制演示视频（台本：桌面 zm/录制台本_边操作边念.md，旁白：zm/旁白_照着念.txt）
2. 验证 1.13 到位半径
3. 遥测补「姿态 + 解锁状态」两个字段；统计补 95 百分位

## 9. 协作规则

一次只安排一个最小任务；先解释再执行；用证据验收；不虚构数字；
代码可用 AI 辅助，但作者必须能解释每一部分。回答尽量通俗，避免大段术语。

## 10. 关键踩坑时间线

- 2026-10-13：QGC 显示已连接却收不到数据 → PX4 GCS 端口 18570 与 VirtualBox 转发错位。
- 2026-10-16：三个航点高度误差都约 10 m → goto_location() 第三参数是绝对高度（AMSL），home 海拔约 488 m。
- 2026-10-24：虚拟机磁盘写满 → /tmp/px4.log 55 分钟涨到 9 GB（后台运行 + pxh 提示符持续写入）。
- 2026-10-25：状态污染导致 5/7、悬停窗口含起飞过渡导致 6/7 → 加前置检查/清理/稳定窗口后连续 3 轮 7/7。
- 2026-10-26：pandas 导入失败 → numpy 2 与系统 numexpr/bottleneck 冲突，移除后解决。
- 2026-10-27：仓库推送到 GitHub；README 加入英文副标题与真实踩坑记录。
- 2026-10-28：OBS 桌面音频绑定失效设备 → 改为默认设备；演示视频准备中（尚未录制）。
