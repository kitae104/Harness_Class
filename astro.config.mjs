// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

// 정적 출력만 쓴다. 외부 CDN·웹폰트·분석 통합을 넣지 않는다(ADR-002, ADR-008).
export default defineConfig({
  output: 'static',
  integrations: [mdx()],
});
