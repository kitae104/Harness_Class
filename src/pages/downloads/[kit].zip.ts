// 실습 키트 다운로드 zip. 빌드할 때 content/kits/<id>/에서 만든다(public/downloads에 커밋하지 않는다, ARCHITECTURE 2절).
// 내려받을 파일이 1개 이상인 키트만 경로를 만든다. 키트가 0개여도 빌드는 통과한다.
import type { APIRoute, GetStaticPaths } from 'astro';
import { buildKitZip, downloadableKits, listKits, type Kit } from '../../lib/kits';

export const getStaticPaths = (() =>
  downloadableKits(listKits()).map((kit) => ({ params: { kit: kit.id }, props: { kit } }))) satisfies GetStaticPaths;

export const GET: APIRoute = ({ props }) => {
  // Response는 ArrayBuffer 기반 배열만 받으므로 복사본을 넘긴다(TS 6 Uint8Array 제네릭).
  const zip = new Uint8Array(buildKitZip((props as { kit: Kit }).kit));
  return new Response(zip, { headers: { 'Content-Type': 'application/zip' } });
};
