import streamlit as st

import pathlib
def load_css(file):
    with open(file) as f:
        st.html(f"<style>{f.read()}</style>")

csspath = pathlib.Path("style.css")
load_css(csspath)


st.title("Page 2")
st.write("This is Page 2.")
