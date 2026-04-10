# HWP Skill Package

## HWP Skill 이란?

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
│  ├─ examples/
│  ├─ agents/
│  ├─ scripts/
│  ├─ references/
│  └─ assets/
```

### 폴더별 의미

- `hwp/`
  - 실제 설치되는 Codex 스킬 폴더입니다.
  - `hwp/examples/` 안에 검토서 샘플, 빈 양식, 예제 payload, 생성 결과 예시가 같이 들어 있습니다.
- `install_hwp_skill.bat`
  - Windows에서 더블클릭으로 설치할 수 있는 파일입니다.
- `install_hwp_skill.ps1`
  - PowerShell 수동 설치 파일입니다.

## 양식 기준

이 패키지의 기본 양식은 우리가 쓰는 한글 `검토서` 양식 기준입니다.

- 검토서 형식의 제목, 섹션, 본문 흐름을 유지합니다.
- 템플릿에 들어있는 박스형 구획과 문단 스타일을 그대로 활용합니다.
- 글자 모양, 문단 스타일, 표 레이아웃은 템플릿에서 읽어온 스타일 기준을 최대한 유지합니다.
- 즉, 단순 텍스트 덤프가 아니라 기존 한글 양식을 보존하면서 내용을 갈아끼우는 방식입니다.

현재 실제 기본 생성 템플릿은 아래 파일입니다.

- `hwp/scripts/templates/base_report_template.hwpx`
  - 원본 계열: `검토서_기본템플릿.hwpx`

빈 양식 샘플은 아래 파일입니다.

- `hwp/examples/Sample.hwpx`
  - 원본 계열: `검토서_기본템플릿_빈양식.hwpx`
  - 내용 없는 양식용 파일입니다.

내용이 들어간 참고본은 아래 파일입니다.

- `hwp/examples/Review_Reference.hwpx`
  - 구조와 톤을 참고하는 용도입니다.
  - 양식 파일로 쓰는 것이 아니라 참고본입니다.

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

## 실제 요청 예시

아래처럼 바로 말하면 됩니다.

```text
$hwp 스킬을 사용해서 샘플 양식으로 하천정비사업 구간 정비 범위에 대한 검토서를 만들어줘.
```

```text
$hwp 스킬을 사용해서 hwp/examples/Sample.hwpx 느낌으로 신규 산업단지 진입도로 폭 검토서를 작성해줘.
```

```text
$hwp 스킬을 사용해서 hwp/examples/Example_Request.md 내용을 기반으로 .hwpx 결과물을 생성해줘.
```

```text
$hwp 스킬을 사용해서 생성된 hwpx를 기본 rulebook 기준으로 검토해줘.
```

## 샘플 파일 설명

- `hwp/examples/Sample.hwpx`
  - 빈 검토서 양식 예시입니다.
- `hwp/examples/Review_Reference.hwpx`
  - 내용이 들어간 참고용 검토서입니다.
  - 양식 자체가 아니라 참고본입니다.
- `hwp/examples/Example_Request.md`
  - 실제 사용 예시용 Markdown 입력 원본입니다.
- `hwp/examples/Example_Payload.json`
  - 위 Markdown을 payload로 변환한 예시입니다.
- `hwp/examples/Example_Generated.hwpx`
  - 위 입력으로 생성한 실제 검토서 결과물입니다.
- `hwp/examples/Prompt_Examples.md`
  - Codex에게 어떻게 요청하면 되는지 문장 예시만 모아둔 파일입니다.

## 예제 결과는 어떻게 보면 되는가

- 가장 빠른 방법은 `hwp/examples/Example_Generated.hwpx`를 직접 열어보는 것입니다.
- 어떤 입력으로 생성됐는지 보려면 `hwp/examples/Example_Request.md`를 먼저 보면 됩니다.
- Codex에서 재현하고 싶다면 아래처럼 말하면 됩니다.

```text
$hwp 스킬을 사용해서 hwp/examples/Example_Request.md를 읽고 같은 형식의 hwpx를 다시 만들어줘.
```

## 사용 가능한 환경

권장 환경은 아래와 같습니다.

- Windows
- Codex 사용 가능 환경
- Python 3 설치 및 PATH 등록
- 한글(Hancom Office 한/글) 설치 권장

추가 설명
- 스킬 자체는 폴더 복사만으로 설치됩니다.
- 다만 `.hwpx` 생성 및 검토 스크립트를 쓰려면 Python 3가 필요합니다.
- 기본 설치 대상은 로컬 사용자 Codex 스킬 폴더입니다.

## 한글 설치가 필요한가

정리하면 아래와 같습니다.

- 스킬 설치 자체:
  - 한글이 없어도 가능합니다.
- Codex로 `.hwpx` 초안 생성:
  - Python 3만 있으면 가능합니다.
- 생성된 `.hwpx` 열기, 눈으로 확인하기, 수동 수정하기:
  - PC에 한글(Hancom Office 한/글)이 설치되어 있는 것이 사실상 필요합니다.
- 실제 실무 문서로 마감하고 편집하기:
  - 한글 설치를 권장하는 수준이 아니라 거의 필수에 가깝습니다.

즉, 이 패키지는 한글이 없어도 설치되고 `.hwpx` 생성까지는 가능하지만, 배포본에 들어 있는 `hwp/examples/Sample.hwpx`, `hwp/examples/Review_Reference.hwpx`, `hwp/examples/Example_Generated.hwpx`를 실제로 열어보고 수정하려면 한글 프로그램이 설치되어 있어야 합니다.

## 주의 사항

- 기본 preset JSON에는 대괄호 placeholder 문구가 들어 있습니다.
- 최종 검토 전에는 placeholder를 실제 문구로 바꿔야 합니다.
- 결과 파일은 작업 중인 폴더에 생성하는 것이 원칙입니다. 스킬 폴더 안에 결과물을 쓰지 않는 편이 좋습니다.
