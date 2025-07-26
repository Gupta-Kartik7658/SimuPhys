# import streamlit as st
# import streamlit.components.v1 as components

# # Sliders
# velocity = st.slider("Velocity", 1, 100, 30)
# angle = st.slider("Angle", 0, 90, 45)
# height = st.slider("Height", 0, 100, 0)
# gravity = st.slider("Gravity", 1, 20, 10)

# # Component (assumes frontend is served via local file or host)
# components.html(f"""
# <iframe src="C:/Users/suraj/Desktop/SimuPhys/Classical Mechanics/Projectile Motion/projectile.html" width="100%" height="600" style="border:none;"
#         onload="this.contentWindow.postMessage({{
#           type: 'streamlit:render',
#           args: {{
#             velocity: {velocity},
#             angle: {angle},
#             height: {height},
#             gravity: {gravity}
#           }}
#         }}, '*')">
# </iframe>
# """, height=600)


import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Projectile Motion Simulator", layout="centered")
st.title("Projectile Motion")

# Streamlit sliders
velocity = st.slider("Velocity (m/s)", 10, 200, 50)
angle = st.slider("Angle (degrees)", 0, 90, 45)
height = st.slider("Initial Height (m)", 0, 100, 0)
gravity = st.slider("Gravity (m/s²)", 1.0, 20.0, 9.8, step=0.1)

# Iframe + JS to send updated values
components.html(f"""
<script>
  function sendMessage() {{
    const iframe = document.getElementById("simframe");
    if (iframe && iframe.contentWindow) {{
      iframe.contentWindow.postMessage({{
        type: 'streamlit:update',
        args: {{
          velocity: {velocity},
          angle: {angle},
          height: {height},
          gravity: {gravity}
        }}
      }}, '*');
    }} else {{
      setTimeout(sendMessage, 50);
    }}
  }}
  window.addEventListener("load", sendMessage);
</script>

<iframe id="simframe" src="Classical Mechanics\Projectile Motion\projectile.html" width="100%" height="630" style="border:none;"></iframe>
""", height=650)
