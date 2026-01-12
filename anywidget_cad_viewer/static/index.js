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
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = camera.fov * (Math.PI / 180);
    const cameraDistance = Math.abs(maxDim / Math.sin(fov / 2)) * 1.5;

    camera.position.set(center.x + cameraDistance, center.y + cameraDistance, center.z + cameraDistance);
    camera.lookAt(center);
    controls.target.copy(center);
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

  // Animation loop
  function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }
  animate();

  // Cleanup on widget destroy
  return () => {
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
