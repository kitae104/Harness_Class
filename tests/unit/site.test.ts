import { describe, expect, it } from 'vitest';
import { lessonById, loadCourse } from '../../src/lib/course';
import {
  activityMinutes,
  coreLessons,
  dayGroups,
  elementNames,
  lessonHref,
  lessonParams,
  lessonTypeLabel,
  locationLabel,
  showsPlaceholder,
} from '../../src/components/site';

const course = loadCourse(new URL('../fixtures/course.yaml', import.meta.url));
const lesson = (id: string) => {
  const found = lessonById(course, id);
  if (!found) throw new Error(`fixture lesson ${id} missing`);
  return found;
};

describe('lessonHref / lessonParams', () => {
  it('builds a root-absolute URL with a trailing slash', () => {
    expect(lessonHref(lesson('t2-second'))).toBe('/course/day1/02/');
  });

  it('builds getStaticPaths params that match the URL', () => {
    expect(lessonParams(lesson('t3-third'))).toEqual({ day: 'day2', num: '01' });
  });

  it('gives the instructor-notes entry ID (content/instructor/day{d}/{nn}.md)', () => {
    const { day, num } = lessonParams(lesson('t2-second'));
    expect(`${day}/${num}`).toBe('day1/02');
  });
});

describe('locationLabel', () => {
  it('shows Day, number and title', () => {
    expect(locationLabel(lesson('t4-fourth'))).toBe('Day 2 · 2교시 — 넷째');
  });
});

describe('coreLessons / dayGroups', () => {
  it('returns core lessons in order', () => {
    expect(coreLessons(course).map((l) => l.id)).toEqual(['t1-first', 't2-second', 't3-third', 't4-fourth']);
  });

  it('groups lessons by day in order', () => {
    const groups = dayGroups(course);
    expect(groups.map((g) => g.day)).toEqual([1, 2]);
    expect(groups[1].lessons.map((l) => l.id)).toEqual(['t3-third', 't4-fourth']);
  });
});

describe('activityMinutes', () => {
  it('sums activity minutes from course.yaml', () => {
    expect(activityMinutes(lesson('t2-second'))).toBe(30);
  });
});

describe('elementNames', () => {
  it('maps element keys to course.yaml names', () => {
    expect(elementNames(course, ['instructions'])).toEqual(['① 지침']);
  });

  it('keeps unknown keys as-is', () => {
    expect(elementNames(course, ['nope'])).toEqual(['nope']);
  });
});

describe('lessonTypeLabel', () => {
  it('labels each lesson type in Korean', () => {
    expect(lessonTypeLabel('concept')).toBe('개념형');
    expect(lessonTypeLabel('practice')).toBe('실습형');
    expect(lessonTypeLabel('project')).toBe('프로젝트형');
  });
});

describe('showsPlaceholder', () => {
  it('shows the placeholder for planned lessons even when MDX exists', () => {
    expect(showsPlaceholder(lesson('t1-first'), true)).toBe(true);
  });

  it('shows the placeholder when MDX is missing', () => {
    expect(showsPlaceholder(lesson('t2-second'), false)).toBe(true);
  });

  it('renders the body for non-planned lessons with MDX', () => {
    expect(showsPlaceholder(lesson('t2-second'), true)).toBe(false);
  });
});
