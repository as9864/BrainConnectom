# BrainConnectom

실제 커넥톰(뇌신경 배선 데이터)을 머신러닝 파이프라인에 직접 꽂아보는 개인 연구용 실험 세 가지입니다.

1. **conn2res 스타일 리저버 컴퓨팅** — 실제 예쁜꼬마선충(C. elegans) 커넥톰이 같은 크기·밀도·스펙트럴 반지름의 무작위 그래프보다 더 나은 "리저버"가 되는가? (`reservoir_experiment/`)
2. **실제 배선을 반영한 FlyHash** — 초파리 후각회로 기반 유사도 해싱(FlyHash)에서, 이상화된 균등 무작위 연결 대신 생물학적으로 편향된(비균등) PN→Kenyon cell 연결을 쓰면 최근접 이웃 검색 성능이 달라지는가? (`flyhash_experiment/`)
3. **종간 보존된 위상학적 사전정보로 인간 구조적 커넥톰 복원** — C. elegans·초파리 구조적 커넥톰에서 뽑아낸 "종을 초월해 보존된 배선 통계"가, 인간 기능적 커넥톰(FC)만으로 구조적 커넥톰(SC)을 복원하는 문제에 도움이 되는가? → **별도 저장소 [StructuralConnectomeTransfer](https://github.com/as9864/StructuralConnectomeTransfer)로 옮겼습니다** (지금은 "종간 배선 원리가 인간 뇌로 얼마나 옮겨 가는가"로 질문이 바뀜)

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

**확장 아이디어**: 다른 뉴런 서브셋/레이어 사용(화학 시냅스 대신 전기 갭 정션), 더 큰 커넥톰으로 교체(hemibrain의 초파리 회로, CAVE/MICrONS로 마우스 피질), reciprocity나 거리 의존성을 보존하는 다른 널 모델 시도 등.

## 2. FlyHash (`flyhash_experiment/`)

```bash
python -m flyhash_experiment.run_experiment
```

sklearn의 `digits` 데이터셋으로 실제 유클리드 최근접 이웃 대비 recall@k를 비교합니다:
- `flyhash_idealized` — Dasgupta et al. 원 논문 모델: 각 Kenyon cell이 정확히 6개의 projection neuron을 균등 무작위로 샘플링
- `flyhash_biased_synthetic` — 좀 더 현실적인 대체 모델: KC마다 차수가 변동(Poisson 분포)하고 PN 샘플링도 비균등("인기 있는" PN vs "드문" PN) — 실측 데이터를 쓸 수 없을 때의 대체 모델
- `flyhash_real_hemibrain` — hemibrain v1.2 커넥톰에서 **실측된** PN→KC 시냅스 개수(KC 1802개 × PN 157개)를 그대로 사용. 데이터는 `data_sources/hemibrain/`에 들어 있어서 토큰 없이 바로 실행됩니다
- `simhash_baseline` — 비교 기준이 되는 고전적 랜덤 초평면 LSH

결과: `results/flyhash_results.csv`, `results/flyhash_comparison.png`.

### 실측 hemibrain 데이터

`data_sources/hemibrain/`에는 Janelia가 공개한 hemibrain v1.2 export(CC BY 4.0)에서 뽑은 PN→KC 연결과 회로 서브그래프가 들어 있습니다. 토큰도 인터넷도 필요 없습니다. 원본에서 다시 만들고 싶으면:

```bash
python -m flyhash_experiment.hemibrain --build   # 약 46MB 다운로드 후 derived 파일 재생성
```

neuPrint 토큰(`.env`의 `NEUPRINT_TOKEN`)은 이 파일이 없을 때만 대체 경로로 쓰입니다. 다른 데이터셋 버전이나 다른 쿼리가 필요할 때 사용하세요.

**여기가 실제로 아직 명확히 답이 안 나온 연구 질문입니다**: 초파리의 실제 배선(비균등)이 원 논문에서 이론적으로 분석한 이상화된 균등 무작위 모델보다 해시 품질 면에서 유리한지 불리한지는 아직 잘 다뤄지지 않았습니다. 실제 데이터를 연동한 뒤에는 `FlyHash`의 `wta_sparsity`를 바꿔보거나, `digits` 대신 더 고차원인 데이터(예: 문장 임베딩)로 바꿔서 입력 차원에 따라 효과가 달라지는지도 확인해볼 만합니다.

## 3. 구조적 커넥톰 복원 → [StructuralConnectomeTransfer](https://github.com/as9864/StructuralConnectomeTransfer)

이 실험은 별도 저장소로 옮겼습니다. 코드, 데이터, 제안서, 논문 초안, 읽기 목록과 git 이력이 모두 그쪽에 있습니다. 이 저장소의 예전 커밋에는 `sc_prior_experiment/`로 남아 있습니다.

## 프로젝트 구조

```
reservoir_experiment/
  connectome.py     - C. elegans 데이터 로딩, 가중치 행렬 및 널 모델 생성
  reservoir.py      - leaky-integrator 에코스테이트 네트워크 리저버
  tasks.py          - 메모리 용량 + NARMA-10 벤치마크 생성/평가
  run_experiment.py - 메인 스크립트, results/*.csv 및 *.png 생성
flyhash_experiment/
  connectome.py     - 이상화/합성편향/실측(hemibrain) PN-KC 배선
  hemibrain.py      - hemibrain 공개 export → 실측 PN-KC 행렬 생성/로딩
  flyhash.py         - FlyHash, SimHash 구현
  run_experiment.py - 메인 스크립트, results/*.csv 및 *.png 생성
data_sources/
  celegans_multiplex/ - 받아둔 커넥톰 데이터셋 (자체 README/LICENSE 포함)
  hemibrain/          - 초파리 hemibrain v1.2에서 뽑은 PN-KC 연결 (자체 README, CC BY 4.0)
docs/
  ARCHITECTURE.md    - 아키텍처와 각 구성요소에 대한 상세 설명
  papers/            - 관련 논문 해설 (번역이 아닌, 읽고 재구성한 요약) + READING_LIST.md(배경 논문 읽기 목록), SUMMARIES.md(논문별 요약)
```
