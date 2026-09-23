# 종간 보존된 위상학적 사전정보를 활용한 인간 구조적 커넥톰 복원

제출자: 한승엽 · 제출일: 2026년 9월 17일

*(`docs/proposal.docx`의 내용을 마크다운으로 옮긴 사본입니다. `sc_prior_experiment/`의 원 제안서.)*

## 1. 연구 배경 및 필요성

뇌의 구조적 커넥톰(structural connectome)과 기능적 커넥톰(functional connectome)은 서로 다른 정보를 담고 있지만 밀접하게 연관되어 있다. 구조는 기능이 일어날 수 있는 물리적 제약을 제공하고, 기능은 구조 위에서 발생하는 동역학의 결과이다. 최근 그래프 신경망(GNN)을 이용해 구조에서 기능을 예측하는 연구는 상당한 성과를 거두었다(HCP 998명 데이터 기준 기능적 연결성 분산의 약 89% 설명).

그러나 역방향, 즉 기능적 연결성만으로 구조적 배선을 복원하는 문제는 훨씬 어렵다. 본질적으로 ill-posed(불량조건) 역문제로, 서로 다른 여러 구조적 배선이 유사한 기능적 연결 패턴을 만들어낼 수 있기 때문이다. 이 문제를 풀려면 "생물학적으로 그럴듯한 배선이란 무엇인가"에 대한 추가적인 사전 지식(prior)이 필요하다.

비교 커넥톰믹스(comparative connectomics) 연구는 C. elegans부터 초파리, 어류, 포유류, 인간에 이르기까지 신경계 규모가 수백~수억 배 차이남에도 불구하고, 모듈성(modularity)·리치클럽 구조(rich-club organization)·배선 비용 최소화(wiring economy) 같은 위상학적 원리가 공통적으로 보존되어 있음을 반복적으로 보고해왔다. 본 연구는 이 "종을 초월해 보존된 배선 원리"를 인간 구조적 커넥톰 복원 문제에 대한 생물학적으로 근거 있는 사전분포(prior)로 활용할 수 있는지를 검증하고자 한다.

본 제안은 제출자가 이미 진행해 온 두 개인 연구 — **실제 C. elegans 커넥톰 기반 리저버 컴퓨팅 실험**과 **초파리 후각회로 기반 FlyHash 실험** — 에서 공통적으로 사용한 "실제 생물학적 배선 vs. 무작위 널 모델(null model)" 비교 방법론을 그대로 확장한 것으로, 축적된 코드베이스와 데이터를 재사용할 수 있다는 실행 가능성 측면의 이점이 있다.

## 2. 연구 목표

**"무척추동물(C. elegans, 초파리) 구조적 커넥톰에서 학습한, 종을 초월해 보존된 위상학적 통계 사전분포가, 인간 기능적 커넥톰으로부터 구조적 커넥톰을 복원하는 문제의 정확도와 생물학적 타당성을 향상시키는가?"**

- 세부목표 1 — 인간 HCP 데이터만을 이용한 FC→SC 디코더 베이스라인을 구축하고 기존 연구 결과를 재현한다.
- 세부목표 2 — C. elegans·초파리 구조적 커넥톰(및 데이터 증강된 변형)으로부터 그래프 생성모델을 학습하여, 생물학적으로 보존된 위상 통계 분포(모듈성, 리치클럽 계수, 차수분포, 클러스터링 계수 등)를 추출한다.
- 세부목표 3 — 세부목표 2에서 얻은 분포를 정규화 항(prior)으로 결합한 FC→SC 모델이 베이스라인 대비 복원 정확도·생물학적 타당성·저데이터 일반화 성능에서 개선을 보이는지 ablation 실험으로 검증한다.

## 3. 관련 연구

### 3.1 구조-기능 결합(SC-FC coupling) 연구

그래프 신경망을 이용해 구조적 커넥티비티로부터 기능적 커넥티비티 및 중심성(centrality)을 예측하는 연구(Sarwar et al., 2021)는 HCP 데이터에서 평균 분산의 89%, 중심성의 99%를 설명하는 성과를 보였다. 반대 방향인 기능에서 구조를 예측하는 문제는 상대적으로 덜 연구되었으며, 최근 리뷰(Network Neuroscience, 2024)는 이 방향의 예측이 근본적으로 더 어렵고 방법론적으로 아직 합의가 부족하다고 평가한다. 본 연구는 이 공백을 다룬다.

### 3.2 비교 커넥톰믹스와 보존된 배선 원리

C. elegans, Platynereis, 초파리, 제브라피시, 마우스 등 단일 뉴런 해상도로 재구성된 다종(多種) 커넥톰을 비교한 연구들은, 신경계 규모가 수 자릿수 차이남에도 불구하고 모듈 구조·리치클럽·배선 경제성(wiring economy) 같은 위상학적 특성이 반복적으로 나타난다는 것을 보였다(Bullmore & Sporns, 2012 및 후속 비교 연구들). 이는 본 제안이 가정하는 "종을 초월한 위상학적 사전분포"의 생물학적 근거가 된다.

### 3.3 본 연구의 위치

본 연구는 (1) 인간 내부 데이터만으로 학습하는 기존 SC-FC 결합 모델과, (2) 위상학적 통계량이 종을 초월해 보존된다는 비교 커넥톰믹스 발견, 이 두 가지를 결합하여, 무척추동물 데이터를 인간 구조 복원의 정규화 사전분포로 사용하는 시도라는 점에서 기존 연구와 구별된다.

## 4. 연구 내용 및 방법

### 4.1 데이터

- C. elegans 화학 시냅스 커넥톰(뉴런 279개) — CoMuNeLab/C-elegans-Multiplex-Connectome, 본 저장소에 이미 확보됨(`data_sources/celegans_multiplex`)
- 초파리 hemibrain 커넥톰(PN→Kenyon cell 등 회로별 서브그래프) — neuPrint 연동, 본 저장소에 이미 파이프라인 구축됨(`flyhash_experiment/connectome.py`)
- 가능 시 추가 확보: 유충 초파리 전뇌 커넥톰(Winding et al., 2023), 데이터 증강을 위한 추가 표본 확보 목적
- 인간 구조적/기능적 커넥톰 쌍 — Human Connectome Project (HCP) S1200 Release, 확산 MRI tractography 기반 SC와 안정상태(resting-state) fMRI 기반 FC, 승인 절차 없이 접근 가능

### 4.2 1단계 — 인간 FC→SC 베이스라인 디코더

HCP 데이터로 그래프 오토인코더(graph autoencoder) 구조의 FC→SC 디코더를 학습한다. 입력은 개인별 기능적 연결행렬, 출력은 예측된 구조적 연결행렬이며, 실제 tractography 기반 SC를 정답(ground truth)으로 지도학습한다. 이는 기존 문헌의 재현이자 이후 단계의 비교 기준이 된다.

### 4.3 2단계 — 무척추동물 위상학적 사전분포 학습

C. elegans와 초파리 구조적 커넥톰만으로는 표본 수가 절대적으로 부족하므로(원본 그래프 2개), 기존 저장소에 이미 구현된 널 모델 기법(degree-preserving rewiring, ER 널 모델)과 초파리 회로별 서브그래프 샘플링(버섯체, 시각엽, 중심복합체 등 상대적으로 독립적인 회로 단위)을 이용해 데이터를 증강한다. 이렇게 확보한 그래프 집합으로 그래프 생성모델(graph VAE)을 학습시켜, 모듈성·리치클럽 계수·클러스터링 계수·차수분포 등 생물학적으로 보존된 위상 통계량의 분포를 추출한다.

### 4.4 3단계 — 사전분포 결합 및 검증

2단계에서 얻은 위상 통계 분포와, 모델이 생성한 예측 SC의 위상 통계 간 거리를 정규화 손실 항으로 추가하여 1단계 모델을 재학습한다. 베이스라인(1단계) 대비 다음을 비교한다:

- 엣지 단위 예측 정확도(상관계수, MSE)
- 그래프 이론 지표의 실제 인간 SC와의 유사도(생물학적 타당성)
- 학습 데이터를 인위적으로 축소했을 때의 일반화 성능(저데이터 환경에서 사전분포의 효과가 더 클 것으로 예상)
- 기능적 타당성 검증 — 예측된 SC를 본 저장소의 `reservoir_experiment` 파이프라인에 그대로 입력하여, 실제 SC로 얻은 메모리 용량·NARMA-10 성능과 유사한 계산적 특성을 재현하는지 확인(기존 실험 자산의 재사용)

### 4.5 한계 인식 및 방법론적 주의

무척추동물 커넥톰의 노드(개별 뉴런)와 인간 거시 커넥톰의 노드(수백만 뉴런을 포함하는 뇌 영역)는 직접 대응되지 않는다. 따라서 본 연구는 노드 단위 가중치를 전이하지 않으며, 오직 그래프 전체 수준의 통계적·위상학적 성질만을 사전분포로 사용한다. 이 설계는 종간 노드 불일치 문제를 원천적으로 회피한다.

## 5. 기존 연구와의 연계성 및 독창성

본 제안은 제출자가 이미 수행한 두 실험의 방법론적 연장선에 있다. 리저버 컴퓨팅 실험은 "실제 배선이 무작위 배선보다 계산적으로 나은가"를, FlyHash 실험은 "실제 배선이 해싱 품질에 영향을 주는가"를 각각 검증했다. 본 제안은 동일한 "실제 생물학적 구조 vs. 통계적 기준선" 프레임을 인간 구조 복원이라는 임상적으로도 의미 있는 문제로 확장한 것이며, 기존에 구축한 커넥톰 로딩·널 모델·리저버 평가 코드를 그대로 재사용할 수 있어 실행 가능성이 높다.

독창성은 (1) 종간 보존된 위상 통계를 노드 대응 없이 그래프 수준 사전분포로만 사용한다는 설계와, (2) 예측된 인간 SC의 타당성을 계산 신경과학적 벤치마크(reservoir 태스크)로 교차 검증한다는 평가 방식에 있다.

## 6. 위험 요소 및 대응 방안

- 위험: 무척추동물 원본 그래프가 2개뿐이라 사전분포 학습이 불안정할 수 있음 → 대응: 널 모델 변형 및 회로별 서브그래프 샘플링으로 증강, 가능 시 유충 초파리·제브라피시 등 추가 공개 커넥톰 확보
- 위험: 종간 위상 통계가 실제로 인간 SC 복원에 유의미한 개선을 주지 않을 가능성(음성 결과) → 대응: 음성 결과 자체도 "종간 보존 원리의 한계"를 보여주는 유의미한 결과로 보고, 사전 정의된 ablation 비교로 정직하게 검증
- 위험: HCP 데이터 접근 및 전처리에 예상보다 시간이 소요될 가능성 → 대응: 이미 전처리된 공개 파생물(예: 선행 연구에서 사용한 998명 SC-FC 쌍) 우선 활용

## 7. 기대 효과 및 의의

- 기능적 뇌영상만 존재하고 구조적 영상이 없는 대규모 코호트(예: 일부 임상 데이터셋)에 대해 구조적 정보를 보완적으로 추정할 수 있는 방법론 제시
- 종간 보존된 배선 원리가 실제로 정량적 이점을 제공하는지에 대한 비교 커넥톰믹스 분야의 실증적 근거 추가
- 재현 가능한 오픈소스 파이프라인 공개 — C. elegans/초파리 구조적 커넥톰부터 인간 SC 복원까지 전 과정 포함
- 후속 연구로 특정 뇌질환(자폐, 수면장애 등) 코호트에서 기능 영상만으로 구조적 이상을 스크리닝하는 임상 응용으로 확장 가능

## 8. 추진 일정 (총 2주, 파일럿 스프린트)

인간 쪽 데이터는 HCP 실접속 대신 우선 합성(synthetic) SC-FC 코호트로 파이프라인을 검증하고, 실제 HCP 데이터 연동은 2주 종료 시점의 후속 과제로 명시적으로 분리한다 — `flyhash_experiment`가 neuPrint 토큰 유무와 무관하게 항상 끝까지 실행되도록 설계한 것과 동일한 원칙이다.

| 기간 | 내용 |
| --- | --- |
| 1일차 | 저장소 구조 설계: `sc_prior_experiment/` 모듈 스캐폴딩, 기존 `reservoir_experiment`·`flyhash_experiment` 코드 재사용 지점 확정 |
| 2-3일차 | `topology.py` 구현: 위상 통계량(모듈성, 리치클럽, 가중 클러스터링 계수, 차수분포) 계산 + 널 모델 증강 함수 |
| 4-5일차 | `invertebrate_prior.py` 구현: C. elegans·초파리 커넥톰 + 증강 표본으로 종간 위상 사전분포 추출 |
| 6-7일차 | `human_data.py` 구현: 인간 SC-FC 합성 코호트 생성기(HCP 실데이터 연동 지점은 인터페이스만 정의) |
| 8-9일차 | `decoder.py` 구현: 베이스라인 FC→SC 디코더(Ridge/MLP) + 사전분포 정규화 항을 결합한 prior-regularized 변형 |
| 10-11일차 | `run_experiment.py`로 baseline vs prior-regularized ablation 비교 실행, `reservoir_experiment` 파이프라인으로 예측 SC의 기능적 타당성 교차검증 |
| 12일차 | 결과 정리: `results/*.csv`, `*.png` 생성, README·ARCHITECTURE 문서화 |
| 13-14일차 | 예비 결과 해석, 한계점·후속 계획(HCP 실데이터 연동) 정리 및 제안서/발표자료 마무리 |

## 9. 참고문헌 및 데이터 출처

- Suárez, L.E. et al. Learning function from structure in neuromorphic networks. *Nature Machine Intelligence*.
- Sarwar, T. et al. (2021). Structure can predict function in the human brain. *Brain Structure and Function*.
- Zhang, L. et al. (2024). Predicting an individual's functional connectivity from their structural connectome. *Network Neuroscience*.
- Bullmore, E. & Sporns, O. (2012). The economy of brain network organization. *Nature Reviews Neuroscience*.
- Witvliet, D. et al. (2021). Connectomes across development reveal principles of brain maturation. *Nature*.
- Winding, M. et al. (2023). The connectome of an insect brain. *Science*.
- Scheffer, L.K. et al. (2020). A connectome and analysis of the adult Drosophila central brain. *eLife*.
- CoMuNeLab/C-elegans-Multiplex-Connectome dataset (`data_sources/celegans_multiplex`의 출처).
- Human Connectome Project (HCP) S1200 Release, ConnectomeDB.
