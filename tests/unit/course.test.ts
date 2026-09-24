import { describe, expect, it } from 'vitest';
import {
  cardsForLesson,
  checkTexts,
  commonCards,
  lessonById,
  lessonByPosition,
  lessonsInOrder,
  lessonUrl,
  loadCourse,
  neighbors,
} from '../../src/lib/course';

const fixture = new URL('../fixtures/course.yaml', import.meta.url);
const course = loadCourse(fixture);
const ids = (items: { id: string }[]) => items.map((item) => item.id);

describe('lessonsInOrder', () => {
  it('sorts lessons by day, then number', () => {
    expect(ids(lessonsInOrder(course))).toEqual(['t1-first', 't2-second', 't3-third', 't4-fourth']);
  });

  it('does not reorder the loaded course', () => {
    lessonsInOrder(course);
    expect(course.lessons[0].id).toBe('t3-third');
  });
});

describe('lessonById / lessonByPosition', () => {
  it('finds a lesson by id', () => {
    expect(lessonById(course, 't2-second')?.title).toBe('둘째');
  });

  it('returns undefined for an unknown id', () => {
    expect(lessonById(course, 'nope')).toBeUndefined();
  });

  it('finds a lesson by day and number', () => {
    expect(lessonByPosition(course, 2, 1)?.id).toBe('t3-third');
  });

  it('returns undefined for an unknown position', () => {
    expect(lessonByPosition(course, 3, 1)).toBeUndefined();
  });
});

describe('neighbors', () => {
  it('has no prev for the first lesson', () => {
    const { prev, next } = neighbors(course, 't1-first');
    expect(prev).toBeUndefined();
    expect(next?.id).toBe('t2-second');
  });

  it('has no next for the last lesson', () => {
    const { prev, next } = neighbors(course, 't4-fourth');
    expect(prev?.id).toBe('t3-third');
    expect(next).toBeUndefined();
  });

  it('crosses the day boundary', () => {
    expect(neighbors(course, 't2-second').next?.id).toBe('t3-third');
    expect(neighbors(course, 't3-third').prev?.id).toBe('t2-second');
  });

  it('returns no neighbors for an unknown id', () => {
    expect(neighbors(course, 'nope')).toEqual({});
  });
});

describe('lessonUrl', () => {
  it('pads the lesson number to two digits', () => {
    expect(lessonUrl({ day: 1, number: 3 })).toBe('/course/day1/03');
  });

  it('keeps two-digit numbers as they are', () => {
    expect(lessonUrl({ day: 2, number: 12 })).toBe('/course/day2/12');
  });
});

describe('cards', () => {
  it('returns cards placed on a lesson', () => {
    expect(ids(cardsForLesson(course, 't2-second'))).toEqual(['card-a', 'card-b']);
  });

  it('returns an empty list for a lesson without cards', () => {
    expect(cardsForLesson(course, 't1-first')).toEqual([]);
  });

  it('returns common cards', () => {
    expect(ids(commonCards(course))).toEqual(['card-common']);
  });

  it('keeps review status from course.yaml', () => {
    const [common] = commonCards(course);
    expect(common.status).toBe('reviewed');
    expect(common.reviewed_hash).toBe('abc123');
  });
});

describe('real content/course.yaml', () => {
  it('loads 14 lessons in day 1 → day 2 order', () => {
    const real = loadCourse();
    const ordered = lessonsInOrder(real);
    expect(ordered).toHaveLength(14);
    expect(ordered.map((l) => [l.day, l.number])).toEqual([
      ...[1, 2, 3, 4, 5, 6, 7].map((n) => [1, n]),
      ...[1, 2, 3, 4, 5, 6, 7].map((n) => [2, n]),
    ]);
  });
});

describe('checkTexts', () => {
  it('reads the {id, text} check format', () => {
    expect(checkTexts(lessonById(course, 't1-first')!)).toEqual(['새 형식 확인']);
  });

  it('still reads the legacy string format (planned lessons)', () => {
    expect(checkTexts(lessonById(course, 't3-third')!)).toEqual(['확인']);
  });
});
