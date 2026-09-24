// @types/node가 설치되어 있지 않아 new-content.test.ts가 쓰는 node 함수만 선언한다.
// src/lib/node-fs.d.ts의 선언과 병합된다. @types/node를 추가하면 이 파일을 지워도 된다.
declare module 'node:fs' {
  export function existsSync(path: string): boolean;
  export function mkdirSync(path: string, options?: { recursive?: boolean }): string | undefined;
  export function mkdtempSync(prefix: string): string;
  export function writeFileSync(path: string, data: string, encoding: 'utf8'): void;
}

declare module 'node:os' {
  export function tmpdir(): string;
}

declare module 'node:path' {
  export function join(...parts: string[]): string;
}
