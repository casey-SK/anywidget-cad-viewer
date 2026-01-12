/**
 * CAD Viewer Widget - Frontend Implementation
 * 
 * This widget renders 3D CAD geometry using Three.js.
 * It receives tessellated mesh data from the Python backend via traitlets.
 */

// Import Three.js from esm.sh (provides properly bundled ESM with resolved dependencies)
import * as THREE from "https://esm.sh/three@0.160.0";
import { OrbitControls } from "https://esm.sh/three@0.160.0/examples/jsm/controls/OrbitControls.js";

export function render({ model, el }) {
  // Check WebGL availability
  const canvas = document.createElement("canvas");
  const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
  
  if (!gl) {
    const errorDiv = document.createElement("div");
    errorDiv.className = "cad-viewer-error";
    errorDiv.innerHTML = `
      <strong>WebGL Not Available</strong><br>
      This viewer requires WebGL support for 3D visualization.<br>
      Please use a modern browser (Chrome, Firefox, Safari, Edge).
    `;
    errorDiv.style.padding = "20px";
    errorDiv.style.backgroundColor = "#ffebee";
    errorDiv.style.border = "2px solid #c62828";
    errorDiv.style.borderRadius = "4px";
    errorDiv.style.color = "#c62828";
    el.appendChild(errorDiv);
    return () => {}; // Return empty cleanup function
  }

  // Create container
  const container = document.createElement("div");
  container.className = "cad-viewer-container";
  el.appendChild(container);

  // Get widget dimensions
  const width = model.get("width");
  const height = model.get("height");

  // Setup Three.js scene
  const scene = new THREE.Scene();
  const backgroundColor = model.get("background_color");
  scene.background = new THREE.Color(backgroundColor);

  // Setup camera
  const camera = new THREE.PerspectiveCamera(
    50, // FOV
    width / height, // Aspect ratio
    0.1, // Near plane
    10000 // Far plane
  );

  // Setup renderer
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(window.devicePixelRatio);
  container.appendChild(renderer.domElement);

  // Setup orbit controls
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.screenSpacePanning = false;
  controls.minDistance = 1;
  controls.maxDistance = 5000;

  // Add lights
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);

  const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.5);
  directionalLight1.position.set(1, 1, 1);
  scene.add(directionalLight1);

  const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.3);
  directionalLight2.position.set(-1, -1, -1);
  scene.add(directionalLight2);

  // Add coordinate axes if enabled
  if (model.get("show_axes")) {
    const axesHelper = new THREE.AxesHelper(100);
    scene.add(axesHelper);
  }

  // Mesh group to hold CAD geometry
  let meshGroup = new THREE.Group();
  scene.add(meshGroup);

  // Function to create geometry from mesh data
  function createGeometry(meshData) {
    // Clear existing meshes
    while (meshGroup.children.length > 0) {
      const child = meshGroup.children[0];
      if (child.geometry) child.geometry.dispose();
      if (child.material) child.material.dispose();
      meshGroup.remove(child);
    }

    // Check for error message
    const errorMessage = model.get("error_message");
    if (errorMessage) {
      console.error("CAD Viewer Error:", errorMessage);
      const errorDiv = document.createElement("div");
      errorDiv.className = "cad-viewer-error";
      errorDiv.textContent = `Error: ${errorMessage}`;
      container.insertBefore(errorDiv, container.firstChild);
      return;
    }

    // Check if mesh data exists
    if (!meshData || !meshData.vertices || meshData.vertices.length === 0) {
      return;
    }

    // Create buffer geometry
    const geometry = new THREE.BufferGeometry();

    // Set vertices
    const vertices = new Float32Array(meshData.vertices);
    geometry.setAttribute("position", new THREE.BufferAttribute(vertices, 3));

    // Set indices
    if (meshData.indices && meshData.indices.length > 0) {
      const indices = new Uint32Array(meshData.indices);
      geometry.setIndex(new THREE.BufferAttribute(indices, 1));
    }

    // Set normals
    if (meshData.normals && meshData.normals.length > 0) {
      const normals = new Float32Array(meshData.normals);
      geometry.setAttribute("normal", new THREE.BufferAttribute(normals, 3));
    } else {
      geometry.computeVertexNormals();
    }

    // Set colors if present
    if (meshData.colors && meshData.colors.length > 0) {
      const colors = new Float32Array(meshData.colors);
      geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    }

    // Create material
    const material = new THREE.MeshStandardMaterial({
      color: 0xcccccc,
      metalness: 0.1,
      roughness: 0.6,
      side: THREE.DoubleSide,
      vertexColors: meshData.colors ? true : false,
    });

    // Create mesh
    const mesh = new THREE.Mesh(geometry, material);
    meshGroup.add(mesh);

    // Add edges if enabled
    if (model.get("show_edges")) {
      const edgesGeometry = new THREE.EdgesGeometry(geometry, 15); // 15 degree threshold
      const edgesMaterial = new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 1 });
      const edges = new THREE.LineSegments(edgesGeometry, edgesMaterial);
      meshGroup.add(edges);
    }

    // Center camera on geometry
    const box = new THREE.Box3().setFromObject(meshGroup);
    const center = box.getCenter(new THREE.Vector3());
    
    // Use camera position from Python model if available, otherwise calculate
    const cameraPos = model.get("camera_position");
    const cameraTarget = model.get("camera_target");
    
    if (cameraPos && cameraPos.length === 3) {
      camera.position.set(cameraPos[0], cameraPos[1], cameraPos[2]);
      controls.target.set(cameraTarget[0], cameraTarget[1], cameraTarget[2]);
    } else {
      // Fallback: calculate from bounding box
      const size = box.getSize(new THREE.Vector3());
      const maxDim = Math.max(size.x, size.y, size.z);
      const fov = camera.fov * (Math.PI / 180);
      const cameraDistance = Math.abs(maxDim / Math.sin(fov / 2)) * 1.5;

      camera.position.set(center.x + cameraDistance, center.y + cameraDistance, center.z + cameraDistance);
      controls.target.copy(center);
    }
    
    camera.lookAt(controls.target);
    controls.update();
  }

  // Initial render
  createGeometry(model.get("mesh_data"));

  // Watch for mesh data changes
  model.on("change:mesh_data", () => {
    createGeometry(model.get("mesh_data"));
  });

  // Watch for background color changes
  model.on("change:background_color", () => {
    scene.background = new THREE.Color(model.get("background_color"));
  });

  // Camera state synchronization to Python model
  let lastSyncTime = 0;
  const SYNC_THROTTLE_MS = 100; // Sync camera state every 100ms max

  function syncCameraState() {
    const now = Date.now();
    if (now - lastSyncTime < SYNC_THROTTLE_MS) {
      return;
    }
    lastSyncTime = now;

    // Update Python model with current camera state
    const position = camera.position.toArray();
    const target = controls.target.toArray();
    
    model.set("camera_position", position);
    model.set("camera_target", target);
    model.save_changes();
  }

  // Sync camera state on controls change
  controls.addEventListener("change", syncCameraState);

  // Performance monitoring for frame rate
  let frameCount = 0;
  let lastFpsTime = performance.now();
  let currentFps = 60;

  function monitorFPS() {
    frameCount++;
    const now = performance.now();
    const elapsed = now - lastFpsTime;

    // Update FPS every second
    if (elapsed >= 1000) {
      currentFps = Math.round((frameCount * 1000) / elapsed);
      frameCount = 0;
      lastFpsTime = now;

      // Log warning if FPS drops below 30
      if (currentFps < 30) {
        console.warn(`CAD Viewer: Low FPS detected (${currentFps} fps). Consider reducing quality or geometry complexity.`);
      }
    }
  }

  // Animation loop with optimization
  let animationFrameId = null;
  let isInteracting = false;
  let lastRenderTime = 0;
  const TARGET_FPS = 60;
  const FRAME_TIME = 1000 / TARGET_FPS;

  // Track interaction state
  controls.addEventListener("start", () => {
    isInteracting = true;
  });
  controls.addEventListener("end", () => {
    isInteracting = false;
  });

  function animate(currentTime) {
    animationFrameId = requestAnimationFrame(animate);

    // Throttle rendering to target FPS when not interacting
    if (!isInteracting) {
      const elapsed = currentTime - lastRenderTime;
      if (elapsed < FRAME_TIME) {
        return;
      }
      lastRenderTime = currentTime - (elapsed % FRAME_TIME);
    } else {
      lastRenderTime = currentTime;
    }

    controls.update();
    renderer.render(scene, camera);
    monitorFPS();
  }
  animate(performance.now());

  // Cleanup on widget destroy
  return () => {
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
    }
    renderer.dispose();
    while (meshGroup.children.length > 0) {
      const child = meshGroup.children[0];
      if (child.geometry) child.geometry.dispose();
      if (child.material) child.material.dispose();
      meshGroup.remove(child);
    }
  };
}

export default { render };
