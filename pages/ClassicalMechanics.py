import streamlit as st
import streamlit.components.v1 as components
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SimuPhys - Classical Mechanics",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

# --- INJECT CUSTOM CSS ---
# This CSS hides the sidebar and its control button completely on this page.
hide_sidebar_style = """
            <style>
                /* Hide default Streamlit header and footer */
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}

                /* Hide the sidebar and the collapse button */
                [data-testid="stSidebar"],
                [data-testid="collapsedControl"] {
                    display: none !important;
                }

                /* Remove all padding and margin from the main block container */
                .block-container,
                [data-testid="stVerticalBlock"],
                .st-emotion-cache-1jicfl2, 
                .st-emotion-cache-zy6yx3 {
                    padding: 0 !important;
                    margin: 0 !important;
                }
                
                .st-emotion-cache-gsx7k2 {
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


# --- LOAD THE CLASSICAL MECHANICS PAGE HTML ---
script_dir = os.path.dirname(os.path.abspath(__file__))
html_file_path = os.path.join(script_dir, '..', 'classical_mechanics_page.html')

try:
    with open(html_file_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), scrolling=False)
except FileNotFoundError:
    st.error("Error: classical_mechanics_page.html not found. Make sure it is in the root directory of your project.")

