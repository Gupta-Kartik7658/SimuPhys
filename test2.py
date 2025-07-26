import streamlit as st
import streamlit.components.v1 as components

# Streamlit UI
st.set_page_config(page_title="EM Wave 3D Simulator", layout="wide")
st.title("🌈 Electromagnetic Wave Simulation (3D)")

with st.sidebar:
    st.header("Wave Parameters")
    amplitude = st.slider("Amplitude", 0.1, 2.0, 1.0, 0.1)
    wavelength = st.slider("Wavelength", 1.0, 10.0, 5.0, 0.5)
    frequency = st.slider("Frequency", 0.1, 2.0, 1.0, 0.1)
    wave_speed = st.slider("Wave Speed", 1.0, 5.0, 1.0, 0.1)

# Embedded HTML + JavaScript
html_code = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>EM Wave</title>
  <style>
    body {{ margin: 0; overflow: hidden; }}
    canvas {{ display: block; }}
  </style>
</head>
<body><script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
<script>
const amplitude = {amplitude};
const wavelength = {wavelength};
const frequency = {frequency};
const waveSpeed = {wave_speed};

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 100);
camera.position.set(5, 4, 10);
camera.lookAt(0, 2, 0);

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);


const pointCount = 400;
const spacing = 0.1;

const ePoints = [];
const bPoints = [];

for (let i = 0; i < pointCount; i++) {{
    const x = (i - pointCount / 2) * spacing;
    ePoints.push(new THREE.Vector3(x, 0, 0));
    bPoints.push(new THREE.Vector3(x, 0, 0));
}}

const eGeometry = new THREE.BufferGeometry().setFromPoints(ePoints);
const eMaterial = new THREE.LineBasicMaterial({{ color: 0x00ff00 }});
const eLine = new THREE.Line(eGeometry, eMaterial);
scene.add(eLine);

const bGeometry = new THREE.BufferGeometry().setFromPoints(bPoints);
const bMaterial = new THREE.LineBasicMaterial({{ color: 0x0000ff }});
const bLine = new THREE.Line(bGeometry, bMaterial);
scene.add(bLine);

// Static particle position
const particleX = 0;  // End of wave
const particleY = 0;
const particleZ = 0;

// Particle (small sphere)
const particleGeometry = new THREE.SphereGeometry(0.1, 16, 16);
const particleMaterial = new THREE.MeshBasicMaterial({{ color: 0xff0000 }});
const particle = new THREE.Mesh(particleGeometry, particleMaterial);
particle.position.set(particleX, particleY, particleZ);
scene.add(particle);

// Tail (straight line back along x-axis)
const tailLength = 40;
const tailStart = new THREE.Vector3(particleX, particleY, particleZ);
const tailEnd = new THREE.Vector3(particleX + tailLength, particleY, particleZ);
const tailGeometry = new THREE.BufferGeometry().setFromPoints([tailStart, tailEnd]);
const tailMaterial = new THREE.LineBasicMaterial({{ color: 0xffff00 }});
const tail = new THREE.Line(tailGeometry, tailMaterial);
scene.add(tail);


const clock = new THREE.Clock();

function animate() {{
    const t = clock.getElapsedTime();

    for (let i = 0; i < pointCount; i++) {{
        const x = (i+200 - pointCount / 2) * spacing;
        const phase = 2 * Math.PI * (x / wavelength - frequency * t);

        const ey = amplitude * Math.sin(phase);
        const bz = amplitude * Math.sin(phase) / 3e8;

        ePoints[i].set(x, ey, 0);
        bPoints[i].set(x, 0, bz * 3e8);
    }}

    eGeometry.setFromPoints(ePoints);
    bGeometry.setFromPoints(bPoints);

    controls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
}}

// Inject OrbitControls and start animation after it's ready
const controlsScript = document.createElement('script');
controlsScript.src = "https://cdn.jsdelivr.net/npm/three@0.134.0/examples/js/controls/OrbitControls.js";
controlsScript.onload = () => {{
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.1;
    controls.rotateSpeed = 0.5;
    controls.zoomSpeed = 0.5;
    animate();
}};
document.head.appendChild(controlsScript);
</script>

</body>
</html>
"""

# Render HTML into Streamlit
components.html(html_code, height=600)
