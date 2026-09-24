// MDX·카드 파일 frontmatter 스키마(zod). 등록부 yaml은 여기서 검사하지 않는다(ADR-004).
// 제목·목표·상태(status, reviewed_hash)는 course.yaml에만 있으므로 frontmatter에 두지 않는다(ADR-003, ADR-011).
// 컬렉션 폴더가 비어 있어도 glob 로더는 경고만 내고 빌드는 계속된다.
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const lessons = defineCollection({
  loader: glob({ base: './content', pattern: ['day1/*.mdx', 'day2/*.mdx'] }),
  schema: z.strictObject({
    lesson_id: z.string().min(1),
  }),
});

const nonEmpty = z.string().min(1);

// PROMPT_GUIDE 2절 카드 파일 스키마
const prompts = defineCollection({
  loader: glob({ base: './content/prompts', pattern: '*.md' }),
  schema: z.strictObject({
    id: nonEmpty,
    stuck_point: nonEmpty,
    where: z.enum(['instructions', 'project-chat', 'new-chat', 'temporary-chat']),
    when: nonEmpty,
    input: nonEmpty,
    l3_structure: nonEmpty,
    l2_template: nonEmpty,
    l1_full: nonEmpty,
    default_level: z.union([z.literal(1), z.literal(2), z.literal(3)]),
    line_notes: z
      .array(
        z.strictObject({
          line: nonEmpty,
          element: nonEmpty,
          why: nonEmpty,
        }),
      )
      .min(1),
    replace: z.array(nonEmpty),
    check: z.array(nonEmpty).min(1),
    do_not_trust: z.array(nonEmpty).min(1),
    next: nonEmpty,
    tested_at: z.coerce.date().nullable(),
    tested_by: z.string().nullable(),
  }),
});

const modules = defineCollection({
  loader: glob({ base: './content/modules', pattern: '*.mdx' }),
  schema: z.strictObject({
    module_id: z.string().min(1),
  }),
});

export const collections = { lessons, prompts, modules };
