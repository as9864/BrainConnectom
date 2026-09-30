# 배경 논문 읽기 목록

이 저장소의 네 실험(`reservoir_experiment`, `flyhash_experiment`, `sc_prior_experiment`, `robot_experiment`)과 관련된 배경 논문을 실험별로 모은 목록입니다.

- ⭐ = 먼저 읽을 논문
- `[ ]` → 다 읽으면 `[x]`로 바꿔서 진행 상황을 기록하세요
- **관련 코드** 칸은 그 논문이 저장소의 어느 부분과 이어지는지를 적은 것입니다
- 서지 정보는 기억에 기반해 정리한 것이라, 인용하기 전에 반드시 원문(DOI/출판사 페이지)으로 저자·연도·저널을 확인하세요. 특히 [확인 필요](#확인-필요-항목) 섹션의 항목은 주의가 필요합니다.

---

## 0. 공통 기초

| 읽음 | 논문 | 관련 코드 |
| --- | --- | --- |
| [ ] | ⭐ Bullmore & Sporns (2009). Complex brain networks: graph theoretical analysis of structural and functional systems. *Nat Rev Neurosci* | 저장소 전체 (네트워크 신경과학 입문) |
| [ ] | Rubinov & Sporns (2010). Complex network measures of brain connectivity: uses and interpretations. *NeuroImage* | `sc_prior_experiment/topology.py` (지표 정의, Brain Connectivity Toolbox) |
| [ ] | ⭐ Maslov & Sneppen (2002). Specificity and stability in topology of protein networks. *Science* | `reservoir_experiment/connectome.py`의 `degree_null` (차수 보존 재배선) |
| [ ] | Chen, Hall & Chklovskii (2006). Wiring optimization can relate neuronal structure and function. *PNAS* 103(12) | `data_sources/celegans_multiplex` (데이터셋 인용 요구 논문) |
| [ ] | De Domenico, Porter & Arenas (2015). MuxViz: a tool for multilayer analysis and visualization of networks. *J Complex Networks* 3(2) | `data_sources/celegans_multiplex` (데이터셋 인용 요구 논문) |
| [ ] | White et al. (1986). The structure of the nervous system of the nematode *C. elegans*. *Phil Trans R Soc B* | C. elegans 커넥톰 원전 |
| [ ] | Varshney et al. (2011). Structural properties of the *C. elegans* neuronal network. *PLoS Comput Biol* | C. elegans 커넥톰 위상 분석 |
| [ ] | Cook et al. (2019). Whole-animal connectomes of both *C. elegans* sexes. *Nature* | 더 최신 C. elegans 커넥톰 (데이터 교체 후보) |

## 1. 리저버 컴퓨팅 — `reservoir_experiment/`

| 읽음 | 논문 | 관련 코드 |
| --- | --- | --- |
| [ ] | ⭐ Suárez et al. (2024). conn2res: a toolbox for connectome-based reservoir computing. *Nat Commun* | 실험 전체 (README에 적힌 원 논문) |
| [ ] | ⭐ Suárez et al. (2021). Learning function from structure in neuromorphic networks. *Nat Mach Intell* | 실험 전체, 제안서 참고문헌 |
| [ ] | Damicelli, Hilgetag & Goulas (2022). Brain connectivity meets reservoir computing. *PLoS Comput Biol* | 실제 커넥톰 vs 널 모델 리저버 비교 |
| [ ] | Goulas, Damicelli & Hilgetag (2021). Bio-instantiated recurrent neural networks. *Neural Networks* | 커넥톰을 RNN 가중치 구조로 쓰는 접근 |
| [ ] | Jaeger (2001). Short term memory in echo state networks. GMD Report 152 | `tasks.py` 메모리 용량 벤치마크 |
| [ ] | Jaeger (2001). The "echo state" approach to analysing and training recurrent neural networks. GMD Report 148 | `reservoir.py` ESN 기본 |
| [ ] | Atiya & Parlos (2000). New results on recurrent network training. *IEEE Trans Neural Netw* | `tasks.py` NARMA-10 |
| [ ] | Lukoševičius & Jaeger (2009). Reservoir computing approaches to recurrent neural network training. *Computer Science Review* | 리저버 컴퓨팅 리뷰 |
| [ ] | Lappalainen et al. (2024). Connectome-constrained networks predict neural activity across the fly visual system. *Nature* | 확장 방향 (커넥톰 제약 모델) |

## 2. FlyHash — `flyhash_experiment/`

| 읽음 | 논문 | 관련 코드 |
| --- | --- | --- |
| [ ] | ⭐ Dasgupta, Stevens & Navlakha (2017). A neural algorithm for a fundamental computing problem. *Science* | `flyhash.py`, `idealized_connectivity()` |
| [ ] | ⭐ Caron, Ruta, Abbott & Axel (2013). Random convergence of olfactory inputs in the *Drosophila* mushroom body. *Nature* | "PN→KC 연결은 무작위" 가정의 근거 |
| [ ] | ⭐ Zheng et al. (2022). Structured sampling of olfactory input by the fly mushroom body. *Curr Biol* | 비균등 연결 근거 — README의 미해결 질문과 직결 |
| [ ] | Litwin-Kumar, Harris, Axel, Sompolinsky & Abbott (2017). Optimal degrees of synaptic connectivity. *Neuron* | KC당 입력 수(~6) 이론, `biased_synthetic` 차수 분포 |
| [ ] | Li et al. (2020). The connectome of the adult *Drosophila* mushroom body provides insights into function. *eLife* | `flyhash_real_hemibrain` |
| [ ] | Scheffer et al. (2020). A connectome and analysis of the adult *Drosophila* central brain. *eLife* | neuPrint hemibrain 데이터 |
| [ ] | Dorkenwald et al. (2024). Neuronal wiring diagram of an adult brain. *Nature* | FlyWire (hemibrain 대안 데이터) |
| [ ] | Eichler et al. (2017). The complete connectome of a learning and memory centre in an insect brain. *Nature* | 유충 버섯체 커넥톰 |
| [ ] | Charikar (2002). Similarity estimation techniques from rounding algorithms. *STOC* | `simhash_baseline` |
| [ ] | Ryali et al. (2020). Bio-inspired hashing for unsupervised similarity search. *ICML* | FlyHash 후속 연구 (BioHash) |

## 3. SC 복원 — `sc_prior_experiment/`, `docs/proposal.md`

### 3.1 구조-기능 결합 (SC-FC coupling)

| 읽음 | 논문 | 관련 코드 |
| --- | --- | --- |
| [ ] | ⭐ Honey et al. (2009). Predicting human resting-state functional connectivity from structural connectivity. *PNAS* | `human_data.py` (SC 위 동역학으로 FC 시뮬레이션) |
| [ ] | ⭐ Suárez, Markello, Betzel & Misic (2020). Linking structure and function in macroscale brain networks. *Trends Cogn Sci* | 제안서 3.1절 (분야 리뷰) |
| [ ] | Sarwar et al. (2021). Structure-function coupling in the human connectome: a machine learning approach. *NeuroImage* | 제안서 3.1절 (개인 수준 SC→FC 딥러닝 예측) |
| [ ] | Neudorf et al. (2022). Structure can predict function in the human brain: a graph neural network deep learning model of functional connectivity and centrality based on structural connectivity. *Brain Struct Funct* | 제안서 3.1절 "89%/99%" 수치의 출처 |
| [ ] | Zalesky et al. (2024). Predicting an individual's functional connectivity from their structural connectome: evaluation of evidence, recommendations, and future prospects. *Netw Neurosci* | 제안서 3.1절 (개인 수준 SC→FC 예측의 한계 평가) |
| [ ] | Rosenthal et al. (2018). Mapping higher-order relations between brain structure and function with embedded vector representations of connectomes. *Nat Commun* | SC-FC 임베딩 접근 |
| [ ] | (조사 필요) FC→SC 역방향 예측 선행 연구 | `decoder.py`, 제안서 3.1절의 "공백" 주장 근거 |

### 3.2 비교 커넥톰믹스와 보존된 배선 원리

| 읽음 | 논문 | 관련 코드 |
| --- | --- | --- |
| [ ] | ⭐ van den Heuvel, Bullmore & Sporns (2016). Comparative connectomics. *Trends Cogn Sci* | 제안서 3.2절 핵심 근거 |
| [ ] | Bullmore & Sporns (2012). The economy of brain network organization. *Nat Rev Neurosci* | 배선 경제성, 제안서 참고문헌 |
| [ ] | van den Heuvel & Sporns (2011). Rich-club organization of the human connectome. *J Neurosci* | `topology.py` 리치클럽 |
| [ ] | Towlson et al. (2013). The rich club of the *C. elegans* neuronal connectome. *J Neurosci* | `invertebrate_prior.py` (같은 지표를 C. elegans에 적용) |
| [ ] | Witvliet et al. (2021). Connectomes across development reveal principles of brain maturation. *Nature* | 증강용 추가 C. elegans 표본 |
| [ ] | Winding et al. (2023). The connectome of an insect brain. *Science* | 증강용 유충 초파리 전뇌 |

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

## 4. 로봇 제어 / 후각 추적 — `robot_experiment/`

| 읽음 | 논문 | 관련 코드 |
| --- | --- | --- |
| [ ] | ⭐ Lechner et al. (2020). Neural circuit policies enabling auditable autonomy. *Nat Mach Intell* | `policy.py` (C. elegans 회로 기반 제어 정책 — 가장 가까운 선행 연구) |
| [ ] | ⭐ Singh, van Breugel, Rao & Brunton (2023). Emergent behaviour and neural dynamics in artificial agents tracking odour plumes. *Nat Mach Intell* | `plume_tracking.py` (RNN 에이전트 plume 추적) |
| [ ] | Kennedy (1983). Zigzagging and casting as a programmed response to wind-borne odour: a review. *Physiol Entomol* | `plume_tracking.py` (surge-and-cast) |
| [ ] | Farrell et al. (2002). Filament-based atmospheric dispersion model to achieve short time-scale structure of odor plumes. *Environ Fluid Mech* | `plume_tracking.py` (퍼프 모델) |
| [ ] | Vergassola, Villermaux & Shraiman (2007). 'Infotaxis' as a strategy for searching without gradients. *Nature* | plume 탐색 베이스라인 후보 |
| [ ] | Baker et al. (2018). Algorithms for olfactory search across species. *J Neurosci* | 후각 탐색 알고리즘 리뷰 |
| [ ] | Pierce-Shimomura, Morse & Lockery (1999). The fundamental role of pirouettes in *Caenorhabditis elegans* chemotaxis. *J Neurosci* | `chemotaxis.py` (실제 선충의 화학주성 전략) |
| [ ] | Salimans et al. (2017). Evolution strategies as a scalable alternative to reinforcement learning. arXiv:1703.03864 | `evolve.py` (OpenAI-ES) |
| [ ] | Wierstra et al. (2014). Natural evolution strategies. *JMLR* | `evolve.py` (centered rank transform) |
| [ ] | Maisak et al. (2013). A directional tuning map of *Drosophila* elementary motion detectors. *Nature* | `drone_nav.py` (T4/T5 운동 감지) |
| [ ] | Shiu et al. (2024). A *Drosophila* computational brain model reveals sensorimotor processing. *Nature* | 실제 전뇌 커넥톰 기반 감각-운동 모델 |
| [ ] | Wang-Chen et al. (2024). NeuroMechFly v2: simulating embodied sensorimotor control in adult *Drosophila*. *Nat Methods* | 커넥톰 + 몸체 시뮬레이션 (후각 추적 포함) |

## 5. 이미 정리한 논문

| 논문 | 해설 |
| --- | --- |
| Prasanth & Tivnan (2026). BioNIC. arXiv:2601.20876 | [BioNIC_해설.md](BioNIC_해설.md) |

---

## 확인 필요 항목

제안서(`docs/proposal.md`, `docs/proposal.docx`)와 대조하며 찾은 인용 문제입니다. 1–3번은 웹 검색으로 서지 정보를 확인한 뒤 제안서에 반영했습니다.

1. ~~**"89% / 99%" 수치의 출처**~~ → **수정 완료**: *Brain Struct Funct*의 GNN 논문은 Neudorf, Kress & Borowsky (2022)입니다. Sarwar et al. (2021)은 *NeuroImage*에 실린 별개 논문이라 따로 인용했습니다. 논문 버전(bioRxiv/출판본)에 따라 보고된 수치가 다를 수 있으니, 인용 전에 출판본의 수치를 다시 확인하세요.
2. ~~**Zhang, L. et al. (2024), *Network Neuroscience***~~ → **수정 완료**: 실제 저자는 Zalesky, Sarwar, Tian, Liu, Yeo & Ramamohanarao (2024)입니다. 이 논문은 FC→SC 역방향이 아니라 **SC→FC 개인 수준 예측**을 평가한 논문이라, 제안서 3.1절의 해당 문장도 내용에 맞게 고쳤습니다.
3. ~~**HCP 데이터 접근 조건**~~ → **수정 완료**: "승인 절차 없이"를 "ConnectomeDB 계정 가입과 Open Access 데이터 이용약관 동의 후 접근 가능"으로 고쳤습니다.
4. **FC→SC 역방향 선행 연구** (남은 과제): `"inferring structural connectivity from functional connectivity"`, `"functional-to-structural connectivity prediction"` 같은 키워드로 조사해서 3.1절 표를 채우세요. 제안서의 "이 방향은 덜 연구되었다"는 주장에는 아직 직접 인용할 근거가 없습니다.
