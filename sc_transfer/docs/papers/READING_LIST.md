# 배경 논문 읽기 목록

이 프로젝트(종간 배선 원리의 전이 가능성, FC→SC)와 관련된 배경 논문 목록입니다. 원래 BrainConnectom 저장소의 네 실험 전체 목록에서 관련 절만 남겼습니다(절 번호는 원본 그대로).

- ⭐ = 먼저 읽을 논문
- `[ ]` → 다 읽으면 `[x]`로 바꿔서 진행 상황을 기록하세요
- **관련 코드** 칸은 그 논문이 저장소의 어느 부분과 이어지는지를 적은 것입니다
- 요약은 [SUMMARIES.md](SUMMARIES.md)에 있습니다
- 서지 정보는 기억에 기반해 정리한 것이라 (3.1b절과 제안서 참고문헌은 웹 검색으로 확인함), 인용하기 전에 반드시 원문(DOI/출판사 페이지)으로 저자·연도·저널을 확인하세요. 특히 [확인 필요](#확인-필요-항목) 섹션의 항목은 주의가 필요합니다.

---

## 0. 공통 기초

| 읽음 | 논문 | 관련 코드 |
| --- | --- | --- |
| [ ] | ⭐ Bullmore & Sporns (2009). Complex brain networks: graph theoretical analysis of structural and functional systems. *Nat Rev Neurosci* | 저장소 전체 (네트워크 신경과학 입문) |
| [ ] | Rubinov & Sporns (2010). Complex network measures of brain connectivity: uses and interpretations. *NeuroImage* | `sctransfer/topology.py` (지표 정의, Brain Connectivity Toolbox) |
| [ ] | ⭐ Maslov & Sneppen (2002). Specificity and stability in topology of protein networks. *Science* | `sctransfer/celegans.py`, `sctransfer/normalized.py`의 차수 보존 널 모델 |
| [ ] | Chen, Hall & Chklovskii (2006). Wiring optimization can relate neuronal structure and function. *PNAS* 103(12) | `data/celegans_multiplex` (데이터셋 인용 요구 논문) |
| [ ] | De Domenico, Porter & Arenas (2015). MuxViz: a tool for multilayer analysis and visualization of networks. *J Complex Networks* 3(2) | `data/celegans_multiplex` (데이터셋 인용 요구 논문) |
| [ ] | White et al. (1986). The structure of the nervous system of the nematode *C. elegans*. *Phil Trans R Soc B* | C. elegans 커넥톰 원전 |
| [ ] | Varshney et al. (2011). Structural properties of the *C. elegans* neuronal network. *PLoS Comput Biol* | C. elegans 커넥톰 위상 분석 |
| [ ] | Cook et al. (2019). Whole-animal connectomes of both *C. elegans* sexes. *Nature* | 더 최신 C. elegans 커넥톰 (데이터 교체 후보) |

## 3. SC 복원과 전이 가능성 — `sctransfer/`, `docs/proposal.md`

### 3.1 구조-기능 결합 (SC-FC coupling)

| 읽음 | 논문 | 관련 코드 |
| --- | --- | --- |
| [ ] | ⭐ Honey et al. (2009). Predicting human resting-state functional connectivity from structural connectivity. *PNAS* | `human_data.py` (SC 위 동역학으로 FC 시뮬레이션) |
| [ ] | ⭐ Suárez, Markello, Betzel & Misic (2020). Linking structure and function in macroscale brain networks. *Trends Cogn Sci* | 제안서 3.1절 (분야 리뷰) |
| [ ] | Sarwar et al. (2021). Structure-function coupling in the human connectome: a machine learning approach. *NeuroImage* | 제안서 3.1절 (개인 수준 SC→FC 딥러닝 예측) |
| [ ] | Neudorf et al. (2022). Structure can predict function in the human brain: a graph neural network deep learning model of functional connectivity and centrality based on structural connectivity. *Brain Struct Funct* | 제안서 3.1절 "89%/99%" 수치의 출처 |
| [ ] | Zalesky et al. (2024). Predicting an individual's functional connectivity from their structural connectome: evaluation of evidence, recommendations, and future prospects. *Netw Neurosci* | 제안서 3.1절 (개인 수준 SC→FC 예측의 한계 평가) |
| [ ] | Rosenthal et al. (2018). Mapping higher-order relations between brain structure and function with embedded vector representations of connectomes. *Nat Commun* | SC-FC 임베딩 접근 |
| [ ] | Fotiadis, Parkes, Davis, Satterthwaite, Shinohara & Bassett (2024). Structure–function coupling in macroscale human brain networks. *Nat Rev Neurosci* 25, 688–704 | 제안서 3.1절 (최신 리뷰) |

### 3.1b FC→SC 역방향 (제안서가 다루는 방향)

서지 정보는 웹 검색으로 확인했습니다. 각 논문 요약은 [SUMMARIES.md](SUMMARIES.md#31b-fcsc-역방향)에 있습니다.

| 읽음 | 논문 | 관련 코드 |
| --- | --- | --- |
| [ ] | ⭐ Zhang, Wang & Zhu (2022). Predicting brain structural network using functional connectivity. *Med Image Anal* 79, 102463. doi:10.1016/j.media.2022.102463 | `decoder.py` — **가장 직접적인 선행 연구** (FC→SC GCN-GAN, HCP·ADNI) |
| [ ] | Zhang, Wang & Zhu (2020). Recovering brain structural connectivity from functional connectivity via multi-GCN based generative adversarial network. *MICCAI 2020*, 53–61 | 위 논문의 학회 버전, 코드: [qidianzl/Recovering-Brain-Structure-Network-Using-Functional-Connectivity](https://github.com/qidianzl/Recovering-Brain-Structure-Network-Using-Functional-Connectivity) |
| [ ] | ⭐ Li & Mateos (2019). Identifying structural brain networks from functional connectivity: a network deconvolution approach. *ICASSP 2019* | `decoder.py` — 확산 모델 기반 역문제 + 희소성 정규화 (prior 정규화와 가장 가까운 발상) |
| [ ] | Li, Mateos & Zhang (2022). Learning to model the relationship between brain structural and functional connectomes. *IEEE Trans Signal Inf Process Netw* 8, 830–843 | 그래프 신호처리 기반 SC↔FC 모델 학습 |
| [ ] | ⭐ Liégeois, Santos, Matta, Van De Ville & Sayed (2020). Revisiting correlation-based functional connectivity and its relationship with structural connectivity. *Netw Neurosci* 4(4), 1235–1251 | `human_data.py`, `decoder.py` — 상관 대신 정밀도 행렬(partial correlation) FC가 SC와 더 잘 맞음 → 입력 FC 정의 선택 |
| [ ] | Chen, Bukhari, Lin & Sejnowski (2022). Functional connectivity of fMRI using differential covariance predicts structural connectivity and behavioral reaction times. *Netw Neurosci* 6(2), 614–633 | 입력 FC를 dCov로 바꾸면 SC 복원이 쉬워지는가 |
| [ ] | Hinne, Ambrogioni, Janssen, Heskes & van Gerven (2014). Structurally-informed Bayesian functional connectivity analysis. *NeuroImage* 86, 294–305 | 반대 방향(SC를 FC 추정의 prior로) — 베이지안 prior 설계 참고 |
| [ ] | Smith et al. (2011). Network modelling methods for FMRI. *NeuroImage* 54(2), 875–891 | 어떤 FC 추정법이 실제 직접 연결을 잘 복원하는가 (시뮬레이션 벤치마크) |
| [ ] | Wu, Yu & Chen (2025). Can functional connectivity be used to refine structural connectivity strength by combining neural computational model and generative adversarial network? *Neural Comput Appl* 37, 3489–3504 | 신경 동역학 모델 + GAN으로 FC에서 SC 강도 보정 |
| [ ] | Zuo et al. (2023). Generative AI enables structural brain network construction from fMRI via symmetric diffusion learning. arXiv:2309.16205 | 확산 모델(DDPM) 기반 fMRI→SC 생성 (프리프린트) |
| [ ] | Tan et al. (2025). SFC-GAN: a generative adversarial network for brain functional and structural connectome translation. arXiv:2501.07055 | CycleGAN 기반 SC↔FC 양방향 변환 (프리프린트) |

### 3.2 비교 커넥톰믹스와 보존된 배선 원리

| 읽음 | 논문 | 관련 코드 |
| --- | --- | --- |
| [ ] | ⭐ van den Heuvel, Bullmore & Sporns (2016). Comparative connectomics. *Trends Cogn Sci* | 제안서 3.2절 핵심 근거 |
| [ ] | Bullmore & Sporns (2012). The economy of brain network organization. *Nat Rev Neurosci* | 배선 경제성, 제안서 참고문헌 |
| [ ] | van den Heuvel & Sporns (2011). Rich-club organization of the human connectome. *J Neurosci* | `topology.py` 리치클럽 |
| [ ] | Towlson et al. (2013). The rich club of the *C. elegans* neuronal connectome. *J Neurosci* | `invertebrate_prior.py` (같은 지표를 C. elegans에 적용) |
| [ ] | Witvliet et al. (2021). Connectomes across development reveal principles of brain maturation. *Nature* | 증강용 추가 C. elegans 표본 |
| [ ] | Winding et al. (2023). The connectome of an insect brain. *Science* | 증강용 유충 초파리 전뇌 |

### 3.2b 전이 가능성 분석(A 방향)의 방법론 근거

정규화·밀도·측정 방식 문제를 다루는 논문입니다. 서지 정보는 웹 검색으로 확인했고, 설명은 [methodology_transferability.md](../methodology_transferability.md)에 있습니다.

| 읽음 | 논문 | 관련 코드 |
| --- | --- | --- |
| [ ] | ⭐ Váša & Mišić (2022). Null models in network neuroscience. *Nat Rev Neurosci* 23, 493–504 | `normalized.py` — 어떤 널 모델을 왜 쓰는가 |
| [ ] | ⭐ Colizza, Flammini, Serrano & Vespignani (2006). Detecting rich-club ordering in complex networks. *Nat Phys* 2, 110–115 | `rich_club_norm` — 리치클럽은 반드시 널 대비로 봐야 함 |
| [ ] | ⭐ van Wijk, Stam & Daffertshofer (2010). Comparing brain networks of different size and connectivity density using graph theory. *PLoS ONE* 5, e13701 | `--density` — 크기·밀도가 다른 네트워크 비교의 한계 |
| [ ] | Humphries & Gurney (2008). Network 'small-world-ness'. *PLoS ONE* 3, e2051 | `clustering_norm` — 무작위 대비 비율로 정의하는 방식 |
| [ ] | Zalesky et al. (2010). Whole-brain anatomical networks: does the choice of nodes matter? *NeuroImage* 50, 970–983 | 노드 정의(parcellation)에 따라 수치가 크게 달라짐 |
| [ ] | Fornito, Zalesky & Breakspear (2013). Graph analysis of the human connectome: promise, progress, and pitfalls. *NeuroImage* 80, 426–444 | 그래프 분석의 함정 총정리 |
| [ ] | Maier-Hein et al. (2017). The challenge of mapping the human connectome based on diffusion tractography. *Nat Commun* 8, 1349 | 인간 SC 측정 오류 → 이진화·정규화 근거 |
| [ ] | ⭐ Assaf et al. (2020). Conservation of brain connectivity and wiring across the mammalian class. *Nat Neurosci* 23, 805–808 | 같은 측정 방식(확산 MRI)으로 본 종간 보존 — 정량적 보존의 선례 |
| [ ] | ⭐ Faskowitz et al. (2023). Connectome topology of mammalian brains and its relationship to taxonomy and phylogeny. *Front Neurosci* 16, 1044372 | 계통적 거리와 위상 유사성 — "사다리"의 중간 단계 |
| [ ] | Puxeddu et al. (2024). Relation of connectome topology to brain volume across 103 mammalian species. *PLoS Biol* 22, e3002489 | 뇌 크기에 따라 위상이 체계적으로 변함 → 정량적 전이가 제한될 근거 |

### 3.3 그래프 생성모델 (사전분포 학습)

| 읽음 | 논문 | 관련 코드 |
| --- | --- | --- |
| [ ] | ⭐ Betzel et al. (2016). Generative models of the human connectome. *NeuroImage* | 제안서 4.3절 (위상 통계를 재현하는 생성모델) |
| [ ] | Akarca et al. (2021). A generative network model of neurodevelopmental diversity in structural brain organization. *Nat Commun* | 개인차를 가진 생성모델 |
| [ ] | Kipf & Welling (2016). Variational graph auto-encoders. arXiv:1611.07308 | 제안서 4.2/4.3절 그래프 오토인코더·VAE |
| [ ] | Simonovsky & Komodakis (2018). GraphVAE: towards generation of small graphs using variational autoencoders. *ICANN* | 제안서 4.3절 graph VAE |

### 3.4 데이터

| 읽음 | 논문 | 관련 코드 |
| --- | --- | --- |
| [ ] | Van Essen et al. (2013). The WU-Minn Human Connectome Project: an overview. *NeuroImage* | `human_data.py`의 `load_hcp_cohort()` 연동 예정 |

## 확인 필요 항목

제안서(`docs/proposal.md`, `docs/proposal.docx`)와 대조하며 찾은 인용 문제입니다. 1–3번은 웹 검색으로 서지 정보를 확인한 뒤 제안서에 반영했습니다.

1. ~~**"89% / 99%" 수치의 출처**~~ → **수정 완료**: *Brain Struct Funct*의 GNN 논문은 Neudorf, Kress & Borowsky (2022)입니다. Sarwar et al. (2021)은 *NeuroImage*에 실린 별개 논문이라 따로 인용했습니다. 논문 버전(bioRxiv/출판본)에 따라 보고된 수치가 다를 수 있으니, 인용 전에 출판본의 수치를 다시 확인하세요.
2. ~~**Zhang, L. et al. (2024), *Network Neuroscience***~~ → **수정 완료**: 실제 저자는 Zalesky, Sarwar, Tian, Liu, Yeo & Ramamohanarao (2024)입니다. 이 논문은 FC→SC 역방향이 아니라 **SC→FC 개인 수준 예측**을 평가한 논문이라, 제안서 3.1절의 해당 문장도 내용에 맞게 고쳤습니다.
3. ~~**HCP 데이터 접근 조건**~~ → **수정 완료**: "승인 절차 없이"를 "ConnectomeDB 계정 가입과 Open Access 데이터 이용약관 동의 후 접근 가능"으로 고쳤습니다.
4. ~~**FC→SC 역방향 선행 연구**~~ → **조사 완료**: [3.1b절](#31b-fcsc-역방향-제안서가-다루는-방향)에 11편을 정리했습니다. 이 방향 연구는 **"없다"가 아니라 "적고, 주로 의료영상 쪽 GAN/GCN 연구"**입니다. 따라서 제안서의 "덜 연구되었다"는 표현은 유지할 수 있지만, 독창성 주장은 "FC→SC 자체"가 아니라 **"종간 위상 통계를 prior로 쓴다는 점"**에 두어야 합니다. 특히 Zhang, Wang & Zhu (2022)는 반드시 인용하고 비교 대상으로 삼아야 합니다. 참고로 원래 제안서의 "Zhang, L. et al." 인용은 이 논문(제1저자 Lu Zhang)과 Zalesky et al. (2024)가 섞인 것으로 보입니다.
