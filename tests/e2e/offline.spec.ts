import { expect, test, type Page } from '@playwright/test';

// dist-offline/을 file://로 직접 열어 인터넷 없이 동작하는지 확인한다(CD-05, ADR-008).
// file:// 밖의 요청은 모두 막고, 막힌 요청이나 콘솔 오류가 하나라도 있으면 실패한다.
const blocked: string[] = [];
const consoleErrors: string[] = [];

// configFile은 저장소 루트의 playwright.config.ts다. 같은 폴더의 dist-offline/을 연다.
function offlineUrl(configFile: string | undefined, file: string) {
  if (!configFile) throw new Error('playwright.config.ts 위치를 알 수 없습니다.');
  const root = configFile.replace(/\\/g, '/').replace(/\/[^/]*$/, '');
  return encodeURI(`file://${root.startsWith('/') ? '' : '/'}${root}/dist-offline/${file}`);
}

function watch(page: Page) {
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('pageerror', (error) => consoleErrors.push(error.message));
}

test.beforeEach(async ({ context, page }) => {
  blocked.length = 0;
  consoleErrors.length = 0;
  await context.route('**/*', (route) => {
    const url = route.request().url();
    if (url.startsWith('file:')) return route.continue();
    blocked.push(url);
    return route.abort('blockedbyclient');
  });
  watch(page);
});

test.afterEach(() => {
  expect(blocked, '외부 요청이 발생했습니다').toEqual([]);
  expect(consoleErrors, '콘솔 오류가 발생했습니다').toEqual([]);
});

test('index.html에서 교시 링크로 이동한다', async ({ page }, testInfo) => {
  await page.goto(offlineUrl(testInfo.config.configFile, 'index.html'));
  await page.getByRole('navigation', { name: '주 메뉴' }).getByRole('link', { name: '전체 과정' }).click();
  await expect(page).toHaveURL(/\/dist-offline\/course\/index\.html$/);
  await page.getByRole('link', { name: '하네스 엔지니어링 이해', exact: true }).click();
  await expect(page).toHaveURL(/\/dist-offline\/course\/day1\/01\/index\.html$/);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('하네스 엔지니어링 이해');
  // 스타일시트가 상대경로로 적용되어야 넓은 화면에서 사이드바가 보인다.
  await expect(page.getByRole('navigation', { name: '교시 목록' })).toBeVisible();
});

test('이전/다음 교시로 이동한다', async ({ page }, testInfo) => {
  await page.goto(offlineUrl(testInfo.config.configFile, 'course/day1/01/index.html'));
  const nav = page.getByRole('navigation', { name: '교시 이동' });
  await nav.getByRole('link', { name: /다음 교시/ }).click();
  await expect(page).toHaveURL(/\/course\/day1\/02\/index\.html$/);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('업무 지침서 작성');
  await nav.getByRole('link', { name: /이전 교시/ }).click();
  await expect(page).toHaveURL(/\/course\/day1\/01\/index\.html$/);
});

test('복사 버튼이 Clipboard API로 동작한다', async ({ page, context }, testInfo) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.goto(offlineUrl(testInfo.config.configFile, 'course/day1/01/index.html'));
  const button = page.locator('[data-copy-text]').first();
  const expected = await button.getAttribute('data-copy-text');
  expect(expected).toBeTruthy();
  await button.click();
  await expect(button.locator('xpath=..').getByRole('status')).toHaveText('복사됨');
  expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(expected);
});

test('Clipboard API가 없어도 대체 경로로 복사한다', async ({ page, context }, testInfo) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.addInitScript(() => {
    Object.defineProperty(Navigator.prototype, 'clipboard', { get: () => undefined, configurable: true });
  });
  await page.goto(offlineUrl(testInfo.config.configFile, 'course/day1/01/index.html'));
  const button = page.locator('[data-copy-text]').nth(1);
  const expected = await button.getAttribute('data-copy-text');
  expect(expected).toBeTruthy();
  await button.click();
  await expect(button.locator('xpath=..').getByRole('status')).toHaveText('복사됨');
  // 이 페이지는 Clipboard API를 지웠으므로 새 페이지에서 클립보드를 읽는다.
  const reader = await context.newPage();
  watch(reader);
  await reader.goto(offlineUrl(testInfo.config.configFile, 'index.html'));
  expect(await reader.evaluate(() => navigator.clipboard.readText())).toBe(expected);
});
