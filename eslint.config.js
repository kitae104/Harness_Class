import tseslint from 'typescript-eslint';
import astro from 'eslint-plugin-astro';

export default [
  { ignores: ['dist/', 'dist-offline/', '.astro/', 'node_modules/', 'references/'] },
  ...tseslint.configs.recommended,
  ...astro.configs.recommended,
];
