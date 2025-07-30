import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Qiskit imports
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace
from qiskit.circuit.library import QFT

# --- Page and UI Configuration ---
st.set_page_config(
    page_title="QFT Simulator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("⚛️ Quantum Fourier Transform (QFT) Simulator")
st.write(
    "This application visualizes the Quantum Fourier Transform on an initial quantum state. "
    "Set the parameters below and run the simulation to see the initial state, the final state on the Bloch spheres, "
    "and the final probability distribution."
)

# --- Parameter Input ---
st.header("1. Simulation Parameters")
col1, col2 = st.columns(2)

with col1:
    num_qubits = st.number_input(
        "Enter the number of qubits:",
        min_value=1, max_value=5, value=2,
        help="The number of qubits in the quantum register. More qubits increase complexity."
    )

num_states = 2**num_qubits
with col2:
    initial_state_decimal = st.number_input(
        f"Enter an initial state (0 to {num_states - 1}):",
        min_value=0, max_value=num_states - 1, value=1,
        help=f"The computational basis state to initialize the system in."
    )

# --- NEW: Expandable Theory and How-To Sections ---
with st.expander("📖 Theory of the Quantum Fourier Transform (QFT)", expanded=False):
    st.write(
        """
        The Quantum Fourier Transform (QFT) is the quantum analogue of the classical Discrete Fourier Transform (DFT). 
        It's a linear transformation on quantum bits that is crucial for many quantum algorithms, most notably Shor's algorithm for factoring and the quantum phase estimation algorithm.
        """
    )
    st.subheader("Definition")
    st.write(
        r"The QFT transforms an orthonormal basis of states $|0\rangle, |1\rangle, \dots, |N-1\rangle$ into another orthonormal basis. "
        r"Its action on a computational basis state $|x\rangle$ is defined as:"
    )
    st.latex(r"\text{QFT}|x\rangle = \frac{1}{\sqrt{N}} \sum_{y=0}^{N-1} e^{2\pi i \frac{xy}{N}} |y\rangle")
    st.write(r"where $N=2^n$ is the dimension of the Hilbert space for an $n$-qubit register.")
    
    st.subheader("Circuit Implementation")
    st.write(
        r"""
        Unlike its classical counterpart, the QFT can be implemented efficiently on a quantum computer. The circuit for an $n$-qubit QFT consists of:
        1. A Hadamard gate on the first qubit.
        2. A series of controlled phase rotation gates.
        3. A final set of SWAP gates to reverse the order of the qubits.
        
        This simulation uses Qiskit's built-in `QFT` object, which constructs this efficient circuit automatically.
        """
    )

with st.expander("💡 How to Use This Simulation", expanded=False):
    st.write("Follow these simple steps to run the simulation:")
    st.markdown(
        """
        1.  **Select Parameters:** Choose the **number of qubits** for the system and the **initial state** (as a decimal number).
        2.  **Run Simulation:** Click the **"Run QFT Simulation"** button.
        3.  **Analyze Results:** Observe the three plots that are generated.
        """
    )
    st.subheader("Interpreting the Plots")
    st.markdown(
        """
        - **Initial/Final Qubit States:** These Bloch spheres show the state of *each individual qubit* before and after the QFT. For an initial basis state, each qubit is either $|0\rangle$ (vector points up) or $|1\rangle$ (vector points down). After the QFT, the qubits become entangled and are in a superposition. The yellow vector shows the state of each qubit after tracing out all others. If the vector is inside the sphere, it indicates the qubit is in a mixed state.
        
        - **Final Probability Distribution:** This bar chart shows the probability of measuring the *entire system* in each of the possible basis states. A key result of applying the QFT to a single basis state is a final state that is an equal superposition of all basis states. Therefore, you should see that all bars have an equal probability of $1/N$.
        """
    )


# --- Core Qiskit and Plotting Functions ---

def perform_qft_with_qiskit(initial_state_decimal, num_qubits):
    """Performs QFT on an initial state using Qiskit's simulator."""
    circuit = QuantumCircuit(num_qubits)
    binary_string = bin(initial_state_decimal)[2:].zfill(num_qubits)
    # Initialize the state
    for i, bit in enumerate(reversed(binary_string)):
        if bit == '1':
            circuit.x(i)
    circuit.barrier()
    # Apply QFT
    qft_gate = QFT(num_qubits=num_qubits, inverse=False)
    circuit.append(qft_gate, range(num_qubits))
    return Statevector(circuit)

def get_bloch_vector(statevector, qubit_index, num_qubits):
    """Calculates the Bloch vector for a single qubit from the total statevector."""
    pauli_x = np.array([[0, 1], [1, 0]])
    pauli_y = np.array([[0, -1j], [1j, 0]])
    pauli_z = np.array([[1, 0], [0, -1]])
    
    qubits_to_trace_out = list(range(num_qubits))
    if num_qubits > 1:
        qubits_to_trace_out.remove(qubit_index)
    
    reduced_density_matrix = partial_trace(statevector, qubits_to_trace_out)
    
    bx = np.real(np.trace(reduced_density_matrix.data @ pauli_x))
    by = np.real(np.trace(reduced_density_matrix.data @ pauli_y))
    bz = np.real(np.trace(reduced_density_matrix.data @ pauli_z))
    
    return [bx, by, bz]

def create_bloch_sphere_traces(state_vector):
    """Creates the Plotly traces for a single Bloch sphere."""
    traces = []
    
    # Sphere Surface
    traces.append(go.Surface(
        x=np.outer(np.cos(np.linspace(0, 2*np.pi, 30)), np.sin(np.linspace(0, np.pi, 30))),
        y=np.outer(np.sin(np.linspace(0, 2*np.pi, 30)), np.sin(np.linspace(0, np.pi, 30))),
        z=np.outer(np.ones(30), np.cos(np.linspace(0, np.pi, 30))),
        opacity=0.2,
        colorscale=[[0, '#606060'], [1, '#909090']],
        showscale=False, cmin=-1, cmax=1,
    ))
    # State Vector
    traces.append(go.Scatter3d(
        x=[0, state_vector[0]], y=[0, state_vector[1]], z=[0, state_vector[2]],
        mode='lines', line=dict(color='#FFFF00', width=8)
    ))
    traces.append(go.Cone(
        x=[state_vector[0]], y=[state_vector[1]], z=[state_vector[2]],
        u=[state_vector[0]], v=[state_vector[1]], w=[state_vector[2]],
        sizemode="absolute", sizeref=0.1, showscale=False,
        colorscale=[[0, '#FFFF00'], [1, '#FFFF00']], anchor="tip"
    ))
    # Axes
    axis_line = dict(color="white", width=1)
    traces.extend([
        go.Scatter3d(x=[-1.1, 1.1], y=[0, 0], z=[0, 0], mode='lines', line=axis_line),
        go.Scatter3d(x=[0, 0], y=[-1.1, 1.1], z=[0, 0], mode='lines', line=axis_line),
        go.Scatter3d(x=[0, 0], y=[0, 0], z=[-1.1, 1.1], mode='lines', line=axis_line)
    ])
    # Axis Labels
    label_style = dict(font=dict(color="white", size=20), xanchor="center", yanchor="middle")
    traces.append(go.Scatter3d(
        x=[1.3, -1.3, 0, 0, 0, 0], y=[0, 0, 1.3, -1.3, 0, 0], z=[0, 0, 0, 0, 1.3, -1.3],
        mode='text', text=['|+⟩', '|-⟩', '|i⟩', '|-i⟩', '|0⟩', '|1⟩'],
        textfont=label_style['font']
    ))
    return traces

def plot_bloch_subplots(state_vectors, title):
    """Creates a Plotly figure with multiple Bloch sphere subplots."""
    num_qubits = len(state_vectors)
    fig = make_subplots(
        rows=1, cols=num_qubits,
        specs=[[{'type': 'surface'}] * num_qubits],
        subplot_titles=[f'Qubit {i}' for i in range(num_qubits)]
    )
    for i, vec in enumerate(state_vectors):
        traces = create_bloch_sphere_traces(vec)
        for trace in traces:
            fig.add_trace(trace, row=1, col=i+1)
            
    fig.update_layout(
        title_text=title, height=400, showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)', # Make the overall plot background transparent
        font_color="white",
        margin=dict(l=10, r=10, b=10, t=80)
    )
    fig.update_scenes(
        xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
        aspectratio=dict(x=1, y=1, z=1),
        bgcolor='rgba(0,0,0,0)' # Make the 3D scene background transparent
    )
    return fig

def plot_probability_bar_chart_plotly(final_statevector):
    """Visualizes the final state probabilities with a Plotly bar chart."""
    N = len(final_statevector.data)
    basis_states = [f'|{i}⟩' for i in range(N)]
    probabilities = final_statevector.probabilities()

    fig = go.Figure(data=[go.Bar(
        x=basis_states, y=probabilities,
        marker_color='#00aaff',
        text=[f'{p:.3f}' for p in probabilities],
        textposition='outside',
        textfont=dict(color='white')
    )])
    fig.update_layout(
        title_text='Final State Probability Distribution',
        xaxis_title='Basis State |y⟩', yaxis_title='Probability',
        plot_bgcolor='#333333', 
        paper_bgcolor='rgba(0,0,0,0)', # Make the overall plot background transparent
        font_color="white",
        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.3)'),
        yaxis_range=[0, max(probabilities) * 1.3 if max(probabilities) > 0 else 0.1]
    )
    return fig

# --- Main Application Logic ---
st.markdown("---")
if st.button("🚀 Run QFT Simulation", type="primary"):
    binary_string = bin(initial_state_decimal)[2:].zfill(num_qubits)

    with st.spinner("Preparing initial state..."):
        st.header("2. Initial Qubit States")
        st.markdown(f"### Initial State: $|{initial_state_decimal}⟩ \\rightarrow$ Binary: $|{binary_string}⟩$")
        initial_vectors = [[0, 0, 1] if bit == '0' else [0, 0, -1] for bit in binary_string]
        fig_initial = plot_bloch_subplots(initial_vectors, "Initial Qubit States on the Bloch Sphere")
        st.plotly_chart(fig_initial, use_container_width=True)

    with st.spinner("Applying Quantum Fourier Transform and calculating final states..."):
        # Perform QFT
        final_statevector = perform_qft_with_qiskit(initial_state_decimal, num_qubits)
        
        # Plot Final Bloch States
        st.header("3. Final Qubit States After QFT")
        final_vectors = [get_bloch_vector(final_statevector, i, num_qubits) for i in range(num_qubits)]
        fig_final = plot_bloch_subplots(final_vectors, "Final Qubit States on the Bloch Sphere")
        st.plotly_chart(fig_final, use_container_width=True)

    with st.spinner("Visualizing final probabilities..."):
        # Plot Probability Distribution
        st.header("4. Final Probability Distribution")
        fig_bar = plot_probability_bar_chart_plotly(final_statevector)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.success("Simulation complete!")
else:
    st.info("Click the button to run the simulation with the specified parameters.")