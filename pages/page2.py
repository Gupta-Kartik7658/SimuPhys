import streamlit as st
import streamlit.components.v1 as components
import base64
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

import pathlib
def load_css(file):
    with open(file) as f:
        st.html(f"<style>{f.read()}</style>")

csspath = pathlib.Path("style.css")
load_css(csspath)

st.markdown("""<div>
<div style="position: absolute; top: 280px; left: 130px; z-index: 10; color: white; padding: 10px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
    <a href="page1" target="_self" class="button-container">page</a>
</div>
<div style="position: absolute; top: 280px; left: 480px; z-index: 10; color: white; padding: 10px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
    <a href="page1" target="_self" class="button-container">page</a>
</div>
<div style="position: absolute; top: 280px; left: 840px; z-index: 10; color: white; padding: 10px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
    <a href="page1" target="_self" class="button-container">page</a>
</div> 
<div style="position: absolute; top: 280px; left: 1180px; z-index: 10; color: white; padding: 10px; border-radius: 8px; display: flex; align-items: center; gap: 10px;">
    <a href="page1" target="_self" class="button-container">page</a>
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
""", height=850,width=1534)
