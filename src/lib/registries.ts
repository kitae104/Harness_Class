// 등록부 yaml 조회 함수. 없는 ID는 undefined를 반환하고, 오류는 빌드 단계에서 쓰는 쪽이 낸다.
import type { ExternalLink, Feature, Source, Term } from './types';
import { contentPath, readYaml } from './yaml';

export function loadFeatures(path: string | URL = contentPath('product-features.yaml')): Feature[] {
  return readYaml<{ features: Feature[] }>(path).features ?? [];
}

export function featureById(id: string, features: Feature[] = loadFeatures()): Feature | undefined {
  return features.find((feature) => feature.id === id);
}

export function loadSources(path: string | URL = contentPath('sources.yaml')): Source[] {
  return readYaml<{ sources: Source[] }>(path).sources ?? [];
}

export function sourceById(id: string, sources: Source[] = loadSources()): Source | undefined {
  return sources.find((source) => source.id === id);
}

export function loadExternalLinks(path: string | URL = contentPath('external-links.yaml')): ExternalLink[] {
  return readYaml<{ links: ExternalLink[] }>(path).links ?? [];
}

export function linkById(id: string, links: ExternalLink[] = loadExternalLinks()): ExternalLink | undefined {
  return links.find((link) => link.id === id);
}

export function loadGlossary(path: string | URL = contentPath('glossary.yaml')): Term[] {
  return readYaml<{ terms: Term[] }>(path).terms ?? [];
}

/** 수강생 화면 표기: student_label이 있으면 그것, 없으면 term. */
export function termLabel(id: string, terms: Term[] = loadGlossary()): string | undefined {
  const found = terms.find((term) => term.id === id);
  return found ? (found.student_label ?? found.term) : undefined;
}
