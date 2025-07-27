import streamlit as st
import streamlit.components.v1 as components

# Streamlit UI configuration
st.set_page_config(page_title="Oscillation Visualizer", layout="wide")
st.title("🎵 Oscillation Types: Damped and Undamped")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Oscillation Parameters")
    A = st.slider("Amplitude (A)", 0.1, 2.0, 1.0, 0.1)
    omega = st.slider("Angular Frequency (ω)", 0.5, 10.0, 2.0, 0.1)
    beta = st.slider("Damping Coefficient (β)", 0.0, 2.0, 0.1, 0.1)
    mode = st.selectbox("Mode", ["Undamped", "Damped", "Overdamped"])

# Embed HTML + Three.js
html_code = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Oscillations</title>
  <style>
    body {{ margin: 0; overflow: hidden; font-family: sans-serif; }}
    canvas {{ display: block; }}
    #controls {{
        position: absolute;
        top: 10px;
        left: 10px;
        background: rgba(255,255,255,0.8);
        padding: 10px;
        border-radius: 8px;
        z-index: 1;
    }}
    button {{
        margin-right: 10px;
        padding: 6px 12px;
        font-size: 14px;
    }}
  </style>
</head>
<body>
<div id="controls">
    <button onclick="play()">▶️ Play</button>
    <button onclick="pause()">⏸️ Pause</button>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.134.0/examples/js/controls/OrbitControls.min.js"></script>
<script>
const A = {A};
const omega = {omega};
const beta = {beta};
const mode = "{mode}";

let isPlaying = false;
let wavefront = 0;

// Scene setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
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

// Axes
const axesHelper = new THREE.AxesHelper(5);
scene.add(axesHelper);

// Line geometry
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

// Clock
const clock = new THREE.Clock();

// Animation loop
function animate() {{
    requestAnimationFrame(animate);

    if (isPlaying) {{
        const t = clock.getElapsedTime();
        wavefront = omega * t;

        for (let i = 0; i < pointCount; i++) {{
            const x = i * spacing;
            let y = 0;

            if (x <= wavefront) {{
                let fade = 1.0;
                const fadeWidth = 0.5;
                const distanceToFront = wavefront - x;
                if (distanceToFront < fadeWidth) {{
                    fade = 0.5 * (1 - Math.cos(Math.PI * distanceToFront / fadeWidth));
                }}

                if (mode === "Undamped") {{
                    y = fade * A * Math.sin(omega * t - omega * x);
                }} else if (mode === "Damped") {{
                    y = fade * A * Math.exp(-beta * x) * Math.sin(omega * t - omega * x);
                }} else if (mode === "Overdamped") {{
                    y = fade * A * Math.exp(-beta * x);
                }}
            }}

            oscPoints[i].set(x, y, 0);
        }}

        oscGeometry.setFromPoints(oscPoints);
    }}

    controls.update();
    renderer.render(scene, camera);
}}

// Button controls
function play() {{
    clock.start();
    isPlaying = true;
}}

function pause() {{
    clock.stop();
    isPlaying = false;
}}

animate();
</script>

</body>
</html>
"""

# Render the HTML
components.html(html_code, height=600)


# Add summary write-up
st.markdown("---")
st.markdown("### 📌 Key Takeaways:")
st.markdown("""
- **Amplitude (A)**: Controls how tall the oscillations are.
- **Angular Frequency (ω)**: Determines the speed of oscillation.
- **Damping Coefficient (β)**: Affects how quickly the wave fades out.
- **Modes**:
  - **Undamped**: Pure sinusoidal wave with no decay.
  - **Damped**: Oscillations fade over distance.
  - **Overdamped**: No oscillation, only exponential decay.
- Interactive **3D visualization** using Three.js.
- Use **play/pause** buttons and **mouse** to explore wave behavior.
""")