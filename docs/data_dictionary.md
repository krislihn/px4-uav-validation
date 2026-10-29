# 遥测数据字典

来源：`scripts/telemetry_logger.py`（MAVSDK `position_velocity_ned()`、
`attitude_euler()`、`armed()` 与 `flight_mode()`）。

| 字段 | 含义 | 单位 | 说明 |
| --- | --- | --- | --- |
| `t_s` | 采样时刻 | s | 相对开始记录的单调时间，定频 1.000 s |
| `rel_alt_m` | 相对高度 | m | 相对起飞点（home），由 `-down_m` 得到 |
| `abs_alt_m` | 绝对高度 | m | 海拔（AMSL）= 起飞前读取的 home 海拔 + rel_alt |
| `north_m` | 北向位置 | m | NED 北向，相对 home |
| `east_m` | 东向位置 | m | NED 东向，相对 home |
| `vn` | 北向速度 | m/s | NED 北向速度 |
| `ve` | 东向速度 | m/s | NED 东向速度 |
| `vd` | 垂向速度 | m/s | NED 向下为正：负值表示上升 |
| `roll_deg` | 横滚角 | deg | 来自 `attitude_euler()` |
| `pitch_deg` | 俯仰角 | deg | 来自 `attitude_euler()` |
| `yaw_deg` | 偏航角 | deg | 来自 `attitude_euler()` |
| `armed` | 解锁状态 | - | `True` 表示飞控已解锁，`False` 表示未解锁 |
| `mode` | 飞行模式 | - | 来自 MAVSDK `flight_mode()`，如 HOLD / TAKEOFF / LAND |

注意：`north_m` / `east_m` 是**米**；而 `flight_results.csv` 中的 `lat_err` / `lon_err` 是**度**，两者不能混用。

2026-10-28 起采集器输出上述 13 个字段；此前的遥测文件只有前 9 个字段。
