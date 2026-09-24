import { expect, test, type Page } from '@playwright/test';

// preview 서버에서 핵심 동작을 확인한다. localhost 밖으로 나가는 요청은 모두 막고, 하나라도 있으면 실패한다.
const blocked: string[] = [];

test.beforeEach(async ({ context }) => {
  blocked.length = 0;
  await context.route('**/*', (route) => {
    const url = new URL(route.request().url());
    if (url.hostname === 'localhost' || url.hostname === '127.0.0.1') return route.continue();
    blocked.push(url.href);
    return route.abort('blockedbyclient');
  });
});

test.afterEach(() => {
  expect(blocked, '외부 요청이 발생했습니다').toEqual([]);
});

const D1_01 = '/course/day1/01/';

function noHorizontalScroll(page: Page) {
  return page.evaluate(
    () => document.documentElement.scrollWidth <= document.documentElement.clientWidth,
  );
}

test('홈 → 전체 과정 → D1-01로 이동한다', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('navigation', { name: '주 메뉴' }).getByRole('link', { name: '전체 과정' }).click();
  await expect(page).toHaveURL(/\/course\/$/);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('전체 과정');
  await page.getByRole('link', { name: '하네스 엔지니어링 이해', exact: true }).click();
  await expect(page).toHaveURL(/\/course\/day1\/01\/$/);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('하네스 엔지니어링 이해');
});

test('D1-01의 다음 교시는 준비 중인 D1-02다', async ({ page }) => {
  await page.goto(D1_01);
  await page.getByRole('navigation', { name: '교시 이동' }).getByRole('link', { name: /다음 교시/ }).click();
  await expect(page).toHaveURL(/\/course\/day1\/02\/$/);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('업무 지침서 작성');
  await expect(page.getByText('준비 중입니다.')).toBeVisible();
});

test('복사 버튼을 누르면 "복사됨"이 보이고 클립보드에 같은 내용이 들어간다', async ({ page, context, baseURL }) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: baseURL });
  await page.goto(D1_01);
  const button = page.locator('[data-copy-text]').first();
  const expected = await button.getAttribute('data-copy-text');
  expect(expected).toBeTruthy();
  await button.click();
  await expect(button.locator('xpath=..').getByRole('status')).toHaveText('복사됨');
  expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(expected);
});

test('375px 폭에서 가로 스크롤이 없다', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 800 });
  for (const path of ['/', '/course/', D1_01, '/course/day1/02/']) {
    await page.goto(path);
    expect(await noHorizontalScroll(page), `${path} 가로 스크롤`).toBe(true);
  }
});

test('체크리스트는 새로고침 뒤에도 유지되고 "진행 초기화"로 해제된다', async ({ page }) => {
  await page.goto(D1_01);
  const list = page.locator('[data-checklist]').first();
  const box = list.getByRole('checkbox').first();
  await box.check();
  await page.reload();
  await expect(box).toBeChecked();
  await list.getByRole('button', { name: '진행 초기화' }).click();
  await expect(box).not.toBeChecked();
  await page.reload();
  await expect(box).not.toBeChecked();
});

test('D1-01 하단에 접힌 "강사 안내"가 있고, 준비 중인 D1-02에는 없다', async ({ page }) => {
  await page.goto(D1_01);
  const notes = page.locator('details.instructor-notes');
  await expect(notes).toHaveCount(1);
  await expect(notes.locator('summary')).toHaveText('강사 안내');
  await expect(notes).not.toHaveAttribute('open', /.*/);
  await expect(notes.getByRole('heading', { name: '시연 순서' })).toBeHidden();
  // LessonNav 바로 앞에 놓인다.
  expect(
    await notes.evaluate((el) => el.nextElementSibling?.classList.contains('lesson-nav') ?? false),
  ).toBe(true);

  await page.goto('/course/day1/02/');
  await expect(page.locator('details.instructor-notes')).toHaveCount(0);
});

test('강사 안내는 인쇄에서 빠지고 발표 모드에서도 접혀 있다', async ({ page }) => {
  await page.goto(D1_01);
  await page.getByRole('button', { name: /발표 모드/ }).click();
  await expect(page.locator('details.instructor-notes')).not.toHaveAttribute('open', /.*/);
  await page.emulateMedia({ media: 'print' });
  await expect(page.locator('details.instructor-notes')).toBeHidden();
});
