import colors from "vuetify/es5/util/colors";

export default {
  ssr: false,

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    titleTemplate: "DEP - %s",
    title: "Home",
    htmlAttrs: {
      lang: "en",
    },
    meta: [
      { charset: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { hid: "description", name: "description", content: "" },
      { name: "format-detection", content: "telephone=no" },
    ],
    link: [{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" }],
  },

  // Customize the progress-bar color
  loading: { color: "#418FDE" },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: ["~/assets/variables.scss", "~/assets/global.scss", "~/assets/transitions.scss"],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
    "@/plugins/extras.js",
    "@/plugins/axios.js",
    "@/plugins/adt.js",
    "@/plugins/import.js",
    "@/plugins/document.js",
    "@/plugins/event_metrics.js",
    "@/plugins/props.js",
    "@/plugins/theme.js",
    "@/plugins/format.js",
    "@/plugins/utils.js",
    "@/plugins/form.js",
    "@/plugins/enums.js",
    "@/plugins/perms.js",
    "@/plugins/snackbar.js",
    "@/plugins/socket.js",
    "@/plugins/table_headers.js",
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: [{ path: "@/components/Enco", prefix: "e" }, "~/components/Global"],

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/eslint
    // '@nuxtjs/eslint-module',
    // https://go.nuxtjs.dev/vuetify
    "@nuxtjs/vuetify",
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    // https://go.nuxtjs.dev/axios
    "@nuxtjs/axios",
    "@nuxtjs/auth-next",
    "portal-vue/nuxt",
  ],

  styleResources: {
    scss: ["~/assets/variables.scss"],
  },

  env: {
    ENV: process.env.ENV || "dev",
  },

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {
    // baseURL: "/api/",
  },
  router: {
    middleware: ["auth"],
  },
  auth: {
    fullPathRedirect: true,
    localStorage: false,
    redirect: {
      login: "/auth",
      logout: "/logout",
      home: "/",
    },
    strategies: {
      social: {
        scheme: "oauth2",
        endpoints: {
          authorization: process.env.OAUTH_URL,
          token: undefined,
          userInfo: "/user",
          logout: null,
        },
        token: {
          property: "access_token",
          type: "Bearer",
          maxAge: 1800,
        },
        responseType: "code",
        redirectUri: process.env.REDIRECT_URL,
        clientId: process.env.OAUTH_CLIENT_ID,
        scope: ["openid", "profile", "email"],
        codeChallengeMethod: "",
      },
    },
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
          fmg: "fff",
          primary: "418FDE",
          accent: colors.grey.darken3,
          secondary: colors.cyan.darken1,
          orange: "D05538",
          // info: colors.teal.lighten1,
          // primary: colors.blue.darken2,
          // accent: colors.grey.darken3,
          // info: colors.teal.lighten1,
          warning: colors.amber.base,
          error: colors.red.darken1,
          background: "1e1e1e",
          words: "fff",
          // success: colors.green.accent3,
        },
        light: {
          fmg: "212e4d",
          primary: "355bb7",
          accent: colors.grey.lighten2,
          secondary: colors.cyan.lighten1,
          orange: "D04423",
          // info: colors.teal.lighten1,
          warning: colors.amber.base,
          error: colors.red.darken1,
          background: "fff",
          words: "000",
          // success: colors.green.accent3,
          // default_button: '418FDE',
          // drawer: '13294B',
          // icon2: '000000',
        },
      },
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
};
