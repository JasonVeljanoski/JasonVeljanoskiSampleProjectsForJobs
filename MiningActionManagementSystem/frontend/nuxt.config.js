import colors from 'vuetify/es5/util/colors'

export default {
  // Disable server-side rendering (https://go.nuxtjs.dev/ssr-mode)
  ssr: false,

  // Global page headers (https://go.nuxtjs.dev/config-head)
  head: {
    titleTemplate: 'ACE - %s',
    title: 'ACE',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' },
    ],
    link: [{ rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }],
  },

  // Global CSS (https://go.nuxtjs.dev/config-css)
  css: ['~/assets/variables.scss', '~/assets/global.scss'],

  // Plugins to run before rendering page (https://go.nuxtjs.dev/config-plugins)
  plugins: [
    '@/plugins/perms.js',
    '@/plugins/format.js',
    '@/plugins/theme.js',
    '@/plugins/utils.js',
    '@/plugins/props.js',
    '@/plugins/form.js',
    '@/plugins/document.js',
    '@/plugins/enums.js',
    '@/plugins/snackbar.js',
    '@/plugins/workgroup_perms.js',
    '@/plugins/axios.js',
    '@/plugins/action_utils.js',
    '@/plugins/table_headers.js',
    '@/plugins/tiptap_vuetify.js',
  ],

  // Auto import components (https://go.nuxtjs.dev/config-components)
  components: [{ path: '~/components/Enco', prefix: 'e' }, '~/components/Global'],

  // Modules for dev and build (recommended) (https://go.nuxtjs.dev/config-modules)
  buildModules: [
    // https://go.nuxtjs.dev/eslint
    // '@nuxtjs/eslint-module',
    // https://go.nuxtjs.dev/vuetify
    '@nuxtjs/axios',
    '@nuxtjs/vuetify',
    '@nuxtjs/pwa',
  ],

  // Modules (https://go.nuxtjs.dev/config-modules)
  modules: ['@nuxtjs/auth-next', '@nuxtjs/style-resources', '@nuxtjs/pwa'],

  styleResources: {
    scss: ['~/assets/variables.scss'],
  },

  env: {
    API_URL: process.env.API_URL,
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
        clientId: '7c7ae6c8-b7c1-408a-bb29-273609f2a749',
        scope: ['openid', 'profile', 'email'],
        codeChallengeMethod: '',
      },
    },
  },

  loading: {
    color: 'var(--v-primary-base)',
    failedColor: 'var(--v-warning-base)',
    height: '3px',
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
          orange: 'D05538',
          warning: colors.amber.base,
          error: colors.red.darken1,
          error2: colors.red.darken4,
          background: '1e1e1e',
        },
        light: {
          fmg: '212e4d',
          primary: '355bb7',
          secondary: colors.cyan.lighten1,
          accent: colors.grey.lighten2,
          orange: 'D04423',
          warning: colors.amber.base,
          error: colors.red.darken1,
          error2: colors.red.darken4,
          background: 'fff',
        },
      },
    },
  },

  pwa: {
    meta: {
      title: 'ACE',
      author: 'ENCO Pty Ltd',
    },
    manifest: {
      name: 'ACE',
      lang: 'en',

      icons: [
        {
          src: '/ace_logo_light.png',
          type: 'image/png',
          sizes: '512x512',
        },
        { src: '/ace_logo_dark.png', type: 'image/png', sizes: '512x512', purpose: 'maskable' },
      ],
      theme_color: '#212e4d',
    },
    workbox: {
      enabled: true,
    },
  },

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
