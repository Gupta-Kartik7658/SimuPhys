import streamlit as st

import streamlit.components.v1 as components
st.set_page_config(layout="centered", initial_sidebar_state="collapsed")

# Hide sidebar and toggle
st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Load CSS
def load_css(file):
    with open(file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")
st.markdown("""
<div style="position: absolute; top: 50px; left: 50px; z-index: 10; background-color: rgba(0,0,0,0.5); color: white; padding: 10px; border-radius: 8px;">
  🚀 Overlay Text via Markdown
</div>
""", unsafe_allow_html=True)

# 3D Canvas
components.html("""
<div id="three-container" style="width: 100%; height: 500px;"></div>
<script type="module">
  import * as THREE from 'https://unpkg.com/three@0.160.1/build/three.module.js';

  // === Scene Setup ===

  const container = document.getElementById("three-container");
  const scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x7200ab, 0.026);
  
  const camera = new THREE.PerspectiveCamera(45, container.innerWidth / container.innerHeight, 0.1, 1000);
  camera.position.set(0, 10, 20);
  camera.lookAt(0, 3, 0);

  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setSize(container.innerWidth, container.innerHeight);
  container.appendChild(renderer.domElement);

  // === Grid Geometry ===
  const geometry = new THREE.PlaneGeometry(200, 35, 280, 49);
  const material = new THREE.MeshBasicMaterial({
    color: 0x44c6f8,
    wireframe: true,
    transparent: true,
    opacity: 0.45,
  });

  const grid = new THREE.Mesh(geometry, material);
  grid.rotation.x = (-Math.PI / 2)*(1.2);
  scene.add(grid);

  // === Animation (Wave Motion) ===
  const clock = new THREE.Clock();

  function animateWave() {
    const time = clock.getElapsedTime();
    const positions = geometry.attributes.position;

    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i);
      const y = positions.getY(i);
      const waveZ = (Math.sin((x + time * 2) * 0.25) * Math.cos((y + time * 2) * 0.25) * 2);
      positions.setZ(i, waveZ);
    }

    positions.needsUpdate = true;
  }

  // === Render Loop ===
  function animate() {
    requestAnimationFrame(animate);
    animateWave();
    renderer.render(scene, camera);
  }

  animate();

  // === Responsive Resize ===
  container.addEventListener('resize', () => {
    camera.aspect = container.innerWidth / container.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.innerWidth, container.innerHeight);
  });
</script>
""",height=400)



