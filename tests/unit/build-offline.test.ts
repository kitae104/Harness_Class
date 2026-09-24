import { describe, expect, it } from 'vitest';
import {
  findExternalAssets,
  rewriteHtml,
  toRelative,
} from '../../scripts/build_offline.mjs';

describe('toRelative', () => {
  it('points a directory link at index.html relative to the page', () => {
    expect(toRelative('course/day1/01/index.html', '/course/day1/02/')).toBe('../02/index.html');
  });

  it('resolves links from the site root page', () => {
    expect(toRelative('index.html', '/course/')).toBe('course/index.html');
    expect(toRelative('index.html', '/')).toBe('index.html');
  });

  it('climbs to the root from a nested page', () => {
    expect(toRelative('course/day1/01/index.html', '/')).toBe('../../../index.html');
    expect(toRelative('course/day1/01/index.html', '/_astro/a.css')).toBe('../../../_astro/a.css');
  });

  it('keeps file links as files', () => {
    expect(toRelative('course/index.html', '/images/x/y.svg')).toBe('../images/x/y.svg');
  });

  it('treats extensionless paths as directories', () => {
    expect(toRelative('index.html', '/course')).toBe('course/index.html');
  });

  it('keeps query strings and fragments', () => {
    expect(toRelative('course/index.html', '/course/day1/01/#practice')).toBe(
      'day1/01/index.html#practice',
    );
    expect(toRelative('index.html', '/a.css?v=1')).toBe('a.css?v=1');
  });

  it('never emits Windows path separators', () => {
    const result = toRelative('course\\day1\\01\\index.html', '/course/day2/01/');
    expect(result).toBe('../../day2/01/index.html');
    expect(result).not.toContain('\\');
  });

  it('decodes nothing and keeps non-ASCII paths as written', () => {
    expect(toRelative('index.html', '/자료/')).toBe('자료/index.html');
  });
});

describe('rewriteHtml', () => {
  const page = 'course/day1/01/index.html';

  it('rewrites root-relative href and src attributes', () => {
    const html =
      '<link rel="stylesheet" href="/_astro/a.css"><a href="/course/day1/02/">다음</a>' +
      '<img src="/images/d/x.svg" alt="">';
    expect(rewriteHtml(html, page)).toBe(
      '<link rel="stylesheet" href="../../../_astro/a.css"><a href="../02/index.html">다음</a>' +
        '<img src="../../../images/d/x.svg" alt="">',
    );
  });

  it('leaves external, protocol-relative, fragment and relative links alone', () => {
    const html =
      '<a href="https://www.law.go.kr/x">법</a><a href="//cdn.example/x">x</a>' +
      '<a href="#top">위</a><a href="../x/">상대</a><a href="mailto:a@example.com">m</a>';
    expect(rewriteHtml(html, page)).toBe(html);
  });

  it('handles single quotes', () => {
    expect(rewriteHtml("<a href='/'>홈</a>", 'index.html')).toBe("<a href='index.html'>홈</a>");
  });
});

describe('findExternalAssets', () => {
  it('reports external scripts, stylesheets and images', () => {
    const html =
      '<script src="https://cdn.example/a.js"></script>' +
      '<link rel="stylesheet" href="http://fonts.example/b.css">' +
      '<link href="//fonts.example/c.css" rel="stylesheet">' +
      '<img alt="" src="https://img.example/d.png">';
    expect(findExternalAssets(html)).toEqual([
      'https://cdn.example/a.js',
      'http://fonts.example/b.css',
      '//fonts.example/c.css',
      'https://img.example/d.png',
    ]);
  });

  it('ignores external anchors and local assets', () => {
    const html =
      '<a href="https://www.law.go.kr/x">법</a><link rel="icon" href="https://x.example/i.svg">' +
      '<script src="/_astro/a.js"></script><link rel="stylesheet" href="../a.css"><img src="x.svg">';
    expect(findExternalAssets(html)).toEqual([]);
  });
});
