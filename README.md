# BrainConnectom

실제 커넥톰(뇌신경 배선 데이터)을 머신러닝 파이프라인에 직접 꽂아보는 개인 연구용 실험 세 가지입니다.

1. **conn2res 스타일 리저버 컴퓨팅** — 실제 예쁜꼬마선충(C. elegans) 커넥톰이 같은 크기·밀도·스펙트럴 반지름의 무작위 그래프보다 더 나은 "리저버"가 되는가? (`reservoir_experiment/`)
2. **실제 배선을 반영한 FlyHash** — 초파리 후각회로 기반 유사도 해싱(FlyHash)에서, 이상화된 균등 무작위 연결 대신 생물학적으로 편향된(비균등) PN→Kenyon cell 연결을 쓰면 최근접 이웃 검색 성능이 달라지는가? (`flyhash_experiment/`)
3. **종간 보존된 위상학적 사전정보로 인간 구조적 커넥톰 복원** — C. elegans·초파리 구조적 커넥톰에서 뽑아낸 "종을 초월해 보존된 배선 통계"가, 인간 기능적 커넥톰(FC)만으로 구조적 커넥톰(SC)을 복원하는 문제에 도움이 되는가? (`sc_prior_experiment/`, 2주 파일럿 스프린트로 진행 중 — 제안서는 [docs/proposal.docx](docs/proposal.docx))

세 실험 모두 별도 다운로드 없이 그 자리에서 바로 실행됩니다. 원래 참고했던 `conn2res` 툴박스는 직접 의존성으로 쓰지 않습니다 — Python 3.8/3.9 시절 패키지(`gym==0.21.0`, `numpy==1.22`)에 고정돼 있어서 최신 Python/setuptools에서는 빌드 자체가 안 됩니다. 그래서 이 저장소의 리저버 컴퓨팅 파이프라인은 같은 아이디어(실제 커넥톰 → 고정 리저버 가중치 → 선형 readout만 학습)를 처음부터 가볍게 재구현한 것입니다. 원 논문: https://www.nature.com/articles/s41467-024-44900-4

더 자세한 아키텍처·구성요소 설명은 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)를 참고하세요.

## 설치

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## 1. 리저버 컴퓨팅 (`reservoir_experiment/`)

데이터: 실제 C. elegans 커넥톰(뉴런 279개, 화학 시냅스 레이어), 출처는
[CoMuNeLab/C-elegans-Multiplex-Connectome](https://github.com/CoMuNeLab/C-elegans-Multiplex-Connectome)이며 `data_sources/celegans_multiplex/`에 이미 받아뒀습니다.

```bash
python -m reservoir_experiment.run_experiment --n-trials 20
```

네 가지 리저버를 비교합니다 (전부 같은 스펙트럴 반지름으로 맞춰서, 순수하게 "배선 구조"만 다르게):
- `real` — 실제 화학 시냅스 커넥톰
- `degree_null` — 각 뉴런의 in/out 차수는 그대로 두고 연결만 무작위로 재배선
- `er_null` — 엣지 개수는 같지만 위치가 완전 무작위
- `dense_esn` — 생물학적 구조와 무관한, 교과서적인 무작위 가우시안 리저버(ESN) 베이스라인

평가는 표준 리저버 컴퓨팅 벤치마크 두 가지로:
- **메모리 용량(memory capacity, Jaeger 2001)** — 선형 readout이 리저버 상태만 보고 과거 입력을 몇 스텝 전까지 복원할 수 있는가
- **NARMA-10** — 비선형 시계열 예측 벤치마크 (NRMSE가 낮을수록 좋음)

결과: `results/reservoir_results.csv` (트라이얼별 원본 수치), `results/reservoir_comparison.png` (오차막대 포함 막대그래프).

**확장 아이디어**: 다른 뉴런 서브셋/레이어 사용(화학 시냅스 대신 전기 갭 정션), 더 큰 커넥톰으로 교체(neuprint로 초파리 버섯체/시각엽, CAVE/MICrONS로 마우스 피질), reciprocity나 거리 의존성을 보존하는 다른 널 모델 시도 등.

## 2. FlyHash (`flyhash_experiment/`)

```bash
python -m flyhash_experiment.run_experiment
```

sklearn의 `digits` 데이터셋으로 실제 유클리드 최근접 이웃 대비 recall@k를 비교합니다:
- `flyhash_idealized` — Dasgupta et al. 원 논문 모델: 각 Kenyon cell이 정확히 6개의 projection neuron을 균등 무작위로 샘플링
- `flyhash_biased_synthetic` — 좀 더 현실적인 대체 모델: KC마다 차수가 변동(Poisson 분포)하고 PN 샘플링도 비균등("인기 있는" PN vs "드문" PN) — neuPrint 토큰이 없을 때 자동으로 이 모델이 사용됩니다
- `flyhash_real_hemibrain` — 토큰을 설정하면 hemibrain 커넥톰에서 **실측된** PN→KC 시냅스 개수를 그대로 사용
- `simhash_baseline` — 비교 기준이 되는 고전적 랜덤 초평면 LSH

결과: `results/flyhash_results.csv`, `results/flyhash_comparison.png`.

### 실제 hemibrain 데이터 연동하기 (선택사항)

1. https://neuprint.janelia.org 에서 구글 계정으로 로그인 (무료)
2. 우측 상단 계정 아이콘 → Account → Auth Token 복사
3. `.env.example`을 `.env`로 복사하고 `NEUPRINT_TOKEN=`에 붙여넣기
4. `python -m flyhash_experiment.run_experiment` 다시 실행 — "NEUPRINT_TOKEN not set" 대신 `[connectome] fetched real hemibrain PN->KC matrix: (...)` 메시지가 뜨면 성공

**여기가 실제로 아직 명확히 답이 안 나온 연구 질문입니다**: 초파리의 실제 배선(비균등)이 원 논문에서 이론적으로 분석한 이상화된 균등 무작위 모델보다 해시 품질 면에서 유리한지 불리한지는 아직 잘 다뤄지지 않았습니다. 실제 데이터를 연동한 뒤에는 `FlyHash`의 `wta_sparsity`를 바꿔보거나, `digits` 대신 더 고차원인 데이터(예: 문장 임베딩)로 바꿔서 입력 차원에 따라 효과가 달라지는지도 확인해볼 만합니다.

## 3. 구조적 커넥톰 복원 (`sc_prior_experiment/`)

**핵심 질문**: 인간 기능적 커넥톰(FC, resting-state fMRI 상관행렬)만으로 구조적 커넥톰(SC, 백질 배선)을 복원하는 문제는 근본적으로 ill-posed(불량조건) 역문제입니다. C. elegans·초파리처럼 규모가 전혀 다른 신경계에서도 모듈성·리치클럽·배선 경제성 같은 위상학적 성질이 종을 초월해 보존된다는 비교 커넥톰믹스 연구 결과를, 이 역문제를 정규화하는 생물학적 사전분포(prior)로 쓸 수 있을까요? 자세한 연구 배경과 방법론은 [docs/proposal.docx](docs/proposal.docx) 제안서를 참고하세요.

```bash
python -m sc_prior_experiment.run_experiment --n-subjects 60
```

세 조건을 비교합니다 (전부 같은 베이스라인 디코더에서 출발, 순수하게 "정규화 방식"만 다르게):
- `baseline` — FC→SC Ridge 회귀 디코더, 정규화 없음
- `null_prior` — C. elegans·초파리 커넥톰의 **Erdos-Renyi 무작위화 버전**으로 만든 통계를 향해 정규화 (부정 대조군: "그럴듯해 보이는 아무 정규화"의 효과만 분리)
- `bio_prior` — 실제 C. elegans·초파리 구조적 커넥톰(+ 서브그래프 표본 증강)에서 뽑은 **종간 보존 위상 통계**(모듈성, 리치클럽, 클러스터링, 노드 강도 분포의 불균등도)를 향해 정규화

인간 SC-FC 데이터는 아직 HCP 실접속 없이 **합성(synthetic) 코호트**로 대체돼 있습니다(`human_data.py`) — 모듈 구조를 가진 SC 템플릿에서 개인별 변이를 주고, 그 위에서 단순 동역학을 굴려 FC를 시뮬레이션합니다. `make_cohort()`와 동일한 인터페이스(`{"sc":.., "fc":..}` 리스트)를 지키는 `load_hcp_cohort()`로 나중에 그대로 교체할 수 있도록 설계했습니다.

평가는 세 갈래로:
- **엣지 단위 정확도** — 예측 SC와 실제 SC 상삼각 벡터의 피어슨 상관계수
- **위상 통계 거리** — 모듈성·리치클럽·클러스터링·노드강도 분포의 (실제 SC 대비) 상대오차 합
- **기능적 타당성 교차검증** — 예측 SC를 `reservoir_experiment`의 리저버·벤치마크 파이프라인에 그대로 태워, 실제 SC로 얻는 메모리 용량·NARMA-10 성능과 비슷한 계산적 특성을 재현하는지 확인 (기존 실험 코드 재사용)

결과: `results/sc_prior_results.csv`, `results/sc_prior_comparison.png`, `results/sc_prior_functional_check.csv`.

**현재 알려진 한계 (정직하게 기록)**: 지금 합성 데이터로 돌려보면 `bio_prior`가 `baseline`보다 딱히 낫지 않습니다 — 합성 인간 코호트의 모듈 구조가 실제 생물학적 배선과 아무 관련이 없으니 당연한 결과입니다. 이 파일럿의 목적은 "효과를 이미 입증하는 것"이 아니라 **3단계 파이프라인이 실제로 끝까지 동작하고, 세 조건이 서로 다른 결과를 내는 것**(즉 정규화 메커니즘 자체는 작동한다는 것)을 확인하는 것입니다. 실제 신호 유무는 HCP 데이터 연동 이후에나 확인 가능합니다.

**확장 아이디어**: `human_data.py`를 실제 HCP S1200 SC/FC 쌍으로 교체, `decoder.py`의 정규화를 강도 분포(CV) 외에 모듈성·클러스터링까지 포함한 다변량 손실항으로 확장, 초파리 회로를 버섯체 외 시각엽·중심복합체로 넓혀 무척추동물 표본 수 늘리기.

## 프로젝트 구조

```
reservoir_experiment/
  connectome.py     - C. elegans 데이터 로딩, 가중치 행렬 및 널 모델 생성
  reservoir.py      - leaky-integrator 에코스테이트 네트워크 리저버
  tasks.py          - 메모리 용량 + NARMA-10 벤치마크 생성/평가
  run_experiment.py - 메인 스크립트, results/*.csv 및 *.png 생성
flyhash_experiment/
  connectome.py     - 이상화/합성편향/실측(neuprint) PN-KC 배선
  flyhash.py         - FlyHash, SimHash 구현
  run_experiment.py - 메인 스크립트, results/*.csv 및 *.png 생성
sc_prior_experiment/
  topology.py           - 그래프 위상 통계량(모듈성/리치클럽/클러스터링/강도) + 널 모델 재사용
  invertebrate_prior.py - C. elegans·초파리 커넥톰에서 종간 위상 사전분포 추출
  human_data.py         - 인간 SC-FC 합성 코호트 생성 (HCP 실데이터 연동 지점 명시)
  decoder.py            - FC→SC 베이스라인 디코더 + 사전분포 정규화 변형
  run_experiment.py     - 메인 스크립트, baseline/null_prior/bio_prior ablation, results/*.csv 및 *.png 생성
data_sources/
  celegans_multiplex/ - 받아둔 커넥톰 데이터셋 (자체 README/LICENSE 포함)
docs/
  ARCHITECTURE.md    - 아키텍처와 각 구성요소에 대한 상세 설명
  proposal.docx      - 실험 3(sc_prior_experiment)의 연구 제안서
  papers/            - 관련 논문 해설 (번역이 아닌, 읽고 재구성한 요약)
```
