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
# This CSS ensures the page is full-width and the sidebar is available for navigation.
force_full_width_style = """
            <style>
                /* Hide default Streamlit header and footer */
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}

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
st.markdown(force_full_width_style, unsafe_allow_html=True)


# --- LOAD THE SIMULATIONS PAGE HTML ---
# This assumes the 'pages' folder is at the same level as 'simulations_page.html'
# A more robust way is to navigate up one directory.
script_dir = os.path.dirname(os.path.abspath(__file__))
html_file_path = os.path.join(script_dir, '..', 'simulations_page.html')

try:
    with open(html_file_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), scrolling=False)
except FileNotFoundError:
    st.error("Error: simulations_page.html not found. Make sure it is in the root directory of your project.")

