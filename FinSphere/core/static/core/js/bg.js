import * as THREE from 'three';
const canvas = document.getElementById('bg');
const hero = document.body.dataset.scene === 'hero';
const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x070b1a, 0.03);
const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 200);
camera.position.z = 14;

scene.add(new THREE.AmbientLight(0x6677aa, 1.2));
const l1 = new THREE.PointLight(0x5eead4, 120, 60); l1.position.set(6, 6, 8); scene.add(l1);
const l2 = new THREE.PointLight(0x8b5cf6, 120, 60); l2.position.set(-8, -4, 6); scene.add(l2);

// starfield of "data points"
const N = 1600, pos = new Float32Array(N * 3);
for (let i = 0; i < pos.length; i++) pos[i] = (Math.random() - 0.5) * 70;
const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
const stars = new THREE.Points(pg, new THREE.PointsMaterial({ size: 0.07, color: 0x7fe9ff, transparent: true, opacity: 0.85 }));
scene.add(stars);

// hero object: stacked gold coins inside a glowing torus-knot
const obj = new THREE.Group();
const gold = new THREE.MeshStandardMaterial({ color: 0xffc857, metalness: 0.95, roughness: 0.22, emissive: 0x3a2200 });
for (let i = 0; i < 7; i++) {
  const c = new THREE.Mesh(new THREE.CylinderGeometry(1.3, 1.3, 0.26, 56), gold);
  c.position.y = i * 0.32 - 1; c.rotation.y = i * 0.45; obj.add(c);
}
const knot = new THREE.Mesh(new THREE.TorusKnotGeometry(3, 0.05, 260, 10, 2, 3),
  new THREE.MeshStandardMaterial({ color: 0x8b5cf6, emissive: 0x5b2fe0 }));
obj.add(knot);
const ring = new THREE.Mesh(new THREE.TorusGeometry(4, 0.02, 8, 120), new THREE.MeshBasicMaterial({ color: 0x5eead4 }));
ring.rotation.x = Math.PI / 2.4; obj.add(ring);
scene.add(obj);

let mx = 0, my = 0;
addEventListener('pointermove', e => { mx = e.clientX / innerWidth - 0.5; my = e.clientY / innerHeight - 0.5; });
function resize() {
  renderer.setSize(innerWidth, innerHeight, false);
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  const wide = innerWidth > 900;
  obj.position.set(hero && wide ? 5.5 : wide ? 9 : 0, hero ? 0 : wide ? 1 : 7, hero ? 0 : -6);
  obj.scale.setScalar(hero ? (wide ? 1 : 0.6) : 0.7);
}
addEventListener('resize', resize); resize();

const clock = new THREE.Clock();
(function loop() {
  const t = clock.getElapsedTime();
  if (!still) {
    obj.rotation.y = t * 0.35; knot.rotation.x = t * 0.2; ring.rotation.z = t * 0.5;
    obj.position.y += (Math.sin(t) * 0.25 - (obj.position.y - (hero ? 0 : 1))) * 0.02;
    stars.rotation.y = t * 0.012;
  }
  camera.position.x += (mx * 3 - camera.position.x) * 0.04;
  camera.position.y += (-my * 2 - camera.position.y) * 0.04;
  camera.lookAt(0, 0, 0);
  renderer.render(scene, camera);
  requestAnimationFrame(loop);
})();
