// Day 2 오후 내 업무 프로젝트의 예시 5종(CD-10). 업무 설명은 docs/PRACTICE_CASES.md 4절에서 옮겼다.
// 키트 제목·자료는 course.yaml kits와 content/kits/<id>/kit.yaml에서만 읽는다. 여기의 id는 키트 ID와 같다(바꾸지 않는다).
import type { Kit } from './kits';

export interface ExampleCase {
  /** course.yaml kits[].id */
  id: string;
  /** 업무 */
  work: string;
  /** 근거 자료 */
  basis: string;
  /** 이런 업무라면 이 예시 */
  fits: string;
  /** 특이사항 */
  note: string;
}

export const EXAMPLE_CASES: ExampleCase[] = [
  {
    id: 'rule-qa',
    work: '규정 Q&A 비서(인사·복무)',
    basis: '교육용 가상 복무 규정(근무시간·연가·병가)',
    fits: '규정·지침에 대한 비슷한 질문을 반복해서 받는 업무',
    note: '국가직·지방직으로 나누지 않습니다. 기관별 세부 질문은 "소속 기관 규정 확인 필요"가 정답입니다.',
  },
  {
    id: 'civil-draft',
    work: '민원 답변 초안 비서',
    basis: '대형 생활폐기물 배출 신고의 교육용 가상 규정',
    fits: '비슷한 민원에 답변 초안을 자주 쓰는 업무',
    note: 'Day 1 전입신고와 다른 유형의 민원입니다.',
  },
  {
    id: 'field-inspection',
    work: '현장 점검 보고 폼 + 정리 비서',
    basis: '교육용 가상 시설 안전점검 규정',
    fits: '현장에서 점검 결과를 모아 보고서로 정리하는 업무',
    note: '사진 문항은 선택입니다. 사람 얼굴·차량 번호·주소가 찍히지 않게 합니다.',
  },
  {
    id: 'demand-survey',
    work: '교육·행사 수요조사 + 결과 보고서',
    basis: '교육용 가상 양식(기관 내부 기준 역할)',
    fits: '설문을 받아 결과를 집계하고 보고하는 업무',
    note: '법령 근거가 없는 업무의 예시입니다.',
  },
  {
    id: 'meeting-minutes',
    work: '회의록 정리 비서',
    basis: '교육용 가상 회의록 양식',
    fits: '회의 메모를 정해진 양식의 회의록으로 정리하는 업무',
    note: '실제 회의 녹취와 참석자 이름을 쓰지 않습니다.',
  },
];

export interface ExampleRow extends ExampleCase {
  /** course.yaml kits에 등록된 키트. 아직 없으면 undefined */
  kit?: Kit;
}

/** 예시 5종에 등록된 키트를 붙이고, 예시가 아닌 키트(과정 공통 키트)는 course.yaml 순서대로 따로 모은다. */
export function splitKits(kits: Kit[]): { examples: ExampleRow[]; others: Kit[] } {
  const ids = new Set(EXAMPLE_CASES.map((item) => item.id));
  return {
    examples: EXAMPLE_CASES.map((item) => {
      const kit = kits.find((candidate) => candidate.id === item.id);
      return kit ? { ...item, kit } : { ...item };
    }),
    others: kits.filter((kit) => !ids.has(kit.id)),
  };
}
