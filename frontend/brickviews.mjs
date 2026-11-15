/**
 * The inspected brick from four viewpoints in one canvas (top, front, side, rotating 3D), with the defect marked
 * on the face where it is. In demo mode the brick is illustrative; the live camera crop is shown beside it.
 */
import * as THREE from './vendor/three.module.min.mjs';

const W = 1.6, H = 0.96, D = 0.8;
const TONES = {normal: 0x39ff6a, defective: 0xff4136, uncertain: 0xffb52e, none: 0x22b84a};
export const BRICK_COLOURS = [0xd8402f, 0xf2c230, 0x2f7fd8, 0x2fa84f];

/** Where a defect sits: face, position on that face and kind (grey tape or black marker). */
const FACES = {
	top: {normal: [0, 1, 0], at: (u, v) => [u * W * 0.35, H / 2 + 0.006, v * D * 0.3], rot: [-Math.PI / 2, 0, 0]},
	front: {normal: [0, 0, 1], at: (u, v) => [u * W * 0.35, v * H * 0.3, D / 2 + 0.006], rot: [0, 0, 0]},
	side: {normal: [1, 0, 0], at: (u, v) => [W / 2 + 0.006, v * H * 0.3, u * D * 0.3], rot: [0, Math.PI / 2, 0]},
};

export class BrickViews {
	constructor(canvas) {
		this.canvas = canvas;
		this.renderer = new THREE.WebGLRenderer({canvas, antialias: true, alpha: false});
		this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
		this.renderer.setScissorTest(true);
		this.scene = new THREE.Scene();
		this.scene.add(new THREE.HemisphereLight(0xffffff, 0x0a120c, 0.75 * Math.PI));
		const key = new THREE.DirectionalLight(0xffffff, 0.8 * Math.PI); key.position.set(2, 4, 3); this.scene.add(key);
		const fill = new THREE.DirectionalLight(0x9fffbf, 0.25 * Math.PI); fill.position.set(-3, 1, -2); this.scene.add(fill);
		const grid = new THREE.GridHelper(6, 24, 0x1f5c2e, 0x0d2614); grid.position.y = -H / 2 - 0.001; this.scene.add(grid);
		this.brick = new THREE.Group(); this.scene.add(this.brick);
		const ortho = () => new THREE.OrthographicCamera(-1.4, 1.4, 1, -1, 0.1, 20);
		this.views = [
			{name: 'TOP', camera: ortho(), place: c => { c.position.set(0, 6, 0.0001); c.lookAt(0, 0, 0); }},
			{name: 'FRONT', camera: ortho(), place: c => { c.position.set(0, 0, 6); c.lookAt(0, 0, 0); }},
			{name: 'SIDE', camera: ortho(), place: c => { c.position.set(6, 0, 0); c.lookAt(0, 0, 0); }},
			{name: '3D', camera: new THREE.PerspectiveCamera(32, 1, 0.1, 30), place: (c, t) => {
				const a = t * 0.00035; c.position.set(Math.sin(a) * 4.4, 2.4, Math.cos(a) * 4.4); c.lookAt(0, 0, 0);
			}},
		];
		this.show({label: 'none', colour: BRICK_COLOURS[0], defect: null});
		new ResizeObserver(() => this.#resize()).observe(canvas);
		this.#resize();
		const loop = now => { this.#render(now); requestAnimationFrame(loop); };
		requestAnimationFrame(loop);
	}

	/** Show a brick: ``label`` colours the outline, ``defect`` = {face, u, v, kind} or null. */
	show({label = 'none', colour = BRICK_COLOURS[0], defect = null}) {
		this.brick.clear();
		const material = new THREE.MeshStandardMaterial({color: colour, roughness: 0.35, metalness: 0.05});
		const body = new THREE.Mesh(new THREE.BoxGeometry(W, H, D), material);
		this.brick.add(body);
		const tone = TONES[label] ?? TONES.none;
		this.brick.add(new THREE.LineSegments(new THREE.EdgesGeometry(body.geometry), new THREE.LineBasicMaterial({color: tone})));
		const stud = new THREE.CylinderGeometry(0.15, 0.15, 0.17, 24);
		for (let i = 0; i < 4; i++) for (let j = 0; j < 2; j++) {
			const s = new THREE.Mesh(stud, material); s.position.set(-0.6 + i * 0.4, H / 2 + 0.085, -0.2 + j * 0.4); this.brick.add(s);
		}
		this.defect = null;
		if (defect && FACES[defect.face]) {
			const face = FACES[defect.face];
			const mark = new THREE.Mesh(
				defect.kind === 'marker' ? new THREE.PlaneGeometry(0.5, 0.06) : new THREE.PlaneGeometry(0.42, 0.16),
				new THREE.MeshStandardMaterial({color: defect.kind === 'marker' ? 0x111111 : 0xa3a8a5, roughness: 0.95, side: THREE.DoubleSide}),
			);
			mark.position.set(...face.at(defect.u ?? 0.2, defect.v ?? 0.1));
			mark.rotation.set(...face.rot); mark.rotateZ(defect.kind === 'marker' ? 0.5 : -0.25);
			this.brick.add(mark);
			const ring = new THREE.Mesh(new THREE.RingGeometry(0.34, 0.38, 48), new THREE.MeshBasicMaterial({color: tone, side: THREE.DoubleSide, transparent: true, opacity: 0.95}));
			ring.position.copy(mark.position).addScaledVector(new THREE.Vector3(...face.normal), 0.004);
			ring.rotation.set(...face.rot);
			this.brick.add(ring);
			this.defect = {ring, face: defect.face};
		}
	}

	#resize() {
		const {width, height} = this.canvas.getBoundingClientRect();
		this.renderer.setSize(width, height, false);
		this.size = {width, height};
	}

	#render(now) {
		const {width, height} = this.size;
		if (!width || !height) return;
		const halfW = width / 2, halfH = height / 2;
		const gap = 3;
		this.views.forEach((view, i) => {
			const x = (i % 2) * halfW, y = (i < 2 ? halfH : 0);
			const w = halfW - gap, h = halfH - gap;
			this.renderer.setViewport(x, y, w, h); this.renderer.setScissor(x, y, w, h);
			this.renderer.setClearColor(i === 3 ? 0x050b07 : 0x030604);
			const c = view.camera;
			if (c.isOrthographicCamera) {
				const aspect = w / h, span = 1.25;
				c.left = -span * aspect; c.right = span * aspect; c.top = span; c.bottom = -span; c.updateProjectionMatrix();
			} else { c.aspect = w / h; c.updateProjectionMatrix(); }
			view.place(c, now);
			if (this.defect) this.defect.ring.material.opacity = 0.55 + 0.45 * Math.abs(Math.sin(now / 350));
			this.renderer.render(this.scene, c);
		});
	}
}

/** A defect placement for a demo part, from a seed so a demo cycle stays consistent across views. */
export function demoDefect(label, seed) {
	if (label === 'normal') return null;
	const faces = ['top', 'front', 'side'], r = n => ((Math.sin(seed * 9301 + n * 49297) + 1) / 2);
	return {face: faces[Math.floor(r(1) * 3) % 3], u: r(2) * 2 - 1, v: r(3) * 2 - 1, kind: label === 'uncertain' ? 'marker' : (r(4) > 0.5 ? 'tape' : 'marker')};
}
