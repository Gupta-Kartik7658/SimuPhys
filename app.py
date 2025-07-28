import streamlit as st
import streamlit.components.v1 as components
import os

# --- PAGE CONFIGURATION ---
# Set layout to "wide" and the sidebar to "collapsed" by default.
st.set_page_config(
    page_title="SimuPhys - Modern Physics Simulations",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

# --- INJECT CUSTOM CSS ---
# This CSS is the definitive fix for removing all Streamlit's default padding/margin and hiding the sidebar.
force_full_width_style = """
            <style>
                /* Hide default Streamlit elements */
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                stSidebar st-emotion-cache-mn9soh e1quxfqw0 {display: None;, visibility: hidden;}
                  

                /* Completely hide the sidebar on the homepage */
                [data-testid="stSidebar"] {
                    display: none;
                }
                [data-testid="collapsedControl"] {
                    display: none
                }

                /* Remove all padding and margin from the main block container and its children */
                .block-container,
                [data-testid="stVerticalBlock"],
                .st-emotion-cache-1jicfl2, 
                .st-emotion-cache-zy6yx3 {
                    padding: 0 !important;
                    margin: 0 !important;
                }
                
                /* This targets the top-level container of the main page */
                .st-emotion-cache-gsx7k2 {
                    gap: 0 !important; /* Removes the vertical gap between elements */
                }
                
                /* Ensure the iframe itself takes up the full space of its container */
                iframe {
                    display: block;
                    width: 100vw; /* Full viewport width */
                    height: 100vh; /* Full viewport height */
                    border: none;
                }
            </style>
            """
st.markdown(force_full_width_style, unsafe_allow_html=True)


# --- LOAD THE SELF-CONTAINED HOMEPAGE ---
script_dir = os.path.dirname(os.path.abspath(__file__))
html_file_path = os.path.join(script_dir, 'homepage.html')

try:
    with open(html_file_path, 'r', encoding='utf-8') as f:
        # We remove the height parameter and set scrolling to False,
        # letting the CSS above control the iframe's size completely.
        components.html(f.read(), scrolling=False)
except FileNotFoundError:
    st.error("Error: homepage.html not found. Please make sure it is in the same directory as app.py.")

