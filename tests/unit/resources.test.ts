import { describe, expect, it } from 'vitest';
import { lessonById, loadCourse } from '../../src/lib/course';
import { featureById, loadSources } from '../../src/lib/registries';
import { KNOWN_ISSUES, featureStatusLabel, sourceGroups } from '../../src/lib/resources';

const course = loadCourse();

describe('KNOWN_ISSUES', () => {
  it('has a situation and a plan B for every entry', () => {
    expect(KNOWN_ISSUES.length).toBeGreaterThan(0);
    for (const issue of KNOWN_ISSUES) {
      expect(issue.situation.length).toBeGreaterThan(0);
      expect(issue.planB.length).toBeGreaterThan(0);
    }
  });

  it('references only registered cards, features and lessons', () => {
    for (const issue of KNOWN_ISSUES) {
      if (issue.card) expect(course.cards.some((card) => card.id === issue.card)).toBe(true);
      if (issue.feature) expect(featureById(issue.feature)).toBeDefined();
      for (const id of issue.lessons ?? []) expect(lessonById(course, id)).toBeDefined();
    }
  });
});

describe('sourceGroups', () => {
  const fixture = loadSources(new URL('../fixtures/sources.yaml', import.meta.url));

  it('groups sources by type in a fixed order with Korean labels, skipping empty groups', () => {
    const groups = sourceGroups(fixture);
    expect(groups.map((group) => group.type)).toEqual(['law', 'fictional']);
    expect(groups[0]?.label).toBe('법령');
    expect(groups[1]?.sources.map((source) => source.id)).toEqual(['fictional-test']);
  });

  it('keeps every real source in exactly one group', () => {
    const real = loadSources();
    const grouped = sourceGroups(real).flatMap((group) => group.sources.map((source) => source.id));
    expect(grouped.sort()).toEqual(real.map((source) => source.id).sort());
  });
});

describe('featureStatusLabel', () => {
  it('labels each status in Korean', () => {
    expect(featureStatusLabel('available')).toBe('사용 가능');
    expect(featureStatusLabel('limited')).toBe('일부 제한');
    expect(featureStatusLabel('unavailable')).toBe('쓸 수 없음');
    expect(featureStatusLabel('unverified')).toBe('확인 중');
  });
});
