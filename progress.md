# PX4 无人机自主飞行与自动化测试平台 · 进度记录

> 用法:每完成一个最小任务就更新一次。新开对话(手机/电脑)时,先粘贴《开场提示词》,
> 再把这个文件的内容发过去,不依赖聊天记忆。
> 规则:没有真实证据的东西一律不写进"已验收"。计划中的功能不写成已完成。

## 1. 当前状态

- 当前阶段:阶段 0、1、2 已完成;阶段 4 分析已补强;阶段 3、5 进入收尾
- 当前任务编号:P2 已完成(P95 与条件对比)
- 上次验收结果:通过(分析脚本生成汇总表与两张新图)
- 今天日期:2026-10-30
- 下次唯一目标:P3 测试增强(日志完整性用例与 ERROR 级判定)

## 2. 环境快照(改过任何版本就更新)

| 项目 | 版本/值 | 怎么确认的 |
| --- | --- | --- |
| 宿主系统 | Windows | 系统信息 |
| 虚拟机 | VirtualBox / PX4-Ubuntu(主机名 px4-server)/ Ubuntu 22.04.5 LTS | VBoxManage list vms, lsb_release -a |
| 内核 | 5.15.0-198-generic | uname -r |
| 时区 | Asia/Shanghai(2026-10-14 前为 Etc/UTC) | timedatectl |
| PX4 | v1.18.0-beta1-1012-gf16f99d4b5(main 分支开发版) | git describe --tags |
| 仿真器 | Gazebo Sim 8.15.0(Harmonic 代) | gz sim --version |
| QGroundControl | 5.1.4(Windows 端) | 可执行文件版本信息 |
| Python | 3.10.12 | python3 -V |
| mavsdk | 1.4.8 | python3 -m pip show mavsdk |
| SITL home 海拔 | 约 488.27 m(默认 home 47.39797, 8.54616) | telemetry.position().absolute_altitude_m |

## 3. 已验收成果(必须能指到证据)

| 内容 | 证据路径/命令 | 通过标准 | 状态 |
| --- | --- | --- | --- |
| 项目目录与 Git 仓库建立 | 提交 05e80ee | 四个子目录存在,git 仓库初始化完成 | 通过 |
| 环境基线记录 | docs/environment.md | 版本、路径、确认方式齐全 | 通过 |
| 已知问题清单 | docs/known_issues.md | 每条问题有现象、推断、验证方法 | 通过 |
| 历史脚本与数据归档 | scripts/、logs/、提交 7d5046c | 家目录散落文件复制入项目并记录来源 | 通过 |
| PX4 SITL + Gazebo 启动 | logs/test_runs/2026-10-18_mission_run.txt | 出现 Ready for takeoff,任务可执行 | 通过 |
| 高度口径问题定位 | logs/test_runs/2026-10-16_alt_probe.csv | 连续曲线证明 home 海拔 488.27 m,命令"10"被当成海拔 | 通过 |
| 航点任务高度修复 | 提交 b268643; flight_results.csv | goto_location 改为 home_abs + 相对高度 | 通过 |
| 航点任务三次全流程复现 | flight_results.csv; 2026-10-18 运行输出 | 3 次自动起飞-3 航点-返航-降落;高度误差 0.00–0.11 m | 通过 |
| 架构图与数据流 | docs/architecture.png, docs/architecture.md | 能讲清四层分工与端口 | 通过 |
| 首次真实飞行遥测 | logs/test_runs/2026-10-24_first_flight.csv | 59 条; rel_alt 最大 2.47 m(t=12.27); 模式 TAKEOFF/LAND/HOLD | 通过 |
| 固定采样与时间戳命名 | logs/test_runs/2026-10-25_171220_telemetry.csv | 60 条; 间隔 min=max=1.000 s | 通过 |
| 姿态与解锁状态遥测 | logs/test_runs/2026-10-28_223349_telemetry.csv | 120 条、13 字段; 59 条 armed=True、61 条 armed=False; 最大相对高度 2.515 m; 姿态角有实际变化 | 通过 |
| 升级后定频采样验证 | logs/test_runs/2026-10-29_145433_telemetry.csv | 5 条; 相邻时间间隔全部为 1.000 s; 新增字段齐全 | 通过 |
| 测试套件首跑 | logs/test_runs/2026-10-25_172913_suite.csv | 7 条用例全部 PASS; 悬停 2.10-2.61 m, 漂移 0.08 m | 通过 |
| 失败检测验证 | logs/test_runs/2026-10-25_183238_suite.csv | 状态污染导致 5/7, 套件正确判 FAIL | 通过 |
| 干净环境复跑 | logs/test_runs/2026-10-25_183459_suite.csv | 7/7 PASS | 通过 |
| 测试套件连续 3 轮 | logs/test_runs/2026-10-25_1926*_suite.csv 等 3 份 | 3×7/7 PASS; 悬停 2.38-2.47 m, 漂移 <=0.07 m; 航点 h_err <=0.93 m | 通过 |
| 数据分析脚本与首版图表 | analysis/analyze_logs.py、summary.csv、figures/ | 有效遥测 5 份、264 条; 高度/速度/漂移图 | 通过 |
| P95 与飞行阶段对比 | analysis/summary.csv、phase_summary.csv、figures/phase_comparison.png | 每份数据含高度/漂移/速度 P95; 按地面悬停、空中悬停、起飞、降落分组 | 通过 |
| 测试条件对比 | analysis/suite_summary.csv、suite_condition_summary.csv、figures/condition_comparison.png | 正常 42/42; 悬停窗口异常 18/21; 状态污染 5/7; 不完整运行不计入通过率图 | 通过 |
| 阶段 5 交付 | README.md、docs/technical_report.md、docs/summary_en.md、docs/data_dictionary.md、analysis/PX4_项目数据与图表.pdf | 文档齐全, 可由 README 复现核心流程 | 通过 |
| QGC 遥测持续刷新 | 2026-10-13 QGC tlog(27753 帧, sysid=1 autopilot=PX4) | 数据持续更新 | 通过(今日未复测) |

## 4. 已解决 / 未解决

已解决:
- 1.1 高度口径:确认 goto_location 第三参数是绝对高度(AMSL)。SITL home 海拔 488.27 m,
  指令写 10 等于要求"降到地下",机体因此落地。证据与修复见 docs/known_issues.md 1.1。

未解决(见 docs/known_issues.md):
- 1.2 所有等待都是固定 sleep,没有状态验证与超时。
- 1.3 每个航点只采样一次。
- 1.4 结果覆盖写:建议输出到 logs/test_runs/ 并按日期编号。
- 1.5 lat_err / lon_err 单位是度,不是米,报告里不得当作米。

## 5. 本次生成的证据文件

- 文档:docs/environment.md、docs/known_issues.md、progress.md
- 归档数据:logs/2026-10-13_flight_results.csv(2026-10-13 一次运行,当时虚拟机时区为 UTC)
- 实验数据:logs/test_runs/2026-10-16_alt_probe.csv(高度-时间曲线)
- 运行输出:logs/test_runs/2026-10-18_mission_run.txt(2026-10-18 完整终端输出)
- 运行结果:flight_results.csv(最近一次运行的三航点误差)
- 归档代码:scripts/connection_check.py、scripts/waypoint_mission.py、scripts/alt_probe.py
- 架构:docs/architecture.png、docs/architecture.md(生成脚本 scripts/draw_architecture.py)
- 飞行遥测:logs/test_runs/2026-10-24_first_flight.csv(59 条, 60 秒)
- 定频遥测:logs/test_runs/2026-10-25_171220_telemetry.csv(60 条, 1.000 s 间隔)
- P1 姿态/解锁飞行遥测:logs/test_runs/2026-10-28_223349_telemetry.csv(120 条, 13 字段)
- P1 定频采样短测:logs/test_runs/2026-10-29_145433_telemetry.csv(5 条, 间隔 1.000 s)
- P2 汇总:analysis/summary.csv、analysis/phase_summary.csv
- P2 条件对比:analysis/suite_summary.csv、analysis/suite_condition_summary.csv
- P2 图表:analysis/figures/phase_comparison.png、analysis/figures/condition_comparison.png
- 测试套件:scripts/run_test_suite.py、docs/test_cases.csv、logs/test_runs/2026-10-25_172913_suite.csv
- 测试套件复跑:logs/test_runs/2026-10-25_183238_suite.csv(5/7)、2026-10-25_183459_suite.csv(7/7)
- 三轮复跑:logs/test_runs/2026-10-25_192618_suite.csv、192709、192800
- 分析:analysis/analyze_logs.py、summary.csv、suite_summary.csv、figures/altitude_curve.png、figures/flight_kinematics.png
- 交付文档:README.md、docs/technical_report.md、docs/summary_en.md、docs/data_dictionary.md
- 参考方案:docs/reference/PX4_UAV_Autonomous_Flight_Automated_Testing_Final_Plan.pdf
- Git 提交:05e80ee、39500bd、7d5046c、9120940、b268643、aa32776、ada0881、bdfe14f

## 6. 我能不能讲清楚(每阶段自查,不通过就停下重来)

- [ ] 能用中文不看资料讲 3 分钟:这个组件是干什么的、数据怎么流的、为什么这么设计
- [ ] 能用英文讲 1 分钟同一件事(可看稿,但要说出口)
- [ ] 能故意弄坏一个地方(改错端口/关掉一个进程)并说清现象和修法

## 7. 下次的唯一任务

P3:给测试套件补日志完整性用例,并把异常级别区分为 ERROR 与 WARN。

## 8. 我要问 ChatGPT 的问题(攒着一起问)

-

## 9. 英语练习记录(每天 15 分钟)

- 今天练的句子/术语:____
- 录了一遍音,自己能听懂吗:____
