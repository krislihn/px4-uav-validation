# 环境基线 Environment Baseline

记录日期: 2026-10-14 (北京时间)
记录人: liuqiang

## 宿主环境
- 宿主系统: Windows
- 虚拟机软件: Oracle VirtualBox
- 虚拟机名称: PX4-Ubuntu (主机名 px4-server)
- 虚拟磁盘文件: D:\VirtualBoxVM\PX4-Ubuntu.vdi (24.3 GB)

## 客户机 Ubuntu
- 发行版: Ubuntu 22.04.5 LTS (jammy)
- 内核: 5.15.0-198-generic
- 时区: 初始为 Etc/UTC, 2026-10-14 改为 Asia/Shanghai
- Python: 3.10.12

## 项目组件
- PX4 源码路径: /home/liuqiang/PX4-Autopilot
- PX4 版本: v1.18.0-beta1-1012-gf16f99d4b5 (main 分支开发版, commit f16f99d4b5)
- 仿真器: Gazebo Sim 8.15.0 (Harmonic 代)
- MAVSDK-Python: 1.4.8
- QGroundControl (Windows 端): 5.1.4

## 连接方式
- SSH: ssh liuqiang@127.0.0.1 -p 2222 (VirtualBox NAT 端口转发 2222 -> 22)
- Windows 快捷方式: C:\Users\Administrator\Desktop\PX4-Ubuntu终端.bat

## 已知问题
- 剪贴板共享与拖放均为 disabled, 未安装增强功能 (SSH 方式不受影响)
- PX4 为 main 分支开发版, 随意 git pull 会破坏可复现性
- flight_results.csv 中 lat_err/lon_err 单位为度, alt_err 单位为米, 且 alt_err 约 10 m 可疑, 待核对生成脚本
