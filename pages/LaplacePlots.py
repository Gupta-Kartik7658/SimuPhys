import numpy as np
import plotly.graph_objects as go
import streamlit as st
import sympy as sp
from scipy.integrate import quad, IntegrationWarning
import warnings

# Suppress warnings from the integration function
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=IntegrationWarning)


def calculate_Cn(n, a, b, V0_func):
    """Calculate Fourier coefficients Cn for V_nought(y)"""
    def integrand(y):
        return V0_func(0, y) * np.sin(n * np.pi * (y + a) / (2 * a))
    
    result, _ = quad(integrand, -a, a)
    return (2 / (a * np.sinh(n * np.pi * b / a))) * result

def parse_user_function(user_input, variables, params, all_constants):
    """
    Parses a user-defined string into a callable function.
    """
    if not user_input or user_input.lower() == 'nan':
        return None
    try:
        if 'V_nought' in user_input:
            def v_nought(x, y):
                V0 = all_constants.get('V0', 5.0) 
                a_val = params.get('a', 1.0)
                return V0 if -a_val / 2 < y < a_val / 2 else 0
            return v_nought

        expr = sp.sympify(user_input)
        local_params = {**params, **all_constants}
        expr_sub = expr.subs(local_params)
        func = sp.lambdify(variables, expr_sub, modules="numpy")
        return func
    except Exception as e:
        st.error(f"Error parsing function '{user_input}': {e}")
        return None

def find_all_symbols(str_list):
    """Helper function to find all custom constants from boundary condition strings."""
    detected_symbols = set()
    standard_vars = {'x', 'y', 'a', 'b'}
    for user_input in str_list:
        if user_input and user_input.lower() != 'nan':
            try:
                if 'V_nought' in user_input:
                    detected_symbols.add('V0')
                    continue
                
                expr = sp.sympify(user_input)
                symbols = expr.free_symbols
                for sym in symbols:
                    sym_str = str(sym)
                    if sym_str not in standard_vars:
                        detected_symbols.add(sym_str)
            except (sp.SympifyError, TypeError):
                pass
    return detected_symbols

def solve_laplace_complete(a, b, nx, ny, terms, boundary_funcs):
    """
    This function's logic is corrected to handle the standard boundary value case properly.
    """
    x = np.linspace(-b, b, nx)
    y = np.linspace(-a, a, ny)
    X, Y = np.meshgrid(x, y)
    V = np.zeros_like(X)
    V0_const = None
    latex_eqn = ""
    parameter_desc = ""

    V_x_minus_func, V_x_plus_func, V_y_minus_func, V_y_plus_func, V_x0_func, V_y0_func = boundary_funcs
    
    # Heuristic check for the classic V0 case
    v_minus_val = V_x_minus_func( -b, 0) if callable(V_x_minus_func) else V_x_minus_func
    v_plus_val = V_x_plus_func(b, 0) if callable(V_x_plus_func) else V_x_plus_func
    
    y_minus_is_zero = np.allclose(V_y_minus_func(-b, -a) if callable(V_y_minus_func) else V_y_minus_func, 0)
    y_plus_is_zero = np.allclose(V_y_plus_func(b, a) if callable(V_y_plus_func) else V_y_plus_func, 0)

    # Case 3: Standard boundary value problem (cosh solution)
    if v_minus_val is not None and v_plus_val is not None and np.allclose(v_minus_val, v_plus_val) and y_minus_is_zero and y_plus_is_zero:
        V0_const = v_minus_val
        for n in range(1, 2 * terms, 2):  # Sum over odd n
            cosh_arg_x = n * np.pi * X / a 
            cosh_arg_b = n * np.pi * b / a
            
            cosh_term = np.cosh(np.clip(cosh_arg_x, -700, 700))
            denom = np.cosh(np.clip(cosh_arg_b, -700, 700))
            
            if np.isinf(denom) or denom < 1e-9:
                V_term = 0
            else:
                V_term = (4 * V0_const / np.pi) * (1 / n) * (cosh_term / denom) * np.sin(n * np.pi * Y / a)
            
            V += V_term
        latex_eqn = r"V(x,y) = \frac{4V_0}{\pi} \sum_{n=1,3,5,...} \frac{1}{n} \frac{\cosh(n\pi x/a)}{\cosh(n\pi b/a)} \sin(n\pi y/a)"
        parameter_desc = f"Solution for $V(x, y=\pm a)=0$ and $V(\pm b, y)=V_0$, with $V_0 = {V0_const:.2f}$"
    else:
        if callable(V_x0_func) and "v_nought" in V_x0_func.__name__:
            for n in range(1, terms + 1):
                Cn = calculate_Cn(n, a, b, V_x0_func)
                term = Cn * np.sin(n * np.pi * Y / a) * np.exp(-n * np.pi * np.abs(X) / a)
                V += term
            latex_eqn = r"V(x,y) = \sum_{n=1}^{\infty} C_n \sin(n\pi y/a)e^{-n\pi|x|/a}"
            parameter_desc = r"Solution for potential on center line"
        else:
            latex_eqn = r"No specific solution implemented for this combination of boundary conditions."
            parameter_desc = r"The plot may be empty or show a trivial solution."


    return X, Y, V, latex_eqn, parameter_desc


# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("⚡️ 2D Laplace Equation Solver")
st.write("This tool solves the Laplace equation $\nabla^2V = 0$ in a 2D rectangular domain with specified boundary conditions.")

# --- Inputs ---
st.header("1. Domain and Simulation Parameters")
c1, c2, c3 = st.columns(3)
with c1:
    a = st.number_input("a (y-dimension half-length)", min_value=0.1, value=1.0, step=0.1)
    b = st.number_input("b (x-dimension half-length)", min_value=0.1, value=1.5, step=0.1)
with c2:
    nx = st.number_input("Grid points in x-direction", min_value=10, value=100, step=10)
    ny = st.number_input("Grid points in y-direction", min_value=10, value=100, step=10)
with c3:
    terms = st.number_input("Number of Fourier terms", min_value=1, max_value=200, value=50, step=5)

st.header("2. Boundary Conditions")
st.markdown("Enter a function of `x` or `y`, a constant, `V_nought(y)` for a step function, or `NaN` to ignore.")
r1c1, r1c2, r1c3 = st.columns(3)
with r1c1:
    V_x_minus_str = st.text_input(label="$V(x=-b, y)$", value="V0")
with r1c2:
    V_x0_str = st.text_input(label="$V(x=0, y)$", value="NaN")
with r1c3:
    V_x_plus_str = st.text_input(label="$V(x=b, y)$", value="V0")

r2c1, r2c2, r2c3 = st.columns(3)
with r2c1:
    V_y_minus_str = st.text_input(label="$V(x, y=-a)$", value="0")
with r2c2:
    V_y0_str = st.text_input(label="$V(x, y=0)$", value="NaN")
with r2c3:
    V_y_plus_str = st.text_input(label="$V(x, y=a)$", value="0")

# --- Dynamic Constant Inputs ---
st.header("3. Custom Constants")
all_strs = [V_x_minus_str, V_x_plus_str, V_y_minus_str, V_y_plus_str, V_x0_str, V_y0_str]
detected_symbols = find_all_symbols(all_strs)
prompted_constants = {}

if detected_symbols:
    st.write("Please provide values for the detected constants in your formulas:")
    num_cols = min(len(detected_symbols), 4)
    const_cols = st.columns(num_cols)
    for i, symbol in enumerate(detected_symbols):
        with const_cols[i % num_cols]:
            prompted_constants[symbol] = st.number_input(f"Value for {symbol}", value=5.0, format="%.2f", key=f"const_{symbol}")
else:
    st.info("No custom constants detected. Use variables like 'V0', 'k', etc. in the formulas above to add them.")

st.markdown("---")

# --- NEW: Expandable Theory and How-To Sections ---
with st.expander("📖 Theory: Solving Laplace's Equation", expanded=False):
    st.subheader("The Laplace Equation")
    st.write("The 2D Laplace equation is a fundamental partial differential equation that describes the behavior of potentials (e.g., electric, gravitational, temperature) in a steady state and in a region with no sources. It is written as:")
    st.latex(r"\nabla^2V = \frac{\partial^2V}{\partial x^2} + \frac{\partial^2V}{\partial y^2} = 0")

    st.subheader("Method of Separation of Variables")
    st.write(
        """
        A powerful technique to solve this equation on a rectangular domain is the method of separation of variables.
        1.  **Assume a solution form:** We assume the potential $V(x, y)$ can be written as a product of two functions, each depending on only one variable: $V(x, y) = X(x)Y(y)$.
        2.  **Separate the equation:** Substituting this into the Laplace equation and rearranging gives:
        """
    )
    st.latex(r"\frac{1}{X(x)}\frac{d^2X}{dx^2} = -\frac{1}{Y(y)}\frac{d^2Y}{dy^2}")
    st.write(
        """
        Since the left side depends only on $x$ and the right side depends only on $y$, both must be equal to the same constant, which we'll call $-k^2$.
        3.  **Solve the ODEs:** This separation yields two ordinary differential equations (ODEs):
        """
    )
    st.latex(r"\frac{d^2X}{dx^2} - k^2X = 0 \quad \text{and} \quad \frac{d^2Y}{dy^2} + k^2Y = 0")
    st.write(
        r"The general solutions to these are $X(x) = A e^{kx} + B e^{-kx}$ and $Y(y) = C \cos(ky) + D \sin(ky)$."
    )
    st.subheader("Applying Boundary Conditions")
    st.write(
        r"""
        The arbitrary constants $A, B, C, D$ and the separation constant $k$ are determined by the specific boundary conditions of the problem. 
        Applying the conditions often leads to a solution that is an infinite sum (a **Fourier series**) of these product solutions, which allows us to match the potential values on all four sides of the rectangle.
        """
    )


with st.expander("💡 How to Use This Simulation", expanded=False):
    st.markdown(
        """
        1.  **Define Domain and Quality:**
            - Set **`a`** and **`b`** to define the rectangular domain from `[-b, b]` in x and `[-a, a]` in y.
            - **`Grid points`** and **`Fourier terms`** control the resolution and accuracy of the solution. Higher values are more accurate but slower.

        2.  **Set Boundary Conditions:**
            - For each of the six lines, enter the potential $V$. This can be a constant (`5.0`), a function (`10*sin(pi*y/a)`), the special step function `V_nought(y)`, or `NaN` to leave it undefined.

        3.  **Define Constants:**
            - If you use a symbolic constant in a formula (like `V0`), an input box for it will automatically appear in this section.

        4.  **Solve and Analyze:**
            - Click the **"Solve and Plot"** button. The app will calculate the potential and display the resulting 3D surface below, along with the specific mathematical formula used for the solution.
        """
    )


# --- Solve and Plot Button ---
if st.button("Solve and Plot", type="primary"):
    with st.spinner("Parsing functions and solving equation..."):
        x_sym, y_sym = sp.symbols('x y')
        params = {'a': a, 'b': b}
        
        boundary_funcs_parsed = []
        for s in all_strs:
            try:
                val = float(s)
                boundary_funcs_parsed.append(val)
            except (ValueError, TypeError):
                boundary_funcs_parsed.append(
                    parse_user_function(s, (x_sym, y_sym), params, prompted_constants)
                )

        X, Y, V, latex_eqn, parameter_desc = solve_laplace_complete(a, b, nx, ny, terms, boundary_funcs_parsed)

        # --- Results Display ---
        st.header("4. Results")
        st.markdown("---")

        if latex_eqn:
            st.markdown(f"**Solution:** $${latex_eqn}$$")
        if parameter_desc:
            st.markdown(f"*{parameter_desc}*")

        fig = go.Figure(data=[go.Surface(z=V, x=X, y=Y, colorbar=dict(title="V"), cmin=np.nanmin(V), cmax=np.nanmax(V))])
        
        fig.update_layout(
            title="Potential Surface V(x, y)",
            scene=dict(
                xaxis_title='x',
                yaxis_title='y',
                zaxis_title='V(x,y)',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
            ),
            height=700,
            margin=dict(t=50, b=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Click the button to solve the equation with the specified parameters.")