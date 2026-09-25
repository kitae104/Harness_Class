import { strFromU8, unzipSync } from 'fflate';
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import {
  buildKitZip,
  downloadableKits,
  downloadFiles,
  kitDownloadHref,
  kitReadme,
  listKits,
  loadKit,
} from '../../src/lib/kits';

// vitest는 저장소 루트에서 실행된다(src/lib/yaml.ts와 같은 전제).
const root = 'tests/fixtures/kits';
const coursePath = `${root}/course.yaml`;
const emptyCoursePath = `${root}/course-empty.yaml`;

describe('loadKit', () => {
  it('reads kit.yaml from <root>/<id>/', () => {
    const kit = loadKit('kit-sample', root);
    expect(kit.title).toBe('샘플 키트');
    expect(kit.files.map((f) => f.path)).toEqual(['rules.md', 'data/faq.md', 'answers.md']);
  });

  it('throws for an unknown kit', () => {
    expect(() => loadKit('nope', root)).toThrow(/nope/);
  });
});

describe('listKits', () => {
  it('follows course.yaml kits order', () => {
    expect(listKits(root, coursePath).map((k) => k.id)).toEqual(['kit-sample', 'kit-nodownload']);
  });

  it('returns no kits when course.yaml kits is empty', () => {
    expect(listKits(root, emptyCoursePath)).toEqual([]);
  });

  it('reads the real course.yaml by default', () => {
    expect(Array.isArray(listKits())).toBe(true);
  });
});

describe('downloadFiles', () => {
  it('keeps only download: true files', () => {
    expect(downloadFiles(loadKit('kit-sample', root)).map((f) => f.path)).toEqual([
      'rules.md',
      'data/faq.md',
    ]);
  });

  it('returns nothing when no file is downloadable', () => {
    expect(downloadFiles(loadKit('kit-nodownload', root))).toEqual([]);
  });
});

describe('downloadableKits', () => {
  it('excludes kits without downloadable files', () => {
    expect(downloadableKits(listKits(root, coursePath)).map((k) => k.id)).toEqual(['kit-sample']);
  });

  it('gives zero paths for zero kits', () => {
    expect(downloadableKits(listKits(root, emptyCoursePath))).toEqual([]);
  });
});

describe('kitReadme', () => {
  const readme = kitReadme(loadKit('kit-sample', root));

  it('includes the title, fictional label and privacy notes', () => {
    expect(readme).toContain('샘플 키트');
    expect(readme).toContain('이 자료는 교육용 가상 자료이며 실제 인물·기관과 무관합니다.');
    expect(readme).toContain('실제 개인정보를 넣지 마세요.');
  });

  it('lists only downloadable files with descriptions', () => {
    expect(readme).toContain('rules.md — 교육용 가상 규정');
    expect(readme).toContain('data/faq.md — 교육용 FAQ');
    expect(readme).not.toContain('answers.md');
  });
});

describe('buildKitZip', () => {
  const entries = unzipSync(buildKitZip(loadKit('kit-sample', root), root));

  it('puts README.txt first, then downloadable files with folder structure', () => {
    expect(Object.keys(entries)).toEqual(['README.txt', 'rules.md', 'data/faq.md']);
  });

  it('keeps file bytes unchanged (UTF-8)', () => {
    const original = readFileSync(`${root}/kit-sample/data/faq.md`, 'utf8');
    expect(strFromU8(entries['data/faq.md']!)).toBe(original);
    expect(strFromU8(entries['README.txt']!)).toContain('교육용 가상 자료');
  });

  it('is deterministic', () => {
    const kit = loadKit('kit-sample', root);
    expect(buildKitZip(kit, root)).toEqual(buildKitZip(kit, root));
  });

  it('throws when a listed file is missing', () => {
    expect(() => buildKitZip(loadKit('kit-missing', root), root)).toThrow(/nothing\.md/);
  });

  it('throws when a path escapes the kit folder', () => {
    expect(() => buildKitZip(loadKit('kit-escape', root), root)).toThrow(/키트 폴더 밖/);
  });
});

describe('kitDownloadHref', () => {
  it('points at the zip endpoint', () => {
    expect(kitDownloadHref('day1-civil')).toBe('/downloads/day1-civil.zip');
  });
});
