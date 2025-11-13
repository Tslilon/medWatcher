// Service Worker for Harrison's Medical RAG
// Provides offline support by caching rendered PDF page images

const CACHE_NAME = 'harrisons-v1';
const PAGE_CACHE_NAME = 'harrisons-pages-v1';
const MAX_CACHED_PAGES = 50; // Limit cache size for Watch

// Assets to cache immediately
const ASSETS_TO_CACHE = [
    '/',
    '/web',
    '/viewer/watch',
    '/static/index.html',
    '/static/watchviewer.html'
];

// Install event - cache essential assets
self.addEventListener('install', (event) => {
    console.log('[SW] Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[SW] Caching essential assets');
                return cache.addAll(ASSETS_TO_CACHE.map(url => new Request(url, {cache: 'reload'})));
            })
            .catch(err => {
                console.error('[SW] Failed to cache assets:', err);
            })
    );
    self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating...');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME && cacheName !== PAGE_CACHE_NAME) {
                        console.log('[SW] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    return self.clients.claim();
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    
    // Handle PDF page images specially - cache them aggressively
    if (url.pathname.startsWith('/pdf/page/')) {
        event.respondWith(handlePageImageRequest(event.request));
        return;
    }
    
    // Handle API requests - always go to network
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(fetch(event.request));
        return;
    }
    
    // For everything else, try cache first, then network
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    console.log('[SW] Serving from cache:', event.request.url);
                    return response;
                }
                return fetch(event.request).then(response => {
                    // Cache successful responses
                    if (response && response.status === 200) {
                        const responseToCache = response.clone();
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(event.request, responseToCache);
                        });
                    }
                    return response;
                });
            })
    );
});

// Handle PDF page image caching with size limits
async function handlePageImageRequest(request) {
    const cache = await caches.open(PAGE_CACHE_NAME);
    
    // Check cache first
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
        console.log('[SW] Serving page image from cache:', request.url);
        return cachedResponse;
    }
    
    // Fetch from network
    try {
        const response = await fetch(request);
        
        if (response && response.status === 200) {
            // Check cache size and evict old entries if needed
            const keys = await cache.keys();
            if (keys.length >= MAX_CACHED_PAGES) {
                // Delete oldest entry (FIFO)
                await cache.delete(keys[0]);
                console.log('[SW] Evicted old page from cache');
            }
            
            // Cache the new page
            const responseToCache = response.clone();
            await cache.put(request, responseToCache);
            console.log('[SW] Cached new page:', request.url);
        }
        
        return response;
    } catch (error) {
        console.error('[SW] Failed to fetch page image:', error);
        
        // Return offline page or error
        return new Response('Offline - page not cached', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

// Handle messages from clients
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CLEAR_CACHE') {
        event.waitUntil(
            caches.keys().then(cacheNames => {
                return Promise.all(cacheNames.map(cache => caches.delete(cache)));
            }).then(() => {
                event.ports[0].postMessage({ success: true });
            })
        );
    }
});

