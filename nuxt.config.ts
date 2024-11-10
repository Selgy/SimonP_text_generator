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
      include: ['@ffmpeg/ffmpeg', '@ffmpeg/util']
    },
    resolve: {
      mainFields: ['browser', 'module', 'main']
    },
    server: {
      headers: {
        "Cross-Origin-Embedder-Policy": "require-corp",
        "Cross-Origin-Opener-Policy": "same-origin"
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
      crossOriginResourcePolicy: 'cross-origin',
      crossOriginOpenerPolicy: 'unsafe-none',
      crossOriginEmbedderPolicy: 'unsafe-none',
      contentSecurityPolicy: {
        'base-uri': ["'none'"],
        'font-src': ["'self'", 'https:', 'data:'],
        'form-action': ["'self'"],
        'frame-ancestors': ["'self'", 'http://localhost:*'],
        'img-src': ["'self'", 'data:', 'blob:'],
        'object-src': ["'none'"],
        'script-src-attr': ["'none'"],
        'style-src': ["'self'", 'https:', "'unsafe-inline'"],
        'script-src': ["'self'", 'https:', "'unsafe-inline'", "'strict-dynamic'", "'nonce-{{nonce}}'", 'http://localhost:*'],
        'upgrade-insecure-requests': true,
        'connect-src': ["'self'", 'https://unpkg.com', 'http://localhost:*'],
        'frame-src': ["'self'", 'http://localhost:*'],
        'worker-src': ["'self'", 'blob:'],
        'child-src': ["'self'", 'blob:'],
        'media-src': ["'self'", 'blob:']
      },
      originAgentCluster: '?1',
      referrerPolicy: 'no-referrer',
      strictTransportSecurity: {
        maxAge: 15552000,
        includeSubdomains: true,
      },
      xContentTypeOptions: 'nosniff',
      xDNSPrefetchControl: 'off',
      xDownloadOptions: 'noopen',
      xFrameOptions: 'SAMEORIGIN',
      xPermittedCrossDomainPolicies: 'none',
      xXSSProtection: '0',
      permissionsPolicy: {
        camera: [],
        'display-capture': [],
        fullscreen: [],
        geolocation: [],
        microphone: []
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