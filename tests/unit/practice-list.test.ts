import { describe, expect, it } from 'vitest';
import { loadCourse } from '../../src/lib/course';
import { moduleHref, practiceLessons } from '../../src/components/site';

const course = loadCourse(new URL('../fixtures/course.yaml', import.meta.url));

describe('practiceLessons', () => {
  it('keeps core practice and project lessons in Day·number order', () => {
    expect(practiceLessons(course).map((lesson) => lesson.id)).toEqual(['t2-second', 't3-third', 't4-fourth']);
  });

  it('drops concept lessons and optional lessons', () => {
    const withOptional = {
      ...course,
      lessons: [...course.lessons, { ...course.lessons[0]!, id: 'opt', type: 'practice' as const, track: 'optional' as const }],
    };
    const ids = practiceLessons(withOptional).map((lesson) => lesson.id);
    expect(ids).not.toContain('t1-first');
    expect(ids).not.toContain('opt');
  });
});

describe('moduleHref', () => {
  it('adds a trailing slash to the module path', () => {
    expect(moduleHref({ path: '/optional/test' })).toBe('/optional/test/');
    expect(moduleHref({ path: '/optional/test/' })).toBe('/optional/test/');
  });
});
