# HWP Skill Package

## 이 패키지가 하는 일

이 패키지는 Codex에서 사용할 수 있는 `hwp` 스킬 배포본입니다.

이 스킬은 다음 작업에 사용합니다.
- 한국어 Hancom 문서 초안 작성
- 검토서, 요청서, 보고서 계열 `.hwpx` 생성
- 샘플 양식에 맞춘 새 문서 작성
- Markdown 또는 구조화된 메모를 `.hwpx`로 변환
- 생성된 `.hwpx`를 룰북으로 간단 검토

기본적으로 `.hwpx`를 결과물로 생성합니다. `.hwp`는 참고용 샘플로 보는 용도에 더 적합합니다.

## 패키지 구조

```text
hwp_skill_bundle_xxxxxxxx_xxxxxx/
├─ README.md
├─ install_hwp_skill.bat
├─ install_hwp_skill.ps1
├─ hwp/
│  ├─ SKILL.md
│  ├─ agents/
│  ├─ scripts/
│  ├─ references/
│  └─ assets/
└─ examples/
   ├─ blank_review_template.hwpx
   ├─ completed_review_example.hwpx
   ├─ example_report.json
   └─ example_report_generated.hwpx
```

### 폴더별 의미

- `hwp/`
  - 실제 설치되는 Codex 스킬 폴더입니다.
- `examples/`
  - 검토서 샘플, 빈 양식, 예제 payload, 생성 결과 예시가 들어 있습니다.
- `install_hwp_skill.bat`
  - Windows에서 더블클릭으로 설치할 수 있는 파일입니다.
- `install_hwp_skill.ps1`
  - PowerShell 수동 설치 파일입니다.

## 설치 방법

### 방법 1. 가장 쉬운 방법

1. 압축을 풉니다.
2. `install_hwp_skill.bat`를 실행합니다.
3. Codex를 재시작합니다.

### 방법 2. Codex에게 설치시키기

압축을 푼 폴더를 Codex가 볼 수 있는 작업 폴더로 연 뒤, 이렇게 요청하면 됩니다.

```text
이 폴더에 있는 hwp 스킬을 설치해줘.
```

더 명확하게 말하려면 이렇게 요청하면 됩니다.

```text
현재 폴더의 hwp 폴더를 내 Codex 스킬 폴더에 설치해줘.
```

Codex가 정상적으로 처리하면 보통 `~/.codex/skills/hwp` 또는 `%USERPROFILE%\.codex\skills\hwp` 쪽으로 복사 설치합니다.

### 방법 3. 수동 설치

`hwp` 폴더를 아래 위치로 복사하면 됩니다.

```text
%USERPROFILE%\.codex\skills\hwp
```

설치 후 Codex를 재시작합니다.

## 사용 방법

설치 후 Codex에서 다음처럼 요청하면 됩니다.

```text
Use $hwp to draft a Korean review report from this markdown and output .hwpx.
```

```text
Use $hwp to match this sample review form and produce a new .hwpx draft.
```

```text
Use $hwp to review this generated .hwpx against the bundled rulebook.
```

한국어로도 요청할 수 있습니다.

```text
$hwp 스킬을 사용해서 이 검토서 샘플 양식에 맞춰 새 hwpx 초안을 만들어줘.
```

## 샘플 파일 설명

- `examples/blank_review_template.hwpx`
  - 빈 검토서 양식 예시입니다.
- `examples/completed_review_example.hwpx`
  - 완성형 검토서 샘플입니다.
- `examples/example_report.json`
  - 생성기 입력용 예제 payload입니다.
- `examples/example_report_generated.hwpx`
  - 예제 payload로 실제 생성한 결과물입니다.

## 사용 가능한 환경

권장 환경은 아래와 같습니다.

- Windows
- Codex 사용 가능 환경
- Python 3 설치 및 PATH 등록

추가 설명
- 스킬 자체는 폴더 복사만으로 설치됩니다.
- 다만 `.hwpx` 생성 및 검토 스크립트를 쓰려면 Python 3가 필요합니다.
- 기본 설치 대상은 로컬 사용자 Codex 스킬 폴더입니다.

## 주의 사항

- 기본 preset JSON에는 대괄호 placeholder 문구가 들어 있습니다.
- 최종 검토 전에는 placeholder를 실제 문구로 바꿔야 합니다.
- 결과 파일은 작업 중인 폴더에 생성하는 것이 원칙입니다. 스킬 폴더 안에 결과물을 쓰지 않는 편이 좋습니다.
