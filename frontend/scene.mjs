/** Small canvas renderer for an illustrative cell. This is not calibrated robot geometry. */
const add = (a, b) => a.map((v, i) => v + b[i]);
const sub = (a, b) => a.map((v, i) => v - b[i]);
const scale = (a, n) => a.map(v => v * n);
const dot = (a, b) => a.reduce((sum, v, i) => sum + v * b[i], 0);
const cross = (a, b) => [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
const unit = a => scale(a, 1 / (Math.hypot(...a) || 1));
const mix = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);

export class CellScene {
	constructor(canvas) {
		this.canvas = canvas;
		this.ctx = canvas.getContext('2d');
		this.yaw = 0.62;
		this.pitch = 0.46;
		this.target = [0, 1.37, 0];
		this.tip = [...this.target];
		this.state = null;
		this.reduced = matchMedia('(prefers-reduced-motion: reduce)');
		let previous = null;
		canvas.addEventListener('pointerdown', e => { previous = [e.clientX, e.clientY]; canvas.setPointerCapture(e.pointerId); });
		canvas.addEventListener('pointermove', e => {
			if (!previous) return;
			this.yaw += (e.clientX - previous[0]) * 0.008;
			this.pitch = Math.max(0.2, Math.min(0.95, this.pitch + (e.clientY - previous[1]) * 0.005));
			previous = [e.clientX, e.clientY];
			this.draw();
		});
		for (const event of ['pointerup', 'pointercancel', 'lostpointercapture']) canvas.addEventListener(event, () => { previous = null; });
		canvas.addEventListener('keydown', e => {
			if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home'].includes(e.key)) return;
			e.preventDefault();
			if (e.key === 'Home') this.reset();
			else {
				this.yaw += e.key === 'ArrowLeft' ? -.1 : e.key === 'ArrowRight' ? .1 : 0;
				this.pitch = Math.max(.2, Math.min(.95, this.pitch + (e.key === 'ArrowUp' ? .06 : e.key === 'ArrowDown' ? -.06 : 0)));
				this.draw();
			}
		});
		new ResizeObserver(() => this.resize()).observe(canvas);
		this.resize();
		const animate = () => {
			if (!document.hidden && this.state?.mode === 'demo' && Math.hypot(...sub(this.tip, this.target)) > .002) {
				this.tip = this.reduced.matches ? [...this.target] : mix(this.tip, this.target, .055);
				this.draw();
			}
			requestAnimationFrame(animate);
		};
		requestAnimationFrame(animate);
	}

	reset() { this.yaw = .62; this.pitch = .46; this.draw(); }
	resize() {
		const rect = this.canvas.getBoundingClientRect();
		this.width = rect.width;
		this.height = rect.height;
		const dpr = Math.min(devicePixelRatio || 1, 2);
		this.canvas.width = rect.width * dpr;
		this.canvas.height = rect.height * dpr;
		this.ctx?.setTransform(dpr, 0, 0, dpr, 0, 0);
		this.draw();
	}

	setState(state) {
		this.state = state;
		if (state.stage === 'fault') { this.target = [...this.tip]; this.draw(); return; }
		const destination = state.destination === 'green' ? [-.75, .3, -.07] : [.78, .3, .65];
		this.target = state.stage === 'act' ? [0, .32, .48]
			: state.stage === 'verify' ? add(destination, [0, .37, 0]) : [0, 1.37, 0];
		this.draw();
	}

	project(p) {
		const cy = Math.cos(this.yaw), sy = Math.sin(this.yaw), cp = Math.cos(this.pitch), sp = Math.sin(this.pitch);
		const x = p[0]*cy - p[2]*sy, depth = p[0]*sy + p[2]*cy;
		const s = Math.min(this.width / 3.8, this.height / 2.9);
		return [this.width*.5 + x*s, this.height*.55 + (depth*sp - (p[1]-.3)*cp)*s, depth*cp + p[1]*sp];
	}

	polygon(vertices, color) {
		const points = vertices.map(p => this.project(p));
		this.faces.push({ points, color, depth: points.reduce((s, p) => s + p[2], 0) / points.length });
	}

	box(center, dimensions, color = '#79b9cc', axes = [[1,0,0],[0,1,0],[0,0,1]]) {
		const vertices = [];
		for (let i = 0; i < 8; i++) {
			let p = center;
			for (let j = 0; j < 3; j++) p = add(p, scale(axes[j], dimensions[j] * (i & (1 << j) ? .5 : -.5)));
			vertices.push(p);
		}
		const faces = [[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]];
		const shades = [0.68, 1, .85, 1.12, .75, .94];
		faces.forEach((face, i) => {
			const rgb = color.match(/\w\w/g).map(v => Math.min(255, Math.round(parseInt(v, 16) * shades[i])));
			this.polygon(face.map(n => vertices[n]), `rgb(${rgb.join(',')})`);
		});
	}

	link(a, b, width, color) {
		const y = unit(sub(b, a));
		const x = unit(cross(y, Math.abs(y[2]) > .9 ? [1,0,0] : [0,0,1]));
		this.box(mix(a,b,.5), [width, Math.hypot(...sub(b,a)), width], color, [x,y,cross(x,y)]);
	}

	cylinder(center, radius, height, color) {
		const ring = (y) => Array.from({length:32}, (_, i) => add(center, [Math.cos(i*Math.PI/16)*radius,y,Math.sin(i*Math.PI/16)*radius]));
		const bottom = ring(0), top = ring(height);
		for (let i = 0; i < 32; i++) this.polygon([bottom[i],bottom[(i+1)%32],top[(i+1)%32],top[i]], color);
		this.polygon(top, color === '#1c2631' ? '#303d48' : color);
	}

	bowl(x, z, color) {
		const n = 40;
		const ring = (r,y) => Array.from({length:n}, (_,i)=>[x+Math.cos(i*Math.PI*2/n)*r,y,z+Math.sin(i*Math.PI*2/n)*r]);
		const lower=ring(.27,.03), outer=ring(.36,.14), inner=ring(.32,.14), bottom=ring(.24,.07);
		for(let i=0;i<n;i++) {
			const j=(i+1)%n;
			this.polygon([lower[i],lower[j],outer[j],outer[i]],color==='green'?'#78ac9e':'#c78d88');
			this.polygon([outer[i],outer[j],inner[j],inner[i]],color==='green'?'#b4d9ca':'#f3c8bf');
			this.polygon([inner[i],inner[j],bottom[j],bottom[i]],color==='green'?'#92bdad':'#e2aba0');
		}
		this.polygon(bottom,color==='green'?'#9dc8b6':'#e6b4aa');
	}

	brick(position) {
		this.box(add(position,[0,.055,0]),[.21,.11,.13],'#3288c9');
		for(const x of [-.065,0,.065]) for(const z of [-.035,.035]) this.cylinder(add(position,[x,.11,z]),.022,.025,'#4e9fda');
		if(this.state?.label==='defective') {
			this.link(add(position,[-.065,.142,-.045]),add(position,[.065,.142,.045]),.012,'#293540');
			this.link(add(position,[-.065,.143,.045]),add(position,[.065,.143,-.045]),.012,'#293540');
		}
	}

	draw() {
		if (!this.ctx || !this.width || !this.height) return;
		const ctx = this.ctx;
		ctx.clearRect(0,0,this.width,this.height);
		if (this.state && this.state.mode !== 'demo') {
			ctx.fillStyle='#70808c';ctx.font='12px system-ui';ctx.textAlign='center';
			ctx.fillText('Live joint rendering awaits calibrated integration',this.width/2,this.height/2);
			return;
		}
		this.faces=[];
		this.box([0,-.075,.15],[2.95,.12,1.95],'#354451');
		this.bowl(-.75,-.07,'green');this.bowl(.78,.65,'pink');
		// Marked review area and inspection outline on the table.
		this.box([-.4,.002,.72],[.43,.004,.32],'#e7c354');
		for(let i=0;i<7;i++) this.box([-.58+i*.056,.006,.72],[.027,.005,.32],'#3a4244');
		for(const z of [.16,.39]) for(const x of [-.14,.14]) this.box([x,.005,z],[.1,.006,.012],'#d4e0e7');
		for(const x of [-.19,.19]) for(const z of [.21,.34]) this.box([x,.005,z],[.012,.006,.08],'#d4e0e7');
		// Camera stand.
		this.cylinder([-1.23,0,-.55],.025,1.7,'#26323c');
		this.link([-1.23,1.7,-.55],[-.75,1.7,-.55],.035,'#293740');
		this.box([-.75,1.65,-.55],[.18,.12,.14],'#23313b');
		this.box([-.75,1.58,-.55],[.055,.025,.055],'#49829d');
		// Stylized arm; no claim that this is the SO-101 URDF or real telemetry.
		const base=[.38,.02,-.48], shoulder=[.38,.27,-.48];
		this.cylinder(base,.23,.17,'#1c2631');
		this.box(shoulder,[.24,.23,.22],'#7ebdd0');
		const elbow=[.54,1.24,-.47], wrist=add(this.tip,[.08,.2,0]);
		this.link(shoulder,elbow,.15,'#79b8ce');
		this.box(mix(shoulder,elbow,.2),[.24,.17,.23],'#1c2631');
		this.box(elbow,[.24,.18,.23],'#1c2631');
		this.link(elbow,wrist,.14,'#88c5d8');
		this.box(wrist,[.23,.19,.22],'#1c2631');
		this.link(wrist,this.tip,.13,'#83bfd2');
		this.box(add(this.tip,[0,-.035,0]),[.18,.07,.12],'#25343f');
		for (const x of [-.085,.085]) this.box(add(this.tip,[x,-.14,0]),[.035,.19,.05],'#202c35');
		let position=[0,.01,.28];
		if(this.state?.stage==='verify') position=add(this.tip,[0,-.23,0]);
		if(this.state?.stage==='complete') position=this.state.destination==='green'?[-.75,.09,-.07]:[.78,.09,.65];
		this.brick(position);
		this.faces.sort((a,b)=>a.depth-b.depth);
		for(const face of this.faces) {
			ctx.beginPath();face.points.forEach((p,i)=>i?ctx.lineTo(p[0],p[1]):ctx.moveTo(p[0],p[1]));ctx.closePath();
			ctx.fillStyle=face.color;ctx.fill();ctx.strokeStyle=face.color;ctx.lineWidth=.5;ctx.stroke();
		}
	}
}

/** Synthetic top-camera crop, deliberately labeled as demonstration imagery. */
export function drawDemoCrop(canvas, label) {
	const ctx=canvas.getContext('2d');
	if(!ctx) return;
	canvas.width=600;canvas.height=400;
	const bg=ctx.createRadialGradient(300,200,10,300,200,350);
	bg.addColorStop(0,'#30414f');bg.addColorStop(1,'#202d37');ctx.fillStyle=bg;ctx.fillRect(0,0,600,400);
	ctx.save();ctx.translate(300,210);ctx.rotate(-.035);
	ctx.shadowBlur=25;ctx.shadowColor='#0c1926';ctx.fillStyle='#2869a5';ctx.fillRect(-57,-54,114,108);ctx.shadowBlur=0;
	const brick=ctx.createLinearGradient(-55,-55,55,55);brick.addColorStop(0,'#3b88ca');brick.addColorStop(1,'#2466a4');
	ctx.fillStyle=brick;ctx.fillRect(-55,-55,110,108);ctx.strokeStyle='#4a91c766';ctx.strokeRect(-55,-55,110,108);
	for(const x of [-25,25]) for(const y of [-25,25]){ctx.beginPath();ctx.arc(x,y,16,0,Math.PI*2);ctx.fillStyle='#6ca2d055';ctx.fill();ctx.strokeStyle='#8ab9db22';ctx.stroke();}
	if(label==='defective'){ctx.strokeStyle='#1b2733';ctx.lineWidth=6;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(4,12);ctx.lineTo(28,37);ctx.moveTo(28,12);ctx.lineTo(4,37);ctx.stroke();}
	if(label==='uncertain'){ctx.fillStyle='#c2d1d12a';ctx.fillRect(-55,-55,110,108);}
	ctx.restore();
}
