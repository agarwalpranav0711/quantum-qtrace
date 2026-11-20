# Q-TRACE Forensic Workstation Design System

## 1. Design Philosophy & Evidentiary Aesthetics

The **Q-TRACE** frontend design system is engineered specifically for digital forensic investigators, insurance fraud examination teams, and scientific researchers. 

Unlike generic software dashboards characterized by decorative gradients, neon saturated colors, or rounded cards, Q-TRACE employs a **dark-first, high-precision laboratory aesthetic**. It communicates:
- **Scientific Rigor**: High-contrast, legible typography and monospace telemetry.
- **Evidentiary Integrity**: Cryptographically locked states styled distinctly from unverified data.
- **Cognitive Clarity**: Low-distraction backgrounds focusing examiner attention on visual photographic artifacts.
- **Transparent Classification**: Clear visual distinction between physical facts, algorithmic calculations, flagged anomalies, and human hypotheses.

---

## 2. Color Palette & Functional Tokens

```text
Background Surfaces:
┌────────────────────────────────────────────────────────┐
│  dark-950 (#080C14): Workstation Base / Canvas Grid    │
├────────────────────────────────────────────────────────┤
│  dark-900 (#0D131F): Card Surfaces & Navigation Bars   │
├────────────────────────────────────────────────────────┤
│  dark-850 (#121A2A): Elevated Panels & Hover States    │
├────────────────────────────────────────────────────────┤
│  dark-800 (#182236): Interactive Inputs & Inner Wells  │
├────────────────────────────────────────────────────────┤
│  dark-700 (#273756): Subtle Structural Borders         │
└────────────────────────────────────────────────────────┘

Semantic Forensic Accents:
┌────────────────────────────────────────────────────────┐
│  qtrace-cyan   (#00E5FF): Active Selection & Navigation│
│  qtrace-emerald(#10B981): Verified Cryptographic Hash  │
│  qtrace-rose   (#F43F5E): Tampered / Hash Invalidation │
│  qtrace-amber  (#F59E0B): Suspect Flagged Anomaly      │
│  qtrace-indigo (#6366F1): Quantum Simulation Telemetry │
└────────────────────────────────────────────────────────┘
```

| Token Name | Hex Code | Purpose & Semantic Role |
| :--- | :--- | :--- |
| `dark-950` | `#080C14` | Deep midnight canvas background, canvas viewport well |
| `dark-900` | `#0D131F` | Primary panel surface, header, sidebar base |
| `dark-850` | `#121A2A` | Elevated cards, dialog surfaces, table row hovers |
| `dark-800` | `#182236` | Input fields, active button states, inner borders |
| `dark-700` | `#273756` | Default component borders, divider lines |
| `cyan-400` | `#22D3EE` | Primary brand accent, selected route highlight, active crosshair |
| `emerald-400` | `#34D399` | WORM verification success, SHA-256 match, online health |
| `rose-400` | `#FB7185` | Bitstream compromised, validation failure, critical warning |
| `amber-400` | `#FBBF24` | Suspect image patch, pending analysis, unverified lead |
| `indigo-400` | `#818CF8` | Quantum NEQR register representation, Qiskit telemetry |

---

## 3. Typography Scale

Q-TRACE pairs **Inter** (for high-legibility interface copy) with **JetBrains Mono** (for cryptographic digests, pixel coordinates, and quantum circuit telemetry):

| Role | Font Family | Size / Leading | Weight | Tracking | Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Display Title** | Inter | `1.125rem` (18px) / `1.5rem` | Bold (700) | Tight (`-0.025em`) | Page titles, major section headers |
| **Section Header** | Inter | `0.875rem` (14px) / `1.25rem` | Semibold (600) | Normal | Card titles, modal headers |
| **Body Primary** | Inter | `0.75rem` (12px) / `1rem` | Regular (400) | Normal | Descriptions, form labels, table cells |
| **Body Secondary** | Inter | `0.6875rem` (11px) / `0.875rem` | Regular (400) | Normal | Metadata labels, helper text |
| **Monospace Telemetry** | JetBrains Mono | `0.75rem` (12px) | Medium (500) | Normal | SHA-256 digests, case numbers, qubits |
| **Micro Monospace** | JetBrains Mono | `0.625rem` (10px) | Regular (400) | Wide (`0.05em`) | Badges, coordinates, timestamps |

---

## 4. Reusable Component Catalog

All primitives reside in [`frontend/src/components/ui/`](file:///d:/WebDev%20PROJECTS/quantum%20qtrace/frontend/src/components/ui):

### 4.1 Button (`Button.tsx`)
- **Variants**: `primary` (cyan accent with dark text), `secondary` (dark graphite surface), `outline` (transparent with cyan border), `danger` (rose surface for critical cancellations), `ghost` (clean hover highlight).
- **Sizes**: `sm` (compact table/header actions), `md` (form submissions), `lg` (hero actions).
- **States**: Default, hover, active, disabled, `isLoading` (renders spinning SVG ring while preserving button geometry).

### 4.2 Forensic Badge (`Badge.tsx`)
- Monospace uppercase tracking indicators.
- **Variants**: `verified` (emerald background & border), `compromised` (rose background & border), `open` (cyan outline), `warning` (amber outline), `indigo` (quantum telemetry), `neutral` (graphite).

### 4.3 Workstation Card (`Card.tsx`)
- Structured surface container with optional subtle border glow (`glow` prop) for high-priority interactive workflows. Subcomponents: `CardHeader`, `CardTitle`, `CardDescription`.

### 4.4 Status Indicator (`StatusIndicator.tsx`)
- Pulsing or solid status dot with millisecond health telemetry label (`operational`, `verified`, `compromised`, `warning`, `idle`).

### 4.5 Empty & Loading States (`EmptyState.tsx`, `LoadingSpinner.tsx`)
- Clean, non-distracting empty states with actionable primary buttons guiding the examiner to the next step.
- Monospace progress spinners communicating live backend processing.

### 4.6 Inputs & Selects (`Input.tsx`, `Select.tsx`)
- Dark-themed form elements with high-contrast text, clear error labels, and cyan focus rings.

### 4.7 Accessible Modal (`Modal.tsx`)
- Accessible dialog overlay with backdrop blur, keyboard escape listener, and scroll lock.

### 4.8 Forensic Image Viewer (`ForensicImageViewer.tsx`)
- High-performance canvas container supporting smooth click-and-drag panning, wheel zoom (0.5× to 5.0×), 1:1 pixel mode, live cursor coordinate crosshair (`X: px, Y: px`), and WORM badge headers.

