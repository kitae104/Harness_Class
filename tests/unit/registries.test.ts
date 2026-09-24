import { describe, expect, it } from 'vitest';
import {
  featureById,
  linkById,
  loadExternalLinks,
  loadFeatures,
  loadGlossary,
  loadSources,
  sourceById,
  termLabel,
} from '../../src/lib/registries';

const fixture = (name: string) => new URL(`../fixtures/${name}`, import.meta.url);

describe('features', () => {
  const features = loadFeatures(fixture('product-features.yaml'));

  it('loads all features', () => {
    expect(features.map((f) => f.id)).toEqual(['feat-available', 'feat-unverified']);
  });

  it('finds a feature by id', () => {
    const feature = featureById('feat-available', features);
    expect(feature?.name).toBe('사용 가능 기능');
    expect(feature?.fallback).toBe('대체 방법 A');
  });

  it('keeps dates as strings', () => {
    expect(featureById('feat-available', features)?.verified_at).toBe('2026-09-01');
  });

  it('returns undefined for an unknown feature', () => {
    expect(featureById('nope', features)).toBeUndefined();
  });

  it('reads the real registry by default', () => {
    expect(featureById('chatgpt-projects')?.product).toBe('ChatGPT');
  });
});

describe('sources', () => {
  const sources = loadSources(fixture('sources.yaml'));

  it('finds a law source with articles and effective date', () => {
    const source = sourceById('law-test', sources);
    expect(source?.effective_date).toBe('2026-01-01');
    expect(source?.articles).toEqual(['제1조(목적)', '제2조(정의)']);
  });

  it('returns undefined for an unknown source', () => {
    expect(sourceById('nope', sources)).toBeUndefined();
  });
});

describe('external links', () => {
  const links = loadExternalLinks(fixture('external-links.yaml'));

  it('finds a link by id', () => {
    expect(linkById('sheet-test', links)?.url).toBe('https://example.com/sheet');
    expect(linkById('form-planned', links)?.url).toBeNull();
  });

  it('returns undefined for an unknown link', () => {
    expect(linkById('nope', links)).toBeUndefined();
  });
});

describe('glossary', () => {
  const terms = loadGlossary(fixture('glossary.yaml'));

  it('prefers student_label', () => {
    expect(termLabel('evals', terms)).toBe('평가');
  });

  it('falls back to term when there is no student_label', () => {
    expect(termLabel('harness', terms)).toBe('하네스');
  });

  it('returns undefined for an unknown term', () => {
    expect(termLabel('nope', terms)).toBeUndefined();
  });
});
