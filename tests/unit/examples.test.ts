import { describe, expect, it } from 'vitest';
import { EXAMPLE_CASES, splitKits } from '../../src/lib/examples';
import { listKits, type Kit } from '../../src/lib/kits';

const kit = (id: string): Kit => ({
  id,
  title: `${id} 키트`,
  track: 'core',
  fictional_label: '가상',
  privacy_notes: '주의',
  files: [],
});

describe('EXAMPLE_CASES', () => {
  it('lists the five CD-10 examples with fixed kit IDs', () => {
    expect(EXAMPLE_CASES.map((item) => item.id)).toEqual([
      'rule-qa',
      'civil-draft',
      'field-inspection',
      'demand-survey',
      'meeting-minutes',
    ]);
    for (const item of EXAMPLE_CASES) {
      expect(item.work && item.basis && item.fits && item.note).toBeTruthy();
    }
  });
});

describe('splitKits', () => {
  it('attaches registered kits to their example and leaves unregistered examples without a kit', () => {
    const { examples } = splitKits([kit('day1-civil'), kit('civil-draft')]);
    expect(examples.map((row) => row.id)).toEqual(EXAMPLE_CASES.map((item) => item.id));
    expect(examples.find((row) => row.id === 'civil-draft')?.kit?.title).toBe('civil-draft 키트');
    expect(examples.find((row) => row.id === 'rule-qa')?.kit).toBeUndefined();
  });

  it('keeps non-example kits in course.yaml order', () => {
    const { others } = splitKits([kit('day1-civil'), kit('rule-qa'), kit('day2-civil-intake')]);
    expect(others.map((item) => item.id)).toEqual(['day1-civil', 'day2-civil-intake']);
  });

  it('works with the real course.yaml kits', () => {
    const { examples, others } = splitKits(listKits());
    expect(examples).toHaveLength(EXAMPLE_CASES.length);
    expect(others.length + examples.filter((row) => row.kit).length).toBe(listKits().length);
  });
});
