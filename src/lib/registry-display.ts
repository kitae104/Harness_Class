// 등록부 정보를 컴포넌트가 어떻게 보여 줄지 고르는 순수 함수(Feature show, ExternalLink tab).
// 문구와 열 이름은 등록부에서만 온다. 잘못된 참조는 빌드를 멈추도록 오류를 던진다.
import type { ExternalLink, Feature } from './types';

export type FeatureShow = 'detail' | 'fallback';

export interface FeatureDisplay {
  /** show="detail": 기능명 뒤 한 문장 */
  detail?: string;
  /** show="fallback": status와 무관한 대안 */
  fallback?: string;
  /** show 없음 + unavailable: 기존 "쓸 수 없는 기능" 박스 */
  unavailable?: string;
}

export function featureDisplay(feature: Feature, show?: FeatureShow): FeatureDisplay {
  if (show === 'detail') {
    if (!feature.detail) throw new Error(`Feature: "${feature.id}"에 detail이 없어 show="detail"을 쓸 수 없습니다`);
    return { detail: feature.detail };
  }
  if (show === 'fallback') return { fallback: feature.fallback };
  return feature.status === 'unavailable' ? { unavailable: feature.fallback } : {};
}

/** 표 양식의 머리행을 탭으로 구분한 한 줄로 만든다. 구글 시트에 붙이면 열이 나뉜다. */
export function templateToTsv(columns: string[]): string {
  return columns.map((column) => column.replace(/\r\n|[\t\r\n]/g, ' ')).join('\t');
}

export type LinkDisplay =
  | { kind: 'link'; title: string; url: string }
  | { kind: 'text'; title: string; fallback: string }
  | { kind: 'template'; title: string; fallback: string; tableTitle: string; columns: string[]; tsv: string };

/**
 * active이고 url이 있으면 링크. 준비 전이면 fallback 문장, fallback_kind가 template이고 tab을 주면 표 양식.
 * tab을 주지 않으면 기존 사용처처럼 문장만 보여 준다(V-LNK-001이 tab 누락을 따로 본다).
 */
export function linkDisplay(link: ExternalLink, tab?: string): LinkDisplay {
  if (link.status === 'active' && link.url) return { kind: 'link', title: link.title, url: link.url };
  const text = { kind: 'text' as const, title: link.title, fallback: link.fallback };
  if (link.fallback_kind !== 'template' || tab === undefined) return text;
  const template = link.fallback_templates?.[tab];
  if (!template) {
    throw new Error(`ExternalLink: "${link.id}"의 fallback_templates에 tab "${tab}"이 없습니다`);
  }
  return {
    kind: 'template',
    title: link.title,
    fallback: link.fallback,
    tableTitle: template.title,
    columns: template.columns,
    tsv: templateToTsv(template.columns),
  };
}
