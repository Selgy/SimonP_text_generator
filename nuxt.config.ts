// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss'],
  
  build: {
    transpile: ['@ffmpeg/ffmpeg', '@ffmpeg/util']
  },

  nitro: {
    // Add these specific Netlify configurations
    preset: 'netlify',
    prerender: {
      failOnError: false,
    },
    // Add external modules configuration
    externals: {
      inline: ['@ffmpeg/ffmpeg', '@ffmpeg/util'],
    },
    // Add module resolution rules
    resolve: {
      alias: {
        // Prevent the problematic module from being bundled
        'nitropack/dist/presets/netlify/legacy/runtime/_deno-env-polyfill': 'unenv/runtime/polyfill/deno-env',
      }
    },
    routeRules: {
      '/**': {
        headers: {
          'Cross-Origin-Embedder-Policy': 'require-corp',
          'Cross-Origin-Opener-Policy': 'same-origin',
          'Cross-Origin-Resource-Policy': 'cross-origin'
        }
      }
    }
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
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Resource-Policy": "cross-origin"
      }
    }
  },

  pages: false,
  layouts: false,
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true }
});