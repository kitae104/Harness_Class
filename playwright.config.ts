import { defineConfig, devices } from '@playwright/test';

// 브라우저 테스트(V-WEB-003). npm run verify와 분리한다(ADR-012). Chromium만 쓴다.
// site.spec.ts는 preview 서버(dist/), offline.spec.ts는 dist-offline/을 file://로 연다.
// 먼저 npm run build:offline을 실행해 dist/와 dist-offline/을 만든다.
const PORT = 4322;

export default defineConfig({
  testDir: 'tests/e2e',
  reporter: 'list',
  use: {
    baseURL: `http://localhost:${PORT}`,
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    // 개발 서버와 겹치지 않도록 전용 포트를 쓰고, 이미 떠 있는 서버를 재사용하지 않는다.
    command: `npm run preview -- --port ${PORT}`,
    url: `http://localhost:${PORT}/`,
    reuseExistingServer: false,
    timeout: 60_000,
  },
});
