# Charlie Nghondzweni

**Data Analyst | Data Engineer | Agricultural Data Science**

📱 0714482318 | ✉️ charlienghondzweni9@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/charlienghondzweni-b01693181)  
🔗 [GitHub](https://github.com/profcoderbae)

---

## Professional Summary

Data analyst and engineer with 3+ years of experience building data pipelines, analytical dashboards, and automation solutions across water, consulting, and energy sectors. Proficient in Python, SQL, and Power BI with hands-on experience in ETL pipeline development, data warehousing, and statistical analysis. Demonstrated ability to work with biological and agricultural datasets through portfolio projects in breeding data management, genomic selection, and field trial analytics. Experienced in translating complex data into actionable insights for diverse stakeholders.

---

## Technical Skills

| Category | Technologies |
|----------|-------------|
| **Languages** | Python (NumPy, Pandas, SciPy, scikit-learn), SQL, R (basic), C++, Java |
| **Data Engineering** | ETL pipelines, SSIS, data warehousing, SQLite, SQL Server, database design |
| **Analytics & Visualization** | Power BI, Tableau, Streamlit, matplotlib, seaborn, Plotly |
| **Cloud & Big Data** | Microsoft Azure, Hadoop (HDFS, YARN, Spark), AWS |
| **Quantitative Methods** | Mixed models (BLUP/BLUE), heritability estimation, genomic selection, QA/QC validation |
| **Tools** | Git, Docker, Flask, Microsoft Office, SharePoint |

---

## Professional Experience

### Data Analyst & Automation Engineer
**Enel Green Power** | Johannesburg | March 2026 – Present

- Design and implement automated data processing workflows for renewable energy operations
- Build data pipelines and analytical solutions supporting business decision-making

### Data Analyst
**LRMG** | Johannesburg | June 2024 – March 2026

- Designed and built ETL pipelines using SSIS to ingest, clean, and transform survey data from Microsoft Forms into SQL Server
- Developed interactive Power BI dashboards for client feedback analysis including NPS trends, risk identification, and financial reporting
- Produced weekly insight reports highlighting client relationship metrics and business performance trends
- Built and optimized big data infrastructure components (YARN, HDFS, Spark) in a development environment
- Managed cloud-based data solutions using Microsoft Azure for enhanced storage and analytics

### Junior Data Analyst
**Rand Water** | Glenvista, Gauteng | February 2023 – May 2024

- Extracted and analyzed large datasets using complex SQL queries for operational insights
- Designed and deployed Power BI dashboards for real-time water infrastructure monitoring
- Automated data processing workflows and statistical analysis using Python
- Created Tableau stories communicating data-driven narratives to non-technical stakeholders

### Frontend Web Developer
**Luigi Corporation** | Tzaneen, Limpopo | October 2020 – January 2022

- Developed and maintained client-facing web applications

---

## Education

**Master's degree, Computer Science**  
North-West University | February 2023 – Present

**BSc Honours, Computer Science**  
North-West University | March 2022 – November 2022

**BSc Computer Science & Electronics**  
North-West University | February 2018 – December 2021

---

## Certifications

- Tableau Desktop Specialist
- Tableau Data Analyst Certificate (School of IT)
- Tableau Developer Certificate (School of IT)
- Introduction to Big Data and Spark
- Analyzing Data Using Python: Data Analytics Using Pandas

---

## Portfolio Projects

### 1. Breeding Data Pipeline
*ETL pipeline for subtropical fruit breeding trial data management*

**Relevance:** Database management, data collection, QA/QC — core responsibilities of breeding data operations.

- Built end-to-end Python ETL pipeline for mango and citrus breeding trial data across 4 field sites, 3 seasons, and 150+ genotypes
- Implemented comprehensive QA/QC validation engine: range checks, IQR-based outlier detection, missing data analysis, evaluator bias detection, and cross-field consistency checks
- Designed normalized SQLite relational database schema for multi-year trial storage with full audit trail
- Generated automated QA/QC reports with publication-quality visualizations (missing data heatmaps, trait distributions, site comparison scatter plots, evaluator scoring analysis)
- Wrote configurable YAML-based validation rules and 10 unit tests with pytest

**Tech:** Python (Pandas, NumPy, SciPy), SQLite, matplotlib, seaborn, PyYAML, pytest  
**GitHub:** [portfolio_projects/breeding-data-pipeline](https://github.com/profcoderbae/deaf-ai-healthcare-assistant/tree/master/portfolio_projects/breeding-data-pipeline)

---

### 2. Genomic Selection Pipeline
*End-to-end genomic prediction pipeline for subtropical fruit breeding*

**Relevance:** Molecular breeding tools, genomic selection, genotype-phenotype integration — directly supports trait discovery and predictive modeling.

- Developed SNP quality control pipeline: MAF filtering, Hardy-Weinberg equilibrium testing, and missing data rate filtering (5,000 → 4,804 markers after QC)
- Computed Genomic Relationship Matrix (GRM) using VanRaden Method 1 and performed PCA-based population structure analysis
- Estimated narrow-sense heritability (h²) across 5 traits using Haseman-Elston regression
- Implemented Henderson's Mixed Model Equations for BLUP breeding value prediction with reliability estimation
- Built and compared 3 genomic selection models (rrBLUP, LASSO, Elastic Net) with 5-fold cross-validation achieving prediction accuracy r = 0.66
- Created multi-trait selection index with economic weighting for crossing decisions
- Generated publication-quality visualizations: PCA plots, GRM heatmaps, GEBV distributions, marker effect Manhattan plots

**Tech:** Python (NumPy, SciPy, scikit-learn), linear algebra, cross-validation  
**GitHub:** [portfolio_projects/genomic-selection-pipeline](https://github.com/profcoderbae/deaf-ai-healthcare-assistant/tree/master/portfolio_projects/genomic-selection-pipeline)

---

### 3. Field Trial Analytics Dashboard
*Interactive Streamlit dashboard for breeder decision support*

**Relevance:** Breeder-friendly analytics, dashboards, visualizations, and training field staff in data interpretation.

- Built interactive 5-page Streamlit dashboard for mango breeding trial data (200 genotypes, 4 seasons, 3 sites)
- Implemented genotype ranking, family/cross performance analysis, and advancement stage tracking (Seedling → Elite)
- Developed Finlay-Wilkinson GxE stability analysis to identify broadly adapted genotypes
- Created interactive multi-trait selection tool with adjustable weight sliders, selection gain visualization, and CSV export for field use
- Designed Plotly interactive visualizations: trait distributions, site comparisons, trait correlation heatmaps, evaluator comparisons

**Tech:** Python, Streamlit, Plotly, Pandas, SciPy  
**GitHub:** [portfolio_projects/field-trial-dashboard](https://github.com/profcoderbae/deaf-ai-healthcare-assistant/tree/master/portfolio_projects/field-trial-dashboard)

---

### 4. Deaf AI Healthcare Assistant (Hackathon Project)
*AI-powered healthcare communication system for deaf patients*

**Relevance:** Demonstrates full-stack development, real-time ML inference, team collaboration, and deploying production systems.

- Built a two-part AI system for Tygerberg Hospital enabling communication between deaf patients and medical staff
- **AI Kiosk Chatbot ("Thandi"):** Animated avatar guides deaf patients through triage using sign language or text, identifies symptoms, assigns departments, and generates QR-coded directions
- **Real-Time Sign Language Translator:** Bidirectional translation — patient signs detected via camera (MediaPipe + custom ML models), converted to text/speech for doctors; doctor's speech converted to animated avatar signing for patients
- Integrated Groq LLM (Llama 3.1) for AI sentence cleanup ("pain head bad" → "I have a bad headache") and symptom analysis
- Deployed as a containerized web app on Render.com using Docker, accessible via any browser with a webcam
- South African Sign Language (SASL) gesture mappings — not just ASL

**Tech:** Python, Flask, SocketIO, MediaPipe, TensorFlow/Keras, Groq AI, SQLite, Docker, Tailwind CSS  
**Live Demo:** [deaf-ai-healthcare-assistant.onrender.com](https://deaf-ai-healthcare-assistant.onrender.com)  
**GitHub:** [profcoderbae/deaf-ai-healthcare-assistant](https://github.com/profcoderbae/deaf-ai-healthcare-assistant)

---

## Other Experience

**Tutor** | North-West University | Aug 2022 – Nov 2022  
Assisted second-year Computer Science students with C++ structural programming.

**Private Tutor** | Matende X Education Foundation | Mar 2022 – Sep 2022  
Tutored Computer Science students in Java and C++ programming.

**Field Worker** | Statistics South Africa | Feb 2022 – Mar 2022  
Enumerated households and captured demographic/living condition data during census.

---

## Key Strengths for Breeding Data Operations

- **Field + Analytics Bridge:** Experience collecting, cleaning, and analyzing real-world operational data — comfortable switching between fieldwork and data management
- **Database & Pipeline Design:** Proven ETL pipeline builder (SSIS, Python, SQL Server) now applied to breeding database management
- **Breeder-Friendly Reporting:** Track record of translating complex analytics into clear dashboards and reports for non-technical stakeholders
- **Quantitative Genetics:** Portfolio demonstrates working knowledge of BLUP/BLUE, heritability, genomic selection, GxE analysis, and selection indices
- **Proactive & Detail-Oriented:** QA/QC validation, outlier detection, and data completeness checks built into every pipeline
