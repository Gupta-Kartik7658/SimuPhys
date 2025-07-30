import numpy as np
import sympy as smp
from sympy.utilities.lambdify import lambdify
from sympy import latex
import plotly.graph_objects as go
import streamlit as st
import plotly.io as pio

# Set the page configuration for a wider layout
st.set_page_config(page_title="Vector Field Visualization", layout="wide", initial_sidebar_state="collapsed")

def to_array(value, grid_points):
    """
    Helper function to safely convert a scalar or array from lambdify 
    into a NumPy array matching the grid shape.
    """
    # Convert the input to a NumPy array
    arr = np.asarray(value)
    # If the array contains a single scalar value
    if arr.size == 1:
        # Create a new array with the same shape as the grid, filled with the scalar value
        return np.full_like(grid_points, arr.item())
    # If it's already an array, ensure it's flattened to 1D
    return arr.ravel()

def main():
    """
    Main function to run the Streamlit application.
    """
    st.title("Vector Field Visualization")
    st.write("Enter the components of the vector field F(x, y, z) and see it visualized, along with its divergence and curl.")
    
    # --- UI INPUTS ---
    # Create columns for a cleaner layout of input fields
    col1, col2, col3 = st.columns(3)
    with col1:
        fx_str = st.text_input("Enter Fₓ(x, y, z):", "y")
    with col2:
        fy_str = st.text_input("Enter Fᵧ(x, y, z):", "-x") 
    with col3:
        fz_str = st.text_input("Enter F_z(x, y, z):", "0") 

    # --- NEW: Slider for grid density ---
    density = st.slider("Select Grid Density:", min_value=3, max_value=15, value=6, step=1,
                        help="Controls the number of vectors shown. Higher values are more detailed but slower.")

    # --- NEW: Collapsible theory sections ---
    with st.expander("Learn about the concepts"):
        st.markdown("""
        #### Vector Fields
        A **vector field** is a function that assigns a vector to each point in a space. In 3D, a vector field $\\vec{F}$ can be written as:
        $$ \\vec{F}(x, y, z) = F_x(x, y, z) \\hat{i} + F_y(x, y, z) \\hat{j} + F_z(x, y, z) \\hat{k} $$
        Vector fields are used in physics and engineering to model phenomena like fluid flow, gravitational fields, and electric fields. The arrows in the visualization show the direction and magnitude of the vector at each point.

        #### Divergence ($\\nabla \\cdot \\vec{F}$)
        The **divergence** of a vector field measures the magnitude of a source or sink at a given point. It's a scalar value.
        - **Positive Divergence**: The field is "spreading out" or originating from that point (a source).
        - **Negative Divergence**: The field is "compressing" or flowing into that point (a sink).
        - **Zero Divergence**: The field is incompressible; what flows in must flow out.
        
        Mathematically, it is calculated as:
        $$ \\nabla \\cdot \\vec{F} = \\frac{\\partial F_x}{\\partial x} + \\frac{\\partial F_y}{\\partial y} + \\frac{\\partial F_z}{\\partial z} $$

        #### Curl ($\\nabla \\times \\vec{F}$)
        The **curl** of a vector field measures the rotation or circulation at a point. It is itself a vector field.
        - The **direction** of the curl vector indicates the axis of rotation (using the right-hand rule).
        - The **magnitude** of the curl vector indicates the speed of the rotation.
        - A curl of zero at all points means the field is **irrotational**.

        Mathematically, it is the cross product of the del operator with the vector field:
        $$ \\nabla \\times \\vec{F} = 
        \\begin{vmatrix}
        \\hat{i} & \\hat{j} & \\hat{k} \\\\
        \\frac{\\partial}{\\partial x} & \\frac{\\partial}{\\partial y} & \\frac{\\partial}{\\partial z} \\\\
        F_x & F_y & F_z
        \\end{vmatrix}
        $$
        """)

    with st.expander("How to enter equations (SymPy Rules)"):
        st.markdown("""
        This tool uses the SymPy library to parse mathematical expressions. Please follow these rules:
        - **Variables**: Use only `x`, `y`, and `z`.
        - **Constants**: Numerical values like `5`, `-10.5`, etc., are allowed. Avoid using other letters as constants.
        - **Multiplication**: Use the asterisk `*`. For example, `2*x` not `2x`.
        - **Powers**: Use a double asterisk `**`. For example, `x**2` for $x^2$.
        - **Standard Functions**:
            - **Trigonometric**: `sin(x)`, `cos(y)`, `tan(z)`
            - **Inverse Trig**: `asin(x)`, `acos(y)`, `atan(z)`
            - **Hyperbolic**: `sinh(x)`, `cosh(y)`
            - **Exponentials & Logarithms**: `exp(x)` for $e^x$, and `log(x)` for the natural logarithm $\\ln(x)$.
        
        **Example**: To represent the field $\\vec{F} = e^{x} \\cos(y) \\hat{i} - \\ln(z) \\hat{j} + x^3 \\hat{k}$, you would enter:
        - **Fₓ**: `exp(x) * cos(y)`
        - **Fᵧ**: `-log(z)`
        - **F_z**: `x**3`
        """)

    # Button to trigger the visualization
    generate_viz = st.button("Generate Visualization", type="primary")
    
    if generate_viz and fx_str and fy_str and fz_str:
        try:
            # --- SYMBOLIC SETUP ---
            x, y, z = smp.symbols('x y z')
            expr_x = smp.sympify(fx_str)
            expr_y = smp.sympify(fy_str)
            expr_z = smp.sympify(fz_str)

            # Lambdify expressions for numerical evaluation
            fx = lambdify((x, y, z), expr_x, 'numpy')
            fy = lambdify((x, y, z), expr_y, 'numpy')
            fz = lambdify((x, y, z), expr_z, 'numpy')

            # --- GRID GENERATION ---
            x_vals = np.linspace(-2, 2, density)
            y_vals = np.linspace(-2, 2, density)
            z_vals = np.linspace(-2, 2, max(2, density // 2)) # Fewer points on z-axis for clarity
            X, Y, Z = np.meshgrid(x_vals, y_vals, z_vals)
            Xf, Yf, Zf = X.ravel(), Y.ravel(), Z.ravel()

            # --- VECTOR FIELD CALCULATION ---
            U = to_array(fx(Xf, Yf, Zf), Xf)
            V = to_array(fy(Xf, Yf, Zf), Xf)
            W = to_array(fz(Xf, Yf, Zf), Xf)

            # Filter out any NaN values to prevent plotting errors
            mask = ~(np.isnan(U) | np.isnan(V) | np.isnan(W))
            Xf_plot, Yf_plot, Zf_plot = Xf[mask], Yf[mask], Zf[mask]
            U_plot, V_plot, W_plot = U[mask], V[mask], W[mask]

            # --- DISPLAY ORIGINAL EQUATION ---
            components = []
            if expr_x: components.append(f"({latex(expr_x)}) \\hat{{i}}")
            if expr_y: components.append(f"({latex(expr_y)}) \\hat{{j}}")
            if expr_z: components.append(f"({latex(expr_z)}) \\hat{{k}}")
            latex_eqn = "\\vec{F}(x,y,z) = " + " + ".join(components) if components else "\\vec{F}(x,y,z) = \\vec{0}"
            
            st.markdown("---")
            st.markdown("### Original Vector Field Equation")
            st.latex(latex_eqn)

            # --- DIVERGENCE AND CURL CALCULATION ---
            div_F = smp.diff(expr_x, x) + smp.diff(expr_y, y) + smp.diff(expr_z, z)
            curl_x = smp.diff(expr_z, y) - smp.diff(expr_y, z)
            curl_y = smp.diff(expr_x, z) - smp.diff(expr_z, x)
            curl_z = smp.diff(expr_y, x) - smp.diff(expr_x, y)
            
            div_F_func = lambdify((x, y, z), div_F, 'numpy')
            curl_x_func = lambdify((x, y, z), curl_x, 'numpy')
            curl_y_func = lambdify((x, y, z), curl_y, 'numpy')
            curl_z_func = lambdify((x, y, z), curl_z, 'numpy')

            div_vals = to_array(div_F_func(Xf, Yf, Zf), Xf)
            curl_U = to_array(curl_x_func(Xf, Yf, Zf), Xf)
            curl_V = to_array(curl_y_func(Xf, Yf, Zf), Xf)
            curl_W = to_array(curl_z_func(Xf, Yf, Zf), Xf)

            curl_magnitude = np.sqrt(curl_U**2 + curl_V**2 + curl_W**2)

            mask_curl = ~(np.isnan(curl_U) | np.isnan(curl_V) | np.isnan(curl_W))
            Xf_curl, Yf_curl, Zf_curl = Xf[mask_curl], Yf[mask_curl], Zf[mask_curl]
            curl_U_plot, curl_V_plot, curl_W_plot = curl_U[mask_curl], curl_V[mask_curl], curl_W[mask_curl]
            curl_magnitude_plot = curl_magnitude[mask_curl]

            # --- PLOTTING ---
            st.markdown("### Vector Field Visualization")
            fig = go.Figure(data=go.Cone(
                x=Xf_plot, y=Yf_plot, z=Zf_plot,
                u=U_plot, v=V_plot, w=W_plot,
                colorscale='Viridis', sizemode="scaled", sizeref=0.5,
                showscale=True, anchor="tail", colorbar=dict(title="Magnitude"),
                customdata=np.sqrt(U_plot**2 + V_plot**2 + W_plot**2),
                hovertemplate="<b>Position</b>: (%{x:.2f}, %{y:.2f}, %{z:.2f})<br><b>Vector</b>: &lt;%{u:.2f}, %{v:.2f}, %{w:.2f}&gt;<br><b>Magnitude</b>: %{customdata:.3f}<extra></extra>"
            ))
            fig.update_layout(margin=dict(l=10, r=10, t=30, b=10),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              scene=dict(aspectmode='cube',
                                         xaxis=dict(title='X', backgroundcolor="rgba(0,0,0,0)"),
                                         yaxis=dict(title='Y', backgroundcolor="rgba(0,0,0,0)"),
                                         zaxis=dict(title='Z', backgroundcolor="rgba(0,0,0,0)")))
            st.plotly_chart(fig, use_container_width=True)

            div_col, curl_col = st.columns(2)
            
            with div_col:
                st.markdown("### Divergence")
                st.latex(f"\\nabla \\cdot \\vec{{F}} = {latex(div_F)}")
                fig_div = go.Figure(data=go.Scatter3d(
                    x=Xf, y=Yf, z=Zf, mode='markers',
                    marker=dict(size=6, color=div_vals, colorscale='Viridis', colorbar=dict(title="Div")),
                    hovertemplate="<b>Position</b>: (%{x:.2f}, %{y:.2f}, %{z:.2f})<br><b>Divergence</b>: %{marker.color:.3f}<extra></extra>"
                ))
                fig_div.update_layout(title="Divergence Visualization", margin=dict(l=0, r=0, t=40, b=0),
                                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                      scene=dict(aspectmode='cube', xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
                st.plotly_chart(fig_div, use_container_width=True)

            with curl_col:
                st.markdown("### Curl")
                curl_parts = []
                if curl_x: curl_parts.append(f"({latex(curl_x)}) \\hat{{i}}")
                if curl_y: curl_parts.append(f"({latex(curl_y)}) \\hat{{j}}")
                if curl_z: curl_parts.append(f"({latex(curl_z)}) \\hat{{k}}")
                curl_latex = "\\nabla \\times \\vec{{F}} = " + " + ".join(curl_parts) if curl_parts else "\\nabla \\times \\vec{{F}} = \\vec{0}"
                st.latex(curl_latex)
                
                fig_curl = go.Figure(data=go.Cone(
                    x=Xf_curl, y=Yf_curl, z=Zf_curl,
                    u=curl_U_plot, v=curl_V_plot, w=curl_W_plot,
                    colorscale='Viridis', sizemode="scaled", sizeref=0.5,
                    showscale=True, anchor="tail", colorbar=dict(title="Curl"),
                    customdata=curl_magnitude_plot,
                    hovertemplate="<b>Position</b>: (%{x:.2f}, %{y:.2f}, %{z:.2f})<br><b>Curl</b>: &lt;%{u:.2f}, %{v:.2f}, %{w:.2f}&gt;<br><b>|Curl|</b>: %{customdata:.3f}<extra></extra>"
                ))
                fig_curl.update_layout(title="Curl Visualization", margin=dict(l=0, r=0, t=40, b=0),
                                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                       scene=dict(aspectmode='cube',
                                                  xaxis=dict(title='X', backgroundcolor="rgba(0,0,0,0)"),
                                                  yaxis=dict(title='Y', backgroundcolor="rgba(0,0,0,0)"),
                                                  zaxis=dict(title='Z', backgroundcolor="rgba(0,0,0,0)")))
                st.plotly_chart(fig_curl, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.warning("Please check the syntax of your input functions. See the rules expander for help.")
    
    elif generate_viz:
        st.warning("Please fill in all vector field components.")

if __name__ == "__main__":
    main()
