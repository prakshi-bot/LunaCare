# LunaCare Curated Female Health Knowledge Base
================================================

This directory houses verified female-health documents to be indexed by Chroma in Phase 3.

Folders:
- `menstrual_health/`: Menstrual cycle biology, dysmenorrhea (cramps), flow tracking.
- `menstrual_hygiene/`: Product safety (pads, tampons, cups), toxic shock syndrome (TSS) prevention, vulvar care.
- `PCOS/`: Polycystic Ovary Syndrome diagnostic criteria (Rotterdam), insulin sensitivity, lifestyle interventions.
- `reproductive_health/`: Cervical screening, Pap smears, HPV awareness, pelvic floor health.
- `pregnancy/`: Prenatal vitamins (folic acid), first-trimester nutrition, gestational warnings.
- `wellness/`: Stress management, cortisol-ovary axis, PMDD/PMS mental wellness.
- `general_womens_health/`: Bone density, iron deficiency, cardiovascular health.

Supported formats: PDF (`.pdf`) and Text (`.txt`).
In Phase 3, running `python ingest.py` will read these directories, split text into chunks, generate embeddings, and populate `vector_store/`.
