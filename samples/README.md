# Samples Directory

This folder will contain example data for testing and development.

## 📁 Files to Upload Tomorrow:

### 1. Apartment JSONs
Upload a few example apartments (5-10 files):
- ✅ Various room types (bedroom, bathroom, kitchen, living room)
- ✅ Different apartment sizes (M1, M2, M3, M4)
- ✅ With furniture already placed (ground truth)

**Naming convention**: `apartment_001.json`, `apartment_002.json`, etc.

### 2. Furniture Catalog SVG
Upload your SVG file with furniture definitions:
- ✅ Contains `<g id="furniture_id">` groups
- ✅ Each group has `<path class="bg">` with outline
- ✅ Defines all furniture IDs used in apartments

**Expected filename**: `furniture_catalog.svg`

---

## 🎯 What We'll Do With These:

### Apartment JSONs → EDA
Run `notebooks/eda_apartments.ipynb` to:
- Identify all room types
- Extract all furniture IDs used
- Check data quality
- Calculate statistics

### Furniture Catalog SVG → Dimensions
Run `notebooks/extract_furniture_catalog.ipynb` to:
- Parse SVG paths
- Calculate bounding boxes
- Extract width/height for each furniture ID
- Generate `furniture_catalog.json`

---

## 📊 Example Structure:

```
samples/
├── README.md                    (this file)
├── apartment_001.json           (M2 with bedroom + bathroom)
├── apartment_002.json           (M3 with living room + kitchen)
├── apartment_003.json           (M4 larger apartment)
├── ...
├── furniture_catalog.svg        (all furniture definitions)
└── furniture_catalog.json       (generated from SVG)
```

---

## ⚙️ Scale Factor Note:

From your description: **1px = 1cm** in SVG

This is set in `utils/svg_parser.py`:
```python
SVG_SCALE_FACTOR = 1.0  # 1px = 1cm → convert to meters (/100)
```

If the scale is different, update this constant after inspecting the SVG.

---

## 🔒 Privacy Note:

Sample files in this folder are **ignored by git** (see `.gitignore`).
Only commit anonymized examples if needed for documentation.
