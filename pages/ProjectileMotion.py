import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# ---- 1. Streamlit Page Setup ----
st.set_page_config(
    page_title="Projectile Motion Simulator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("🚀 Projectile Motion Simulator")
st.write("An interactive physics simulator built entirely in Python. Adjust parameters, then start the simulation.")

# ---- 2. Physics Engine ----
class Projectile:
    """
    Handles the physics calculations for the projectile.
    """
    def __init__(self, x, y, vx, vy, params):
        self.x, self.y, self.vx, self.vy, self.params = x, y, vx, vy, params
        ball_volume_m3 = self.params['ball_volume'] / 1_000_000
        self.m = (self.params['ball_density'] * ball_volume_m3) or 0.001
        radius = np.cbrt((3 * ball_volume_m3) / (4 * np.pi))
        cross_sectional_area = np.pi * radius**2
        self.drag_constant = 0.5 * self.params['air_density'] * cross_sectional_area * self.params['drag_coefficient']

    def update(self, dt):
        """Update the projectile's state over a time step dt."""
        speed = np.sqrt(self.vx**2 + self.vy**2)
        total_ax, total_ay = self.params['wind'], -self.params['gravity']

        if speed > 0:
            F_drag = self.drag_constant * speed**2
            ax_drag = -(F_drag / self.m) * (self.vx / speed)
            ay_drag = -(F_drag / self.m) * (self.vy / speed)
            total_ax += ax_drag
            total_ay += ay_drag
            
        self.vx += total_ax * dt
        self.vy += total_ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

# ---- 3. Session State and Helper Functions ----
def reset_simulation():
    """Resets the simulation to its initial state based on current slider values."""
    st.session_state.status = "stopped"
    st.session_state.t = 0.0
    st.session_state.h0 = st.session_state.param_h0
    st.session_state.max_height = st.session_state.h0
    st.session_state.path_x = [0]
    st.session_state.path_y = [st.session_state.h0]
    
    angle_rad = np.deg2rad(st.session_state.param_angle)
    st.session_state.x = 0
    st.session_state.y = st.session_state.h0
    st.session_state.vx = st.session_state.param_v0 * np.cos(angle_rad)
    st.session_state.vy = st.session_state.param_v0 * np.sin(angle_rad)
    
    st.session_state.initial_v = st.session_state.param_v0
    st.session_state.initial_angle = st.session_state.param_angle
    st.session_state.initial_h = st.session_state.param_h0

# Initialize state if it doesn't exist
if 'status' not in st.session_state:
    st.session_state.param_v0 = 50.0
    st.session_state.param_angle = 45.0
    st.session_state.param_h0 = 0.0
    st.session_state.param_gravity = 9.8
    st.session_state.param_wind = 0.0
    st.session_state.param_ball_density = 1000.0
    st.session_state.param_ball_volume = 500.0
    st.session_state.param_air_density = 1.225
    st.session_state.param_drag_coefficient = 0.47
    reset_simulation()

# ---- 4. UI: Inputs on Main Screen ----
st.header("Simulation Parameters")
is_running = st.session_state.status != 'stopped'

c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("Initial Conditions")
    st.caption("These values are locked after starting.")
    st.slider("Velocity (m/s)", 10.0, 200.0, key="param_v0", on_change=reset_simulation, disabled=is_running)
    st.slider("Angle (°)", 0.0, 90.0, key="param_angle", on_change=reset_simulation, disabled=is_running)
    st.slider("Initial Height (m)", 0.0, 100.0, key="param_h0", on_change=reset_simulation, disabled=is_running)
with c2:
    st.subheader("Physics Parameters")
    st.caption("Change these mid-flight while paused!")
    st.slider("Gravity (m/s²)", 1.0, 20.0, key="param_gravity")
    st.slider("Wind Accel. (m/s²)", -10.0, 10.0, key="param_wind")
    st.slider("Drag Coefficient (Cd)", 0.0, 2.0, key="param_drag_coefficient")
with c3:
    st.subheader("Object & Air Properties")
    st.caption("Change these mid-flight while paused!")
    st.slider("Air Density (kg/m³)", 0.0, 2.0, key="param_air_density", format="%.3f")
    st.slider("Ball Density (kg/m³)", 100.0, 10000.0, key="param_ball_density")
    st.slider("Ball Volume (cm³)", 100.0, 10000.0, key="param_ball_volume")
    
# ---- 5. UI: Theory and How-To ----
with st.expander("📖 Theory and Formulas"):
    st.subheader("Ideal Kinematic Equations (No Air Drag)")
    st.write("For a projectile with no air resistance, the motion is governed by gravity alone.")
    st.latex(r"x(t) = v_{0x} t \quad \text{where} \quad v_{0x} = v_0 \cos(\theta)")
    st.latex(r"y(t) = h_0 + v_{0y} t - \frac{1}{2} g t^2 \quad \text{where} \quad v_{0y} = v_0 \sin(\theta)")
    st.markdown("---")
    st.subheader("Air Drag Force")
    st.write("This simulation models quadratic air drag, where the resistance force is proportional to the square of the object's speed. The drag force $F_D$ always opposes the velocity vector.")
    st.latex(r"F_D = \frac{1}{2} \rho A C_d v^2")
    st.markdown(
        """
        - **$\rho$ (rho):** Density of the surrounding air.
        - **$A$:** Cross-sectional area of the projectile.
        - **$C_d$:** Drag coefficient, a dimensionless value based on the object's shape (e.g., ~0.47 for a sphere).
        - **$v$:** The current speed of the object.
        """
    )
    st.subheader("How Object Properties Matter")
    st.write("The sliders for ball density and volume affect the simulation through two key properties:")
    st.markdown(
        r"""
        1.  **Mass ($m$):** Calculated from ball density ($\rho_{ball}$) and volume ($V_{ball}$), where $m = \rho_{ball} \times V_{ball}$. A more massive object is less affected by a given drag force ($a = F/m$).
        2.  **Cross-sectional Area ($A$):** Calculated from the volume, assuming a sphere: $A = \pi \left(\sqrt[3]{\frac{3V_{ball}}{4\pi}}\right)^2$. A larger area increases the drag force.
        """
    )

with st.expander("💡 How to Use This Simulation"):
    st.markdown(
        """
        1.  **Set Initial Conditions:** Use the first column of sliders to set the launch velocity, angle, and height. These can only be changed before a simulation starts.
        2.  **Adjust Physics:** Use the other sliders to change environmental physics and object properties.
        3.  **Run the Simulation:**
            - Click **Start** to begin the animation.
            - Click **Pause** at any time to freeze the simulation.
            - While paused, you can change the **Physics** or **Object** parameters to see how they affect the rest of the trajectory.
            - Click **Resume** to continue the simulation with the new parameters applied.
            - Click **Reset** to return to the initial launch conditions.
        """
    )

# ---- 6. UI: Controls and Placeholders ----
st.markdown("---")
control_cols = st.columns([1, 1, 5]) 

with control_cols[0]:
    if st.session_state.status in ["stopped", "paused"]:
        if st.button("▶️ " + ("Resume" if st.session_state.status == "paused" else "Start"), type="primary", use_container_width=True):
            st.session_state.status = "running"
            st.rerun()
    else:
        if st.button("⏸️ Pause", use_container_width=True):
            st.session_state.status = "paused"
            st.rerun()
with control_cols[1]:
    if st.button("🔁 Reset", use_container_width=True):
        reset_simulation()
        st.rerun()

info_placeholder = st.empty()
plot_placeholder = st.empty()
summary_placeholder = st.empty()


# ---- 7. Drawing and Animation Logic ----
def draw_current_state():
    """Helper function to draw the info table and plot for the current state."""
    speed = np.sqrt(st.session_state.vx**2 + st.session_state.vy**2)
    info_placeholder.markdown(
        f"""
        | Time | Position | Speed | Velocity (x,y) | Max Height |
        |---|---|---|---|---|
        | `{st.session_state.t:.2f}` s | `({st.session_state.x:.1f}, {st.session_state.y:.1f})` m | `{speed:.2f}` m/s | `({st.session_state.vx:.1f}, {st.session_state.vy:.1f})` m/s | `{st.session_state.max_height:.2f}` m|
        """
    )
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=st.session_state.path_x, y=st.session_state.path_y, mode='lines', name='Path', line=dict(color='#00d4aa', width=3)))
    fig.add_trace(go.Scatter(x=[st.session_state.x], y=[st.session_state.y], mode='markers', name='Ball', marker=dict(color='#ff4b4b', size=12, symbol='circle')))
    
    plot_range_x = max(100, st.session_state.x * 1.1) if st.session_state.x > 0 else 100
    plot_range_y = max(50, st.session_state.max_height * 1.1) if st.session_state.max_height > 0 else 50
    fig.update_layout(xaxis_title="Distance (m)", yaxis_title="Height (m)", xaxis=dict(range=[0, plot_range_x], constrain='domain'), yaxis=dict(range=[0, plot_range_y], scaleanchor="x", scaleratio=1), showlegend=False, height=500, margin=dict(l=20, r=20, t=20, b=20))
    plot_placeholder.plotly_chart(fig, use_container_width=True)

# Draw the initial or paused state
draw_current_state()

# Rerun-based animation loop
if st.session_state.status == "running":
    params = {key.replace('param_', ''): val for key, val in st.session_state.items() if key.startswith('param_')}
    p = Projectile(st.session_state.x, st.session_state.y, st.session_state.vx, st.session_state.vy, params)
    
    dt = 0.05
    p.update(dt)
    
    st.session_state.t += dt
    st.session_state.x, st.session_state.y, st.session_state.vx, st.session_state.vy = p.x, p.y, p.vx, p.vy
    st.session_state.path_x.append(p.x)
    st.session_state.path_y.append(p.y)
    st.session_state.max_height = max(st.session_state.max_height, p.y)

    if p.y < 0:
        st.session_state.status = "stopped"
        summary_placeholder.success("Simulation Complete!")
        # Final calculations for summary
        vy0 = st.session_state.initial_v * np.sin(np.deg2rad(st.session_state.initial_angle))
        vx0 = st.session_state.initial_v * np.cos(np.deg2rad(st.session_state.initial_angle))
        gravity_at_launch = st.session_state.param_gravity # Use current gravity for this calc
        time_no_drag = (vy0 + np.sqrt(vy0**2 + 2 * gravity_at_launch * st.session_state.initial_h)) / gravity_at_launch
        range_no_drag = vx0 * time_no_drag
        
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Time of Flight", f"{st.session_state.t:.2f} s")
        sc2.metric("Range", f"{p.x:.2f} m")
        sc3.metric("Max Height", f"{st.session_state.max_height:.2f} m")
        st.info(f"Launched at {st.session_state.initial_v}° and {st.session_state.initial_angle} m/s. Without wind or air drag, the ideal range would be **{range_no_drag:.2f} m**.")
        st.balloons()
        st.rerun()

    time.sleep(0.01) # Controls animation speed
    st.rerun()