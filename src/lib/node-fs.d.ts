// @types/node가 설치되어 있지 않아 이 계층이 쓰는 node:fs 함수 하나만 선언한다.
// @types/node를 추가하면 이 선언과 병합되므로 그때 이 파일을 지워도 된다.
declare module 'node:fs' {
  export function readFileSync(path: string | URL, encoding: 'utf8'): string;
}
