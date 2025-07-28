import numpy as np
import plotly.graph_objs as go
import plotly.io as pio

pio.renderers.default = "browser"

# --- Parameter Input with Defaults and Error Handling ---
def get_float(prompt, default):
    try:
        val = input(f"{prompt} [default={default}]: ").strip()
        return float(val) if val else default
    except Exception:
        print(f"Invalid input, using default {default}")
        return default

def get_int(prompt, default):
    try:
        val = input(f"{prompt} [default={default}]: ").strip()
        return int(val) if val else default
    except Exception:
        print(f"Invalid input, using default {default}")
        return default

# Get parameters from user or use defaults
sigma = get_float("Enter sigma (width)", 0.8)
px = get_float("Enter px (momentum in x)", 4.0)
py = get_float("Enter py (momentum in y)", 0.0)
grid_size = get_int("Enter grid size", 32)
space_extent = get_float("Enter space extent", 8.0)
t_max = get_float("Enter max time", 6.0)
dt = get_float("Enter time step", 0.08)

hbar = 1.0
mass = 1.0
x0, y0, z0 = -4.0, 0.0, 0.0  # Initial position

def create_wave_packet_3d(grid_size, space_extent, sigma, px, py, time):
    try:
        x = np.linspace(-space_extent, space_extent, grid_size)
        y = np.linspace(-space_extent, space_extent, grid_size)
        z = np.linspace(-space_extent, space_extent, grid_size)
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

        x_center = x0 + (px / mass) * time
        y_center = y0 + (py / mass) * time
        z_center = z0

        sigma_t = sigma * np.sqrt(1 + (hbar * time / (mass * sigma**2))**2)
        envelope = np.exp(-((X - x_center)**2 + (Y - y_center)**2 + (Z - z_center)**2) / (2 * sigma_t**2))

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

        # Normalize for plotting
        prob_density /= np.max(prob_density) if np.max(prob_density) != 0 else 1
        real_part /= np.max(np.abs(real_part)) if np.max(np.abs(real_part)) != 0 else 1
        imag_part /= np.max(np.abs(imag_part)) if np.max(np.abs(imag_part)) != 0 else 1

        return {
            'x': x, 'y': y, 'z': z,
            'prob_density': prob_density,
            'real': real_part,
            'imag': imag_part,
            'phase': phase,
        }
    except Exception as e:
        print(f"Error in wave packet calculation: {e}")
        # Return zeros if error
        arr = np.zeros((grid_size, grid_size, grid_size))
        return {
            'x': np.linspace(-space_extent, space_extent, grid_size),
            'y': np.linspace(-space_extent, space_extent, grid_size),
            'z': np.linspace(-space_extent, space_extent, grid_size),
            'prob_density': arr,
            'real': arr,
            'imag': arr,
            'phase': arr,
        }

# --- Animation Setup ---
slice_idx = grid_size // 2
times = np.arange(0, t_max, dt)

# Downsample for 3D surface speed
def downsample(arr, stride=2):
    return arr[::stride, ::stride]

def make_surface(z, x, y, colorscale, zmin=None, zmax=None):
    stride = max(1, grid_size // 32)
    return go.Surface(
        z=downsample(z, stride),
        x=downsample(x, stride),
        y=downsample(y, stride),
        colorscale=colorscale,
        showscale=False,
        cmin=zmin,
        cmax=zmax,
        opacity=0.95
    )

# Precompute meshgrid for 2D and 3D
x = np.linspace(-space_extent, space_extent, grid_size)
y = np.linspace(-space_extent, space_extent, grid_size)
X, Y = np.meshgrid(x, y, indexing='ij')

# Precompute all frames for speed
frames_2d = []
frames_3d = []
for t in times:
    wave = create_wave_packet_3d(grid_size, space_extent, sigma, px, py, t)
    real_slice = wave['real'][:, :, slice_idx]
    imag_slice = wave['imag'][:, :, slice_idx]
    prob_slice = wave['prob_density'][:, :, slice_idx]
    phase_slice = wave['phase'][:, :, slice_idx]

    # 2D frame
    frame2d = go.Frame(
        data=[
            go.Heatmap(z=real_slice, x=x, y=y, colorscale='RdBu', zmin=-1, zmax=1, showscale=False),
            go.Heatmap(z=imag_slice, x=x, y=y, colorscale='RdBu', zmin=-1, zmax=1, showscale=False),
            go.Heatmap(z=prob_slice, x=x, y=y, colorscale='Viridis', zmin=0, zmax=1, showscale=False),
            go.Heatmap(z=phase_slice, x=x, y=y, colorscale='HSV', zmin=-np.pi, zmax=np.pi, showscale=False),
        ],
        name=f"{t:.2f}"
    )
    frames_2d.append(frame2d)

    # 3D frame
    frame3d = go.Frame(
        data=[
            make_surface(real_slice, X, Y, "RdBu", zmin=-1, zmax=1),
            make_surface(imag_slice, X, Y, "RdBu", zmin=-1, zmax=1),
            make_surface(prob_slice, X, Y, "Viridis", zmin=0, zmax=1)
        ],
        name=f"{t:.2f}"
    )
    frames_3d.append(frame3d)

# Initial data for the first frame
init_wave = create_wave_packet_3d(grid_size, space_extent, sigma, px, py, 0)
real_slice = init_wave['real'][:, :, slice_idx]
imag_slice = init_wave['imag'][:, :, slice_idx]
prob_slice = init_wave['prob_density'][:, :, slice_idx]
phase_slice = init_wave['phase'][:, :, slice_idx]

# 2D Plot (all 2D slices as subplots)
from plotly.subplots import make_subplots
fig2d = make_subplots(
    rows=2, cols=2,
    subplot_titles=["Re(Ψ)", "Im(Ψ)", "|Ψ|²", "Phase(Ψ)"]
)
fig2d.add_trace(go.Heatmap(z=real_slice, x=x, y=y, colorscale='RdBu', zmin=-1, zmax=1, showscale=False), row=1, col=1)
fig2d.add_trace(go.Heatmap(z=imag_slice, x=x, y=y, colorscale='RdBu', zmin=-1, zmax=1, showscale=False), row=1, col=2)
fig2d.add_trace(go.Heatmap(z=prob_slice, x=x, y=y, colorscale='Viridis', zmin=0, zmax=1, showscale=False), row=2, col=1)
fig2d.add_trace(go.Heatmap(z=phase_slice, x=x, y=y, colorscale='HSV', zmin=-np.pi, zmax=np.pi, showscale=False), row=2, col=2)
fig2d.update_layout(
    title="2D Slices of 3D Gaussian Wave Packet",
    height=800,
    width=1000,
    updatemenus=[{
        "type": "buttons",
        "buttons": [
            {"label": "Play", "method": "animate", "args": [None, {"frame": {"duration": 60, "redraw": True}, "fromcurrent": True}]},
            {"label": "Pause", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 87},
        "showactive": True,
        "x": 0.1,
        "xanchor": "right",
        "y": 1.1,
        "yanchor": "top"
    }],
    sliders=[{
        "steps": [
            {"args": [[f"{t:.2f}"], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
             "label": f"{t:.2f}", "method": "animate"}
            for t in times
        ],
        "transition": {"duration": 0},
        "x": 0.1,
        "len": 0.8,
        "xanchor": "left",
        "y": 0,
        "yanchor": "top"
    }]
)
fig2d.frames = frames_2d

# 3D Plot (all 3D surfaces as subplots)
fig3d = make_subplots(
    rows=1, cols=3,
    specs=[[{'type': 'surface'}, {'type': 'surface'}, {'type': 'surface'}]],
    subplot_titles=["3D Re(Ψ)", "3D Im(Ψ)", "3D |Ψ|²"]
)
fig3d.add_trace(make_surface(real_slice, X, Y, "RdBu", zmin=-1, zmax=1), row=1, col=1)
fig3d.add_trace(make_surface(imag_slice, X, Y, "RdBu", zmin=-1, zmax=1), row=1, col=2)
fig3d.add_trace(make_surface(prob_slice, X, Y, "Viridis", zmin=0, zmax=1), row=1, col=3)
fig3d.update_layout(
    title="3D Surfaces of 3D Gaussian Wave Packet (Central Z Slice)",
    height=600,
    width=1800,
    scene=dict(
        xaxis_title="x",
        yaxis_title="y",
        zaxis_title="Value"
    ),
    updatemenus=[{
        "type": "buttons",
        "buttons": [
            {"label": "Play", "method": "animate", "args": [None, {"frame": {"duration": 60, "redraw": True}, "fromcurrent": True}]},
            {"label": "Pause", "method": "animate", "args": [[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]}
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 87},
        "showactive": True,
        "x": 0.1,
        "xanchor": "right",
        "y": 1.1,
        "yanchor": "top"
    }],
    sliders=[{
        "steps": [
            {"args": [[f"{t:.2f}"], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
             "label": f"{t:.2f}", "method": "animate"}
            for t in times
        ],
        "transition": {"duration": 0},
        "x": 0.1,
        "len": 0.8,
        "xanchor": "left",
        "y": 0,
        "yanchor": "top"
    }]
)
fig3d.frames = frames_3d

fig2d.show()
fig3d.show()