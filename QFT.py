import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from matplotlib.patches import FancyArrow

# Qiskit imports
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, partial_trace
from qiskit.circuit.library import QFT
import plotly.io as pio
pio.renderers.default = "browser"

def get_user_input():
    """Gets the number of qubits and the initial state from the user."""
    while True:
        try:
            num_qubits = int(input("Enter the number of qubits (e.g., 2, 3): "))
            if num_qubits > 0:
                break
            else:
                print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    num_states = 2**num_qubits
    print(f"Number of possible states (N): {num_states}")

    while True:
        try:
            initial_state_decimal = int(input(f"Enter an initial state (an integer from 0 to {num_states - 1}): "))
            if 0 <= initial_state_decimal < num_states:
                break
            else:
                print(f"State must be between 0 and {num_states - 1}.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    return num_qubits, initial_state_decimal

def perform_qft_with_qiskit(initial_state_decimal, num_qubits):
    """Performs QFT on an initial state using Qiskit's simulator."""
    print("\nApplying the Quantum Fourier Transform using Qiskit...")
    circuit = QuantumCircuit(num_qubits)
    binary_string = bin(initial_state_decimal)[2:].zfill(num_qubits)
    for i, bit in enumerate(reversed(binary_string)):
        if bit == '1':
            circuit.x(i)
    circuit.barrier()
    qft_gate = QFT(num_qubits=num_qubits, inverse=False)
    circuit.append(qft_gate, range(num_qubits))
    return Statevector(circuit)

def get_bloch_vector(statevector, qubit_index, num_qubits):
    """Calculates the Bloch vector for a single qubit from the total statevector."""
    pauli_x = np.array([[0, 1], [1, 0]])
    pauli_y = np.array([[0, -1j], [1j, 0]])
    pauli_z = np.array([[1, 0], [0, -1]])
    
    qubits_to_trace_out = list(range(num_qubits))
    qubits_to_trace_out.remove(qubit_index)
    
    reduced_density_matrix = partial_trace(statevector, qubits_to_trace_out)
    
    bx = np.real(np.trace(np.dot(reduced_density_matrix.data, pauli_x)))
    by = np.real(np.trace(np.dot(reduced_density_matrix.data, pauli_y)))
    bz = np.real(np.trace(np.dot(reduced_density_matrix.data, pauli_z)))
    
    return [bx, by, bz]

def create_bloch_sphere_traces(state_vector):
    """Creates the Plotly traces for a single Bloch sphere, vector, and axes."""
    traces = []
    
    # 1. Sphere Surface
    traces.append(go.Surface(
        x=np.outer(np.cos(np.linspace(0, 2*np.pi, 30)), np.sin(np.linspace(0, np.pi, 30))),
        y=np.outer(np.sin(np.linspace(0, 2*np.pi, 30)), np.sin(np.linspace(0, np.pi, 30))),
        z=np.outer(np.ones(30), np.cos(np.linspace(0, np.pi, 30))),
        opacity=0.2,
        colorscale=[[0, '#606060'], [1, '#909090']],
        showscale=False,
        cmin=-1, cmax=1,
    ))

    # 2. State Vector Line and Arrowhead
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
    
    # 3. Internal Axes
    axis_line = dict(color="white", width=1)
    traces.append(go.Scatter3d(x=[-1, 1], y=[0, 0], z=[0, 0], mode='lines', line=axis_line))
    traces.append(go.Scatter3d(x=[0, 0], y=[-1, 1], z=[0, 0], mode='lines', line=axis_line))
    traces.append(go.Scatter3d(x=[0, 0], y=[0, 0], z=[-1, 1], mode='lines', line=axis_line))

    # 4. Axis Labels
    label_style = dict(font=dict(color="white", size=16), xanchor="center", yanchor="middle")
    traces.append(go.Scatter3d(x=[1.1, -1.1, 0, 0, 0, 0], y=[0, 0, 1.1, -1.1, 0, 0], z=[0, 0, 0, 0, 1.1, -1.1],
                               mode='text', text=['|+⟩', '|–⟩', '|i⟩', '|–i⟩', '|0⟩', '|1⟩'], textfont=label_style['font']))

    return traces

def plot_bloch_subplots(state_vectors, title):
    """Creates a figure with multiple Bloch sphere subplots."""
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
        title_text=title,
        height=400,
        width=350 * num_qubits,
        showlegend=False,
        paper_bgcolor="#1e1e1e",
        font_color="white",
        # scene_template="plotly_dark",
        margin=dict(l=10, r=10, b=10, t=80)
    )
    fig.update_scenes(
        xaxis_visible=False, 
        yaxis_visible=False, 
        zaxis_visible=False,
        aspectratio=dict(x=1, y=1, z=1)
    )
    fig.show()

def plot_probability_bar_chart(final_statevector):
    """Visualizes the final state probabilities with a bar chart."""
    print("\nVisualizing the final probability distribution...")
    N = len(final_statevector.data)
    basis_states = np.arange(N)
    probabilities = final_statevector.probabilities()
    phases = np.angle(final_statevector.data)

    fig, ax = plt.subplots(figsize=(12, 6), facecolor='#1e1e1e')
    ax.set_facecolor('#333333')

    bars = ax.bar(basis_states, probabilities, color='#00aaff', edgecolor='black',
                   label='Probability (Amplitude²)')

    ax.set_xlabel('Basis State |y⟩', fontsize=12, color='white')
    ax.set_ylabel('Probability', fontsize=12, color='white')
    ax.set_title('Final State Probability Distribution', fontsize=16, color='white')
    ax.set_xticks(basis_states)
    ax.set_xticklabels([f'|{i}⟩' for i in basis_states], color='white')
    ax.set_ylim(0, max(probabilities) * 1.2 if max(probabilities) > 0 else 0.1)
    
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.show()

def main():
    """Main function to run the simulation."""
    print("--- QFT Simulator with Qiskit and Bloch Spheres ---")
    
    num_qubits, initial_state_decimal = get_user_input()
    binary_string = bin(initial_state_decimal)[2:].zfill(num_qubits)

    # 1. Plot Initial States
    print(f"\nInitial State: |{initial_state_decimal}⟩  =>  Binary: |{binary_string}⟩")
    initial_vectors = [[0, 0, 1] if bit == '0' else [0, 0, -1] for bit in binary_string]
    plot_bloch_subplots(initial_vectors, "Initial Qubit States")

    # 2. Perform QFT
    final_statevector = perform_qft_with_qiskit(initial_state_decimal, num_qubits)

    # 3. Plot Final States
    print("\nCalculating the final state of each individual qubit...")
    final_vectors = [get_bloch_vector(final_statevector, i, num_qubits) for i in range(num_qubits)]
    plot_bloch_subplots(final_vectors, "Final Qubit States After QFT")
    
    # 4. Plot Probability Distribution
    plot_probability_bar_chart(final_statevector)

    print("\nSimulation complete.")

if __name__ == '__main__':
    main()
