// 레이아웃·페이지가 쓰는 표시용 순수 함수. 값은 모두 course.yaml에서 읽는다(ADR-003).
import { lessonsInOrder, lessonUrl } from '../lib/course';
import type { Course, Lesson, LessonType } from '../lib/types';

/** 사이트 루트 기준 절대경로, 끝에 /를 붙인다. 오프라인 상대경로 변환은 build:offline이 한다. */
export function lessonHref(lesson: Pick<Lesson, 'day' | 'number'>): string {
  return `${lessonUrl(lesson)}/`;
}

/** /course/[day]/[num] 경로 파라미터. lessonUrl과 같은 모양이어야 한다. */
export function lessonParams(lesson: Pick<Lesson, 'day' | 'number'>): { day: string; num: string } {
  return { day: `day${lesson.day}`, num: String(lesson.number).padStart(2, '0') };
}

export function locationLabel(lesson: Pick<Lesson, 'day' | 'number' | 'title'>): string {
  return `Day ${lesson.day} · ${lesson.number}교시 — ${lesson.title}`;
}

export function coreLessons(course: Course): Lesson[] {
  return lessonsInOrder(course).filter((lesson) => lesson.track === 'core');
}

export function dayGroups(course: Course): { day: number; lessons: Lesson[] }[] {
  const groups: { day: number; lessons: Lesson[] }[] = [];
  for (const lesson of lessonsInOrder(course)) {
    const last = groups[groups.length - 1];
    if (last && last.day === lesson.day) last.lessons.push(lesson);
    else groups.push({ day: lesson.day, lessons: [lesson] });
  }
  return groups;
}

export function activityMinutes(lesson: Pick<Lesson, 'activities'>): number {
  return lesson.activities.reduce((sum, activity) => sum + activity.minutes, 0);
}

export function elementNames(course: Course, keys: string[]): string[] {
  return keys.map((key) => course.elements[key] ?? key);
}

const TYPE_LABELS: Record<LessonType, string> = {
  concept: '개념형',
  practice: '실습형',
  project: '프로젝트형',
};

export function lessonTypeLabel(type: LessonType): string {
  return TYPE_LABELS[type];
}

/** planned이거나 MDX가 없으면 "준비 중"으로 보여 준다(ARCHITECTURE 5절). */
export function showsPlaceholder(lesson: Pick<Lesson, 'status'>, hasMdx: boolean): boolean {
  return lesson.status === 'planned' || !hasMdx;
}
