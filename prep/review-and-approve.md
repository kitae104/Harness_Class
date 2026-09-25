# 강사 재검토·승인·검사 (OQ-23)

AI는 콘텐츠를 draft까지만 올립니다. reviewed는 강사가 직접 `npm run review:approve`로만 올립니다(ADR-011). 명령은 저장소 폴더의 PowerShell에서 실행합니다(macOS·Linux는 `python` 대신 `python3`).

## 1. 재검토
- 사이트를 교시 순서대로 수강생 입장에서 읽습니다(로컬: `npm run build && npm run preview`, 또는 PR의 Vercel Preview).
- 교시마다 `docs/QUALITY_CHECKLIST.md` 3절 루브릭(목표 달성·초보자 지원·하네스 관점·정확성)이 모두 2점인지 봅니다.
- 빨간 점선 상자(**강의 준비** 표시)와 강사 안내의 `## 강의 준비` 절은 준비할 일 목록입니다. 전체 목록은 `npm run prep:list`.

## 2. 승인
```
git status --short        # 파일 전체가 바뀐 것처럼 보이면(줄바꿈) 멈추고 확인
npm run review:approve <id>   # 검토를 마친 교시·카드·키트마다
```
- 아직 draft인 항목과 해시가 깨진 항목은 `python scripts/validate_course.py --production`의 V-REV-001·V-REV-002 오류로 한 번에 볼 수 있습니다.
- 카드의 `tested_at`을 채우거나 본문을 고치면 해시가 바뀌므로, **편집을 모두 끝낸 뒤** 승인을 몰아서 합니다.

## 3. 검사
```
python scripts/validate_course.py --production
npm run verify
```

## 4. 개설 직전 (CD-25)
```
npm run prep:list -- --check   # 남은 강의 준비 표시가 있으면 실패
npm run prep:strip             # 표시를 모두 지움 → 지운 교시는 해시가 바뀌므로 다시 승인
```
그다음 `prep/` 폴더, `src/components/PrepNote.astro`, `scripts/prep_notes.mjs`와 그 테스트, package.json의 `prep:*` 두 줄, `src/styles/global.css`의 "강의 준비 표시" 블록을 지우고 verify를 다시 돌립니다([README.md](README.md)의 제거 절차).
