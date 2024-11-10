// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss', 'nuxt-security'],
  
  build: {
    transpile: ['@ffmpeg/ffmpeg', '@ffmpeg/util']
  },

  vite: {
    define: {
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)
    },
    optimizeDeps: {
      exclude: ['@ffmpeg/ffmpeg', '@ffmpeg/util']
    },
    resolve: {
      mainFields: ['browser', 'module', 'main']
    },
    server: {
      headers: {
        "Cross-Origin-Embedder-Policy": "require-corp",
        "Cross-Origin-Opener-Policy": "same-origin",
        'Cross-Origin-Resource-Policy': 'cross-origin',
        'Content-Security-Policy': {
          'img-src': ["'self'", 'data:', 'blob:'],
          'media-src': ["'self'", 'blob:'],
          'connect-src': ["'self'", 'https://unpkg.com', 'http://localhost:*', 'blob:'],
          'script-src': ["'self'", 'https://unpkg.com', "'unsafe-inline'", "'unsafe-eval'", 'http://localhost:*'],
          'worker-src': ["'self'", 'blob:'],
          'child-src': ["'self'", 'blob:'],
          'frame-src': ["'self'", 'blob:'],
          'default-src': ["'self'", 'blob:', 'https:', 'http:', 'data:'],
          'style-src': ["'self'", "'unsafe-inline'"],
          'base-uri': ["'self'"],
          'frame-ancestors': ["'self'"],
          'upgrade-insecure-requests': true
        }
      }
    }
  },

  nitro: {
    preset: 'netlify',
    routeRules: {
      '/**': {
        headers: {
          'Cross-Origin-Embedder-Policy': 'require-corp',
          'Cross-Origin-Opener-Policy': 'same-origin',
          'Cross-Origin-Resource-Policy': 'cross-origin'
        }
      }
    },
    externals: {
      exclude: ['node_modules/nitropack/dist/presets/netlify/legacy/runtime/_deno-env-polyfill']
    }
  },

  pages: false,
  layouts: false,
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  security: {
    strict: false,
    headers: {
      crossOriginEmbedderPolicy: 'require-corp',
      crossOriginOpenerPolicy: 'same-origin',
      crossOriginResourcePolicy: 'cross-origin',
      contentSecurityPolicy: {
        'base-uri': ["'none'"],
        'font-src': ["'self'", "https:", "data:"],
        'form-action': ["'self'"],
        'img-src': ["'self'", "data:", "blob:"],
        'object-src': ["'none'"],
        'script-src-attr': ["'none'"],
        'style-src': ["'self'", "https:", "'unsafe-inline'"],
        'script-src': [
          "'self'",
          "https:",
          "'unsafe-inline'",
          "'strict-dynamic'",
          "'nonce-{{nonce}}'"
        ],
        'worker-src': ["'self'", "blob:"],
        'child-src': ["'self'", "blob:"],
        'frame-src': ["'self'", "blob:"],
        'connect-src': ["'self'", "https://unpkg.com", "http://localhost:*", "blob:"],
        'upgrade-insecure-requests': true
      }
    },
    requestSizeLimiter: {
      maxRequestSizeInBytes: 2000000,
      maxUploadFileRequestInBytes: 8000000,
      throwError: true
    },
    rateLimiter: {
      tokensPerInterval: 150,
      interval: 300000,
      headers: false,
      driver: {
        name: 'lruCache'
      },
      throwError: true
    },
    xssValidator: {
      throwError: true
    },
    corsHandler: {
      origin: ['http://localhost:3000'],
      methods: ['GET', 'HEAD', 'PUT', 'PATCH', 'POST', 'DELETE'],
      credentials: true,
      preflight: {
        statusCode: 204
      }
    },
    allowedMethodsRestricter: {
      methods: '*',
      throwError: true
    },
    hidePoweredBy: true,
    basicAuth: false,
    enabled: true,
    csrf: false,
    nonce: true,
    removeLoggers: {
      external: [],
      consoleType: ['log', 'debug'],
      include: [/\.[jt]sx?$/, /\.vue\??/],
      exclude: [/node_modules/, /\.git/]
    },
    ssg: {
      meta: true,
      hashScripts: true,
      hashStyles: false,
      nitroHeaders: true,
      exportToPresets: true,
    },
    sri: true
  }
});