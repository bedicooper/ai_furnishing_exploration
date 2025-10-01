# TODO List - AI Furnishing Project

## 🔴 **TOMORROW (Oct 2, 2025)** - Data Collection

### Step 1: Upload Sample Data
- [✅] Wgraj 5-10 przykładowych mieszkań do `samples/`
  - Różne typy: M1, M2, M3, M4
  - Z różnymi pomieszczeniami
  - Format: `apartment_001.json`, `apartment_002.json`, ...
  
- [ ] Wgraj katalog mebli SVG do `samples/`
  - Plik: `furniture_catalog.svg`
  - Sprawdź czy ma strukturę: `<g id="b2"><path class="bg" d="..."/></g>`

### Step 2: Extract Furniture Catalog
- [ ] Otwórz: `notebooks/extract_furniture_catalog.ipynb`
- [ ] Uruchom wszystkie celle
- [ ] Sprawdź czy wymiary mają sens (b2 = łóżko podwójne ~2m x 1.5m)
- [ ] Jeśli wymiary dziwne → dostosuj `SVG_SCALE_FACTOR` w `utils/svg_parser.py`
- [ ] Wygeneruj: `samples/furniture_catalog.json`

### Step 3: Run EDA on Apartments
- [✅] Otwórz: `notebooks/eda_apartments.ipynb`
- [✅] Zaktualizuj `data_dir` → ścieżka do `samples/`
- [✅] Uruchom wszystkie celle
- [✅] Zapisz wyniki do `configs/eda_stats.json`

### Step 4: Analyze Results
- [✅] Jakie `furniture_ids` występują w mieszkaniach?
- [✅] Czy wszystkie ID są w katalogu SVG? (jeśli nie → trzeba dodać)
- [✅] Jakie `room_types` są w danych?
- [✅] Ile średnio mebli na pokój?

---

## 🟡 **LATER** - Data Pipeline

### Phase 1: Full Dataset Collection (Week of Oct 7)
- [ ] Napisać skrypt do wyciągania wszystkich ~100k mieszkań z bazy
- [ ] Setup: `datasets_pipelines/apartment_jsons_pipe/1_collect/`
- [ ] Zapisać do: `apartment_jsons_pipe/raw/`

### Phase 2: Validation (Week of Oct 7)
- [ ] Sprawdzić kompletność danych (boundaries, walls, doors)
- [ ] Flagować missing fields
- [ ] Setup: `2_validate/`

### Phase 3: Processing (Week of Oct 14)
- [ ] Stworzyć pary (input=pusty, output=umeblowany)
- [ ] Normalizacja współrzędnych
- [ ] Ekstrakcja features
- [ ] Setup: `3_process/`

### Phase 4: Split (Week of Oct 14)
- [ ] Train/Val/Test split (80/10/10)
- [ ] Stratyfikacja po typie mieszkania
- [ ] Setup: `4_split/`

---

## 🟢 **FUTURE** - Model Training

### Stage 1: Semantic Model (Week of Oct 21)
- [ ] Przygotować dane treningowe: `room_features → furniture_ids`
- [ ] Fine-tune LLaMA-3-8B
- [ ] Evaluation: semantic correctness

### Stage 2: Geometric Solver (Week of Oct 28)
- [ ] Implementacja rule-based placement
- [ ] Collision detection
- [ ] Evaluation: spatial feasibility

### Stage 3: Full Pipeline (Week of Nov 4)
- [ ] Połączyć Stage 1 + Stage 2
- [ ] Generowanie różnych wariantów (diversity)
- [ ] Human evaluation

---

## 📝 Notes

### Insert Point Clarification
- **Twoje ustalenie**: Insert point = lewy górny róg bboxa mebla
- **W JSONach**: `"insert_point": [1086.01, 190.01]` to pozycja w układzie pokoju
- **Scale**: Mebel ma `x_scale`, `y_scale` - mnożniki bazowych wymiarów

### SVG Path Background
- **Class**: `<path class="bg">` to obrys mebla
- **Scale**: 1px = 1cm (lub sprawdź współczynnik)
- **Bbox**: Można wyliczyć z path → width/height

### Key Dependencies
```bash
pip install torch transformers datasets
pip install pandas numpy matplotlib seaborn
pip install shapely  # geometric validation
```

---

## 🎯 Current Status

- ✅ Project structure created
- ✅ PRD.md filled out
- ✅ Utility scripts created (`json_processing.py`, `svg_parser.py`, `furniture_catalog.py`)
- ✅ Notebooks prepared (`eda_apartments.ipynb`, `extract_furniture_catalog.ipynb`)
- ⏳ Waiting for sample data upload
- ⏳ EDA to be run
- ⏳ Furniture catalog to be extracted

**Next action**: Upload data to `samples/` and run notebooks! 🚀
