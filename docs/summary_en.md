# Project Summary (English)

I built a simulation-based validation platform for a PX4 multicopter. The system runs PX4 SITL
with Gazebo on Ubuntu and communicates over MAVLink with QGroundControl on the host and with
MAVSDK-Python scripts inside the virtual machine.

What I implemented:

- a fixed-rate telemetry logger (nine fields, 1.000 s sampling, timestamped output files);
- seven automated test cases covering connection, telemetry continuity, arming, takeoff,
  hover stability, waypoint arrival and landing;
- automatic PASS/FAIL judgement with precondition checks, safe cleanup, and a stable-window
  rule (three consecutive samples must satisfy the threshold);
- pandas-based analysis that produces summary tables, an altitude curve and a
  flight-kinematics figure.

Results: three consecutive runs, **21 of 21 judgements passed**. Hover altitude stayed at
2.38-2.47 m (target 2.5 m) with horizontal drift below 0.07 m; waypoint horizontal error was
at most 0.93 m and altitude error at most 0.08 m.

I also diagnosed a real bug: `goto_location()` takes an absolute altitude (AMSL), while the
original script passed a relative altitude. Because the SITL home altitude is about 488 m,
the vehicle descended instead of climbing. A controlled altitude trace confirmed the cause;
after the fix the altitude error dropped from about 10 m to below 0.11 m.

Limitations: all results are from SITL only, and the ~0.93 m waypoint offset is most likely
the autopilot's arrival radius, which still needs to be verified.
