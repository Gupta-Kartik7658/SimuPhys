import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# ---- Physics: Compute Electric Field ----
def compute_field_grid(t, grid_size=20):
    A = 1.0  # Amplitude of oscillation
    w = 2.0  # Angular frequency
    c = 3.0  # Speed of light
    q = 1.0  # Unit charge

    x_vals = np.linspace(-5, 5, grid_size)
    y_vals = np.linspace(-5, 5, grid_size)

    x_list, y_list, u_list, v_list = [], [], [], []

    for x in x_vals:
        for y in y_vals:
            r = np.sqrt(x**2 + y**2)
            if r < 0.5:
                # Avoid singularity near charge
                u, v = 0, 0
            else:
                delay = r / c
                phase = w * (t - delay)
                E_mag = (q * A * w**2 * np.sin(phase)) / r
                theta = np.arctan2(y, x)
                u = E_mag * np.cos(theta)
                v = E_mag * np.sin(theta)

            x_list.append(x)
            y_list.append(y)
            u_list.append(u)
            v_list.append(v)

    return x_list, y_list, u_list, v_list

# ---- Streamlit Setup ----
st.set_page_config(layout="wide")
st.title("⚡ Oscillating Charge Creating Light (3Blue1Brown Style)")
st.markdown("This visualizes how a wiggling point charge emits electromagnetic waves using a simplified radiation field model.")

# Sidebar Controls
fps = st.sidebar.slider("Frames per second", 1, 60, 20)
duration = st.sidebar.slider("Duration (seconds)", 1, 20, 10)
grid_size = st.sidebar.slider("Field grid density", 10, 40, 20)
pause = st.sidebar.checkbox("Pause animation")

# Placeholder for Plotly plot
plot_placeholder = st.empty()

# ---- Animation Loop ----
start_time = time.time()
frame = 0

while (not pause) and (time.time() - start_time < duration):
    t = time.time() - start_time

    x, y, u, v = compute_field_grid(t, grid_size=grid_size)

    fig = go.Figure()

    # Draw vector field (arrows)
    fig.add_trace(go.Cone(
        x=x, y=y, z=[0]*len(x),
        u=u, v=v, w=[0]*len(x),
        sizemode="absolute",
        sizeref=0.5,
        anchor="tail",
        colorscale="Viridis",
        showscale=False,
        opacity=0.8
    ))

    # Draw central charge oscillation
    y_charge = 1.0 * np.sin(2.0 * t)
    fig.add_trace(go.Scatter3d(
        x=[0], y=[y_charge], z=[0],
        mode='markers',
        marker=dict(size=6, color='blue'),
        name='Oscillating Charge'
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-5, 5], visible=False),
            yaxis=dict(range=[-5, 5], visible=False),
            zaxis=dict(range=[-0.5, 0.5], visible=False),
            aspectratio=dict(x=1, y=1, z=0.2)
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=600
    )

    plot_placeholder.plotly_chart(fig, use_container_width=True)
    time.sleep(1 / fps)


