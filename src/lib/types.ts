// course.yaml과 등록부 yaml의 TypeScript 타입.
// 값 검증은 하지 않는다 — 등록부 검사는 scripts/validate_course.py만 한다(ADR-004).
// 날짜는 yaml 1.2 core 스키마로 읽으므로 문자열이다.

export type Status = 'planned' | 'draft' | 'reviewed';
export type Track = 'core' | 'optional';
export type LessonType = 'concept' | 'practice' | 'project';
export type Where = 'instructions' | 'project-chat' | 'new-chat' | 'temporary-chat';
export type CardLevel = 1 | 2 | 3;

export interface Activity {
  kind: string;
  name: string;
  minutes: number;
}

export interface Objective {
  id: string;
  text: string;
  outputs: string[];
  /** 이 목표를 확인하는 lessons[].checks[].id 목록(V-LSN-005) */
  checks?: string[];
}

/** 결과 확인. 문자열은 planned 교시에서만 허용되는 과거 형식이다. */
export interface CheckItem {
  id: string;
  text: string;
}
export type Check = string | CheckItem;

export interface Output {
  id: string;
  text: string;
  used_by: string[];
}

export interface StuckPoint {
  id: string;
  text: string;
  supports: number[];
  card?: string;
}

export interface Card {
  id: string;
  /** 교시 ID 또는 'common' */
  lesson: string;
  title: string;
  category: string;
  level: CardLevel;
  where: Where;
  track: Track;
  status: Status;
  reviewed_hash?: string;
}

export interface Lesson {
  id: string;
  day: number;
  number: number;
  title: string;
  type: LessonType;
  subject: string;
  track: Track;
  status: Status;
  reviewed_hash?: string;
  elements: string[];
  overview?: boolean;
  activities: Activity[];
  objectives: Objective[];
  outputs: Output[];
  checks: Check[];
  cards: string[];
  stuck_points: StuckPoint[];
  skip_if_short: string[];
}

export interface Module {
  id: string;
  title: string;
  track: Track;
  status: Status;
  path: string;
  reviewed_hash?: string;
}

/** course.yaml kits[] 항목. 자료는 content/kits/<id>/kit.yaml(PRACTICE_CASES 1절). */
export interface CourseKit {
  id: string;
  title: string;
  status: Status;
  reviewed_hash?: string;
}

export interface Constraints {
  total_hours: number;
  days: number;
  lessons_per_day: number;
  lesson_minutes: number;
  max_core_minutes: number;
  min_element_coverage: number;
  max_cards_per_lesson: number;
  max_core_cards: number;
  freshness_days: number;
}

export interface Completion {
  required_outputs: string[];
  optional_outputs: string[];
  participation: string[];
  self_check: string[];
}

export interface Course {
  course: {
    title: string;
    edition: string;
    level: string;
    audience: string;
  };
  constraints: Constraints;
  elements: Record<string, string>;
  subjects: Record<string, string>;
  supports: Record<number, string>;
  activity_kinds: string[];
  completion: Completion;
  cards: Card[];
  lessons: Lesson[];
  modules: Module[];
  kits?: CourseKit[];
}

export interface Feature {
  id: string;
  product: string;
  plan: string;
  name: string;
  status: 'available' | 'limited' | 'unavailable' | 'unverified';
  detail?: string;
  verified_at: string | null;
  verified_by: 'web' | 'hands-on' | null;
  source: string | null;
  ui_path?: string;
  fallback: string;
  used_in: string[];
  tbd?: string;
}

export interface Source {
  id: string;
  type: 'law' | 'official-doc' | 'guideline' | 'proposal' | 'user-decision' | 'fictional';
  title: string;
  url: string | null;
  version?: string;
  effective_date?: string;
  articles?: string[];
  published?: string;
  note?: string;
  accessed_at: string;
  license: string;
}

export interface ExternalLink {
  id: string;
  title: string;
  kind: 'sheet-template' | 'form-template' | 'shared-form' | 'doc';
  owner: string;
  url: string | null;
  verified_at: string | null;
  fallback: string;
  /** 준비 전 대안: 표 양식 / 실제 다운로드 파일 / 없음(V-LNK-001) */
  fallback_kind?: 'template' | 'download' | 'none';
  /** fallback_kind: template일 때 탭 ID → 표 양식 */
  fallback_templates?: Record<string, { title: string; columns: string[] }>;
  /** fallback_kind: download일 때 파일 경로 */
  fallback_file?: string;
  status: string;
}

export interface Term {
  id: string;
  term: string;
  en: string;
  definition: string;
  student_label?: string;
}
