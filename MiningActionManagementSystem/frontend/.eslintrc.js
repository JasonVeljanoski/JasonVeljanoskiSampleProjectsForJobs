module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
  },
  parserOptions: {
    parser: '@babel/eslint-parser',
    requireConfigFile: false,
  },
  extends: ['@nuxtjs', 'plugin:vue/recommended', 'plugin:nuxt/recommended', 'prettier'],
  plugins: [],
  // add your custom rules here
  rules: {
    camelcase: 'off',
    eqeqeq: 0,
    'prefer-const': 'warn',
    'node/handle-callback-err': 0,
    'vue/multi-word-component-names': 0,
    'vue/no-mutating-props': 0,
    'vue/prop-name-casing': 0,
    'vue/require-default-prop': 0,
    'vue/require-prop-types': 'error',
    'vue/return-in-computed-property': 'warn',
    'vue/valid-v-for': 'warn',
    'no-unused-vars': 'warn',
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'vue/valid-v-slot': ['error', { allowModifiers: true }],
  },
}
