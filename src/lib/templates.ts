// /templates 페이지의 양식 구조. 등록부에 원천이 없는 양식(하네스 설계서, 점검표 12항목)만 여기에 둔다.
// - 요소 키와 요소 이름은 course.yaml `elements`에서만 온다. 여기에는 요소 키별 칸 설명만 있다.
// - 설계서 칸 설명: docs/HARNESS_ELEMENTS.md 2절(요소 정의)·3절(담는 곳).
// - 점검표 12항목: docs/HARNESS_ELEMENTS.md 4절(제안서 원문, D2-7 상호평가 기준).
// - 외부 자원 표 양식(하네스 대장 탭 등)은 content/external-links.yaml에서 읽는다(linkTemplateTabs).
import { templateToTsv } from './registry-display';
import type { ExternalLink } from './types';

export interface DesignSheetCell {
  /** 이 칸에 적을 것 */
  fill: string;
  /** 요소를 담는 곳 */
  container: string;
}

/** 하네스 설계서 1장 — 요소 키(course.yaml elements)별 칸. */
export const DESIGN_SHEET: Record<string, DesignSheetCell> = {
  instructions: {
    fill: '역할, 업무 범위, 금지사항, 출력 형식, 모를 때 행동(지침서 5항목)',
    container: 'Project 지침란',
  },
  context: {
    fill: '규정·편람·FAQ·업무 매뉴얼 등 자료 목록과 기준일, 출처(조문) 표시 규칙',
    container: 'Project 파일(입력 데이터가 아님)',
  },
  tools: {
    fill: '입력을 모으고(폼) 쌓고(시트) 여러 건을 처리하는(ChatGPT) 흐름, AI가 하는 일과 하지 않는 일',
    container: '구글 폼(입력) → 구글 시트(축적) → 채팅 첨부로 여러 건 처리 → 시트(대장)',
  },
  evals: {
    fill: '평가 문항, 기대 결과, 채점 기준, 현재 점수와 목표 점수',
    container: '하네스 대장 평가 탭 + Project 밖 비개인화 임시 채팅에서 쓰는 채점 카드',
  },
  guardrails: {
    fill: '개인정보 처리 규칙, 근거 없는 답·범위 밖 판단 막기, "초안" 표시, 발송·공개 전 사람이 확인하는 단계',
    container: '지침의 금지사항, 폼 설정, 데이터 제어 설정, 사람 검토 열, 기관 보안 협의',
  },
  observability: {
    fill: '질문·답변·출처 기록, 지침 버전과 개정 이유, 개정 담당자와 주기',
    container: '하네스 대장 지침 버전·로그 탭',
  },
};

/** 설계서 머리 칸. */
export const DESIGN_SHEET_HEADER = ['업무 이름', 'AI에게 맡길 일(한 문장)', '작성일', '버전'];

/** 점검표 12항목 — 요소 키별 2항목, 번호는 요소 순서대로 매긴다. */
export const CHECKLIST_12: Record<string, [string, string]> = {
  instructions: ['역할·범위가 한 문장으로 적혀 있다', '"모를 때 행동"이 적혀 있다'],
  context: ['등록 자료 목록과 기준일자가 있다', '출처 없는 답을 막는 규칙이 있다'],
  tools: ['AI가 하는 일과 하지 않는 일이 구분된다', '동료가 설명 없이 써볼 수 있다'],
  evals: ['평가세트가 10문항 이상이다', '현재 점수와 목표 점수가 있다'],
  guardrails: ['개인정보 처리 규칙이 있다', '발송·공개 전 사람이 확인하는 단계가 있다'],
  observability: ['질문·답변·출처가 기록된다', '개정 담당자와 주기가 있다'],
};

export interface DesignSheetRow extends DesignSheetCell {
  key: string;
  name: string;
}

export interface ChecklistItem {
  number: number;
  key: string;
  element: string;
  text: string;
}

/** 데이터 모듈과 course.yaml elements의 키가 정확히 같아야 한다. 어긋나면 빌드를 멈춘다. */
function assertSameKeys(label: string, data: Record<string, unknown>, elements: Record<string, string>): void {
  for (const key of Object.keys(elements)) {
    if (!(key in data)) throw new Error(`${label}: course.yaml elements의 "${key}" 칸이 없습니다`);
  }
  for (const key of Object.keys(data)) {
    if (!(key in elements)) throw new Error(`${label}: "${key}"가 course.yaml elements에 없습니다`);
  }
}

export function designSheetRows(elements: Record<string, string>): DesignSheetRow[] {
  assertSameKeys('하네스 설계서', DESIGN_SHEET, elements);
  return Object.entries(elements).map(([key, name]) => ({ key, name, ...DESIGN_SHEET[key]! }));
}

/** 문서 편집기에 붙여 넣을 설계서 빈 양식(텍스트). */
export function designSheetText(rows: DesignSheetRow[]): string {
  const lines = ['하네스 설계서', '', ...DESIGN_SHEET_HEADER.map((field) => `${field}: `)];
  for (const row of rows) {
    lines.push('', `${row.name} — ${row.fill}`, `(담는 곳: ${row.container})`, '- ');
  }
  return `${lines.join('\n')}\n`;
}

export function checklistItems(elements: Record<string, string>): ChecklistItem[] {
  assertSameKeys('점검표', CHECKLIST_12, elements);
  let number = 0;
  return Object.entries(elements).flatMap(([key, element]) =>
    CHECKLIST_12[key]!.map((text) => ({ number: ++number, key, element, text })),
  );
}

/** 여러 행을 시트에 붙일 수 있는 탭 구분 텍스트로 만든다. 칸 안의 탭·줄바꿈은 공백으로 바꾼다. */
export function rowsToTsv(rows: string[][]): string {
  return rows.map((row) => templateToTsv(row)).join('\n');
}

export interface LinkTemplateTab {
  linkId: string;
  linkTitle: string;
  tab: string;
  tableTitle: string;
  columns: string[];
  tsv: string;
}

/** fallback_kind: template인 외부 자원의 모든 탭 양식(등록부 순서). */
export function linkTemplateTabs(links: ExternalLink[]): LinkTemplateTab[] {
  return links
    .filter((link) => link.fallback_kind === 'template')
    .flatMap((link) =>
      Object.entries(link.fallback_templates ?? {}).map(([tab, template]) => ({
        linkId: link.id,
        linkTitle: link.title,
        tab,
        tableTitle: template.title,
        columns: template.columns,
        tsv: templateToTsv(template.columns),
      })),
    );
}
