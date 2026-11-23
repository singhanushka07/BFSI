"""
Generates 3 realistic synthetic financial PDFs for ChromaDB RAG pre-loading.
Pure-Python PDF writer — no fpdf2 or reportlab required.
"""
import os

SAMPLE_PDF_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_pdfs")


class MinimalPDF:
    """Minimal PDF 1.4 writer: multi-page, text only, Helvetica built-in font."""

    def __init__(self, title: str):
        self.title = title
        self.pages: list[list[str]] = []
        self._cur: list[str] = []
        self._new_page()

    def _new_page(self):
        if self._cur:
            self.pages.append(self._cur)
        self._cur = []

    def _esc(self, text: str) -> str:
        return (text
                .replace("\\", "\\\\")
                .replace("(", "\\(")
                .replace(")", "\\)")
                .replace("\r", ""))

    def _wrap(self, text: str, max_chars: int = 93) -> list[str]:
        words = text.split()
        lines, line = [], []
        for w in words:
            if sum(len(x) + 1 for x in line) + len(w) <= max_chars:
                line.append(w)
            else:
                if line:
                    lines.append(" ".join(line))
                line = [w]
        if line:
            lines.append(" ".join(line))
        return lines or [""]

    def title_line(self, text: str, y: float):
        self._cur.extend([
            "BT", "/F2 12 Tf",
            f"0.1 0.35 0.75 rg",
            f"50 {y:.1f} Td",
            f"({self._esc(text)}) Tj",
            "0 0 0 rg", "ET",
        ])

    def section(self, heading: str, y: float) -> float:
        self._cur.extend([
            "BT", "/F2 10.5 Tf",
            "0.1 0.35 0.75 rg",
            f"50 {y:.1f} Td",
            f"({self._esc(heading)}) Tj",
            "0 0 0 rg", "ET",
        ])
        return y - 15

    def body(self, text: str, y: float) -> float:
        for line in self._wrap(text):
            if y < 60:
                self._new_page()
                y = 735
            self._cur.extend([
                "BT", "/F1 9 Tf",
                "0.18 0.2 0.27 rg",
                f"50 {y:.1f} Td",
                f"({self._esc(line)}) Tj",
                "0 0 0 rg", "ET",
            ])
            y -= 12
        return y - 3

    def kv(self, label: str, value: str, y: float) -> float:
        if y < 60:
            self._new_page()
            y = 735
        self._cur.extend([
            "BT", "/F2 9 Tf",
            "0.25 0.25 0.35 rg",
            f"50 {y:.1f} Td",
            f"({self._esc(label + ':')}  ) Tj",
            "/F1 9 Tf",
            "0.1 0.1 0.15 rg",
            f"({self._esc(value)}) Tj",
            "0 0 0 rg", "ET",
        ])
        return y - 13

    def build(self) -> bytes:
        if self._cur:
            self.pages.append(self._cur)
            self._cur = []

        n = len(self.pages)
        page_ids = list(range(3, 3 + n))
        f1_id = 3 + n
        f2_id = 4 + n
        cont_ids = list(range(5 + n, 5 + 2 * n))

        all_objs = []

        # 1: catalog
        all_objs.append(f"<< /Type /Catalog /Pages 2 0 R >>".encode())
        # 2: pages
        kids = " ".join(f"{p} 0 R" for p in page_ids)
        all_objs.append(f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode())
        # page objects
        for pid, cid in zip(page_ids, cont_ids):
            all_objs.append((
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 {f1_id} 0 R /F2 {f2_id} 0 R >> >> "
                f"/Contents {cid} 0 R >>"
            ).encode())
        # fonts
        all_objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
        all_objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
        # content streams
        for page_ops in self.pages:
            raw = "\n".join(page_ops).encode("latin-1", errors="replace")
            all_objs.append(f"<< /Length {len(raw)} >>\nstream\n".encode() + raw + b"\nendstream")

        pdf = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
        offsets = []
        for i, content in enumerate(all_objs):
            offsets.append(len(pdf))
            pdf += f"{i + 1} 0 obj\n".encode() + content + b"\nendobj\n"

        xref_pos = len(pdf)
        xref = f"xref\n0 {len(all_objs) + 1}\n0000000000 65535 f \n"
        for off in offsets:
            xref += f"{off:010d} 00000 n \n"
        pdf += xref.encode()
        pdf += f"trailer\n<< /Size {len(all_objs) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
        return pdf


def _save(pdf: MinimalPDF, filename: str) -> str:
    os.makedirs(SAMPLE_PDF_DIR, exist_ok=True)
    path = os.path.join(SAMPLE_PDF_DIR, filename)
    with open(path, "wb") as f:
        f.write(pdf.build())
    return path


def generate_techcorp_annual_report() -> str:
    p = MinimalPDF("TechCorp Global Annual Report 2024")
    y = 740
    p.title_line("TechCorp Global (NASDAQ: TCG) — Annual Report 2024", y); y -= 30

    y = p.section("Executive Summary", y)
    y = p.body("TechCorp Global reports total revenue of $18.4 billion for fiscal year ended December 31, 2024, "
               "representing 7.2% year-over-year growth. Net income reached $2.1 billion (margin 11.4%). "
               "Despite strong performance, management acknowledges heightened market volatility and geopolitical "
               "risks that may impact future earnings. The Board approved a $500 million share buyback program.", y)

    y = p.section("Financial Highlights", y)
    y = p.kv("Total Revenue", "$18.4 billion (FY2024) vs $17.2 billion (FY2023)", y)
    y = p.kv("Net Income", "$2.1 billion — Net Margin 11.4%", y)
    y = p.kv("Total Assets", "$54.7 billion", y)
    y = p.kv("Total Debt", "$12.3 billion", y)
    y = p.kv("Total Equity", "$31.8 billion", y)
    y = p.kv("Debt-to-Equity Ratio", "0.39 — moderate leverage", y)
    y = p.kv("Current Ratio", "1.87 — adequate short-term liquidity", y)
    y = p.kv("Return on Equity (ROE)", "6.6% — below sector median of 12%", y)
    y = p.kv("Return on Assets (ROA)", "3.8%", y)
    y = p.kv("Earnings Per Share (EPS)", "$4.32 diluted", y)
    y = p.kv("Free Cash Flow", "$3.2 billion", y); y -= 5

    y = p.section("Market Risk", y)
    y = p.body("TechCorp Global is exposed to significant market risk from fluctuations in interest rates, foreign "
               "currency exchange rates, and equity market valuations. The company 30-day annualized stock volatility "
               "stands at 34%, above the sector average of 22%. A 100 basis point interest rate increase would raise "
               "annual interest expense by approximately $123 million given variable-rate debt exposure. Beta of 1.42 "
               "indicates above-market systematic risk. VaR at 95% confidence stands at 5.8% daily, implying potential "
               "single-day losses exceeding $1.07 billion at current market cap with 5% probability.", y)

    y = p.section("Liquidity and Financial Risk", y)
    y = p.body("Total debt of $12.3 billion includes $3.1 billion maturing within 12 months, requiring refinancing "
               "under potentially unfavorable market conditions. Leverage ratio Net Debt/EBITDA of 2.1x remains within "
               "covenant thresholds but leaves limited headroom should EBITDA decline more than 15%. Accounts receivable "
               "days outstanding increased to 58 days from 49 days. Inventory write-downs of $287 million recorded due "
               "to product obsolescence.", y)

    y = p.section("Regulatory and Compliance Risk", y)
    y = p.body("TechCorp operates across 47 jurisdictions under GDPR, CCPA, and sector-specific data protection laws. "
               "Formal inquiries from three regulatory bodies regarding data handling, with potential fines $150M-$800M. "
               "SOX Section 404 identified two material weaknesses in ICFR related to IT access controls and revenue "
               "recognition for multi-element arrangements. AML screening infrastructure upgraded at cost of $45 million "
               "following regulatory guidance on enhanced due diligence requirements.", y)

    y = p.section("Operational and Sentiment Risk", y)
    y = p.body("Recent media coverage: 38% negative sentiment driven by executive departures and supply chain disruptions. "
               "CFO and Chief Risk Officer both departed Q3 2024, creating uncertainty regarding financial strategy and "
               "risk governance. Customer satisfaction scores declined 8 percentage points year-over-year. ESG rating "
               "downgraded by two major rating agencies. Supply chain concentration risk elevated with 62% of critical "
               "components sourced from single geographic region.", y)

    y = p.section("FY2025 Outlook", y)
    y = p.body("Management provides FY2025 guidance of $19.0-$19.8 billion in revenue. Capital expenditure projected at "
               "$2.8 billion. The company maintains $4.1 billion in unrestricted cash and $5.0 billion available credit "
               "facilities. Failure to remediate internal control weaknesses, resolve regulatory inquiries, or refinance "
               "maturing debt on favorable terms could materially adversely affect financial position.", y)

    return _save(p, "TechCorp_Annual_Report_2024.pdf")


def generate_financehub_risk_disclosure() -> str:
    p = MinimalPDF("FinanceHub Risk Disclosure 2024")
    y = 740
    p.title_line("FinanceHub Ltd (LSE: FHL) — Risk Disclosure & Compliance Report 2024", y); y -= 30

    y = p.section("Overview", y)
    y = p.body("FinanceHub Ltd is a diversified financial services group providing retail banking, investment "
               "management, and insurance across 12 markets. This Basel III Pillar 3 disclosure details material risk "
               "exposures. Total assets under management: 89.4 billion GBP. Common Equity Tier 1 (CET1) ratio: 13.2%, "
               "above the minimum regulatory requirement of 10.5%.", y)

    y = p.section("Capital Adequacy — Basel III Compliance", y)
    y = p.body("Total Capital Ratio of 16.8% provides a buffer of 630 basis points above minimum requirements including "
               "Capital Conservation Buffer and G-SIB surcharge. Risk-Weighted Assets (RWA) total 54.2 billion GBP, "
               "reflecting 12% increase year-over-year from loan book growth. Leverage Ratio 5.4% comfortably exceeds "
               "3.0% minimum. Stress testing under Bank of England adverse scenario: CET1 depletion 3.1 percentage "
               "points, maintaining capital above 7.0% threshold in all scenarios.", y)

    y = p.section("Credit Risk Assessment", y)
    y = p.body("Non-performing loan (NPL) ratio increased to 3.2% from 2.7% in 2023, driven by commercial real estate "
               "portfolio stress. Loan loss provisions of 1.2 billion GBP recognized in FY2024, representing 1.4% of "
               "total loan book. Mortgage book quality stable with weighted average LTV of 58%. ECL model under IFRS 9 "
               "projects 890 million GBP in Stage 2 and Stage 3 provisions over next 12 months. Counterparty credit "
               "risk for derivatives: 3.4 billion gross, reduced to 1.1 billion net after netting agreements.", y)

    y = p.section("AML / KYC Compliance Status", y)
    y = p.body("847 Suspicious Activity Reports (SARs) filed with NCA in FY2024, up 23%. Investment 78 million GBP in "
               "financial crime infrastructure including AI-powered transaction screening and enhanced beneficial ownership "
               "verification. FCA review Q2 2024 identified deficiencies in correspondent banking due diligence, resulting "
               "in Voluntary Requirement (VREQ) requiring remediation within 18 months at estimated cost 45 million GBP. "
               "KYC refresh rates: 94% of high-risk customers within 12-month cycle (target: 98%).", y)

    y = p.section("Market Risk", y)
    y = p.body("NII sensitivity: 340 million GBP impact from 200 basis point parallel rate increase, reflecting asset-"
               "sensitive balance sheet positioning. Duration gap 2.3 years. FX revenues 34% of total income. 10% GBP "
               "depreciation would increase reported revenue by approximately 280 million GBP. Trading book VaR (99% "
               "confidence, 10-day holding period) averaged 42 million GBP in FY2024, within 75 million GBP board limit. "
               "Equity risk in investment portfolio totals 2.1 billion GBP, beta 0.89 vs FTSE All-Share.", y)

    y = p.section("MiFID II and Consumer Duty Compliance", y)
    y = p.body("Full MiFID II compliance achieved across all product lines including transaction reporting, best execution "
               "monitoring, and product governance requirements. Consumer Duty implementation completed July 2024 with "
               "enhanced fair value assessments for 247 retail products. Three products failed fair value test and were "
               "withdrawn, affecting 1.2 billion GBP in customer assets. 12 personal data breaches reported to ICO in "
               "FY2024, none classified as high severity. PCI DSS Level 1 certification maintained.", y)

    return _save(p, "FinanceHub_Risk_Disclosure_2024.pdf")


def generate_bfsi_regulatory_summary() -> str:
    p = MinimalPDF("BFSI Regulatory Framework 2024")
    y = 740
    p.title_line("BFSI Sector — Regulatory Compliance Framework Reference 2024", y); y -= 30

    y = p.section("Basel III — Capital and Liquidity Standards", y)
    y = p.body("Basel III establishes minimum capital requirements ensuring financial stability. Key requirements: "
               "CET1 ratio minimum 4.5%, Tier 1 Capital minimum 6.0%, Total Capital Ratio minimum 8.0%, Capital "
               "Conservation Buffer 2.5%, G-SIB surcharge 1.0%-3.5% for systemically important institutions. "
               "Liquidity Coverage Ratio (LCR) requires HQLA sufficient to survive 30-day stress scenario. "
               "Net Stable Funding Ratio (NSFR) ensures long-term assets funded by stable long-term liabilities. "
               "Penalties: mandatory capital plans, dividend restrictions, and in severe cases license revocation.", y)

    y = p.section("AML/KYC — Financial Crime Prevention Framework", y)
    y = p.body("AML compliance requires risk-based customer due diligence (CDD) procedures. KYC obligations include "
               "customer identification, beneficial ownership verification, and ongoing monitoring. Enhanced Due "
               "Diligence mandatory for PEPs, high-risk countries, and complex ownership structures. Transaction "
               "monitoring must flag structuring, rapid fund movement, and round-dollar transactions. SARs must be "
               "filed within 30 days. Tipping off customers about SAR filings is a criminal offense. Fines: "
               "Deutsche Bank $150M (2023), Goldman Sachs $2.9B (2020) for AML failures.", y)

    y = p.section("Dodd-Frank Act — Systemic Risk Regulation", y)
    y = p.body("Dodd-Frank (2010) established comprehensive financial regulation following the 2008 crisis. Title I "
               "designates SIFIs subject to enhanced prudential standards. Title VII regulates OTC derivatives "
               "requiring central clearing, exchange trading, and reporting. The Volcker Rule (Section 619) prohibits "
               "proprietary trading and restricts hedge fund sponsorship. DFAST stress testing mandates annual tests "
               "for institutions with assets exceeding $100 billion. Resolution planning requires living wills for "
               "rapid and orderly resolution under bankruptcy.", y)

    y = p.section("IFRS 9 — Expected Credit Loss Model", y)
    y = p.body("IFRS 9 replaced IAS 39 introducing the Expected Credit Loss (ECL) model for impairment recognition. "
               "Three-stage classification: Stage 1 (performing) 12-month ECL; Stage 2 (significant credit "
               "deterioration) lifetime ECL; Stage 3 (credit-impaired) lifetime ECL with interest on net amount. "
               "Forward-looking macro-economic scenarios must be incorporated. Minimum three scenarios required: "
               "base, upside, downside. Disclosures must include reconciliation of opening to closing loss allowance "
               "and sensitivity analysis of ECL to macro assumptions.", y)

    y = p.section("GDPR — Data Protection Requirements for BFSI", y)
    y = p.body("GDPR imposes strict obligations on financial institutions processing personal data of EU residents. "
               "Legal bases for financial data include contract performance, legal obligation, legitimate interests, "
               "and explicit consent. Data subjects have rights to access, rectification, erasure, restriction, "
               "portability, and objection. DPOs mandatory for banks and insurers due to large-scale processing. "
               "Data breach notification to supervisory authority within 72 hours if likely to result in risk. "
               "Maximum penalties: 20 million EUR or 4% of global annual turnover. BFSI fines: Deutsche Bank 6.3M "
               "EUR, N26 4.25M EUR.", y)

    y = p.section("SOX Section 404 — Internal Controls Over Financial Reporting", y)
    y = p.body("SOX Section 404 requires management to assess ICFR effectiveness annually using COSO 2013 framework. "
               "Management must evaluate control design and operating effectiveness. External auditors must "
               "independently attest to management assessment for accelerated filers. Material weaknesses require "
               "immediate disclosure. Common BFSI control deficiencies: inadequate IT access segregation, insufficient "
               "review over complex estimates, weaknesses in third-party vendor management, deficiencies in "
               "period-end financial close processes. Remediation costs $5M-$50M typically.", y)

    y = p.section("MiFID II — Investment Services and Market Conduct", y)
    y = p.body("MiFID II governs investment services across the European Economic Area. Best execution obligations "
               "require all sufficient steps to obtain best possible result for clients. Transaction reporting: all "
               "transactions in financial instruments reported to competent authorities within one business day. "
               "Product governance requires manufacturers and distributors to define target markets. Research "
               "unbundling separates payment for research from execution commissions. Algorithmic trading firms "
               "must implement kill switches and pre-trade risk controls. Record-keeping mandates retention of all "
               "communications relating to transactions.", y)

    return _save(p, "BFSI_Regulatory_Framework_2024.pdf")


def generate_all_sample_pdfs() -> list[tuple[str, str, str]]:
    """Returns list of (file_path, company, doc_type) tuples."""
    results = []
    for fn, company, doc_type in [
        (generate_techcorp_annual_report, "TechCorp Global", "annual_report"),
        (generate_financehub_risk_disclosure, "FinanceHub Ltd", "risk_disclosure"),
        (generate_bfsi_regulatory_summary, "BFSI Sector", "regulatory_framework"),
    ]:
        try:
            path = fn()
            results.append((path, company, doc_type))
        except Exception as e:
            print(f"[PDF Generator] {company} PDF failed: {e}")
    return results


if __name__ == "__main__":
    paths = generate_all_sample_pdfs()
    for path, company, doc_type in paths:
        size = os.path.getsize(path) if os.path.exists(path) else 0
        print(f"Generated: {os.path.basename(path)} ({size:,} bytes) [{company} / {doc_type}]")
