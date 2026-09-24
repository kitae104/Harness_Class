import { readFileSync } from 'node:fs';
import { parse } from 'yaml';

/** 저장소 루트 기준 content/ 경로. Astro 빌드와 vitest는 모두 루트에서 실행되므로 상대경로로 충분하다. */
export function contentPath(name: string): string {
  return `content/${name}`;
}

/** UTF-8 yaml 파일을 읽는다. 타입 단언만 하고 값은 검증하지 않는다(ADR-004). */
export function readYaml<T>(path: string | URL): T {
  return parse(readFileSync(path, 'utf8')) as T;
}
