const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Header, Footer, 
        AlignmentType, LevelFormat, HeadingLevel, BorderStyle, WidthType, 
        PageNumber, PageBreak, ShadingType } = require('docx');
const fs = require('fs');

const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 40, bold: true, color: "1a365d", font: "Arial" },
        paragraph: { spacing: { before: 0, after: 200 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: "1a365d", font: "Arial" },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: "0891b2", font: "Arial" },
        paragraph: { spacing: { before: 280, after: 140 }, outlineLevel: 1 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullet-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ]
  },
  sections: [{
    properties: {
      page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
    },
    headers: {
      default: new Header({ children: [new Paragraph({ 
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "IHEP Investor Pitch Deck Content", italics: true, size: 18, color: "666666" })]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Page ", size: 20 }), new TextRun({ children: [PageNumber.CURRENT], size: 20 }), new TextRun({ text: " of ", size: 20 }), new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 20 })]
      })] })
    },
    children: [
      // Title
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("INVESTOR PITCH DECK CONTENT")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "Slide-by-Slide Content Guide", size: 24, italics: true, color: "666666" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 }, children: [new TextRun({ text: "18 Slides | 16:9 Format | Navy Blue (#1a365d) + Cyan (#0891b2)", size: 20 })] }),
      
      // Design Notes
      new Paragraph({ shading: { fill: "e0f2fe", type: ShadingType.CLEAR }, spacing: { after: 200 }, children: [new TextRun({ text: "Design Notes: ", bold: true }), new TextRun("Professional, clean design. White backgrounds with minimal text per slide. Use data visualizations where possible. Avoid cluttered slides.")] }),
      
      // Slide 1
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 1: TITLE SLIDE")] }),
      new Paragraph({ shading: { fill: "f1f5f9", type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "Visual: ", bold: true }), new TextRun("IHEP logo, subtle abstract node visualization")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Main Title: ", bold: true }), new TextRun("INTEGRATED HEALTH EMPOWERMENT PROGRAM")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Tagline: ", bold: true }), new TextRun("Transforming Aftercare. Accelerating Cures.")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Investment Details: ", bold: true }), new TextRun("Series Seed | $3.5M Raise | $12M Pre-Money Valuation")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Presenter: ", bold: true }), new TextRun("Jason Jarmacz, Founder and Principal Investigator")] }),
      new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Footer: ", bold: true }), new TextRun("CONFIDENTIAL - Do Not Distribute")] }),
      new Paragraph({ shading: { fill: "fef3c7", type: ShadingType.CLEAR }, children: [new TextRun({ text: "Speaker Note: ", bold: true, italics: true }), new TextRun({ text: "Open with personal story. \"In 2024, 15,000 Americans died from HIV-related causes - not because we lack treatment, but because 40% disappear from care within six months. IHEP exists to close that gap.\"", italics: true })] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // Slide 2
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 2: THE PROBLEM - QUANTIFIED")] }),
      new Paragraph({ shading: { fill: "f1f5f9", type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "Visual: ", bold: true }), new TextRun("Three-column layout with stark statistics and icons")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Headline: ", bold: true }), new TextRun("THE CRISIS IN AFTERCARE")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Stat 1: ", bold: true }), new TextRun("40% Patient Dropout - Post-diagnosis care abandonment")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Stat 2: ", bold: true }), new TextRun("$290B Annual Cost - Healthcare non-adherence")] }),
      new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Stat 3: ", bold: true }), new TextRun("66% Viral Suppression - vs. 95% clinical potential")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Key Formula:", bold: true })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, shading: { fill: "f1f5f9", type: ShadingType.CLEAR }, spacing: { after: 200 }, children: [new TextRun({ text: "Impact = (0.40 dropout rate) x ($420K lifetime cost) x (38K new diagnoses) = $6.4B preventable costs annually", font: "Courier New", size: 20 })] }),
      new Paragraph({ shading: { fill: "fef3c7", type: ShadingType.CLEAR }, children: [new TextRun({ text: "Speaker Note: ", bold: true, italics: true }), new TextRun({ text: "\"This isn't a clinical failure - we have the medications. This is a systems failure. Patients get a prescription and a follow-up appointment. No wonder 40% disappear.\"", italics: true })] }),
      
      // Slide 3
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 3: THE MARKET OPPORTUNITY")] }),
      new Paragraph({ shading: { fill: "f1f5f9", type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "Visual: ", bold: true }), new TextRun("Concentric circles showing TAM/SAM/SOM")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Headline: ", bold: true }), new TextRun("MASSIVE, GROWING MARKET")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "TAM: ", bold: true }), new TextRun("$293B - Global digital health by 2027 (25.9% CAGR)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "SAM: ", bold: true }), new TextRun("$47B - U.S. chronic disease management technology")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "SOM: ", bold: true }), new TextRun("$2.8B - U.S. HIV digital health and care coordination")] }),
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Beachhead Stats: ", bold: true }), new TextRun("1.2M Americans with HIV | 38K new diagnoses annually | $420K lifetime cost")] }),
      new Paragraph({ shading: { fill: "fef3c7", type: ShadingType.CLEAR }, children: [new TextRun({ text: "Speaker Note: ", bold: true, italics: true }), new TextRun({ text: "\"HIV is our entry point to a $47B platform opportunity. The architecture applies to any life-altering condition.\"", italics: true })] }),
      
      // Slide 4
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 4: THE IHEP SOLUTION")] }),
      new Paragraph({ shading: { fill: "f1f5f9", type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "Visual: ", bold: true }), new TextRun("Three-layer architecture diagram")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Headline: ", bold: true }), new TextRun("MORPHOGENETIC DIGITAL HEALTH ECOSYSTEM")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Layer 1 - Patient Digital Twin: ", bold: true }), new TextRun("Real-time predictive health representation (75% accuracy)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Layer 2 - Organizational Twin: ", bold: true }), new TextRun("Mapping care ecosystems (25% efficiency improvement)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Layer 3 - Federated AI Network: ", bold: true }), new TextRun("Cross-site learning without data movement")] }),
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Mathematical Foundation: ", bold: true })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, shading: { fill: "f1f5f9", type: ShadingType.CLEAR }, children: [new TextRun({ text: "d(phi)/dt = D * nabla^2(phi) + f(phi) - lambda * phi", font: "Courier New", size: 20 })] }),
      new Paragraph({ shading: { fill: "fef3c7", type: ShadingType.CLEAR }, children: [new TextRun({ text: "Speaker Note: ", bold: true, italics: true }), new TextRun({ text: "\"This is not an app. It's a mathematically-grounded ecosystem that gets smarter with every patient interaction.\"", italics: true })] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // Slide 5
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 5: COMPETITIVE LANDSCAPE")] }),
      new Paragraph({ shading: { fill: "f1f5f9", type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "Visual: ", bold: true }), new TextRun("2x2 matrix - Clinical Integration vs. AI Sophistication")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Headline: ", bold: true }), new TextRun("COMPETITIVE POSITIONING")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Telehealth (Teladoc, Amwell): ", bold: true }), new TextRun("Clinical access but no AI personalization")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Disease Apps (MyTherapy): ", bold: true }), new TextRun("User-friendly but fragmented, no integration")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "EHR Portals (Epic MyChart): ", bold: true }), new TextRun("Provider integration but poor UX, zero AI")] }),
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "IHEP Position: ", bold: true }), new TextRun("Only platform combining clinical integration + AI + community + cure research")] }),
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Competitive Moats:", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Compliance-first architecture (2-year head start)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Federated learning (privacy + power)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Google Cloud partnership (enterprise validation)")] }),
      
      // Slide 6
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 6: BUSINESS MODEL AND UNIT ECONOMICS")] }),
      new Paragraph({ shading: { fill: "f1f5f9", type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "Visual: ", bold: true }), new TextRun("Revenue stream timeline across phases")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Headline: ", bold: true }), new TextRun("PATH TO COMMERCIAL SUSTAINABILITY")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Phase I-II (Years 1-5): ", bold: true }), new TextRun("SBIR/STTR grants (~$2.2M) + Foundation grants ($2M)")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Phase II-III (Years 3-7): ", bold: true }), new TextRun("Healthcare contracts ($150-300 PMPM) + Data licensing")] }),
      new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Phase III (Years 8-10): ", bold: true }), new TextRun("Insurance reimbursement + EHR licensing ($500K-2M) + Pharma partnerships")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Unit Economics (Commercial Phase):", bold: true })] }),
      new Table({
        columnWidths: [4680, 4680],
        rows: [
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, shading: { fill: "e0f2fe", type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "CAC", bold: true })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("$500")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, shading: { fill: "e0f2fe", type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "LTV", bold: true })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("$3,600")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, shading: { fill: "e0f2fe", type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "LTV:CAC Ratio", bold: true })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 4680, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "7.2:1", bold: true })] })] })
          ]})
        ]
      }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // Slide 7
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 7: FINANCIAL PROJECTIONS")] }),
      new Paragraph({ shading: { fill: "f1f5f9", type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "Visual: ", bold: true }), new TextRun("Bar chart (revenue) with line overlay (profitability path)")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Headline: ", bold: true }), new TextRun("10-YEAR FINANCIAL MODEL")] }),
      new Table({
        columnWidths: [2340, 2340, 2340, 2340],
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, shading: { fill: "1a365d", type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Metric", bold: true, color: "FFFFFF" })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, shading: { fill: "1a365d", type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Year 1", bold: true, color: "FFFFFF" })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, shading: { fill: "1a365d", type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Year 5", bold: true, color: "FFFFFF" })] })] }),
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, shading: { fill: "1a365d", type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Year 10", bold: true, color: "FFFFFF" })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Participants")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("300")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("5,000")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("25,000")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("Revenue")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$0")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$1.2M")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$35M")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun("EBITDA Margin")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("N/A")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("-78%")] })] }),
            new TableCell({ borders: cellBorders, width: { size: 2340, type: WidthType.DXA }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "23%", bold: true })] })] })
          ]})
        ]
      }),
      new Paragraph({ spacing: { before: 200 }, children: [new TextRun({ text: "Key Metrics: ", bold: true }), new TextRun("Break-even Year 8 | 30-Year NPV: $287.4M | IRR: 34.2%")] }),
      new Paragraph({ shading: { fill: "fef3c7", type: ShadingType.CLEAR }, children: [new TextRun({ text: "Speaker Note: ", bold: true, italics: true }), new TextRun({ text: "\"The 34% IRR significantly exceeds typical healthcare venture returns of 20-25%. And this doesn't price cure pathway optionality.\"", italics: true })] }),
      
      // Slide 8
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 8: THE CURE ACCELERATION THESIS")] }),
      new Paragraph({ shading: { fill: "f1f5f9", type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "Visual: ", bold: true }), new TextRun("Funnel diagram: Data Collection to Cure Pathways")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Headline: ", bold: true }), new TextRun("BEYOND CARE: BUILDING THE ROADMAP TO CURE")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Digital Twin Advantage:", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Longitudinal data: Thousands of patients, years of tracking")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Predictive models: Anticipate resistance mutations")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Bio-AI simulation: Test strategies in silico")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Federated insights: Cross-site patterns revealing cure mechanisms")] }),
      new Paragraph({ spacing: { before: 200 }, children: [new TextRun({ text: "Commercial Value: ", bold: true }), new TextRun("HIV therapeutic market $32B | Functional cure value $50-100B (NOT in financial model)")] }),
      new Paragraph({ shading: { fill: "fef3c7", type: ShadingType.CLEAR }, children: [new TextRun({ text: "Speaker Note: ", bold: true, italics: true }), new TextRun({ text: "\"Every other digital health company optimizes today's care. We do that AND build tomorrow's cures. That's pure upside optionality.\"", italics: true })] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // Slides 9-12
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 9: TECHNOLOGY ARCHITECTURE")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Key Points:", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Frontend: Next.js 14 + React 18 + Three.js")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Backend: Python microservices + Vertex AI")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Data: PostgreSQL + Google Healthcare API (FHIR R4)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Security: Seven-layer defense, P(breach) <= 10^-21")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Partnership: Signed Google Cloud business partnership")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 10: TRACTION AND VALIDATION")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Completed:", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Comprehensive architecture designed and validated")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Google Cloud business partnership executed")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("30-year financial model with sensitivity analysis")] }),
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "6-Month Milestones:", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Security infrastructure deployed and audited")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("MVP platform operational")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("First 50 patients enrolled (Miami pilot)")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 11: GO-TO-MARKET STRATEGY")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Geographic Expansion:", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Phase I: Miami + Orlando (150-300 participants)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Phase II: LA/San Diego + NY/Massachusetts (5,000 participants)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Phase III: 10 major HIV epicenters (25,000+ participants)")] }),
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Acquisition Strategy: ", bold: true }), new TextRun("Community health workers + Provider referrals + Patient-to-patient (CAC: $500)")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 12: TEAM")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Current:", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Jason Jarmacz - Founder, Principal Investigator")] }),
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Phase I Hiring:", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("CTO: Healthcare AI expertise")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("CSCO: CISSP, NIST framework implementation")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Clinical Director: MD with HIV/AIDS specialty")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Community Director: HIV service organization leadership")] }),
      
      new Paragraph({ children: [new PageBreak()] }),
      
      // Slides 13-18
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 13: SOCIAL IMPACT AND HEALTH EQUITY")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Disparity Statistics:", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Black Americans: 41% of diagnoses (13% of population)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Hispanic/Latino: 29% of diagnoses (18% of population)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Southern states: 51% of diagnoses")] }),
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "IHEP Approach: ", bold: true }), new TextRun("Start where need is greatest, hire from communities served (50%+ peer navigators)")] }),
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "B Corporation: ", bold: true }), new TextRun("Protecting mission through legal structure")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 14: REGULATORY AND COMPLIANCE")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Frameworks:", bold: true }), new TextRun(" HIPAA | NIST SP 800-53r5 | NIST AI RMF | FDA Digital Health")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Seven-Layer Defense: ", bold: true }), new TextRun("P(breach) = 99.99999% protection")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Competitive Advantage: ", bold: true }), new TextRun("Competitors retrofitting: 18-24 months, $2-5M. IHEP: Built-in from day one.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 15: RISK FACTORS")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "PHI Breach: ", bold: true }), new TextRun("Mitigation: Mathematical security proof, $10M insurance")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Regulatory Changes: ", bold: true }), new TextRun("Mitigation: Exceeds current requirements, quarterly audits")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "AI Bias: ", bold: true }), new TextRun("Mitigation: Demographic monitoring, human-in-loop")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Funding Gap: ", bold: true }), new TextRun("Mitigation: SBIR/STTR pathway, diversified sources")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 16: INVESTMENT TERMS")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Offering: ", bold: true }), new TextRun("$3.5M Convertible Note")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("6% simple interest | 24-month maturity")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("20% discount to Series A | $15M cap")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Converts on $8M+ qualified financing")] }),
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Use of Funds: ", bold: true }), new TextRun("Personnel 71% | Compliance 6% | Infrastructure 4% | Contingency 13%")] }),
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "Lead Benefits ($1M+): ", bold: true }), new TextRun("Board observer seat, pro-rata rights")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 17: WHY NOW?")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Technology Maturity: ", bold: true }), new TextRun("Federated learning, cloud infrastructure, digital twin frameworks ready")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Regulatory Clarity: ", bold: true }), new TextRun("NIST AI RMF published, HIPAA cloud guidance clarified")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Market Readiness: ", bold: true }), new TextRun("COVID accelerated telehealth adoption, value-based care expanding")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Competitive Window: ", bold: true }), new TextRun("18-24 months before convergence - time to build is NOW")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("SLIDE 18: THE ASK AND CLOSING")] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "The Opportunity:", bold: true })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Transform aftercare for 1.2M Americans")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Build AI infrastructure for cures")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Scale to 5x market expansion")] }),
      new Paragraph({ spacing: { before: 100 }, children: [new TextRun({ text: "The Investment: ", bold: true }), new TextRun("$3.5M Seed | 34.2% IRR | $287M NPV")] }),
      new Paragraph({ spacing: { before: 200 }, shading: { fill: "e0f2fe", type: ShadingType.CLEAR }, children: [new TextRun({ text: "\"We're not just building a company. We're building the future of healthcare. Let's build it together.\"", bold: true, italics: true, size: 24 })] }),
      
      new Paragraph({ spacing: { before: 400 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "END OF PITCH DECK CONTENT", bold: true, size: 20, color: "666666" })] }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/mnt/user-data/outputs/04_IHEP_Pitch_Deck_Content.docx", buffer);
  console.log("Pitch Deck Content created successfully");
});
