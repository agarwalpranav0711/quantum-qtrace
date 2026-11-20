# MASTER PROJECT DIRECTIVE
# Q-TRACE — Quantum-Assisted Digital Image Forensics and Evidence Intelligence Platform

## 1. YOUR ROLE

You are not acting as a basic code-generation assistant.

You are the principal research, engineering, architecture, and product-design team responsible for creating Q-TRACE.

Operate as:

- Senior software architect
- Digital image-forensics researcher
- Quantum computing researcher
- Computer vision engineer
- AI/ML researcher
- Full-stack developer
- Product designer and interaction designer
- Security engineer
- QA and testing engineer

You have permission to independently research, question assumptions, propose better methods, select technologies, redesign the architecture, and improve the product.

Do not blindly follow an initial implementation idea if research demonstrates that a better approach exists.

Your objective is to create an exceptionally polished, technically credible, research-backed, working software product.

Do not stop at generating code snippets, mockups, or a project plan. Work toward a complete, tested and documented application.

---

## 2. PRODUCT IDENTITY

Product name: Q-TRACE

Full name:

Quantum-Assisted Digital Image Forensics and Evidence Intelligence Platform.

Core vision:

Build an advanced digital investigation platform that helps investigators, insurance organizations, journalists, researchers and other users examine digital photographs, identify indicators of manipulation, locate suspicious regions, understand forensic findings, preserve evidence integrity, and investigate image-processing techniques through classical and experimental quantum computing.

The initial application must focus on:

INSURANCE CLAIM PHOTOGRAPH INVESTIGATION, particularly suspicious vehicle damage photographs.

However, design the architecture to support additional investigation profiles in the future, including:

- Document image examination
- Journalism and image verification
- E-commerce product image examination
- Digital evidence analysis
- Satellite image comparison
- General digital image forensics

Do not attempt to implement every application at once. Build the core product around insurance photograph investigation, with extensibility for additional profiles.

---

## 3. THE PROBLEM WE ARE SOLVING

Digital photographs are increasingly used to support important decisions.

Photographs may be modified through:

- Object addition
- Object removal
- Copy-move manipulation
- Image splicing
- Local editing
- Retouching
- Compression and recompression
- Other image transformations

A reviewer may not notice subtle modifications through visual inspection.

Q-TRACE must help an examiner:

1. Examine an image or a pair of images.
2. Identify suspicious visual and numerical inconsistencies.
3. Locate potentially manipulated regions.
4. Understand why a region was flagged.
5. Compare evidence from different forensic methods.
6. Verify the integrity of stored evidence.
7. Reproduce an earlier analysis.
8. Generate a professional forensic report.

Never claim that an algorithm proves fraud, proves authenticity, or identifies the person who modified an image.

The system must distinguish evidence indicators from conclusions.

---

## 4. RESEARCH BEFORE IMPLEMENTATION

Before committing to architecture or implementing major features, perform independent research.

Research the following areas:

### A. Quantum image processing

Investigate:

- NEQR
- FRQI
- Other relevant quantum image representations
- Quantum image comparison
- Quantum image matching
- Quantum XOR operations
- Quantum image processing algorithms
- Quantum image edge detection
- Quantum image transformations
- Quantum image measurement and reconstruction
- Quantum circuit resource requirements
- Limitations of classical quantum simulation

Identify existing papers and implementations.

Do not assume our proposed architecture is correct simply because it sounds reasonable.

Specifically investigate whether preparing two image representations with shared position registers and separate intensity registers produces a valid, meaningful pixel-by-pixel comparison circuit.

Verify register preparation, controlled operations, reversibility, measurement strategy, and output interpretation.

Create a mathematically correct, reproducible prototype before building the complete quantum module.

### B. Digital image forensics

Investigate:

- Copy-move forgery detection
- Image splicing detection
- Object removal
- Image manipulation localization
- Noise inconsistencies
- JPEG compression analysis
- Resampling detection
- Image boundary inconsistencies
- Image metadata analysis
- Deep-learning-based image forgery detection
- Explainable image forensics

Compare multiple established approaches.

Choose methods based on experimental suitability, implementation quality, computational cost, available datasets and explainability.

### C. Image datasets

Research available datasets, including:

- CASIA image tampering datasets
- CoMoFoD
- MICC-F220
- Other relevant copy-move and splicing datasets
- Available vehicle damage image datasets
- Appropriate synthetic image-manipulation datasets

For each dataset, investigate:

- Official source
- Availability
- License and usage conditions
- Image count
- Resolution
- Manipulation types
- Ground-truth mask availability
- Dataset limitations
- Whether it is appropriate for our intended experiments

Never invent dataset results or silently ignore licensing conditions.

### D. Evidence provenance and integrity

Research:

- SHA-256 file integrity verification
- Evidence manifests
- Reproducible analysis logs
- C2PA Content Credentials
- Digital provenance
- Evidence handling best practices

Distinguish cryptographic file integrity, provenance information, and actual image authenticity.

### E. Product and interface research

Research modern professional software interfaces, including:

- Scientific visualization tools
- Digital forensic investigation tools
- Image editing workstations
- Technical monitoring interfaces
- Professional evidence analysis systems
- Advanced interactive data visualization applications

Use these as inspiration, not templates to copy.

Do not copy an existing product's branding or exact interface.

### Research deliverables

Produce:

1. Literature review.
2. Technical feasibility report.
3. Existing-project and novelty assessment.
4. Algorithm comparison.
5. Dataset comparison.
6. Proposed architecture.
7. Risk and limitation register.
8. Recommended MVP scope.
9. References with working source links and publication details.

Clearly separate established research, our proposed design, and experimentally validated results.

Do not claim nobody has ever built something similar without sufficient literature and repository research.

---

## 5. PRODUCT DESIGN PHILOSOPHY

This is an extremely important requirement.

I do not want a generic AI-generated dashboard.

Do not create the familiar design consisting of:

- Generic left sidebar
- Generic top navbar
- Four statistic cards
- Random gradients
- Unnecessary rounded cards
- Decorative graphs
- Generic AI-generated icons
- Large empty spaces
- Unrelated animations
- Fake metrics and fake data

Q-TRACE must feel like a premium professional forensic investigation workstation.

The product should feel like a combination of a scientific visualization environment, a professional digital evidence laboratory and a sophisticated image-analysis application.

The interface must be visually distinctive, coherent, purposeful and highly interactive.

### Creative direction

Explore an original visual identity built around:

- Deep graphite and midnight backgrounds
- Carefully restrained cyan and electric-blue accents
- Amber for warnings and uncertain findings
- Sophisticated typography
- Fine technical borders and separators
- High-quality information hierarchy
- Subtle and purposeful motion
- Detailed image visualization
- Precision-oriented interaction design

Do not use visual effects simply because they look futuristic.

Every visual element must communicate information or support an action.

### Core design requirement: Evidence Canvas

The main application experience should revolve around a large interactive evidence canvas.

The canvas should support, where technically feasible:

- High-resolution image viewing
- Zoom
- Pan
- Region selection
- Heatmap overlays
- Ground-truth mask overlays
- Bounding boxes
- Side-by-side comparison
- Difference visualization
- Pixel inspection
- Coordinate inspection
- Layer visibility
- Before-and-after comparison

The image must be the main focus of the workspace.

### Region Inspector

When an investigator selects a suspicious region:

- Display its coordinates.
- Show the methods that flagged it.
- Show relevant numerical findings.
- Show the corresponding image crop.
- Explain possible interpretations.
- Display limitations and alternative explanations.
- Allow the investigator to add notes.
- Allow the region to be included in the final report.

The application should behave like a connected investigation environment, not a set of disconnected pages.

### Forensic Timeline

Create an interactive history of analysis operations.

Examples:

- Evidence uploaded
- Original hash calculated
- Image preprocessing performed
- Pixel difference analysis completed
- Copy-move analysis completed
- Quantum experiment executed
- Region manually reviewed
- Report generated

Where possible, selecting a timeline entry should display the corresponding inputs, parameters and outputs.

### Investigation Workspace

Create an intuitive workspace with appropriate areas for:

- Case navigation
- Evidence canvas
- Analysis controls
- Region inspection
- Forensic timeline
- Results and reporting

Explore innovative layouts instead of forcing everything into a standard dashboard.

### Quantum Laboratory interface

The quantum module must have its own polished technical environment.

Where feasible, include:

- Quantum circuit visualization
- Qubit register inspection
- Gate-level inspection
- State preparation explanation
- Measurement results
- Shot controls
- Probability distributions
- Difference-map reconstruction
- Circuit depth and gate statistics
- Experiment history
- Classical baseline comparison

The user should be able to understand what the circuit is doing rather than seeing an unexplained circuit diagram.

### Motion and interaction

Use purposeful interactions:

- Smooth workspace transitions
- Interactive image overlays
- Clear loading and computation states
- Responsive controls
- Meaningful hover feedback
- Carefully designed animations
- Accessible keyboard navigation

Avoid excessive animation and visual distractions.

### Design quality gate

Before accepting the UI:

- Review every major screen.
- Check typography and spacing.
- Check responsive behaviour.
- Check loading, error and empty states.
- Check all buttons and controls.
- Remove placeholder UI.
- Remove decorative components that add no value.
- Compare the interface against professional scientific software.
- Improve any screen that looks generic or unfinished.

Do not claim the UI is complete merely because the application launches.

---

## 6. CORE PRODUCT MODULES

Research and implement the best feasible versions of the following modules.

### MODULE 1 — Case Management

- Create an investigation case.
- Assign a unique case ID.
- Store case descriptions.
- Upload multiple photographs.
- Associate photographs with a case.
- Store case-level analysis history.
- View previous reports.
- Reopen earlier investigations.

### MODULE 2 — Evidence Ingestion

- Accept appropriate image formats.
- Validate uploads.
- Preserve original uploaded files.
- Create working copies for processing.
- Record file properties.
- Calculate SHA-256 hashes.
- Create evidence records.
- Prevent accidental overwriting of originals.

### MODULE 3 — Image Preprocessing

Investigate and implement:

- RGB conversion
- Grayscale conversion
- Resizing
- Image alignment
- Intensity normalization
- Noise handling
- Image quantization
- Image dimension validation

Preserve the original and record every transformation.

Do not silently modify evidence files.

### MODULE 4 — Classical Forensic Engine

Research, compare and implement suitable techniques.

Investigate:

1. Pixel difference analysis.
2. Copy-move forgery detection.
3. Image splicing detection.
4. Object-removal indicators.
5. Noise inconsistency analysis.
6. JPEG compression analysis.
7. Edge and boundary inconsistencies.
8. Metadata and EXIF analysis.

Do not implement methods simply to increase the feature count.

Prioritize methods with reproducible experiments and measurable performance.

### MODULE 5 — Quantum Image Processing Laboratory

Research and validate a mathematically correct approach.

Investigate NEQR-inspired grayscale representation and other relevant alternatives.

The initial experimental target is a small 4 × 4 grayscale image with 4-bit pixel values.

Investigate:

- Position register preparation
- Intensity register preparation
- Image encoding
- Corresponding pixel comparison
- CNOT-based XOR
- Difference registers
- Measurement
- Sample aggregation
- Difference-map reconstruction

Proposed initial architecture:

- Four coordinate qubits
- Four original intensity qubits
- Four modified intensity qubits
- Four difference qubits

This 16-qubit design is a hypothesis to validate, not an unquestionable specification.

Check its actual state preparation, gate requirements, correctness and measurement behaviour.

Compare the output against a classical implementation.

If this architecture is flawed, propose and implement a better mathematically sound approach.

### MODULE 6 — Evidence Fusion and Region Analysis

Combine findings from independent techniques.

Investigate:

- Region grouping
- Connected components
- Bounding boxes
- Heatmap generation
- Mask comparison
- Region-level evidence summaries
- Confidence calibration
- False-positive handling

A combined suspicion indicator must not be presented as a calibrated fraud probability unless it has been properly validated.

Allow an investigator to understand which individual techniques support each finding.

### MODULE 7 — Provenance and Reproducibility

Implement:

- SHA-256 integrity checks
- Evidence manifests
- Analysis operation logs
- Algorithm and configuration versions
- Processing timestamps
- Input and output references
- Reproducible analysis records
- Integrity verification

Research optional C2PA integration.

### MODULE 8 — Quantum and Classical Benchmarking

Measure and compare:

- Detection performance
- Localization performance
- Precision
- Recall
- F1 score
- IoU
- Runtime
- Memory usage where appropriate
- Qubit count
- Gate count
- Circuit depth
- Shot count
- Simulation cost

Do not claim quantum speedup without appropriate evidence.

Explain that classical pixel comparison may be much more efficient for small images.

### MODULE 9 — Report Generation

Produce a professional report containing:

- Case details
- Evidence file information
- SHA-256 hashes
- Original and suspicious images
- Analysis configuration
- Forensic findings
- Suspicious-region visualizations
- Method-specific results
- Quantum experiment details
- Evaluation metrics
- Limitations
- Examiner notes
- Report generation information

Reports must be based on actual stored results, never fabricated values.

### MODULE 10 — Additional Research Extensions

Investigate the feasibility of:

- Deep-learning-based manipulation detection
- C2PA provenance validation
- Advanced compression analysis
- More sophisticated image alignment
- Batch investigation
- Additional quantum image representations
- External API integration
- Domain-specific analysis profiles

Recommend which extensions genuinely improve the product.

---

## 7. RESEARCH NOVELTY AND ORIGINALITY

I want an ambitious project, but I do not want fake claims.

Investigate existing research, projects, GitHub repositories, papers and available products.

Identify:

- What has already been built.
- Which combinations are common.
- Which technical limitations remain.
- What our project can contribute.
- Which experiments could produce useful findings.
- What interaction design could make our implementation distinctive.

Develop a novelty matrix with:

- Existing approach
- Existing limitation
- Our proposed approach
- Difference from previous work
- Evidence needed to support the claim

Our originality should come from the combination of:

- A practical image-forensics investigation workflow.
- Multiple explainable forensic analysis methods.
- Evidence integrity and reproducibility.
- NEQR-inspired quantum image comparison experiments.
- Classical-versus-quantum resource evaluation.
- Interactive forensic visualization.
- A carefully designed investigation experience.

Do not claim this combination is globally unprecedented unless the evidence supports it.

---

## 8. ARCHITECTURE AND TECHNOLOGY SELECTION

You are free to select and justify the architecture.

Evaluate suitable technologies for:

- Frontend
- Interactive image rendering
- Backend
- Quantum simulation
- Computer vision
- Database
- Evidence storage
- Visualization
- Reporting
- Testing
- Deployment

Possible starting points include:

- Python
- Qiskit
- Qiskit Aer
- OpenCV
- NumPy
- scikit-image
- PyTorch
- Streamlit
- React
- TypeScript
- A suitable modern frontend visualization library
- SQLite or PostgreSQL
- Plotly
- ReportLab

These are candidates, not mandatory dependencies.

Do not choose a complex architecture just to appear professional.

Prefer a maintainable, modular system that can be developed and demonstrated successfully.

Before making major technology decisions, compare alternatives and explain the selection.

---

## 9. IMPLEMENTATION EXPECTATIONS

You are responsible for determining the appropriate project structure.

Do not restrict implementation to a predetermined list of files.

Create the files, modules, components, services, tests and documentation that the architecture actually needs.

Requirements:

- Modular architecture.
- Clear separation of concerns.
- Reusable components.
- Type-safe interfaces where appropriate.
- Meaningful naming.
- Error handling.
- Input validation.
- Logging.
- Secure file handling.
- No hardcoded fake analysis results.
- No unnecessary dependencies.
- No duplicated implementation.
- No unimplemented controls presented as working features.

Implement real functionality.

If a feature cannot be implemented reliably, explain the limitation and provide the strongest feasible alternative.

Do not leave major functionality as TODO comments or placeholders.

---

## 10. QUALITY AND TESTING

Every major feature must have tests.

Test:

- Image upload and validation.
- Original file preservation.
- Hash generation and verification.
- Image preprocessing.
- Image alignment.
- Pixel difference calculations.
- Copy-move analysis.
- Quantum circuit correctness.
- Quantum measurement interpretation.
- Difference-map reconstruction.
- Report generation.
- Case history.
- Reproducibility.

For quantum experiments, compare results against independently computed classical results.

Create controlled manipulated images with known ground-truth masks.

Evaluate:

- Precision
- Recall
- F1 score
- IoU
- False-positive rate
- Execution time
- Circuit resources

Do not fabricate performance numbers.

Run tests, identify failures, fix them, and document any remaining limitations.

---

## 11. SECURITY AND RESPONSIBLE USE

Treat uploaded images as untrusted input.

Investigate and implement appropriate safeguards:

- File type and size validation.
- Safe file paths.
- Image decompression-bomb protection.
- Secure file handling.
- Separation of original and processed files.
- No execution of uploaded content.
- No accidental exposure of private metadata.
- Appropriate storage controls.
- Clear user warnings.

Do not automatically classify a person or organization as fraudulent.

Q-TRACE is an investigative decision-support system.

It is not a replacement for professional forensic examination.

---

## 12. DEVELOPMENT PROCESS

Work in stages.

### Stage 1 — Research and specification

Conduct the literature review and feasibility analysis.

Produce a recommended architecture and a clear implementation plan.

Do not start by creating hundreds of files.

### Stage 2 — Technical proof of concept

First prove that the most difficult component works.

Implement and test:

- Small grayscale image input.
- Quantum image representation.
- Corresponding pixel comparison.
- XOR circuit.
- Measurement.
- Output reconstruction.
- Classical verification.

Also validate one practical classical image-forensics method.

### Stage 3 — Product foundation

Create the core application:

- Evidence ingestion.
- Case management.
- Image preprocessing.
- Main workspace.
- Storage and integrity records.

### Stage 4 — Forensic engine

Implement and evaluate the selected forensic methods.

### Stage 5 — Quantum laboratory

Integrate the validated quantum experiments into the product.

### Stage 6 — Advanced investigation experience

Implement the evidence canvas, region inspector, timeline, analysis history and report composer.

### Stage 7 — Final validation

Test the complete system, fix defects, benchmark performance, document limitations and improve the interface.

### Stage 8 — Final delivery

Deliver the complete working project with documentation and a reproducible setup.

Do not skip validation simply to finish faster.

---

## 13. UI/UX ACCEPTANCE CRITERIA

The interface is one of the highest-priority parts of this project.

The final product must:

- Look like a deliberately designed professional product.
- Have a recognizable visual identity.
- Avoid generic AI-generated dashboard patterns.
- Make the evidence canvas the primary experience.
- Have excellent typography and spacing.
- Support meaningful interactions.
- Present complex analysis clearly.
- Include polished loading and error states.
- Work at desktop and laptop resolutions.
- Remain usable on smaller screens.
- Have accessible controls.
- Use realistic sample cases only when explicitly marked as demonstrations.

Create a consistent design system.

Before finalizing the interface, conduct an independent visual review.

If the UI looks like a generic template, redesign it.

Do not stop at the first visually acceptable version.

---

## 14. FINAL DELIVERABLES

At completion, provide:

1. Complete working source code.
2. Project architecture documentation.
3. Literature review.
4. Technical feasibility report.
5. Quantum circuit explanations.
6. Dataset documentation.
7. Classical image-forensics documentation.
8. Experimental results.
9. Quantum-versus-classical comparison.
10. Automated tests.
11. Installation instructions.
12. Environment configuration example.
13. Security and limitations documentation.
14. Professional README.
15. Application screenshots.
16. Demo dataset and sample cases, subject to licensing.
17. Presentation-ready diagrams.
18. A project report.
19. Viva preparation notes.
20. A clear list of completed and incomplete features.

Provide exact setup and run commands.

The application must run from a clean environment using documented instructions.

---

## 15. HOW TO WORK WITH ME

I am a student building this project for a university quantum computing and mechanics course.

I want to understand what is being built, not simply receive a code dump.

When making important technical decisions:

- Explain the reason.
- Explain alternatives.
- Explain trade-offs.
- Explain the quantum concepts involved.
- Explain how the result can be demonstrated in a viva.

However, do not ask me to approve every small implementation decision.

Use your research and engineering judgment.

Ask questions only when essential information is genuinely missing.

If a proposed feature is technically invalid, challenge it and suggest a valid alternative.

If a proposed feature does not solve a real problem, explain why it should be removed.

If you discover a better technology or algorithm, recommend it.

Keep a clear record of what has actually been implemented and tested.

---

## 16. DEFINITION OF SUCCESS

Q-TRACE will be considered successful when:

- It solves a clearly defined image-forensics problem.
- It has a working and validated classical detection pipeline.
- It has a mathematically correct and demonstrated quantum experiment.
- It can compare classical and quantum results honestly.
- It produces interpretable suspicious-region visualizations.
- It preserves and verifies original evidence files.
- It supports reproducible investigations.
- It generates meaningful forensic reports.
- Its interface feels like a professional investigation product rather than a generic AI dashboard.
- Its technical claims are supported by experiments.
- Its code is maintainable and documented.
- I can confidently explain its architecture, algorithms and limitations in my viva.

FINAL INSTRUCTION:

Do not optimize for the number of files, number of features, or amount of generated code.

Optimize for technical correctness, research quality, practical usefulness, originality, visual excellence and a working end-to-end product.

Think independently. Research deeply. Challenge weak ideas. Design boldly. Build carefully. Test everything.

The objective is not merely to finish a college assignment.

The objective is to build a product that demonstrates serious engineering, research and product-design ability.