// course.yaml 조회 함수. 레이아웃·컴포넌트는 course.yaml을 직접 읽지 않고 이 모듈을 쓴다.
import type { Card, Course, Lesson } from './types';
import { contentPath, readYaml } from './yaml';

export function loadCourse(path: string | URL = contentPath('course.yaml')): Course {
  return readYaml<Course>(path);
}

/** Day, 교시 번호 순. 원본 배열은 바꾸지 않는다. */
export function lessonsInOrder(course: Course): Lesson[] {
  return [...course.lessons].sort((a, b) => a.day - b.day || a.number - b.number);
}

export function lessonById(course: Course, id: string): Lesson | undefined {
  return course.lessons.find((lesson) => lesson.id === id);
}

export function lessonByPosition(course: Course, day: number, number: number): Lesson | undefined {
  return course.lessons.find((lesson) => lesson.day === day && lesson.number === number);
}

/** 이전/다음 교시. Day 경계를 넘어 이어진다(Day 1 7교시 다음은 Day 2 1교시). */
export function neighbors(course: Course, id: string): { prev?: Lesson; next?: Lesson } {
  const ordered = lessonsInOrder(course);
  const index = ordered.findIndex((lesson) => lesson.id === id);
  if (index < 0) return {};
  const result: { prev?: Lesson; next?: Lesson } = {};
  if (index > 0) result.prev = ordered[index - 1];
  if (index < ordered.length - 1) result.next = ordered[index + 1];
  return result;
}

/** /course/day{d}/{nn} — nn은 두 자리 교시 번호(ARCHITECTURE 5절). */
export function lessonUrl(lesson: Pick<Lesson, 'day' | 'number'>): string {
  return `/course/day${lesson.day}/${String(lesson.number).padStart(2, '0')}`;
}

export function cardsForLesson(course: Course, id: string): Card[] {
  return course.cards.filter((card) => card.lesson === id);
}

export function commonCards(course: Course): Card[] {
  return cardsForLesson(course, 'common');
}
