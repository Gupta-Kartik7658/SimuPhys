import streamlit as st
import streamlit.components.v1 as components

# Streamlit UI configuration
st.set_page_config(page_title="Oscillation Visualizer", layout="wide")

# --- CSS to hide the default Streamlit sidebar/menu ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            [data-testid="stSidebar"] {
                    display: none;
                }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("🎵 Oscillation Types with Synchronized 3D Object")
st.markdown("Adjust the parameters below to see how they affect both the wave and the motion of the box.")
st.markdown("---")

# --- Main app controls ---
st.header("⚙️ Oscillation Parameters")
col1, col2 = st.columns(2)

with col1:
    A = st.slider("Amplitude (A)", 0.1, 5.0, 2.0, 0.1, key="amplitude")
    omega = st.slider("Angular Frequency (ω)", 0.5, 10.0, 3.0, 0.1, key="omega")

with col2:
    beta = st.slider("Damping Coefficient (β)", 0.0, 2.0, 0.5, 0.1, key="beta")
    mode = st.selectbox("Mode", ["Undamped", "Damped", "Overdamped"], key="mode")

st.markdown("---")


# Embed HTML + Three.js
html_code = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Oscillations with Synced Object</title>
  <style>
    body {{ margin: 0; overflow: hidden; font-family: sans-serif; background-color: #111; }}
    canvas {{ display: block; }}
    #controls {{
        position: absolute;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0,0,0,0.5);
        padding: 10px 15px;
        border-radius: 15px;
        z-index: 1;
        display: flex;
        gap: 10px;
    }}
    button {{
        background-color: #444;
        color: white;
        border: 1px solid #666;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s;
    }}
    button:hover {{
        background-color: #555;
    }}
  </style>
</head>
<body>
<div id="controls">
    <button onclick="play()">▶️ Play</button>
    <button onclick="pause()">⏸️ Pause</button>
    <button onclick="reset()">🔄 Reset</button>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.134.0/examples/js/controls/OrbitControls.min.js"></script>
<script>
// Parameters from Streamlit
const A = {A};
const omega = {omega};
const beta = {beta};
const mode = "{mode}";

// Animation state
let isPlaying = true;
let totalElapsedTime = 0;
const waveSpeed = 4.0;

// --- Scene Setup ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(10, 4, 15);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.body.appendChild(renderer.domElement);

// --- Controls ---
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.target.set(10, 0, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// --- Lighting ---
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);
const pointLight = new THREE.PointLight(0xffffff, 1.5, 100);
pointLight.position.set(4, 5, 5);
scene.add(pointLight);

// --- Axes Helper ---
const axesHelper = new THREE.AxesHelper(5);
scene.add(axesHelper);

// --- Roof (anchor for the spring) ---
const roofYPosition = 4.0;
const roofGeometry = new THREE.BoxGeometry(2, 0.5, 2);
const roofMaterial = new THREE.MeshStandardMaterial({{ color: 0x888888 }});
const roof = new THREE.Mesh(roofGeometry, roofMaterial);
roof.position.set(0, roofYPosition, 0);
scene.add(roof);

// --- The Oscillating Object (Box) ---
const boxSize = 0.8;
const boxGeometry = new THREE.BoxGeometry(boxSize, boxSize, boxSize);
const boxMaterial = new THREE.MeshStandardMaterial({{
    color: 0x00ffff,
    metalness: 0.3,
    roughness: 0.4
}});
const box = new THREE.Mesh(boxGeometry, boxMaterial);
box.position.set(0, A, 0);
scene.add(box);

// --- The Spring ---
function createSpringGeometry(radius, height, coils, tubularSegments, radialSegments, tubeRadius) {{
    const points = [];
    for (let i = 0; i <= tubularSegments; i++) {{
        const y = (i / tubularSegments) * -height;
        const angle = (i / tubularSegments) * Math.PI * 2 * coils;
        const x = Math.cos(angle) * radius;
        const z = Math.sin(angle) * radius;
        points.push(new THREE.Vector3(x, y, z));
    }}
    const path = new THREE.CatmullRomCurve3(points);
    const geometry = new THREE.TubeGeometry(path, tubularSegments, tubeRadius, radialSegments, false);
    
    geometry.userData.originalPositions = geometry.attributes.position.clone();
    geometry.userData.originalHeight = height;

    return geometry;
}}

const springRestHeight = 2.0;
const springGeometry = createSpringGeometry(0.25, springRestHeight, 10, 256, 8, 0.05);
const springMaterial = new THREE.MeshStandardMaterial({{ color: 0xcccccc, metalness: 0.8, roughness: 0.3 }});
const spring = new THREE.Mesh(springGeometry, springMaterial);
spring.position.y = roofYPosition - 0.25;
scene.add(spring);

// --- The Wave (Line) ---
const pointCount = 500;
const spacing = 0.05;
const oscPoints = [];
for (let i = 0; i < pointCount; i++) {{
    const x = i * spacing;
    oscPoints.push(new THREE.Vector3(x, 0, 0));
}}
const oscGeometry = new THREE.BufferGeometry().setFromPoints(oscPoints);
const oscMaterial = new THREE.LineBasicMaterial({{ color: 0xffffff, linewidth: 2 }});
const oscLine = new THREE.Line(oscGeometry, oscMaterial);
scene.add(oscLine);

// --- Animation Logic ---
const clock = new THREE.Clock(); 

function updateSpring() {{
    const boxTopY = box.position.y + boxSize / 2;
    const roofBottomY = roofYPosition - 0.25;
    const currentHeight = roofBottomY - boxTopY;
    
    const originalHeight = spring.geometry.userData.originalHeight;
    const scaleFactor = currentHeight / originalHeight;
    
    const positions = spring.geometry.attributes.position;
    const originalPositions = spring.geometry.userData.originalPositions;

    for (let i = 0; i < positions.count; i++) {{
        const originalY = originalPositions.getY(i);
        positions.setY(i, originalY * scaleFactor);
    }}
    
    positions.needsUpdate = true;
}}

function animate() {{
    requestAnimationFrame(animate);

    if (isPlaying) {{
        totalElapsedTime += clock.getDelta();
        const t = totalElapsedTime;

        let boxY = 0;
        if (mode === "Undamped") {{
            boxY = A * Math.cos(omega * t);
        }} else if (mode === "Damped") {{
            boxY = A * Math.exp(-beta * 0.5 * t) * Math.cos(omega * t);
        }} else if (mode === "Overdamped") {{
            boxY = A * Math.exp(-beta * 2.0 * t);
        }}
        box.position.y = boxY;

        updateSpring();

        for (let i = 0; i < pointCount; i++) {{
            const x = oscPoints[i].x;
            const timeAtPoint = t - (x / waveSpeed);
            let y = 0;

            if (timeAtPoint >= 0) {{
                if (mode === "Undamped") {{
                    y = A * Math.cos(omega * timeAtPoint);
                }} else if (mode === "Damped") {{
                    y = A * Math.exp(-beta * 0.5 * timeAtPoint) * Math.cos(omega * timeAtPoint);
                }} else if (mode === "Overdamped") {{
                    y = A * Math.exp(-beta * 2.0 * timeAtPoint);
                }}
            }}
            oscPoints[i].y = y;
        }}
        oscGeometry.setFromPoints(oscPoints);
    }}

    controls.update();
    renderer.render(scene, camera);
}}

// --- UI Controls ---
function play() {{
    if (!isPlaying) {{
        clock.start(); 
        isPlaying = true;
    }}
}}

function pause() {{
    if (isPlaying) {{
        clock.stop();
        isPlaying = false;
    }}
}}

function reset() {{
    isPlaying = false; 
    clock.stop();
    totalElapsedTime = 0;
    
    box.position.y = A;
    updateSpring();

    for (let i = 0; i < pointCount; i++) {{
        oscPoints[i].y = 0;
    }}
    oscGeometry.setFromPoints(oscPoints);

    renderer.render(scene, camera);
}}

// --- Handle Window Resize ---
window.addEventListener('resize', () => {{
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}});

box.position.y = A;
updateSpring();
animate();
</script>

</body>
</html>
"""

# Render the HTML component in Streamlit
# The height is changed from 600 to 500 to make the component smaller.
components.html(html_code, height=500, scrolling=False)

# Add summary write-up
st.markdown("---")
st.header("The Science of Oscillation")
st.markdown("""
This simulation demonstrates three fundamental types of mechanical oscillation, governed by the interplay between a restoring force (from the spring) and a damping force (like air resistance).
""")

st.subheader("Undamped Oscillation")
st.markdown("""
In an ideal, frictionless world, an oscillator exhibits **Simple Harmonic Motion (SHM)**. The system's total mechanical energy is conserved, causing it to oscillate with a constant amplitude ($A$) and a single, natural frequency ($\omega$). The displacement is described by:
$$ x(t) = A \cos(\omega t) $$
""")

st.subheader("Damped Oscillation")
st.markdown("""
In reality, dissipative forces cause the oscillation's energy to decrease. The amplitude is no longer constant but decays exponentially over time due to the **damping coefficient** ($\beta$). The system still oscillates, but its swings get progressively smaller until it stops. The equation is:
$$ x(t) = A e^{-\\beta t} \cos(\omega' t) $$
""")

st.subheader("Overdamped Oscillation")
st.markdown("""
When the damping force is very strong (a large $\beta$), the system is **overdamped**. It returns to equilibrium as quickly as possible *without oscillating at all*. Imagine a pendulum trying to swing through thick honey; it would simply ooze back to the center without overshooting.
""")