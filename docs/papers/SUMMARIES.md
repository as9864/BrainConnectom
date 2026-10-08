# 배경 논문 요약 모음

[READING_LIST.md](READING_LIST.md)에 있는 논문들을 한 파일에서 훑어볼 수 있게 짧게 요약한 문서입니다. 논문마다 세 줄로 정리했습니다.

- **질문**: 이 논문이 풀려는 문제
- **핵심**: 방법과 주요 결과
- **여기서**: 이 저장소의 어느 부분에 어떻게 쓰이는지

> **읽기 전에**
> - 원문 번역이 아니라 **짧게 재구성한 요약**입니다. 원문을 대신할 수 없습니다.
> - 3.1b절(FC→SC 역방향)은 웹 검색으로 초록과 서지 정보를 확인하고 썼습니다. 나머지는 널리 알려진 내용을 기억으로 정리한 것입니다. 수치는 대부분 일부러 빼 두었습니다.
> - 논문을 실제로 읽은 뒤에는 요약 아래에 `> 메모:` 줄을 달아 자기 생각을 덧붙이는 식으로 쓰면 좋습니다.

**목차**: [0. 공통 기초](#0-공통-기초) · [1. 리저버 컴퓨팅](#1-리저버-컴퓨팅) · [2. FlyHash](#2-flyhash) · [3. SC 복원](#3-sc-복원) · [4. 로봇·후각 추적](#4-로봇후각-추적) · [한눈에 보는 연결 관계](#한눈에-보는-연결-관계)

---

## 0. 공통 기초

**Bullmore & Sporns (2009), Complex brain networks** — *Nat Rev Neurosci*
- 질문: 뇌를 그래프(노드·엣지)로 보면 무엇을 알 수 있는가?
- 핵심: 구조적·기능적 뇌 네트워크 모두에서 small-world, 허브, 모듈 구조가 나타난다는 것을 정리한 입문 리뷰입니다. 그래프 이론 지표로 뇌를 분석하는 표준 틀을 제시했습니다.
- 여기서: 저장소 전체의 개념적 출발점입니다.

**Rubinov & Sporns (2010), Complex network measures of brain connectivity** — *NeuroImage*
- 질문: 뇌 네트워크 지표를 어떻게 정의하고 해석해야 하는가?
- 핵심: 클러스터링, 경로 길이, 모듈성, 중심성 등의 정의와 가중/방향 그래프 버전을 정리했습니다. Brain Connectivity Toolbox(BCT)의 기반 논문입니다.
- 여기서: StructuralConnectomeTransfer의 `sctransfer/topology.py`에 구현한 지표들이 표준 정의와 맞는지 확인할 때 봅니다.

**Maslov & Sneppen (2002), Specificity and stability in topology of protein networks** — *Science*
- 질문: 관측된 네트워크 패턴이 차수 분포만으로 설명되는가, 아니면 그 이상의 구조인가?
- 핵심: 각 노드의 차수는 유지한 채 엣지 쌍을 교환하는 재배선 널 모델을 제안했습니다. 이 모델과 비교해 "우연 이상의" 구조를 판별합니다.
- 여기서: `degree_null`의 원전입니다. 네 실험 모두의 "실제 vs 널 모델" 비교 방법론이 여기서 나옵니다.

**Chen, Hall & Chklovskii (2006), Wiring optimization can relate neuronal structure and function** — *PNAS*
- 질문: 뉴런의 위치는 배선 길이를 최소화하도록 배치되어 있는가?
- 핵심: C. elegans 뉴런 배치를 배선 비용 최소화 모델로 상당 부분 설명했습니다. 이 과정에서 정리한 연결 데이터가 이후 다층 커넥톰 데이터셋의 바탕이 됐습니다.
- 여기서: `data_sources/celegans_multiplex`가 인용을 요구하는 논문입니다. "배선 경제성"을 C. elegans에서 보여준 근거이기도 합니다.

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
- 여기서: `reservoir_experiment`에서 쓰는 279개 뉴런 네트워크의 위상 특성을 해석하는 기준입니다.

**Cook et al. (2019), Whole-animal connectomes of both C. elegans sexes** — *Nature*
- 질문: 뇌뿐 아니라 몸 전체, 그리고 수컷까지 포함한 커넥톰은 어떻게 생겼나?
- 핵심: 암수(자웅동체·수컷) 전체의 커넥톰을 시냅스 가중치와 함께 재구성했습니다.
- 여기서: 데이터를 교체하거나 증강할 때의 후보입니다. 성별 간 차이를 널 모델과 비교해 볼 수도 있습니다.

---

## 1. 리저버 컴퓨팅

**Suárez et al. (2024), conn2res** — *Nat Commun*
- 질문: 실제 커넥톰을 리저버로 쓰는 실험을 표준화할 수 있는가?
- 핵심: 커넥톰을 불러와 리저버로 만들고, 과제를 주고, readout을 학습·평가하는 과정을 모듈화한 툴박스입니다. 다양한 커넥톰과 과제로 예시 분석을 보여줍니다.
- 여기서: `reservoir_experiment`가 재구현한 원 도구입니다. 의존성 문제로 직접 쓰지 못한 이유는 README에 있습니다.

**Suárez et al. (2021), Learning function from structure in neuromorphic networks** — *Nat Mach Intell*
- 질문: 인간 커넥톰의 배선 구조가 계산 능력(기억 등)에 영향을 주는가?
- 핵심: 인간 커넥톰을 리저버로 쓰고 널 모델과 비교했습니다. 동역학이 임계점 근처일 때 실제 배선의 이점이 드러나고, 기능 네트워크(intrinsic networks) 단위의 조직이 성능과 관련된다고 보고했습니다.
- 여기서: `reservoir_experiment`의 질문(실제 vs 널 모델)과 가장 가깝습니다. 스펙트럴 반지름을 바꿔 가며 비교하는 설계는 이 논문에서 가져왔습니다.

**Damicelli, Hilgetag & Goulas (2022), Brain connectivity meets reservoir computing** — *PLoS Comput Biol*
- 질문: 여러 종의 커넥톰 리저버는 무작위 리저버보다 나은가?
- 핵심: 여러 종의 커넥톰을 리저버로 써서 다양한 과제에서 널 모델과 비교했습니다. 이점은 과제와 조건에 따라 다르게 나타났습니다.
- 여기서: "실제 배선이 항상 낫지는 않다"는 결과를 해석할 때 비교할 대상입니다.

**Goulas, Damicelli & Hilgetag (2021), Bio-instantiated recurrent neural networks** — *Neural Networks*
- 질문: 커넥톰을 RNN의 연결 구조로 그대로 쓰면 어떤 이점이 있나?
- 핵심: 실제 커넥톰의 위상을 RNN 가중치 구조로 옮겨(bio-instantiation) 학습 성능과 효율을 비교했습니다. 이 방식을 쉽게 해 주는 도구(bio2art)도 함께 소개했습니다.
- 여기서: 리저버(고정 가중치)와 달리 가중치를 학습시키는 방향으로 확장할 때 참고합니다.

**Jaeger (2001), The "echo state" approach…** — GMD Report 148
- 질문: 순환망의 내부 가중치는 고정하고 출력층만 학습해도 되는가?
- 핵심: 에코 스테이트 네트워크(ESN)를 제안했습니다. 조건(echo state property)을 만족하는 무작위 순환망에 선형 readout만 학습합니다.
- 여기서: `reservoir.py`의 `LeakyESN`과 `robot_experiment/policy.py`의 기본 구조입니다.

**Jaeger (2001), Short term memory in echo state networks** — GMD Report 152
- 질문: 리저버는 과거 입력을 얼마나 오래 기억하는가?
- 핵심: 메모리 용량(MC)을 "k스텝 전 입력을 선형 readout으로 복원한 정확도(결정계수)를 k에 대해 합한 값"으로 정의했습니다. 뉴런 수가 그 상한입니다.
- 여기서: `tasks.py` 메모리 용량 벤치마크의 원전입니다.

**Atiya & Parlos (2000), New results on recurrent network training** — *IEEE Trans Neural Netw*
- 질문: 순환망 학습 알고리즘을 비교하려면 어떤 비선형 시계열 과제를 쓸까?
- 핵심: NARMA 계열 과제를 벤치마크로 사용했습니다. 이후 NARMA-10이 리저버 컴퓨팅의 표준 과제가 됐습니다.
- 여기서: `tasks.py` NARMA-10의 출처입니다.

**Lukoševičius & Jaeger (2009), Reservoir computing approaches to RNN training** — *Computer Science Review*
- 질문: ESN, LSM 등 리저버 계열 방법을 어떻게 정리할 수 있나?
- 핵심: 리저버 생성 방법, readout 학습, 스펙트럴 반지름이나 leak rate 같은 하이퍼파라미터 선택 요령을 종합한 리뷰입니다.
- 여기서: 리저버 하이퍼파라미터를 조정할 때 참고합니다.

**Lappalainen et al. (2024), Connectome-constrained networks predict neural activity across the fly visual system** — *Nature*
- 질문: 커넥톰과 과제 목표만으로 개별 뉴런의 반응을 예측할 수 있는가?
- 핵심: 초파리 시각계 커넥톰으로 구조를 고정하고, 운동 감지 과제로 미지의 파라미터만 학습했습니다. 그 결과 실측 뉴런 반응을 상당히 잘 예측했습니다.
- 여기서: "커넥톰은 제약, 학습은 나머지"라는 발상의 가장 강력한 사례입니다. `drone_nav.py`의 T4/T5 운동 감지 직관과도 이어집니다.

---

## 2. FlyHash

**Dasgupta, Stevens & Navlakha (2017), A neural algorithm for a fundamental computing problem** — *Science*
- 질문: 초파리 후각 회로는 어떤 계산을 하는가?
- 핵심: PN→KC의 희소 무작위 확장 투영과 winner-take-all 희소화가 지역 민감 해싱(LSH)처럼 작동한다고 해석했습니다. 이 방식(FlyHash)이 고전 LSH보다 유사도 검색에서 나은 경우가 있음을 보였습니다.
- 여기서: `flyhash.py`, `idealized_connectivity()`의 원전입니다.

**Caron, Ruta, Abbott & Axel (2013), Random convergence of olfactory inputs in the Drosophila mushroom body** — *Nature*
- 질문: KC는 어떤 PN(사구체)에서 입력을 받는가? 정해진 규칙이 있는가?
- 핵심: 개별 KC가 받는 사구체 입력을 추적한 결과, 뚜렷한 구조가 보이지 않고 무작위에 가깝다고 보고했습니다.
- 여기서: FlyHash의 "균등 무작위 연결" 가정을 뒷받침하는 실험적 근거입니다.

**Zheng et al. (2022), Structured sampling of olfactory input by the fly mushroom body** — *Curr Biol*
- 질문: 전자현미경 커넥톰으로 보면 PN→KC 연결은 정말 무작위인가?
- 핵심: 대규모 EM 데이터로 분석하니 PN 입력 샘플링이 완전 무작위가 아니었습니다. 일부 사구체(특히 먹이 관련 냄새)가 과대 표집되는 등 구조가 있다고 보고했습니다.
- 여기서: Caron et al.과 대립하는 결과로, `flyhash_biased_synthetic`과 `flyhash_real_hemibrain`을 설계한 동기입니다. README의 "미해결 질문"에 가장 직접 닿아 있습니다.

**Litwin-Kumar, Harris, Axel, Sompolinsky & Abbott (2017), Optimal degrees of synaptic connectivity** — *Neuron*
- 질문: KC 하나가 몇 개의 입력을 받는 것이 최적인가?
- 핵심: 확장 층의 표현 차원(분리 능력)을 최대화하는 입력 수를 이론적으로 계산했습니다. 결과가 실측값(약 6개)과 비슷하게 나왔고, 소뇌 과립세포에도 같은 논리를 적용했습니다.
- 여기서: `biased_synthetic`에서 KC 차수 분포를 정할 때의 이론적 기준입니다.

**Li et al. (2020), The connectome of the adult Drosophila mushroom body** — *eLife*
- 질문: hemibrain으로 본 버섯체 회로 전체는 어떻게 생겼나?
- 핵심: KC, MBON, DAN 등 버섯체 세포 유형과 연결을 상세히 분석했습니다. KC 사이의 연결 등 예상 밖의 회로 요소도 보고했습니다.
- 여기서: `flyhash_real_hemibrain`의 PN→KC 데이터를 해석할 때 참고합니다.

**Scheffer et al. (2020), A connectome and analysis of the adult Drosophila central brain** — *eLife*
- 질문: 성체 초파리 중심 뇌의 커넥톰을 만들 수 있는가?
- 핵심: 약 2만 5천 개 뉴런, 약 2천만 개 연결의 hemibrain 커넥톰을 공개했습니다. 세포 유형 정의와 neuPrint 공개 도구도 함께 나왔습니다.
- 여기서: neuPrint 연동과 StructuralConnectomeTransfer의 초파리 회로 서브그래프 데이터 소스입니다.

**Dorkenwald et al. (2024), Neuronal wiring diagram of an adult brain** — *Nature*
- 질문: 초파리 성체 뇌 전체(양반구)의 커넥톰은?
- 핵심: FlyWire 협업 교정으로 성체 초파리 전뇌 커넥톰을 완성했습니다. hemibrain보다 범위가 넓습니다.
- 여기서: hemibrain의 대안입니다. 좌우 버섯체를 비교하면 개체 내 변이와 널 모델을 비교해 볼 수 있습니다.

**Eichler et al. (2017), The complete connectome of a learning and memory centre in an insect brain** — *Nature*
- 질문: 유충 초파리 버섯체의 완전한 배선은?
- 핵심: 유충 버섯체 전체 커넥톰을 재구성했습니다. 다양한 연결 모티프와 KC 사이의 연결 등을 보고했습니다.
- 여기서: 성체와 비교할 수 있는 또 하나의 PN→KC 표본입니다.

**Charikar (2002), Similarity estimation techniques from rounding algorithms** — *STOC*
- 질문: 코사인 유사도를 보존하는 해시를 만들 수 있는가?
- 핵심: 무작위 초평면의 부호로 비트를 만드는 SimHash를 제안했습니다. 충돌 확률이 두 벡터 사이 각도와 직결됩니다.
- 여기서: `simhash_baseline`의 원전입니다.

**Ryali et al. (2020), Bio-inspired hashing for unsupervised similarity search** — *ICML*
- 질문: FlyHash의 무작위 투영을 데이터에 맞게 학습시키면 더 나아지는가?
- 핵심: 생물학적으로 그럴듯한 국소 학습 규칙으로 투영을 학습하는 BioHash를 제안했습니다. FlyHash 등보다 좋은 검색 성능을 보고했습니다.
- 여기서: "실측 배선 vs 이상화 무작위" 비교에 더해 "학습된 배선"이라는 세 번째 비교축을 줍니다.

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
- 여기서: `run_experiment.py`의 평가를 설계할 때 반드시 참고해야 합니다. 특히 "집단 평균 SC를 그대로 내놓는 디코더"를 기준선에 추가해야 개선이 개인 신호 때문인지 알 수 있습니다.

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

## 4. 로봇·후각 추적

**Lechner et al. (2020), Neural circuit policies enabling auditable autonomy** — *Nat Mach Intell*
- 질문: C. elegans 회로에서 영감을 받은 작은 신경망으로 실제 제어를 할 수 있는가?
- 핵심: 선충 신경회로 구조(감각→인터→명령→운동 뉴런)를 본뜬 소수 뉴런의 신경 회로 정책(NCP)으로 자율주행 차선 유지를 수행했습니다. 대형 네트워크에 견줄 성능과 해석 가능성을 보였습니다.
- 여기서: `robot_experiment`와 가장 가까운 선행 연구입니다. 차이점은 NCP가 "회로 구조를 본뜬 설계"인 데 비해 이 저장소는 "실측 커넥톰을 고정 리저버로" 쓴다는 것입니다. 이 차이를 명확히 하세요.

**Singh, van Breugel, Rao & Brunton (2023), Emergent behaviour and neural dynamics in artificial agents tracking odour plumes** — *Nat Mach Intell*
- 질문: 난류 냄새 플룸을 추적하도록 강화학습한 RNN 에이전트는 어떤 행동과 내부 표현을 갖게 되는가?
- 핵심: 곤충과 비슷한 surge·casting 행동이 저절로 나타났습니다. 내부 동역학에는 "마지막 냄새 감지 이후 경과 시간" 같은 기억 변수가 표현됐습니다.
- 여기서: `plume_tracking.py`와 설정이 거의 같습니다. "이 과제는 기억이 필요하다"는 코드 주석의 근거이며, 학습된 RNN과 커넥톰 리저버를 비교할 직접 대상입니다.

**Kennedy (1983), Zigzagging and casting as a programmed response to wind-borne odour** — *Physiol Entomol*
- 질문: 나방은 바람에 실린 냄새를 어떻게 따라가는가?
- 핵심: 냄새를 감지하면 바람을 거슬러 전진(surge)하고, 놓치면 바람에 수직으로 지그재그(casting)하는 행동을 정리한 리뷰입니다.
- 여기서: `plume_tracking.py` 휴리스틱 베이스라인의 근거입니다.

**Farrell et al. (2002), Filament-based atmospheric dispersion model** — *Environ Fluid Mech*
- 질문: 짧은 시간 척도의 간헐적인 냄새 플룸을 어떻게 시뮬레이션할까?
- 핵심: 퍼프(filament)들이 바람을 따라 이동하며 퍼지는 계산 효율적인 확산 모델을 제안했습니다.
- 여기서: `plume_tracking.py` 퍼프 모델의 원전입니다.

**Vergassola, Villermaux & Shraiman (2007), 'Infotaxis'** — *Nature*
- 질문: 농도 기울기가 없는 희박한 신호로 냄새원을 찾으려면?
- 핵심: 냄새원 위치에 대한 정보 이득(엔트로피 감소)을 최대화하는 방향으로 움직이는 infotaxis를 제안했습니다. 결과적으로 casting과 비슷한 궤적이 나타납니다.
- 여기서: 베이지안 최적 전략에 가까운 강한 베이스라인입니다. 리저버 정책의 상한을 가늠할 때 씁니다.

**Baker et al. (2018), Algorithms for olfactory search across species** — *J Neurosci*
- 질문: 여러 종은 어떤 후각 탐색 알고리즘을 쓰는가?
- 핵심: 곤충, 선충, 포유류 등의 후각 탐색 전략과 그 신경 기반을 비교 정리한 리뷰입니다.
- 여기서: `chemotaxis.py`(부드러운 기울기)와 `plume_tracking.py`(간헐적 신호)의 과제 차이를 생물학적으로 설명할 근거입니다.

**Pierce-Shimomura, Morse & Lockery (1999), The fundamental role of pirouettes in C. elegans chemotaxis** — *J Neurosci*
- 질문: 선충은 어떻게 화학물질 농도를 따라가는가?
- 핵심: 농도가 떨어질 때 급회전(pirouette) 빈도를 높이는 biased random walk가 화학주성의 핵심 전략임을 보였습니다.
- 여기서: `chemotaxis.py` 에이전트가 학습한 전략을 실제 선충 전략과 비교할 기준입니다.

**Salimans et al. (2017), Evolution strategies as a scalable alternative to RL** — arXiv:1703.03864
- 질문: 기울기 없이 진화 전략(ES)만으로 강화학습 문제를 풀 수 있는가?
- 핵심: 대칭(antithetic) 샘플링과 순위 변환을 쓴 단순한 ES가 대규모 병렬화로 RL 벤치마크에서 경쟁력 있는 성능을 냈습니다.
- 여기서: `evolve.py` 알고리즘의 원전입니다.

**Wierstra et al. (2014), Natural evolution strategies** — *JMLR*
- 질문: 탐색 분포의 파라미터를 자연 기울기로 업데이트하면?
- 핵심: 자연 기울기 기반 ES(NES)를 제안했습니다. fitness shaping(순위 변환)으로 보상 척도에 강건하게 만들었습니다.
- 여기서: `evolve.py`의 centered rank transform의 출처입니다.

**Maisak et al. (2013), A directional tuning map of Drosophila elementary motion detectors** — *Nature*
- 질문: 초파리의 기본 운동 감지기는 어디에 있나?
- 핵심: T4(밝은 가장자리)와 T5(어두운 가장자리) 세포가 네 방향 운동에 선택적으로 반응하며, 서로 다른 층으로 출력한다는 것을 보였습니다.
- 여기서: `drone_nav.py`의 "근접도와 그 시간미분(looming)"이라는 광류 입력을 설계한 생물학적 근거입니다.

**Shiu et al. (2024), A Drosophila computational brain model reveals sensorimotor processing** — *Nature*
- 질문: 전뇌 커넥톰만으로 만든 단순 모델이 실제 감각-운동 회로를 예측할 수 있는가?
- 핵심: FlyWire 커넥톰과 신경전달물질 정보로 누설 적분-발화 모델을 만들었습니다. 이 모델이 미각·섭식 관련 회로의 활성화를 예측했고, 일부 예측은 실험으로 검증됐습니다.
- 여기서: "실측 커넥톰을 그대로 동역학 모델로 쓴다"는 이 저장소 접근의 대규모 버전입니다.

**Wang-Chen et al. (2024), NeuroMechFly v2** — *Nat Methods*
- 질문: 초파리 몸체 물리 시뮬레이션에 감각(시각, 후각)과 제어를 결합할 수 있는가?
- 핵심: MuJoCo 기반 초파리 모델에 시각·후각 입력과 계층적 제어를 추가했습니다. 냄새 추적이나 시각 추적 같은 과제를 시연했습니다.
- 여기서: 점 에이전트 대신 실제 초파리 몸체로 plume 추적을 옮길 때의 플랫폼입니다.

---

## 한눈에 보는 연결 관계

```
                    Maslov & Sneppen (널 모델)
                              │  ← 네 실험 공통 "실제 vs 무작위" 비교
     ┌──────────────┬─────────┴─────────┬──────────────────────┐
 리저버 컴퓨팅        FlyHash             SC 복원               로봇·후각
 Jaeger (ESN, MC)    Dasgupta (FlyHash)  Honey (SC→FC 동역학)   Lechner (NCP)
 Suárez 2021/2024    Caron ↔ Zheng       Zhang 2022 (FC→SC GAN) Singh 2023 (RNN plume)
 Damicelli           (무작위 vs 구조)     Li & Mateos (역문제)    Kennedy / Farrell
      │                                  Liégeois (FC 정의)           │
      │                                  van den Heuvel 2016 (종간)   │
      └──────── 예측 SC를 리저버로 검증 ──┘                            │
      └────────────── 같은 리저버를 로봇 정책으로 ────────────────────┘
```

**우선순위 제안** (제안서 진행 기준):
1. **Zhang, Wang & Zhu (2022)**: 가장 직접적인 경쟁 연구입니다. 비교 베이스라인으로 삼을지 결정해야 합니다.
2. **Liégeois et al. (2020)**: 입력 FC의 정의를 바꾸는 것만으로 이득이 있을 수 있는 가장 값싼 실험입니다.
3. **Li & Mateos (2019)**: prior 정규화를 수식으로 정식화할 틀입니다.
4. **van den Heuvel et al. (2016)**과 **Towlson et al. (2013)**: 핵심 가정의 근거입니다.
5. **Zalesky et al. (2024)**: 평가 설계(집단 평균 기준선)에 반드시 반영해야 합니다.
