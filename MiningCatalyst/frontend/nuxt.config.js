import colors from 'vuetify/es5/util/colors'

export default {
  // Disable server-side rendering: https://go.nuxtjs.dev/ssr-mode
  ssr: false,

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    titleTemplate: '%s',
    title: 'Catalyst',
    htmlAttrs: {
      lang: 'en',
    },
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' },
      { name: 'format-detection', content: 'telephone=no' },
    ],
    link: [{ rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }],
  },

  // Global CSS (https://go.nuxtjs.dev/config-css)
  css: ['~/assets/global.scss'],
  // css: ['~/assets/variables.scss', '~/assets/global.scss'],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
    '@/plugins/format.js',
    '@/plugins/utils.js',
    '@/plugins/theme.js',
    '@/plugins/perms.js',
    '@/plugins/snackbar.js',
    '@/plugins/axios.js',
    '@/plugins/props.js',
    '@/plugins/settings.js',
    '@/plugins/enums.js',
    '@/plugins/initiative.js',
    '@/plugins/lists.js',
    '@/plugins/form.js',
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: [{ path: '~/components/enco', prefix: 'e' }, '~/components/global'],

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/eslint
    '@nuxt/typescript-build',
    // '@nuxtjs/eslint-module',
    // https://go.nuxtjs.dev/vuetify
    '@nuxtjs/vuetify',
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    // https://go.nuxtjs.dev/axios
    '@nuxtjs/axios',
    '@nuxtjs/auth-next',
    '@nuxtjs/style-resources',
    'portal-vue/nuxt',
  ],

  styleResources: {
    scss: ['~/assets/variables.scss'],
  },

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {
    // Workaround to avoid enforcing hard-coded localhost:3000: https://github.com/nuxt-community/axios-module/issues/308
    baseURL: '/',
  },

  env: {
    // API_URL: process.env.API_URL,
    ENV: process.env.ENV || 'dev',
  },
  router: {
    middleware: ['auth'],
  },
  auth: {
    localStorage: false,
    redirect: {
      login: '/auth',
      logout: '/logout',
      // callback: '/',
      home: '/',
    },
    strategies: {
      social: {
        scheme: 'oauth2',
        endpoints: {
          authorization: 'https://login.microsoftonline.com/143a7396-a856-47d7-8e31-62990b5bacd0/oauth2/v2.0/authorize',
          token: undefined,
          userInfo: '/user',
          logout: null,
        },
        token: {
          property: 'access_token',
          type: 'Bearer',
          maxAge: 1800,
        },
        refreshToken: {
          property: 'refresh_token',
          maxAge: 60 * 60 * 24 * 30,
        },
        responseType: 'code',
        redirectUri: process.env.REDIRECT_URL,
        // TODO get from .env
        clientId: '9dc584b2-c472-498c-aefb-5b09948dd8b9',
        scope: ['openid', 'profile', 'email'],
        codeChallengeMethod: '',
      },
    },
  },

  loading: {
    color: 'var(--v-primary-base)',
    failedColor: 'var(--v-warning-base)',
    height: '6px',
  },

  // Vuetify module configuration: https://go.nuxtjs.dev/config-vuetify
  vuetify: {
    theme: {
      options: {
        customProperties: true,
      },
      // dark: true,
      themes: {
        dark: {
          fmg: 'fff',
          primary: '418FDE',
          secondary: colors.cyan.darken1,
          accent: colors.grey.darken3,
          accent2: colors.blueGrey.darken4,
          warning: colors.amber.base,
          error: colors.red.darken1,
          error2: colors.red.darken4,
          background: '1e1e1e',
          tableBackground: colors.grey.darken3,
        },
        light: {
          fmg: '212e4d',
          primary: '355bb7',
          secondary: colors.cyan.lighten1,
          accent: colors.grey.lighten2,
          accent2: colors.grey.lighten4,
          warning: colors.amber.base,
          error: colors.red.darken1,
          error2: colors.red.darken4,
          background: 'fff',
          tableBackground: colors.grey.lighten4,
        },
      },
    },
  },

  pwa: {},

  // Build Configuration (https://go.nuxtjs.dev/config-build)
  build: {
    watchers: {
      webpack: {
        aggregateTimeout: 300,
        poll: 1000,
      },
    },
  },
}
