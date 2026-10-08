# HCP 실데이터 준비 가이드

`sctransfer`가 쓰는 인간 데이터는 두 종류입니다.

| 종류 | 무엇을 할 수 있나 | 준비 |
| --- | --- | --- |
| **집단 평균** (ENIGMA Toolbox) | 1부: 종간 정규화 통계 비교 | 자동 다운로드 (`--human hcp_group`) |
| **개인별 SC·FC 쌍** | 2부: FC→SC 복원과 prior 효용 비교 | **직접 준비** (`--human hcp_cohort`) |

> 두 경우 모두 **HCP Open Access Data Use Terms**가 적용됩니다. ConnectomeDB(<https://db.humanconnectome.org>)에 가입하고 약관에 동의해야 합니다. 집단 평균 행렬도 HCP 데이터에서 파생된 것이라 마찬가지입니다. 개인별 데이터는 이 약관 때문에 저장소에 올리지 않습니다(`data/hcp/`는 gitignore 처리됨).

## 1. 집단 평균 (바로 사용 가능)

```bash
python -m sctransfer.run_transfer --human hcp_group                 # 원래 밀도
python -m sctransfer.run_transfer --human hcp_group --density 0.04  # 밀도 맞춤
```

처음 실행할 때 GitHub(raw.githubusercontent.com)에서 CSV를 받아 `data/hcp_enigma/raw/`에 저장합니다. 자세한 출처와 처리 과정은 `data/hcp_enigma/README.md`에 있습니다.

## 2. 개인별 SC·FC 쌍 (직접 준비)

### 받을 데이터 (HCP Young Adult, S1200)
- **확산 MRI 전처리본** (`Diffusion Preprocessed`): SC를 만들 재료입니다.
- **휴지기 fMRI 전처리본** (`Resting State fMRI FIX-Denoised`): FC를 만들 재료입니다.
- 처음에는 **100 Unrelated Subjects** 묶음으로 시작하길 추천합니다. 가족 관계가 없어 교차검증에서 정보가 새지 않습니다.

### 행렬 만들기
- **SC**: MRtrix3로 tractography(ACT + SIFT2 권장, ENIGMA와 같은 방식)를 돌린 뒤, 뇌 영역 지도(예: Schaefer 100 또는 Desikan 68)로 영역 쌍마다 streamline 가중치를 합칩니다.
- **FC**: 같은 뇌 영역 지도로 영역별 평균 시계열을 뽑고 피어슨 상관을 계산합니다. 음수는 0으로 두는 것이 이 파이프라인의 기본 가정입니다.
- **SC와 FC는 반드시 같은 뇌 영역 지도**를 써야 합니다.
- 피험자당 tractography는 수 시간이 걸리고 디스크도 많이 씁니다. 연구실 서버나 HPC를 권장합니다.

### 저장 형식 (둘 중 하나)

```text
# (a) 파일 하나
data/hcp/cohort.npz
    sc           (n_subjects, n, n)
    fc           (n_subjects, n, n)
    subject_ids  (n_subjects,)       선택

# (b) 피험자별 폴더
data/hcp/<subject_id>/sc.npy   (.csv, .txt도 가능)
data/hcp/<subject_id>/fc.npy
```

SC를 log 변환해 저장했다면 `--sc-is-log`를 붙이세요. 로더가 exp로 되돌려 강도 순서를 보존합니다.

### 실행

```bash
python -m sctransfer.run_transfer --human hcp_cohort --hcp-cohort data/hcp/cohort.npz
```

로더는 모양 확인, 대칭화, 대각선 0 처리, SC 음수 제거를 자동으로 합니다. 같은 형식의 가짜 데이터로 1부·2부가 끝까지 도는 것을 확인했습니다.

## 논문에 적을 것
- HCP 감사 문구(Data Use Terms에 명시된 문장)
- 집단 평균을 썼다면 ENIGMA Toolbox 인용: Larivière et al. (2021), *Nat Methods* 18, 698–700
- 사용한 뇌 영역 지도, tractography 설정, 밀도 처리 방식
