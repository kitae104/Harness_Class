import { describe, expect, it } from 'vitest';
import { loadCourse } from '../../src/lib/course';
import { loadExternalLinks } from '../../src/lib/registries';
import {
  CHECKLIST_12,
  DESIGN_SHEET,
  checklistItems,
  designSheetRows,
  designSheetText,
  linkTemplateTabs,
  rowsToTsv,
} from '../../src/lib/templates';

const elements = loadCourse().elements;
const fixtureLinks = loadExternalLinks(new URL('../fixtures/external-links.yaml', import.meta.url));

describe('designSheetRows', () => {
  it('gives one row per course.yaml element, in course.yaml order, with names from the registry', () => {
    const rows = designSheetRows(elements);
    expect(rows.map((row) => row.key)).toEqual(Object.keys(elements));
    expect(rows.map((row) => row.name)).toEqual(Object.values(elements));
    for (const row of rows) {
      expect(row.fill.length).toBeGreaterThan(0);
      expect(row.container.length).toBeGreaterThan(0);
    }
  });

  it('throws when an element has no design-sheet cell', () => {
    expect(() => designSheetRows({ ...elements, extra: '⑦ 추가' })).toThrow(/extra/);
  });

  it('throws when a design-sheet cell has no element in course.yaml', () => {
    const { instructions: _dropped, ...rest } = elements;
    expect(_dropped).toBeDefined();
    expect(() => designSheetRows(rest)).toThrow(/instructions/);
  });

  it('covers every element key exactly once in the data module', () => {
    expect(Object.keys(DESIGN_SHEET).sort()).toEqual(Object.keys(elements).sort());
  });
});

describe('designSheetText', () => {
  it('includes the header fields and every element name', () => {
    const text = designSheetText(designSheetRows(elements));
    expect(text.startsWith('하네스 설계서')).toBe(true);
    for (const name of Object.values(elements)) expect(text).toContain(name);
    expect(text).toContain('업무 이름:');
  });
});

describe('checklistItems', () => {
  const items = checklistItems(elements);

  it('numbers 12 items from 1 in element order, two per element', () => {
    expect(items).toHaveLength(12);
    expect(items.map((item) => item.number)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]);
    expect(items[0]?.element).toBe(elements.instructions);
    expect(items[11]?.element).toBe(elements.observability);
  });

  it('keeps the checklist text from the data module', () => {
    expect(items.map((item) => item.text)).toEqual(Object.keys(elements).flatMap((key) => CHECKLIST_12[key] ?? []));
  });

  it('throws when an element has no checklist items', () => {
    expect(() => checklistItems({ ...elements, extra: '⑦ 추가' })).toThrow(/extra/);
  });
});

describe('rowsToTsv', () => {
  it('joins cells with tabs and rows with line breaks', () => {
    expect(rowsToTsv([['a', 'b'], ['c', 'd']])).toBe('a\tb\nc\td');
  });

  it('flattens tabs and line breaks inside a cell', () => {
    expect(rowsToTsv([['a\tb', 'c\nd']])).toBe('a b\tc d');
  });
});

describe('linkTemplateTabs', () => {
  it('lists every fallback_templates tab of template links, in registry order', () => {
    const tabs = linkTemplateTabs(fixtureLinks);
    expect(tabs.map((tab) => `${tab.linkId}/${tab.tab}`)).toEqual([
      'sheet-template-planned/baseline',
      'sheet-template-planned/log',
    ]);
    expect(tabs[0]).toMatchObject({
      linkTitle: '준비 중 시트',
      tableTitle: '기준 질문 기록',
      columns: ['번호', '질문', '답(붙여 넣기)', '메모'],
      tsv: '번호\t질문\t답(붙여 넣기)\t메모',
    });
  });

  it('reads the real registry without errors', () => {
    expect(linkTemplateTabs(loadExternalLinks()).length).toBeGreaterThan(0);
  });
});
