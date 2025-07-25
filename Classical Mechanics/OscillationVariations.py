import streamlit as st
import streamlit.components.v1 as components

# Streamlit UI configuration
st.set_page_config(page_title="Oscillation Visualizer", layout="wide")
st.title("🎵 Oscillation Types: Damped and Undamped")

# Sidebar controls
with st.sidebar:
    st.header("Oscillation Parameters")
    A = st.slider("Amplitude (A)", 0.1, 2.0, 1.0, 0.1)
    omega = st.slider("Angular Frequency (ω)", 0.5, 10.0, 2.0, 0.1)
    beta = st.slider("Damping Coefficient (β)", 0.0, 2.0, 0.1, 0.1)
    mode = st.selectbox("Mode", ["Undamped", "Damped", "Overdamped"])

# Embed HTML + Three.js simulation with OrbitControls
html_code = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Oscillations</title>
  <style>
    body {{ margin: 0; overflow: hidden; }}
    canvas {{ display: block; }}
  </style>
</head>
<body>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.134.0/examples/js/controls/OrbitControls.min.js"></script>
<script>
const A = {A};
const omega = {omega};
const beta = {beta};
const mode = "{mode}";

// Scene, camera, renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 100);
camera.position.set(6, 4, 10);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.1;
controls.rotateSpeed = 0.5;
controls.zoomSpeed = 0.5;

// Axes helper
const axesHelper = new THREE.AxesHelper(5);
scene.add(axesHelper);

// Create line points for oscillator
const pointCount = 300;
const spacing = 0.05;
const oscPoints = [];
for (let i = 0; i < pointCount; i++) {{
    const x = i * spacing;
    oscPoints.push(new THREE.Vector3(x, 0, 0));
}}
const oscGeometry = new THREE.BufferGeometry().setFromPoints(oscPoints);
const oscMaterial = new THREE.LineBasicMaterial({{ color: 0x00ffff }});
const oscLine = new THREE.Line(oscGeometry, oscMaterial);
scene.add(oscLine);

// Particle at wave end
const particleGeometry = new THREE.SphereGeometry(0.1, 16, 16);
const particleMaterial = new THREE.MeshBasicMaterial({{ color: 0xff0000 }});
const particle = new THREE.Mesh(particleGeometry, particleMaterial);
scene.add(particle);

// Clock for timing
const clock = new THREE.Clock();

// Animation loop with controls
function animate() {{
    function renderLoop() {{
        const t = clock.getElapsedTime();

        // Update wave points
        for (let i = 0; i < pointCount; i++) {{
            const x = i * spacing;
            let y = 0;
            if (mode === "Undamped") {{
                y = A * Math.sin(omega * t - omega * x);
            }} else if (mode === "Damped") {{
                y = A * Math.exp(-beta * x) * Math.sin(omega * t - omega * x);
            }} else if (mode === "Overdamped") {{
                y = A * Math.exp(-beta * x);
            }}
            oscPoints[i].set(x, y, 0);
        }}
        oscGeometry.setFromPoints(oscPoints);

        // Update particle and tail
        const endY = oscPoints[pointCount - 1].y;
        particle.position.set(0, endY, 0);
       
        

        // Render with controls
        controls.update();
        renderer.render(scene, camera);
        requestAnimationFrame(renderLoop);
    }}
    renderLoop();
}}

animate();
</script>
</body>
</html>
"""

# Render the HTML
components.html(html_code, height=600)
