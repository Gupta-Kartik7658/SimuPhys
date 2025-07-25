import numpy as np
import sympy as smp
from sympy.utilities.lambdify import lambdify
from sympy import latex
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"

def main():
    # Get user input
    fx_str = input("Enter Fₓ(x, y, z): ") or "2*x*y"
    fy_str = input("Enter Fᵧ(x, y, z): ") or "sin(cos(x*y))"
    fz_str = input("Enter F_z(x, y, z): ") or "5*x"
    density = input("Enter grid density (default=6): ")
    density = int(density) if density.strip() else 6

    try:
        # Symbols
        x, y, z = smp.symbols('x y z')
        try:
            expr_x = smp.sympify(fx_str)
            expr_y = smp.sympify(fy_str)
            expr_z = smp.sympify(fz_str)
        except Exception as e:
            print(f"Invalid field input: {e}")
            return

        fx = lambdify((x, y, z), expr_x, modules='numpy')
        fy = lambdify((x, y, z), expr_y, modules='numpy')
        fz = lambdify((x, y, z), expr_z, modules='numpy')

        # Grid
        x_vals = np.linspace(-2, 2, density)
        y_vals = np.linspace(-2, 2, density)
        z_vals = np.linspace(-2, 2, max(2, density // 2))
        X, Y, Z = np.meshgrid(x_vals, y_vals, z_vals)
        Xf, Yf, Zf = X.ravel(), Y.ravel(), Z.ravel()

        # Vector field components
        try:
            U = fx(Xf, Yf, Zf)
            V = fy(Xf, Yf, Zf)
            W = fz(Xf, Yf, Zf)
        except Exception as e:
            print(f"Error evaluating vector field: {e}")
            return

        # Filter out NaNs for plotting
        mask = ~(np.isnan(U) | np.isnan(V) | np.isnan(W))
        if mask.sum() == 0:
            print("Warning: All vector field values are invalid (NaN). Showing empty plot.")
            Xf_plot, Yf_plot, Zf_plot = Xf, Yf, Zf
            U_plot = V_plot = W_plot = np.zeros_like(Xf)
        else:
            Xf_plot, Yf_plot, Zf_plot = Xf[mask], Yf[mask], Zf[mask]
            U_plot, V_plot, W_plot = U[mask], V[mask], W[mask]

        # LaTeX representation
        components = []
        if expr_x != 0:
            components.append(f"{latex(expr_x)} \\hat{{i}}")
        if expr_y != 0:
            components.append(f"{latex(expr_y)} \\hat{{j}}")
        if expr_z != 0:
            components.append(f"{latex(expr_z)} \\hat{{k}}")
        latex_eqn = "\\vec{F}(x,y,z) = " + " + ".join(components)

        # Divergence and Curl
        div_F = smp.diff(expr_x, x) + smp.diff(expr_y, y) + smp.diff(expr_z, z)
        curl_F = smp.Matrix([
            smp.diff(expr_z, y) - smp.diff(expr_y, z),
            smp.diff(expr_x, z) - smp.diff(expr_z, x),
            smp.diff(expr_y, x) - smp.diff(expr_x, y)
        ])

        div_F_func = lambdify((x, y, z), div_F, modules='numpy')
        curl_F_func = lambdify((x, y, z), curl_F, modules='numpy')

        try:
            div_vals = div_F_func(Xf, Yf, Zf)
        except Exception as e:
            print(f"Error evaluating divergence: {e}")
            div_vals = np.zeros_like(Xf)

        try:
            curl_result = curl_F_func(Xf, Yf, Zf)
            curl_U = np.asarray(curl_result[0]).ravel()
            curl_V = np.asarray(curl_result[1]).ravel()
            curl_W = np.asarray(curl_result[2]).ravel()
        except Exception as e:
            print(f"Error evaluating curl: {e}")
            curl_U = curl_V = curl_W = np.zeros_like(Xf)

        curl_magnitude = np.sqrt(curl_U**2 + curl_V**2 + curl_W**2)

        # Filter out NaNs for curl
        mask_curl = ~(np.isnan(curl_U) | np.isnan(curl_V) | np.isnan(curl_W))
        if mask_curl.sum() == 0:
            print("Warning: All curl values are invalid (NaN). Showing empty plot.")
            Xf_curl, Yf_curl, Zf_curl = Xf, Yf, Zf
            curl_U_plot = curl_V_plot = curl_W_plot = np.zeros_like(Xf)
            curl_magnitude_plot = np.zeros_like(Xf)
        else:
            Xf_curl, Yf_curl, Zf_curl = Xf[mask_curl], Yf[mask_curl], Zf[mask_curl]
            curl_U_plot, curl_V_plot, curl_W_plot = curl_U[mask_curl], curl_V[mask_curl], curl_W[mask_curl]
            curl_magnitude_plot = curl_magnitude[mask_curl]

        # Plot Vector Field
        fig = go.Figure()
        fig.add_trace(go.Cone(
            x=Xf_plot, y=Yf_plot, z=Zf_plot,
            u=U_plot, v=V_plot, w=W_plot,
            colorscale='Viridis',
            sizemode="scaled",
            sizeref=0.5,
            showscale=True,
            anchor="tail",
            colorbar=dict(title="Magnitude", thickness=15),
            hovertemplate=
                "Coordinates: (%{x:.3f}, %{y:.3f}, %{z:.3f})<br>" +
                "Field Value: %{u:.3f} î + %{v:.3f} ĵ + %{w:.3f} k̂<br>" +
                "Magnitude Value: %{customdata:.3f}<extra></extra>",
            customdata=np.sqrt(U_plot**2 + V_plot**2 + W_plot**2)
        ))
        fig.update_layout(
            scene=dict(
                xaxis=dict(title='X', backgroundcolor="rgba(240,240,255,0.95)", gridcolor="lightgray", zerolinecolor="gray"),
                yaxis=dict(title='Y', backgroundcolor="rgba(240,255,240,0.95)", gridcolor="lightgray", zerolinecolor="gray"),
                zaxis=dict(title='Z', backgroundcolor="rgba(255,240,240,0.95)", gridcolor="lightgray", zerolinecolor="gray"),
                aspectmode='cube'
            ),
            title=dict(
                text=f"$${latex_eqn}$$",
                font=dict(size=22, family="DejaVu Sans Mono"),
                x=0.5,
                xanchor="center",
                y=0.95,
                yanchor="top"
            ),
            margin=dict(l=10, r=10, t=80, b=10),
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        pio.show(fig)

        # Plot Divergence
        fig_div = go.Figure()
        fig_div.add_trace(go.Scatter3d(
            x=Xf, y=Yf, z=Zf,
            mode='markers',
            marker=dict(
                size=6,
                color=div_vals,
                colorscale='RdBu',
                colorbar=dict(title="Divergence"),
                opacity=0.8
            ),
            hovertemplate="(%{x:.2f}, %{y:.2f}, %{z:.2f})<br>Divergence: %{marker.color:.2f}<extra></extra>"
        ))
        fig_div.update_layout(
            scene=dict(
                xaxis=dict(title='X'),
                yaxis=dict(title='Y'),
                zaxis=dict(title='Z'),
                aspectmode='cube'
            ),
            title=dict(
                text=f"Divergence: $$\\nabla \\cdot \\vec{{F}} = {latex(div_F)}$$",
                font=dict(size=20),
                x=0.5,
                xanchor="center"
            ),
            margin=dict(l=10, r=10, t=80, b=10)
        )
        pio.show(fig_div)

        # Plot Curl
        fig_curl = go.Figure()
        fig_curl.add_trace(go.Cone(
            x=Xf_curl, y=Yf_curl, z=Zf_curl,
            u=curl_U_plot, v=curl_V_plot, w=curl_W_plot,
            colorscale='Viridis',
            sizemode="scaled",
            sizeref=0.5,
            showscale=True,
            anchor="tail",
            colorbar=dict(title="|Curl|", thickness=15),
            hovertemplate=
                "Coordinates: (%{x:.3f}, %{y:.3f}, %{z:.3f})<br>" +
                "Curl: %{u:.3f} î + %{v:.3f} ĵ + %{w:.3f} k̂<br>" +
                "|Curl| = %{customdata:.3f}<extra></extra>",
            customdata=curl_magnitude_plot
        ))
        fig_curl.update_layout(
            scene=dict(
                xaxis=dict(title='X', backgroundcolor="rgba(240,240,255,0.95)", gridcolor="lightgray", zerolinecolor="gray"),
                yaxis=dict(title='Y', backgroundcolor="rgba(240,255,240,0.95)", gridcolor="lightgray", zerolinecolor="gray"),
                zaxis=dict(title='Z', backgroundcolor="rgba(255,240,240,0.95)", gridcolor="lightgray", zerolinecolor="gray"),
                aspectmode='cube'
            ),
            title=dict(
                text=f"Curl: $$\\nabla \\times \\vec{{F}} = {latex(curl_F[0])} \\hat{{i}} + {latex(curl_F[1])} \\hat{{j}} + {latex(curl_F[2])} \\hat{{k}}$$",
                font=dict(size=22, family="DejaVu Sans Mono"),
                x=0.5,
                xanchor="center",
                y=0.95,
                yanchor="top"
            ),
            margin=dict(l=10, r=10, t=80, b=10),
            paper_bgcolor="white",
            plot_bgcolor="white"
        )
        pio.show(fig_curl)

    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
