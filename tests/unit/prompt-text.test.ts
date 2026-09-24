import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { parse } from 'yaml';
import { levelLabel, listBrackets, splitBrackets, whereLabel } from '../../src/lib/prompt-text';
import { loadGlossary } from '../../src/lib/registries';

const glossary = loadGlossary(new URL('../fixtures/glossary.yaml', import.meta.url));

/** 테스트 전용: 카드 파일의 frontmatter만 읽는다. */
function readCard(name: string): Record<string, unknown> {
  const raw = readFileSync(new URL(`../fixtures/${name}`, import.meta.url), 'utf8').replace(/\r\n/g, '\n');
  const match = /^---\n([\s\S]*?)\n---/.exec(raw);
  if (!match) throw new Error(`${name}: frontmatter 없음`);
  return parse(match[1]) as Record<string, unknown>;
}

describe('splitBrackets', () => {
  it('splits bracket parts and keeps the brackets', () => {
    expect(splitBrackets('너는 [내 업무]를 돕는다.')).toEqual([
      { text: '너는 ', bracket: false },
      { text: '[내 업무]', bracket: true },
      { text: '를 돕는다.', bracket: false },
    ]);
  });

  it('handles adjacent and edge brackets', () => {
    expect(splitBrackets('[가][나] 끝')).toEqual([
      { text: '[가]', bracket: true },
      { text: '[나]', bracket: true },
      { text: ' 끝', bracket: false },
    ]);
  });

  it('returns plain text when there is no bracket', () => {
    expect(splitBrackets('대괄호 없음')).toEqual([{ text: '대괄호 없음', bracket: false }]);
  });

  it('returns an empty array for empty text', () => {
    expect(splitBrackets('')).toEqual([]);
  });

  it('does not treat empty, unclosed or multi-line brackets as brackets', () => {
    const text = '빈 [] 과 [닫히지 않음\n다음 줄]';
    expect(splitBrackets(text).every((part) => !part.bracket)).toBe(true);
  });

  it('joins back to the original text', () => {
    const text = '앞 [가] 가운데 [나]\n뒤';
    expect(splitBrackets(text).map((part) => part.text).join('')).toBe(text);
  });
});

describe('listBrackets', () => {
  it('lists unique brackets in order of appearance', () => {
    expect(listBrackets('[나] [가] [나]')).toEqual(['[나]', '[가]']);
  });

  it('returns an empty list when there is no bracket', () => {
    expect(listBrackets('없음')).toEqual([]);
  });

  it('matches the replace list of the sample card', () => {
    const card = readCard('prompt-sample.md');
    expect(listBrackets(card.l2_template as string)).toEqual(card.replace);
  });
});

describe('levelLabel', () => {
  it('uses glossary student labels', () => {
    expect(levelLabel(1)).toBe('따라 쓰기');
    expect(levelLabel(2)).toBe('바꿔 쓰기');
    expect(levelLabel(3)).toBe('직접 쓰기');
  });

  it('fails when the glossary has no label for the level', () => {
    expect(() => levelLabel(1, glossary)).toThrow(/level-1/);
  });
});

describe('whereLabel', () => {
  it('labels the four paste targets', () => {
    expect(whereLabel('instructions')).toBe('지침란');
    expect(whereLabel('project-chat')).toBe('Project 채팅');
    expect(whereLabel('new-chat')).toBe('새 채팅');
    expect(whereLabel('temporary-chat')).toBe('임시 채팅');
  });

  it('fails for an unknown paste target', () => {
    expect(() => whereLabel('email' as never)).toThrow(/email/);
  });
});
