import streamlit as st
import streamlit.components.v1 as components

# ---- Streamlit Page Setup ----
st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("⚡ Visualizing Electromagnetic Waves")
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

st.markdown(
    "This interactive 3D simulation shows how an oscillating charge emits electromagnetic waves. "
    "Use the controls below to change the wave's properties and your mouse to explore the 3D scene."
)

st.markdown("---")

# ---- Top Controls Section ----
st.header("⚙️ Simulation Controls")
st.info(
    "Adjusting a slider will restart the animation with the new value."
)

# Create three columns for the sliders to sit side-by-side
c1, c2, c3 = st.columns(3)

with c1:
    amplitude = st.slider(
        "Amplitude (A)",
        min_value=0.5,
        max_value=5.0,
        value=2.5,
        step=0.1,
        help="Controls how far the charge moves. This affects the wave's strength."
    )

with c2:
    frequency = st.slider(
        "Frequency (ω)",
        min_value=0.5,
        max_value=5.0,
        value=2.0,
        step=0.1,
        help="Controls how fast the charge oscillates. This affects the wavelength."
    )

with c3:
    grid_density = st.slider(
        "Field Grid Density",
        min_value=10,
        max_value=40,
        value=25,
        step=1,
        help="Controls how many field vectors are displayed."
    )

st.markdown("---")


# ---- Bottom Animation Section ----
# This f-string contains the HTML, CSS, and JavaScript.
three_js_component = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Electromagnetic Wave Simulation</title>
    <style>
        body {{ margin: 0; overflow: hidden; background: black; font-family: sans-serif; }}
        
        /* These containers will now take the full width of the page area */
        #main-container {{
            width: 100%;
            height: 560px; /* Fixed height for the main animation */
        }}
        #subplot-container {{
            width: 100%;
            height: 300px; /* Fixed height for the subplot */
            background-color: #080808;
            border-top: 2px solid #333;
            cursor: grab;
        }}
        #subplot-container:active {{
            cursor: grabbing;
        }}
    </style>
</head>
<body>
    <div id="main-container"></div>
    <div id="subplot-container"></div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.134.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        // --- Use values from Streamlit sliders ---
        const A = {amplitude};
        const w = {frequency};
        const gridSize = {grid_density};
        const propagationSpeed = 10.0;
        const c = propagationSpeed;

        const clock = new THREE.Clock();

        // ====================================================================
        // --- MAIN 3D SIMULATION SETUP ---
        // ====================================================================
        const mainContainer = document.getElementById('main-container');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, mainContainer.clientWidth / mainContainer.clientHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(mainContainer.clientWidth, mainContainer.clientHeight);
        mainContainer.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 10;
        controls.maxDistance = 200;
        camera.position.set(30, 25, 30);
        camera.lookAt(0, 0, 0);

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
        directionalLight.position.set(15, 30, 20);
        scene.add(directionalLight);

        const charge = new THREE.Mesh(
            new THREE.SphereGeometry(0.2, 32, 32),
            new THREE.MeshPhongMaterial({{ color: 0x3399ff, emissive: 0x003366 }})
        );
        scene.add(charge);

        const eFieldHelpers = [], bFieldHelpers = [];
        const arrowLengthScale = 1.2, maxArrowLength = 2.5;
        const spacing = 40 / gridSize;
        const UP = new THREE.Vector3(0, 1, 0), DOWN = new THREE.Vector3(0, -1, 0);

        for (let i = -gridSize; i <= gridSize; i++) {{
            for (let j = -gridSize; j <= gridSize; j++) {{
                const x = i * spacing;
                const z = j * spacing;
                if (x*x + z*z < 1.5) continue;
                const origin = new THREE.Vector3(x, 0, z);
                const eArrow = new THREE.ArrowHelper(UP, origin, 1, 0xFFEE00, 0.3, 0.2);
                scene.add(eArrow);
                eFieldHelpers.push({{ arrow: eArrow, x, z }});
                const bArrow = new THREE.ArrowHelper(UP, origin, 1, 0xFF69B4, 0.3, 0.2);
                scene.add(bArrow);
                bFieldHelpers.push({{ arrow: bArrow, x, z }});
            }}
        }}

        const influenceRings = [];
        const ringMaterial = new THREE.MeshBasicMaterial({{ color: 0xAAAAAA, transparent: true, side: THREE.DoubleSide, opacity: 0.7 }});
        const ringSpawnInterval = 0.5;
        let lastRingSpawnTime = -Infinity;
        const maxRingWidth = 0.2;

        function createInfluenceRing(time) {{
            const ringGroup = new THREE.Group();
            ringGroup.spawnTime = time;
            const ringMesh = new THREE.Mesh(new THREE.RingGeometry(0.01, 0.02, 64), ringMaterial.clone());
            ringMesh.rotation.x = Math.PI / 2;
            ringGroup.add(ringMesh);
            scene.add(ringGroup);
            influenceRings.push(ringGroup);
        }}

        function updateInfluenceRings(currentTime) {{
            for (let i = influenceRings.length - 1; i >= 0; i--) {{
                const ringGroup = influenceRings[i];
                const ringMesh = ringGroup.children[0];
                const material = ringMesh.material;
                const timeSinceSpawn = currentTime - ringGroup.spawnTime;
                const radius = timeSinceSpawn * propagationSpeed;
                const opacity = Math.max(0, 0.7 - Math.pow(radius / (gridSize * spacing), 1.5));
                const width = Math.max(0.01, maxRingWidth / (1 + Math.sqrt(radius)));

                if (opacity <= 0.01 || radius > (gridSize * spacing) * 1.5) {{
                    scene.remove(ringGroup);
                    ringMesh.geometry.dispose();
                    material.dispose();
                    influenceRings.splice(i, 1);
                }} else {{
                    ringMesh.geometry.dispose();
                    ringMesh.geometry = new THREE.RingGeometry(radius, radius + width, 64);
                    material.opacity = opacity;
                }}
            }}
        }}

        function animateMainScene(t) {{
            controls.update();
            charge.position.y = A * Math.sin(w * t);

            if (t - lastRingSpawnTime > ringSpawnInterval / w) {{
                createInfluenceRing(t);
                lastRingSpawnTime = t;
            }}
            updateInfluenceRings(t);

            for(let i = 0; i < eFieldHelpers.length; i++) {{
                const eData = eFieldHelpers[i];
                const bData = bFieldHelpers[i];
                const {{ x, z }} = eData;
                const r = Math.sqrt(x * x + z * z);
                const retardedTime = t - (r / c);

                if (retardedTime < 0) {{
                    eData.arrow.setLength(0);
                    bData.arrow.setLength(0);
                    continue;
                }}

                const phase = w * retardedTime;
                const E_y = (A * w * w * Math.sin(phase)) / r;
                const length = Math.min(maxArrowLength, arrowLengthScale * Math.abs(E_y));
                const headLength = length * 0.3, headWidth = length * 0.2;

                if (length < 0.01) {{
                    eData.arrow.setLength(0);
                    bData.arrow.setLength(0);
                }} else {{
                    eData.arrow.setDirection(E_y > 0 ? UP : DOWN);
                    eData.arrow.setLength(length, headLength, headWidth);
                    const tangentDir = new THREE.Vector3(-z, 0, x).normalize();
                    bData.arrow.setDirection(E_y > 0 ? tangentDir : tangentDir.clone().negate());
                    bData.arrow.setLength(length, headLength, headWidth);
                }}
            }}
            renderer.render(scene, camera);
        }}

        // ====================================================================
        // --- SUBPLOT 3D WAVEFORM SETUP ---
        // ====================================================================
        const subContainer = document.getElementById('subplot-container');
        const sceneSub = new THREE.Scene();
        const cameraSub = new THREE.PerspectiveCamera(60, subContainer.clientWidth / subContainer.clientHeight, 0.1, 1000);
        cameraSub.position.set(8, 6, 14);
        cameraSub.lookAt(0, 0, 0);

        const rendererSub = new THREE.WebGLRenderer({{ antialias: true }});
        rendererSub.setPixelRatio(window.devicePixelRatio);
        rendererSub.setSize(subContainer.clientWidth, subContainer.clientHeight);
        subContainer.appendChild(rendererSub.domElement);

        const controlsSub = new THREE.OrbitControls(cameraSub, rendererSub.domElement);
        controlsSub.enableDamping = true;
        controlsSub.dampingFactor = 0.1;
        controlsSub.minDistance = 5;
        controlsSub.maxDistance = 50;
        
        const subLight = new THREE.AmbientLight(0xffffff, 1.0);
        sceneSub.add(subLight);
        const gridHelper = new THREE.GridHelper(20, 20, 0x333333, 0x333333);
        sceneSub.add(gridHelper);
        
        const waveSegments = 128;
        const waveLength = 20;
        const tubeRadius = 0.1;
        const ePoints = [];
        const bPoints = [];
        for (let i = 0; i <= waveSegments; i++) {{
            const x = (i / waveSegments) * waveLength - (waveLength / 2);
            ePoints.push(new THREE.Vector3(x, 0, 0));
            bPoints.push(new THREE.Vector3(x, 0, 0));
        }}

        const ePath = new THREE.CatmullRomCurve3(ePoints);
        const bPath = new THREE.CatmullRomCurve3(bPoints);
        
        const eMaterial = new THREE.MeshStandardMaterial({{ color: 0xFFEE00, metalness: 0.1, roughness: 0.5 }});
        const bMaterial = new THREE.MeshStandardMaterial({{ color: 0xFF69B4, metalness: 0.1, roughness: 0.5 }});

        let eGeom = new THREE.TubeGeometry(ePath, waveSegments, tubeRadius, 8, false);
        let bGeom = new THREE.TubeGeometry(bPath, waveSegments, tubeRadius, 8, false);
        const eWave = new THREE.Mesh(eGeom, eMaterial);
        const bWave = new THREE.Mesh(bGeom, bMaterial);
        sceneSub.add(eWave, bWave);

        function animateSubplot(t) {{
            controlsSub.update();

            const subplot_A = A * 0.4;
            const subplot_speed = 4.0;
            const k = (w * 2) / subplot_speed;

            const pathPointsE = eWave.geometry.parameters.path.points;
            const pathPointsB = bWave.geometry.parameters.path.points;
            
            for (let i = 0; i <= waveSegments; i++) {{
                const x = (i / waveSegments) * waveLength - (waveLength / 2);
                const phase = k * x - w * 2 * t;

                pathPointsE[i].y = subplot_A * Math.sin(phase);
                pathPointsB[i].z = subplot_A * Math.sin(phase);
            }}

            eWave.geometry.dispose();
            eWave.geometry = new THREE.TubeGeometry(eWave.geometry.parameters.path, waveSegments, tubeRadius, 8, false);
            
            bWave.geometry.dispose();
            bWave.geometry = new THREE.TubeGeometry(bWave.geometry.parameters.path, waveSegments, tubeRadius, 8, false);

            rendererSub.render(sceneSub, cameraSub);
        }}

        // ====================================================================
        // --- GLOBAL ANIMATION LOOP & RESIZE ---
        // ====================================================================
        function animate() {{
            requestAnimationFrame(animate);
            const t = clock.getElapsedTime();
            animateMainScene(t);
            animateSubplot(t);
        }}

        window.addEventListener('resize', () => {{
            // Main scene
            camera.aspect = mainContainer.clientWidth / mainContainer.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(mainContainer.clientWidth, mainContainer.clientHeight);
            // Subplot scene
            cameraSub.aspect = subContainer.clientWidth / subContainer.clientHeight;
            cameraSub.updateProjectionMatrix();
            rendererSub.setSize(subContainer.clientWidth, subContainer.clientHeight);
        }});

        animate();
    </script>
</body>
</html>
"""

# Render the HTML component below the controls
# Set height to accommodate both the main scene (560px) and subplot (300px)
components.html(three_js_component, height=860)


# ---- Explanation Section ----
st.markdown("---")
st.header("Anatomy of an EM Wave")
st.markdown("""
The plot above shows a simplified, **interactive 3D view** of a plane electromagnetic wave propagating through space.
- The Electric Field (E) (yellow tube) oscillates vertically.
- The Magnetic Field (B) (pink tube) oscillates horizontally.
- Notice that the E and B fields are always **in phase** and **perpendicular** to each other and to the direction of propagation.
""")
st.markdown("---")