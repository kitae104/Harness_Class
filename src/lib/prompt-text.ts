// AI에게 도움받기 카드의 프롬프트 텍스트를 다루는 순수 함수.
import { loadGlossary, termLabel } from './registries';
import type { CardLevel, Term, Where } from './types';

export interface TextPart {
  text: string;
  bracket: boolean;
}

// 한 줄 안에서 닫힌, 비어 있지 않은 대괄호만 "바꿀 부분"으로 본다.
const BRACKET = /\[[^[\]\n]+\]/g;

/** 텍스트를 대괄호 부분과 나머지로 나눈다. 대괄호 문자는 대괄호 부분에 남긴다. */
export function splitBrackets(text: string): TextPart[] {
  const parts: TextPart[] = [];
  let last = 0;
  for (const match of text.matchAll(BRACKET)) {
    const start = match.index ?? 0;
    if (start > last) parts.push({ text: text.slice(last, start), bracket: false });
    parts.push({ text: match[0], bracket: true });
    last = start + match[0].length;
  }
  if (last < text.length) parts.push({ text: text.slice(last), bracket: false });
  return parts;
}

/** 대괄호 부분을 처음 나온 순서대로, 중복 없이 돌려준다. 카드의 replace 목록과 비교한다. */
export function listBrackets(text: string): string[] {
  return [...new Set(splitBrackets(text).filter((part) => part.bracket).map((part) => part.text))];
}

/** 단계 이름(따라 쓰기/바꿔 쓰기/직접 쓰기)은 glossary의 level-N student_label에서 읽는다. */
export function levelLabel(level: CardLevel, terms: Term[] = loadGlossary()): string {
  const label = termLabel(`level-${level}`, terms);
  if (label === undefined) throw new Error(`glossary에 level-${level} 용어가 없습니다.`);
  return label;
}

const WHERE_LABELS: Record<Where, string> = {
  instructions: '지침란',
  'project-chat': 'Project 채팅',
  'new-chat': '새 채팅',
  'temporary-chat': '임시 채팅',
};

/** 붙여넣을 곳 배지 문구. */
export function whereLabel(where: Where): string {
  const label = WHERE_LABELS[where];
  if (label === undefined) throw new Error(`알 수 없는 붙여넣을 곳: ${where}`);
  return label;
}
