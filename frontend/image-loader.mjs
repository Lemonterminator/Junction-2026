/** Load one complete image at a time, coalescing updates to the newest pending URL. */
export class LatestImageLoader {
	constructor(image, onError = () => {}) {
		this.image = image;
		this.onError = onError;
		this.current = null;
		this.pending = null;
		this.displayed = null;
		image.addEventListener('load', () => this.finish(false));
		image.addEventListener('error', () => this.finish(true));
	}

	/** Set an image URL, or null to cancel pending work and clear the presentation. */
	setSource(url) {
		if (url === null) {
			this.current = null;
			this.pending = null;
			this.displayed = null;
			this.image.hidden = true;
			this.image.removeAttribute('src');
			return;
		}
		if (this.current !== null) {
			this.pending = url === this.current ? null : url;
			return;
		}
		if (url !== this.displayed) this.start(url);
	}

	start(url) {
		this.current = url;
		this.pending = null;
		this.image.src = url;
	}

	finish(failed) {
		if (this.current === null) return;
		const completed = this.current;
		const next = this.pending;
		this.current = null;
		this.pending = null;
		this.displayed = failed ? null : completed;
		this.image.hidden = failed;
		if (failed) this.onError(completed);
		if (next !== null && next !== this.displayed) this.start(next);
	}
}
