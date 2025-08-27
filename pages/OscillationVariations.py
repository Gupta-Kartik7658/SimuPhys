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

with st.expander("🔬 The Science of Oscillation"):
    st.markdown("""
    The motion of the mass-on-a-spring system is described by a second-order linear homogeneous differential equation, derived from Newton's second law, $F=ma$. The net force is the sum of the spring's restoring force ($-kx$) and the damping force ($-c\\frac{dx}{dt}$), where 'c' is the damping coefficient.
    """)
    st.subheader("The Governing Equation")
    st.markdown("""
    This gives us the general equation for a damped harmonic oscillator:
    $$ m\\frac{d^2x}{dt^2} + c\\frac{dx}{dt} + kx = 0 $$
    By redefining the constants, we can analyze the solutions for different scenarios.
    """)

    st.subheader("Undamped Oscillation")
    st.markdown("""
    In an ideal, frictionless system ($c=0$), energy is conserved, leading to **Simple Harmonic Motion (SHM)**. The equation simplifies to:
    $$ \\frac{d^2x}{dt^2} + \\omega_0^2 x = 0 $$
    The solution describes a perfect, unending wave with a constant amplitude ($A$) and natural frequency ($\\omega_0$):
    $$ x(t) = A \\cos(\\omega_0 t) $$
    """)

    st.subheader("Damped Oscillation")
    st.markdown("""
    In reality, damping forces ($c > 0$) cause the system to lose energy. The amplitude decays exponentially over time due to the **damping coefficient** ($\\beta = c/2m$). The solution is:
    $$ x(t) = A e^{-\\beta t} \\cos(\\omega' t) $$
    Here, the oscillation frequency $\\omega'$ is slightly less than the natural frequency $\\omega_0$.
    """)

    st.subheader("Overdamped Oscillation")
    st.markdown("""
    When damping is very strong, the system returns to equilibrium as quickly as possible *without oscillating at all*. The solution to the differential equation has no sinusoidal component, only decaying exponential terms.
    """)

    st.header("⏰ The Heartbeat of Technology")
    st.markdown("""
    The predictable nature of oscillators is crucial for technology. For instance, a **Quartz Crystal Oscillator** is the timing heart of virtually every computer and smartphone. Its incredibly stable vibrations produce a "clock signal" that acts as a metronome, synchronizing all of the device's operations.
    """)

with st.expander("📖 How to Use This Simulation"):
    st.markdown("""
    - **Adjust the Sliders:**
        - **Amplitude (A):** Controls the initial height or maximum displacement of the box.
        - **Angular Frequency (ω):** Controls how fast the box oscillates. Higher values mean faster oscillations.
        - **Damping Coefficient (β):** Controls how quickly the oscillation loses energy. At `0.0`, it's undamped. Higher values make it stop faster.

    - **Select a Mode:**
        - **Undamped:** An ideal oscillation that never stops.
        - **Damped:** A realistic oscillation that gradually fades out.
        - **Overdamped:** The system returns to the middle without oscillating at all.

    - **Interact with the 3D View:**
        - **Rotate:** Click and drag with your mouse to rotate the camera.
        - **Zoom:** Use your mouse scroll wheel to zoom in and out.
        - **Pan:** Right-click and drag to move the view.

    - **Use the Animation Controls:**
        - **Play/Pause/Reset** buttons at the bottom control the animation playback.
    """)

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
components.html(html_code, height=500, scrolling=False)

# --- Theory and instructions expanders ---
st.markdown("---")

