module.exports = [
  {
    ignores: ['node_modules/**', 'dist/**', 'build/**', 'public/**'],
  },
  {
    plugins: {
      react: require('eslint-plugin-react'),
    },
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: { ecmaVersion: 'latest', ecmaFeatures: { jsx: true } },
    },
    settings: { react: { version: 'detect' } },
    rules: {},
  },
];
