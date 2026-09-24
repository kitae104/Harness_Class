import { describe, expect, it } from 'vitest';
import { featureDisplay, linkDisplay, templateToTsv } from '../../src/lib/registry-display';
import { featureById, linkById, loadExternalLinks, loadFeatures } from '../../src/lib/registries';
import type { ExternalLink, Feature } from '../../src/lib/types';

const fixture = (name: string) => new URL(`../fixtures/${name}`, import.meta.url);
const links = loadExternalLinks(fixture('external-links.yaml'));
const features = loadFeatures(fixture('product-features.yaml'));
const link = (id: string) => linkById(id, links) as ExternalLink;
const feature = (id: string) => featureById(id, features) as Feature;

describe('templateToTsv', () => {
  it('joins column names with tabs into one header row', () => {
    expect(templateToTsv(['번호', '질문', '메모'])).toBe('번호\t질문\t메모');
  });

  it('replaces tabs and line breaks inside a column name with a space', () => {
    expect(templateToTsv(['a\tb', 'c\r\nd'])).toBe('a b\tc d');
  });

  it('returns an empty string for no columns', () => {
    expect(templateToTsv([])).toBe('');
  });
});

describe('linkDisplay', () => {
  it('shows only the link when active with a url, even if a tab is given', () => {
    expect(linkDisplay(link('sheet-test'), 'baseline')).toEqual({
      kind: 'link',
      title: '테스트 시트',
      url: 'https://example.com/sheet',
    });
  });

  it('shows the template table for the requested tab', () => {
    expect(linkDisplay(link('sheet-template-planned'), 'baseline')).toEqual({
      kind: 'template',
      title: '준비 중 시트',
      fallback: '아래 표 양식을 복사해 씁니다',
      tableTitle: '기준 질문 기록',
      columns: ['번호', '질문', '답(붙여 넣기)', '메모'],
      tsv: '번호\t질문\t답(붙여 넣기)\t메모',
    });
    expect(linkDisplay(link('sheet-template-planned'), 'log')).toMatchObject({ tableTitle: '로그', tsv: '날짜\t내용' });
  });

  it('fails with id and tab when the tab is not in the templates', () => {
    expect(() => linkDisplay(link('sheet-template-planned'), 'nope')).toThrow(/sheet-template-planned.*nope/);
  });

  it('keeps the plain fallback sentence when no tab is given (existing usage)', () => {
    expect(linkDisplay(link('sheet-template-planned'))).toEqual({
      kind: 'text',
      title: '준비 중 시트',
      fallback: '아래 표 양식을 복사해 씁니다',
    });
  });

  it('shows only the fallback sentence for download and none kinds', () => {
    expect(linkDisplay(link('sheet-download-planned'), 'baseline')).toEqual({
      kind: 'text',
      title: '다운로드 대안 시트',
      fallback: 'xlsx 파일을 내려받아 씁니다',
    });
    expect(linkDisplay(link('form-planned'))).toMatchObject({ kind: 'text', fallback: 'CSV' });
  });

  it('treats an active link without a url as not ready', () => {
    expect(linkDisplay({ ...link('sheet-test'), url: null })).toMatchObject({ kind: 'text' });
  });
});

describe('featureDisplay', () => {
  it('shows nothing extra by default, and the fallback box only when unavailable', () => {
    expect(featureDisplay(feature('feat-available'))).toEqual({});
    expect(featureDisplay({ ...feature('feat-available'), status: 'unavailable' })).toEqual({
      unavailable: '대체 방법 A',
    });
  });

  it('shows detail when asked', () => {
    expect(featureDisplay(feature('feat-available'), 'detail')).toEqual({ detail: '설명' });
  });

  it('fails when detail is asked but not registered', () => {
    expect(() => featureDisplay(feature('feat-unverified'), 'detail')).toThrow(/feat-unverified/);
  });

  it('shows the fallback regardless of status', () => {
    expect(featureDisplay(feature('feat-available'), 'fallback')).toEqual({ fallback: '대체 방법 A' });
    expect(featureDisplay({ ...feature('feat-available'), status: 'unavailable' }, 'fallback')).toEqual({
      fallback: '대체 방법 A',
    });
  });
});
