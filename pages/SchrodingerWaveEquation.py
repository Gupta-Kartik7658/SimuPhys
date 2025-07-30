import numpy as np
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
import time

# --- Page and UI Configuration ---
st.set_page_config(page_title="Quantum Wave Packet", layout="wide", initial_sidebar_state="collapsed")
st.title("⚛️ 3D Quantum Wave Packet Animation")
st.write("This application simulates the time evolution of a 3D Gaussian wave packet for a free particle.")

# --- Parameter Input ---
st.header("Simulation Parameters")
col1, col2, col3, col4 = st.columns(4)
with col1:
    sigma = st.slider("Sigma (Initial Width)", 0.1, 2.0, 0.8, 0.1, key="sigma")
    px = st.slider("Momentum Px", -5.0, 5.0, 4.0, 0.5, key="px")
with col2:
    py = st.slider("Momentum Py", -5.0, 5.0, 0.0, 0.5, key="py")
    grid_size = st.select_slider("Grid Size", options=[16, 32, 48, 64], value=32, key="grid")
with col3:
    space_extent = st.slider("Space Extent", 4.0, 12.0, 8.0, 1.0, key="space")
    t_max = st.slider("Max Time", 1.0, 10.0, 6.0, 0.5, key="tmax")
with col4:
    dt = st.slider("Time Step (dt)", 0.02, 0.2, 0.08, 0.02, key="dt")

st.markdown("---") # Visual separator

# --- NEW: Theory and Formula Section ---
with st.expander("📖 Theory and Formulas", expanded=False):
    st.subheader("The Gaussian Wave Packet")
    st.write(
        "In quantum mechanics, a wave packet is a solution to the Schrödinger equation that describes a particle localized in space. "
        "This simulation shows a **Gaussian wave packet**, which has a Gaussian function as its spatial probability distribution. "
        "It represents a state of minimum uncertainty, satisfying the Heisenberg Uncertainty Principle."
    )
    st.write("The evolution is governed by the time-dependent Schrödinger equation for a free particle (where potential $V=0$):")
    st.latex(r"i\hbar \frac{\partial}{\partial t} \Psi(\mathbf{r}, t) = -\frac{\hbar^2}{2m} \nabla^2 \Psi(\mathbf{r}, t)")
    st.write(r"The wavefunction $\Psi(\mathbf{r}, t)$ is a complex function whose squared magnitude, $|\Psi|^2$, gives the probability density of finding the particle at position $\mathbf{r}$ at time $t$.")

    st.subheader("Initial State and Time Evolution")
    st.write(r"At $t=0$, the wave packet is described by:")
    st.latex(r"\Psi(\mathbf{r}, 0) \propto e^{-\frac{(\mathbf{r}-\mathbf{r}_0)^2}{2\sigma^2}} e^{i\mathbf{p}_0 \cdot (\mathbf{r}-\mathbf{r}_0)/\hbar}")
    st.write(
        r"where $\mathbf{r}_0$ is the initial position, $\mathbf{p}_0$ is the initial average momentum, and $\sigma$ is the initial spatial width of the packet."
    )

    st.write("As time progresses, two things happen:")
    st.markdown(
        r"""
        1.  **Translation:** The center of the packet, $\mathbf{r}_t$, moves with the group velocity $v_g = \mathbf{p}_0/m$.
            $$ \mathbf{r}_t = \mathbf{r}_0 + \frac{\mathbf{p}_0}{m}t $$
        2.  **Dispersion:** The packet spreads out over time. The width becomes time-dependent, $\sigma_t$:
            $$ \sigma_t = \sigma \sqrt{1 + \left(\frac{\hbar t}{m\sigma^2}\right)^2} $$
        """
    )
    st.write("The plots visualize different aspects of the wavefunction's 2D slice at $z=0$: **Re(Ψ)** (real part), **Im(Ψ)** (imaginary part), **|Ψ|²** (probability density), and **Phase(Ψ)**.")

with st.expander("💡 How to Use This Simulation", expanded=False):
            st.write(
                "This simulation allows you to explore how the properties of a quantum wave packet change its evolution. "
                "Simply adjust the sliders below and click the 'Generate & Animate' button to see the results."
            )
            st.subheader("Parameter Effects")
            st.markdown(
                """
                - **Sigma (Initial Width) $\sigma$:** Controls the initial size of the packet. A **smaller** sigma means a more localized particle, but due to the uncertainty principle, it has a larger spread in momentum and will disperse **faster**. A **larger** sigma creates a wider packet that spreads more slowly.

                - **Momentum Px, Py:** Sets the initial velocity of the packet. This determines the speed and direction of its travel across the simulation space.

                - **Grid Size:** The resolution of the simulation. Higher values produce smoother, more accurate plots but take much longer to compute. Lower values are faster but may appear blocky.

                - **Space Extent:** The size of the simulation box (from `-extent` to `+extent`). Make sure this is large enough to contain the packet for the duration of the animation.

                - **Max Time $t_{max}$:** The total duration of the animation.

                - **Time Step (dt):** The time between animation frames. A smaller `dt` results in a smoother animation but increases the number of frames to calculate.
                """
            )

# Constants
hbar = 1.0
mass = 1.0
x0, y0, z0 = -4.0, 0.0, 0.0  # Initial position

# --- Core Calculation Function ---
@st.cache_data
def create_wave_packet_3d(grid_size, space_extent, sigma, px, py, time):
    """
    Calculates the 3D wave packet's state at a given time.
    """
    x = np.linspace(-space_extent, space_extent, grid_size)
    y = np.linspace(-space_extent, space_extent, grid_size)
    z = np.linspace(-space_extent, space_extent, grid_size)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    x_center = x0 + (px / mass) * time
    y_center = y0 + (py / mass) * time
    z_center = z0

    sigma_t_sq = sigma**2 * (1 + (hbar * time / (mass * sigma**2))**2)
    envelope = np.exp(-((X - x_center)**2 + (Y - y_center)**2 + (Z - z_center)**2) / (2 * sigma_t_sq))

    kx = px / hbar
    ky = py / hbar
    phase_motion = kx * (X - x_center) + ky * (Y - y_center)
    energy = (px**2 + py**2) / (2 * mass)
    phase_time = -energy * time / hbar

    if time > 0:
        beta = hbar * time / (mass * sigma**2)
        dispersive_phase = ((X - x_center)**2 + (Y - y_center)**2 + (Z - z_center)**2) * (beta / (2 * sigma**2 * (1 + beta**2)))
    else:
        dispersive_phase = 0

    total_phase = phase_motion + phase_time + dispersive_phase
    psi = envelope * np.exp(1j * total_phase)

    prob_density = np.abs(psi)**2
    real_part = np.real(psi)
    imag_part = np.imag(psi)
    phase = np.angle(psi)

    # Normalize for visualization
    prob_density /= np.max(prob_density) if np.max(prob_density) > 1e-9 else 1
    real_part /= np.max(np.abs(real_part)) if np.max(np.abs(real_part)) > 1e-9 else 1
    imag_part /= np.max(np.abs(imag_part)) if np.max(np.abs(imag_part)) > 1e-9 else 1

    return {
        'x': x, 'y': y, 'z': z,
        'prob_density': prob_density,
        'real': real_part,
        'imag': imag_part,
        'phase': phase,
    }

# --- Main Application Logic ---
if st.button("🚀 Generate & Animate", type="primary"):
    with st.spinner(f"Calculating animation frames... (Grid Size: {grid_size}, Time Steps: {int(t_max/dt)})"):
        
        slice_idx = grid_size // 2
        times = np.arange(0, t_max, dt)

        def make_surface(z_data, x_grid, y_grid, colorscale, zmin=None, zmax=None):
            return go.Surface(
                z=z_data, x=x_grid, y=y_grid,
                colorscale=colorscale, showscale=False, cmin=zmin, cmax=zmax, opacity=0.95
            )

        x_grid = np.linspace(-space_extent, space_extent, grid_size)
        y_grid = np.linspace(-space_extent, space_extent, grid_size)
        X, Y = np.meshgrid(x_grid, y_grid, indexing='ij')

        frames = []
        start_time = time.time()
        for t in times:
            wave = create_wave_packet_3d(grid_size, space_extent, sigma, px, py, t)
            real_slice = wave['real'][:, :, slice_idx]
            imag_slice = wave['imag'][:, :, slice_idx]
            prob_slice = wave['prob_density'][:, :, slice_idx]
            phase_slice = wave['phase'][:, :, slice_idx]

            frames.append(go.Frame(
                data=[
                    make_surface(real_slice, X, Y, "RdBu", zmin=-1, zmax=1),
                    make_surface(imag_slice, X, Y, "RdBu", zmin=-1, zmax=1),
                    go.Heatmap(z=real_slice),
                    go.Heatmap(z=imag_slice),
                    go.Heatmap(z=prob_slice),
                    go.Heatmap(z=phase_slice),
                ], name=f"{t:.2f}"
            ))
        
        end_time = time.time()
        st.info(f"Frame calculation finished in {end_time - start_time:.2f} seconds.")

        

        # --- NEW: "How to Use" Section ---
        


        init_wave = create_wave_packet_3d(grid_size, space_extent, sigma, px, py, 0)
        real_slice_init = init_wave['real'][:, :, slice_idx]
        imag_slice_init = init_wave['imag'][:, :, slice_idx]
        prob_slice_init = init_wave['prob_density'][:, :, slice_idx]
        phase_slice_init = init_wave['phase'][:, :, slice_idx]
        
        fig = make_subplots(
            rows=3, cols=2,
            specs=[
                [{'type': 'surface'}, {'type': 'surface'}],
                [{'type': 'heatmap'}, {'type': 'heatmap'}],
                [{'type': 'heatmap'}, {'type': 'heatmap'}]
            ],
            subplot_titles=(
                "3D Re(Ψ)", "3D Im(Ψ)",
                "2D Re(Ψ)", "2D Im(Ψ)",
                r"2D |Ψ|²", "2D Phase(Ψ)"
            ),
            vertical_spacing=0.12,
            row_heights=[1, 1, 1],
            column_widths=[1, 1]
        )

        # Add initial traces
        fig.add_trace(make_surface(real_slice_init, X, Y, "RdBu", zmin=-1, zmax=1), row=1, col=1)
        fig.add_trace(make_surface(imag_slice_init, X, Y, "RdBu", zmin=-1, zmax=1), row=1, col=2)
        fig.add_trace(go.Heatmap(z=real_slice_init, x=x_grid, y=y_grid, colorscale='RdBu', zmin=-1, zmax=1, showscale=False), row=2, col=1)
        fig.add_trace(go.Heatmap(z=imag_slice_init, x=x_grid, y=y_grid, colorscale='RdBu', zmin=-1, zmax=1, showscale=False), row=2, col=2)
        fig.add_trace(go.Heatmap(z=prob_slice_init, x=x_grid, y=y_grid, colorscale='Viridis', zmin=0, zmax=1, showscale=False), row=3, col=1)
        fig.add_trace(go.Heatmap(z=phase_slice_init, x=x_grid, y=y_grid, colorscale='hsv', zmin=-np.pi, zmax=np.pi, showscale=False), row=3, col=2)

        # Unified animation controls
        fig.update_layout(
            height=1500,
            title_text="Wave Packet Evolution (2D Slice at z=0)",
            updatemenus=[{
                "type": "buttons", "direction": "left", "pad": {"r": 10, "t": 20},
                "showactive": True, "x": 0.1, "xanchor": "right", "y": 1.02, "yanchor": "top",
                "bgcolor": "#F0F2F6",
                "bordercolor": "#F0F2F6",
                "font": {"color": "#31333F"},
                "buttons": [
                    {"label": "▶ Play", "method": "animate", "args": [None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True, "transition": {"duration": 0}}]},
                    {"label": "❚❚ Pause", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]}
                ],
            }],
            sliders=[{
                "active": 0, "steps": [{"args": [[f.name], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}], "label": f.name, "method": "animate"} for f in frames],
                "transition": {"duration": 0}, "x": 0.1, "len": 0.9, "xanchor": "left", "y": -0.02, "yanchor": "top", "currentvalue": {"font": {"size": 16}, "prefix": "Time: ", "visible": True, "xanchor": "right"}
            }]
        )
        
        # Update scene properties for 3D plots
        scene_props = dict(
            xaxis_title="x", yaxis_title="y", zaxis_title="Value",
            camera_eye=dict(x=1.8, y=1.8, z=1.8),
            aspectratio=dict(x=1, y=1, z=0.7) 
        )
        fig.update_scenes(scene_props, row=1, col=1)
        fig.update_scenes(scene_props, row=1, col=2)
        
        # Ensure heatmap plots have a 1:1 aspect ratio
        fig.update_yaxes(scaleanchor="x", scaleratio=1)
        
        fig.frames = frames
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Adjust the parameters above and click 'Generate & Animate' to start the simulation.")