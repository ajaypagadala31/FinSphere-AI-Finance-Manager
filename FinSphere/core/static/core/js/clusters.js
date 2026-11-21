import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
const data = JSON.parse(document.getElementById('cluster-data').textContent);
const host = document.getElementById('cluster3d'), tip = document.getElementById('tip');
const COL = [0xff6b8b, 0x5eead4, 0x8b5cf6, 0xffc857, 0x7fb0ff];
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); host.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 100); camera.position.set(6, 4, 9);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.autoRotate = true; controls.autoRotateSpeed = 1.2;
renderer.domElement.addEventListener('pointerdown', () => controls.autoRotate = false);
scene.add(new THREE.AmbientLight(0xffffff, 1.4)); const pl = new THREE.PointLight(0xffffff, 200, 50); pl.position.set(5, 8, 6); scene.add(pl);

const grid = new THREE.GridHelper(10, 10, 0x3b4a8f, 0x1f2a5c); grid.position.y = -3.2; scene.add(grid);
scene.add(new THREE.AxesHelper(3.5));
const maxT = Math.max(...data.map(d => d.total));
const meshes = [];
function label(text) {
  const c = document.createElement('canvas'); c.width = 256; c.height = 64; const g = c.getContext('2d');
  g.fillStyle = '#e8ecff'; g.font = '600 28px sans-serif'; g.textAlign = 'center'; g.fillText(text, 128, 40);
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthTest: false }));
  s.scale.set(2.2, .55, 1); return s;
}
data.forEach(d => {
  const r = 0.2 + 0.55 * Math.sqrt(d.total / maxT);
  const m = new THREE.Mesh(new THREE.SphereGeometry(r, 32, 24),
    new THREE.MeshStandardMaterial({ color: COL[d.cluster % 5], metalness: .3, roughness: .25, emissive: COL[d.cluster % 5], emissiveIntensity: .25 }));
  m.position.set(d.x * 3.5, d.y * 3, d.z * 3.5); m.userData = d; scene.add(m); meshes.push(m);
  const l = label(d.category); l.position.set(m.position.x, m.position.y + r + .4, m.position.z); scene.add(l);
  const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints([m.position, new THREE.Vector3(m.position.x, -3.2, m.position.z)]),
    new THREE.LineBasicMaterial({ color: COL[d.cluster % 5], transparent: true, opacity: .25 })); scene.add(line);
});
const ray = new THREE.Raycaster(), ptr = new THREE.Vector2(2, 2);
host.addEventListener('pointermove', e => {
  const b = host.getBoundingClientRect(); ptr.set(((e.clientX - b.left) / b.width) * 2 - 1, -((e.clientY - b.top) / b.height) * 2 + 1);
  tip.style.left = e.clientX - b.left + 14 + 'px'; tip.style.top = e.clientY - b.top + 14 + 'px';
});
function size() { const w = host.clientWidth, h = host.clientHeight; renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix(); }
addEventListener('resize', size); size();
(function loop() {
  controls.update(); ray.setFromCamera(ptr, camera);
  const hit = ray.intersectObjects(meshes)[0];
  meshes.forEach(m => m.scale.setScalar(hit && hit.object === m ? 1.25 : 1));
  if (hit) { const d = hit.object.userData; tip.innerHTML = `<b>${d.category}</b> · ${d.label}<br>Total ${d.total.toLocaleString()} · ${d.count} txns`; tip.style.opacity = 1; } else tip.style.opacity = 0;
  renderer.render(scene, camera); requestAnimationFrame(loop);
})();
