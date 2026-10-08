# 배경 논문 요약 모음

[READING_LIST.md](READING_LIST.md)에 있는 논문들(원래 BrainConnectom 전체 목록 중 이 프로젝트 관련 절)을 한 파일에서 훑어볼 수 있게 짧게 요약한 문서입니다. 논문마다 세 줄로 정리했습니다.

- **질문**: 이 논문이 풀려는 문제
- **핵심**: 방법과 주요 결과
- **여기서**: 이 저장소의 어느 부분에 어떻게 쓰이는지

> **읽기 전에**
> - 원문 번역이 아니라 **짧게 재구성한 요약**입니다. 원문을 대신할 수 없습니다.
> - 3.1b절(FC→SC 역방향)은 웹 검색으로 초록과 서지 정보를 확인하고 썼습니다. 나머지는 널리 알려진 내용을 기억으로 정리한 것입니다. 수치는 대부분 일부러 빼 두었습니다.
> - 논문을 실제로 읽은 뒤에는 요약 아래에 `> 메모:` 줄을 달아 자기 생각을 덧붙이는 식으로 쓰면 좋습니다.

**목차**: [0. 공통 기초](#0-공통-기초) · [3. SC 복원](#3-sc-복원) · [우선순위](#우선순위-제안)

---

## 0. 공통 기초

**Bullmore & Sporns (2009), Complex brain networks** — *Nat Rev Neurosci*
- 질문: 뇌를 그래프(노드·엣지)로 보면 무엇을 알 수 있는가?
- 핵심: 구조적·기능적 뇌 네트워크 모두에서 small-world, 허브, 모듈 구조가 나타난다는 것을 정리한 입문 리뷰입니다. 그래프 이론 지표로 뇌를 분석하는 표준 틀을 제시했습니다.
- 여기서: 저장소 전체의 개념적 출발점입니다.

**Rubinov & Sporns (2010), Complex network measures of brain connectivity** — *NeuroImage*
- 질문: 뇌 네트워크 지표를 어떻게 정의하고 해석해야 하는가?
- 핵심: 클러스터링, 경로 길이, 모듈성, 중심성 등의 정의와 가중/방향 그래프 버전을 정리했습니다. Brain Connectivity Toolbox(BCT)의 기반 논문입니다.
- 여기서: `sctransfer/topology.py`에 구현한 지표들이 표준 정의와 맞는지 확인할 때 봅니다.

**Maslov & Sneppen (2002), Specificity and stability in topology of protein networks** — *Science*
- 질문: 관측된 네트워크 패턴이 차수 분포만으로 설명되는가, 아니면 그 이상의 구조인가?
- 핵심: 각 노드의 차수는 유지한 채 엣지 쌍을 교환하는 재배선 널 모델을 제안했습니다. 이 모델과 비교해 "우연 이상의" 구조를 판별합니다.
- 여기서: `degree_null`의 원전입니다. 네 실험 모두의 "실제 vs 널 모델" 비교 방법론이 여기서 나옵니다.

**Chen, Hall & Chklovskii (2006), Wiring optimization can relate neuronal structure and function** — *PNAS*
- 질문: 뉴런의 위치는 배선 길이를 최소화하도록 배치되어 있는가?
- 핵심: C. elegans 뉴런 배치를 배선 비용 최소화 모델로 상당 부분 설명했습니다. 이 과정에서 정리한 연결 데이터가 이후 다층 커넥톰 데이터셋의 바탕이 됐습니다.
- 여기서: `data/celegans_multiplex`가 인용을 요구하는 논문입니다. "배선 경제성"을 C. elegans에서 보여준 근거이기도 합니다.

**De Domenico, Porter & Arenas (2015), MuxViz** — *J Complex Networks*
- 질문: 여러 종류의 연결(다층 네트워크)을 어떻게 분석하고 시각화할까?
- 핵심: 다층 네트워크 분석·시각화 도구를 소개했고, 예시로 C. elegans 다층 커넥톰(전기 시냅스, 화학 시냅스)을 사용했습니다.
- 여기서: 같은 데이터셋의 인용 요구 논문입니다. 전기 갭 정션 레이어를 쓰는 확장 실험을 할 때 참고합니다.

**White et al. (1986), The structure of the nervous system of C. elegans** — *Phil Trans R Soc B*
- 질문: 한 동물의 신경계 전체 배선도를 그릴 수 있는가?
- 핵심: 전자현미경 연속 절편으로 C. elegans 성체 신경계 302개 뉴런의 연결을 재구성했습니다. 최초의 전체 커넥톰입니다.
- 여기서: 모든 C. elegans 커넥톰 데이터의 원전입니다.

**Varshney et al. (2011), Structural properties of the C. elegans neuronal network** — *PLoS Comput Biol*
- 질문: White et al.의 데이터를 보완하면 C. elegans 네트워크는 어떤 위상 특성을 보이는가?
- 핵심: 배선도를 갱신하고 차수 분포, small-world 특성, 리치클럽 경향, 모티프 등을 분석했습니다.
- 여기서: `sctransfer/celegans.py`가 불러오는 279개 뉴런 네트워크의 위상 특성을 해석하는 기준입니다.

**Cook et al. (2019), Whole-animal connectomes of both C. elegans sexes** — *Nature*
- 질문: 뇌뿐 아니라 몸 전체, 그리고 수컷까지 포함한 커넥톰은 어떻게 생겼나?
- 핵심: 암수(자웅동체·수컷) 전체의 커넥톰을 시냅스 가중치와 함께 재구성했습니다.
- 여기서: 데이터를 교체하거나 증강할 때의 후보입니다. 성별 간 차이를 널 모델과 비교해 볼 수도 있습니다.

---

## 3. SC 복원

### 3.1 구조-기능 결합 (SC→FC 방향)

**Honey et al. (2009), Predicting human resting-state FC from SC** — *PNAS*
- 질문: 백질 구조 연결(SC)로 안정상태 기능 연결(FC)을 예측할 수 있는가?
- 핵심: SC 위에서 신경 동역학 모델을 돌려 FC를 시뮬레이션했더니, 실측 FC와 상당히 맞았습니다. 하지만 직접 구조 연결이 없는 영역 쌍에도 강한 FC가 흔했습니다. 그래서 **FC로 SC를 역추론하는 것은 SC→FC보다 불안정하다**고 지적했습니다.
- 여기서: `human_data.py`의 "SC 위에 동역학을 돌려 FC를 만든다" 설계의 원형입니다. 제안서가 다루는 역문제가 어려운 이유의 고전적 근거이기도 합니다.

**Suárez, Markello, Betzel & Misic (2020), Linking structure and function in macroscale brain networks** — *Trends Cogn Sci*
- 질문: 구조와 기능을 연결하는 모델들은 어떤 종류가 있나?
- 핵심: 통계적 모델, 통신(communication) 모델, 생물물리 모델 등으로 분류해 정리했습니다. 구조-기능 결합이 뇌 영역마다 다르다는 점을 강조한 리뷰입니다.
- 여기서: 제안서 3.1절의 배경 설명에 쓸 리뷰입니다.

**Sarwar et al. (2021), Structure-function coupling in the human connectome: a machine learning approach** — *NeuroImage*
- 질문: 딥러닝으로 개인의 SC에서 개인의 FC를 예측할 수 있는가?
- 핵심: 완전연결 신경망으로 SC→FC를 학습했습니다. 생물물리 모델보다 높은 예측 정확도를 보였고, 예측된 FC가 인지 수행의 개인차도 설명했습니다.
- 여기서: `decoder.py`의 MLP 계열 디코더가 반대 방향으로 참고할 구조입니다.

**Neudorf, Kress & Borowsky (2022), Structure can predict function in the human brain (GNN)** — *Brain Struct Funct*
- 질문: 그래프 신경망으로 SC에서 FC와 기능적 중심성을 예측할 수 있는가?
- 핵심: HCP 데이터로 GNN 모델을 학습해 평균 FC와 중심성의 분산을 높은 비율로 설명했습니다. 수치는 논문 버전마다 다르게 보고되니 출판본에서 확인하세요.
- 여기서: 제안서 "89%/99%" 인용의 출처입니다. 그래프 오토인코더를 설계할 때 참고합니다.

**Zalesky et al. (2024), Predicting an individual's FC from their structural connectome** — *Netw Neurosci*
- 질문: 개인 수준 SC→FC 예측은 실제로 얼마나 잘 되는가?
- 핵심: 약 1,000명의 데이터로 평가했습니다. 개인 효과 예측은 유의미하지만, 집단 평균 기준선 대비 개선은 약 8–11%로 크지 않았습니다. Riemann 기하, 교차검증 의존성, 표준화 등 평가 방법에 대한 권고도 담았습니다.
- 여기서: `run_pilot.py`의 평가를 설계할 때 반드시 참고해야 합니다. 특히 "집단 평균 SC를 그대로 내놓는 디코더"를 기준선에 추가해야 개선이 개인 신호 때문인지 알 수 있습니다.

**Rosenthal et al. (2018), Mapping higher-order relations between brain structure and function** — *Nat Commun*
- 질문: SC를 벡터 임베딩으로 표현하면 FC와의 관계가 더 잘 드러나는가?
- 핵심: 커넥톰 노드를 임베딩(node2vec 계열)으로 표현해, 직접 연결을 넘어서는 고차 구조-기능 관계를 포착했습니다.
- 여기서: 디코더 입력을 FC 행렬 대신 임베딩으로 바꾸는 확장 아이디어입니다.

**Fotiadis et al. (2024), Structure–function coupling in macroscale human brain networks** — *Nat Rev Neurosci*
- 질문: 구조-기능 결합 연구는 현재 어디까지 왔나?
- 핵심: 결합을 측정하는 방법, 발달·노화·질환에 따른 변화, 방법론적 쟁점을 정리한 최신 리뷰입니다.
- 여기서: 제안서 3.1절의 "최근 리뷰"로 인용하기에 적합합니다.

### 3.1b FC→SC 역방향

제안서가 실제로 다루는 방향입니다. 연구가 없지는 않지만 적고, 대부분 의료영상 분야의 GCN/GAN 연구입니다. 제안서의 독창성은 "FC→SC를 처음 한다"가 아니라 **"종간 보존 위상 통계를 prior로 쓴다"**에 두어야 합니다.

**⭐ Zhang, Wang & Zhu (2022), Predicting brain structural network using functional connectivity** — *Med Image Anal* 79 (학회 버전: MICCAI 2020)
- 질문: 개인의 FC로 그 사람의 SC를 생성할 수 있는가?
- 핵심: MGCN-GAN을 제안했습니다. 생성자는 여러 개의 다층 GCN으로 간접 연결을 모델링하고, 판별자는 GCN으로 진짜 SC와 예측 SC를 구분합니다. GAN의 불안정성을 줄이기 위해 **구조 보존(structure-preserving) 손실**을 추가했습니다. HCP와 ADNI 데이터에서 신뢰할 만한 개인 SC를 생성했다고 보고했으며, 코드가 공개되어 있습니다.
- 여기서: **가장 직접적인 선행 연구이자 반드시 비교해야 할 베이스라인**입니다. "구조 보존 손실"은 이 저장소의 "위상 통계 prior 정규화"와 발상이 비슷합니다. 그래서 "인간 SC 자체의 구조 vs 종간 보존 통계" 중 어느 쪽 prior가 나은지가 자연스러운 비교 실험이 됩니다.

**⭐ Li & Mateos (2019), Identifying structural brain networks from FC: a network deconvolution approach** — *ICASSP*
- 질문: fMRI 신호만으로 숨은 구조 네트워크를 역추정할 수 있는가?
- 핵심: 뇌 활동을 미지의 구조 네트워크 위의 선형 확산 과정이 만든 그래프 신호로 모델링했습니다. 그러면 FC(공분산)는 구조 인접행렬의 다항식 함수가 됩니다. 이를 이용해 FC의 고유벡터로 구조 네트워크의 고유벡터를 추정하고, 고유값은 희소성 정규화 볼록 최적화로 복원합니다.
- 여기서: 딥러닝 없이 역문제를 푸는 원리적 방법입니다. 희소성 대신 "모듈성·리치클럽 같은 위상 prior"를 정규화 항으로 넣는 변형이 곧 이 저장소의 아이디어입니다. 해석하기 쉬운 베이스라인으로 쓰기 좋습니다.

**Li, Mateos & Zhang (2022), Learning to model the relationship between brain structural and functional connectomes** — *IEEE TSIPN* 8
- 질문: SC와 FC의 관계를 그래프 신호처리 모델로 학습할 수 있는가?
- 핵심: 위 연구를 확장해 SC와 FC 사이의 매핑을 지도학습으로 학습하는 틀을 제안했습니다.
- 여기서: 선형 확산 가정을 학습 가능한 형태로 완화할 때 참고합니다.

**⭐ Liégeois et al. (2020), Revisiting correlation-based FC and its relationship with SC** — *Netw Neurosci* 4(4)
- 질문: 어떤 방식으로 FC를 정의해야 SC와 잘 맞는가?
- 핵심: 5분 이상의 fMRI 데이터가 있으면, 상관행렬보다 **정밀도 행렬(partial correlation) 기반 FC**가 SC와 더 잘 맞았습니다. 매개 영역의 영향을 걷어낸 "직접" 의존성을 반영하기 때문입니다.
- 여기서: 디코더 입력 FC를 상관행렬 대신 정밀도 행렬로 바꾸는 것만으로 성능이 오를 수 있습니다. `human_data.py`의 합성 FC와 HCP 연동 모두에서 비교해 볼 값싼 실험입니다.

**Chen, Bukhari, Lin & Sejnowski (2022), FC using differential covariance predicts SC** — *Netw Neurosci* 6(2)
- 질문: 상관이 아닌 다른 FC 추정법이 구조 연결을 더 잘 드러내는가?
- 핵심: 신호의 미분을 이용한 differential covariance(dCov)로 FC를 추정했습니다. HCP에서는 확산 MRI의 강한 피질 연결을, 마취된 마우스에서는 바이러스 추적 연결을 잘 식별했습니다.
- 여기서: Liégeois et al.과 같은 맥락에서, 입력 FC의 정의를 바꾸는 또 하나의 선택지입니다.

**Hinne et al. (2014), Structurally-informed Bayesian functional connectivity analysis** — *NeuroImage* 86
- 질문: SC를 prior로 쓰면 FC(정밀도 행렬) 추정이 좋아지는가?
- 핵심: 확산 MRI의 SC가 FC 모델의 희소성 구조를 결정하는 베이지안 모델을 제안했습니다. graphical lasso와 비교했고, 부분상관의 불확실성까지 정량화합니다.
- 여기서: 방향은 반대(SC→FC 추정 보조)이지만, **"구조 정보를 베이지안 prior로 넣는" 설계**가 이 저장소의 prior 정규화와 구조적으로 같습니다. 정규화 항을 확률적으로 정식화할 때 참고합니다.

**Smith et al. (2011), Network modelling methods for FMRI** — *NeuroImage* 54(2)
- 질문: 여러 FC 추정법 중 실제 직접 연결을 가장 잘 복원하는 것은?
- 핵심: 정답 네트워크를 아는 시뮬레이션 fMRI로 다양한 방법을 비교했습니다. 부분상관, 정규화된 역공분산, 베이즈넷 계열이 직접 연결 검출에 강했고, 방향성 추정은 대부분 어려웠습니다.
- 여기서: "FC만으로 구조를 어디까지 알 수 있나"의 고전적 벤치마크입니다. 합성 코호트 평가의 설계 모델로 쓸 수 있습니다.

**Wu, Yu & Chen (2025), Can FC be used to refine SC strength…** — *Neural Comput Appl* 37
- 질문: tractography가 만드는 SC 강도의 편향을 FC로 보정할 수 있는가?
- 핵심: 신경 계산 모델과 GAN을 결합해, 실측 FC와 맞도록 SC 강도를 보정했습니다.
- 여기서: FC로 SC를 "처음부터 생성"하지 않고 "기존 SC를 보정"하는 변형 과제입니다. 저데이터 실험의 대안 설정으로 쓸 수 있습니다.

**Zuo et al. (2023), Generative AI enables structural brain network construction from fMRI via symmetric diffusion learning** — arXiv:2309.16205 (프리프린트)
- 질문: 확산 생성모델로 fMRI에서 SC를 만들 수 있는가?
- 핵심: DDPM과 적대적 학습을 결합한 DiffGAN-F2S로, 대칭성을 가진 고품질 SC를 fMRI에서 생성했습니다.
- 여기서: 최신 생성모델 계열의 FC→SC 사례입니다. 동료 심사 전 논문이라는 점을 감안하세요.

**Tan et al. (2025), SFC-GAN** — arXiv:2501.07055 (프리프린트)
- 질문: SC↔FC를 양방향으로 변환할 수 있는가?
- 핵심: CycleGAN 구조에 합성곱 층을 넣어 SC와 FC 사이의 양방향 변환을 학습했습니다.
- 여기서: 순환 일관성(SC→FC→SC)을 추가 손실로 쓰는 아이디어입니다. `human_data.py`의 동역학 시뮬레이터를 FC 재생성기로 삼으면 비슷한 일관성 검증을 할 수 있습니다.

### 3.2 비교 커넥톰믹스와 보존된 배선 원리

**van den Heuvel, Bullmore & Sporns (2016), Comparative connectomics** — *Trends Cogn Sci*
- 질문: 여러 종의 커넥톰에서 공통 원리가 보이는가?
- 핵심: 선충부터 인간까지 여러 종의 커넥톰을 비교해, 모듈성, 허브·리치클럽, 배선 비용과 효율의 절충 같은 원리가 반복적으로 나타난다고 정리했습니다.
- 여기서: 제안서의 핵심 가정("종간 보존 위상 통계")을 떠받치는 가장 중요한 근거입니다.

**Bullmore & Sporns (2012), The economy of brain network organization** — *Nat Rev Neurosci*
- 질문: 뇌 네트워크 구조는 무엇의 절충으로 만들어졌나?
- 핵심: 배선 비용 최소화와 정보 전달 효율 극대화 사이의 경제적 절충이 뇌 조직을 결정한다고 주장했습니다. 질환에서 이 균형이 어떻게 깨지는지도 논의했습니다.
- 여기서: "배선 경제성"을 prior 통계에 넣을 근거입니다. 현재 `topology.py`에는 거리 정보가 없으니, 추가하려면 노드 좌표가 필요합니다.

**van den Heuvel & Sporns (2011), Rich-club organization of the human connectome** — *J Neurosci*
- 질문: 인간 커넥톰의 허브끼리는 서로 촘촘히 연결되어 있는가?
- 핵심: 인간 확산 MRI 커넥톰에서 고차수 허브끼리 우연 이상으로 조밀하게 연결된 리치클럽 구조를 확인했습니다.
- 여기서: `topology.py` 리치클럽 계수의 인간 쪽 기준입니다.

**Towlson et al. (2013), The rich club of the C. elegans neuronal connectome** — *J Neurosci*
- 질문: 선충 커넥톰에도 리치클럽이 있는가?
- 핵심: C. elegans에서도 리치클럽을 확인했고, 리치클럽 뉴런이 주로 운동 관련 명령 인터뉴런이라고 보고했습니다.
- 여기서: "같은 지표가 종을 넘어 나타난다"는 제안서 가정의 직접 근거입니다. `invertebrate_prior.py` 결과와 비교할 기준값입니다.

**Witvliet et al. (2021), Connectomes across development reveal principles of brain maturation** — *Nature*
- 질문: 발달하면서 커넥톰은 어떻게 변하나?
- 핵심: 유전적으로 동일한 선충 8마리를 발달 단계별로 재구성했습니다. 성숙할수록 뇌가 더 순방향(feedforward)이 되고 모듈성이 뚜렷해졌으며, 개체 간 변이도 관찰됐습니다.
- 여기서: 무척추동물 표본이 2개뿐인 문제를 완화할 **추가 실측 표본 8개**입니다. 널 모델 증강보다 생물학적으로 타당합니다.

**Winding et al. (2023), The connectome of an insect brain** — *Science*
- 질문: 곤충 뇌 전체의 시냅스 수준 배선도는?
- 핵심: 유충 초파리 뇌 전체를 전자현미경으로 재구성했습니다. 축삭·수상돌기를 구분해 네 가지 연결 유형의 다층 네트워크로 분석했고, 순환 구조와 허브 등을 보고했습니다.
- 여기서: 서브그래프 샘플링에 쓸 수 있는 또 하나의 완전한 커넥톰입니다.

### 3.3 그래프 생성모델 (사전분포 학습)

**Betzel et al. (2016), Generative models of the human connectome** — *NeuroImage*
- 질문: 단순한 연결 규칙으로 인간 커넥톰의 위상 통계를 재현할 수 있는가?
- 핵심: 거리 비용과 위상 규칙(이웃 공유 등)을 결합한 여러 생성 모델을 비교했습니다. 공간 제약과 이웃 공유(homophily) 규칙의 조합이 실제 커넥톰의 통계를 가장 잘 재현했습니다.
- 여기서: 제안서 4.3절 graph VAE의 해석 가능한 대안입니다. 소수의 파라미터만 있는 생성 모델을 종별로 맞추고 그 파라미터를 prior로 쓰면, 표본이 적은 문제에도 강합니다.

**Akarca et al. (2021), A generative network model of neurodevelopmental diversity in structural brain organization** — *Nat Commun*
- 질문: 생성 모델 파라미터로 개인차를 설명할 수 있는가?
- 핵심: 소아 코호트에서 개인별로 생성 모델 파라미터를 맞추고, 그 파라미터가 인지 능력 등 개인차와 관련됨을 보였습니다.
- 여기서: "생성 모델 파라미터 = 개인 또는 종의 특성 요약"이라는 관점을 제공합니다. 종간 prior와 개인 SC 사이의 거리를 정의할 때 참고합니다.

**Kipf & Welling (2016), Variational graph auto-encoders** — arXiv:1611.07308
- 질문: 그래프의 잠재 표현을 비지도로 학습할 수 있는가?
- 핵심: GCN 인코더와 내적 디코더로 구성된 VGAE를 제안하고 링크 예측에 적용했습니다.
- 여기서: 제안서 4.2절 "그래프 오토인코더" FC→SC 디코더의 기본 구조입니다.

**Simonovsky & Komodakis (2018), GraphVAE** — *ICANN*
- 질문: VAE로 작은 그래프 전체를 한 번에 생성할 수 있는가?
- 핵심: 그래프 전체를 확률적 완전 인접행렬로 한 번에 생성하는 VAE를 제안했습니다. 노드 순서 문제는 그래프 매칭으로 해결했습니다.
- 여기서: 제안서 4.3절 graph VAE의 원형입니다. 노드 수가 수백 개를 넘으면 쓰기 어렵고, 종마다 노드 수가 다릅니다. 그래서 그래프 자체보다 **위상 통계 벡터의 분포**를 학습하는 현재 구현 방향이 더 현실적입니다.

### 3.4 데이터

**Van Essen et al. (2013), The WU-Minn Human Connectome Project: an overview** — *NeuroImage*
- 질문: HCP는 어떤 데이터를 어떻게 수집하나?
- 핵심: 약 1,200명 성인의 확산 MRI, 안정상태 및 과제 fMRI, 행동 데이터를 수집·공개하는 HCP의 설계를 소개했습니다.
- 여기서: `load_hcp_cohort()`를 구현할 때 데이터 구성을 파악하는 출발점입니다.

---

## 우선순위 제안

1. **Zhang, Wang & Zhu (2022)**: 가장 직접적인 경쟁 연구입니다. 비교 베이스라인으로 삼을지 결정해야 합니다.
2. **Liégeois et al. (2020)**: 입력 FC의 정의를 바꾸는 것만으로 이득이 있을 수 있는 가장 값싼 실험입니다.
3. **Li & Mateos (2019)**: prior 정규화를 수식으로 정식화할 틀입니다.
4. **van den Heuvel et al. (2016)**과 **Towlson et al. (2013)**: 핵심 가정의 근거입니다.
5. **Zalesky et al. (2024)**: 평가 설계(집단 평균 기준선)에 반드시 반영해야 합니다.

