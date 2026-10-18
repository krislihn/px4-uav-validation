# 系统架构与数据流

![architecture](architecture.png)

## 四个角色

| 组件 | 在哪台机器 | 负责什么 |
| --- | --- | --- |
| Gazebo Sim 8.15 | Ubuntu 虚拟机 | 仿真世界、物理、传感器 |
| PX4 SITL | Ubuntu 虚拟机 | 飞控软件: 状态估计、控制、混控 |
| MAVSDK-Python | Ubuntu 虚拟机 | 我们的脚本: 发指令、读遥测 |
| QGroundControl 5.1.4 | Windows | 地面站: 看地图和状态(可选) |

## 四条链路(均为实测确认)

1. **Gazebo <-> PX4**: gz transport, lockstep。传感器数据从 Gazebo 进入 PX4,电机指令从 PX4 回到 Gazebo。
2. **MAVSDK <-> PX4**: MAVLink UDP。PX4 本机监听 14580,向 14540 发送;MAVSDK 监听 14540。
3. **QGC <-> PX4**: MAVLink UDP。PX4 监听 18570,主动推送到 10.0.2.2:14550(虚拟机里 10.0.2.2 就是宿主机);QGC 在 Windows 上监听 14550。VirtualBox NAT 负责这一跳。
4. **日志**: PX4 写 .ulg(机载);QGC 写 .tlog(Windows);我们的脚本写 CSV。

## 一句话总结

Gazebo 负责"世界",PX4 负责"飞",MAVSDK 负责"用代码飞",QGC 负责"看"。
关掉 QGC 不影响飞行,它只是观察者(已实测:不开 QGC 时脚本仍可完成三次航点任务)。

## 为什么这个图重要

面试常问"你的数据是怎么流的"。这张图能让人在 30 秒内看清四层分工,
也能解释为什么"MAVSDK 能读到位置"不等于"仿真闭环正常"。
