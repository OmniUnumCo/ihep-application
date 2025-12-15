/**
 * IHEP Complete Architecture Document Generator
 * Generates production-ready Word document with full technical specifications
 */

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, PageOrientation, LevelFormat,
        HeadingLevel, BorderStyle, WidthType, ShadingType, PageNumber,
        PageBreak } = require('docx');
const fs = require('fs');

// Table styling
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };
const headerShading = { fill: "1a365d", type: ShadingType.CLEAR };
const altRowShading = { fill: "f7fafc", type: ShadingType.CLEAR };

// Create document
const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Arial", size: 24 }
      }
    },
    paragraphStyles: [
      {
        id: "Title",
        name: "Title",
        basedOn: "Normal",
        run: { size: 56, bold: true, color: "1a365d", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER }
      },
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 32, bold: true, color: "1a365d", font: "Arial" },
        paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 }
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 28, bold: true, color: "2d3748", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 80 }, outlineLevel: 1 }
      },
      {
        id: "Heading3",
        name: "Heading 3",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 24, bold: true, color: "4a5568", font: "Arial" },
        paragraph: { spacing: { before: 200, after: 60 }, outlineLevel: 2 }
      }
    ]
  },
  numbering: {
    config: [
      {
        reference: "bullet-list",
        levels: [{
          level: 0,
          format: LevelFormat.BULLET,
          text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
      {
        reference: "numbered-list",
        levels: [{
          level: 0,
          format: LevelFormat.DECIMAL,
          text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          children: [
            new TextRun({ text: "IHEP Complete Architecture - ", size: 20, color: "718096" }),
            new TextRun({ text: "CONFIDENTIAL", size: 20, bold: true, color: "e53e3e" })
          ]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "Page ", size: 20, color: "718096" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 20, color: "718096" }),
            new TextRun({ text: " of ", size: 20, color: "718096" }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 20, color: "718096" })
          ]
        })]
      })
    },
    children: [
      // Title Page
      new Paragraph({ spacing: { before: 2400 } }),
      new Paragraph({
        heading: HeadingLevel.TITLE,
        children: [new TextRun("IHEP Complete Application Architecture")]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 480, after: 240 },
        children: [new TextRun({
          text: "Integrated Health Empowerment Program",
          size: 32,
          color: "4a5568"
        })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 240, after: 240 },
        children: [new TextRun({
          text: "Production-Ready Implementation with Financial Generation Module",
          size: 28,
          italics: true,
          color: "718096"
        })]
      }),
      new Paragraph({ spacing: { before: 960 } }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Version 2.0.0", size: 24, bold: true })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 120 },
        children: [new TextRun({ text: "November 30, 2025", size: 24 })]
      }),
      new Paragraph({ spacing: { before: 960 } }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Prepared by:", size: 22, color: "718096" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 120 },
        children: [new TextRun({ text: "Jason Jarmacz", size: 24, bold: true })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Founder & Principal Investigator", size: 22 })]
      }),
      new Paragraph({ spacing: { before: 960 } }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({
          text: "BUSINESS SENSITIVE - INVESTOR READY",
          size: 24,
          bold: true,
          color: "c53030"
        })]
      }),
      
      // Page break
      new Paragraph({ children: [new PageBreak()] }),
      
      // Executive Summary
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Executive Summary")]
      }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun(
          "This document presents the complete, production-ready implementation of the IHEP Digital Twin Ecosystem with integrated Financial Health Twin Module. The architecture delivers a comprehensive healthcare aftercare platform combining clinical management, behavioral engagement, social support, and financial empowerment into a unified system."
        )]
      }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun(
          "The platform implements a seven-layer security model with mathematical guarantees exceeding fourteen nines of protection probability, fully compliant with HIPAA, NIST SP 800-53r5, and SOC 2 Type II requirements. The morphogenetic self-healing framework provides autonomous system resilience through reaction-diffusion dynamics and multi-agent coordination."
        )]
      }),
      
      // Key Metrics Table
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Key Platform Metrics")]
      }),
      new Table({
        columnWidths: [4680, 4680],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({
                borders: cellBorders,
                shading: headerShading,
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "Metric", bold: true, color: "FFFFFF" })]
                })]
              }),
              new TableCell({
                borders: cellBorders,
                shading: headerShading,
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "Value", bold: true, color: "FFFFFF" })]
                })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Security Protection Level")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("P(breach) < 10^-14 (fourteen nines)")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("Target Participants (Year 5)")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("25,000 active users")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Financial Impact (Year 5)")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("$14.92M participant benefit")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("ROI Per Dollar Invested")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("$3.18 return per $1.00")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Benefits Programs Tracked")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("300+ federal, state, and local programs")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("System Availability Target")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("99.95% uptime SLA")] })] })
            ]
          })
        ]
      }),
      
      // Page break
      new Paragraph({ children: [new PageBreak()] }),
      
      // Four-Twin Architecture
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Four-Twin Ecosystem Architecture")]
      }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun(
          "The IHEP platform implements a comprehensive digital twin architecture that represents each participant across four interconnected dimensions. This multi-dimensional approach enables holistic health optimization by addressing not just clinical factors, but the full spectrum of determinants that influence health outcomes."
        )]
      }),
      
      // Clinical Twin
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("1. Clinical Twin")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun(
          "The Clinical Twin aggregates and synthesizes medical data to provide a comprehensive view of the participant's health status. Data sources include lab results, vital signs, medication history, and treatment protocols."
        )]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Lab Results: CD4 counts, viral load, metabolic panels")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Vital Signs: Blood pressure, heart rate, weight trends")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Medications: Current regimens, adherence patterns, refill schedules")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Treatment History: Interventions, outcomes, side effects")]
      }),
      
      // Behavioral Twin
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("2. Behavioral Twin")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun(
          "The Behavioral Twin tracks engagement patterns and lifestyle factors that influence health outcomes. This dimension captures how participants interact with the healthcare system and their daily health behaviors."
        )]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Medication Adherence: Dose timing, missed doses, refill patterns")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Appointment Attendance: Visit frequency, cancellations, no-shows")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("App Engagement: Feature usage, session duration, notification response")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Self-Reported Metrics: Mood, energy, symptom tracking")]
      }),
      
      // Social Twin
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("3. Social Twin")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun(
          "The Social Twin maps social determinants of health (SDOH) and community resources available to each participant. This dimension recognizes that health outcomes are significantly influenced by social and environmental factors."
        )]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Support Network: Family, friends, peer navigators, care team")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Housing Stability: Housing type, stability score, assistance programs")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Food Security: Access to nutrition, food assistance enrollment")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Transportation: Access to healthcare appointments, mobility options")]
      }),
      
      // Financial Twin (NEW)
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("4. Financial Health Twin (NEW)")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun(
          "The Financial Health Twin is the newest dimension, integrating comprehensive financial data to address economic barriers to health. Research demonstrates strong correlation between financial stability and medication adherence, making this dimension critical for holistic care."
        )]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Income Tracking: Multiple income streams with stability scoring")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Expense Management: Categorized expenses, fixed vs. variable analysis")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Debt Optimization: Payoff trajectories, DTI ratio management")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Benefits Optimization: 300+ programs, eligibility matching, enrollment assistance")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Opportunity Matching: AI-powered income opportunity recommendations")]
      }),
      
      // Page break
      new Paragraph({ children: [new PageBreak()] }),
      
      // Mathematical Foundation
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Mathematical Foundation")]
      }),
      
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Financial Health Score Calculation")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun(
          "The Financial Health Score is computed as a weighted composite of five normalized components, each representing a critical dimension of financial wellness:"
        )]
      }),
      new Paragraph({
        spacing: { after: 200 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({
          text: "F_score = w_i * I_stability + w_e * E_ratio + w_d * D_burden + w_b * B_utilization + w_s * S_progress",
          italics: true,
          size: 22
        })]
      }),
      
      // Component definitions table
      new Table({
        columnWidths: [2000, 2500, 4860],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({
                borders: cellBorders,
                shading: headerShading,
                children: [new Paragraph({ children: [new TextRun({ text: "Component", bold: true, color: "FFFFFF" })] })]
              }),
              new TableCell({
                borders: cellBorders,
                shading: headerShading,
                children: [new Paragraph({ children: [new TextRun({ text: "Weight", bold: true, color: "FFFFFF" })] })]
              }),
              new TableCell({
                borders: cellBorders,
                shading: headerShading,
                children: [new Paragraph({ children: [new TextRun({ text: "Formula", bold: true, color: "FFFFFF" })] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Income Stability")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("0.25 (25%)")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("1 - CV(Income) where CV = sigma/mu")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("Expense Ratio")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("0.20 (20%)")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("min(1, (Income - Fixed) / Discretionary_Target)")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Debt Burden")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("0.20 (20%)")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("max(0, 1 - DTI / 0.36)")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("Benefits Utilization")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("0.15 (15%)")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("Enrolled_Value / Eligible_Value")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Savings Progress")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("0.20 (20%)")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("min(1, Savings / (3 * Monthly_Expenses))")] })] })
            ]
          })
        ]
      }),
      
      // Morphogenetic Framework
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Morphogenetic Self-Healing Dynamics")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun(
          "The platform implements a reaction-diffusion based morphogenetic computing framework for autonomous self-healing. Signal propagation follows partial differential equations inspired by biological pattern formation:"
        )]
      }),
      new Paragraph({
        spacing: { after: 200 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({
          text: "dphi/dt = D * nabla^2(phi) + f(phi) - lambda * phi",
          italics: true,
          size: 22
        })]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun("Where phi represents the field state (Error, Latency, or Spare Capacity), D is the diffusion coefficient controlling signal spreading, f(phi) is the reaction term for signal injection, and lambda is the decay rate.")]
      }),
      
      // Agent Table
      new Paragraph({
        heading: HeadingLevel.HEADING_3,
        children: [new TextRun("Morphogenetic Agents")]
      }),
      new Table({
        columnWidths: [2000, 3000, 4360],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: headerShading, children: [new Paragraph({ children: [new TextRun({ text: "Agent", bold: true, color: "FFFFFF" })] })] }),
              new TableCell({ borders: cellBorders, shading: headerShading, children: [new Paragraph({ children: [new TextRun({ text: "Trigger", bold: true, color: "FFFFFF" })] })] }),
              new TableCell({ borders: cellBorders, shading: headerShading, children: [new Paragraph({ children: [new TextRun({ text: "Action", bold: true, color: "FFFFFF" })] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Weaver", bold: true })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("L_hot AND delta_S >= 0.1")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Shift 15% load from slow to fast endpoints")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun({ text: "Builder", bold: true })] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("S_low AND L_triggered")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("Expand capacity by 25%")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Scavenger", bold: true })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("E_hot for 3+ consecutive ticks")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Open circuit breaker, quarantine endpoint")] })] })
            ]
          })
        ]
      }),
      
      // Page break
      new Paragraph({ children: [new PageBreak()] }),
      
      // Security Architecture
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Seven-Layer Security Architecture")]
      }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun(
          "The IHEP platform implements defense-in-depth through seven distinct security layers. Each layer provides independent protection, and the combined breach probability is the product of individual layer probabilities:"
        )]
      }),
      new Paragraph({
        spacing: { after: 200 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({
          text: "P(breach) = Product(P_i) = 10^-3 * 10^-3 * 10^-2 * 10^-2 * 10^-2 * 10^-1 * 10^-1 = 10^-14",
          italics: true,
          size: 20
        })]
      }),
      
      // Security layers table
      new Table({
        columnWidths: [800, 2800, 3200, 2560],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: headerShading, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Layer", bold: true, color: "FFFFFF" })] })] }),
              new TableCell({ borders: cellBorders, shading: headerShading, children: [new Paragraph({ children: [new TextRun({ text: "Name", bold: true, color: "FFFFFF" })] })] }),
              new TableCell({ borders: cellBorders, shading: headerShading, children: [new Paragraph({ children: [new TextRun({ text: "Controls", bold: true, color: "FFFFFF" })] })] }),
              new TableCell({ borders: cellBorders, shading: headerShading, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "P(breach)", bold: true, color: "FFFFFF" })] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("1")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Identity & Access")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("MFA, biometric, Zero Trust")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("10^-3")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("2")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("Network & Perimeter")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("Cloud Armor, WAF, DDoS")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("10^-3")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("3")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("API Gateway")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Rate limiting, validation")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("10^-2")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("4")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("Application")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("Input sanitization, OWASP")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("10^-2")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("5")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Data Storage")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Envelope encryption, AES-256")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("10^-2")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("6")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("Monitoring & Audit")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("SIEM, anomaly detection")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("10^-1")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("7")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Healthcare API")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("FHIR compliance, PHI isolation")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("10^-1")] })] })
            ]
          })
        ]
      }),
      
      // Page break
      new Paragraph({ children: [new PageBreak()] }),
      
      // Technology Stack
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Technology Stack")]
      }),
      
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Frontend")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Next.js 14 with App Router and React Server Components")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("React 18 with TypeScript for type safety")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Three.js with React Three Fiber for 3D digital twin visualization")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("TailwindCSS for responsive, utility-first styling")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Recharts and Chart.js for financial data visualization")]
      }),
      
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Backend")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Python 3.11+ with Flask/FastAPI microservices")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Cloud Run for serverless container deployment")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Cloud SQL PostgreSQL 15 for relational data")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Memorystore Redis 7 for caching and morphogenetic signals")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Google Healthcare API with FHIR R4 for PHI storage")]
      }),
      
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Infrastructure")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Google Cloud Platform with signed BAA")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Terraform for infrastructure-as-code")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Cloud KMS for envelope encryption key management")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Cloud Armor for WAF and DDoS protection")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("GitHub Actions for CI/CD with blue-green deployments")]
      }),
      
      // Page break
      new Paragraph({ children: [new PageBreak()] }),
      
      // Implementation Timeline
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Implementation Timeline")]
      }),
      
      new Table({
        columnWidths: [2000, 3500, 3860],
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({ borders: cellBorders, shading: headerShading, children: [new Paragraph({ children: [new TextRun({ text: "Phase", bold: true, color: "FFFFFF" })] })] }),
              new TableCell({ borders: cellBorders, shading: headerShading, children: [new Paragraph({ children: [new TextRun({ text: "Duration", bold: true, color: "FFFFFF" })] })] }),
              new TableCell({ borders: cellBorders, shading: headerShading, children: [new Paragraph({ children: [new TextRun({ text: "Deliverables", bold: true, color: "FFFFFF" })] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Phase 1: Foundation")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Weeks 1-6")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Infrastructure setup, CI/CD, security baseline")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("Phase 2: Core")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("Weeks 7-14")] })] }),
              new TableCell({ borders: cellBorders, shading: altRowShading, children: [new Paragraph({ children: [new TextRun("Financial Twin engine, ML services, dashboard")] })] })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Phase 3: Integration")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Weeks 15-20")] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("External APIs, testing, pilot deployment")] })] })
            ]
          })
        ]
      }),
      
      // Closing
      new Paragraph({ spacing: { before: 480 } }),
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Conclusion")]
      }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun(
          "The IHEP Complete Application Architecture with Financial Generation Module represents a paradigm shift in healthcare aftercare technology. By integrating clinical, behavioral, social, and financial dimensions into a unified digital twin ecosystem, the platform addresses the full spectrum of factors that influence health outcomes."
        )]
      }),
      new Paragraph({
        spacing: { after: 200 },
        children: [new TextRun(
          "The morphogenetic self-healing framework ensures system resilience through mathematically-proven reaction-diffusion dynamics, while the seven-layer security architecture provides protection exceeding fourteen nines. This combination of innovation and rigor positions IHEP as the definitive solution for comprehensive healthcare management."
        )]
      }),
      new Paragraph({
        spacing: { before: 480 },
        alignment: AlignmentType.CENTER,
        children: [new TextRun({
          text: "This is healthcare technology aligned with human flourishing.",
          italics: true,
          size: 26,
          color: "1a365d"
        })]
      })
    ]
  }]
});

// Generate document
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync('/mnt/user-data/outputs/IHEP_Complete_Architecture_v2.docx', buffer);
  console.log('Document generated successfully!');
});
