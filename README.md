# AI Furnishing Project

Automatic generation of furniture layouts for apartment floor plans.

## Project Structure

```
ai_furnishing_exploration/
├── PRD.md                    # Product Requirements Document
├── notebooks/
│   ├── 0_prototype.ipynb     # Quick zero-shot test (TODO)
│   ├── 1_baseline.ipynb      # Stage 1: Semantic model
│   └── 2_geometric.ipynb     # Stage 2: Placement solver
├── utils/
│   ├── json_processing.py    # Apartment JSON utilities
│   └── furniture_catalog.py  # Furniture dimensions & rules
├── samples/                  # Example inputs/outputs
└── results/                  # Model outputs, visualizations
```

## Approach: Hybrid 2-Stage Pipeline

### Stage 1: Semantic Model (What to place)
- **Input**: Room features (type, area, shape)
- **Output**: List of furniture IDs
- **Model**: Fine-tuned LLM (LLaMA-3-8B)

### Stage 2: Geometric Solver (Where to place)
- **Input**: Furniture IDs + room boundary + furniture dimensions
- **Output**: Insert points, angles, scales
- **Model**: Rule-based (with collision detection) or VAE

## Data Pipeline

Located in `datasets_pipelines/apartment_jsons_pipe/`:

1. **0_scan/**: EDA on raw apartment JSONs
2. **1_collect/**: Extract from database
3. **2_validate/**: Quality checks
4. **3_process/**: Create (empty, furnished) pairs
5. **4_split/**: Train/val/test split

## Key Insights

From initial analysis:
- ~100k apartments with furniture available
- Each apartment has ONE furnished version (ground truth)
- Furniture represented as: `id`, `insert_point`, `angle`, `x_scale`, `y_scale`
- Rooms vary but patterns repeat (many ~rectangular bedrooms)
- LLM should learn semantic pairs: `idBedroom` → `b2` (bed), `sz` (nightstand)
- Geometric placement requires understanding dimensions from SVG catalog

## Next Steps

### ✅ Done (Oct 1, 2025)
1. ✅ Set up project structure
2. ✅ Create utility scripts (`json_processing.py`, `svg_parser.py`, `furniture_catalog.py`)
3. ✅ Prepare notebooks (`eda_apartments.ipynb`, `extract_furniture_catalog.ipynb`)
4. ✅ Document approach in `PRD.md`

### 🔄 Tomorrow (Oct 2, 2025)
1. Upload sample data to `samples/`:
   - 5-10 apartment JSONs
   - Furniture catalog SVG
2. Run `extract_furniture_catalog.ipynb` → generate `furniture_catalog.json`
3. Run `eda_apartments.ipynb` → analyze data
4. Validate SVG scale factor (1px = 1cm?)

### ⏳ Next Week
5. Build full data pipeline (100k apartments)
6. Train Stage 1 (semantic model)
7. Implement Stage 2 (geometric solver)

**See `TODO.md` for detailed checklist!**

## Dependencies

```bash
pip install torch transformers datasets
pip install pandas numpy matplotlib seaborn
pip install shapely  # For geometric validation
```

## References

- PRD: See `PRD.md` for detailed requirements
- Data pipeline: `datasets_pipelines/apartment_jsons_pipe/`
