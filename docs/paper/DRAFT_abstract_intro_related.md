# 논문 초안 뼈대: Abstract · Introduction · Related Work

> **대상 논문**: `sc_prior_experiment` / [제안서](../proposal.md) — 종간 보존 위상 통계를 prior로 쓰는 FC→SC 복원
> **상태**: 아이디어 정리용 초안입니다. `[[ ]]` 안은 실험 결과가 나오면 채울 자리입니다.
> **참고**: 인용은 [READING_LIST.md](../papers/READING_LIST.md)에 정리한 논문 기준이고, 요약은 [SUMMARIES.md](../papers/SUMMARIES.md)에 있습니다.

논문 순서는 Abstract → Introduction → Related Work(→ Methods …)이지만, 정리는 **요청하신 순서(Abstract, Related Work, Introduction)**대로 했습니다. Introduction은 Related Work에서 정리한 "공백"을 가져다 쓰는 구조라, 이 순서로 읽는 편이 자연스럽습니다.

---

## 0. 먼저 정할 것: 논문의 한 문장

모든 섹션이 이 한 문장을 향해야 합니다.

> **한국어**: 기능적 연결성(FC)으로 구조적 연결성(SC)을 복원하는 불량조건 역문제에서, 무척추동물 커넥톰에서 추출한 종간 보존 위상 통계를 사전분포로 쓰면 복원의 정확도와 생물학적 타당성이 개선되는가, 그리고 그 개선은 "그럴듯한 아무 정규화"가 아니라 생물학 때문인가?
>
> **English**: Can graph-level topological statistics conserved across species, estimated from invertebrate connectomes, serve as a biologically grounded prior that regularizes the ill-posed inference of human structural connectivity from functional connectivity—and is any gain attributable to biology rather than to regularization per se?

**핵심 주장 후보** (결과에 따라 고르기):
- **(A) 양성 결과**: 종간 prior가 복원을 개선하고, 널 prior로는 같은 효과가 나지 않는다.
- **(B) 조건부 결과**: 저데이터 환경에서만 개선된다. 제안서의 예상과 같습니다.
- **(C) 음성 결과**: 개선되지 않는다. 이 경우 "종간 보존 원리가 거시 규모 인간 SC 복원에 정량적으로 전이되는 데에는 한계가 있다"는 결과로 씁니다.

설계상 (C)도 논문이 되도록 되어 있습니다. 널 prior 대조군과 사전 정의된 ablation이 있기 때문입니다. 이 점을 Introduction에서 미리 강조해 두면 어느 결과가 나와도 이야기가 무너지지 않습니다.

---

## 1. Abstract

### 구조 (약 200–250 단어, 6문장)

| # | 역할 | 들어갈 내용 |
| --- | --- | --- |
| 1 | 배경 | SC와 FC는 긴밀히 연관되고, SC→FC 예측은 크게 발전했다 |
| 2 | 문제 | 역방향 FC→SC는 불량조건이다. 여러 SC가 비슷한 FC를 만들기 때문에 추가 사전지식이 필요하다 |
| 3 | 아이디어 | 비교 커넥톰믹스의 종간 보존 위상 원리를 노드 대응 없이 그래프 수준 prior로 쓴다 |
| 4 | 방법 | C. elegans·초파리 커넥톰 + 증강 → 위상 통계 분포, FC→SC 디코더에 정규화로 결합, 널 prior 대조군 |
| 5 | 결과 | `[[ ]]` 엣지 정확도, 위상 거리, 저데이터 성능, 리저버 기반 기능적 타당성 |
| 6 | 의의 | 종간 보존 원리의 정량적 효용 또는 한계, 오픈소스 파이프라인 |

### 초안 (English)

> The structural connectome (SC) constrains the functional connectome (FC), and predicting FC from SC has advanced considerably with machine learning. The inverse problem—inferring SC from FC—remains comparatively underexplored and is fundamentally ill-posed, as many distinct wiring diagrams can give rise to similar patterns of functional coupling. Resolving it requires prior knowledge about what biologically plausible wiring looks like. Comparative connectomics has repeatedly reported that topological properties such as modularity, rich-club organization and wiring economy recur across nervous systems that differ in size by orders of magnitude. Here we ask whether these conserved properties can serve as a biologically grounded prior for FC-to-SC inference. We estimate a distribution over graph-level topological statistics from invertebrate connectomes (*C. elegans* and *Drosophila*), augmented by subgraph sampling, and use it to regularize a supervised FC-to-SC decoder. Because the prior acts only on graph-level statistics, it sidesteps the absence of node correspondence between single-neuron invertebrate connectomes and regional human connectomes. To separate the effect of biology from that of regularization per se, we compare against a matched null prior derived from randomized versions of the same connectomes. `[[Across N subjects, the biological prior improved/did not improve edge-level accuracy (r = …) and reduced topological discrepancy by …%, with the largest gains when training data were limited.]]` We further assess functional plausibility by using the predicted SCs as reservoirs in standard reservoir-computing benchmarks. `[[Results suggest that …]]` We release an open-source pipeline spanning invertebrate connectomes to human SC inference.

### 초안 (한국어, 내용 확인용)

> 구조적 커넥톰(SC)은 기능적 커넥톰(FC)을 제약하며, SC로 FC를 예측하는 연구는 머신러닝으로 크게 발전했다. 반면 FC로 SC를 추론하는 역문제는 상대적으로 덜 연구되었고 근본적으로 불량조건이다. 서로 다른 여러 배선이 비슷한 기능적 결합 패턴을 만들 수 있기 때문이다. 이를 풀려면 생물학적으로 그럴듯한 배선에 대한 사전지식이 필요하다. 비교 커넥톰믹스는 규모가 수 자릿수 다른 신경계에서도 모듈성, 리치클럽, 배선 경제성 같은 위상 특성이 반복된다고 보고해 왔다. 본 연구는 이 보존된 특성을 FC→SC 추론의 사전분포로 쓸 수 있는지 묻는다. C. elegans와 초파리 커넥톰(및 서브그래프 표본)에서 그래프 수준 위상 통계의 분포를 추정하고, 이를 지도학습 FC→SC 디코더의 정규화에 사용한다. prior가 그래프 수준 통계에만 작용하므로, 단일 뉴런 해상도의 무척추동물 커넥톰과 영역 단위 인간 커넥톰 사이에 노드 대응이 없다는 문제를 피한다. 생물학의 효과와 정규화 자체의 효과를 분리하기 위해, 같은 커넥톰을 무작위화해서 만든 널 prior와 비교한다. `[[결과]]` 또한 예측 SC를 리저버로 사용해 기능적 타당성을 평가한다. `[[결과]]`

### 쓸 때 주의점
- **"최초"라는 표현은 쓰지 않습니다.** FC→SC 자체는 Zhang, Wang & Zhu (2022), Li & Mateos (2019) 등 선행 연구가 있습니다. 새로운 점은 **"종간 prior"**와 **"널 prior 대조군"**입니다.
- **결과 문장은 실제 HCP 결과가 나온 뒤에 씁니다.** 지금 저장소의 결과는 합성 코호트 기준이라 Abstract에 넣을 수 없습니다.

---

## 2. Related Work

네 개 소절로 나눕니다. 각 소절은 **"무엇이 알려져 있나 → 무엇이 빠져 있나 → 우리가 어떻게 채우나"**로 끝나야 합니다.

### 2.1 Structure–function coupling: SC → FC

- **흐름**: 생물물리 모델(Honey et al., 2009) → 통계·통신 모델 정리(Suárez et al., 2020) → 딥러닝(Sarwar et al., 2021; Neudorf et al., 2022) → 개인 수준 예측의 한계 평가(Zalesky et al., 2024) → 최신 리뷰(Fotiadis et al., 2024)
- **핵심 포인트**:
  - 집단 수준에서는 SC가 FC를 잘 예측합니다.
  - 개인 수준 예측은 집단 평균 기준선 대비 개선이 작습니다(Zalesky et al., 2024).
  - 직접 구조 연결이 없는 영역 쌍에도 강한 FC가 흔해서, 역추론이 어렵습니다(Honey et al., 2009).
- **이 소절의 마무리 문장**: "정방향조차 개인 수준에서는 어렵고, 역방향은 여기에 불량조건성까지 더해진다."

### 2.2 Inferring SC from FC

- **세 계열로 분류**:
  1. **FC 추정법 개선**: 직접 의존성을 잡는 FC를 쓰는 방향입니다. 정밀도 행렬/부분상관(Smith et al., 2011; Liégeois et al., 2020), differential covariance(Chen et al., 2022).
  2. **모델 기반 역문제**: 확산 모델을 가정하고 희소성으로 정규화하는 network deconvolution(Li & Mateos, 2019; Li, Mateos & Zhang, 2022).
  3. **딥 생성 모델**: GCN-GAN(Zhang, Wang & Zhu, 2020/2022), 확산 모델(Zuo et al., 2023), CycleGAN(Tan et al., 2025), SC 강도 보정(Wu et al., 2025).
- **공통점과 빈틈**: 세 계열 모두 prior나 정규화를 **(i) 일반적 가정(희소성)**에서 가져오거나 **(ii) 인간 SC 데이터 자체**에서 학습합니다. 예를 들어 Zhang et al.의 구조 보존 손실이 (ii)에 해당합니다. **다른 종의 커넥톰에서 온 독립적인 생물학적 사전지식**을 쓴 연구는 찾지 못했습니다.
- **주의**: 이 "찾지 못했다"는 문헌 검색 범위를 적어 두고 조심스럽게 표현하세요. 투고 전에 한 번 더 검색해야 합니다.
- **이 소절의 마무리 문장**: "기존 정규화는 희소성 같은 일반 가정이나 인간 데이터 자체에서 오며, 인간 데이터와 독립적인 생물학적 prior는 쓰이지 않았다."

### 2.3 Comparative connectomics and conserved wiring principles

- **흐름**: 네트워크 신경과학의 기초(Bullmore & Sporns, 2009) → 배선 경제성(Bullmore & Sporns, 2012) → 인간 리치클럽(van den Heuvel & Sporns, 2011)과 C. elegans 리치클럽(Towlson et al., 2013) → 종간 비교 리뷰(van den Heuvel, Bullmore & Sporns, 2016)
- **데이터**: C. elegans(White et al., 1986; Varshney et al., 2011; Cook et al., 2019; Witvliet et al., 2021), 초파리(Scheffer et al., 2020; Winding et al., 2023; Dorkenwald et al., 2024)
- **빈틈**: 보존 원리는 주로 **기술적(descriptive)**으로 보고되었습니다. 이 원리가 다른 종의 추론 문제에 **정량적 이점**을 주는지는 검증된 적이 없습니다.
- **이 소절의 마무리 문장**: "보존된다는 관찰은 많지만, 그것이 '쓸모 있는' 사전지식인지는 검증되지 않았다."

### 2.4 Generative models and priors over graphs

- **흐름**: 공간·위상 규칙 기반 생성 모델(Betzel et al., 2016; Akarca et al., 2021) → 그래프 VAE(Kipf & Welling, 2016; Simonovsky & Komodakis, 2018) → 베이지안 구조 prior(Hinne et al., 2014, 방향은 반대지만 prior 설계가 같음)
- **우리 선택의 근거**: 노드 수와 노드 의미가 종마다 다르므로, 그래프 자체보다 **그래프 수준 통계 벡터의 분포**를 prior로 쓴다는 설계를 여기서 정당화합니다.

### (선택) 2.5 Connectomes as computational substrates

- **흐름**: 커넥톰 리저버(Suárez et al., 2021, 2024; Damicelli et al., 2022), 커넥톰 제약 모델(Lappalainen et al., 2024; Shiu et al., 2024)
- **용도**: 리저버 기반 기능적 타당성 평가를 논문에 포함할 경우에만 넣습니다. 이 평가를 부록으로 빼면 이 소절도 짧게 줄이거나 생략합니다.

### 관련 연구 대비 위치 (표로 넣으면 좋음)

| 연구 | 방향 | prior / 정규화의 출처 | 노드 대응 필요 | 널 대조군 |
| --- | --- | --- | --- | --- |
| Li & Mateos (2019) | FC→SC | 일반 가정 (희소성) | – | ✗ |
| Zhang, Wang & Zhu (2022) | FC→SC | 인간 SC (구조 보존 손실) | 같은 종 | ✗ |
| Hinne et al. (2014) | SC→FC 추정 | 개인 SC | 같은 개인 | ✗ |
| Liégeois et al. (2020) | FC 정의 | – | – | – |
| **본 연구** | FC→SC | **무척추동물 커넥톰 (종간)** | **불필요 (그래프 수준)** | **✓ (ER 널 prior)** |

---

## 3. Introduction

5개 문단, **깔때기 구조**(넓은 배경 → 좁은 문제 → 우리 기여)로 씁니다.

**¶1. 왜 SC와 FC의 관계가 중요한가**
- 구조는 기능의 물리적 제약이고, 기능은 구조 위 동역학의 결과입니다.
- SC→FC 예측은 크게 발전했습니다. 집단 수준에서 GNN이 FC 분산의 대부분을 설명합니다(Neudorf et al., 2022).
- 하지만 개인 수준 예측의 이득은 제한적입니다(Zalesky et al., 2024).

**¶2. 역방향 문제와 그 필요성**
- **응용 동기**: fMRI만 있고 확산 MRI가 없거나 품질이 낮은 코호트가 많습니다. 이런 데이터에서 구조를 보완 추정할 수 있다면 쓸모가 큽니다.
- **어려움**: 불량조건입니다. 직접 연결이 없어도 강한 FC가 나타나기 때문입니다(Honey et al., 2009).
- **따라서**: "그럴듯한 배선"에 대한 사전지식이 필요합니다.

**¶3. 기존 접근의 한계**
- 기존 FC→SC 방법의 prior는 희소성 같은 일반 가정(Li & Mateos, 2019)이거나, 인간 데이터 자체에서 학습됩니다(Zhang et al., 2022).
- **전자**는 뇌에 특화되지 않았습니다.
- **후자**는 학습 데이터가 적을 때 prior도 같이 약해지고, 인간 데이터의 편향(예: tractography 편향)을 그대로 물려받습니다.
- 인간 데이터와 **독립적인** 생물학적 사전지식의 출처가 필요합니다.

**¶4. 우리 아이디어**
- 비교 커넥톰믹스는 규모가 전혀 다른 종에서도 모듈성, 리치클럽, 배선 경제성이 반복됨을 보였습니다(van den Heuvel et al., 2016; Towlson et al., 2013).
- 이를 **인간 데이터와 독립적인 prior**로 씁니다.
- **핵심 설계**: 노드 단위 정보는 전이하지 않고 그래프 수준 통계만 씁니다. 그래서 종간 노드 대응 문제가 원천적으로 없습니다.
- **핵심 통제**: 같은 그래프를 무작위화한 널 prior와 비교해, "정규화 자체의 효과"와 "생물학의 효과"를 분리합니다.

**¶5. 기여 (글머리표로)**
1. 무척추동물 커넥톰에서 인간 SC 복원용 그래프 수준 위상 prior를 추출하는 방법 (노드 대응 불필요)
2. 생물학적 prior와 널 prior를 비교하는 ablation 설계. 이득의 출처를 검증 가능하게 만듭니다.
3. 엣지 정확도, 위상 거리, 저데이터 일반화에 더해 **리저버 컴퓨팅 기반 기능적 타당성**까지 보는 다면 평가
4. `[[주요 결과 한 줄]]`
5. 무척추동물 커넥톰부터 인간 SC 추론까지 전 과정을 담은 오픈소스 파이프라인

---

## 4. 논문 쓰기 전에 메워야 할 간극 (정직하게)

현재 코드와 위 초안이 주장하는 내용 사이에 차이가 있습니다. 투고 전에 코드를 초안에 맞추거나, 초안을 코드에 맞춰 낮춰야 합니다.

| 초안의 주장 | 현재 구현 (`sc_prior_experiment/`) | 해야 할 일 |
| --- | --- | --- |
| 모듈성·리치클럽·클러스터링 등 **다변량** prior | `decoder.py`는 **노드 강도 CV(허브 불균등도) 하나만** 사용 | 다변량 prior로 확장하거나, 논문을 "허브 구조 prior"로 좁히기 |
| prior를 **손실 항**으로 결합해 학습 | Ridge 예측 **이후 후처리 reshape** (`alpha_blend`) | 학습 중 정규화로 바꾸거나, "post-hoc projection"으로 정직하게 서술 |
| ~~초파리 **실측** 커넥톰~~ ✅ | hemibrain v1.2 회로 5개(버섯체·중심복합체·측각·더듬이엽·외측 복합체)의 실측 연결을 사용 (`data_sources/hemibrain/`) | 완료. 논문 Methods에 회로 정의(ROI 목록), 시냅스 3개 이상 기준, 300-뉴런 서브그래프 샘플링을 명시 |
| 인간 HCP 데이터 | 합성 코호트 (`human_data.py`) | `load_hcp_cohort()` 구현 |
| 그래프 VAE로 분포 학습 (제안서) | 통계의 평균과 표준편차만 집계 | 논문에서는 "경험적 분포"로 서술하거나 VAE 구현 |
| 개인 수준 개선 | 기준선이 Ridge 하나뿐 | **집단 평균 SC 기준선**(Zalesky 권고)과 **MGCN-GAN 비교** 추가 |
| 배선 경제성 | 거리 정보 없음 | 노드 좌표를 쓰는 통계를 추가하거나, 주장에서 빼기 |
| 저데이터 일반화 | 실험 없음 | 학습 표본 수를 바꿔 가며 곡선 그리기 |

**우선순위 추천**: ~~(1) 초파리 실측 데이터~~ ✅ → (2) HCP 연동 → (3) 집단 평균 기준선 → (4) 다변량 prior → (5) 저데이터 곡선. 이 다섯 개가 끝나야 Abstract의 `[[ ]]`를 채울 수 있습니다.

---

## 5. 열린 결정 사항

- **투고처**: 신경과학 저널(*Network Neuroscience*, *NeuroImage*)이냐 ML 학회 워크숍(NeurIPS/ICLR의 뇌·생물 워크숍)이냐에 따라 Related Work의 비중이 달라집니다. 저널이면 2.1·2.3을, ML이면 2.2·2.4를 두껍게 씁니다.
- **리저버 평가의 위치**: 본문에 넣으면 독창성 포인트가 되지만 심사자에게 "왜 리저버인가"를 설득해야 합니다. 부록이 더 안전할 수 있습니다.
- **다른 세 실험(리저버, FlyHash, 로봇)의 위치**: 이 논문에서는 "선행 방법론(실제 vs 널 비교)의 출처"로 한 문단만 언급하는 것을 추천합니다. 네 실험을 한 논문에 다 담으면 초점이 흐려집니다.
