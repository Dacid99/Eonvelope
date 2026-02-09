// Base Service Worker implementation.  To use your own Service Worker, set the PWA_SERVICE_WORKER_PATH variable in settings.py

var staticCacheName = `django-pwa-v${Date().now()}`;

// list all static files to be cached in the pwa
var filesToCache = [
	// eonvelope
	"/static/eonvelope/css/eonvelope.css",
	"/static/eonvelope/icons/favicon-16x16.png",
	"/static/eonvelope/icons/favicon-32x32.png",
	"/static/eonvelope/icons/favicon-96x96.png",
	"/static/eonvelope/icons/favicon-192x192.png",
	"/static/eonvelope/icons/favicon-512x512.png",
	"/static/eonvelope/icons/favicon.svg",
	"/static/eonvelope/icons/favicon.ico",
	// web
	"/static/web/js/bs_theme-toggler.js",
	"/static/web/js/form-utils.js",
	"/static/web/js/multiSelect.js",
	"/static/web/js/spinner-text.js",
	"/static/web/js/timezone.js",
	"/static/web/js/urlTools.js",
];

// Cache on install
self.addEventListener("install", (event) => {
	this.skipWaiting();
	event.waitUntil(
		caches.open(staticCacheName).then((cache) => {
			return cache.addAll(filesToCache);
		}),
	);
});

// Clear cache on activate
self.addEventListener("activate", (event) => {
	event.waitUntil(
		caches.keys().then((cacheNames) => {
			return Promise.all(
				cacheNames
					.filter((cacheName) => cacheName.startsWith("django-pwa-"))
					.filter((cacheName) => cacheName !== staticCacheName)
					.map((cacheName) => caches.delete(cacheName)),
			);
		}),
	);
});

// Serve from Cache
self.addEventListener("fetch", (event) => {
	event.respondWith(
		caches.match(event.request).then((response) => {
			return response || fetch(event.request);
		}),
	);
});
