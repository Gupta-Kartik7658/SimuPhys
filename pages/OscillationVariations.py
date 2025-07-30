import streamlit as st
import streamlit.components.v1 as components

# Streamlit UI configuration
st.set_page_config(page_title="Oscillation Visualizer", layout="wide")
st.title("🎵 Oscillation Types with Synchronized 3D Object")
st.markdown("Adjust the parameters in the sidebar to see how they affect both the wave and the motion of the box.")


# Sidebar controls
with st.sidebar:
    st.header("⚙️ Oscillation Parameters")
    A = st.slider("Amplitude (A)", 0.1, 5.0, 2.0, 0.1)
    omega = st.slider("Angular Frequency (ω)", 0.5, 10.0, 3.0, 0.1)
    beta = st.slider("Damping Coefficient (β)", 0.0, 2.0, 0.5, 0.1)
    mode = st.selectbox("Mode", ["Undamped", "Damped", "Overdamped"])

# Embed HTML + Three.js
# I've replaced the cylinder with a realistic, animated helix spring.
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
// Function to create a helix geometry
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
    
    // Store original data for animation
    geometry.userData.originalPositions = geometry.attributes.position.clone();
    geometry.userData.originalHeight = height;

    return geometry;
}}

const springRestHeight = 2.0;
const springGeometry = createSpringGeometry(0.25, springRestHeight, 10, 256, 8, 0.05);
const springMaterial = new THREE.MeshStandardMaterial({{ color: 0xcccccc, metalness: 0.8, roughness: 0.3 }});
const spring = new THREE.Mesh(springGeometry, springMaterial);
// Position the top of the spring at the bottom of the roof
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
    
    // Animate by manipulating vertices for a realistic stretch/compress effect
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
    const t = clock.getElapsedTime();

    if (isPlaying) {{
        // 1. Calculate the oscillator's (box's) current Y position based on time.
        let boxY = 0;
        if (mode === "Undamped") {{
            boxY = A * Math.cos(omega * t);
        }} else if (mode === "Damped") {{
            boxY = A * Math.exp(-beta * 0.5 * t) * Math.cos(omega * t);
        }} else if (mode === "Overdamped") {{
            boxY = A * Math.exp(-beta * 2.0 * t);
        }}
        box.position.y = boxY;

        // 2. Update the spring to connect the roof and the box
        updateSpring();

        // 3. Generate the wave based on the oscillator's history.
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

        // Update the line geometry
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
    clock.stop();
    clock.start();
    if(isPlaying) {{
        // keep it running if it was
    }} else {{
        // pause it if it was paused
        clock.stop();
    }}
    
    box.position.y = A;
    updateSpring();

    for (let i = 0; i < pointCount; i++) {{
        oscPoints[i].y = 0;
    }}
    oscGeometry.setFromPoints(oscPoints);

    if (!isPlaying) {{
        renderer.render(scene, camera);
    }}
}}


// --- Handle Window Resize ---
window.addEventListener('resize', () => {{
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}});

// Set initial state of the spring before starting animation
box.position.y = A;
updateSpring();

// Start the animation
animate();
</script>

</body>
</html>
"""

# Render the HTML component in Streamlit
components.html(html_code, height=700, scrolling=False)

# Add summary write-up
st.markdown("---")
st.markdown("### 📌 How It Works (Corrected Physics):")
st.markdown("""
- **Realistic Spring**: The simple cylinder has been replaced with a helical spring that stretches and compresses realistically by changing the distance between its coils.
- **Stationary Oscillator**: The box now behaves like a true oscillator, moving vertically at a fixed position (`x=0`).
- **Time-Based Damping**: The damping effect correctly reduces the box's oscillation amplitude over *time*, not distance.
- **Propagating Wave**: The line graph represents the history of the box's motion, propagating outwards from the oscillator.
- **Corrected Modes**:
  - **Undamped**: The box oscillates with a constant amplitude.
  - **Damped**: The box's oscillations slowly fade out over time.
  - **Overdamped**: The box returns smoothly to its equilibrium point without oscillating.
""")
