import streamlit as st
import streamlit.components.v1 as components
import base64
from PIL import Image
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
body {
  margin: 0 !important;
  padding: 0 !important;
}
html, .main, .block-container {
  padding: 0 !important;
  margin: 0 !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
body {
  overflow: hidden !important;
}
html, .main, .block-container {
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# Hide sidebar and toggle
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Optional: Load CSS (keep if you want external style)
def load_css(file):
    with open(file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode("utf-8")
    return f"data:image/png;base64,{b64_string}"  # jpg → jpeg for compatibility

logo_base64 = get_base64_image("SimuPhysimg.png")

st.markdown(f"""
<div style="position: absolute; top: -20vh; left: 28vw; z-index: 10; color: white; padding: 10px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
  <img src="{logo_base64}" width="650" height= "650" />
</div>
""", unsafe_allow_html=True)


st.markdown("""<div>
<div style="position: absolute; top: 35vh; left: 10vw; z-index: 10; color: white; padding: 10px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
    <a href="QuantumMechanics" target="_self" class="button-container">Quantum Mechanics</a>
</div>
<div style="position: absolute; top: 35vh; left: 70vw; z-index: 10; color: white; padding: 10px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
    <a href="Electromagnetism" target="_self" class="button-container">Electromagnetism</a>
</div>
<div style="position: absolute; top: 50vh; left: 40vw; z-index: 10; color: white; padding: 10px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
    <a href="ClassicalMechanics" target="_self" class="button-container">Classical Mechanics</a>
</div>    
            </div>        
""", unsafe_allow_html=True)

components.html("""
<div id="three-container" style="
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -1;
  overflow: hidden;
  margin: 0;
  padding: 0;
"></div>


<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
  const container = document.getElementById("three-container");
  
  const c1 = document.getElementById("button-container");
  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x7200ab, 0.026);

  const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
  camera.position.set(0, 10, 20);
  camera.lookAt(0, 3, 0);

  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  const geometry = new THREE.PlaneGeometry(200, 35, 280, 49);
  const material = new THREE.MeshBasicMaterial({
    color: 0x44c6f8,
    wireframe: true,
    transparent: true,
    opacity: 0.45,
  });

  const grid = new THREE.Mesh(geometry, material);
  grid.rotation.x = (-Math.PI / 2) * 1.2;
  scene.add(grid);

  const clock = new THREE.Clock();

  function animateWave() {
    const time = clock.getElapsedTime();
    const positions = geometry.attributes.position;
    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i);
      const y = positions.getY(i);
      const waveZ = Math.sin((x + time * 2) * 0.25) * Math.cos((y + time * 2) * 0.25) * 2;
      positions.setZ(i, waveZ);
    }
    positions.needsUpdate = true;
  }

  function animate() {
    requestAnimationFrame(animate);
    animateWave();
    renderer.render(scene, camera);
  }

  animate();

  window.addEventListener('resize', () => {
    const width = container.clientWidth;
    const height = container.clientHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  });
</script>
""", height=800,width=1534)
