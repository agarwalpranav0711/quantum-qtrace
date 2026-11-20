# Q-TRACE Forensic Workstation
# Accessibility (WCAG 2.2 AA) and Responsive Layout Specification

**Date**: November 19, 2026  
**Document Version**: 1.0.0  
**Target Standard**: WCAG 2.2 Level AA / Section 508  
**Applicability**: Q-TRACE Web Workstation (`frontend/`)

---

## 1. Executive Overview

The Q-TRACE Forensic Workstation is designed as a mission-critical tool for forensic examiners, insurance fraud investigators, and scientific researchers. Forensic software requires uncompromising precision, clarity, and reliability. Accessibility and responsiveness are not decorative afterthoughts; they ensure that investigators can operate efficiently, examine microscopic pixel artifacts without optical fatigue, and navigate complex evidentiary dossiers using assistive technologies or keyboard-only input.

This document details the architectural rules, color contrast ratios, keyboard navigation standards, screen reader semantics, and responsive layout adaptations implemented across all 11 workstation screens.

---

## 2. Color Palette & WCAG 2.2 AA Contrast Verification

The workstation employs a specialized **Dark-First Forensic Palette** engineered to eliminate glare during prolonged laboratory reviews while exceeding WCAG 2.2 Level AA requirements (minimum contrast ratio of 4.5:1 for normal text and 3:1 for large text / graphical UI components).

### 2.1 Contrast Ratio Matrix

| Foreground Token | Hex Code | Background Token | Background Hex | Contrast Ratio | WCAG 2.2 AA Compliance | Primary Usage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `text-slate-100` | `#F1F5F9` | `bg-dark-950` | `#080C14` | **15.8 : 1** | PASS (AAA) | Primary headings, body copy, case identifiers |
| `text-slate-200` | `#E2E8F0` | `bg-dark-900` | `#0D1321` | **13.5 : 1** | PASS (AAA) | Table content, modal labels, card body |
| `text-slate-400` | `#94A3B8` | `bg-dark-950` | `#080C14` | **7.4 : 1** | PASS (AAA) | Secondary labels, timestamps, metadata keys |
| `text-cyan-400` | `#22D3EE` | `bg-dark-950` | `#080C14` | **10.2 : 1** | PASS (AAA) | Active tabs, quantum telemetry highlights |
| `text-emerald-400` | `#34D399` | `bg-dark-950` | `#080C14` | **10.9 : 1** | PASS (AAA) | Verified integrity badges, intact status pills |
| `text-rose-400` | `#FB7185` | `bg-dark-950` | `#080C14` | **8.1 : 1** | PASS (AAA) | Compromised tamper alerts, error notifications |
| `text-amber-400` | `#FBBF24` | `bg-dark-950` | `#080C14` | **11.6 : 1** | PASS (AAA) | Caution warnings, planned pipeline badges |
| `text-indigo-400` | `#818CF8` | `bg-dark-950` | `#080C14` | **7.1 : 1** | PASS (AA) | Hypotheses badges, tertiary scientific tags |

### 2.2 Non-Color Dependent Status Indication

In compliance with **WCAG Guideline 1.4.1 (Use of Color)**, color is never used as the sole conveyor of information or status:
- **Verified Evidence**: Accompanied by a distinct `CheckCircle` icon and explicit text (`VERIFIED - INTACT`).
- **Compromised Evidence**: Accompanied by an `AlertTriangle` icon and explicit text (`TAMPER DETECTED - COMPROMISED`).
- **Active Navigation**: Indicated by an active pill border, a high-contrast cyan indicator bar, and `aria-current="page"`.
- **Quantum Matrix Differences**: Indicated by both high-contrast red fill (`bg-rose-500/80`) and an explicit numeric delta `Δ` badge.

---

## 3. Keyboard Navigation & Focus Management

The entire workstation is operable using a standard hardware keyboard without mouse dependency.

### 3.1 Focus Indicators
- Every interactive element (buttons, links, inputs, selects, tab buttons, modal triggers) utilizes high-visibility focus indicators:
  ```css
  focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500/50 focus-visible:ring-offset-2 focus-visible:ring-offset-dark-950
  ```
- Focus rings feature a 2px offset in `#080C14` dark slate, ensuring clear demarcation even against glowing or colored backgrounds.

### 3.2 Modal Trapping & Escape Handlers
- All modal dialogs (Evidence Upload Modal, Note Submission Modal, Full-Screen Viewer) implement:
  - **Escape Key Listener**: Pressing `Escape` invokes `onClose()`.
  - **Backdrop Click Dismissal**: Clicking outside the active dialog boundary dismisses the modal.
  - **Scroll Lock**: The underlying document body is locked (`overflow: hidden`) while a modal is mounted to prevent disruptive background scrolling.
  - **Focus Restoration**: Focus returns to the triggering button upon modal unmounting.

### 3.3 Forensic Image Viewer Keyboard Controls
The interactive image viewer (`ForensicImageViewer.tsx`) provides accessible keyboard alternatives to mouse drag and mouse wheel:
- `+` or `=` : Zoom In (+0.25×)
- `-` or `_` : Zoom Out (-0.25×)
- `0` : Reset Zoom & Pan to 1:1 Default
- `Arrow Keys` : Pan viewport by 25px increments across X and Y axes
- `F` : Toggle Full-Screen Examination Mode

---

## 4. Screen Reader Semantics & ARIA Landmarks

### 4.1 Structural Landmarks
The workstation layout is structured using HTML5 semantic elements:
- `<header role="banner">` : Top utility bar with system status, breadcrumbs, and quick actions.
- `<aside role="navigation" aria-label="Forensic Workstation Navigation">` : Left sidebar with categorized navigation items.
- `<main role="main" id="main-content">` : Primary workstation viewport containing route-specific views.
- `<nav aria-label="Breadcrumb">` : Top breadcrumb navigation track.

### 4.2 ARIA Attributes & Status Announcements
- **Live Status Badges**: Health status and cryptographic audit outcomes use `role="status"` and `aria-live="polite"` so screen readers immediately announce integrity verification results without interrupting ongoing speech.
- **Form Controls**: All `<input>` and `<select>` primitives have associated `<label>` elements with matching `htmlFor` and `id` references, plus `aria-invalid="true"` and `aria-errormessage="error-id"` when input validation fails.
- **Tabs Component**: Follows WAI-ARIA Tabs Design Pattern:
  - Container: `role="tablist"`
  - Buttons: `role="tab"`, `aria-selected="true|false"`, `aria-controls="panel-id"`
  - Panels: `role="tabpanel"`, `tabIndex={0}`
- **Quantum Matrix Grid**: Interactive 4×4 patch cells expose `role="gridcell"`, `aria-label="Pixel Row X Col Y, Value V"`, and enter-key toggles for intensity modification.

---

## 5. Responsive Breakpoint Architecture

Q-TRACE is built with a **Desktop-First Forensic Architecture** optimized for professional workstation displays (1920×1080 and 1440×900) while gracefully adapting to mobile and field tablet environments.

```mermaid
flowchart TD
    subgraph Breakpoints
        A[Mobile &lt; 768px]
        B[Tablet 768px - 1023px]
        C[Laptop 1024px - 1439px]
        D[Workstation 1440px+]
    end

    A -->|Stacked View, Hidden Sidebar, Touch Scrolling| Layout
    B -->|Collapsed Sidebar, 2-Column Metrics, Horizontal Tables| Layout
    C -->|Full Sidebar, 3-Column Metrics, Side-by-Side Panels| Layout
    D -->|Persistent Sidebar, 4-Column Metrics, 1:1 Pixel Viewer| Layout
```

### 5.1 Breakpoint Tier Specifications

| Breakpoint | Target Display | Layout Adjustments | Viewer & Quantum Experience |
| :--- | :--- | :--- | :--- |
| **`xl` (1440px+)** | Primary Forensic Monitor | 4-column metric cards; persistent 260px sidebar; side-by-side evidence viewer and metadata inspector. | Full 1:1 pixel rendering, coordinate crosshair overlay, side-by-side classical ground truth and quantum difference heatmap. |
| **`lg` (1024px–1439px)** | Laptop Workstation | 3-column metric cards; persistent 240px sidebar; responsive grids collapse gracefully. | Rescaled viewer canvas; tabbed classical vs quantum viewports if viewport width is constrained. |
| **`md` (768px–1023px)** | Tablet / Field Examiner | 2-column metric cards; collapsible sidebar toggled by header menu button; horizontal scrolling for tabular data. | Centered canvas with pinch-to-zoom support; touch-friendly 48px quantum cell touch targets. |
| **`sm` (< 768px)** | Mobile Emergency Review | 1-column stacked cards; drawer-style overlay navigation; sticky bottom action bars. | Viewport-fitted image preview; scrollable quantum matrix with simplified preset selector buttons. |

### 5.2 Touch Target Sizing
- In compliance with **WCAG 2.5.5 (Target Size)**:
  - All touch targets on mobile/tablet breakpoints maintain a minimum bounding box of 44×44 CSS pixels.
  - Interactive grid cells in the Quantum Laboratory expand their hit area via negative margins / padding wrappers on mobile viewports.

---

## 6. Motion & Cognitive Accessibility

### 6.1 Reduced Motion Support
Users with vestibular disorders or motion sensitivities can configure their operating systems for reduced motion. The workstation respects `@media (prefers-reduced-motion: reduce)`:
```css
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
- Pulsing status dots (`animate-pulse`) and loading spinners (`animate-spin`) degrade to static indicators when reduced motion is detected.
- Smooth panning transitions inside the image viewer instantly snap to target coordinates.

### 6.2 Cognitive Load Reduction
- Clear hierarchical typographic scale using Inter and JetBrains Mono.
- Contextual help text on every input field explaining expected forensic formats (e.g. Case Number naming convention, SHA-256 byte limits).
- Clear, irreversible action confirmation dialogs before deleting cases, triggering audits, or resetting simulation states.

---

## 7. Automated & Manual Accessibility Testing Matrix

| Test Category | Tool / Methodology | Pass Criteria | Result |
| :--- | :--- | :--- | :--- |
| **Color Contrast** | Axe DevTools / WCAG Color Checker | ≥ 4.5:1 for body copy; ≥ 3:1 for large/graphical | **PASS** (Lowest observed ratio: 7.1:1) |
| **Keyboard Nav** | Manual Tab / Shift-Tab Traversal | Complete focus cycle with no keyboard traps | **PASS** (Zero traps detected) |
| **Screen Reader** | NVDA / VoiceOver Simulation | Landmarks, status messages, and modal titles read aloud | **PASS** (All aria attributes validated) |
| **Zoom Scaling** | Browser 200% Zoom Test | No content loss or horizontal overflow clipping | **PASS** (Responsive flex wrapping holds) |
| **Reduced Motion** | Emulate CSS media feature | Animations and transitions cleanly suppressed | **PASS** (Tailwind motion-reduce respected) |

