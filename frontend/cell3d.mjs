/**
 * Illustrative 3D sorting cell (three.js, vendored). It animates the demo stages and carries the guided tour's
 * annotations. The arm is a presentation model with its own inverse kinematics, not calibrated SO-101 kinematics,
 * and it never mirrors or commands the real robot.
 */
import * as THREE from './vendor/three.module.min.mjs';

const C = {g: 0x39ff6a, red: 0xff4136, amber: 0xffb52e, bg: 0x030504};
const POS = {
	robot: new THREE.Vector3(1.0, 0, -0.9), spot: new THREE.Vector3(0, 0, 0.7),
	green: new THREE.Vector3(-1.9, 0, -1.1), pink: new THREE.Vector3(2.5, 0, 1.0),
	review: new THREE.Vector3(-1.9, 0, 1.4), laptop: new THREE.Vector3(3.0, 0, -1.6),
};
const BRICK = {w: 0.8, h: 0.36, d: 0.5};
const L1 = 2.2, L2 = 2.1, SH = 1.05, G = 0.5;
const VIEWS = {
	home: {az: -0.32, el: 0.62, dist: 11.8, target: [0.3, 0.4, 0.1]},
	camera: {az: -0.55, el: 0.42, dist: 7.5, target: [-0.6, 2.0, 0.2]},
	brick: {az: -0.2, el: 0.75, dist: 5.2, target: [0, 0.2, 0.7]},
	bins: {az: -0.05, el: 0.95, dist: 10.5, target: [0.2, 0, 0.1]},
	arm: {az: 0.35, el: 0.45, dist: 8.5, target: [1.0, 1.2, -0.4]},
	laptop: {az: 0.6, el: 0.55, dist: 6.0, target: [2.6, 0.4, -1.4]},
};
const ease = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const reduceMotion = () => globalThis.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

export class Cell3D {
	constructor(canvas, overlay) {
		this.canvas = canvas; this.overlay = overlay;
		this.renderer = new THREE.WebGLRenderer({canvas, antialias: true});
		this.renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
		this.renderer.shadowMap.enabled = true;
		this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
		this.scene = new THREE.Scene();
		this.scene.background = new THREE.Color(C.bg);
		this.scene.fog = new THREE.Fog(C.bg, 15, 32);
		this.camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
		this.view = {...VIEWS.home, target: new THREE.Vector3(...VIEWS.home.target)};
		this.anchors = {};
		this.annotations = [];
		this.placed = {green: [], pink: []};
		this.brick = null; this.carried = null;
		this.tip = new THREE.Vector3(); this.grip = 1;
		this.lastEpisode = null; this.lastStage = null; this.busy = Promise.resolve();
		this.#build();
		this.#controls();
		new ResizeObserver(() => this.#resize()).observe(canvas.parentElement);
		this.#resize();
		const loop = now => { this.#frame(now); requestAnimationFrame(loop); };
		requestAnimationFrame(loop);
	}

	// ---------------------------------------------------------------- scene
	#mat(color, o = {}) { return new THREE.MeshStandardMaterial({color, roughness: 0.6, metalness: 0.2, ...o}); }
	#mesh(geo, material, cast = true) { const m = new THREE.Mesh(geo, material); m.castShadow = cast; m.receiveShadow = true; return m; }
	#edges(m, color = C.g, opacity = 0.5) {
		m.add(new THREE.LineSegments(new THREE.EdgesGeometry(m.geometry), new THREE.LineBasicMaterial({color, transparent: true, opacity})));
		return m;
	}
	#glow(color) { return new THREE.MeshBasicMaterial({color}); }

	#build() {
		const s = this.scene;
		s.add(new THREE.HemisphereLight(0xcfe8d6, 0x0a120c, 0.7 * Math.PI));
		const sun = new THREE.DirectionalLight(0xffffff, 0.9 * Math.PI);
		sun.position.set(-4, 10, 6); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
		Object.assign(sun.shadow.camera, {left: -7, right: 7, top: 7, bottom: -7});
		s.add(sun);
		this.spotLight = new THREE.PointLight(C.g, 0, 6, 0); this.spotLight.position.set(0, 3.4, 0.7); s.add(this.spotLight);

		const floor = this.#mesh(new THREE.PlaneGeometry(60, 60), this.#mat(0x050806, {metalness: 0}), false);
		floor.rotation.x = -Math.PI / 2; floor.position.y = -0.9; s.add(floor);
		const grid = new THREE.GridHelper(40, 40, 0x1f5c2e, 0x0e2a15); grid.position.y = -0.89; s.add(grid);
		const table = this.#edges(this.#mesh(new THREE.BoxGeometry(8.6, 0.25, 5.6), this.#mat(0x0b110d, {roughness: 0.85}), false), C.g, 0.7);
		table.position.y = -0.125; s.add(table);
		const tgrid = new THREE.GridHelper(5.6, 14, 0x154a23, 0x0d2614); tgrid.scale.x = 8.6 / 5.6; tgrid.position.y = 0.004; s.add(tgrid);
		for (const [x, z] of [[-4, -2.5], [4, -2.5], [-4, 2.5], [4, 2.5]]) {
			const leg = this.#mesh(new THREE.BoxGeometry(0.2, 0.65, 0.2), this.#mat(0x111713)); leg.position.set(x, -0.57, z); s.add(leg);
		}
		this.bins = {green: this.#bin(C.g, POS.green), pink: this.#bin(C.red, POS.pink)};
		this.#reviewMark();
		this.#spotMarker();
		this.#cameraMast();
		this.#laptop();
		this.#arm();
		this.tip.copy(this.home);
		Object.assign(this.anchors, {
			green: POS.green.clone().setY(0.5), pink: POS.pink.clone().setY(0.5), review: POS.review.clone().setY(0.05),
			spot: POS.spot.clone().setY(0.4), camera: new THREE.Vector3(POS.spot.x, 3.95, POS.spot.z), laptop: POS.laptop.clone().setY(0.9),
		});
	}

	#bin(color, at) {
		const pts = [], R = 0.95, H = 0.45;
		for (let i = 0; i <= 12; i++) { const t = i / 12; pts.push(new THREE.Vector2(0.45 + (R - 0.45) * Math.sin(t * Math.PI / 2), H * (1 - Math.cos(t * Math.PI / 2)))); }
		for (let i = 12; i >= 0; i--) { const t = i / 12; pts.push(new THREE.Vector2(0.40 + (R - 0.47) * Math.sin(t * Math.PI / 2), 0.05 + (H - 0.02) * (1 - Math.cos(t * Math.PI / 2)))); }
		const g = new THREE.Group();
		g.add(this.#mesh(new THREE.LatheGeometry(pts, 48), this.#mat(0x1a201c, {roughness: 0.4, metalness: 0.5, side: THREE.DoubleSide})));
		const rim = new THREE.Mesh(new THREE.TorusGeometry(R - 0.035, 0.03, 8, 64), this.#glow(color));
		rim.rotation.x = Math.PI / 2; rim.position.y = H; g.add(rim);
		const light = new THREE.PointLight(color, 0.6, 2.4, 0); light.position.y = 0.6; g.add(light);
		g.position.copy(at); this.scene.add(g);
		return {group: g, rim, light};
	}

	#reviewMark() {
		const c = document.createElement('canvas'); c.width = c.height = 256;
		const x = c.getContext('2d');
		x.fillStyle = '#0b0b0b'; x.fillRect(0, 0, 256, 256);
		x.strokeStyle = '#ffb52e'; x.lineWidth = 22;
		for (let i = -256; i < 512; i += 52) { x.beginPath(); x.moveTo(i, 256); x.lineTo(i + 256, 0); x.stroke(); }
		const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
		const p = this.#mesh(new THREE.PlaneGeometry(1.5, 1.2), new THREE.MeshStandardMaterial({map: tex, roughness: 0.8, emissive: 0x2a1c00, emissiveMap: tex}), false);
		p.rotation.x = -Math.PI / 2; p.position.copy(POS.review); p.position.y = 0.007; this.scene.add(p);
	}

	#spotMarker() {
		const g = new THREE.Group(), m = this.#glow(C.g), s = 0.95, dash = 0.17, gap = 0.12;
		for (let side = 0; side < 4; side++) {
			for (let d = -s / 2; d < s / 2 - 0.02; d += dash + gap) {
				const len = Math.min(dash, s / 2 - d), mid = d + len / 2;
				const b = new THREE.Mesh(new THREE.BoxGeometry(len, 0.01, 0.035), m);
				if (side < 2) b.position.set(mid, 0, side ? s / 2 : -s / 2);
				else { b.position.set(side === 2 ? -s / 2 : s / 2, 0, mid); b.rotation.y = Math.PI / 2; }
				g.add(b);
			}
		}
		g.position.copy(POS.spot); g.position.y = 0.008; this.scene.add(g);
	}

	#cameraMast() {
		const black = this.#mat(0x151a17, {metalness: 0.5});
		const pole = this.#mesh(new THREE.CylinderGeometry(0.07, 0.07, 4.2, 16), black); pole.position.set(-2.6, 2.1, -1.9); this.scene.add(pole);
		const len = Math.hypot(POS.spot.x + 2.6, POS.spot.z + 1.9);
		const boom = this.#mesh(new THREE.CylinderGeometry(0.05, 0.05, len, 12), black); boom.rotation.z = Math.PI / 2; boom.position.x = len / 2;
		const arm = new THREE.Group(); arm.position.set(-2.6, 4.1, -1.9); arm.rotation.y = -Math.atan2(POS.spot.z + 1.9, POS.spot.x + 2.6); arm.add(boom); this.scene.add(arm);
		const body = this.#edges(this.#mesh(new THREE.BoxGeometry(0.35, 0.25, 0.35), black)); body.position.set(POS.spot.x, 3.95, POS.spot.z); this.scene.add(body);
		this.lens = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.12, 16), this.#glow(0x0f3d1b));
		this.lens.position.set(POS.spot.x, 3.78, POS.spot.z); this.scene.add(this.lens);
		this.cone = new THREE.Mesh(new THREE.ConeGeometry(0.75, 3.6, 32, 1, true),
			new THREE.MeshBasicMaterial({color: C.g, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false}));
		this.cone.position.set(POS.spot.x, 1.95, POS.spot.z); this.scene.add(this.cone);
		this.scan = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 1.1), new THREE.MeshBasicMaterial({color: C.g, transparent: true, opacity: 0, side: THREE.DoubleSide, depthWrite: false}));
		this.scan.rotation.x = -Math.PI / 2; this.scan.position.copy(POS.spot); this.scene.add(this.scan);
	}

	#laptop() {
		const g = new THREE.Group();
		const base = this.#edges(this.#mesh(new THREE.BoxGeometry(1.5, 0.06, 1.0), this.#mat(0x1b2220, {metalness: 0.6})), C.g, 0.35);
		base.position.y = 0.03; g.add(base);
		const lid = new THREE.Group(); lid.position.set(0, 0.06, -0.5); lid.rotation.x = -0.32; g.add(lid);
		const screen = this.#edges(this.#mesh(new THREE.BoxGeometry(1.5, 0.95, 0.04), this.#mat(0x1b2220, {metalness: 0.6})), C.g, 0.35);
		screen.position.y = 0.475; lid.add(screen);
		const c = document.createElement('canvas'); c.width = 256; c.height = 160;
		this.laptopCanvas = c;
		this.laptopTex = new THREE.CanvasTexture(c); this.laptopTex.colorSpace = THREE.SRGBColorSpace;
		const display = new THREE.Mesh(new THREE.PlaneGeometry(1.36, 0.82), new THREE.MeshBasicMaterial({map: this.laptopTex}));
		display.position.set(0, 0.475, 0.025); lid.add(display);
		this.chips = ['CPU', 'GPU', 'NPU'].map((name, i) => {
			const chip = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.02, 0.22), this.#glow(0x0f3d1b));
			chip.position.set(-0.4 + i * 0.4, 0.07, 0.15); g.add(chip); return chip;
		});
		g.position.copy(POS.laptop); g.rotation.y = -0.5; this.scene.add(g);
		this.#drawLaptop(null);
	}

	#drawLaptop(text) {
		const x = this.laptopCanvas.getContext('2d');
		x.fillStyle = '#021005'; x.fillRect(0, 0, 256, 160);
		x.fillStyle = '#39ff6a'; x.font = '18px monospace';
		x.fillText('ARMIGO EDGE', 16, 30);
		x.font = '14px monospace'; x.fillStyle = '#22b84a';
		(text ?? 'idle · local inference').split('\n').forEach((line, i) => x.fillText(line, 16, 62 + i * 22));
		this.laptopTex.needsUpdate = true;
	}

	#arm() {
		const metal = this.#mat(0x2c332e, {roughness: 0.35, metalness: 0.7}), black = this.#mat(0x0e120f, {roughness: 0.5, metalness: 0.4});
		const ring = r => new THREE.Mesh(new THREE.TorusGeometry(r, 0.025, 8, 40), this.#glow(C.g));
		const robot = new THREE.Group(); robot.position.copy(POS.robot); this.scene.add(robot);
		const base = this.#edges(this.#mesh(new THREE.CylinderGeometry(0.62, 0.7, 0.3, 40), black), C.g, 0.25); base.position.y = 0.15; robot.add(base);
		const baseRing = ring(0.64); baseRing.rotation.x = Math.PI / 2; baseRing.position.y = 0.3; robot.add(baseRing);
		this.yaw = new THREE.Group(); this.yaw.position.y = 0.3; robot.add(this.yaw);
		const tower = this.#mesh(new THREE.CylinderGeometry(0.38, 0.42, SH - 0.3, 32), metal); tower.position.y = (SH - 0.3) / 2; this.yaw.add(tower);
		this.shoulder = new THREE.Group(); this.shoulder.position.y = SH - 0.3; this.yaw.add(this.shoulder);
		this.shoulder.add(this.#edges(this.#mesh(new THREE.BoxGeometry(0.5, 0.5, 0.55), black), C.g, 0.4));
		const r1 = ring(0.2); r1.position.z = 0.29; this.shoulder.add(r1);
		this.shoulder.add(this.#edges(this.#mesh(new THREE.BoxGeometry(L1, 0.34, 0.36).translate(L1 / 2, 0, 0), metal), C.g, 0.18));
		const s1 = new THREE.Mesh(new THREE.BoxGeometry(L1 * 0.6, 0.03, 0.01), this.#glow(C.g)); s1.position.set(L1 / 2, 0, 0.185); this.shoulder.add(s1);
		this.elbow = new THREE.Group(); this.elbow.position.x = L1; this.shoulder.add(this.elbow);
		this.elbow.add(this.#edges(this.#mesh(new THREE.BoxGeometry(0.46, 0.46, 0.5), black), C.g, 0.4));
		const r2 = ring(0.18); r2.position.z = 0.26; this.elbow.add(r2);
		this.elbow.add(this.#edges(this.#mesh(new THREE.BoxGeometry(L2, 0.28, 0.3).translate(L2 / 2, 0, 0), metal), C.g, 0.18));
		const s2 = new THREE.Mesh(new THREE.BoxGeometry(L2 * 0.6, 0.03, 0.01), this.#glow(C.g)); s2.position.set(L2 / 2, 0, 0.155); this.elbow.add(s2);
		this.wrist = new THREE.Group(); this.wrist.position.x = L2; this.elbow.add(this.wrist);
		this.wrist.add(this.#edges(this.#mesh(new THREE.BoxGeometry(0.36, 0.36, 0.4), black), C.g, 0.4));
		const palm = this.#mesh(new THREE.BoxGeometry(0.16, 0.3, 1.05), black); palm.position.x = 0.2; this.wrist.add(palm);
		const finger = new THREE.BoxGeometry(0.48, 0.12, 0.09).translate(0.24, 0, 0);
		this.fingers = [this.#mesh(finger, metal), this.#mesh(finger, metal)];
		this.fingers.forEach(f => { f.position.x = 0.26; this.wrist.add(f); });
		this.statusRing = baseRing;
		this.home = new THREE.Vector3(POS.robot.x - 0.6, 2.3, POS.robot.z + 1.4);
		this.anchors.arm = new THREE.Vector3(); this.anchors.base = POS.robot.clone().setY(0.4);
	}

	#solve() {
		const d = this.tip.clone().sub(POS.robot);
		this.yaw.rotation.y = Math.atan2(-d.z, d.x);
		const r = Math.hypot(d.x, d.z), wy = d.y + G - SH;
		const dist = THREE.MathUtils.clamp(Math.hypot(r, wy), Math.abs(L1 - L2) + 0.05, L1 + L2 - 0.001);
		const a2 = Math.acos(THREE.MathUtils.clamp((dist * dist - L1 * L1 - L2 * L2) / (2 * L1 * L2), -1, 1));
		const a1 = Math.atan2(wy, r) + Math.atan2(L2 * Math.sin(a2), L1 + L2 * Math.cos(a2));
		this.shoulder.rotation.z = a1; this.elbow.rotation.z = -a2; this.wrist.rotation.z = -Math.PI / 2 - (a1 - a2);
		const z = BRICK.d / 2 + 0.05 + this.grip * 0.16;
		this.fingers[0].position.z = z; this.fingers[1].position.z = -z;
		this.anchors.arm.copy(this.tip).add(new THREE.Vector3(0, 0.7, 0));
	}

	#makeBrick(color, defect) {
		const g = new THREE.Group(), material = this.#mat(color, {roughness: 0.35, metalness: 0.1});
		g.add(this.#mesh(new THREE.BoxGeometry(BRICK.w, BRICK.h, BRICK.d), material));
		const stud = new THREE.CylinderGeometry(0.075, 0.075, 0.07, 20);
		for (let i = 0; i < 4; i++) for (let j = 0; j < 2; j++) {
			const s = this.#mesh(stud, material); s.position.set(-0.3 + i * 0.2, BRICK.h / 2 + 0.035, -0.1 + j * 0.2); g.add(s);
		}
		if (defect) {
			const mark = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.012, 0.09), new THREE.MeshStandardMaterial({color: defect === 'tape' ? 0x9aa09c : 0x111111, roughness: 0.9}));
			mark.position.set(0.05, BRICK.h / 2 + 0.008, 0.08); mark.rotation.y = -0.5; g.add(mark);
		}
		this.scene.add(g);
		return g;
	}

	// ---------------------------------------------------------------- motion
	#tween(fn, ms) {
		if (reduceMotion()) ms = Math.min(ms, 60);
		return new Promise(resolve => {
			const t0 = performance.now();
			const step = now => { const t = Math.min(1, (now - t0) / ms); fn(ease(t)); t < 1 ? requestAnimationFrame(step) : resolve(); };
			requestAnimationFrame(step);
		});
	}
	#move(to, ms) { const from = this.tip.clone(); return this.#tween(t => this.tip.lerpVectors(from, to, t), ms); }
	#gripTo(v, ms) { const from = this.grip; return this.#tween(t => { this.grip = from + (v - from) * t; }, ms); }

	async #pickAndPlace(destination) {
		const brick = this.brick; if (!brick) return;
		const pile = this.placed[destination], n = pile.length % 4, layer = Math.floor(pile.length / 4) % 2;
		const c = POS[destination], target = new THREE.Vector3(c.x + (n % 2 ? 0.25 : -0.25), 0.06 + BRICK.h / 2 + layer * BRICK.h, c.z + (n > 1 ? 0.25 : -0.25));
		const above = (p, h) => new THREE.Vector3(p.x, h, p.z), pick = POS.spot.clone().setY(BRICK.h / 2);
		await this.#gripTo(1, 120);
		await this.#move(above(pick, 1.5), 420);
		await this.#move(pick, 280);
		await this.#gripTo(0, 140);
		this.carried = brick;
		await this.#move(above(pick, 1.8), 260);
		await this.#move(above(target, 1.8), 560);
		await this.#move(target, 300);
		this.carried = null; brick.position.copy(target); this.brick = null;
		await this.#gripTo(1, 120);
		pile.push(brick);
		if (pile.length > 8) this.scene.remove(pile.shift());
		this.#flash(this.bins[destination].light, 3);
		await this.#move(above(target, 1.9), 220);
		await this.#move(this.home, 480);
	}

	#flash(light, peak) { const base = light.intensity; this.#tween(t => { light.intensity = base + peak * Math.sin(Math.PI * t); }, 700); }

	/** Follow one demo/live state; animations run once per stage change. */
	setState(state, {brickColor = 0xd8402f, defect = null} = {}) {
		const fresh = state.episode_id !== this.lastEpisode || (state.stage === 'perceive' && this.lastStage !== 'perceive');
		if (fresh && state.mode === 'demo') {
			if (this.brick) { this.scene.remove(this.brick); this.brick = null; }
			this.lastEpisode = state.episode_id;
			if (state.stage !== 'fault') {
				const brick = this.#makeBrick(brickColor, defect);
				brick.position.set(POS.spot.x, 1.6, POS.spot.z); this.brick = brick;
				this.#tween(t => { brick.position.y = 1.6 + (BRICK.h / 2 - 1.6) * t; }, 360);
			}
		}
		if (state.stage === this.lastStage && !fresh) return;
		this.lastStage = state.stage;
		const ringColor = state.stage === 'fault' ? C.red : state.stage === 'review' ? C.amber : C.g;
		this.statusRing.material.color.setHex(ringColor);
		if (state.stage === 'perceive') {
			this.lens.material.color.setHex(C.g);
			this.#tween(t => { this.cone.material.opacity = 0.12 * Math.sin(Math.PI * t); this.spotLight.intensity = 2 * Math.sin(Math.PI * t); }, 1000)
				.then(() => this.lens.material.color.setHex(0x0f3d1b));
		}
		if (state.stage === 'detect') {
			this.chips[2].material.color.setHex(C.g);
			this.#drawLaptop(state.mode === 'demo' ? 'anomaly model\nscoring the crop…' : `anomaly model\n${state.device ?? 'device unverified'}`);
			this.#tween(t => { this.scan.position.y = 0.05 + 0.5 * t; this.scan.material.opacity = 0.35 * Math.sin(Math.PI * t); }, 900)
				.then(() => this.chips[2].material.color.setHex(0x0f3d1b));
		}
		if (state.stage === 'reason' || state.stage === 'review') {
			this.#drawLaptop(`score ${Number.isFinite(state.score) ? state.score.toFixed(2) : '—'}\n→ ${state.destination ? state.destination + ' bowl' : 'human review'}`);
		}
		if (state.stage === 'act' && state.mode === 'demo' && state.destination && state.destination !== 'blue') {
			this.busy = this.busy.then(() => this.#pickAndPlace(state.destination));
		}
	}

	focus(name, ms = 1100) {
		const v = VIEWS[name] ?? VIEWS.home, from = {...this.view, target: this.view.target.clone()};
		const to = new THREE.Vector3(...v.target);
		return this.#tween(t => {
			this.view.az = from.az + (v.az - from.az) * t; this.view.el = from.el + (v.el - from.el) * t;
			this.view.dist = from.dist + (v.dist - from.dist) * t; this.view.target.lerpVectors(from.target, to, t);
		}, ms);
	}
	reset() { return this.focus('home', 600); }

	/** Annotations pinned to scene anchors: [{anchor:'camera', title, text, tone:'green'|'amber'|'red'}]. */
	annotate(list = []) {
		this.overlay.replaceChildren();
		this.annotations = list.map((a, i) => {
			const el = document.createElement('div');
			el.className = `annotation tone-${a.tone ?? 'green'}`;
			el.style.setProperty('--delay', `${i * 120}ms`);
			el.innerHTML = '<i></i><div><b></b><span></span></div>';
			el.querySelector('b').textContent = a.title; el.querySelector('span').textContent = a.text ?? '';
			this.overlay.append(el);
			return {...a, el};
		});
	}

	// ---------------------------------------------------------------- input + render
	#controls() {
		let drag = null;
		this.canvas.addEventListener('pointerdown', e => { drag = {x: e.clientX, y: e.clientY}; this.canvas.setPointerCapture(e.pointerId); });
		this.canvas.addEventListener('pointermove', e => {
			if (!drag) return;
			this.view.az -= (e.clientX - drag.x) * 0.006;
			this.view.el = THREE.MathUtils.clamp(this.view.el + (e.clientY - drag.y) * 0.005, 0.12, 1.35);
			drag = {x: e.clientX, y: e.clientY};
		});
		this.canvas.addEventListener('pointerup', () => { drag = null; });
		this.canvas.addEventListener('wheel', e => { e.preventDefault(); this.view.dist = THREE.MathUtils.clamp(this.view.dist * (1 + e.deltaY * 0.001), 4.5, 18); }, {passive: false});
		this.canvas.addEventListener('keydown', e => {
			const step = {ArrowLeft: [0.08, 0], ArrowRight: [-0.08, 0], ArrowUp: [0, 0.06], ArrowDown: [0, -0.06]}[e.key];
			if (!step) return;
			e.preventDefault(); this.view.az += step[0]; this.view.el = THREE.MathUtils.clamp(this.view.el + step[1], 0.12, 1.35);
		});
	}

	#resize() {
		const box = this.canvas.parentElement.getBoundingClientRect();
		this.renderer.setSize(box.width, box.height, false);
		this.camera.aspect = box.width / Math.max(1, box.height); this.camera.updateProjectionMatrix();
	}

	#frame(now) {
		const {az, el, dist, target} = this.view;
		this.camera.position.set(target.x + dist * Math.cos(el) * Math.sin(az), target.y + dist * Math.sin(el), target.z + dist * Math.cos(el) * Math.cos(az));
		this.camera.lookAt(target);
		this.#solve();
		if (this.carried) this.carried.position.copy(this.tip);
		if (!reduceMotion()) this.statusRing.scale.setScalar(1 + 0.03 * Math.sin(now / 400));
		this.renderer.render(this.scene, this.camera);
		const w = this.canvas.clientWidth, h = this.canvas.clientHeight;
		for (const a of this.annotations) {
			const p = this.anchors[a.anchor]?.clone().project(this.camera);
			if (!p || p.z > 1) { a.el.hidden = true; continue; }
			a.el.hidden = false;
			const x = (p.x + 1) / 2 * w, y = (1 - p.y) / 2 * h;
			a.el.style.transform = `translate(${Math.round(x)}px, ${Math.round(y)}px)`;
			a.el.classList.toggle('flip', x > w * 0.62);
			a.el.classList.toggle('below', y < 110);
		}
	}
}
