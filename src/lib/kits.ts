// 실습 키트(content/kits/<id>/) 읽기와 다운로드 zip 생성. zip은 빌드 산출물이다(ARCHITECTURE 2절).
// 키트 구조 판정은 validator V-KIT-001이 한다. 여기서의 예외는 잘못된 zip을 만들지 않기 위한 빌드 안전장치다.
import { strToU8, zipSync } from 'fflate';
import { readFileSync } from 'node:fs';
import type { CourseKit } from './types';
import { contentPath, readYaml } from './yaml';

// @types/node가 없어 파일을 바이트 그대로 읽는 겹정의만 더한다(src/lib/node-fs.d.ts와 병합).
declare module 'node:fs' {
  export function readFileSync(path: string): Uint8Array;
}

export interface KitFile {
  path: string;
  role: string;
  download?: boolean;
  description?: string;
}

export interface Kit {
  id: string;
  title: string;
  track: string;
  fictional_label: string;
  privacy_notes: string;
  files: KitFile[];
}

const KITS_ROOT = contentPath('kits');
/** zip 항목 시각을 고정해 같은 자료면 같은 zip이 나오게 한다. */
const ZIP_MTIME = new Date('2026-01-01T00:00:00Z');
const README = 'README.txt';

/** <root>/<id>/kit.yaml. 파일이 없으면 예외(없는 키트 ID는 빌드를 멈춘다). */
export function loadKit(id: string, root: string = KITS_ROOT): Kit {
  const file = `${root}/${id}/kit.yaml`;
  let kit: Kit;
  try {
    kit = readYaml<Kit>(file);
  } catch (error) {
    throw new Error(`KitDownload: 키트 "${id}"의 kit.yaml을 읽을 수 없습니다 (${file})`, { cause: error });
  }
  return { ...kit, files: kit.files ?? [] };
}

/** course.yaml kits 순서대로 키트를 읽는다. kits가 비어 있으면 빈 배열. */
export function listKits(root: string = KITS_ROOT, coursePath: string = contentPath('course.yaml')): Kit[] {
  const entries = readYaml<{ kits?: CourseKit[] }>(coursePath).kits ?? [];
  return entries.map((entry) => loadKit(entry.id, root));
}

export function downloadFiles(kit: Kit): KitFile[] {
  return kit.files.filter((file) => file.download === true);
}

/** 다운로드 zip을 만들 키트: 내려받을 파일이 1개 이상인 키트. */
export function downloadableKits(kits: Kit[]): Kit[] {
  return kits.filter((kit) => downloadFiles(kit).length > 0);
}

/** 사이트 루트 기준 zip 경로. 오프라인 상대경로 변환은 build:offline이 한다. */
export function kitDownloadHref(id: string): string {
  return `/downloads/${id}.zip`;
}

/** zip 맨 앞에 넣는 안내문: 제목, 가상 자료 표기, 개인정보 주의, 파일 목록. */
export function kitReadme(kit: Kit): string {
  const lines = downloadFiles(kit).map((file) =>
    file.description ? `- ${file.path} — ${file.description}` : `- ${file.path}`,
  );
  return [
    kit.title,
    '',
    kit.fictional_label,
    '',
    `개인정보·보안 주의: ${kit.privacy_notes}`,
    '',
    '파일 목록',
    ...lines,
    '',
  ].join('\n');
}

/** 키트 폴더 기준 상대경로를 정규화한다. 절대경로·드라이브 문자·폴더 밖으로 나가는 경로는 예외. */
function kitRelativePath(kit: Kit, path: string): string {
  const fail = () => new Error(`KitDownload: 키트 "${kit.id}"의 파일 경로 "${path}"가 키트 폴더 밖을 가리킵니다`);
  if (!path || /^[\\/]/.test(path) || path.includes(':')) throw fail();
  const parts: string[] = [];
  for (const part of path.split(/[\\/]/)) {
    if (part === '' || part === '.') continue;
    if (part === '..') {
      if (parts.length === 0) throw fail();
      parts.pop();
    } else {
      parts.push(part);
    }
  }
  if (parts.length === 0) throw fail();
  return parts.join('/');
}

/** README.txt + download: true 파일(kit.yaml path 그대로, 바이트 그대로)을 담은 zip. */
export function buildKitZip(kit: Kit, root: string = KITS_ROOT): Uint8Array {
  const entries: Record<string, Uint8Array> = { [README]: strToU8(kitReadme(kit)) };
  for (const file of downloadFiles(kit)) {
    const rel = kitRelativePath(kit, file.path);
    if (rel === README || rel === 'kit.yaml') {
      throw new Error(`KitDownload: 키트 "${kit.id}"의 파일 이름 "${rel}"은 쓸 수 없습니다`);
    }
    try {
      entries[rel] = readFileSync(`${root}/${kit.id}/${rel}`);
    } catch (error) {
      throw new Error(`KitDownload: 키트 "${kit.id}"의 kit.yaml에 적힌 파일이 없습니다: ${file.path}`, {
        cause: error,
      });
    }
  }
  return zipSync(entries, { level: 9, mtime: ZIP_MTIME });
}
