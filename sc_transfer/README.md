# sc_transfer — 종간 배선 원리는 인간 뇌로 얼마나 옮겨 가는가

선충(*C. elegans*)과 초파리(*Drosophila*) 커넥톰에서 보이는 배선 원리(모듈성, 클러스터링, 리치클럽, 허브 구조)가, **규모와 측정 방식의 차이를 보정한 뒤** 인간 구조적 커넥톰(SC)에 정량적으로 얼마나 옮겨 가는지 검증하는 프로젝트입니다. 응용 과제로 기능적 커넥톰(FC)에서 SC를 복원하는 문제에서 이 원리들이 prior로서 쓸모 있는지도 봅니다.

> 원래 [BrainConnectom](../) 저장소의 `sc_prior_experiment`였던 것을 독립 프로젝트로 분리했습니다. 다른 실험(리저버, FlyHash, 로봇)에 의존하지 않고 이 폴더만으로 실행됩니다.

## 한눈에 보기

| 항목 | 내용 |
| --- | --- |
| **핵심 질문** | 종간 보존 원리는 정량적으로 어디까지 옮겨 가나? 어떤 원리가 옮겨 가나? |
| **방법** | 통계를 널 모델 대비 비율로 정규화 → prior 출처를 사다리(널 → 무척추동물 → 인간 → 정답)로 놓고 비교 → 전이 지수 TI |
| **데이터** | C. elegans 279 뉴런 · 초파리 hemibrain 회로 5개 · HCP 집단 평균 SC (뇌 영역 지도 6종) |
| **현재 결론** | 방향(무작위보다 높음)은 네 원리 모두 보존. 값까지 옮겨 가는 건 **모듈성**뿐이고, **허브 구조(차수 불균등도)**는 옮겨 가지 않음 |
| **막힌 곳** | FC→SC 효용 검증(2부)에 필요한 **HCP 개인별 SC·FC 쌍** — 직접 준비 필요 |

자세한 배경·방법·결과: **[docs/methodology_transferability.md](docs/methodology_transferability.md)**

## 설치

```bash
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

모든 명령은 **이 폴더(`sc_transfer/`)에서** 실행합니다.

## 실행

```bash
# 주 분석: 종간 전이 가능성
python -m sctransfer.run_transfer --human hcp_group                 # 실제 HCP 집단 평균 (1부, 약 4분)
python -m sctransfer.run_transfer --human hcp_group --density 0.04  # 밀도 맞춤 민감도 분석
python -m sctransfer.run_transfer                                   # 합성 인간 코호트 (1부 + 2부, 방법 검증용)
python -m sctransfer.run_transfer --human hcp_cohort --hcp-cohort data/hcp/cohort.npz   # 개인별 HCP (직접 준비)

# 초기 파일럿 (원래 프레이밍, 참고용)
python -m sctransfer.run_pilot --n-subjects 60

# 초파리 회로 데이터 재생성 (공개 export 약 46MB 다운로드)
python -m sctransfer.hemibrain --build
```

결과는 `results/`에 CSV로 저장됩니다 (gitignore).

## 구조

```
sc_transfer/
├── sctransfer/                     파이썬 패키지
│   ├── run_transfer.py             ★ 주 분석: 정규화 통계, prior 사다리, 전이 지수(TI), 원리별 분석
│   ├── normalized.py               널 모델 대비 정규화 통계 + 밀도 맞춤
│   ├── hcp_data.py                 HCP 로더 (ENIGMA 집단 평균 자동 다운로드 / 개인별 데이터 형식)
│   ├── celegans.py                 C. elegans 커넥톰 로더 + 널 모델
│   ├── hemibrain.py                초파리 hemibrain 회로 생성·로딩
│   ├── invertebrate_prior.py       무척추동물 표본 (부분 그래프 샘플링, 종별 동일 가중치)
│   ├── topology.py                 원시 그래프 통계 (파일럿용)
│   ├── human_data.py               합성 인간 SC-FC 코호트
│   ├── decoder.py                  FC→SC Ridge 디코더 + 허브 재구성
│   ├── run_pilot.py                초기 파일럿 (bio/null prior vs baseline)
│   └── reservoir.py, tasks.py      파일럿의 기능적 타당성 검사 (리저버 벤치마크)
├── data/
│   ├── celegans_multiplex/         C. elegans 커넥톰 (자체 README·라이선스)
│   ├── hemibrain/circuits/         초파리 회로 5개 (CC BY 4.0, README 참고)
│   └── hcp_enigma/                 HCP 집단 평균 캐시 (README만 커밋, HCP 약관 적용)
├── docs/
│   ├── methodology_transferability.md   ★ 현재 방향의 배경·가설·방법·결과
│   ├── hcp_data_guide.md           HCP 데이터 준비 방법과 약관
│   ├── proposal.md / .docx         원 제안서 (제출 당시 그대로)
│   ├── paper/DRAFT_abstract_intro_related.md   논문 초안 (원래 프레이밍, 재작성 필요)
│   └── papers/                     읽기 목록(READING_LIST)과 논문 요약(SUMMARIES)
├── CLAUDE.md                       새 세션을 위한 프로젝트 맥락
└── requirements.txt
```

## 지금까지의 흐름

1. **파일럿** (`run_pilot.py`): 무척추동물 prior로 FC→SC 복원 정확도를 올리려 했습니다. 하지만 **prior에 정답을 줘도 엣지 정확도가 오르지 않는다**는 것이 확인됐습니다. 그래프 전체 통계는 엣지 수천 개를 제약하기에 정보가 너무 적습니다.
2. **방향 전환 (A)** (`run_transfer.py`): 질문을 "종간 원리가 정량적으로 얼마나 옮겨 가는가"로 바꿨습니다. 인간 prior는 경쟁자가 아니라 상한선이 됩니다.
3. **실제 데이터**:
   - 초파리는 hemibrain 실측 회로로 바꿨습니다.
   - 인간은 HCP 집단 평균 SC로 1부를 완료했습니다.

| 원리 | 방향 보존 | 정량 전이 |
| --- | --- | --- |
| 모듈성 | ✅ | ✅ 가장 잘 옮겨 감 (밀도 맞춤 시 z −0.3) |
| 클러스터링 | ✅ | ✗ 인간 값이 지도·밀도에 따라 1.5~14로 변함 |
| 리치클럽 | ✅ (약함) | ✗ |
| 차수 불균등도 | ✅ | ✗ 무척추동물이 인간의 2~3배 |

## 다음 할 일

1. **HCP 개인별 SC·FC 쌍 준비 → 2부 실행.** 방법은 [docs/hcp_data_guide.md](docs/hcp_data_guide.md)에 있습니다.
2. **포유류 중간 단계 추가.** MaMI 데이터(Assaf 2020, Faskowitz 2023, Puxeddu 2024)를 넣어 계통적 거리에 따른 전이 감소를 봅니다.
3. **논문 초안을 새 질문에 맞게 다시 쓰기.** 대상은 `docs/paper/`입니다.

## 데이터 출처와 라이선스

- **C. elegans**: CoMuNeLab/C-elegans-Multiplex-Connectome. 인용: Chen, Hall & Chklovskii (2006), De Domenico, Porter & Arenas (2015). `data/celegans_multiplex/README.md` 참고.
- **초파리**: FlyEM hemibrain v1.2, CC BY 4.0. 인용: Scheffer et al. (2020). `data/hemibrain/README.md` 참고.
- **인간**: WU-Minn HCP (ENIGMA Toolbox 경유). HCP Open Access Data Use Terms에 동의해야 사용할 수 있습니다. 인용: Larivière et al. (2021). `data/hcp_enigma/README.md` 참고.
