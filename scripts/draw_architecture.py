import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(11, 6.8))
ax.set_xlim(0, 11)
ax.set_ylim(0, 6.8)
ax.axis("off")


def box(x, y, w, h, title, sub, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                                linewidth=1.5, edgecolor="#333333", facecolor=color))
    ax.text(x + w / 2, y + h - 0.32, title, ha="center", va="center",
            fontsize=12, fontweight="bold")
    ax.text(x + w / 2, y + h / 2 - 0.28, sub, ha="center", va="center",
            fontsize=8.5, color="#333333")


def arrow(p1, p2, label):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="<->", mutation_scale=13,
                                 linewidth=1.4, color="#555555"))
    ax.text((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 + 0.14, label,
            ha="center", va="bottom", fontsize=8, color="#333333")


box(3.9, 4.7, 3.2, 1.35, "Gazebo Sim 8.15", "physics, world, sensors", "#dbeafe")
box(3.9, 2.5, 3.2, 1.65, "PX4 SITL",
    "EKF / control / mixer\nout: 14580->14540, 18570->14550", "#fef3c7")
box(0.5, 2.5, 2.6, 1.65, "MAVSDK-Python", "our scripts\nlistens UDP 14540", "#dcfce7")
box(7.9, 2.5, 2.6, 1.65, "QGroundControl", "Windows host\nlistens UDP 14550", "#fae8ff")

ax.add_patch(FancyArrowPatch((5.5, 4.65), (5.5, 4.18), arrowstyle="<->", mutation_scale=13,
                             linewidth=1.4, color="#555555"))
ax.text(6.2, 4.42, "gz transport", ha="left", va="center", fontsize=8, color="#333333")
arrow((3.85, 3.32), (3.15, 3.32), "MAVLink")
arrow((7.15, 3.32), (7.85, 3.32), "MAVLink")
ax.text(5.5, 1.45,
        "Gazebo provides physics and sensor data; PX4 is the flight controller;\n"
        "MAVSDK-Python sends commands and reads telemetry; QGC is monitoring only (optional).",
        ha="center", va="center", fontsize=9.5, color="#333333")
ax.set_title("PX4 UAV Autonomous Flight Platform - Data Flow",
             fontsize=14, fontweight="bold")
fig.tight_layout()
fig.savefig("docs/architecture.png", dpi=160)
print("saved docs/architecture.png")
