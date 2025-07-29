import streamlit as st
import streamlit.components.v1 as components
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SimuPhys - Explore Simulations",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="auto" 
)

# --- INJECT CUSTOM CSS ---
# This CSS ensures the page is full-width but keeps the sidebar available for navigation.
robust_style_with_sidebar = """
            <style>
                /* Hide default Streamlit header and footer */
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}

                /* Completely hide the sidebar on the homepage */
                [data-testid="stSidebar"] {
                    display: none;
                }
                
                /* Remove all padding and margin from the main block container */
                .block-container {
                    padding: 0 !important;
                    margin: 0 !important;
                }
                
                [data-testid="stVerticalBlock"] {
                    gap: 0 !important;
                }
                
                iframe {
                    display: block;
                    width: 100%; /* Use 100% instead of 100vw to respect the sidebar */
                    height: 100vh;
                    border: none;
                }
            </style>
            """
st.markdown(robust_style_with_sidebar, unsafe_allow_html=True)


# --- LOAD THE SIMULATIONS PAGE HTML ---
script_dir = os.path.dirname(os.path.abspath(__file__))
html_file_path = os.path.join(script_dir, '..', 'simulations_page.html')

try:
    with open(html_file_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), scrolling=False)
except FileNotFoundError:
    st.error("Error: simulations_page.html not found. Make sure it is in the root directory of your project.")

