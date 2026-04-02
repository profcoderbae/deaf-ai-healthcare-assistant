"""Generate a professional PDF CV from structured data using fpdf2."""

from fpdf import FPDF

class CVPDF(FPDF):
    def header(self):
        pass  # No header needed

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Charlie Nghondzweni | Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(30, 80, 120)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 80, 120)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def sub_heading(self, text):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(40, 40, 40)
        self.cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")

    def detail_line(self, text):
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, text, new_x="LMARGIN", new_y="NEXT")

    def body_text(self, text):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 4.8, text)

    def bullet(self, text):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(50, 50, 50)
        x0 = self.get_x()
        self.cell(5, 4.8, "-")
        w = self.w - self.r_margin - self.get_x()
        self.multi_cell(w, 4.8, text)
        self.set_x(x0)

    def tech_line(self, label, value):
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(50, 50, 50)
        x0 = self.get_x()
        w_label = 32
        self.cell(w_label, 5, label + ":")
        self.set_font("Helvetica", "", 9.5)
        w_value = self.w - self.r_margin - self.get_x()
        self.multi_cell(w_value, 5, value)
        # reset x for next line
        self.set_x(x0)

    def add_link_line(self, label, url):
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(50, 50, 50)
        self.cell(28, 5, label + ": ")
        self.set_text_color(30, 80, 180)
        self.set_font("Helvetica", "U", 9.5)
        self.cell(0, 5, url, link=url, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(50, 50, 50)


def build_cv():
    pdf = CVPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_margins(18, 15, 18)

    # ── Name & Title ──
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, "Charlie Nghondzweni", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 6, "Data Analyst  |  Data Engineer  |  Agricultural Data Science", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # ── Contact ──
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 5, "0714482318  |  charlienghondzweni9@gmail.com  |  linkedin.com/in/charlienghondzweni-b01693181  |  github.com/profcoderbae", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # ── Professional Summary ──
    pdf.section_title("Professional Summary")
    pdf.body_text(
        "Data analyst and engineer with 3+ years of experience building data pipelines, analytical dashboards, "
        "and automation solutions across water, consulting, and energy sectors. Proficient in Python, SQL, and Power BI "
        "with hands-on experience in ETL pipeline development, data warehousing, and statistical analysis. Demonstrated "
        "ability to work with biological and agricultural datasets through portfolio projects in breeding data management, "
        "genomic selection, and field trial analytics. Experienced in translating complex data into actionable insights "
        "for diverse stakeholders."
    )
    pdf.ln(4)

    # ── Technical Skills ──
    pdf.section_title("Technical Skills")
    skills = [
        ("Languages", "Python (NumPy, Pandas, SciPy, scikit-learn), SQL, R (basic), C++, Java"),
        ("Data Engineering", "ETL pipelines, SSIS, data warehousing, SQLite, SQL Server, database design"),
        ("Analytics & Viz", "Power BI, Tableau, Streamlit, matplotlib, seaborn, Plotly"),
        ("Cloud & Big Data", "Microsoft Azure, Hadoop (HDFS, YARN, Spark), AWS"),
        ("Quant Methods", "Mixed models (BLUP/BLUE), heritability, genomic selection, QA/QC validation"),
        ("Tools", "Git, Docker, Flask, Microsoft Office, SharePoint"),
    ]
    for label, value in skills:
        pdf.tech_line(label, value)
    pdf.ln(4)

    # ── Experience ──
    pdf.section_title("Professional Experience")

    # Enel
    pdf.sub_heading("Data Analyst & Automation Engineer")
    pdf.detail_line("Enel Green Power  |  Johannesburg  |  March 2026 - Present")
    pdf.ln(1)
    for b in [
        "Design and implement automated data processing workflows for renewable energy operations",
        "Build data pipelines and analytical solutions supporting business decision-making",
    ]:
        pdf.bullet(b)
    pdf.ln(3)

    # LRMG
    pdf.sub_heading("Data Analyst")
    pdf.detail_line("LRMG  |  Johannesburg  |  June 2024 - March 2026")
    pdf.ln(1)
    for b in [
        "Designed and built ETL pipelines using SSIS to ingest, clean, and transform survey data from Microsoft Forms into SQL Server",
        "Developed interactive Power BI dashboards for client feedback analysis including NPS trends, risk identification, and financial reporting",
        "Produced weekly insight reports highlighting client relationship metrics and business performance trends",
        "Built and optimized big data infrastructure components (YARN, HDFS, Spark) in a development environment",
        "Managed cloud-based data solutions using Microsoft Azure for enhanced storage and analytics",
    ]:
        pdf.bullet(b)
    pdf.ln(3)

    # Rand Water
    pdf.sub_heading("Junior Data Analyst")
    pdf.detail_line("Rand Water  |  Glenvista, Gauteng  |  February 2023 - May 2024")
    pdf.ln(1)
    for b in [
        "Extracted and analyzed large datasets using complex SQL queries for operational insights",
        "Designed and deployed Power BI dashboards for real-time water infrastructure monitoring",
        "Automated data processing workflows and statistical analysis using Python",
        "Created Tableau stories communicating data-driven narratives to non-technical stakeholders",
    ]:
        pdf.bullet(b)
    pdf.ln(3)

    # Luigi
    pdf.sub_heading("Frontend Web Developer")
    pdf.detail_line("Luigi Corporation  |  Tzaneen, Limpopo  |  October 2020 - January 2022")
    pdf.ln(1)
    pdf.bullet("Developed and maintained client-facing web applications")
    pdf.ln(4)

    # ── Education ──
    pdf.section_title("Education")

    for degree, school, dates in [
        ("Master's degree, Computer Science", "North-West University", "February 2023 - Present"),
        ("BSc Honours, Computer Science", "North-West University", "March 2022 - November 2022"),
        ("BSc Computer Science & Electronics", "North-West University", "February 2018 - December 2021"),
    ]:
        pdf.sub_heading(degree)
        pdf.detail_line(f"{school}  |  {dates}")
        pdf.ln(2)
    pdf.ln(2)

    # ── Certifications ──
    pdf.section_title("Certifications")
    for cert in [
        "Tableau Desktop Specialist",
        "Tableau Data Analyst Certificate (School of IT)",
        "Tableau Developer Certificate (School of IT)",
        "Introduction to Big Data and Spark",
        "Analyzing Data Using Python: Data Analytics Using Pandas",
    ]:
        pdf.bullet(cert)
    pdf.ln(4)

    # ═══════════════════════════════════════════
    # ── Portfolio Projects ──
    # ═══════════════════════════════════════════
    pdf.section_title("Portfolio Projects")

    # ── Project 1: Breeding Data Pipeline ──
    pdf.sub_heading("1. Breeding Data Pipeline")
    pdf.detail_line("ETL pipeline for subtropical fruit breeding trial data management")
    pdf.ln(1)
    pdf.set_font("Helvetica", "BI", 9)
    pdf.set_text_color(30, 80, 120)
    pdf.cell(0, 5, "Relevance: Database management, data collection, QA/QC - core responsibilities of breeding data operations.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    for b in [
        "Built end-to-end Python ETL pipeline for mango and citrus breeding trial data across 4 field sites, 3 seasons, and 150+ genotypes",
        "Implemented comprehensive QA/QC validation engine: range checks, IQR-based outlier detection, missing data analysis, evaluator bias detection, and cross-field consistency checks",
        "Designed normalized SQLite relational database schema for multi-year trial storage with full audit trail",
        "Generated automated QA/QC reports with publication-quality visualizations (missing data heatmaps, trait distributions, site comparison scatter plots, evaluator scoring analysis)",
        "Wrote configurable YAML-based validation rules and 10 unit tests with pytest (all passing)",
    ]:
        pdf.bullet(b)
    pdf.ln(1)
    pdf.tech_line("Tech", "Python (Pandas, NumPy, SciPy), SQLite, matplotlib, seaborn, PyYAML, pytest")
    pdf.ln(3)

    # ── Project 2: Genomic Selection Pipeline ──
    pdf.sub_heading("2. Genomic Selection Pipeline")
    pdf.detail_line("End-to-end genomic prediction pipeline for subtropical fruit breeding")
    pdf.ln(1)
    pdf.set_font("Helvetica", "BI", 9)
    pdf.set_text_color(30, 80, 120)
    pdf.cell(0, 5, "Relevance: Molecular breeding tools, genomic selection, genotype-phenotype integration.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    for b in [
        "Developed SNP quality control pipeline: MAF filtering, Hardy-Weinberg equilibrium testing, missing data rate filtering (5,000 to 4,804 markers after QC)",
        "Computed Genomic Relationship Matrix (GRM) using VanRaden Method 1 and PCA-based population structure analysis",
        "Estimated narrow-sense heritability (h2) across 5 traits using Haseman-Elston regression",
        "Implemented Henderson's Mixed Model Equations for BLUP breeding value prediction with reliability estimation",
        "Built and compared 3 genomic selection models (rrBLUP, LASSO, Elastic Net) with 5-fold cross-validation achieving prediction accuracy r = 0.66",
        "Created multi-trait selection index with economic weighting for crossing decisions",
    ]:
        pdf.bullet(b)
    pdf.ln(1)
    pdf.tech_line("Tech", "Python (NumPy, SciPy, scikit-learn), linear algebra, cross-validation")
    pdf.ln(3)

    # ── Project 3: Field Trial Dashboard ──
    pdf.sub_heading("3. Field Trial Analytics Dashboard")
    pdf.detail_line("Interactive Streamlit dashboard for breeder decision support")
    pdf.ln(1)
    pdf.set_font("Helvetica", "BI", 9)
    pdf.set_text_color(30, 80, 120)
    pdf.cell(0, 5, "Relevance: Breeder-friendly analytics, dashboards, visualizations, training field staff.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    for b in [
        "Built interactive 5-page Streamlit dashboard for mango breeding trial data (200 genotypes, 4 seasons, 3 sites)",
        "Implemented genotype ranking, family/cross performance analysis, and advancement stage tracking (Seedling to Elite)",
        "Developed Finlay-Wilkinson GxE stability analysis to identify broadly adapted genotypes",
        "Created interactive multi-trait selection tool with adjustable weight sliders, selection gain visualization, and CSV export",
    ]:
        pdf.bullet(b)
    pdf.ln(1)
    pdf.tech_line("Tech", "Python, Streamlit, Plotly, Pandas, SciPy")
    pdf.ln(3)

    # ── Project 4: Hackathon ──
    pdf.sub_heading("4. Deaf AI Healthcare Assistant (Hackathon Project)")
    pdf.detail_line("AI-powered healthcare communication system for deaf patients at Tygerberg Hospital")
    pdf.ln(1)
    pdf.set_font("Helvetica", "BI", 9)
    pdf.set_text_color(30, 80, 120)
    pdf.cell(0, 5, "Relevance: Full-stack development, real-time ML inference, team collaboration, production deployment.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    for b in [
        "Built a two-part AI system enabling bidirectional communication between deaf patients and medical staff",
        "AI Kiosk Chatbot: Animated avatar guides patients through triage using sign language or text, assigns departments, generates QR directions",
        "Real-Time Translator: Patient signs detected via camera (MediaPipe + custom ML), converted to text/speech; doctor speech converted to avatar signing",
        "Integrated Groq LLM (Llama 3.1) for sentence cleanup and symptom analysis; deployed on Render.com using Docker",
        "South African Sign Language (SASL) gesture mappings - accessible via any browser with a webcam",
    ]:
        pdf.bullet(b)
    pdf.ln(1)
    pdf.tech_line("Tech", "Python, Flask, SocketIO, MediaPipe, TensorFlow/Keras, Groq AI, Docker")
    pdf.add_link_line("Live Demo", "https://deaf-ai-healthcare-assistant.onrender.com")
    pdf.add_link_line("GitHub", "https://github.com/profcoderbae/deaf-ai-healthcare-assistant")
    pdf.ln(4)

    # ── Key Strengths ──
    pdf.section_title("Key Strengths for Breeding Data Operations")
    for b in [
        "Field + Analytics Bridge: Experience collecting, cleaning, and analyzing real-world operational data - comfortable switching between fieldwork and data management",
        "Database & Pipeline Design: Proven ETL pipeline builder (SSIS, Python, SQL Server) now applied to breeding database management",
        "Breeder-Friendly Reporting: Track record of translating complex analytics into clear dashboards and reports for non-technical stakeholders",
        "Quantitative Genetics: Working knowledge of BLUP/BLUE, heritability, genomic selection, GxE analysis, and selection indices",
        "Proactive & Detail-Oriented: QA/QC validation, outlier detection, and data completeness checks built into every pipeline",
    ]:
        pdf.bullet(b)

    # ── Save ──
    output_path = r"c:\Users\tedex\OneDrive\Documents\Deaf AI asistance\portfolio_projects\Charlie_Nghondzweni_CV.pdf"
    pdf.output(output_path)
    print(f"PDF saved to: {output_path}")


if __name__ == "__main__":
    build_cv()
