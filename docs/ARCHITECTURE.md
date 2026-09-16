# 아키텍처 & 구성요소 설명

이 저장소는 서로 독립적인 세 실험(`reservoir_experiment/`, `flyhash_experiment/`, `sc_prior_experiment/`)으로 구성되어 있습니다. 앞의 두 실험은 같은 철학을 따릅니다:

```
[실제 커넥톰 데이터] → [고정된 생물학적 구조를 가진 모델] → [표준 ML 벤치마크로 채점] → [무작위/이상화 모델과 비교]
```

즉 "신경망 자체를 학습시키는" 게 아니라 **배선 구조는 고정하고, 그 위에 얹는 아주 작은 부분(선형 readout, 혹은 없음)만 학습**시킵니다. 이렇게 해야 "배선 구조 자체가 계산에 기여하는가"라는 질문에 순수하게 답할 수 있기 때문입니다.

세 번째 실험(`sc_prior_experiment/`)은 같은 "실제 구조 vs. 통계적 대조군" 프레임을 한 단계 더 밀어붙입니다: 이번엔 배선 구조 자체를 다른 종(인간)의 예측 문제에 대한 **정규화 사전분포(prior)**로 재사용합니다.

---

## 전체 디렉토리 구조

```
BrainConnectom/
├── reservoir_experiment/     실험 A: 커넥톰 기반 리저버 컴퓨팅
│   ├── connectome.py         데이터 로딩 + 가중치 행렬 + 널 모델 생성
│   ├── reservoir.py          리저버(동역학 시스템) 구현
│   ├── tasks.py               벤치마크 과제 생성 및 채점
│   └── run_experiment.py     실행 스크립트 (엔트리 포인트)
│
├── flyhash_experiment/       실험 B: 초파리 후각회로 기반 해싱
│   ├── connectome.py         PN→KC 연결성 3가지 모드 (이상화/합성/실측)
│   ├── flyhash.py             FlyHash, SimHash 알고리즘 구현
│   └── run_experiment.py     실행 스크립트 (엔트리 포인트)
│
├── sc_prior_experiment/      실험 C: 종간 위상 사전분포로 인간 구조적 커넥톰 복원
│   ├── topology.py            그래프 위상 통계량 + 널 모델 (reservoir_experiment 재사용)
│   ├── invertebrate_prior.py  C. elegans·초파리 → 종간 위상 사전분포(bio) + ER 널 대조군(null)
│   ├── human_data.py          인간 SC-FC 합성 코호트 (HCP 연동 지점 명시)
│   ├── decoder.py             FC→SC 베이스라인 + 사전분포 정규화 디코더
│   └── run_experiment.py     실행 스크립트 (엔트리 포인트)
│
├── data_sources/
│   └── celegans_multiplex/   실제 C. elegans 커넥톰 원본 데이터 (외부 프로젝트에서 받아옴)
│
├── results/                  실행할 때마다 생성되는 결과물 (csv, png) — git에는 안 올라감
├── .env.example               neuPrint API 토큰을 넣는 위치 (선택사항)
├── requirements.txt            의존성 목록 (pip freeze 결과)
└── docs/
    ├── ARCHITECTURE.md         이 문서
    └── proposal.docx           실험 C의 연구 제안서
```

세 실험은 서로 독립된 모듈이지만, `sc_prior_experiment`는 `reservoir_experiment.connectome`(널 모델)과 `flyhash_experiment.connectome`(초파리 배선), `reservoir_experiment.reservoir`/`tasks`(기능적 타당성 교차검증)를 명시적으로 import해서 재사용합니다 — 세 번째 실험이 앞의 두 실험의 결과물을 재료로 쓰는 구조이기 때문입니다. `reservoir_experiment`와 `flyhash_experiment` 둘 사이에는 여전히 상호 의존이 없어서, 이 둘 중 하나만 지우거나 복사해서 다른 프로젝트로 옮겨도 문제없이 동작합니다.

---

## 실험 A: `reservoir_experiment/` — 커넥톰 리저버 컴퓨팅

### 데이터 흐름

```
celegans_connectome_multiplex.edges (원본 텍스트 파일)
        │  connectome.load_edges()
        ▼
{(뉴런i, 뉴런j): 시냅스 가중치}  ← 화학 시냅스 레이어(2,3)만 골라서 합산
        │  connectome.build_weight_matrix()
        ▼
279×279 실측 가중치 행렬 W_real
        │  connectome.rescale_spectral_radius()  ← 모든 후보를 같은 "증폭 강도"로 정규화
        ▼
┌─────────────┬──────────────┬─────────────┬──────────────┐
│  real       │ degree_null  │  er_null    │  dense_esn   │
│ (실측 그대로) │(같은 차수분포,│(같은 엣지수, │ (생물학과 무관 │
│             │ 배선만 재구성)│ 위치만 무작위)│ 한 랜덤 가우시안)│
└─────────────┴──────────────┴─────────────┴──────────────┘
        │  reservoir.LeakyESN.run(입력 신호)
        ▼
시간에 따른 리저버 내부 상태(state) 시퀀스
        │  tasks.evaluate_memory_capacity() / evaluate_narma10()
        ▼
Ridge 회귀로 readout만 학습 → 점수(메모리 용량, NARMA-10 NRMSE)
        │  run_experiment.py가 여러 시드로 반복 후 집계
        ▼
results/reservoir_results.csv, results/reservoir_comparison.png
```

### 모듈별 설명

**`connectome.py` — 데이터와 "비교 대상" 생성**
- `load_edges(layers)` : 원본 엣지 파일을 파싱합니다. 데이터셋은 레이어 1(전기적 갭 정션), 2(단일 화학 시냅스), 3(다중 화학 시냅스)로 나뉘어 있는데, 기본값은 화학 시냅스인 2·3번 레이어를 합산해서 사용합니다.
- `build_weight_matrix()` : 위 엣지 딕셔너리를 279×279 numpy 행렬로 바꿉니다. 행/열 인덱스는 뉴런 ID, 값은 실제 시냅스 개수입니다.
- `rescale_spectral_radius()` : 리저버 컴퓨팅에서는 가중치 행렬의 "스펙트럴 반지름"(가장 큰 고유값의 절댓값)이 동역학의 안정성·기억력을 크게 좌우합니다. 네 가지 모델을 공정하게 비교하려면 이 값을 전부 똑같이 맞춰야 하므로, 어떤 원본 행렬이 와도 목표 스펙트럴 반지름으로 스케일링하는 함수가 따로 있습니다.
- `null_model_degree_preserving()` : 실측 그래프의 "각 뉴런이 몇 개의 연결을 갖는가"(차수 분포)는 그대로 유지한 채, `networkx.directed_edge_swap`으로 실제 연결 상대만 무작위로 뒤섞습니다. "차수 분포는 같지만 배선 패턴 자체는 다른" 대조군입니다.
- `null_model_erdos_renyi()` : 엣지 개수만 맞추고 위치는 완전 무작위로 배치하는, 가장 단순한 무작위 그래프 대조군입니다.
- `null_model_dense_gaussian()` : 생물학적 구조를 전혀 참고하지 않는, 리저버 컴퓨팅 교과서에 나오는 표준 "에코 스테이트 네트워크(ESN)" 방식 — 밀도만 맞춘 무작위 가우시안 가중치입니다.

**`reservoir.py` — 동역학 시스템**
- `LeakyESN` 클래스 하나만 있습니다. 표준 leaky-integrator 리저버 방정식을 구현합니다:
  `x[t+1] = (1-leak)·x[t] + leak·tanh(W·x[t] + Win·u[t])`
  - `W`는 위에서 만든 4가지 커넥톰 행렬 중 하나
  - `Win`은 입력을 리저버로 투사하는 무작위 가중치(뉴런 개수 × 입력 차원)이며, 매 실행마다 새로 생성됩니다
  - `leak`은 리저버가 과거를 얼마나 빨리 "잊는지" 조절하는 값(기본 0.3)
- `run(u)` : 입력 시퀀스를 한 스텝씩 흘려보내며 매 시점의 내부 상태(279차원 벡터)를 기록해 반환합니다. 이후 이 상태들이 readout 학습의 입력(feature)이 됩니다.

**`tasks.py` — 벤치마크 과제**
- `generate_memory_capacity_input()` / `evaluate_memory_capacity()` : Jaeger(2001)가 제안한 고전적 리저버 컴퓨팅 벤치마크입니다. 무작위 입력을 리저버에 흘려보낸 뒤, "k 스텝 전의 입력값을 지금 리저버 상태만 보고 얼마나 정확히 복원할 수 있는가"를 delay 1~30에 대해 각각 선형회귀(Ridge)로 측정하고 R²를 전부 더합니다. 이 총합이 클수록 리저버가 "단기 기억"을 잘 유지한다는 뜻입니다.
- `generate_narma10()` / `evaluate_narma10()` : NARMA-10은 표준 비선형 시계열 예측 벤치마크입니다(과거 10 스텝의 값과 입력에 비선형적으로 의존하는 수식으로 생성). 리저버 상태로부터 다음 값을 선형회귀로 예측하고 NRMSE(정규화된 오차, 낮을수록 좋음)로 채점합니다.
- 두 과제 모두 "리저버 자체는 학습시키지 않고, 그 위에 얹는 선형 readout만 학습시킨다"는 리저버 컴퓨팅의 핵심 원칙을 따릅니다.

**`run_experiment.py` — 오케스트레이션**
- `build_variants()` : 커넥톰을 불러와 4가지 리저버 후보를 만들고 전부 같은 스펙트럴 반지름으로 정규화합니다.
- `run_trial()` : 시드 하나에 대해 4가지 리저버 각각을 두 벤치마크에 태워 점수를 냅니다.
- `main()` : `--n-trials`만큼 시드를 바꿔가며 반복하고, 평균·표준편차를 표로 출력한 뒤 `results/`에 CSV와 막대그래프 PNG로 저장합니다. 트라이얼을 늘릴수록(예: `--n-trials 50`) 통계적으로 더 믿을 만한 결과가 나옵니다.

---

## 실험 B: `flyhash_experiment/` — 초파리 후각회로 기반 해싱

### 데이터 흐름

```
┌───────────────┬──────────────────────┬────────────────────┐
│  idealized     │  biased_synthetic    │  real (neuprint)    │
│ (원 논문의     │ (토큰 없을 때 자동    │ (hemibrain 실측 데이터,│
│  균등 무작위   │  대체되는, 통계적으로 │  .env에 토큰 설정 시) │
│  모델)         │  좀 더 사실적인 모델) │                     │
└───────────────┴──────────────────────┴────────────────────┘
        │  각각 (2000 KC × 50 PN) 형태의 연결 가중치 행렬
        ▼
FlyHash(연결 가중치)
        │  1) 입력 벡터(64차원 손글씨 숫자 이미지)를 무작위 투사로 50차원 "PN 활성"으로 변환
        │  2) PN 활성 × 연결 가중치 = 2000개 Kenyon cell의 활성값
        │  3) 상위 5%만 남기고 나머지는 0으로 (winner-take-all)
        ▼
희소 이진 해시 코드 (샘플마다 2000비트 중 ~5%만 1)
        │  run_experiment.recall_at_k()
        ▼
"진짜" 유클리드 최근접 이웃과 얼마나 겹치는지(recall@k) 비교
        │  SimHash(고전 LSH) 베이스라인과도 비교
        ▼
results/flyhash_results.csv, results/flyhash_comparison.png
```

### 모듈별 설명

**`connectome.py` — 세 가지 연결성 모델**
- `idealized_connectivity()` : Dasgupta et al. (2017, Science) 원 논문이 이론 분석에 사용한 모델입니다. Kenyon cell 하나가 정확히 6개의 projection neuron을 균등 무작위로, 중복 없이 골라 연결됩니다(가중치는 전부 1).
- `biased_synthetic_connectivity()` : 실제 전자현미경 재구성 결과는 이렇게 깔끔하지 않다는 점을 반영한 모델입니다. ① 각 KC가 연결하는 PN 개수(차수)가 정확히 6이 아니라 평균 6짜리 **포아송 분포**를 따르고, ② 모든 PN이 똑같이 자주 선택되는 게 아니라 일부 PN이 지프(Zipf) 분포처럼 유난히 "인기 있게" 선택됩니다. neuPrint 토큰이 없을 때 실험은 자동으로 이 모델을 사용합니다.
- `try_fetch_real_connectivity()` : `.env`에 `NEUPRINT_TOKEN`이 설정돼 있으면 `neuprint-python`으로 hemibrain 데이터셋에 실제 접속해서, 이름에 "PN"이 들어간 뉴런과 "KC"로 시작하는 Kenyon cell 사이의 **실측 시냅스 개수**를 그대로 가중치 행렬로 만듭니다. 토큰이 없거나 네트워크 요청이 실패하면 예외를 잡아서 `None`을 반환하고, 호출한 쪽(`run_experiment.py`)이 자동으로 `biased_synthetic_connectivity()`로 대체합니다 — 즉 인터넷이 없어도, 토큰이 없어도 실험 전체는 항상 끝까지 돌아갑니다.

**`flyhash.py` — 해싱 알고리즘 두 가지**
- `FlyHash` 클래스 : 위 세 가지 연결성 행렬 중 하나를 받아서, 입력 벡터를 희소 이진 해시 코드로 바꿉니다.
  - `_project_to_pn_space()` : 원본 입력(예: 64차원 이미지 픽셀)을 무작위 선형 투사로 50차원 "PN 활성값"으로 바꿉니다. 실제 초파리가 냄새 분자를 50개 남짓한 후각수용체 뉴런 활성 패턴으로 바꾸는 과정을 흉내 낸 것입니다.
  - `hash()` : PN 활성값에 연결 가중치 행렬을 곱해 2000개 KC의 활성값을 얻고, 그중 상위 몇 %(기본 5%, `wta_sparsity`)만 1로 남기고 나머지는 0으로 만듭니다. 이 "승자독식(winner-take-all)" 과정이 실제 뇌에서는 APL이라는 억제성 뉴런 하나가 담당하는 것으로 알려져 있습니다.
- `SimHash` 클래스 : 비교 기준이 되는 고전적 LSH입니다. 무작위 초평면을 여러 개 그어서 입력이 초평면의 어느 쪽에 있는지(0/1)로 해시 코드를 만드는, 생물학과 무관한 표준 알고리즘입니다.
- `hamming_neighbors()` : 해시 코드 사이의 해밍 거리(다른 비트 개수)가 가장 작은 순서로 이웃을 찾는 헬퍼 함수입니다.

**`run_experiment.py` — 오케스트레이션**
- `true_neighbors()` : sklearn `digits` 데이터셋(손글씨 숫자, 1797개 샘플, 64차원)에서 원본 공간의 유클리드 거리 기준 "정답" 최근접 이웃을 미리 계산해둡니다.
- `build_methods()` : 이상화/합성편향/실측(가능하면) 연결성으로 만든 FlyHash 3종과 SimHash 베이스라인, 총 최대 4가지 방법을 준비합니다.
- `recall_at_k()` : 각 방법이 만든 해시 코드로 찾은 "이웃"이, 미리 계산해둔 진짜 이웃과 얼마나 겹치는지(recall@k)를 채점합니다.
- `main()` : 전체를 실행하고 결과를 표로 출력한 뒤 `results/`에 CSV와 recall@k 곡선 그래프로 저장합니다.

---

## 실험 C: `sc_prior_experiment/` — 종간 위상 사전분포로 인간 구조적 커넥톰 복원

### 데이터 흐름

```
C. elegans 실측 커넥톰 ──┐
                         ├─ subsample_subgraph() 증강 ─┐
초파리 PN→KC (bipartite embed) ─┘                      │
                                                        ▼
                              topology_signature() [모듈성/리치클럽/클러스터링/강도]
                                     │ (real)                    │ (erdos_renyi_null)
                                     ▼                            ▼
                              bio_prior {stat: mean,std}   null_prior {stat: mean,std}

인간 SC-FC 합성 코호트 (human_data.make_cohort)
        │  train/test 분할
        ▼
Ridge 회귀로 FC→SC 베이스라인 디코더 학습 (decoder.train_baseline_decoder)
        │
        ├─ baseline 예측        = predict_sc(model, fc)
        ├─ null_prior 예측      = prior_regularized_predict(..., null_prior)
        └─ bio_prior 예측       = prior_regularized_predict(..., bio_prior)
                 │  세 조건 모두 실제 SC와 비교
                 ▼
        edge_correlation() / topology_distance()
                 │  대표 피험자 1명은 추가로
                 ▼
   reservoir_experiment.LeakyESN + tasks 로 "기능적 타당성" 교차검증
                 │
                 ▼
results/sc_prior_results.csv, sc_prior_comparison.png, sc_prior_functional_check.csv
```

### 모듈별 설명

**`topology.py` — 그래프 수준 통계량과 증강**
- `topology_signature(W)` : 모듈성(greedy modularity), 리치클럽 계수, 노드 강도 평균/표준편차, (선택적으로) 가중 클러스터링 계수를 딕셔너리로 반환합니다. 전부 **그래프 전체 수준**의 스칼라 통계이고, 개별 노드(뉴런) 단위 정보는 전혀 쓰지 않습니다 — 무척추동물 뉴런과 인간 거시 ROI는 노드 단위로 대응시킬 방법이 없기 때문에, 이 설계가 종간 노드 불일치 문제를 원천적으로 피해갑니다.
- `subsample_subgraph(W, frac_nodes)` : 실측 그래프에서 노드를 무작위로 골라낸 induced subgraph. 널 모델과 달리 엣지를 뒤섞지 않고 **진짜 배선을 그대로 유지**하기 때문에, 원본 그래프가 딱 2개(C. elegans, 초파리)뿐인 상황에서 "진짜 생물학적 구조" 표본을 늘리는 합법적인 방법입니다.
- `erdos_renyi_null` / `degree_preserving_null` : `reservoir_experiment.connectome`의 함수를 그대로 재노출합니다. 부정 대조군(null_prior)에는 **일부러 degree-preserving이 아니라 ER 널을 씁니다** — decoder.py의 정규화가 노드 강도 분포(정확히는 강도의 변동계수, CV)를 타겟으로 하는데, degree-preserving 널은 정의상 원본과 강도 분포가 거의 같아서 이 통계량에 대해서는 의미 있는 대조군이 되지 못하기 때문입니다.

**`invertebrate_prior.py` — 종간 사전분포 추출**
- `_embed_bipartite()` : 초파리 PN→KC 연결(KC 수 × PN 수 직사각 행렬)을 정사각 인접행렬로 임베딩합니다. 이 그래프는 구조상 이분 그래프(bipartite)라 삼각형이 존재할 수 없으므로 클러스터링 계수는 항상 0입니다 — 버그가 아니라 그래프 종류 자체의 성질이라, 초파리 쪽에서는 클러스터링을 사전분포 계산에서 아예 제외합니다.
- `build_prior()` : C. elegans(실측 + 서브그래프 8개) + 초파리(실측 + 서브그래프 8개), 총 18개 그래프 표본의 위상 통계 평균·표준편차를 모아 `bio_prior`를, 같은 그래프들의 ER 널 버전으로 `null_prior`를 만듭니다.

**`human_data.py` — 인간 SC-FC 코호트 (현재는 합성 데이터)**
- HCP 실데이터는 2주 파일럿 범위 밖입니다. 대신 `make_group_template_sc()`로 모듈 구조를 가진 그룹 SC 템플릿을 만들고, `perturb_individual_sc()`로 피험자별 변이를 주고, `simulate_fc_from_sc()`로 (reservoir.py의 leaky-integrator와 같은 방식의) 단순 제약 동역학을 돌려 FC를 시뮬레이션합니다.
- `load_hcp_cohort()`는 아직 `NotImplementedError`만 던지는 스텁입니다 — docstring에 실제 HCP 연동 시 무엇을 채워야 하는지 적어뒀고, `make_cohort()`와 똑같은 반환 형태(`[{"sc":..., "fc":...}, ...]`)만 지키면 나머지 파이프라인은 한 줄도 안 바꿔도 됩니다. flyhash_experiment가 neuPrint 토큰 유무와 무관하게 항상 끝까지 도는 것과 같은 설계 원칙입니다.

**`decoder.py` — 베이스라인과 사전분포 정규화**
- `train_baseline_decoder()` : FC 상삼각 벡터 → SC 상삼각 벡터로 가는 Ridge 회귀. 인간 데이터만 쓰는 순수 지도학습 베이스라인입니다.
- `_reshape_toward_target_hubness()` : 예측된 SC의 노드 강도 분포를 사전분포가 가진 변동계수(CV = std/mean)를 향해 **재구성**합니다. 전역 스케일만 곱하는 방식은 피어슨 상관계수에 영향을 줄 수 없어서(상관계수는 양의 배율 변환에 불변) 처음 구현에서 걸러졌고, 지금은 노드별 강도 조정량의 기하평균으로 각 엣지를 개별 재조정합니다 — "리치클럽/허브 구조가 종을 초월해 보존된다"는 사전분포를 실제 엣지 패턴 변화로 연결하는 구현입니다.
- `prior_regularized_predict()` : 위 재구성을 베이스라인 예측과 `alpha_blend` 비율로 섞습니다.

**`run_experiment.py` — 오케스트레이션**
- `edge_correlation()` : 예측/실제 SC 상삼각 벡터의 피어슨 상관계수.
- `topology_distance()` : 공유 통계량(모듈성/리치클럽/클러스터링/강도) 각각의 **상대오차** 제곱합의 제곱근. 절대오차를 쓰지 않는 이유는 통계량마다 자연스러운 스케일이 완전히 달라서(모듈성은 0~1, 강도는 임의 단위) 절대오차 합이 스케일 큰 항에 지배당하기 때문입니다.
- `functional_validity_check()` : 대표 피험자 1명에 대해, 예측 SC와 실제 SC를 각각 `reservoir_experiment`의 `LeakyESN` + `tasks`(메모리 용량, NARMA-10)에 그대로 태워 계산적 특성이 비슷한지 확인합니다 — "엣지가 통계적으로 비슷하다"를 넘어 "계산적으로도 비슷하게 행동하는가"를 보는 독립적인 검증입니다.
- `main()` : 세 조건(`baseline`/`null_prior`/`bio_prior`)을 테스트 피험자 전체에 대해 비교하고 `results/`에 CSV 2개와 막대그래프를 저장합니다.

### 지금 합성 데이터로 실행하면 나오는 결과 (정직하게 기록)

`python -m sc_prior_experiment.run_experiment --n-subjects 20 --n-regions 50`로 돌려보면 `bio_prior`가 `baseline`보다 엣지 상관계수·위상 거리 양쪽에서 오히려 살짝 나쁘게 나옵니다. 합성 인간 코호트의 모듈 구조가 실제 생물학적 배선과 아무 관계가 없으니 당연한 결과이고, 이 파일럿 단계의 목표는 애초에 "효과를 입증"하는 게 아니라 **3단계 파이프라인이 끝까지 동작하고, 세 조건이 실제로 서로 다른 예측을 만들어낸다**(즉 정규화 메커니즘 자체는 살아있다)는 것을 확인하는 것입니다. 진짜 신호가 있는지는 `human_data.py`를 실제 HCP 데이터로 교체한 뒤에만 답할 수 있습니다.

## 공통 설계 결정 이유

- **왜 conn2res를 직접 의존성으로 안 썼나** : 2022년 이후 유지보수가 끊긴 학술 툴박스라 Python 3.8/3.9, numpy 1.22, `gym==0.21.0`에 고정돼 있고, 이 조합이 최신 setuptools/Python 3.13에서 아예 빌드되지 않습니다(자세한 내용은 이 저장소를 만들 때의 대화 기록 참고). 핵심 아이디어만 가져와 직접 구현하는 편이 의존성 문제 없이 코드를 완전히 이해하고 수정할 수 있어 개인 연구에 더 적합하다고 판단했습니다.
- **왜 "실측 데이터가 없어도 항상 끝까지 실행되게" 만들었나** : neuPrint 토큰 발급은 사용자가 직접 해야 하는 외부 가입 절차이기 때문에, 이게 없어도 즉시 결과를 볼 수 있어야 실험을 이어갈 동기가 생깁니다. 대신 대체 모델(무작위/합성편향)에는 항상 어떤 모델이 쓰였는지 콘솔에 명시적으로 출력합니다.
- **왜 스펙트럴 반지름을 통일하나 (실험 A)** : 그렇지 않으면 "배선 구조 차이" 때문에 성능이 다른 건지, 단순히 "증폭 강도가 우연히 달라서" 다른 건지 구분할 수 없기 때문입니다. 리저버 컴퓨팅 분야에서 topology를 공정 비교할 때 쓰는 표준적인 관행입니다.
- **왜 세 가지 널 모델을 두나 (실험 A)** : `degree_null`과 `er_null`은 "무작위성의 강도"가 다릅니다. `degree_null`은 실측 그래프와 차수 분포까지 같아서 가장 엄격한 대조군이고, `er_null`은 엣지 개수만 같은 느슨한 대조군, `dense_esn`은 생물학과 아예 무관한 기준선입니다. 세 단계로 비교해야 "정확히 어떤 통계적 성질이 성능 차이를 만드는지" 좁혀갈 수 있습니다.

## 확장하고 싶을 때 어디를 고치면 되는지

| 하고 싶은 것 | 수정할 파일 |
|---|---|
| 다른 커넥톰 레이어(전기 시냅스) 써보기 | `reservoir_experiment/connectome.py`의 `build_weight_matrix(layers=...)` 호출부 |
| 더 큰/다른 종의 커넥톰으로 교체 | `reservoir_experiment/connectome.py`에 새 로더 함수 추가 |
| 새로운 벤치마크 과제 추가 | `reservoir_experiment/tasks.py`에 함수 추가 후 `run_experiment.py`에서 호출 |
| FlyHash의 희소도(WTA 비율) 바꾸기 | `flyhash_experiment/flyhash.py`의 `FlyHash(wta_sparsity=...)` |
| 다른 입력 데이터셋으로 FlyHash 테스트 | `flyhash_experiment/run_experiment.py`의 `load_digits()` 부분 교체 |
| 실측 커넥톰을 다른 회로로 바꾸기(예: 시각엽) | `flyhash_experiment/connectome.py`의 `try_fetch_real_connectivity()`에서 `NeuronCriteria` 쿼리 조건 수정 |
| 실제 HCP SC/FC 데이터 연동 | `sc_prior_experiment/human_data.py`의 `load_hcp_cohort()` 구현, `run_experiment.py`에서 `make_cohort()` 호출을 교체 |
| 사전분포 정규화에 모듈성·클러스터링도 포함 | `sc_prior_experiment/decoder.py`의 `_reshape_toward_target_hubness()` 확장 (현재는 강도 CV만 사용) |
| 무척추동물 표본 수 늘리기 | `sc_prior_experiment/invertebrate_prior.py`에 유충 초파리 전뇌·시각엽 등 새 로더 추가 |
