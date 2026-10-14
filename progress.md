# PX4 无人机自主飞行与自动化测试平台 · 进度记录

> 用法:每完成一个最小任务就更新一次。新开对话(手机/电脑)时,先粘贴《开场提示词》,再把这个文件的内容发过去,不依赖聊天记忆。
> 规则:没有真实证据的东西一律不写进"已验收"。计划中的功能不写成已完成。

## 1. 当前状态

- 当前阶段:阶段 0(环境与架构)收尾中;阶段 1、2 已有历史雏形,待验证
- 当前任务编号:T-004 已完成
- 上次验收结果:通过(环境基线入档,提交 05e80ee / 39500bd / 7d5046c)
- 今天日期:2026-10-14
- 下次唯一目标:重跑航点任务并连续记录高度,验证 docs/known_issues.md 1.1 的高度口径问题

## 2. 环境快照(改过任何版本就更新)

| 项目 | 版本/值 | 怎么确认的 |
| --- | --- | --- |
| 宿主系统 | Windows | 系统信息 |
| 虚拟机 | VirtualBox / PX4-Ubuntu(主机名 px4-server)/ Ubuntu 22.04.5 LTS | VBoxManage list vms, lsb_release -a |
| 内核 | 5.15.0-198-generic | uname -r |
| 时区 | Asia/Shanghai(2026-10-14 前为 Etc/UTC) | timedatectl |
| PX4 | v1.18.0-beta1-1012-gf16f99d4b5(main 分支开发版) | git describe --tags |
| 仿真器 | Gazebo Sim 8.15.0(Harmonic 代) | gz sim --versions |
| QGroundControl | 5.1.4(Windows 端) | 可执行文件版本信息 |
| Python | 3.10.12 | python3 -V |
| mavsdk | 1.4.8 | python3 -m pip show mavsdk |

## 3. 已验收成果(必须能指到证据)

| 内容 | 证据路径/命令 | 通过标准 | 状态 |
| --- | --- | --- | --- |
| 项目目录与 Git 仓库建立 | 提交 05e80ee | 四个子目录存在,git 仓库初始化完成 | 通过 |
| 环境基线记录 | docs/environment.md | 版本、路径、确认方式齐全 | 通过 |
| 已知问题清单 | docs/known_issues.md | 每条问题有现象、推断、验证方法 | 通过 |
| 历史脚本与数据归档 | scripts/、logs/、提交 7d5046c | 家目录散落文件复制入项目并记录来源 | 通过 |
| PX4 SITL + Gazebo 启动 | 尚未在项目内留证 | 模型随物理运动,无持续报错 | 未做 |
| QGC 遥测持续刷新 | 尚未留证 | 数据持续更新 | 未做 |
| MAVSDK 连续读取遥测 | scripts/connection_check.py | 连续采样且数值合理(现为一次性读取) | 部分 |

## 4. 卡住的问题 / 未解决

- 主要未解决问题见 docs/known_issues.md 1.1:航点任务的 alt_err 口径可疑,三个航点的
  alt_err 都约等于 10 m,反推当时相对高度约为 0 m,怀疑 goto_location 的绝对高度参数
  被当作相对高度使用。
- 其他脚本缺陷(固定 sleep 无超时、单点采样、结果覆盖写)见 docs/known_issues.md 1.2 - 1.4。

## 5. 本次生成的证据文件

- 文档:docs/environment.md、docs/known_issues.md、progress.md
- 归档数据:logs/2026-10-13_flight_results.csv(2026-10-13 一次运行,当时虚拟机时区为 UTC)
- 归档代码:scripts/connection_check.py、scripts/waypoint_mission.py
- 参考方案:docs/reference/PX4_UAV_Autonomous_Flight_Automated_Testing_Final_Plan.pdf
- Git 提交:05e80ee、39500bd、7d5046c

## 6. 我能不能讲清楚(每阶段自查,不通过就停下重来)

- [ ] 能用中文不看资料讲 3 分钟:这个组件是干什么的、数据怎么流的、为什么这么设计
- [ ] 能用英文讲 1 分钟同一件事(可看稿,但要说出口)
- [ ] 能故意弄坏一个地方(改错端口/关掉一个进程)并说清现象和修法

## 7. 下次的唯一任务

在仿真运行的前提下重跑航点任务,同时连续记录 relative_altitude_m 与绝对高度,
回答两个问题:(1) 起飞后相对高度是否真的上升到 10 m?(2) goto_location 的高度参数
是绝对高度还是相对高度?结论写回 docs/known_issues.md 的 1.1。

## 8. 我要问 ChatGPT 的问题(攒着一起问)

-

## 9. 英语练习记录(每天 15 分钟)

- 今天练的句子/术语:____
- 录了一遍音,自己能听懂吗:____
