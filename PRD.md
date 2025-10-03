# PRD: AI Furnishing Project

## 1. Problem Statement & Goals

### Business Problem
Automatyczne generowanie aranżacji wnętrz (rozmieszczenie mebli) dla mieszkań na podstawie ich planów architektonicznych

### External Dependencies
- [✅] **Dataset**: 503 apartments analyzed (sample from ~100k in `Jednostka/datasets/apartment_jsons/`)
- [✅] **Furniture catalog**: Schema understood, 1 example available (`b1.json`)
- [ ] **Compute**: Jednostka GPU dla fine-tuningu (needed for production)
- [ ] **APIs**: OpenAI/Claude dla prototypu (opcjonalne)

### Data Constraints
- ✅ **Sample data analyzed**: 503 apartments from 2 projects (AQU-MAR, MET-ZAC)
  - 39 unique furniture IDs in use
  - 12 room types (idBedroom, idBathroom, idLivingRoomWithAnnex, etc.)
  - 100% furniture coverage
  - ~19.4 furniture items per apartment
- ⚠️ **Limited furniture catalog access**: Due to data confidentiality
  - Have schema and one example (`b1.json`)
  - Cannot share full catalog in exploration repo
  - Full access for internal offline models to complete library
- ⚠️ **Full dataset access**: ~100k apartments available in Jednostka
  - Exploration done on 503 sample
  - Full pipeline will process all 100k 

**Input:** JSON z pustym mieszkaniem (ściany, okna, drzwi, pomieszczenia bez mebli)  
**Output:** JSON z tym samym mieszkaniem + wygenerowane meble w `equipments` i `caseworks`

**Business value:**
- Automatyzacja procesu projektowania różnych wariantów aranżacji
- Generowanie wielu propozycji dla klienta
- Przyśpieszenie workflow architektów wnętrz

### Success Metrics
- [ ] **Semantic correctness**: 95%+ poprawnych par pomieszczenie→meble (brak WC w salonie)
- [ ] **Spatial feasibility**: 90%+ wygenerowanych mebli nie koliduje ze ścianami/drzwiami
- [ ] **Diversity**: generowanie min. 5 różnych sensownych aranżacji dla tego samego mieszkania
- [ ] **Human evaluation**: 70%+ aranżacji ocenionych jako "do zaakceptowania" przez architekta
- [ ] **Baseline to beat**: reguły hardcoded (if bedroom → bed) → oczekujemy ~40% akceptowalności

### Timeline
- **Research phase**: 2025-10-01 do 2025-11-15 (6 tygodni)
- **MVP deadline**: 2025-12-01 (prototyp działający na 500 mieszkaniach)
- **Production ready**: 2026-01-31 

## 2. Data Strategy

### Required Datasets
- [ ] **Dataset: apartment_jsons** (~100k mieszkań z meblami)
  - Source: `Jednostka/datasets/apartment_jsons/` (już istniejący)
  - Size estimate: ~100 000 mieszkań z pełną aranżacją
  - Quality concerns: 
    - Czy wszystkie mieszkania mają meble?
    - Jakie są brakujące typy pomieszczeń?
    - Czy są błędne aranżacje (WC w salonie)?
  - **Output format**: JSON ze strukturą `compartments[].equipments[]` + `caseworks[]`

### Data Pipeline Plan
- [✅] **Exploration** (COMPLETE):
  - EDA on 503 apartments → `results/eda_stats.json`
  - Schema understanding → `FURNITURE_SCHEMA.md`
  - Data quality assessment → `results/EDA_ANALYSIS.md`
  
- [ ] **Collection** (`datasets_pipelines/apartment_jsons_pipe/1_collect/`):
  - Wczytać wszystkie ~100k JSONy z Jednostka
  - Filtrować tylko mieszkania z co najmniej 1 meblem
  
- [ ] **Validation** (`2_validate/`):
  - Sprawdzić kompletność danych geometrycznych (boundaries, walls, doors)
  - Wykryć missing fields w `equipments`/`caseworks`
  - Flagować potencjalnie błędne pary (pomieszczenie-mebel)
  
- [ ] **Processing** (`3_process/`):
  - **Utworzenie par (input, output)**:
    - Input: JSON z pustymi `equipments[]` i `caseworks[]`
    - Output: JSON z oryginalnymi meblami
  - Normalizacja współrzędnych do [0,1]
  - Ekstrakcja features: area, perimeter, name_cad, door_positions, window_positions
  
- [ ] **Split** (`4_split/`):
  - Train: 80% (~80k)
  - Val: 10% (~10k)
  - Test: 10% (~10k)
  - Stratyfikacja po typie mieszkania (M1, M2, M3, M4)

## 3. ML Approach

### Initial Hypothesis
**Approach: Hybrid 2-Stage Pipeline**

**Stage 1: LLM dla semantyki** (co wstawić)
- Input: `room_type`, `area`, `boundary_shape` (uproszczone features)
- Output: Lista ID mebli do wstawienia: `["b2", "sz", "wardrobe"]`
- Model: Fine-tuned LLaMA-3-8B na 100k przykładach

**Stage 2: Geometric solver** (gdzie wstawić)
- Input: Lista ID + boundary + furniture dimensions (z SVG catalog)
- Output: `insert_point`, `angle` dla każdego mebla
- Model: Rule-based lub VAE/Diffusion

**Dlaczego hybrid?**
- LLM jest świetny w pattern matching semantycznym (`idBedroom` → `b2`)
- LLM jest słaby w geometrii (insert_point to losowe liczby)
- Separacja odpowiedzialności → łatwiejsze debugowanie
- Możliwość użycia reguł geometrycznych (collision detection)

### Alternative Approaches
1. **Approach A: LLM Fine-tune** (BASELINE)
   - Model: LLaMA-3-8B / Mistral-7B
   - Format: JSON → JSON completion
   - Pros: Szybki start, dobre wyniki na structured data
   - Cons: Black-box, trudne debugowanie błędów przestrzennych

2. **Approach B: Hybrydowy (Rules + ML)**
   - Warstwa 1: Reguły semantyczne (bedroom → bed, bathroom → WC)
   - Warstwa 2: ML model do pozycjonowania (VAE/Diffusion dla coordinates)
   - Pros: Kontrola nad absurdami, interpretowalność
   - Cons: Wymaga domain expertise, więcej engineering

3. **Approach C: Graph Neural Network**
   - Reprezentacja: Pokoje = nodes, Drzwi = edges
   - Model: GraphSAGE / GAT do predykcji labels (meble)
   - Pros: Naturalna reprezentacja przestrzeni, dobre dla relacji
   - Cons: Bardziej research, mniej przykładów implementacji

4. **Approach D: Zero-shot z GPT-4/Claude**
   - Prototyp: 500 przykładów przez API
   - Pros: Najszybszy start, ocena feasibility
   - Cons: Koszty, latencja, brak kontroli

### Technical Constraints
- Inference time requirements: < 5s na jedno mieszkanie (dla produkcji)
- Model size limits: Max 13B params (fit na Jednostka GPU)
- Hardware constraints: Fine-tuning na Jednostka (A100 40GB)
- Integration requirements: Output musi być valid JSON zgodny ze schematem 

## 4. Exploration Roadmap

### Phase 1: Data Understanding ✅ COMPLETE
- [✅] EDA notebook (`notebooks/eda_apartments.ipynb`)
- [✅] Data quality assessment (`results/EDA_ANALYSIS.md`)
- [✅] Furniture schema documented (`FURNITURE_SCHEMA.md`)
- [✅] Feature engineering: room_type (`name_cad`), area, perimeter, window_area, boundary
- [ ] Baseline model performance (next: move to `ai_furnishing` repo)

### Phase 2: Model Experiments
- [ ] Baseline implementation (`1_baseline.ipynb`)
- [ ] Model comparison (`2_experiments.ipynb`)
- [ ] Hyperparameter tuning
- [ ] Feature selection

### Phase 3: Validation & Analysis
- [ ] Cross-validation results
- [ ] Error analysis
- [ ] Model interpretability
- [ ] Performance on edge cases

## 5. Production Considerations

### Model Requirements
- Accuracy threshold: 
- Latency requirements: 
- Scalability needs: 

### Integration Plan
- Input format: 
- Output format: 
- API requirements: 
- Monitoring strategy: 

## 6. Risk Assessment

### Technical Risks
- [ ] Data availability/quality
- [ ] Model performance
- [ ] Computational requirements
- [x] **Insert point heterogeneity** (DISCOVERED 2025-10-01)

### Known Issues & Mitigations

#### Issue 1: Insert Point Heterogeneity ✅ RESOLVED (Oct 2)
**Problem**: SVG furniture definitions have inconsistent insert points

**Resolution**: Discovered structured JSON furniture definitions with:
- `insert_point_type`: ["wall_based", "universal", "opening", "standalone"]
- Boundaries are RELATIVE to insert_point
- Schema clarifies placement logic per type

**New approach**: ✅ BETTER THAN EXPECTED
- Use JSON parser instead of SVG parser
- Filter out `"opening"` type (doors/windows - don't place)
- Apply type-specific placement logic in Stage 2
- `clash_detection_boundary` provided for collision detection
- See: `NOTES_2025_10_02_furniture_jsons.md`

#### Issue 2: Collision Detection in 3D ℹ️ DISCOVERED (Oct 2)
**Finding**: Furniture has `layer_index` for vertical collision layers
- Example: Chair (layer=2) can go under Table (layer=1)
- Enables realistic multi-layer arrangements

**Mitigation**: 
- Initial implementation: Treat all as same layer (conservative)
- Future optimization: Layer-aware collision detection
- Low priority for MVP

### Mitigation Strategies
- Risk 1 → Mitigation plan
- Risk 2 → Mitigation plan

## 7. Resources & Dependencies

### Required Skills/Tools
- [ ] **Libraries**: transformers, PyTorch, datasets (Hugging Face)
- [ ] **Fine-tuning**: Axolotl / PEFT (LoRA) dla efektywnego treningu
- [ ] **Zero-shot testing**: OpenAI/Anthropic API (prototyp)
- [ ] **Geometric validation**: Shapely, numpy do sprawdzania kolizji
- [ ] **Domain expertise**: Konsultacje z architektami wnętrz (walidacja wyników)

### External Dependencies
- [ ] **Dataset**: `Jednostka/datasets/apartment_jsons/` (pobrać istnieje)
- [ ] **Compute**: Jednostka GPU dla fine-tuningu
- [ ] **APIs**: OpenAI/Claude dla prototypu (opcjonalne)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|  
| 2025-10-01 | Hybrid 2-stage pipeline (semantic + geometric) | LLM świetny w pattern matching (room→furniture), słaby w geometrii (coordinates) |
| 2025-10-01 | Stage 1: Fine-tune LLM dla semantyki | 100k przykładów wystarczy do nauki par (idBedroom→b2) |
| 2025-10-01 | Stage 2: Rule-based geometric solver | Insert points wymagają zrozumienia wymiarów i kolizji |
| 2025-10-02 | Furniture as JSON (not SVG) | Discovered structured JSON with dimensions, boundaries, insert_point_type |
| 2025-10-02 | Boundaries are RELATIVE to insert_point | Simplifies transformation logic (scale → rotate → translate) |
| 2025-10-03 | Room type = `name_cad` field | Key for extracting room features from apartment JSON |
| 2025-10-03 | Research phase complete, move to production repos | 503 apartments analyzed, schema understood, ready for `datasets_pipelines` and `ai_furnishing` |

## Next Actions

### Phase 0: Research & Exploration ✅ COMPLETE (Oct 1-3, 2025)
- [✅] **503 apartments** uploaded and analyzed
- [✅] **EDA complete** (`notebooks/eda_apartments.ipynb` → `results/eda_stats.json`)
- [✅] **Furniture schema** understood and documented (`FURNITURE_SCHEMA.md`)
- [✅] **Data structure** mapped (room_type = `name_cad`, boundaries are relative)
- [✅] **Approach defined**: Hybrid 2-Stage Pipeline (Semantic + Geometric)
- **✅ Decision**: Ready to proceed with full pipeline and model training

### Faza 1: Data Pipeline (2 tygodnie)
- [ ] **EDA**: `datasets_pipelines/apartment_jsons_pipe/0_scan/`
  - Ile mieszkań ma meble?
  - Jakie typy pomieszczeń/mebli występują?
  - Czy są błędne dane?
- [ ] **Zbudować pipeline** w `datasets_pipelines/apartment_jsons_pipe/`
- [ ] **Wygenerować pairs** (empty → furnished)

### Faza 2: Exploration (2 tygodnie)
- [ ] **Baseline**: Fine-tune LLaMA-3-8B na 10k przykładach
- [ ] **Evaluation**: Semantic correctness + spatial feasibility
- [ ] **Iterate**: Jeśli baseline słaby → rozważyć Approach B (hybrid)