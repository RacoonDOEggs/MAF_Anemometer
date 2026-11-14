"""
Plot MAF sensor readings from maf_readings.csv.

Figure 1: 3D scatter of voltage vs (wind_speed, temp) with a fitted trend surface.
Figure 2: 2D scatter of resistance vs temp with a fitted trend line.

Trend models (least squares):
  voltage    = a + b*sqrt(wind_speed) + c*temp   (hot-wire / King's-law style response)
  resistance = m*temp + k                        (linear thermistor/RTD response)
"""
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "maf_readings.csv"

df = pd.read_csv(CSV_PATH)
U = df["wind_speed"].to_numpy(dtype=float)
T = df["temp"].to_numpy(dtype=float)
V = df["voltage"].to_numpy(dtype=float)
R = df["resistance"].to_numpy(dtype=float)


def r_squared(y, y_hat):
    ss_res = np.sum((y - y_hat) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return 1 - ss_res / ss_tot


# ---------------------------------------------------------------------------
# Figure 1: voltage surface over wind speed and temperature
# ---------------------------------------------------------------------------
def v_design(u, t):
    return np.column_stack([np.ones_like(u), np.sqrt(u), t])


coef_v, *_ = np.linalg.lstsq(v_design(U, T), V, rcond=None)
a, b, c = coef_v
r2_v = r_squared(V, v_design(U, T) @ coef_v)

u_grid = np.linspace(U.min(), U.max(), 50)
t_grid = np.linspace(T.min(), T.max(), 50)
UU, TT = np.meshgrid(u_grid, t_grid)
VV = a + b * np.sqrt(UU) + c * TT

fig1 = plt.figure(figsize=(10, 7))
ax1 = fig1.add_subplot(projection="3d")
ax1.plot_surface(UU, TT, VV, cmap="viridis", alpha=0.55, linewidth=0, antialiased=True)
ax1.scatter(U, T, V, color="crimson", s=45, depthshade=False, label="Measured")

# Vertical stems from each point to the surface make residuals easy to see
V_fit_pts = a + b * np.sqrt(U) + c * T
for ui, ti, vi, vf in zip(U, T, V, V_fit_pts):
    ax1.plot([ui, ui], [ti, ti], [vi, vf], color="crimson", linewidth=0.8, alpha=0.7)

ax1.set_xlabel("Wind speed (m/s)")
ax1.set_ylabel("Temperature (°C)")
ax1.set_zlabel("Voltage (V)")
ax1.set_title(
    f"MAF voltage vs wind speed & temperature\n"
    f"V = {a:.3f} + {b:.3f}·√U {c:+.4f}·T   (R² = {r2_v:.3f})"
)
ax1.view_init(elev=22, azim=-130)
ax1.legend(loc="upper left")
fig1.tight_layout()
fig1.savefig("maf_voltage_surface.png", dpi=150)

# ---------------------------------------------------------------------------
# Figure 2: resistance vs temperature
# ---------------------------------------------------------------------------
m, k = np.polyfit(T, R, 1)
r2_r = r_squared(R, m * T + k)
t_line = np.linspace(T.min(), T.max(), 100)

fig2, ax2 = plt.subplots(figsize=(8, 5.5))
ax2.scatter(T, R, color="crimson", s=45, zorder=3, label="Measured")
ax2.plot(t_line, m * t_line + k, color="tab:blue", linewidth=2,
         label=f"Fit: R = {m:.4f}·T + {k:.3f}  (R² = {r2_r:.3f})")
ax2.set_xlabel("Temperature (°C)")
ax2.set_ylabel("Resistance (kΩ)")
ax2.set_title("Thermocouple Resistance vs Temperature")
ax2.grid(True, alpha=0.3)
ax2.legend()
fig2.tight_layout()
fig2.savefig("maf_resistance_vs_temp.png", dpi=150)

plt.show()
