import streamlit as st
import streamlit.components.v1 as components
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SimuPhys - Quantum Mechanics",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

# --- INJECT CUSTOM CSS ---
# This CSS hides the sidebar and its control button completely on this page.
hide_sidebar_style = """
            <style>
                /* Hide default Streamlit elements */
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}

                /* Completely hide the sidebar */
                [data-testid="stSidebar"] {
                    display: none;
                }

                .block-container {
                    padding: 0 !important;
                    margin: 0 !important;
                }
                
                [data-testid="stVerticalBlock"] {
                    gap: 0 !important;
                }

                iframe {
                    display: block;
                    width: 100vw;
                    height: 100vh;
                    border: none;
                }
            </style>
            """
st.markdown(hide_sidebar_style, unsafe_allow_html=True)


# --- LOAD THE QUANTUM MECHANICS PAGE HTML ---
script_dir = os.path.dirname(os.path.abspath(__file__))
html_file_path = os.path.join(script_dir, '..', 'quantum_mechanics_page.html')

try:
    with open(html_file_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), scrolling=False)
except FileNotFoundError:
    st.error("Error: quantum_mechanics_page.html not found. Make sure it is in the root directory of your project.")

