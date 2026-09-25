// /resources 페이지 데이터. 등록부 값(제품 정보·출처·카드·교시)은 ID로만 가리키고 옮겨 적지 않는다.
// 알려진 문제와 플랜 B: docs/TOOL_GUIDE.md 5절.
import type { Feature, Source } from './types';

export interface KnownIssue {
  situation: string;
  planB: string;
  /** 공통 문제 해결 카드 ID(course.yaml cards) */
  card?: string;
  /** 관련 제품 정보 ID(product-features.yaml) */
  feature?: string;
  /** 플랜 B를 쓰는 교시 ID(course.yaml lessons) */
  lessons?: string[];
}

export const KNOWN_ISSUES: KnownIssue[] = [
  {
    situation: '교육망에서 파일 업로드가 막힘',
    planB: '근거 자료 본문을 입력창에 붙여 넣고, 표는 복사해 붙입니다.',
    lessons: ['d1-context', 'd2-batch-classify'],
  },
  {
    situation: '결과 표를 시트에 붙이면 한 칸에 다 들어감',
    planB: '공통 카드로 표를 다시 받아 붙입니다.',
    card: 'card-help-broken-table',
  },
  {
    situation: '출력이 중간에 끊기거나 너무 김',
    planB: '공통 카드를 쓰고, 문항을 나눠 실행합니다.',
    card: 'card-help-long-output',
  },
  {
    situation: '결과가 이상함',
    planB: '지침·자료·입력 중 어디가 원인인지 공통 카드로 확인합니다.',
    card: 'card-help-odd-result',
  },
  {
    situation: '사용량 한도에 도달함',
    planB: '강사 화면을 보며 따라가고, 다음 교시에 이어서 합니다.',
    feature: 'chatgpt-file-uploads',
  },
  {
    situation: 'Project를 쓸 수 없음',
    planB: '일반 대화 첫 메시지에 지침과 근거 발췌를 붙여 넣고, 같은 대화 안에서 실습합니다.',
    feature: 'chatgpt-projects',
  },
  {
    situation: '강의 사이트에 접속할 수 없음',
    planB: '강사가 나눠 준 오프라인 자료(압축 파일)를 풀어 브라우저로 열거나, 강사 PC 화면을 봅니다.',
  },
];

const SOURCE_GROUPS: { type: Source['type']; label: string }[] = [
  { type: 'law', label: '법령' },
  { type: 'fictional', label: '교육용 가상 자료' },
  { type: 'guideline', label: '지침·가이드라인' },
  { type: 'official-doc', label: '공식 문서' },
  { type: 'proposal', label: '제안서' },
  { type: 'user-decision', label: '과정 운영 결정' },
];

export interface SourceGroup {
  type: Source['type'];
  label: string;
  sources: Source[];
}

/** 출처를 종류별로 묶는다. 빈 묶음은 뺀다. 등록부 순서를 유지한다. */
export function sourceGroups(sources: Source[]): SourceGroup[] {
  return SOURCE_GROUPS.map((group) => ({
    ...group,
    sources: sources.filter((source) => source.type === group.type),
  })).filter((group) => group.sources.length > 0);
}

const FEATURE_STATUS_LABELS: Record<Feature['status'], string> = {
  available: '사용 가능',
  limited: '일부 제한',
  unavailable: '쓸 수 없음',
  unverified: '확인 중',
};

export function featureStatusLabel(status: Feature['status']): string {
  return FEATURE_STATUS_LABELS[status];
}
