# 아키텍처 & 구성요소 설명

이 저장소의 두 실험(`reservoir_experiment/`, `flyhash_experiment/`)은 같은 철학을 따릅니다. 세 번째 실험이던 구조적 커넥톰 복원은 독립 프로젝트 [`sc_transfer/`](../sc_transfer/)로 분리했습니다.

```
[실제 커넥톰 데이터] → [고정된 생물학적 구조를 가진 모델] → [표준 ML 벤치마크로 채점] → [무작위/이상화 모델과 비교]
```

즉 "신경망 자체를 학습시키는" 게 아니라 **배선 구조는 고정하고, 그 위에 얹는 아주 작은 부분(선형 readout, 혹은 없음)만 학습**시킵니다. 이렇게 해야 "배선 구조 자체가 계산에 기여하는가"라는 질문에 순수하게 답할 수 있기 때문입니다.

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
│   ├── hemibrain.py          hemibrain 공개 export → 실측 PN→KC 행렬 (토큰 불필요)
│   ├── flyhash.py             FlyHash, SimHash 알고리즘 구현
│   └── run_experiment.py     실행 스크립트 (엔트리 포인트)
│
├── sc_transfer/              (분리됨) 종간 배선 원리 전이 가능성 프로젝트 — 자체 README·문서·데이터
│
├── data_sources/
│   ├── celegans_multiplex/   실제 C. elegans 커넥톰 원본 데이터 (외부 프로젝트에서 받아옴)
│   └── hemibrain/            초파리 hemibrain v1.2에서 뽑은 PN→KC 연결 (CC BY 4.0, 자체 README)
│
├── results/                  실행할 때마다 생성되는 결과물 (csv, png) — git에는 안 올라감
├── .env.example               neuPrint API 토큰을 넣는 위치 (선택사항)
├── requirements.txt            의존성 목록 (pip freeze 결과)
└── docs/
    └── ARCHITECTURE.md         이 문서
```

`reservoir_experiment`와 `flyhash_experiment` 사이에는 상호 의존이 없어서, 둘 중 하나만 지우거나 복사해서 다른 프로젝트로 옮겨도 문제없이 동작합니다. `sc_transfer/`는 필요한 코드(C. elegans 로더, 널 모델, 리저버, 초파리 회로)를 자체 사본으로 가지고 있어 이 두 실험과도 독립적입니다.

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
│  균등 무작위   │  대체되는, 통계적으로 │  저장소에 포함, 토큰 불필요)│
│  모델)         │  좀 더 사실적인 모델) │                     │
└───────────────┴──────────────────────┴────────────────────┘
        │  (KC × PN) 연결 가중치 행렬 — 이상화/합성은 2000×50, 실측은 1802×157
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
- `biased_synthetic_connectivity()` : 실제 전자현미경 재구성 결과는 이렇게 깔끔하지 않다는 점을 반영한 모델입니다. ① 각 KC가 연결하는 PN 개수(차수)가 정확히 6이 아니라 평균 6짜리 **포아송 분포**를 따르고, ② 모든 PN이 똑같이 자주 선택되는 게 아니라 일부 PN이 지프(Zipf) 분포처럼 유난히 "인기 있게" 선택됩니다. 실측 데이터를 쓸 수 없을 때의 대체 모델입니다.
- `try_fetch_real_connectivity()` : hemibrain v1.2의 **실측 PN→KC 시냅스 개수**를 가중치 행렬로 돌려줍니다. 먼저 저장소에 포함된 `data_sources/hemibrain/pn_kc.npz`(Janelia가 공개한 export에서 `hemibrain.py`로 뽑은 파일, 토큰 불필요)를 읽고, 이 파일이 없을 때만 `.env`의 `NEUPRINT_TOKEN`으로 neuPrint에 직접 접속합니다. 둘 다 안 되면 `None`을 반환하고 호출한 쪽이 `biased_synthetic_connectivity()`로 대체합니다 — 인터넷이 없어도 실험 전체는 항상 끝까지 돌아갑니다.
- `hemibrain.py` : 공개 export(`traced-neurons.csv`, `traced-total-connections.csv`, `traced-roi-connections.csv`)를 받아서 ① PN→KC 행렬과 ② 뇌 영역(ROI) 단위로 자른 회로 서브그래프 5개(버섯체, 중심복합체, 측각, 더듬이엽, 외측 복합체)를 만듭니다. `python -m flyhash_experiment.hemibrain --build`로 다시 생성할 수 있습니다.

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

## 실험 C → `sc_transfer/`로 분리

구조적 커넥톰 복원 실험은 독립 프로젝트가 되었습니다. 설계와 방법론은 [sc_transfer/README.md](../sc_transfer/README.md)와 [sc_transfer/docs/methodology_transferability.md](../sc_transfer/docs/methodology_transferability.md)를 보세요.

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
