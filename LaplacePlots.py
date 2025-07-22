import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import sympy as sp
from scipy.integrate import quad, IntegrationWarning
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=IntegrationWarning)

pio.renderers.default = "browser"

def calculate_Cn(n, a, b, V0_func):
    """Calculate Fourier coefficients Cn for V_nought(y)"""
    def integrand(y):
        return V0_func(0, y) * np.sin(n * np.pi * (y + a) / (2 * a))
    
    result, _ = quad(integrand, -a, a)
    return (2 / (a * np.sinh(n * np.pi * b / a))) * result

def parse_user_function(user_input, variables, params={}, prompted={}):
    if user_input.lower() == 'nan':
        return None
    try:
        # Handle special functions
        if '(' in user_input and ')' in user_input:
            func_name = user_input.split('(')[0].strip()
            var_name = user_input.split('(')[1].split(')')[0].strip()
            
            if func_name == 'V_nought':
                def v_nought(x, y):
                    V0 = prompted.get('V0', 5.0)
                    # Step function for testing
                    return V0 if -params['a']/2 < y < params['a']/2 else 0
                
                if 'V0' not in prompted:
                    V0 = float(input("Enter value for V0 in V_nought(y): "))
                    prompted['V0'] = V0
                    
                return v_nought
        
        expr = sp.sympify(user_input)
        all_symbols = expr.free_symbols
        var_symbols = set(sp.symbols([str(v) for v in variables]))
        param_symbols = set(sp.symbols(list(params.keys())))
        other_symbols = all_symbols - var_symbols - param_symbols
        local_params = dict(params)
        for sym in other_symbols:
            sym_str = str(sym)
            if sym_str in prompted:
                local_params[sym_str] = prompted[sym_str]
            else:
                val = input(f"Enter value for constant '{sym_str}': ")
                try:
                    local_params[sym_str] = float(val)
                except ValueError:
                    print(f"Invalid value for '{sym_str}', using 0.")
                    local_params[sym_str] = 0.0
                prompted[sym_str] = local_params[sym_str]
        expr_sub = expr.subs(local_params)
        func = sp.lambdify(variables, expr_sub, modules="numpy")
        return func
    except Exception as e:
        print(f"Error parsing function '{user_input}': {e}")
        return None

def solve_laplace_complete(a, b, nx, ny, terms, boundary_funcs):
    x = np.linspace(-2*b, 2*b, nx)
    y = np.linspace(-2*a, 2*a, ny)
    X, Y = np.meshgrid(x, y)
    V = np.zeros_like(X)
    V0 = None
    latex_eqn = ""
    parameter_desc = ""

    V_x_minus, V_x_plus, V_y_minus, V_y_plus, V_x0, V_y0 = boundary_funcs

    # Use scaling to prevent overflow
    scale = min(a, b)
    X_scaled = X/scale
    Y_scaled = Y/scale
    a_scaled = a/scale
    b_scaled = b/scale

    # Case 1: V_nought at x=-b
    if V_x_minus is not None and callable(V_x_minus):
        for n in range(1, terms + 1):
            Cn = calculate_Cn(n, a, b, V_x_minus)
            sinh_term = np.sinh(n * np.pi * (X_scaled + b_scaled) / (2 * a_scaled))
            sin_term = np.sin(n * np.pi * (Y + a) / (2 * a))
            
            term = Cn * sinh_term * sin_term
            term = np.clip(term, -1e15, 1e15)
            V += term
        
        latex_eqn = r"V(x,y) = \sum_{n=1}^{\infty} C_n \sinh\left(\frac{n\pi(x+b)}{2a}\right)\sin\left(\frac{n\pi(y+a)}{2a}\right)"
        parameter_desc = r"where $C_n = \frac{2}{a\sinh(n\pi b/a)}\int_{-a}^a V_0(y)\sin\left(\frac{n\pi(y+a)}{2a}\right)dy$"
        
        # Scale back the solution
        V = np.clip(V, -1e15, 1e15)
    
    # Case 2: Center line solution with V_nought
    elif V_x0 is not None:
        for n in range(1, terms + 1):
            Cn = calculate_Cn(n, a, b, V_x0)
            term = Cn * np.sin(n * np.pi * Y / a) * np.exp(-n * np.pi * np.abs(X) / a)
            V += np.clip(term, -1e15, 1e15)
        
        latex_eqn = r"V(x,y) = \sum_{n=1}^{\infty} C_n \sin(n\pi y/a)e^{-n\pi|x|/a}"
        parameter_desc = r"where $C_n$ are the Fourier coefficients"
    
    # Case 3: Standard boundary value problem
    else:
        if V_x_minus is not None and V_x_plus is not None:
            y_test = 0
            v_minus = V_x_minus(-b, y_test) if callable(V_x_minus) else V_x_minus
            v_plus = V_x_plus(b, y_test) if callable(V_x_plus) else V_x_plus
            if v_minus is not None and v_plus is not None and abs(v_minus - v_plus) < 1e-10:
                V0 = v_minus
        
        if V0 is not None:
            for n in range(1, 2*terms, 2):
                cosh_term = np.clip(np.cosh(n * np.pi * X_scaled / a_scaled), -1e15, 1e15)
                denom = np.clip(np.cosh(n * np.pi * b_scaled / a_scaled), 1e-15, 1e15)
                V += (4*V0/np.pi) * (1/n) * (cosh_term / denom) * np.sin(n * np.pi * Y_scaled)
            
            latex_eqn = r"V(x,y) = \frac{4V_0}{\pi} \sum_{n=1,3,5,...} \frac{1}{n} \frac{\cosh(n\pi x/a)}{\cosh(n\pi b/a)} \sin(n\pi y/a)"
            parameter_desc = f"where V₀ = {V0}"

    return X, Y, V, latex_eqn, parameter_desc

# Plot the potential surface
def plot_surface(X, Y, V):
    fig = go.Figure(data=[go.Surface(z=V, x=X, y=Y)])
    fig.update_layout(
        title="Potential Surface V(x, y)",
        scene=dict(
            xaxis_title='x',
            yaxis_title='y',
            zaxis_title='V(x, y)'
        )
    )
    fig.show()

# Main
if __name__ == "__main__":
    print("=== Laplace Equation Solver (General Boundary Conditions) ===")
    try:
        # Domain and grid
        a = float(input("Enter value for a (y-dimension length): "))
        b = float(input("Enter value for b (x-dimension length): "))
        nx = int(input("Enter grid points in x-direction (e.g., 50): "))
        ny = int(input("Enter grid points in y-direction (e.g., 50): "))
        terms = int(input("Enter number of Fourier terms (e.g., 50): "))

        # All boundary conditions
        print("\n--- Enter boundary conditions (enter 'NaN' to skip) ---")
        V_x_minus_str = input("V(x=-b, y) = ") or "NaN"
        V_x_plus_str = input("V(x=b, y) = ") or "NaN"
        V_y_minus_str = input("V(x, y=-a) = ") or "NaN"
        V_y_plus_str = input("V(x, y=a) = ") or "NaN"
        V_x0_str = input("V(x=0, y) = ") or "NaN"
        V_y0_str = input("V(x, y=0) = ") or "NaN"

        # Parse functions with shared prompted constants
        x, y = sp.symbols('x y')
        params = {'a': a, 'b': b}
        prompted_constants = {}
        
        boundary_funcs = [
            parse_user_function(s, (x, y), params, prompted_constants)
            for s in [V_x_minus_str, V_x_plus_str, V_y_minus_str, 
                     V_y_plus_str, V_x0_str, V_y0_str]
        ]

        # Solve with all boundary conditions
        X, Y, V, latex_eqn, parameter_desc = solve_laplace_complete(a, b, nx, ny, terms, boundary_funcs)

        fig = go.Figure(data=[
            go.Surface(
                z=V, 
                x=X, 
                y=Y,
                showscale=True,
                colorbar=dict(title="Potential V"),
                contours=dict(
                    x=dict(show=True, color='lightgray', width=1),
                    y=dict(show=True, color='lightgray', width=1),
                    z=dict(show=True, color='lightgray', width=1)
                ),
                lighting=dict(
                    ambient=0.8,
                    diffuse=0.8,
                ),
            )
        ])

        fig.update_layout(
            title=dict(
                text=(f"$${latex_eqn}$$<br>" + 
                      r"$\lambda_n = \frac{n\pi}{2b}$, " + 
                      r"$\mu_m = \frac{m\pi}{2a}$<br>" +
                      parameter_desc),
                x=0.5,
                y=0.95,
                xanchor="center",
                yanchor="top",
                font=dict(size=16)
            ),
            scene=dict(
                xaxis=dict(
                    range=[-2*b, 2*b], 
                    title='x',
                    gridcolor='lightgray',
                    showgrid=True,
                    zeroline=True,
                    zerolinecolor='gray'
                ),
                yaxis=dict(
                    range=[-2*a, 2*a], 
                    title='y',
                    gridcolor='lightgray',
                    showgrid=True,
                    zeroline=True,
                    zerolinecolor='gray'
                ),
                zaxis=dict(
                    title='V(x,y)',
                    gridcolor='lightgray',
                    showgrid=True,
                    zeroline=True,
                    zerolinecolor='gray'
                ),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
            ),
            width=1000,
            height=800,
            margin=dict(t=100)  # Increased top margin for equation
        )
        fig.show()

    except Exception as e:
        print(f"An error occurred: {e}")
        raise  # Show full traceback for debugging