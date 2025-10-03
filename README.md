# AI Furnishing - Exploration & Planning

**Research repository for automatic furniture placement in apartment floor plans.**

---

## **Purpose of This Repo**

This is an **exploration/planning repository**, NOT production code.

**Goals:**
1. **Understand the problem** - What data do we have? What's the structure?
2. **Analyze the data** - EDA on 503 apartments, furniture schema
3. **Define the approach** - Hybrid 2-Stage Pipeline (Semantic + Geometric)
4. **Document findings** - PRD, schema reference, technical notes
5. **Define next steps** - What to build in production repos

**What happens next:**
- **Dataset preparation** → `datasets_pipelines` repo (collect, validate, process 100k apartments)
- **Model training & inference** → `ai_furnishing` repo (Stage 1 & 2 implementation)

---

## **Current Status (Oct 3, 2025)**

### Completed - Research Phase
- **503 apartments analyzed** (AQU-MAR, MET-ZAC projects)
- **EDA complete** → `results/eda_stats.json`
  - 39 unique furniture IDs
  - 12 room types (idBedroom, idBathroom, idLivingRoomWithAnnex, etc.)
  - ~19.4 furniture items per apartment
  - 100% furniture coverage
- **Furniture schema understood** → `FURNITURE_SCHEMA.md`
  - JSON format with dimensions, collision boundaries, insert_point_type
  - Example furniture: `samples/b1.json`
- **Apartment structure mapped** → `name_cad` = room type
- **Approach defined** → `PRD.md` (Hybrid 2-Stage Pipeline)
- **Utility scripts created** → `utils/` (json_processing, json_furniture_parser)

### 🎯 Next: Move to Production Repos
- **datasets_pipelines**: Build pipeline for 100k apartments
- **ai_furnishing**: Implement Stage 1 (Semantic) + Stage 2 (Geometric)

---

## Repository Structure

```
ai_furnishing_exploration/
├── README.md                         # This file - overview & findings
├── PRD.md                            # Product Requirements Document
├── FURNITURE_SCHEMA.md               # Furniture JSON schema reference
├── samples/
│   ├── apartments/                   # 503 apartment JSONs (confidential)
│   └── b1.json                       # Example furniture definition
├── results/
│   ├── eda_stats.json                # EDA results (503 apartments)
│   └── EDA_ANALYSIS.md               # Detailed analysis & insights
├── utils/                            # Helper scripts (for exploration only)
│   ├── json_processing.py            # Apartment JSON utilities
│   └── json_furniture_parser.py      # Furniture JSON parser
└── notebooks/                        # Jupyter notebooks (EDA, catalog extraction)
    ├── eda_apartments.ipynb
    └── extract_furniture_catalog.ipynb
```

**Note**: `utils/` and `notebooks/` are for exploration only. Production code goes to `datasets_pipelines` and `ai_furnishing` repos.

---

## Chosen Approach: Hybrid 2-Stage Pipeline

**Decision**: Separate semantic (what furniture) from geometric (where to place)

### Stage 1: Semantic Model (What to place)
- **Input**: Room features (room_type, area, perimeter, window_area, boundary)
- **Output**: List of furniture IDs (e.g., `["b22", "sz", "wardrobe"]`)
- **Model**: Fine-tuned LLM (LLaMA-3-8B) or rule-based
- **Training data**: ~2,220 rooms from 503 apartments

### Stage 2: Geometric Solver (Where to place)
- **Input**: Furniture IDs + room boundary + furniture catalog (dimensions, collision boundaries)
- **Output**: Insert points, angles, scales for each furniture
- **Model**: Rule-based with collision detection (initially), VAE/Diffusion (advanced)
- **Key features**: 
  - Respect `insert_point_type` (wall_based, universal, standalone, opening)
  - Check collisions using `clash_detection_boundary`
  - Validate `access_area_boundary` (optional)
  - Handle `layer_index` for 3D collision (future)

**Why this separation?**
- LLMs excel at patterns/semantics but poor at precise geometry
- Enables independent debugging and optimization
- Can swap Stage 2 implementation without retraining Stage 1

## Key Findings

### Data Availability
- **~100k apartments** with furniture in database (confidential)
- **503 apartments** analyzed in this repo (sample from 2 projects: AQU-MAR, MET-ZAC)
- **Furniture catalog** exists as JSON files (confidential, 1 example: `b1.json`)
- **100% ground truth** - all apartments have furniture placements

### Data Structure

**Apartments** (`compartments[]`):
```json
{
  "name_cad": "idBedroom",           // Room type
  "area": 12.5,
  "perimeter": 14.2,
  "boundary": [[x,y], ...],          // Room polygon
  "window_area": 1.8,
  "equipments": [                    // Placed furniture
    {
      "id": "b22",                   // Furniture ID
      "insert_point": [485.42, 365.0],
      "angle": 90,
      "x_scale": 1,
      "y_scale": 0.89               // Furniture can be scaled!
    }
  ],
  "caseworks": [...]                // Kitchen furniture (special)
}
```

**Furniture** (JSON files):
```json
{
  "id": "b1",
  "block_id": "APLUS_LOZKO_POJEDYNCZE",  // Human-readable name
  "category": "basic",                    // sanitary, basic, door, window, etc.
  "insert_point_type": "universal",       // wall_based, universal, opening, standalone
  "layer_index": 2,                       // 1-6 (floor to ceiling, for 3D collision)
  "default_x_length": 200,                // Width in cm
  "default_y_length": 100,                // Height in cm
  "clash_detection_boundary": [[x,y]...], // Collision polygon (relative to insert_point)
  "access_area_boundary": [[x,y]...],     // Required clearance (can be null)
  "in_compartments": ["idBedroom", ...]   // Room restrictions (can be null)
}
```

**See**: `FURNITURE_SCHEMA.md` for complete reference

### Semantic Patterns (from 503 apartments)

Top furniture by room type:
- **idBedroom** → `sz` (wardrobe, 1212×), `b22` (double bed, 328×)
- **idBathroom** → `wc2`/`wcg` (toilet, 493×), `wb` (basin, 509×), `sh` (shower, 190×)
- **idLivingRoomWithAnnex** → `kitchenette` (891×), `stv`/`tvo` (TV stand, 450×), `st` (table, 334×)

**Universal items**: `fr` (fridge, 503×), `sip` (sink, 503×) - in EVERY apartment!

→ **Polish apartments are highly standardized** - Stage 1 semantic model will be very accurate!

## Next Steps - Production Implementation

**Research phase COMPLETE** - Now move to production repos:

### 1. Dataset Pipeline (`datasets_pipelines` repo)
**Goal**: Process 100k apartments into training data

**Tasks**:
- Extract all apartments from database
- Validate data quality (required fields, boundaries)
- Create (empty, furnished) training pairs
- Generate per-room training examples: `room_features → furniture_ids`
- Train/val/test split (80/10/10, stratified by apartment type)

**Output**: 
- `training_pairs.json` (~80k apartments → ~320k room examples)
- `validation_pairs.json` (~10k apartments)
- `test_pairs.json` (~10k apartments)

**Note**: Fix `room_type` extraction → use `name_cad` field

---

### 2. AI Furnishing (`ai_furnishing` repo)
**Goal**: Train and deploy Stage 1 + Stage 2 models

**Stage 1 Tasks**:
- Option A: Rule-based baseline (semantic mappings from EDA)
- Option B: Fine-tune LLaMA-3-8B on training pairs
- Evaluation: semantic correctness (95%+ target)

**Stage 2 Tasks**:
- Implement geometric solver with collision detection
- Use `clash_detection_boundary` from furniture catalog
- Handle `insert_point_type` variants (wall_based, universal, standalone)
- Account for `x_scale`, `y_scale` in placement
- Evaluation: spatial feasibility (90%+ non-colliding target)

**Integration**:
- Connect Stage 1 → Stage 2 pipeline
- Generate multiple diverse arrangements per apartment
- Human evaluation: 70%+ acceptance rate

---

## Documentation Reference

- **`PRD.md`** - Complete project requirements, metrics, timeline
- **`FURNITURE_SCHEMA.md`** - Furniture JSON schema with all fields explained
- **`results/EDA_ANALYSIS.md`** - Detailed analysis of 503 apartments
- **`results/eda_stats.json`** - Statistics (room types, furniture IDs, frequencies)

---

## Success Metrics (from PRD)

### Semantic Correctness (Stage 1)
- **Target**: 95%+ furniture IDs valid for room type
- **Baseline**: Rule-based from EDA patterns (should hit 90%+)

### Spatial Feasibility (Stage 2)
- **Target**: 90%+ placements without collisions
- **Method**: Collision detection using `clash_detection_boundary`

### Diversity
- **Target**: 5+ distinct arrangements per apartment
- **Method**: Randomize placement order, angles, positions

### Human Acceptance
- **Target**: 70%+ layouts acceptable to designers
- **Method**: Manual review of 50-100 generated apartments

---

## Key Learnings

1. **Furniture as JSON** >> SVG parsing - structured data with dimensions and boundaries
2. **Scale factors matter** - `x_scale`, `y_scale` ≠ 1 means furniture is resized
3. **Caseworks are special** - `kitchenette` has `countertop_boundary`, handle separately
4. **Polish apartments standardized** - every apt has fridge+sink, bedrooms have wardrobes
5. **Layer index enables 3D** - chair (layer 2) can go under table (layer 3)
6. **Room adjacency available** - `doors[]` with `from_room`/`to_room` for advanced constraints

---

## Related Repositories

- **`datasets_pipelines`** - Data collection, validation, processing (100k apartments)
- **`ai_furnishing`** - Model training, inference, deployment (Stage 1 & 2)
- **`ai_furnishing_exploration`** - This repo (research, planning, EDA)
