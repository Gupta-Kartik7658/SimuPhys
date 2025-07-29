import streamlit as st
import streamlit.components.v1 as components
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SimuPhys - Modern Physics Simulations",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

# --- INJECT CUSTOM CSS ---
# This new CSS block uses stable `data-testid` selectors to be version-proof.
robust_style = """
            <style>
                /* Hide default Streamlit elements */
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}

                /* Completely hide the sidebar on the homepage */
                [data-testid="stSidebar"] {
                    display: none;
                }

                /* Target the main container and remove its padding */
                .block-container {
                    padding: 0 !important;
                    margin: 0 !important;
                }
                
                /* This is the key to removing the top gap */
                [data-testid="stVerticalBlock"] {
                    gap: 0 !important;
                }

                /* Ensure the iframe itself takes up the full space */
                iframe {
                    display: block;
                    width: 100vw;
                    height: 100vh;
                    border: none;
                }
            </style>
            """
st.markdown(robust_style, unsafe_allow_html=True)


# --- LOAD THE SELF-CONTAINED HOMEPAGE ---
script_dir = os.path.dirname(os.path.abspath(__file__))
html_file_path = os.path.join(script_dir, 'homepage.html')

try:
    with open(html_file_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), scrolling=False)
except FileNotFoundError:
    st.error("Error: homepage.html not found. Please make sure it is in the same directory as app.py.")

