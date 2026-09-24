# Codex conversation

## User

Look into all the dataset files in the directory and provide where to start pre-processing. I want to pre-process the data, encoding and feature engineering. Provide a doc on which file/files to start and what to do. The instructions shld be filewise and the useful files should be considered. The processed files will run through ML pipelines to be decided later.

## Assistant

I’ll inventory the data files, profile their schemas and quality, then produce a file-by-file preprocessing and feature-engineering guide for the ML stage. I’m using the document workflow so the deliverable is a reviewable document rather than just chat notes.

## Activity

    $ Get-Location
    
    Path
    ----
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data
    
    
    ✓ • 574ms

## Activity

    $ Get-Content -Raw 'C:\Users\nitin\.codex\plugins\cache\openai-primary-runtime\documents\26.819.11345\skills\documents\SKILL.md'
    ---
    name: documents
    description: Create, edit, redline, and comment on `.docx`, Word, and Google Docs-targeted document artifacts inside the container, with a strict render-and-verify workflow. Use `render_docx.py` to generate page PNGs (and optional PDF) for visual QA, then iterate until layout is flawless before delivering the final document.
    ---
    
    # Documents Skill (Read â€¢ Create â€¢ Edit â€¢ Redline â€¢ Comment)
    
    Use this skill when you need to create or modify `.docx`, Word, or Google
    Docs-targeted document artifacts **in this container environment** and verify
    them visually.
    
    ## Tools + Contract
    
    - Use Codex workspace dependencies for docx artifact work: resolve them through the workspace dependency loader or runtime skill, then treat the returned Node/Python runtimes and package directory as authoritative. Do not use system `node`, system `python`, global npm packages, or repo-local installs.
    - For document creation and deterministic OOXML edits, it is still acceptable to use the bundled Python/OOXML helper scripts in this skill package when the JS surface is incomplete.
    - Run any builder or helper file from a writable workspace or temp directory, not from the managed dependency directory itself.
    - Final user-facing responses should describe only the requested document result. Do not link QA intermediates unless the user explicitly asks for them.
    
    ## Artifact Template Selection
    
    Open the template selection picker for creating new documents when the user has not provided a template, reference, or visual direction. Also open the picker when the user asks to browse or upload templates. Do not open it if the user declines templates or requests a connected-source design search. Subject matter, audience, tone, company names, and source files do not by themselves specify a template or visual direction.
    
    Call `list_artifact_templates({artifactKind, request})` with `artifactKind: "document"`, or `"google-docs"` for Google Docs requests. Include compatible Office and Google templates without changing the requested output format.
    
    Rank templates by relevance, breaking ties in favor of personal or shared templates. Include a mix of styles. Pass their `skillName` values unchanged to `choose_artifact_template({artifactKind, request, templates})` and call it once. Set `includeAllTemplates: true` only when the user requests the full catalog. The picker displays at most ten templates.
    
    Follow the selected template or uploaded reference. Save an uploaded reference only when `saveForFutureUse` is true. Use Template Creator with the returned `displayName`. Continue without a template if the picker is declined, cancelled, unavailable, or fails. Do not replace the picker with `request_user_input` or a chat list. Browsing templates does not authorize artifact creation.
    
    Immediately before the first create/edit authoring command, run `mark_artifact_operation_started.mjs` successfully exactly once using the command below. Do not run it for read-only work. For edits, replace `create` with `edit`; adjust the expected count and output format to match the requested outputs.
    
    ```bash
    node container_tools/mark_artifact_operation_started.mjs --operation-kind create --expected-output-count 1 --output-format docx
    ```
    
    ## Google Docs-targeted output
    
    For a net-new Google Docs request, create and visually verify a local `.docx` with this skill first. The native Google Docs deliverable must then be produced by the Google Drive plugin's document import action, `mcp__codex_apps__google_drive_import_document`, with `upload_mode: "native_google_docs"`.
    
    Before rendering or importing any Google Docs-targeted DOCX, run the deterministic title sanitizer:
    
    ```bash
    python scripts/google_docs_title_sanitize.py input.docx --out sanitized.docx
    python scripts/google_docs_title_sanitize.py sanitized.docx --check
    ```
    
    Use the sanitized DOCX for render QA and native Google Docs import. This is not a style preference or prose reminder: the sanitizer removes Word `Title` paragraph-style border residue, direct title-paragraph borders, and leading title-block paragraph borders from the OOXML so Word's built-in blue title rule cannot survive into the imported Google Doc.
    
    Do not use Computer Use, Browser Use, blank-Google-Doc creation plus Google Docs write APIs, or another direct-to-Docs construction path for net-new Google Docs unless the user explicitly asks for that alternate workflow. If they do, mention first that output quality is expected to be best when a local `.docx` is imported through the Google Drive plugin.
    
    If the Google Drive plugin is unavailable, use the plugin-install/user-elicitation flow to ask the user to install `google-drive@openai-curated`. If the plugin is available but `_import_document` is missing, ask the user to reinstall or refresh the Google Drive plugin before continuing with the native Google Docs deliverable.
    
    ## Template Following
    
    When an attached or retained DOCX is meant to control a new document, read
    `template-distill.md` and then `template-create.md`. Keep the reference file and
    the task-local `$TMP_DIR/artifact.md` together throughout authoring. In this
    mode, the retained reference is the design authority: do not apply a generic
    design preset, page baseline, or header pattern unless the user explicitly asks
    to depart from the template. The render gate and Google Docs import contract
    still apply. For a Google Docs-targeted result, record any change made by the
    required title sanitizer as an intentional fidelity deviation.
    
    ## Non-negotiable: render â†’ inspect PNGs â†’ iterate
    
    **You do not â€œknowâ€ a DOCX is satisfactory until youâ€™ve rendered it and visually inspected page images.**
    DOCX text extraction (or reading XML) will miss layout defects: clipping, overlap, missing glyphs, broken tables, spacing drift, and header/footer issues.
    
    **Shipping gate:** before delivering any DOCX, you must:
    - Run `render_docx.py` to produce `page-<N>.png` images (optionally also a PDF with `--emit_pdf`)
    - Open the PNGs (100% zoom) and confirm every page is clean
    - If anything looks off, fix the DOCX and **re-render** (repeat until flawless)
    
    If rendering fails because LibreOffice/`soffice` is missing, it is acceptable to return the requested DOCX without rendered PNG QA. In that fallback case, use the relevant Markdown task docs in this skill package as the authoritative guidance for building and checking the document structurally, state clearly in the final response that rendering/visual QA could not be completed, and do not imply that the document passed the render gate.
    
    If rendering fails for any other reason, fix rendering first (LibreOffice profile/HOME, conversion errors, or renderer setup) rather than guessing.
    
    **Deliverable discipline:** Rendered artifacts (PNGs and optional PDFs) are for internal QA only. Unless the user explicitly asks for intermediates, **return only the requested final deliverable** (e.g., when the task asks for a DOCX, deliver the DOCX â€” not page images or PDFs).
    
    ## Design Preset Contract
    
    Outside template-following mode, a design preset is mandatory for new DOCX creation and major rewrites unless the user explicitly asks for a different visual system. For existing-document edit tasks, preserve the original document and apply the minimal local edits described later in this skill.
    
    Picking a preset is not enough. You must resolve the preset into exact numeric tokens and apply those numbers in the DOCX implementation. Do not rely on Word defaults, built-in list styles, theme defaults, inherited paragraph spacing, or renderer-dependent behavior for any preset-controlled value.
    
    Before writing content, read `references/design_presets.md` and choose exactly one preset:
    
    - `google_docs_default` for any net-new document whose destination is a native Google Doc, unless the user explicitly asks for a special, branded, or highly polished visual treatment.
    - `standard_business_brief` for formal memos, RFI responses, decision memos, and board-style briefs.
    - `compact_reference_guide` for launch guides, negotiation briefs, checklists, and dense operator references.
    - `narrative_proposal` for grants, proposals, and persuasive documents with longer prose.
    - Use an archetype alias from the reference file when it is a closer match: `rfi_response`, `decision_memo`, `launch_messaging_guide`, `contract_negotiation_brief`, `neighborhood_business_proposal`, or `grant_proposal`.
    
    If the destination is Google Docs, choose `google_docs_default`. Google Docs-targeted documents should feel native: Arial-based typography, black hierarchy, simple title treatment.
    
    For Google Docs-targeted documents, never create the title with the built-in Word `Title` paragraph style, including `doc.add_paragraph(..., style="Title")` or `doc.add_paragraph(style="Title")`. Always create a plain paragraph and apply the selected style-sheet title tokens directly: font family, size, color, weight, spacing, and border/rule settings. For `google_docs_default`, that means Arial 26 pt, black, normal weight, 0 pt before, 3 pt after, and no underline, bottom border, horizontal rule, or other Word-template residue. This instruction is not the enforcement layer; `scripts/google_docs_title_sanitize.py` is the deterministic enforcement layer and must still run before render/import.
    
    If creating a new first-page header, cover, or title block for a non-Google-docs document, also read `references/header_templates.md` and choose one header pattern before drafting. For `google_docs_default`, keep the opening block simple unless the user explicitly requests richer first-page furniture.
    
    Then resolve the preset into a token map and apply the tokens consistently:
    
    1. Set page, margin, type scale, paragraph rhythm, heading, list, table, callout, header, footer, and color tokens before drafting. For `google_docs_default`, that means explicitly carrying the simple Google Docs defaults instead of inheriting the more polished Word-oriented defaults above.
    2. Implement those tokens through Word styles, real numbering definitions, explicit table geometry, and header/footer parts. Do not fake headings, lists, or tables with one-off direct formatting.
    3. Use ad-hoc formatting only when the document needs a specific exception; record the exception as a named override and reuse it consistently wherever that role appears.
    4. Keep the preset stable throughout the document. Do not mix body spacing, heading colors, list indents, table fills, or page furniture from multiple presets.
    
    Baseline geometry for all presets: US Letter portrait, 1 inch margins, 9360 DXA usable width, real Word styles for Normal/Title/Subtitle/Heading 1/Heading 2/Heading 3, real Word numbering for lists, and DXA table widths only.
    
    Tables must use explicit Word geometry. Build rows first, compute exact DXA column widths, then use `scripts/table_geometry.py` or equivalent logic so `tblW`, `tblInd`, `tblGrid`, and every `tcW` agree. Set table indent to the start cell margin token (`120` DXA by default) so the visible outer border aligns with surrounding paragraph text. Do not rely on autofit, percentage widths, centered default tables, fixed row heights, or tables as layout/divider hacks.
    
    Lists must use real numbering definitions. Never create fake bullets with Unicode bullet text, hyphen-prefixed paragraphs, manual numbers, or newline-separated list items inside one paragraph. Wrapped list lines must align under the item text, not under the marker.
    
    Before final render review, run a preset audit: page geometry, styles, heading spacing/colors, list indents, table widths/table indents/cell margins, callout fills, headers/footers, and direct-formatting exceptions must match the selected token map. Also check for fake headings, fake bullets, missing table geometry, clipped/pinned table text, inconsistent page furniture, and unexplained direct formatting drift. For `google_docs_default`, fail the audit if the title style or title paragraph contains `w:pBdr`, a bottom border, an underline, a horizontal rule, or any rendered decorative line under the title.
    
    ## Form factor selection
    
    For new DOCX creation and major rewrites, choose content form factors deliberately before drafting. Start from the information type, then calibrate the structure to the document archetype. Use the lightest readable structure that helps the reader understand, compare, act on, or fill in the information with the least friction.
    
    First map each major content unit to a form factor:
    
    - PROSE SECTION: narrative, explanation, background, or rationale. Use paragraphs under clear headings, with short supporting bullets only when they improve skimming.
    - LEAD CALLOUT: decision, recommendation, or key takeaway. Use a short labeled paragraph, callout, or lead paragraph followed by concise rationale.
    - NUMBERED STEPS: sequence, workflow, or procedure. Use step blocks with clear action verbs; add owner/status fields only when they are central to execution.
    - GROUPED BULLETS: loose factors, considerations, pros/cons, or requirements. Use bullets or short subsections when order is not the main point.
    - CHECKLIST: actions, acceptance checks, or review criteria. Use compact labels and enough spacing to scan.
    - NOTE BOX: warnings, caveats, constraints, or important notes. Use a callout with restrained emphasis.
    - DEFINITION LIST: definitions, metadata, or key facts. Use labeled paragraphs, definition lists, or compact key-value blocks.
    - TABLE: repeated comparable records, status grids, budgets, RFI/compliance matrices, or schedules with shared fields.
    - FORM LAYOUT: forms and questionnaires. Use readable fields, sectioning, and response space; use grids only where repeated response structure helps completion.
    - SOURCE LIST: evidence, citations, and sources. Use footnotes, endnotes, short source lists, or appendices according to document type and density.
    
    ### Table Gate
    
    Use a table only when the content is truly row/column data: repeated items, shared fields, and useful comparison or lookup.
    
    Do not use tables to package normal prose. If cells become mini-paragraphs, switch to prose sections, bullets, steps, checklists, callouts, or appendix material.
    
    Before finalizing, run a table-overuse audit:
    
    - If most cells in a table are sentence- or paragraph-length prose, convert that section to prose, bullets, steps, callouts, or labeled paragraphs.
    - If two or more adjacent sections use tables, check whether at least one should become bullets or paragraphs for readability.
    
    During render review, check content diversity and archetype fit. If multiple adjacent components use the same visual form, decide whether one should become prose, bullets, steps, a callout, or an appendix. The goal is not variety for its own sake; it is to match form to reading task and document purpose.
    
    ## Design standards for document generation
    
    For generating new documents or major rewrite/repackages, follow the design standards below unless the user explicitly requests otherwise. The user's instructions always take precedence; otherwise, adhere to these standards.
    
    When creating the document design, do not compromise on the content and make factual/technical errors. Do not produce something that looks polished but not actually what the user requested.
    
    It is very important that the document is professional and aesthetically pleasing. As such, you should follow this general workflow to make your final delivered document:
    
    1. Before you make the DOCX, please first think about the high-level design of the DOCX:
       - Before creating the document, decide what kind of document it is (for example, a memo, report, SOP, workflow, form, proposal, or manual) and design accordingly. In general, you shall create documents which are professional, visually polished, and aesthetically pleasing. However, you should also calibrate the level of styling to the document's purpose: for formal, serious, or highly utilitarian documents, visual appeal should come mainly from strong typography, spacing, hierarchy, and overall polish rather than expressive styling. The goal is for the document's visual character to feel appropriate to its real-world use case, with readability and usability always taking priority.
       - You should make documents that feel visually natural. If a human looks at your document, they should find the design natural and smooth. This is very important; please think carefully about how to achieve this.
       - Think about how you would like the first page to be organized. How about subsequent pages? What about the placement of the title? What does the heading ladder look like? Should there be a clear hierarchy? etc
       - Which form factors should represent each type of information, such as prose sections, bullets, numbered steps, checklists, callouts, tables, forms, images, or appendices? Plan the design for each chosen component.
       - Think about the general spacing and layout. What will be the default body spacing? What page budget is allocated between packaging and substance? How will page breaks behave around tables and figures, since we must make sure to avoid large blank gaps, keep captions and their visuals together when possible, and keep content from becoming too wide by maintaining generous side margins so the page feels balanced and natural.
       - Think about font, type scale, consistent accent treatment, etc. Try to avoid forcing large chunks of small text into narrow areas. When space is tight, adjust font size, line breaks, alignment, or layout instead of cramming in more text.
    2. Once you have a working DOCX, continue iterating until the entire document is polished and correct. After every change or edit, render the DOCX and review it carefully to evaluate the result. If LibreOffice/`soffice` is missing, continue using the relevant Markdown task docs in this skill package for structural QA and document-design guidance, and disclose that visual render QA was skipped. The plan from (1) should guide you, but it is only a flexible draft; you should update your decisions as needed throughout the revision process. Important: each time you render and reflect, you should check for both:
    
       1. Design aesthetics: the document should be aesthetically pleasing and easy to skim. Ask yourself: if a human were to look at my document, would they find it aesthetically nice? It should feel natural, smooth, and visually cohesive.
       2. Formatting issues that need to be fixed: e.g. text overlap, overflow, cramped spacing between adjacent elements, awkward spacing in tables/charts, awkward page breaks, etc. This is super important. Do not stop revising until all formatting issues are fixed.
    
    While making and revising the DOCX, please adhere to and check against these quality reminders, to ensure the deliverable is visually high quality:
    
    - Document density: Try to avoid having verbose dense walls of text, unless it's necessary. Avoid long runs of consecutive plain paragraphs or too many words before visual anchors. For some tasks this may be necessary (i.e. verbose legal documents); in those cases ignore this suggestion.
    - Font: Use professional, easy-to-read font choices with appropriate size that is not too small. Usage of bold, underlines, and italics should be professional.
    - Color: Use color intentionally for titles, headings, subheadings, and selective emphasis so important information stands out in a visually appealing way. The palette and intensity should fit the document's purpose, with more restrained use where a formal or serious tone is needed.
    - Visuals: Consider using varied form factors, including diagrams and other visual components, when they improve comprehension, navigation, or usability.
    - Tables: Please invest significant effort to make sure your tables are well-made and aesthetically/visually good. Below are some suggestions, as well as some hard constraints that you must relentlessly check to make sure your table satisfies them.
      - Suggestions:
        - Set deliberate table/cell widths and heights instead of defaulting to full page width.
        - Choose column widths intentionally rather than giving every column equal width by default. Very short fields (for example: item number, checkbox, score, result, year, date, or status) should usually be kept compact, while wider columns should be reserved for longer content.
        - Avoid overly wide tables, and leave generous side margins so the layout feels natural.
        - Keep all text vertically centered and make deliberate horizontal alignment choices.
        - Ensure cell height avoids a crowded look. Leave clear vertical spacing between a table and its caption or following text.
      - Hard constraints:
        - To prevent clipping/overflow:
          - Never use fixed row heights that can truncate text; allow rows to expand with wrapped content.
          - Ensure cell padding and line spacing are sufficient so descenders/ascenders don't get clipped.
          - If content is tight, prefer (in order): wrap text -> adjust column widths -> reduce font slightly -> abbreviate headers/use two-line headers.
        - Padding / breathing room: Ensure text doesn't sit against cell borders or look "pinned" to the upper-left. Favor generous internal padding on all sides, and keep it consistent across the table.
        - Vertical alignment: In general, you should center your text vertically. Make sure that the content uses the available cell space naturally rather than clustering at the top.
        - Horizontal alignment: Do not default all body cells to top-left alignment. Choose horizontal alignment intentionally by column type: centered alignment often works best for short values, status fields, dates, numbers, and check indicators; left alignment is usually better for narrative or multi-line text.
        - Line height inside cells: Use line spacing that avoids a cramped feel and prevents ascenders/descenders from looking clipped. If a cell feels tight, adjust wrapping/width/padding before shrinking type.
        - Width + wrapping sanity check: Avoid default equal-width columns when the content in each column clearly has different sizes. Avoid lines that run so close to the right edge that the cell feels overfull. If this happens, prefer wrapping or column-width adjustments before reducing font size.
        - Spacing around tables: Keep clear separation between tables and surrounding text (especially the paragraph immediately above/below) so the layout doesn't feel stuck together. Captions and tables should stay visually paired, with deliberate spacing.
        - Quick visual QA pass: Look for text that appears "boundary-hugging", specifically content pressed against the top or left edge of a cell or sitting too close beneath a table. Also watch for overly narrow descriptive columns and short-value columns whose contents feel awkwardly pinned. Correct these issues through padding, alignment, wrapping, or small column-width adjustments.
    - Forms / questionnaires: Design these as a usable form, not a spreadsheet.
      - Prioritize clear response options, obvious and well-sized check targets, readable scale labels, generous row height, clear section hierarchy, light visual structure. Please size fields and columns based on the content they hold rather than by equal-width table cells.
      - Use spacing, alignment, and subtle header/section styling to organize the page. Avoid dense full-grid borders, cramped layouts, and ambiguous numeric-only response areas.
    - Coherence vs. fragmentation: In general, try to keep things to be one coherent representation rather than fragmented, if possible.
      - For example, don't split one logical dataset across multiple independent tables unless there's a clear, labeled reason.
      - For example, if a table must span across pages, continue to the next page with a repeated header and consistent column order
    - Background shapes/colors: Where helpful, consider section bands, note boxes, control grids, or other visual containers with suitable colors to improve scanability and communication. Use them when they suit the document type. If you do use these, make sure they are formatted well, with no overlaps, awkward spacing, etc.
    - Spacing: Please check rigorously for spacing issues. Please always use a natural amount of spacing between adjacent components. Use clear, generous vertical spacing between sections and paragraphs, and leave a bit of extra space between subheadings and the content that follows when it improves readability. Use indentation and alignment intentionally so the document's hierarchy is immediately clear. At the same time, avoid large "layout gaps" caused by a table or chart not fitting at the bottom of a page and getting pushed to the next one. If this happens, please try these suggestions:
      - scaling the visual modestly or simplify labels without hurting readability, formatting, or aesthetics of the visual
      - Splitting the table/figure cleanly across multiple pages, but use repeated headers to make the page continuation clear.
    - Text boxes: For text boxes, please follow the same breathing-room rules as the tables: make sure to use generous internal padding, intentional alignment, and sufficient line spacing so text never feels cramped, clipped, or pinned to the edges. Keep spacing around the text box clear so it remains visually distinct from surrounding content, and if the content feels tight, prefer adjusting box size, padding, or text wrapping before reducing font size.
    - Layout/archetype: Remember to choose the right document archetype/template (proposal, SOP, workflow, form, handbook, etc.). Use a coherent style system. Once a style system is chosen, apply it consistently across headings, spacing, table treatments, callouts, and accent usage. If appropriate to the document type, include a cover page or front-matter elements such as title, subtitle, metadata, or branding.
    
    ### Editing tasks (DOCX edits) â€” apply instead of major rewrite behavior
    
    When the user asks to edit an existing document, preserve the original and make minimal, local changes:
    
    - Prefer inline edits (small replacements) over rewriting whole paragraphs.
    - Use clear inline annotations/comments at the point of change (margin comments or comment markers). Donâ€™t move all feedback to the end.
    - Keep the original structure unless thereâ€™s a strong reason; if a restructure is needed, do it surgically and explain via comments.
    - Donâ€™t â€œcross out everything and rewriteâ€; avoid heavy, blanket deletions. The goal is trackable improvements, not a fresh draft unless explicitly requested.
    
    ## Quick start (common one-liners)
    
    ```bash
    # 0) Sanitize Google Docs-targeted title blocks before render/import
    python scripts/google_docs_title_sanitize.py input.docx --out sanitized.docx
    python scripts/google_docs_title_sanitize.py sanitized.docx --check
    
    # 1) Render any DOCX to PNGs (visual QA)
    python render_docx.py input.docx --output_dir out
    
    # 2) Remove reviewer comments (finalization)
    python scripts/comments_strip.py input.docx --out no_comments.docx
    
    # 3) Accept tracked changes (finalization)
    python scripts/accept_tracked_changes.py input.docx --mode accept --out accepted.docx
    
    # 4) Accessibility audit (+ optional safe fixes)
    python scripts/a11y_audit.py input.docx
    python scripts/a11y_audit.py input.docx --out_json a11y_report.json
    python scripts/a11y_audit.py input.docx --fix_image_alt from_filename --out a11y_fixed.docx
    
    # 5) Redact sensitive text (layout-preserving by default)
    python scripts/redact_docx.py input.docx redacted.docx --emails --phones
    ```
    
    ## Package layout
    
    This skill is organized for progressive discovery: start here, then jump into task- or OOXML-specific docs.
    
    DOCS SKILL PACKAGE
    
    Root:
    - SKILL.md: short overview + routing
    - manifest.txt: machine-readable list of files to download (one relative path per line)
    - render_docx.py: canonical DOCXâ†’PNG renderer (container-safe LO profile + writable HOME + verbose logs)
    
    References:
    - references/design_presets.md: preset-first design tokens, archetype aliases, OOXML conversions, and preset audit checklist
    - references/header_templates.md: concise first-page header pattern picker and code snippets
    
    Tasks:
    - tasks/read_review.md
    - tasks/create_edit.md
    - tasks/verify_render.md
    - tasks/accessibility_a11y.md
    - tasks/comments_manage.md
    - tasks/protection_restrict_editing.md
    - tasks/privacy_scrub_metadata.md
    - tasks/multi_doc_merge.md
    - tasks/style_lint_normalize.md
    - tasks/forms_content_controls.md
    - tasks/captions_crossrefs.md
    - tasks/redaction_anonymization.md
    - tasks/clean_tracked_changes.md
    - tasks/compare_diff.md
    - tasks/templates_style_packs.md
    - tasks/watermarks_background.md
    - tasks/footnotes_endnotes.md
    - tasks/fixtures_edge_cases.md
    - tasks/navigation_internal_links.md
    
    OOXML:
    - ooxml/tracked_changes.md
    - ooxml/comments.md
    - ooxml/hyperlinks_and_fields.md
    - ooxml/rels_and_content_types.md
    
    Troubleshooting:
    - troubleshooting/libreoffice_headless.md
    - troubleshooting/run_splitting.md
    
    Scripts:
    
    **Core building blocks (importable helpers):**
    - `scripts/docx_ooxml_patch.py` â€” low-level OOXML patch helper (tracked changes, comments, hyperlinks, relationships). Other scripts reuse this.
    - `scripts/fields_materialize.py` â€” materialize `SEQ`/`REF` field *display text* for deterministic headless rendering/QA.
    - `scripts/table_geometry.py` â€” apply/audit exact Word table geometry for python-docx tables (`tblW`, `tblInd`, `tblGrid`, and every `tcW` match).
    
    **High-leverage utilities (also importable, but commonly invoked as CLIs):**
    - `render_docx.py` â€” canonical DOCX â†’ PNG renderer (optional PDF via `--emit_pdf`; do not deliver intermediates unless asked).
    - `scripts/render_and_diff.py` â€” render + per-page image diff between two DOCXs.
    - `scripts/google_docs_title_sanitize.py` â€” deterministic OOXML sanitizer/audit for Google Docs-targeted DOCX title blocks; removes Word Title-style bottom borders/rules before render/import.
    - `scripts/content_controls.py` â€” list / wrap / fill Word content controls (SDTs) for forms/templates.
    - `scripts/captions_and_crossrefs.py` â€” insert Caption paragraphs for tables/figures + optional bookmarks around caption numbers.
    - `scripts/insert_ref_fields.py` â€” replace `[[REF:bookmark]]` markers with real `REF` fields (cross-references).
    - `scripts/internal_nav.py` â€” add internal navigation links (static TOC + Top/Bottom + figN/tblN jump links).
    - `scripts/style_lint.py` â€” report common formatting/style inconsistencies.
    - `scripts/style_normalize.py` â€” conservative cleanup (clear run-level overrides; optional paragraph overrides).
    - `scripts/redact_docx.py` â€” layout-preserving redaction/anonymization.
    - `scripts/privacy_scrub.py` â€” remove personal metadata + `rsid*` attributes.
    - `scripts/set_protection.py` â€” restrict editing (read-only / comments / forms).
    - `scripts/comments_extract.py` â€” extract comments to JSON (text, author/date, resolved flag, anchored snippets).
    - `scripts/comments_strip.py` â€” remove all comments (final-delivery mode).
    
    **Audits / conversions / niche helpers:**
    - `scripts/fields_report.py`, `scripts/heading_audit.py`, `scripts/section_audit.py`, `scripts/images_audit.py`, `scripts/footnotes_report.py`, `scripts/watermark_audit_remove.py`
    - `scripts/xlsx_to_docx_table.py`, `scripts/docx_table_to_csv.py`
    - `scripts/insert_toc.py`, `scripts/insert_note.py`, `scripts/apply_template_styles.py`, `scripts/accept_tracked_changes.py`, `scripts/make_fixtures.py`
    
    **v7 additions (stress-test helpers):**
    - `scripts/watermark_add.py` â€” add a detectable VML watermark object into an existing header.
    - `scripts/comments_add.py` â€” add multiple comments (by paragraph substring match) and wire up comments.xml plumbing if needed.
    - `scripts/comments_apply_patch.py` â€” append/replace comment text and mark/clear resolved state (`w:done=1`).
    - `scripts/add_tracked_replacements.py` â€” generate tracked-change replacements (`<w:del>` + `<w:ins>`) in-place.
    - `scripts/a11y_audit.py` â€” audit a11y issues; can also apply simple fixes via `--fix_table_headers` / `--fix_image_alt`.
    - `scripts/flatten_ref_fields.py` â€” replace REF/PAGEREF field blocks with their cached visible text for deterministic rendering.
    
    > `scripts/xlsx_to_docx_table.py` also marks header rows as repeating headers (`w:tblHeader`) to improve a11y and multi-page tables.
    
    Examples:
    - examples/end_to_end_smoke_test.md
    
    > Note: `manifest.txt` is **machine-readable** and is used by download tooling. It must contain only relative file paths (one per line).
    
    
    ## Coverage map (scripts â†” task guides)
    
    This is a quick index so you can jump from a helper script to the right task guide.
    
    ### Layout & style
    - `style_lint.py`, `style_normalize.py` â†’ `tasks/style_lint_normalize.md`
    - `apply_template_styles.py` â†’ `tasks/templates_style_packs.md`
    - `section_audit.py` â†’ `tasks/sections_layout.md`
    - `heading_audit.py` â†’ `tasks/headings_numbering.md`
    
    ### Figures / images
    - `images_audit.py`, `a11y_audit.py` â†’ `tasks/images_figures.md`, `tasks/accessibility_a11y.md`
    - `captions_and_crossrefs.py` â†’ `tasks/captions_crossrefs.md`
    
    ### Tables / spreadsheets
    - `table_geometry.py` â†’ root `Design Preset Contract` table geometry rules
    - `xlsx_to_docx_table.py` â†’ `tasks/tables_spreadsheets.md`
    - `docx_table_to_csv.py` â†’ `tasks/tables_spreadsheets.md`
    
    ### Fields & references
    - `fields_report.py`, `fields_materialize.py` â†’ `tasks/fields_update.md`
    - `insert_ref_fields.py`, `flatten_ref_fields.py` â†’ `tasks/fields_update.md`, `tasks/captions_crossrefs.md`
    - `insert_toc.py` â†’ `tasks/toc_workflow.md`
    
    ### Review lifecycle (comments / tracked changes)
    - `add_tracked_replacements.py`, `accept_tracked_changes.py` â†’ `tasks/clean_tracked_changes.md`
    - `comments_add.py`, `comments_extract.py`, `comments_apply_patch.py`, `comments_strip.py` â†’ `tasks/comments_manage.md`
    
    ### Privacy / publishing
    - `privacy_scrub.py` â†’ `tasks/privacy_scrub_metadata.md`
    - `redact_docx.py` â†’ `tasks/redaction_anonymization.md`
    - `watermark_add.py`, `watermark_audit_remove.py` â†’ `tasks/watermarks_background.md`
    
    ### Navigation & multi-doc assembly
    - `internal_nav.py` â†’ `tasks/navigation_internal_links.md`
    - `merge_docx_append.py` â†’ `tasks/multi_doc_merge.md`
    
    ### Forms & protection
    - `content_controls.py` â†’ `tasks/forms_content_controls.md`
    - `set_protection.py` â†’ `tasks/protection_restrict_editing.md`
    
    ### QA / regression
    - `render_and_diff.py`, `render_docx.py` â†’ `tasks/compare_diff.md`, `tasks/verify_render.md`
    - `make_fixtures.py` â†’ `tasks/fixtures_edge_cases.md`
    - `docx_ooxml_patch.py` â†’ used across guides for targeted patches
    
    ## Skill folder contents
    - `tasks/` â€” task playbooks (what to do step-by-step)
    - `references/` â€” compact reference material loaded only when needed, including design presets
    - `ooxml/` â€” advanced OOXML patches (tracked changes, comments, hyperlinks, fields)
    - `scripts/` â€” reusable helper scripts
    - `examples/` â€” small runnable examples
    - `template-distill.md` â€” distill a retained DOCX into a task-local `artifact.md`
    - `template-create.md` â€” create from the retained DOCX and its `artifact.md`
    
    ## Default workflow (80/20)
    
    **Rule of thumb:** every meaningful edit batch must end with a render + PNG review. No exceptions.
    "80/20" here means: follow the simplest workflow that covers *most* DOCX tasks reliably.
    
    **Golden path (donâ€™t mix-and-match unless debugging):**
    1. **Clarify** Ask any clarification questions as needed
    2. **Author/edit with `python-docx`** (paragraphs, runs, styles, tables, headers/footers).
    3. **Render â†’ inspect PNGs immediately** (DOCX â†’ PNGs). Treat this as your feedback loop.
    4. **Fix and repeat** until the PNGs are visually perfect.
    5. **Only if needed**: use OOXML patching for tracked changes, comments, hyperlinks, or fields.
    6. **Re-render and inspect again** after *any* OOXML patch or layout-sensitive change.
    7. **Deliver only after the latest PNG review passes** (all pages, 100% zoom).
    
    ### Documents clarification questions
    
    - Ask for new documents or major rewrites. Skip this for edits/conversions.
    - Inspect prompt, conversation history, existing file and relevant references to figure out what questions to ask.
    - Questions should cover topic, audience, and purpose and come before planning
    - When asking questions, focus on consequential dimensions not stated or clearly implied.
    - When the artifact is a new analysis, focus on which definition, metric, or lens should drive conclusions.
    - Unresolved reference labels or question marks are user-owned: ask, don't infer.
    - Once topic, audience, and purpose are clear, proceed without asking. Choose emphasis, format, length, style, details. Use placeholders for missing facts.
    
    Use `request_user_input` once if available, else ask via a message. First option should be `Use your judgment (Recommended)` exactly. Recommend no other. Add 1â€“2 exclusive alternatives.
    
    ## Visual review (recommended)
    Use the packaged renderer (dedicated LibreOffice profile + writable HOME):
    
    ```bash
    python render_docx.py /mnt/data/input.docx --output_dir /mnt/data/out
    # If debugging LibreOffice:
    python render_docx.py /mnt/data/input.docx --output_dir /mnt/data/out --verbose
    # Optional: also write <input_stem>.pdf to --output_dir (for debugging/archival):
    python render_docx.py /mnt/data/input.docx --output_dir /mnt/data/out --emit_pdf
    ```
    
    Then inspect the generated `page-<N>.png` files.
    
    **Success criteria (render + visual QA):**
    - PNGs exist for each page
    - Page count matches expectations
    - **Inspect every page at 100% zoom** (no â€œspot checkâ€ for final delivery)
    - No clipping/overlap, no broken tables, no missing glyphs, no header/footer misplacement
    
    **Note:** LibreOffice sometimes prints scary-looking stderr (e.g., `error : Unknown IO error`) even when output is correct. Treat the render as successful if the PNGs exist and look right (and if you used `--emit_pdf`, the PDF exists and is non-empty).
    
    ### What rendering does and doesnâ€™t validate
    
    - **Great for:** layout correctness, fonts, spacing, tables, headers/footers, and whether **tracked changes** visually appear.
    - **Not reliable for:** **comments** (often not rendered in headless PDF export). For comments, also do **structural checks** (comments.xml + anchors + rels + content-types).
    
    ## Quality reminders
    - Donâ€™t ship visible defects (clipped/overlapping text, broken tables, unreadable glyphs).
    - Donâ€™t leak tool citation tokens into the DOCX (convert them to normal human citations).
    - Prefer ASCII punctuation (avoid exotic Unicode hyphens/dashes that render inconsistently).
    
    ## Where to go next
    - If the task is **reading/reviewing**: `tasks/read_review.md`
    - If the task is **creating/editing**: `tasks/create_edit.md`
    - If you need an **accessibility audit** (alt text, headings, tables, links): `tasks/accessibility_a11y.md`
    - If you need to **extract or remove comments**: `tasks/comments_manage.md`
    - If you need to **restrict editing / make read-only**: `tasks/protection_restrict_editing.md`
    - If you need to **scrub personal metadata** (author/rsid/custom props): `tasks/privacy_scrub_metadata.md`
    - If you need to **merge/append DOCXs**: `tasks/multi_doc_merge.md`
    - If you need **format consistency / style cleanup**: `tasks/style_lint_normalize.md`
    - If you need **forms / content controls (SDTs)**: `tasks/forms_content_controls.md`
    - If you need **captions + cross-references**: `tasks/captions_crossrefs.md`
    - If you need **redaction/anonymization**: `tasks/redaction_anonymization.md`
    - If the task is **verification/raster review**: `tasks/verify_render.md`
    - If your render looks wrong but content is right (stale fields): `tasks/fields_update.md`
    - If you need a **Table of Contents**: `tasks/toc_workflow.md`
    - If you need **internal navigation links** (static TOC + Back-to-TOC + Top/Bottom): `tasks/navigation_internal_links.md`
    - If headings/numbering/TOC levels are messy: `tasks/headings_numbering.md`
    - If you have mixed portrait/landscape or margin weirdness: `tasks/sections_layout.md`
    - If images shift or overlap across renderers: `tasks/images_figures.md`
    - If you need spreadsheet â†” table round-tripping: `tasks/tables_spreadsheets.md`
    - If you need **tracked changes (redlines)**: `ooxml/tracked_changes.md`
    - If you need **comments**: `ooxml/comments.md`
    - If you need **hyperlinks/fields/page numbers/headers**: `ooxml/hyperlinks_and_fields.md`
    - If LibreOffice headless is failing: `troubleshooting/libreoffice_headless.md`
    - If you need a **clean copy** with tracked changes accepted: `tasks/clean_tracked_changes.md`
    - If you need to **diff two DOCXs** (render + per-page diff): `tasks/compare_diff.md`
    - If you need **templates / style packs (DOTX)**: `tasks/templates_style_packs.md`
    - If you need a **first-page header / cover / title block**: `references/header_templates.md`
    - If you need **watermark audit/removal**: `tasks/watermarks_background.md`
    - If you need **true footnotes/endnotes**: `tasks/footnotes_endnotes.md`
    - If you want reproducible fixtures for edge cases: `tasks/fixtures_edge_cases.md`
    
    ## Final response citations
    
    Place :codex-file-citation{...} inline in prose without wrapping it in backticks or a code block, not in a trailing list. Use `purpose="source"` for Q&A/no-op and `purpose="output"` for create/edit.
    
    - [HARD REQUIREMENT] Create/edit: cite each final DOCX exactly once with a plain output citation. Summarize representative changes; do not cite every section/page or add a separate filename, path, or Markdown link. Example: `Created :codex-file-citation{path="/abs/path/launch-plan.docx" purpose="output"}, highlighting the rollout and owners.`
    - Q&A: do not edit/re-export. Inspect complete relevant pages and preserve material headings, question/table labels, footnotes, sources, and sample sizes; cite each needed page once.
    
    For page-specific evidence, use a page number verified against the latest render/inspection:
    
    :codex-file-citation{path="/abs/path/file.docx" purpose="source" artifact_kind="document" page_number="4"}
    
    Document locators support only `page_number`; otherwise use a plain citation. Do not guess or add object, label, paragraph, table, or cell IDs. Do not cite intermediates unless asked.
    
    ✓ • 110ms

## Activity

    $ Get-ChildItem -File -Recurse | Select-Object FullName,Name,Extension,Length,LastWriteTime | Sort-Object FullName | Format-Table -AutoSize
    
    
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\archive\india_states.geojson
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\area-wise-waterbodies-india-statewise.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\cea_historical_coal_consumption_2004_2023.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\cea_historical_cost_of_power_supply_and_realisation.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\cea_historical_energy_requirement_availability_2003_2026.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\cea_historical_peak_demand_met_2003_2026.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\cea_historical_per_capita_consumption_2005_2023.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\cea_historical_power_capacity_growth_since_1985.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\cea_installed_capacity_statewise_fuelwise_jul2026.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\cea_transmission_grid_voltage_classes.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\cubems-smart-building-energy-and-iaq-summary.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\Datacenters distribution in india.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\Datacenters distribution in india.xlsx
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\Electricity Substation.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\Executive_Summary_July_2026_Actual.pdf
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\file_02.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\mnre_bio_and_solar_breakdown_2025.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\mnre_re_cumulative_capacity_timeseries_2018_2025.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\mnre_re_estimated_potential_by_state.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\mnre_re_generation_by_source_statewise_2024_2025.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\mnre_re_installed_capacity_by_source_2025.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\mnre_re_share_in_total_capacity_2025.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\region_cordinates.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\State_Region_corrected.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\state-ground-water-level-information.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\statewise and national renewable energy stats.pdf
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\statewise land cost.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\Substation_Details_1789031375809.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\Substation_Details_1789031375809.xlsx
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\sub-stations-220-kv-and.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\Unrequired data\global-data-center-dataset.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\Unrequired data\global-data-center-dataset-original.csv
    C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\Unrequired data\global-data-center-energy-consumption.csv
    
    
    ✓ • 484ms

## Activity

    $ Get-Content -Raw 'C:\Users\nitin\.codex\plugins\cache\openai-primary-runtime\documents\26.819.11345\skills\documents\tasks\create_edit.md'; Get-Content -Raw 'C:\Users\nitin\.codex\plugins\cache\openai-primary-runtime\documents\26.819.11345\skills\documents\references\design_presets.md'; Get-Content -Raw 'C:\Users\nitin\.codex\plugins\cache\openai-primary-runtime\documents\26.819.11345\skills\documents\references\header_templates.md'
    # Task: Create / edit a DOCX
    
    ## Default tool: python-docx
    Use `python-docx` for:
    - paragraphs/runs
    - built-in heading styles (Heading 1 / Heading 2)
    - tables (structure + cell text + basic formatting)
    - simple headers/footers and margins
    
    Exception: for Google Docs-targeted output, do not use the built-in Word
    `Title` style. Build the title as a plain paragraph with explicit run and
    paragraph formatting, then run `scripts/google_docs_title_sanitize.py` before
    render/import.
    
    ## Practical python-docx gotchas
    
    ### 1) Header/footer tables require a width
    When adding tables to headers/footers, `add_table` requires an explicit width:
    
    ```python
    from docx.shared import Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    
    section = doc.sections[0]
    footer = section.footer
    table = footer.add_table(rows=1, cols=3, width=Inches(6.5))
    # Align text inside each cell
    table.rows[0].cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
    ```
    
    ### 2) Fonts can require setting both `run.font.name` and `w:rFonts`
    Some renderers/Word builds donâ€™t respect only `run.font.name`:
    
    ```python
    from docx.oxml.ns import qn
    
    run.font.name = "Gill Sans"
    run._element.rPr.rFonts.set(qn("w:ascii"), "Gill Sans")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Gill Sans")
    ```
    
    ### 3) â€œClear header paragraphâ€ isnâ€™t always one call
    If you need to replace an existing header paragraph, remove runs (or replace the paragraph XML). Avoid assuming a `clear()` method exists.
    
    ### 4) Tracked changes and comments are not first-class
    If the user requests *real* tracked changes or *real* Word comments, plan for OOXML patching (see `ooxml/`).
    
    ## After every meaningful batch of edits: render and review
    Use the loop from `tasks/verify_render.md` (DOCX â†’ PNG) to avoid shipping layout defects. (Internally the renderer uses a PDF step; `--emit_pdf` can persist it if needed.)
    
    ## Output hygiene
    Keep `/mnt/data` clean: deliverables only unless the user asks for intermediate render artifacts.
    
    # Design Presets
    
    Use this reference for new DOCX creation and major rewrites that do not have a selected template or supplied design reference. Existing-document edits should preserve the source document's style unless the user asks for a redesign.
    
    ## Required workflow
    
    1. Pick exactly one preset or archetype alias before drafting. If the target surface is a net-new Google Doc, pick `google_docs_default` unless the user explicitly asks for a special or highly polished visual treatment.
    2. Resolve it into a concrete token map with exact values for every preset-controlled property: page geometry, margins, header/footer distance, body spacing, heading spacing, line spacing, list marker alignment, list text indent, hanging indent, table widths, table indents, cell margins, colors, and fills.
    3. Apply the tokens through Word styles, real numbering definitions, explicit table geometry, callout styles, headers, and footers.
    4. Treat any deviation as a named override and reuse that override consistently.
    5. Before rendering, audit the DOCX against the selected token map, including direct inspection of styles, numbering definitions, section properties, and table XML when needed.
    
    Do not combine presets in one document unless the user explicitly asks for a mixed style system. Do not rely on Word defaults, inherited built-in style values, or approximate visual matches. If a value appears in the selected preset, encode that exact value in the DOCX. Google Docs-targeted documents are not a reason to fall back to a Word-oriented preset by document archetype alone; use `google_docs_default` first, then treat any special styling as an explicit override.
    
    ## Exactness requirement
    
    Preset compliance means the generated DOCX carries the selected preset's actual numbers:
    
    - Paragraph styles must encode the preset's font, size, color, `before`, `after`, and line spacing values. For OOXML, this means values such as `w:before`, `w:after`, and `w:line` are present where the preset controls them.
    - Lists must use numbering definitions whose marker alignment, text indent, hanging indent, tab stop, paragraph spacing, and line spacing match the preset. Built-in styles such as `List Bullet` or `List Number` are acceptable only after their numbering definitions have been set or patched to the preset values.
    - Tables must use fixed DXA geometry. `tblW`, `tblGrid/gridCol`, and every `tcW` must agree with the preset or a named table-pattern override. `tblInd` must match the start cell margin token so the visible outer border aligns with surrounding paragraph text.
    - Table-adjacent citation text must use the selected preset's `table_citation_text` component token instead of inheriting body or caption defaults.
    - Page setup must encode the preset's page size, margins, usable width, and header/footer distances in section properties.
    - Named overrides are allowed only when the document needs a specific exception. Record the override and apply it consistently; do not let ad-hoc direct formatting drift across similar elements.
    
    ## Shared base tokens
    
    All presets inherit these values unless they override them.
    
    | Token | Value |
    |---|---|
    | Page size | US Letter, 8.5 x 11 in, portrait |
    | Margins | 1.0 in top/right/bottom/left |
    | Header/footer distance | 0.492 in |
    | Usable width | 6.5 in / 9360 DXA |
    | Base body style | `Normal` |
    | Default base font | Calibri |
    | Default base size | 11 pt |
    | Heading 1 | 16 pt, `#2E74B5` |
    | Heading 2 | 13 pt, `#2E74B5` |
    | Heading 3 | 12 pt, `#1F4D78` |
    | Table width | 6.5 in / 9360 DXA |
    | Table indent | 120 DXA / 0.083 in, matching default start cell margin |
    | Table geometry | fixed DXA `tblW`, `tblInd`, `tblGrid`, and matching `tcW` |
    | Table default visual | thin single grid, white body cells, restrained optional header/callout fill |
    | Header/footer style | quiet running label/header rule and muted right-aligned page number for multi-page polished docs |
    
    Google Docs exception: `google_docs_default` overrides the shared color, furniture, and table defaults. Its output should feel like a native Google Doc after import, not like a Word template imported into Docs.
    
    ## OOXML conversion cheatsheet
    
    | Design value | OOXML value |
    |---|---|
    | 1.0 in | 1440 DXA |
    | 6.5 in content/table width | 9360 DXA |
    | 0.083 in table indent / cell start margin | 120 DXA |
    | 0.5 in list text indent | 720 DXA |
    | 0.38 in list text indent | about 540 DXA |
    | 0.25 in marker alignment | 360 DXA |
    | 0.18 in marker alignment | about 260 DXA |
    | 0.19 in hanging indent | about 270 DXA |
    | 10 pt before | `w:before="200"` |
    | 8 pt after | `w:after="160"` |
    | 7 pt after | `w:after="140"` |
    | 6 pt after | `w:after="120"` |
    | 5 pt after | `w:after="100"` |
    | 4 pt before | `w:before="80"` |
    | 4 pt after | `w:after="80"` |
    | 3 pt after | `w:after="60"` |
    | 1.333 line spacing | `w:line="320" w:lineRule="auto"` |
    | 1.25 line spacing | `w:line="300" w:lineRule="auto"` |
    | 1.208 line spacing | `w:line="290" w:lineRule="auto"` |
    | 1.167 line spacing | `w:line="280" w:lineRule="auto"` |
    
    ## Preset token schema
    
    Use this shape mentally or in builder code. Fill every value before writing content.
    
    ```yaml
    document_style_preset:
      preset_name: "<resolved preset or alias>"
      page:
        size: Letter
        orientation: portrait
        margins: {top: 1.0in, right: 1.0in, bottom: 1.0in, left: 1.0in}
        header: 0.492in
        footer: 0.492in
        content_width: {in: 6.5, dxa: 9360}
      typography:
        base_font: "<font>"
        base_size: 11pt
        body: {alignment: left, before: 0pt, after: "<pt>", line_spacing: "<single|multiple>"}
      title:
        size: "<pt>"
        color: "<hex>"
        before: "<pt>"
        after: "<pt>"
      headings:
        h1: {size: 16pt, color: "#2E74B5", before: "<pt>", after: "<pt>"}
        h2: {size: 13pt, color: "#2E74B5", before: "<pt>", after: "<pt>"}
        h3: {size: 12pt, color: "#1F4D78", before: "<pt>", after: "<pt>"}
      lists:
        bullet_level_0: {marker: "â€¢", marker_aligned_at: "<in>", text_indent_at: "<in>", hanging: "<in>", after: "<pt>", line_spacing: "<single|multiple>"}
        decimal_level_0: {marker: "%1.", marker_aligned_at: "<in>", text_indent_at: "<in>", hanging: "<in>", after: "<pt>", line_spacing: "<single|multiple>"}
      tables:
        width_dxa: 9360
        indent_dxa: 120
        border_style: single_grid
        header_fill: "<hex|none>"
        cell_margins_dxa: {top: 80, bottom: 80, start: 120, end: 120}
      table_citation_text:
        use: "source/citation text immediately above or below a table"
        paragraph: {before: 4pt, after: 4pt}
      colors:
        heading_blue: "#2E74B5"
        heading_dark_blue: "#1F4D78"
        ink_blue: "#0B2545"
        table_fill_blue_gray: "#E8EEF5"
        table_fill_light_gray: "#F2F4F7"
        callout_fill: "#F4F6F9"
        positive_dark_blue: "#1F3A5F"
        caution_gold: "#7A5A00"
        risk_red: "#9B1C1C"
    ```
    
    ## Base presets
    
    ### `google_docs_default`
    
    Use for net-new Google Docs that should feel native, familiar, and understated after import. This is the default preset whenever the destination is Google Docs unless the user explicitly asks for a more polished, branded, or special-purpose visual treatment.
    
    ```yaml
    preset_name: google_docs_default
    target_surface: google_docs
    typography:
      base_font: Arial
      body: {size: 11pt, alignment: left, before: 0pt, after: 8pt, line_spacing: 1.15}
    title:
      size: 26pt
      color: "#000000"
      weight: normal
      before: 0pt
      after: 3pt
      implementation: plain paragraph with direct run formatting
      border: none
    headings:
      h1: {size: 20pt, weight: normal, color: "#000000", before: 20pt, after: 6pt}
      h2: {size: 16pt, weight: normal, color: "#000000", before: 18pt, after: 6pt}
      h3: {size: 14pt, weight: normal, color: "#434343", before: 16pt, after: 4pt}
    lists:
      bullet_level_0: {marker: "â—", marker_aligned_at: 0.25in, text_indent_at: 0.5in, hanging: 0.25in, after: 4pt, line_spacing: 1.15}
      decimal_level_0: {marker: "%1.", marker_aligned_at: 0.25in, text_indent_at: 0.5in, hanging: 0.25in, after: 4pt, line_spacing: 1.15}
    tables:
      width_dxa: 9360
      indent_dxa: 0
      cell_margins_dxa: {top: 80, bottom: 80, start: 120, end: 120}
      border_style: quiet_minimal
      header_fill: none
      default_use: "only for genuinely tabular data"
    callouts:
      default_style: none
    page_furniture:
      running_header: none
      running_footer: none
      first_page_header_template: none
    table_citation_text:
      use: "source/citation text immediately above or below a table"
      paragraph: {before: 4pt, after: 4pt}
    colors:
      title: "#000000"
      heading: "#000000"
      body: "#000000"
      muted: "#555555"
      border: "#DADCE0"
      fill: none
    ```
    
    Google Docs-specific guidance:
    
    - Build titles as plain paragraphs with explicit formatting from the selected style-sheet title tokens. Never use the built-in Word `Title` paragraph style for Google Docs-targeted output, including `doc.add_paragraph(..., style="Title")` or `doc.add_paragraph(style="Title")`. For `google_docs_default`, apply Arial 26 pt black normal-weight run formatting, 0 pt before, 3 pt after, and no border/rule styling.
    - Prefer prose sections, short bullets, and simple numbered lists over callouts, metadata grids, section bands, or dense tables.
    - Keep the first page simple: title, optional short subtitle or one-line metadata, then body content. Do not add running headers, footer rules, cover treatments, mastheads, or decorative title furniture unless the user explicitly asks for them.
    - Use black for title, headings, body text, and emphasis. A muted gray is acceptable only for light secondary metadata when it improves scanability.
    - Use tables only for actual comparison, status, schedule, or data-entry needs. When a table is necessary, keep it quiet: no colored header fills, no zebra striping, no heavy borders, no table-as-layout tricks.
    - Use native-looking hierarchy rather than â€œpolishâ€ imported from Word. The goal is a document that feels like somebody authored it directly in Google Docs with default settings and good judgment.
    - Treat any visible line under the title as a failed render QA check. The title block must not contain a blue underline, paragraph bottom border, horizontal rule, or Word-template residue in either rendered output or OOXML inspection.
    
    ### `standard_business_brief`
    
    Use for formal memos, RFI responses, decision memos, board memos, and executive briefs.
    
    ```yaml
    preset_name: standard_business_brief
    typography:
      base_font: Calibri
      body: {size: 11pt, alignment: left, before: 0pt, after: 6pt, line_spacing: 1.10}
    headings:
      h1: {size: 16pt, color: "#2E74B5", before: 16pt, after: 8pt}
      h2: {size: 13pt, color: "#2E74B5", before: 12pt, after: 6pt}
      h3: {size: 12pt, color: "#1F4D78", before: 8pt, after: 4pt}
    lists:
      bullet_level_0: {marker_aligned_at: 0.25in, text_indent_at: 0.5in, hanging: 0.25in, after: 8pt, line_spacing: 1.167}
      decimal_level_0: {marker_aligned_at: 0.25in, text_indent_at: 0.5in, hanging: 0.25in, after: 8pt, line_spacing: 1.167}
    tables:
      width_dxa: 9360
      indent_dxa: 120
      cell_margins_dxa: {top: 80, bottom: 80, start: 120, end: 120}
      border_style: single_grid
      header_fill: "#F2F4F7"
    table_citation_text:
      use: "source/citation text immediately above or below a table"
      paragraph: {before: 4pt, after: 4pt}
    ```
    
    ### `compact_reference_guide`
    
    Use for launch guides, negotiation briefs, checklists, and dense operator references.
    
    ```yaml
    preset_name: compact_reference_guide
    typography:
      base_font: Calibri
      body: {size: 11pt, alignment: left, before: 0pt, after: 6pt, line_spacing: 1.25}
    headings:
      h1: {size: 16pt, color: "#2E74B5", before: 18pt, after: 10pt}
      h2: {size: 13pt, color: "#2E74B5", before: 14pt, after: 7pt}
      h3: {size: 12pt, color: "#1F4D78", before: 10pt, after: 5pt}
    lists:
      bullet_level_0: {marker_aligned_at: 0.187in, text_indent_at: 0.375in, hanging: 0.188in, after: 4pt, line_spacing: 1.25}
      decimal_level_0: {marker_aligned_at: 0.187in, text_indent_at: 0.375in, hanging: 0.188in, after: 4pt, line_spacing: 1.25}
    tables:
      width_dxa: 9360
      indent_dxa: 120
      cell_margins_dxa: {top: 80, bottom: 80, start: 120, end: 120}
      border_style: single_grid
      header_fill: "#E8EEF5"
      compact_label_detail_widths: [1.181in, 5.319in]
      standard_label_detail_widths: [1.875in, 4.625in]
    table_citation_text:
      use: "source/citation text immediately above or below a table"
      paragraph: {before: 4pt, after: 4pt}
    ```
    
    ### `narrative_proposal`
    
    Use for grant proposals, business proposals, and persuasive documents with longer prose.
    
    ```yaml
    preset_name: narrative_proposal
    typography:
      base_font: Calibri
      body: {size: 11pt, alignment: justified, before: 0pt, after: 8pt, line_spacing: 1.333}
    headings:
      h1: {size: 16pt, color: "#2E74B5", before: 18pt, after: 10pt}
      h2: {size: 13pt, color: "#2E74B5", before: 12pt, after: 6pt}
      h3: {size: 12pt, color: "#1F4D78", before: 8pt, after: 4pt}
    lists:
      bullet_level_0: {marker_aligned_at: 0.181in, text_indent_at: 0.375in, hanging: 0.194in, after: 4pt, line_spacing: 1.208}
      decimal_level_0: {marker_aligned_at: 0.181in, text_indent_at: 0.375in, hanging: 0.194in, after: 4pt, line_spacing: 1.208}
    tables:
      width_dxa: 9360
      indent_dxa: 120
      cell_margins_dxa: {top: 80, bottom: 80, start: 120, end: 120}
      border_style: single_grid
      header_fill: "#F4F6F9"
    table_citation_text:
      use: "source/citation text immediately above or below a table"
      paragraph: {before: 4pt, after: 4pt}
    ```
    
    ## Archetype aliases
    
    Aliases inherit a base preset and override only the listed values.
    
    | Alias | Base preset | Overrides |
    |---|---|---|
    | `rfi_response` | `standard_business_brief` | Body after 6pt; H1 before 16pt/after 8pt; H2 before 12pt/after 6pt; list marker 0.25in, text 0.5in; use 3-4 column full-width compliance matrices. |
    | `decision_memo` | `standard_business_brief` | Base font Arial; body after 6pt; H1 before 12pt/after 6pt; H2 before 10pt/after 5pt; list marker 0.25in, text 0.5in. |
    | `launch_messaging_guide` | `compact_reference_guide` | Body after 6pt, line 1.25; H1 before 18pt/after 10pt; H2 before 14pt/after 7pt; H3 before 10pt/after 5pt; table use can be heavy. |
    | `contract_negotiation_brief` | `compact_reference_guide` | Body after 6pt; H1 before 14pt/after 8pt; H2 before 11pt/after 6pt; H3 before 8pt/after 4pt; prefer 1.181in/5.319in label-detail grids. |
    | `neighborhood_business_proposal` | `narrative_proposal` | Body justified, after 8pt, line 1.333; H1 before 18pt/after 10pt; H2 before 12pt/after 6pt; H3 before 8pt/after 4pt; decimal lists may lead action sequences. |
    | `grant_proposal` | `narrative_proposal` | Body left or justified by section, after 6pt, line 1.25 for compact prose; H1 before 16pt/after 8pt; H2 before 12pt/after 6pt; reserve tables for budget and evaluation. |
    
    ## Table patterns
    
    Use full-width tables by default. Pick column widths by content and keep the total at 9360 DXA. Use `tblInd=120` DXA unless a named override intentionally changes table placement; this aligns the visible outer border with surrounding paragraph text instead of aligning only the first cell's text.
    
    | Pattern | Widths | Use |
    |---|---|---|
    | One-column callout | 6.5 in | Message blocks, grouped examples, callouts. |
    | Compact label-detail | 1.181 in, 5.319 in | Term/value, clause/position, compact reference rows. |
    | Standard label-detail | 1.875 in, 4.625 in | Brief metadata, description tables, playbooks. |
    | Two-up comparison | 3.25 in, 3.25 in | Option A/B, do/don't, before/after. |
    | Three-column matrix | 1.5 in, 2.5 in, 2.5 in | Decision criteria, stakeholder impact, roadmap. |
    | Four-column matrix | content-specific, sum 6.5 in | RFI compliance, budget, status, risk tables. |
    
    Always run the table geometry helper or an equivalent audit after table generation.
    
    ## Preset audit
    
    Before final render review, verify:
    
    - Page size, margins, header/footer distance, and content width match the token map.
    - Body and heading styles carry the selected font, size, color, spacing, and line spacing.
    - Lists use real numbering definitions with the selected marker alignment, text indent, hanging indent, spacing, and line spacing.
    - Tables use 9360 DXA unless intentionally compact, `tblInd` equals the start cell margin token, and `tblW`, `tblGrid`, and each `tcW` agree.
    - Table-adjacent citation text above or below tables carries the selected preset's `table_citation_text` spacing.
    - Callout/header/table fills use only the preset colors or a named override.
    - Headers and footers are consistent across pages.
    - There are no fake headings, fake bullets, manual numbering, percentage-width tables, fixed row heights that clip, or unexplained direct formatting drift.
    
    For `google_docs_default`, also verify:
    
    - Title, headings, body text, and list text all use Arial with black text unless a named override says otherwise.
    - No blue heading colors, colored callout fills, zebra striping, dense grid borders, decorative header rules, running header/footer chrome, or other Word-template residue remain.
    - The first page reads like a native Google Doc: simple title block, clear section hierarchy, restrained spacing, and no table-first packaging of normal prose.
    - Tables appear only where the content is truly tabular and use quiet minimal styling with `tblInd=0` unless a named override intentionally changes placement.
    
    # Header Templates
    
    Use this reference when creating a new DOCX or a major repackage that needs first-page title/header furniture. Pick one pattern before drafting the document body.
    
    ## Opinionated Method
    
    1. Choose the document job first: decision/reference, persuasive ask, report/guide, customer or partner packet, session plan, or proof story.
    2. Use exactly one first-page header pattern. Do not mix centered-cover, memo metadata, metric-strip, and quote treatments in the same opening block.
    3. Set the running section header/footer first, then build the visible first-page title block.
    4. Replace sample text, colors, and metadata with the document's actual content. Keep the structure, hierarchy, and spacing intent.
    5. Treat these snippets as inspiration, not a dependency. If helper names differ, implement the same Word-native effects with `python-docx`: real paragraphs, paragraph borders for rules, explicit table geometry for metadata grids, and standard section headers/footers.
    6. No border bottoms for header
    
    ## Pattern Picker
    
    | Pattern | Use for | First-page signal |
    |---|---|---|
    | `memo_masthead` | decision memos, exec briefs, board recommendations, strategy notes, PRDs, RFCs, specs, policy memos, status updates, incident reports, postmortems, risk reviews, audit/compliance notes, technical findings, research summaries | title, subtitle, dense metadata rows, strong bottom rule |
    | `proposal_centerpiece` | grants, RFP/RFI responses, sales proposals, project proposals, SOWs, funding asks, business cases, sponsorship pitches, partnership proposals, product pitches, procurement responses, formal applications | centered title stack plus balanced two-column metadata |
    | `editorial_cover` | reports, white papers, market/trend research, field guides, playbooks, handbooks, manuals, SOPs, reference guides, newsletters, annual/quarterly reviews, thought leadership, narrative briefs | generous vertical whitespace and a cover-like centered title |
    | `customer_pack` | onboarding packs, kickoff packets, implementation plans, customer success plans, QBR/EBR packets, account plans, partner enablement, rollout plans, change-management docs, stakeholder packets, leave-behinds, training packets | left-aligned commercial title with compact metadata grid |
    | `workshop_agenda` | agendas, offsites, workshops, design sprints, trainings, classes, webinars, run-of-show docs, meeting briefs, interview guides, discovery sessions, retrospectives, planning sessions, checklists with timed steps | title stack anchored by a time/objective metric strip |
    | `customer_story` | case studies, testimonials, success stories, proof narratives, launch announcements, impact reports, before/after writeups, user research readouts, customer profiles, press one-pagers, advocacy stories | title stack plus centered pull quote |
    
    Default to `memo_masthead` for serious internal or technical documents, `proposal_centerpiece` for persuasive asks, `editorial_cover` for polished long-form reading, and `customer_pack` for operational customer/partner docs. Use `workshop_agenda` when sequence or participation is the point. Use `customer_story` when a quote, outcome, or proof point is central.
    
    ## Shared Helper Contract
    
    The examples assume local helpers like `set_section_header`, `set_section_footer`, `add_title`, `add_subtitle`, `add_kicker`, `add_para`, `add_spacer`, `add_metadata_rows`, `add_inline_metadata_grid`, `add_metric_strip`, and `paragraph_border_bottom`.
    
    If those helpers are unavailable, recreate the effects directly:
    
    - Running header/footer: use `section.header` and `section.footer`.
    - Title stack: use normal Word paragraphs with explicit size, bold/italic, color, alignment, and spacing.
    - Metadata grid: use a small fixed-width table with explicit DXA geometry and cell margins.
    - Bottom rule: use a paragraph border, not a fake table or repeated characters.
    - Metric strip: use a fixed-width table with clear fill, compact labels, and enough cell padding.
    
    ## `memo_masthead`
    
    ```python
    def set_run_font(run, name="Arial", size=None, color=None, bold=None, italic=None):
        run.font.name = name
        run._element.rPr.rFonts.set(qn("w:ascii"), name)
        run._element.rPr.rFonts.set(qn("w:hAnsi"), name)
        if size is not None:
            run.font.size = Pt(size)
        if color is not None:
            run.font.color.rgb = color
        if bold is not None:
            run.bold = bold
        if italic is not None:
            run.italic = italic
    
    ## don't change me
    def add_metadata_rows(doc):
        rows = [
            ("To", "Executive Team"),
            ("From", "Launch Program Lead"),
            ("Date", "May 4, 2026"),
            ("Re", "Decision: delay launch by two weeks vs. ship with onboarding gap"),
            ("Status", "Decision required this week"),
        ]
    
        for label, value in rows:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = MASTHEAD_METADATA_LINE_SPACING
            label_run = p.add_run(f"{label}: ")
            set_run_font(label_run, size=11, color=BLACK, bold=True)
            value_run = p.add_run(value)
            set_run_font(value_run, size=11, color=BLACK)
    
    def page_memo_masthead(doc, section):
        set_section_header(
            section,
            "Decision Memo",
            "Project Lighthouse - Confidential",
            color=MUTED,
            rule=False,
        )
        set_section_footer(section, f"Page 1 of {TOTAL_PAGES}")
    
        add_spacer(doc, 16)
        add_title(doc, "DECISION MEMO", size=23, color=RGBColor(0, 0, 0), after=4)
        add_subtitle(
            doc,
            "Project Lighthouse - Launch Date vs. Onboarding Completeness",
            size=14,
            color=RGBColor(55, 55, 55),
            after=16,
        )
        add_metadata_rows(
            doc,
            [
                ("To:", "Project Lighthouse Cross-Functional Launch Team"),
                ("From:", "Launch Program Lead"),
                ("Date:", "April 29, 2026"),
                ("Re:", "Decision: delay launch by two weeks vs. ship with onboarding gap"),
                ("Status:", "Decision required by EOD Friday, May 1, 2026"),
            ],
            label_width=1.0,
        )
    
        add_spacer(doc, 14)
        rule = doc.add_paragraph()
    ```
    
    ## `proposal_centerpiece`
    
    ```python
    def page_proposal_centerpiece(doc, section):
        set_section_header(
            section,
            "Riverbend Arts Collective | Walls That Speak",
            "City of Riverbend Small Community Grant",
            color=MUTED,
            rule=False,
        )
        set_section_footer(section, f"Page 2 of {TOTAL_PAGES}")
    
        add_para(
            doc,
            "Riverbend Arts Collective",
            size=12,
            bold=True,
            color=GRAY,
            align=WD_ALIGN_PARAGRAPH.CENTER,
            after=8,
        )
        add_title(
            doc,
            "Walls That Speak",
            size=24,
            color=RGBColor(0, 0, 0),
            align=WD_ALIGN_PARAGRAPH.CENTER,
            after=4,
        )
        add_subtitle(
            doc,
            "A Weekend Public Mural Festival",
            size=14,
            color=GRAY,
            align=WD_ALIGN_PARAGRAPH.CENTER,
            after=8,
        )
        add_para(
            doc,
            "Proposal to the City of Riverbend Cultural Affairs Office | Small Community Grant Program",
            size=10.5,
            color=GRAY,
            bold=True,
            align=WD_ALIGN_PARAGRAPH.CENTER,
            after=26,
        )
    
        rule = doc.add_paragraph()
        add_spacer(doc, 10)
        add_inline_metadata_grid(
            doc,
            section,
            [
                ("Applicant:", "Riverbend Arts Collective (501(c)(3))"),
                ("Contact:", "Maya Ortiz, Executive Director"),
                ("Email/Phone:", "maya@riverbendarts.org | (555) 412-9087"),
                ("Site:", "Mill District, between 4th and 7th Streets"),
            ],
            [
                ("Proposed Dates:", "September 19-20, 2026"),
                ("Amount Requested:", "$8,500"),
                ("Total Budget:", "$23,400"),
                ("Project Lead:", "Devon Pierce"),
            ],
        )
    ```
    
    ## `editorial_cover`
    
    ```python
    def page_editorial_cover(doc, section):
        set_section_header(
            section,
            "Pour With Intention",
            "Trend Report - April 2026",
            color=MUTED,
            rule=True,
        )
        set_section_footer(section, f"Page 3 of {TOTAL_PAGES}")
    
        add_spacer(doc, 132)
        add_kicker(
            doc,
            "Trend Report",
            color=GOLD,
            align=WD_ALIGN_PARAGRAPH.CENTER,
            after=18,
        )
        add_title(
            doc,
            "Pour With Intention",
            size=30,
            color=RGBColor(32, 55, 72),
            align=WD_ALIGN_PARAGRAPH.CENTER,
            after=8,
        )
        add_subtitle(
            doc,
            "How Neighborhood Coffee Shops Can Use AI",
            size=15,
            color=RGBColor(43, 81, 99),
            align=WD_ALIGN_PARAGRAPH.CENTER,
            after=2,
        )
        add_subtitle(
            doc,
            "Without Losing Their Local Voice",
            size=15,
            color=RGBColor(43, 81, 99),
            align=WD_ALIGN_PARAGRAPH.CENTER,
            after=28,
        )
        add_para(
            doc,
            "-  An Independent Operator's Field Guide  -",
            size=10.5,
            color=GOLD,
            align=WD_ALIGN_PARAGRAPH.CENTER,
            after=88,
        )
        add_para(
            doc,
            "April 2026",
            size=12,
            bold=True,
            color=RGBColor(32, 55, 72),
            align=WD_ALIGN_PARAGRAPH.CENTER,
            after=4,
        )
        add_para(
            doc,
            "Prepared for independent cafe owners and small-chain operators",
            size=9.5,
            italic=True,
            color=RGBColor(80, 80, 80),
            align=WD_ALIGN_PARAGRAPH.CENTER,
            after=22,
        )
    ```
    
    ## `customer_pack`
    
    ```python
    def page_customer_pack(doc, section):
        set_section_header(
            section,
            "Partner Pack",
            "Acme Onboarding Enablement",
            color=MUTED,
            rule=True,
            rule_color="D7DBE2",
        )
        set_section_footer(section, f"Page 4 of {TOTAL_PAGES}")
    
        add_kicker(doc, "Customer Enablement Pack", color=GOLD, after=0)
        add_title(doc, "Acme Onboarding Sprint", size=31, color=NAVY, after=8)
        add_subtitle(
            doc,
            "A partner-ready packet for kickoff, enablement, and success planning.",
            size=13.5,
            color=GRAY,
            after=22,
        )
        add_inline_metadata_grid(
            doc,
            section,
            [
                ("Prepared for:", "Acme Revenue Operations"),
                ("Prepared by:", "Customer Success and Solutions"),
            ],
            [
                ("Engagement:", "Four-week onboarding sprint"),
                ("Start:", "May 18, 2026"),
            ],
            left_weight=1.05,
            right_weight=1.0,
        )
    ```
    
    ## `workshop_agenda`
    
    ```python
    def page_workshop_agenda(doc, section):
        set_section_header(
            section,
            "Workshop Agenda",
            "Design Sprint - Day 1",
            color=MUTED,
            rule=False,
        )
        set_section_footer(section, f"Page 5 of {TOTAL_PAGES}")
    
        add_kicker(doc, "Workshop Agenda", color=BLUE, after=0)
        add_title(doc, "AI Support Design Sprint", size=29, color=NAVY, after=8)
        add_subtitle(
            doc,
            "A session-first intro for agendas, offsites, working sessions, and trainings.",
            size=13.2,
            color=GRAY,
            after=18,
        )
        add_metric_strip(
            doc,
            section,
            [
                ("9:00", "Context and goals"),
                ("10:15", "Customer journey map"),
                ("1:00", "Concept sketches"),
                ("3:30", "Decision readout"),
            ],
            fill="FFF8E8",
            accent=GOLD,
        )
    ```
    
    ## `customer_story`
    
    ```python
    def page_customer_story(doc, section):
        set_section_header(
            section,
            "Customer Story",
            "Northstar Retail - Draft",
            color=MUTED,
            rule=True,
            rule_color="D8D3C7",
        )
        set_section_footer(section, f"Page 6 of {TOTAL_PAGES}")
    
        add_kicker(doc, "Customer Story", color=GOLD, after=0)
        add_title(
            doc,
            "How Northstar Retail Cut Support Escalations by 31%",
            size=28,
            color=NAVY,
            after=12,
        )
        add_subtitle(
            doc,
            "A narrative intro for case studies, success stories, and customer-facing proof.",
            size=13.2,
            color=GRAY,
            after=22,
        )
        add_para(
            doc,
            '"We needed a support experience that helped store teams move faster without losing the human tone our customers expect."',
            size=14,
            color=RGBColor(70, 70, 70),
            italic=True,
            align=WD_ALIGN_PARAGRAPH.CENTER,
            after=18,
        )
        add_para(
            doc,
            "- VP Customer Experience, Northstar Retail",
            size=9.5,
            color=GOLD,
            bold=True,
            align=WD_ALIGN_PARAGRAPH.CENTER,
            after=24,
        )
    ```
    
    ✓ • 164ms

## Assistant

The folder contains 34 source artifacts: mostly energy, renewable, water, land, grid/substation, and data-centre datasets, plus two likely source/reference PDFs. I’ll also inspect the PDFs so the recommendations distinguish usable ML tables from documentation and duplicate exports.

## Activity

    $ Get-Content -Raw 'C:\Users\nitin\.codex\plugins\cache\openai-primary-runtime\pdf\26.819.11345\skills\pdf\SKILL.md'
    ---
    name: "pdf"
    description: "Read, create, inspect, render, and verify PDF files where visual layout matters, including fillable AcroForms. Use Poppler rendering plus Python tools such as reportlab, pdfplumber, and pypdf for generation and extraction."
    ---
    
    # PDF Skill
    
    ## When To Use
    
    - Read or review PDF content where layout and visuals matter.
    - Create PDFs programmatically with reliable formatting.
    - Fill and validate interactive PDF forms.
    - Validate final rendering before delivery.
    
    ## Workflow
    
    Immediately before the first create/edit authoring command, run `mark_artifact_operation_started.mjs` successfully exactly once using the command below. Do not run it for read-only work. For edits, replace `create` with `edit`; adjust the expected count and output format to match the requested outputs.
    
    ```bash
    node container_tools/mark_artifact_operation_started.mjs --operation-kind create --expected-output-count 1 --output-format pdf
    ```
    
    1. Prefer visual review: render PDF pages to PNGs and inspect them.
       - Use `pdftoppm` from the bundled runtime or system Poppler when available.
       - If unavailable, install Poppler or ask the user to review the output locally.
    2. Use `reportlab` to generate PDFs when creating new documents.
    3. Use `pdfplumber` or `pypdf` for text extraction and quick checks; do not rely on text extraction for layout fidelity.
    4. After each meaningful update, re-render pages and verify alignment, spacing, and legibility.
    
    ## Fill And Validate AcroForms
    
    Visual review alone is not a correctness check for a fillable PDF. A page `/Widget` annotation can render a value from its appearance stream while the canonical `/AcroForm/Fields` tree is missing or contains a stale value.
    
    1. Keep the result interactive by default; set `flatten=True` only when the user explicitly requests a completed, static form. Preserve the source PDF, and do not flatten a signed PDF without an explicit workflow decision.
    2. Inspect both representations before filling: enumerate fields from `reader.get_fields()` and `/Widget` annotations from every page's `/Annots`, following `/Parent` and `/Kids`. If a widget and a canonical field have the same name but are distinct objects with no `/Parent` relationship, do not call `reattach_fields()` blindly: it can create a second top-level field with the same name. Report the ambiguity or produce a static result.
    3. Recover genuinely orphaned widgets, fill all pages, and write the result with `pypdf`:
    
    ```python
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import NameObject
    
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    
    # Restores widgets that are missing from /AcroForm/Fields.
    writer.reattach_fields()
    fields = writer.get_fields() or {}
    missing = set(expected_values) - set(fields)
    if missing:
        raise ValueError(f"Form fields not found after repair: {sorted(missing)}")
    
    values_to_write = dict(expected_values)
    if flatten:
        # Paint every existing value before removing every widget.
        values_to_write = {
            name: field.get("/V", "/Off" if field.get("/FT") == "/Btn" else "")
            for name, field in fields.items()
        }
        values_to_write.update(expected_values)
    
    writer.update_page_form_field_values(
        None, values_to_write, auto_regenerate=False, flatten=flatten
    )
    
    if flatten:
        # pypdf's flatten=True paints appearances but does not remove widgets.
        writer.remove_annotations(subtypes="/Widget")
        writer.root_object.pop(NameObject("/AcroForm"), None)
    
    with open(output_pdf, "wb") as stream:
        writer.write(stream)
    ```
    
    4. Reopen the written PDF before delivery. For an interactive result, require every expected field to be present in `get_fields()` with the expected `/V`, enumerate page widgets again, and confirm their effective `/V` (the widget value or inherited `/Parent` value) agrees. Confirm each updated widget has a non-empty `/AP` `/N` appearance and render the final pages to catch stale or clipped appearances. Do not rely on `/NeedAppearances` or a successful PNG render as proof that logical field data was updated.
    5. For a flattened result, require zero `/Widget` annotations and no remaining `/AcroForm` field tree after reopening, then render the final pages. Keep an editable copy when the user may need to revise the form.
    
    ## Temp And Output Conventions
    
    - Use `tmp/pdfs/` for intermediate files; delete them when done.
    - Write final artifacts under `output/pdf/` when working in this repo.
    - Keep filenames stable and descriptive.
    
    ## Dependencies
    
    Prefer the Codex bundled workspace/runtime dependencies when available. The primary runtime is expected to include:
    
    - Python packages: `reportlab`, `pdfplumber`, `pypdf`
    - Rendering tools: `pdftoppm` and `pdfinfo` from Poppler
    
    If a dependency is missing, install only what is needed.
    
    Python packages:
    
    ```bash
    uv pip install reportlab pdfplumber pypdf
    ```
    
    If `uv` is unavailable:
    
    ```bash
    python3 -m pip install reportlab pdfplumber pypdf
    ```
    
    System tools for rendering:
    
    ```bash
    # macOS (Homebrew)
    brew install poppler
    
    # Ubuntu/Debian
    sudo apt-get install -y poppler-utils
    ```
    
    If installation is not possible in this environment, tell the user which dependency is missing and how to install it locally.
    
    ## Environment
    
    No required environment variables.
    
    ## Rendering Command
    
    ```bash
    pdftoppm -png "$INPUT_PDF" "$OUTPUT_PREFIX"
    ```
    
    ## Quality Expectations
    
    - Maintain polished visual design: consistent typography, spacing, margins, and section hierarchy.
    - Avoid rendering issues: clipped text, overlapping elements, broken tables, black squares, or unreadable glyphs.
    - Charts, tables, and images must be sharp, aligned, and clearly labeled.
    - Use ASCII hyphens only. Avoid U+2011 and other Unicode dashes.
    - Citations and references must be human-readable; never leave tool tokens or placeholder strings.
    
    ## Final Checks
    
    - Do not deliver until the latest PNG inspection shows zero visual or formatting defects.
    - Confirm headers, footers, page numbering, and section transitions look polished.
    - Keep intermediate files organized or remove them after final approval.
    
    ## Final response citations
    
    Place `:codex-file-citation{...}` inline in prose, not in a trailing list. Use `purpose="source"` for Q&amp;A/no-op and `purpose="output"` for create/edit.
    
    - [HARD REQUIREMENT] Create/edit: cite each final PDF exactly once with a plain output citation. Summarize representative changes; do not cite every page or add a separate filename, path, or Markdown link. Example: `Created :codex-file-citation{path="/abs/path/report.pdf" purpose="output"}, with the completed analysis and appendix.`
    - Q&amp;A/no-op: do not edit or re-export. Inspect the complete relevant pages, preserve material headings, table/figure labels, footnotes, sources, and sample sizes, and cite each source PDF once with a plain source citation.
    
    PDF citations currently support only plain file citations. Do not add `artifact_kind`, `page_number`, or other locators. Never cite rendered PNGs, scratch files, builders, or QA intermediates unless asked.
    
    ✓ • 83ms

## Assistant

The Word report will use a compact reference-guide format, since it needs to be an operational, file-by-file handoff. I’m also applying the spreadsheet and PDF inspection workflows to the two workbook exports and the source PDFs.

## Activity

    $ Get-Content -Raw 'C:\Users\nitin\.codex\plugins\cache\openai-primary-runtime\spreadsheets\26.819.11345\skills\SKILL.md'
    Get-Content : Cannot find path
    'C:\Users\nitin\.codex\plugins\cache\openai-primary-runtime\spreadsheets\26.819.11345\skills\SKILL.md' because it does
    not exist.
    At line:2 char:1
    + Get-Content -Raw 'C:\Users\nitin\.codex\plugins\cache\openai-primary- ...
    + ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        + CategoryInfo          : ObjectNotFound: (C:\Users\nitin\...skills\SKILL.md:String) [Get-Content], ItemNotFoundEx
       ception
        + FullyQualifiedErrorId : PathNotFound,Microsoft.PowerShell.Commands.GetContentCommand
    
    ✗ (1) • 261ms

## Activity

    $ Get-Content -Raw 'C:\Users\nitin\.codex\plugins\cache\openai-primary-runtime\spreadsheets\26.819.11345\skills\spreadsheets\SKILL.md'
    ---
    name: "Spreadsheets"
    description: "Create, edit, analyze, and verify standalone spreadsheet files or Google Sheets-ready workbooks, including .xlsx, .xls, .csv, and .tsv. Do not use for live controlling Microsoft Excel app or a live Excel session."
    ---
    
    # Spreadsheets skill (Create â€¢ Edit â€¢ Analyze â€¢ Visualize)
    Use this skill when you need to work with spreadsheets (.xlsx, .csv, .tsv) to do any of the following:
    - Create or modify a new workbook/sheet with proper formulas, cell/number formatting, and structured layout
    - Read or analyze tabular data (filter, aggregate, pivot, compute metrics) directly in a sheet
    - Visualize data with in-sheet charts/tables and sensible formatting
    - Recalculate/evaluate formulas to update results after changes
    
    ## Decision Boundary
    
    - For Google Sheets-targeted outputs, such as creating or editing a Google Sheet, follow the additional instructions here: `routing/google_sheets.md`.
    
    Do not follow those routing instructions if irrelevant to the task. Default is to create/edit spreadsheets with artifact tool.
    
    ## Tools + Contract Requirements
    - Use `@oai/artifact-tool` JS library for all spreadsheet authoring, using only the executables and dependency paths provided by `load_workspace_dependencies`. Do not use system, global, or repo-local dependencies.
    - If the runtime or `@oai/artifact-tool` is unavailable, report a blocker. Do not guess or search for paths, install packages, use resolution hacks, or import bundled internals.
    - Work in a writable, conversation-specific or tmp directory. In that working directory, create a `node_modules` symlink or Windows junction pointing to the loader-provided `node_modules` directory. Never modify the loader-provided dependency directory.
    - Prefer one executable `.mjs` builder and patch/rerun it. Do not use heredocs or duplicate builders.
    - Use the provided API reference. Do not inspect package internals or prototypes. If blocked, run at most one targeted `workbook.help("<api_or_feature>")` query.
    - Do not use alternate workbook creation/editing libraries such as `openpyxl`, `xlsxwriter`, or `pandas.ExcelWriter` unless the user explicitly asks.
    - For supporting analysis or data processing outside workbook authoring, use JS or spreadsheet formulas when sufficient. If Python is necessary, prefer the bundled python libraries, save JSON/CSV intermediates, and have the JS builder create the workbook. Use existing system Python or user-provided libraries only when the bundled environment lacks a required capability. Keep auditable and user-editable calculations in the workbook as formulas.
    - Use `update_plan` for complex spreadsheet work.
    - In your final response, do not mention or link builders, previews, or other support files unless requested.
    
    ## Artifact Template Selection
    
    Open the template selection picker for creating new spreadsheets when the user has not provided a template, reference, or visual direction. Also open the picker when the user asks to browse or upload templates. Do not open it if the user declines templates or requests a connected-source design search. Subject matter, audience, tone, company names, and source files do not by themselves specify a template or visual direction.
    
    Call `list_artifact_templates({artifactKind, request})` with `artifactKind: "spreadsheet"`, or `"google-sheets"` for Google Sheets requests. Include compatible Office and Google templates without changing the requested output format.
    
    Rank templates by relevance, breaking ties in favor of personal or shared templates. Include a mix of styles. Pass their `skillName` values unchanged to `choose_artifact_template({artifactKind, request, templates})` and call it once. Set `includeAllTemplates: true` only when the user requests the full catalog. The picker displays at most ten templates.
    
    Follow the selected template or uploaded reference. Save an uploaded reference only when `saveForFutureUse` is true. Use Template Creator with the returned `displayName`. Continue without a template if the picker is declined, cancelled, unavailable, or fails. Do not replace the picker with `request_user_input` or a chat list. Browsing templates does not authorize artifact creation.
    
    Immediately before the first create/edit authoring command, run `mark_artifact_operation_started.mjs` successfully exactly once using the command below. Do not run it for read-only work. For edits, replace `create` with `edit`; adjust the expected count and output format to match the requested outputs.
    
    ```bash
    node container_tools/mark_artifact_operation_started.mjs --operation-kind create --expected-output-count 1 --output-format xlsx
    ```
    
    ## Other documents
    - `style_guidelines.md`: REQUIRED for formatting requirements
    - `artifact_tool_docs/API_QUICK_START.md`: REQUIRED API documentation for `artifact_tool` JS library, which exposes methods to read, manipulate, edit, recalculate, render, import and save spreadsheets. You must read it entirely to get started.
    - `features/charts.md`: Read when creating or editing charts.
    
    ## Domain Requirements
    You must read these domain rules when the request clearly relates to the domain, but do not load domain guidance for unrelated tasks unless asked:
    - Finance and investment banking: `domain_guidance/financial_models.md`
    - Corporate finance and FP&A: `domain_guidance/corporate_finance_fpa.md`
    - Healthcare: `domain_guidance/healthcare.md`
    - Marketing and advertising: `domain_guidance/marketing_advertising.md`
    - Scientific research: `domain_guidance/scientific_research.md`
    
    Instruction precedence for workbook content, layout, and formatting is: user request > reference/template > domain and formatting defaults.
    
    ## Making edits on a spreadsheet or using an uploaded reference or template.
    - Before modifying: ALWAYS study and match the existing format, style and conventions when making edits by rendering and viewing the image. Read related values and formulas.
    - For visual fix requests, start with the smallest plausible local change. Do not apply sheet-wide autofit, wrapping, or restyling unless requested.
    - Ensure existing formulas, layouts, structures, and patterns are consistent. For example, if asked to add another column or row to a table and there is conditional formatting applied to the whole table, it should extend to the new column or rows as well.
    - Keep edits targeted unless a broader change is clearly necessary. Exceptions are when there's dependencies, e.g. a dynamic chart that is based on the range of values in a table and a new row is added, the chart should also update.
    - Extend conditional formatting if needed to keep style consistent for an area or table.
    - Never overwrite formatting for spreadsheets with established formats, unless requested or to extend an added range.
    
    ## Importing or extracting data from screenshots or reference images
    - When a reference image or screenshot is provided, use appropriate data formats (e.g. number/date formats) based on the workbook topic, audience and purpose instead of trying to recreate the rendered format with just text. Preserve numeric/date usability even when the screenshot shows locale-specific punctuation or currency symbols.
    - Use formulas when appropriate and correct: For screenshot recreation, do not bulk-write numeric tables as all static values until you have separated any clearly formula-derived ranges; test adjacent numeric rows/columns for exact repeated relationships such as sums, differences, products, ratios, or constant multiples, then keep inputs hardcoded and write derived ranges as formulas.
    - Match visible styling, but do not infer intentional formatting from ambiguous image artifacts such as zoom, antialiasing, or compression. Infer font weight only from relative contrast or clear semantics; if all visible text has the same apparent weight, use normal weight.
    
    ## Handling queries and questions
    - The user may ask questions about the sheet instead of requesting an edit or a change. Simply answer those questions about the spreadsheet based on the context available rather than making an edit the user didn't intend for. Use the selected workflow's read tools to inspect relevant values, formulas, tables, and objects.
    - For a read-only question, do not modify or export the workbook.
    - Locate the requested output by its row and column labels and period, inspect its displayed value and formula, and trace formula precedents to labeled assumptions or raw inputs instead of stopping at an intermediate total.
    - Explain calculations with the workbook's displayed values and preserve units and period conversions. For broad questions about assumptions or drivers, rank the inputs that actually drive the requested output rather than inferring from nearby labels.
    
    ## Error Recovery
    On first tool or API error:
    1. Read error text.
    2. Consult the selected workflow's targeted help or schema discovery only if needed.
    3. Retry with minimal patch (not full rewrite).
    4. Continue from existing workbook state.
    
    Do not loop indefinitely on similar failures.
    
    ## Formula Rules
    - Place assumptions and raw data in dedicated cells or clearly delineated input ranges, following the reference workbook's organization when one is provided.
    - Keep lookup, mapping, scoring, and quality-control rules in visible cells or tables and reference them from formulas instead of hardcoding the logic.
    - Derived values must be formulas (not hardcoded) and legible.
    - Keep calculations formula driven, and prefer consistent formula patterns across a range where possible for readability. For example, formulas should be consistent across all projection periods.
    - Use absolute/relative references correctly for fill/copy behavior.
    - Use references instead of hardcoded or magic numbers inside formulas e.g. Use `=A5*(1+$A$6)` instead of =A5*1.05
    - Formulas should be simple, legible and **easily auditable**. Use helper cells for intermediate values rather than performing complex calculations in a single cell. Users should be able to trace the model from inputs to outputs easily.
    - No harcoded numbers inside calculation areas unless explicitly allowed. Always ensure color formatting conventions are properly applied.
    - For any complex formulas or important assumptions, add comments to cells to explain.
    - Always reference cells on other Excel sheets using the format ='Sheet Name'!A1, wrapping the sheet name in single quotes every time since quotes are required for any spaces or special characters.
    
    ### Ensure formulas are correct
    - Checklist: No formula errors, all cell references are correct, no off-by-one errors in ranges, edge cases (zero values, negative numbers) are handled, no unintended circular references.
    - For source-backed analyses and summaries, spot-check representative outputs and reconcile key totals with source definitions.
    
    ## Data Formatting Rules
    - Store numbers, percentages, currency, and dates as typed spreadsheet values, not preformatted strings. Use text only for true identifiers such as ZIP codes, account IDs, SKUs, or labels.
    - Use Excel-invariant number/date format codes, not locale-specific display strings. Examples include `#,##0`, `#,##0.0`, `0.0%`, `0.00%`, `"$"#,##0`, `"$"#,##0.00`, `yyyy-mm-dd`, `mmm yyyy` but choose the format that best fits the data.
    - Percentages: When not specified or no reference is provided, use 1 decimal for most internal/analytical cells, 0 decimals for user-facing/dashboard outputs, and 2 decimals where small differences in rates matter.
    - Do not swap `.` and `,` in format codes to mimic locale separators; separators are controlled by spreadsheet/render locale. Use `0.0%`, not `0,0%`, and `#,##0`, not `#.##0`.
    - Choose the appropriate format for readability. Match precision to meaning: counts use `#,##0`; rates usually use `0.0%` or `0.00%`; currency uses whole units unless cents matter.
    
    ## Quality Guidelines
    - Build correct, readable workbooks for the intended audience with clear structure, consistent formatting, reliable formulas, and useful outputs. Keep them as simple as practical.
    - After autofit and wrapping, cap oversized column widths and row heights.
    - Make workbooks easy for another person to update, trace, and audit without the original author.
    
    ### Spreadsheets clarification questions
    
    - Ask for new spreadsheets or major rewrites. Skip this for edits/conversions.
    - Inspect prompt, conversation history, existing file and relevant references to figure out what questions to ask.
    - Questions should cover topic, audience, and purpose and come before planning
    - When asking questions, focus on consequential dimensions not stated or clearly implied.
    - When the artifact is a new analysis, focus on which definition, metric, or lens should drive conclusions.
    - Unresolved reference labels or question marks are user-owned: ask, don't infer.
    - Once topic, audience, and purpose are clear, proceed without asking. Choose emphasis, format, length, style, details. Use placeholders for missing facts.
    
    Use `request_user_input` once if available, else ask via a message. First option should be `Use your judgment (Recommended)` exactly. Recommend no other. Add 1â€“2 exclusive alternatives.
    
    ## Completion Criteria
    ### Criteria for Question / Read only requests
    - Answer from the available workbook context. Do not edit or overwrite unless the user asks for a workbook change.
    
    ### Criteria for all create and edit requests
    Complete only when:
    - Workbook content is populated and formulas compute.
    - No obvious formula errors in key scanned ranges (no bad refs/off-by-one/circular errors).
    - `.xlsx` saved to `outputs/<unique_thread_id>/`.
    - Visual render verification passes:
      - Layout is organized, legible, and aligned to request style (or default/existing formatting baseline for edits).
      - Important numbers and callouts are all visible.
      - Numbers, text, charts and content is not clipped or awkwardly wrapped.
    
    ## Verification Rules
    Before final response, verify values/formulas and visual quality.
    
    1. Inspect key ranges:
    ```js
    const check = await workbook.inspect({
      kind: "table",
      range: "Dashboard!A1:H20",
      include: "values,formulas",
      tableMaxRows: 20,
      tableMaxCols: 12,
    });
    console.log(check.ndjson);
    ```
    
    2. Scan formula errors:
    ```js
    const errors = await workbook.inspect({
      kind: "match",
      searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
      options: { useRegex: true, maxResults: 300 },
      summary: "final formula error scan",
    });
    console.log(errors.ndjson);
    ```
    
    3. Render sheets/ranges to verify visual output (skip if already verified and no style changes):
    ```js
    const blob = await workbook.render({ sheetName: "Sheet1", range: "A1:H20", scale: 2 });
    ```
    Make sure you do at least one visual pass of all the sheets in the workbook before the final export.
    
    Visual requirements:
    - Fix severe defects before finalizing: blank/broken charts, clipped key headers or numbers, unreadable colors, obvious formula errors, default blank sheets, or content outside the visible working area.
    - Ensure logical labels or titles appear once, and merged ranges exist where labels or content intentionally span multiple columns.
    - Ensure texts are all clearly visible and NOT clipped, columns and appropriately sized
    - Do focused visual repair pass(s) after the initial render. Limit looping/time sinks for minor polish: stop once the workbook is correct, legible, and exported; note any minor limitation briefly and finalize.
    
    4. Keep verification compact:
    - Inspect key ranges.
    - Avoid huge NDJSON dumps.
    
    5. Export:
    ```js
    await fs.mkdir(outputDir, { recursive: true });
    const output = await SpreadsheetFile.exportXlsx(workbook);
    await output.save(`${outputDir}/output.xlsx`);
    ```
    
    6. Finalize immediately after successful export + compact verification.
    - Do not export extra `.xlsx` variants unless asked.
    
    ## Citation Requirements
    ### Cite sources inside the spreadsheet
    - Use plain-text URLs in spreadsheet cells.
    - For financial models, cite model-input sources in cell comments.
    - For researched row-wise data tables, include source URLs in a dedicated source column.
    
    ## Final response citations
    
    Place :codex-file-citation{...} inline in prose without wrapping it in backticks or a code block, not in a trailing list. Use `purpose="source"` for Q&A/no-op and `purpose="output"` for create/edit.
    
    - [HARD REQUIREMENT] Create/edit: cite each final workbook exactly once with a plain output citation. Summarize representative changes; do not cite every sheet/range or add a separate filename, path, or Markdown link. Example: `Created :codex-file-citation{path="/abs/path/inventory.xlsx" purpose="output"} with formula-driven status and a summary.`
    - Q&A: cite whole-workbook claims plainly; otherwise use the narrowest reliable `sheet` + `range` (the exact cell for a discrete value). Cite discontiguous cells separately. For objects, use `sheet` + exact inspected `object_id`; add `object_kind`/`label` only when useful. Never cite a sheet alone or guess locators.
    - Calculations: cite only distinct inputs, drivers, formulas, or results the answer needs.
    
    :codex-file-citation{path="/abs/path/book.xlsx" purpose="source" artifact_kind="workbook" sheet="Revenue Model" range="C27"}
    
    Never cite intermediates unless asked.
    
    ## Comment Author
    - If the authenticated/user profile or env context provides a user display name, use it as the threaded comment display name unless the user requests another name. Default to `User`.
    
    
    ## Source, PDF, and Attachment Processing
    - Keep source notes compact: record file name, section/table label, and enough context to audit the number. Do not paste large PDF excerpts into the workbook unless requested.
    - Bundled Python libraries available in the bundled runtime environment for extraction/analysis include `pandas`, `numpy`, `pypdf`, `python-docx`, and `reportlab`. You may read/extract in separate scripts if needed.
    - Bundled JS libraries available for document/PDF work include `docx`, `pdf-lib`, and `pdfjs-dist`.
    
    ✓ • 70ms

## Activity

    $ py -3 -c "import sys, pandas, openpyxl; print(sys.version); print('pandas', pandas.__version__); print('openpyxl', openpyxl.__version__)"
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
        import sys, pandas, openpyxl; print(sys.version); print('pandas', pandas.__version__); print('openpyxl', openpyxl.__version__)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ModuleNotFoundError: No module named 'pandas'
    ✗ (1) • 263ms

## Activity

    $ py -3 -c "import sys; print(sys.version); import docx; print('python-docx available')"
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
        import sys; print(sys.version); import docx; print('python-docx available')
                                        ^^^^^^^^^^^
    3.14.2 (tags/v3.14.2:df79316, Dec  5 2025, 17:18:21) [MSC v.1944 64 bit (AMD64)]
    ModuleNotFoundError: No module named 'docx'
    ✗ (1) • 37ms

## Activity

    $ Get-Command soffice -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source; Get-Command pdftotext -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source; Get-Command pdfinfo -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source; Get-Command node -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
    C:\Program Files\Git\mingw64\bin\pdftotext.exe
    C:\Users\nitin\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdfinfo.exe
    C:\Program Files\nodejs\node.exe
    ✓ • 684ms

## Activity

    $ Get-Command pandoc -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source; Get-Command word -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source; Get-ChildItem 'C:\Program Files\Microsoft Office' -Recurse -Filter WINWORD.EXE -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
    C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE
    ✓ • 781ms

## Activity

    $ & { $files = Get-ChildItem -File -Recurse -Filter '*.csv' | Sort-Object FullName; foreach ($f in $files) { try { $rows = @(Import-Csv -LiteralPath $f.FullName -ErrorAction Stop); $headers = if ($rows.Count -gt 0) { @($rows[0].PSObject.Properties.Name) } else { @((Get-Content -LiteralPath $f.FullName -TotalCount 1) -split ',') }; $missing = foreach ($h in $headers) { $n = @($rows | Where-Object { [string]::IsNullOrWhiteSpace([string]$_.PSObject.Properties[$h].Value) }).Count; "$h=$n" }; [PSCustomObject]@{File=$f.Name; Bytes=$f.Length; Rows=$rows.Count; Columns=$headers.Count; Headers=($headers -join ' | '); BlankCells=($missing -join '; ')} | ConvertTo-Json -Compress } catch { [PSCustomObject]@{File=$f.Name; Error=$_.Exception.Message} | ConvertTo-Json -Compress } } }
    {"File":"area-wise-waterbodies-india-statewise.csv","Bytes":1486,"Rows":37,"Columns":8,"Headers":"State | \u003c 0.5 ha | \u003e= 0.5 - \u003c 1 ha | \u003e= 1 - \u003c 2 ha | \u003e= 2 - \u003c 10 ha | \u003e= 10 - \u003c 50 ha | \u003e= 50 - \u003c 100 ha | \u003e= 100 ha","BlankCells":"State=0; \u003c 0.5 ha=0; \u003e= 0.5 - \u003c 1 ha=0; \u003e= 1 - \u003c 2 ha=0; \u003e= 2 - \u003c 10 ha=0; \u003e= 10 - \u003c 50 ha=0; \u003e= 50 - \u003c 100 ha=0; \u003e= 100 ha=0"}
    {"File":"cea_historical_coal_consumption_2004_2023.csv","Bytes":707,"Rows":43,"Columns":2,"Headers":"Financial_Year | Coal_Consumption_Million_Tonnes","BlankCells":"Financial_Year=0; Coal_Consumption_Million_Tonnes=0"}
    {"File":"cea_historical_cost_of_power_supply_and_realisation.csv","Bytes":376,"Rows":9,"Columns":4,"Headers":"Financial_Year | Cost_of_Supply_paise_per_kWh | Realisation_incl_Agriculture_paise_per_kWh | Realisation_Agriculture_Only_paise_per_kWh","BlankCells":"Financial_Year=0; Cost_of_Supply_paise_per_kWh=0; Realisation_incl_Agriculture_paise_per_kWh=0; Realisation_Agriculture_Only_paise_per_kWh=0"}
    {"File":"cea_historical_energy_requirement_availability_2003_2026.csv","Bytes":1311,"Rows":23,"Columns":7,"Headers":"Financial_Year | Energy_Requirement_MU | Energy_Availability_MU | Energy_Surplus_Deficit_MU | Energy_Deficit_Pct | Growth_Energy_Requirement_Pct | Growth_Energy_Availability_Pct","BlankCells":"Financial_Year=0; Energy_Requirement_MU=0; Energy_Availability_MU=0; Energy_Surplus_Deficit_MU=0; Energy_Deficit_Pct=0; Growth_Energy_Requirement_Pct=0; Growth_Energy_Availability_Pct=0"}
    {"File":"cea_historical_peak_demand_met_2003_2026.csv","Bytes":1237,"Rows":23,"Columns":7,"Headers":"Financial_Year | Peak_Demand_MW | Peak_Met_MW | Peak_Surplus_Deficit_MW | Peak_Deficit_Pct | Growth_Peak_Demand_Pct | Growth_Peak_Met_Pct","BlankCells":"Financial_Year=0; Peak_Demand_MW=0; Peak_Met_MW=0; Peak_Surplus_Deficit_MW=0; Peak_Deficit_Pct=0; Growth_Peak_Demand_Pct=0; Growth_Peak_Met_Pct=0"}
    {"File":"cea_historical_per_capita_consumption_2005_2023.csv","Bytes":567,"Rows":34,"Columns":2,"Headers":"Financial_Year | Per_Capita_Consumption_kWh","BlankCells":"Financial_Year=0; Per_Capita_Consumption_kWh=0"}
    {"File":"cea_historical_power_capacity_growth_since_1985.csv","Bytes":879,"Rows":8,"Columns":9,"Headers":"Plan_Year | Thermal_Coal_MW | Thermal_Gas_MW | Thermal_Diesel_MW | Thermal_Total_MW | Nuclear_MW | Hydro_MW | RES_MNRE_MW | Grand_Total_MW","BlankCells":"Plan_Year=0; Thermal_Coal_MW=0; Thermal_Gas_MW=0; Thermal_Diesel_MW=0; Thermal_Total_MW=0; Nuclear_MW=0; Hydro_MW=0; RES_MNRE_MW=0; Grand_Total_MW=0"}
    {"File":"cea_installed_capacity_statewise_fuelwise_jul2026.csv","Bytes":17437,"Rows":177,"Columns":13,"Headers":"Region | State_UT | Sector | Coal_MW | Lignite_MW | Gas_MW | Diesel_MW | Thermal_Total_MW | Nuclear_MW | Hydro_MW | RES_MNRE_MW | Total_RES_incl_Hydro_MW | Grand_Total_MW","BlankCells":"Region=0; State_UT=0; Sector=0; Coal_MW=0; Lignite_MW=0; Gas_MW=0; Diesel_MW=0; Thermal_Total_MW=0; Nuclear_MW=0; Hydro_MW=0; RES_MNRE_MW=0; Total_RES_incl_Hydro_MW=0; Grand_Total_MW=0"}
    {"File":"cea_transmission_grid_voltage_classes.csv","Bytes":408,"Rows":5,"Columns":4,"Headers":"Voltage_Level | Line_Type | Voltage_kV | Typical_Application","BlankCells":"Voltage_Level=0; Line_Type=0; Voltage_kV=0; Typical_Application=0"}
    {"File":"cubems-smart-building-energy-and-iaq-summary.csv","Bytes":1663,"Rows":14,"Columns":9,"Headers":"file | floor | year | rows | total_kw_minutes | light_kw_minutes | plug_kw_minutes | ac_kw_minutes | peak_kw","BlankCells":"file=0; floor=0; year=0; rows=0; total_kw_minutes=0; light_kw_minutes=0; plug_kw_minutes=0; ac_kw_minutes=0; peak_kw=0"}
    {"File":"Datacenters distribution in india.csv","Bytes":425,"Rows":34,"Columns":2,"Headers":"Market | Data Centers","BlankCells":"Market=0; Data Centers=0"}
    {"File":"Electricity Substation.csv","Bytes":1073,"Rows":12,"Columns":8,"Headers":"City Name | Ward No. | Year | Name of Electrical Substations | Address | Longitude | Latitude | Capacity (MVA)","BlankCells":"City Name=0; Ward No.=0; Year=0; Name of Electrical Substations=0; Address=0; Longitude=0; Latitude=0; Capacity (MVA)=0"}
    {"File":"file_02.csv","Bytes":303684,"Rows":4945,"Columns":9,"Headers":"index | Date | Region | Thermal Generation Actual (in MU) | Thermal Generation Estimated (in MU) | Nuclear Generation Actual (in MU) | Nuclear Generation Estimated (in MU) | Hydro Generation Actual (in MU) | Hydro Generation Estimated (in MU)","BlankCells":"index=0; Date=0; Region=0; Thermal Generation Actual (in MU)=0; Thermal Generation Estimated (in MU)=0; Nuclear Generation Actual (in MU)=1854; Nuclear Generation Estimated (in MU)=1854; Hydro Generation Actual (in MU)=0; Hydro Generation Estimated (in MU)=0"}
    {"File":"mnre_bio_and_solar_breakdown_2025.csv","Bytes":2302,"Rows":41,"Columns":9,"Headers":"State_UT | Biomass_Bagasse_Cogen_MW | Biomass_Non_Bagasse_Cogen_MW | Waste_to_Energy_Grid_MW | Waste_to_Energy_Offgrid_MW | Solar_Ground_Mounted_MW | Solar_Rooftop_MW | Solar_Hybrid_Component_MW | Solar_Offgrid_KUSUM_MW","BlankCells":"State_UT=0; Biomass_Bagasse_Cogen_MW=0; Biomass_Non_Bagasse_Cogen_MW=0; Waste_to_Energy_Grid_MW=0; Waste_to_Energy_Offgrid_MW=0; Solar_Ground_Mounted_MW=0; Solar_Rooftop_MW=0; Solar_Hybrid_Component_MW=0; Solar_Offgrid_KUSUM_MW=0"}
    {"File":"mnre_re_cumulative_capacity_timeseries_2018_2025.csv","Bytes":3743,"Rows":42,"Columns":10,"Headers":"Region | State_UT | RE_MW_2017_18 | RE_MW_2018_19 | RE_MW_2019_20 | RE_MW_2020_21 | RE_MW_2021_22 | RE_MW_2022_23 | RE_MW_2023_24 | RE_MW_2024_25","BlankCells":"Region=0; State_UT=0; RE_MW_2017_18=0; RE_MW_2018_19=0; RE_MW_2019_20=0; RE_MW_2020_21=0; RE_MW_2021_22=0; RE_MW_2022_23=0; RE_MW_2023_24=0; RE_MW_2024_25=0"}
    {"File":"mnre_re_estimated_potential_by_state.csv","Bytes":2411,"Rows":38,"Columns":8,"Headers":"State_UT | Wind_Potential_MW | Small_Hydro_Potential_MW | Biomass_Potential_MW | Bagasse_Cogen_Potential_MW | Solar_Ground_Potential_MW | Large_Hydro_Potential_MW | Total_Estimated_RE_Potential_MW","BlankCells":"State_UT=0; Wind_Potential_MW=0; Small_Hydro_Potential_MW=0; Biomass_Potential_MW=0; Bagasse_Cogen_Potential_MW=0; Solar_Ground_Potential_MW=0; Large_Hydro_Potential_MW=0; Total_Estimated_RE_Potential_MW=0"}
    {"File":"mnre_re_generation_by_source_statewise_2024_2025.csv","Bytes":1894,"Rows":38,"Columns":7,"Headers":"State_UT | Small_Hydro_MU | Wind_Power_MU | Bio_Power_MU | Solar_Power_MU | Large_Hydro_MU | Total_RE_Generation_MU","BlankCells":"State_UT=0; Small_Hydro_MU=0; Wind_Power_MU=0; Bio_Power_MU=0; Solar_Power_MU=0; Large_Hydro_MU=0; Total_RE_Generation_MU=0"}
    {"File":"mnre_re_installed_capacity_by_source_2025.csv","Bytes":2023,"Rows":41,"Columns":7,"Headers":"State_UT | Small_Hydro_MW | Wind_Power_MW | Bio_Power_MW | Solar_Power_MW | Large_Hydro_MW | Total_RES_MW","BlankCells":"State_UT=0; Small_Hydro_MW=0; Wind_Power_MW=0; Bio_Power_MW=0; Solar_Power_MW=0; Large_Hydro_MW=0; Total_RES_MW=0"}
    {"File":"mnre_re_share_in_total_capacity_2025.csv","Bytes":2370,"Rows":39,"Columns":8,"Headers":"State_UT | Non_RE_Capacity_MW | RES_excl_Hydro_MW | Large_Hydro_MW | Total_RE_incl_Hydro_MW | Grand_Total_Capacity_MW | RES_Share_Percent | RE_Share_Percent","BlankCells":"State_UT=0; Non_RE_Capacity_MW=0; RES_excl_Hydro_MW=0; Large_Hydro_MW=0; Total_RE_incl_Hydro_MW=0; Grand_Total_Capacity_MW=0; RES_Share_Percent=0; RE_Share_Percent=0"}
    {"File":"region_cordinates.csv","Bytes":155,"Rows":5,"Columns":3,"Headers":"Region | Latitude | Longitude","BlankCells":"Region=0; Latitude=0; Longitude=0"}
    {"File":"State_Region_corrected.csv","Bytes":1179,"Rows":34,"Columns":4,"Headers":"State / Union territory (UT) | Area (km2) | Region | National Share (%)","BlankCells":"State / Union territory (UT)=0; Area (km2)=0; Region=0; National Share (%)=0"}
    {"File":"state-ground-water-level-information.csv","Bytes":931,"Rows":29,"Columns":4,"Headers":"State | Total Number of Monitored Stations | Observed Range of Water Level-min | Observed Range of Water Level-max","BlankCells":"State=0; Total Number of Monitored Stations=0; Observed Range of Water Level-min=0; Observed Range of Water Level-max=0"}
    {"File":"statewise land cost.csv","Bytes":844,"Rows":12,"Columns":5,"Headers":"State | Lowest (Rs/Acre) | Average (Rs/Acre) | Highest (Rs/Acre) | 5-Year CAGR","BlankCells":"State=0; Lowest (Rs/Acre)=0; Average (Rs/Acre)=0; Highest (Rs/Acre)=0; 5-Year CAGR=0"}
    {"File":"Substation_Details_1789031375809.csv","Bytes":225414,"Rows":2851,"Columns":7,"Headers":"Name | Sector | Voltage Ratio (kV/kV) | Executive Agency | Capacity (MW/MVA) | Month Of Completion | Year Of Completion (FY)","BlankCells":"Name=2; Sector=5; Voltage Ratio (kV/kV)=5; Executive Agency=6; Capacity (MW/MVA)=5; Month Of Completion=5; Year Of Completion (FY)=5"}
    {"File":"sub-stations-220-kv-and.csv","Bytes":1521,"Rows":20,"Columns":2,"Headers":"Sector | State Sector","BlankCells":"Sector=0; State Sector=0"}
    {"File":"global-data-center-dataset.csv","Bytes":85939,"Rows":191,"Columns":21,"Headers":"country | total_data_centers | hyperscale_data_centers | colocation_data_centers | floor_space_sqft_total | power_capacity_MW_total | average_renewable_energy_usage_percent | tier_distribution | key_operators | cloud_provider | internet_penetration_percent | avg_latency_to_global_hubs_ms | number_of_fiber_connections | growth_rate_of_data_centers_percent_per_year | cooling_technologies_common | regulatory_challenges_or_limits | disaster_recovery_sites_common | green_dc_initiatives_description | source_of_data | Unnamed: 19 | Unnamed: 20","BlankCells":"country=0; total_data_centers=0; hyperscale_data_centers=0; colocation_data_centers=0; floor_space_sqft_total=10; power_capacity_MW_total=26; average_renewable_energy_usage_percent=46; tier_distribution=12; key_operators=21; cloud_provider=19; internet_penetration_percent=10; avg_latency_to_global_hubs_ms=29; number_of_fiber_connections=26; growth_rate_of_data_centers_percent_per_year=20; cooling_technologies_common=9; regulatory_challenges_or_limits=6; disaster_recovery_sites_common=17; green_dc_initiatives_description=22; source_of_data=6; Unnamed: 19=96; Unnamed: 20=119"}
    {"File":"global-data-center-dataset-original.csv","Bytes":92556,"Rows":191,"Columns":19,"Headers":"country | total_data_centers | hyperscale_data_centers | colocation_data_centers | floor_space_sqft_total | power_capacity_MW_total | average_renewable_energy_usage_percent | tier_distribution | key_operators | cloud_provider | internet_penetration_percent | avg_latency_to_global_hubs_ms | number_of_fiber_connections | growth_rate_of_data_centers_percent_per_year | cooling_technologies_common | regulatory_challenges_or_limits | disaster_recovery_sites_common | green_dc_initiatives_description | source_of_data","BlankCells":"country=0; total_data_centers=0; hyperscale_data_centers=0; colocation_data_centers=0; floor_space_sqft_total=0; power_capacity_MW_total=0; average_renewable_energy_usage_percent=0; tier_distribution=0; key_operators=10; cloud_provider=0; internet_penetration_percent=0; avg_latency_to_global_hubs_ms=0; number_of_fiber_connections=0; growth_rate_of_data_centers_percent_per_year=2; cooling_technologies_common=0; regulatory_challenges_or_limits=0; disaster_recovery_sites_common=1; green_dc_initiatives_description=12; source_of_data=4"}
    {"File":"global-data-center-energy-consumption.csv","Bytes":5190,"Rows":137,"Columns":3,"Headers":"Region | Country | Number of data centre","BlankCells":"Region=2; Country=2; Number of data centre=0"}
    ✓ • 2.32s

## Activity

    $ & { Get-ChildItem -File -Recurse -Filter '*.csv' | Sort-Object FullName | ForEach-Object { "`n### $($_.FullName.Substring((Get-Location).Path.Length + 1))"; Get-Content -LiteralPath $_.FullName -TotalCount 4 } }
    
    ### area-wise-waterbodies-india-statewise.csv
    State,< 0.5 ha,>= 0.5 - < 1 ha,>= 1 - < 2 ha,>= 2 - < 10 ha,>= 10 - < 50 ha,>= 50 - < 100 ha,>= 100 ha
    Andaman & Nicobar,9,1,2,9,4,6,2
    Andhra Pradesh,3342,5265,7203,14535,5057,783,548
    Arunachal Pradesh,187,150,222,488,214,13,1
    
    ### cea_historical_coal_consumption_2004_2023.csv
    Financial_Year,Coal_Consumption_Million_Tonnes
    2004-05,278.0
    2005-06,281.0
    2006-07,302.0
    
    ### cea_historical_cost_of_power_supply_and_realisation.csv
    Financial_Year,Cost_of_Supply_paise_per_kWh,Realisation_incl_Agriculture_paise_per_kWh,Realisation_Agriculture_Only_paise_per_kWh
    2004-05,254.0,209.0,75.68
    2005-06,260.0,221.0,76.36
    2006-07,276.0,227.0,74.23
    
    ### cea_historical_energy_requirement_availability_2003_2026.csv
    Financial_Year,Energy_Requirement_MU,Energy_Availability_MU,Energy_Surplus_Deficit_MU,Energy_Deficit_Pct,Growth_Energy_Requirement_Pct,Growth_Energy_Availability_Pct
    2003-04,559264.0,519398.0,-39866.0,-7.1,2.5,4.4
    2004-05,591373.0,548115.0,-43258.0,-7.3,5.7,5.5
    2005-06,631757.0,578819.0,-52938.0,-8.4,6.8,5.6
    
    ### cea_historical_peak_demand_met_2003_2026.csv
    Financial_Year,Peak_Demand_MW,Peak_Met_MW,Peak_Surplus_Deficit_MW,Peak_Deficit_Pct,Growth_Peak_Demand_Pct,Growth_Peak_Met_Pct
    2003-04,84574.0,75066.0,-9508.0,-11.2,3.8,4.9
    2004-05,87906.0,77652.0,-10254.0,-11.7,3.9,3.4
    2005-06,93255.0,81792.0,-11463.0,-12.3,6.1,5.3
    
    ### cea_historical_per_capita_consumption_2005_2023.csv
    Financial_Year,Per_Capita_Consumption_kWh
    2014-15,530.4
    2015-16,545.9
    2016-17,574.3
    
    ### cea_historical_power_capacity_growth_since_1985.csv
    Plan_Year,Thermal_Coal_MW,Thermal_Gas_MW,Thermal_Diesel_MW,Thermal_Total_MW,Nuclear_MW,Hydro_MW,RES_MNRE_MW,Grand_Total_MW
    End of 6th Plan(March-1985),26310.83,541.5,177.37,27029.7,1095.0,14460.02,0.0,42584.72
    End of 7th Plan (March-1990),41237.48,2343.0,165.09,43745.57,1565.0,18307.63,18.14,63636.34
    End of 8th Plan (March-1997),54154.48,6561.9,293.9,61010.28,2225.0,21658.08,902.01,85795.37
    
    ### cea_installed_capacity_statewise_fuelwise_jul2026.csv
    Region,State_UT,Sector,Coal_MW,Lignite_MW,Gas_MW,Diesel_MW,Thermal_Total_MW,Nuclear_MW,Hydro_MW,RES_MNRE_MW,Total_RES_incl_Hydro_MW,Grand_Total_MW
    Northern Region,Northern Region,State,0.0,0.0,1800.4,0.0,1800.4,0.0,0.0,0.0,0.0,1800.4
    Northern Region,Northern Region,Private,878.22,0.0,0.0,0.0,878.22,0.0,0.0,546.1,546.1,1424.32
    Northern Region,Northern Region,Central,2786.14,0.0,207.01,0.0,2993.16,153.38,1178.01,0.37,1178.38,4324.92
    
    ### cea_transmission_grid_voltage_classes.csv
    Voltage_Level,Line_Type,Voltage_kV,Typical_Application
    +/- 800 kV HVDC,HVDC,800,Long-distance bulk power corridor
    +/- 500 kV HVDC,HVDC,500,Inter-regional transmission corridor
    765 kV,Extra High Voltage AC,765,National & Regional grid backbone
    
    ### cubems-smart-building-energy-and-iaq-summary.csv
    file,floor,year,rows,total_kw_minutes,light_kw_minutes,plug_kw_minutes,ac_kw_minutes,peak_kw
    cubems-smart-building-energy-and-iaq-data/2018Floor1.csv,1,2018,264960,30323000,16333500,5086570,8902940,4794.33
    cubems-smart-building-energy-and-iaq-data/2018Floor2.csv,2,2018,264960,41161700,1275570,438372,5727340,585.02
    cubems-smart-building-energy-and-iaq-data/2018Floor3.csv,3,2018,264960,43532700,1282840,291586,2853630,700.26
    
    ### Datacenters distribution in india.csv
    Market,Data Centers
    Mumbai,60
    Chennai,33
    Hyderabad,36
    
    ### Electricity Substation.csv
    City Name,Ward No.,Year,Name of Electrical Substations,Address,Longitude,Latitude,Capacity (MVA)
    Aizawl,NA,Dec-19,New 132 kV Zuangtui Sub-Station,Zuangtui,88.5966,22.5446,2 x 25
    Aizawl,NA,Jul-01,132 kV Zuangtui Sub-Station,Zuangtui,88.5966,22.5446,4 x 12.5
    Aizawl,NA,Jul-02,132 kV Luangmual Sub-Station,Luangmual,92.7835,23.797,3 x 12.5
    
    ### file_02.csv
    index,Date,Region,Thermal Generation Actual (in MU),Thermal Generation Estimated (in MU),Nuclear Generation Actual (in MU),Nuclear Generation Estimated (in MU),Hydro Generation Actual (in MU),Hydro Generation Estimated (in MU)
    0,2017-09-01,Northern,624.23,484.21,30.36,35.57,273.27,320.81
    1,2017-09-01,Western,"1,106.89","1,024.33",25.17,3.81,72.0,21.53
    2,2017-09-01,Southern,576.66,578.55,62.73,49.8,111.57,64.78
    
    ### mnre_bio_and_solar_breakdown_2025.csv
    State_UT,Biomass_Bagasse_Cogen_MW,Biomass_Non_Bagasse_Cogen_MW,Waste_to_Energy_Grid_MW,Waste_to_Energy_Offgrid_MW,Solar_Ground_Mounted_MW,Solar_Rooftop_MW,Solar_Hybrid_Component_MW,Solar_Offgrid_KUSUM_MW
    Andhra Pradesh,378.1,113.57,53.16,49.19,4990.86,290.8,0.0,88.34
    Arunachal Pradesh,0.0,0.0,0.0,0.0,1.27,6.68,0.0,6.9
    Assam,0.0,2.0,0.0,0.0,126.0,61.1,0.0,9.44
    
    ### mnre_re_cumulative_capacity_timeseries_2018_2025.csv
    Region,State_UT,RE_MW_2017_18,RE_MW_2018_19,RE_MW_2019_20,RE_MW_2020_21,RE_MW_2021_22,RE_MW_2022_23,RE_MW_2023_24,RE_MW_2024_25
    Northern Region,Haryana,510.49,519.11,547.19,762.51,1242.13,1362.09,1832.92,2449.94
    Northern Region,Himachal Pradesh,10514.3,10707.75,10768.91,10916.61,11303.49,11330.42,11356.16,12196.18
    Northern Region,Jammu & Kashmir,3650.22,3664.1,3581.11,3588.11,3551.61,3556.12,3595.37,3624.42
    
    ### mnre_re_estimated_potential_by_state.csv
    State_UT,Wind_Potential_MW,Small_Hydro_Potential_MW,Biomass_Potential_MW,Bagasse_Cogen_Potential_MW,Solar_Ground_Potential_MW,Large_Hydro_Potential_MW,Total_Estimated_RE_Potential_MW
    Andhra Pradesh,123336.0,409.32,1999.49,279.6,299312.12,2596.0,427932.53
    Arunachal Pradesh,246.0,2064.92,18.46,0.0,467.52,50394.0,53190.9
    Assam,459.0,201.99,321.89,0.0,19173.13,643.0,20799.01
    
    ### mnre_re_generation_by_source_statewise_2024_2025.csv
    State_UT,Small_Hydro_MU,Wind_Power_MU,Bio_Power_MU,Solar_Power_MU,Large_Hydro_MU,Total_RE_Generation_MU
    Andhra Pradesh,294.36,7235.04,379.35,7993.48,0.0,9205.31
    Arunachal Pradesh,0.58,0.0,0.0,1.3,4205.16,4207.04
    Assam,208.55,0.0,0.3,305.52,998.75,1513.11
    
    ### mnre_re_installed_capacity_by_source_2025.csv
    State_UT,Small_Hydro_MW,Wind_Power_MW,Bio_Power_MW,Solar_Power_MW,Large_Hydro_MW,Total_RES_MW
    Andhra Pradesh,163.31,4377.15,594.02,5370.0,1610.0,12114.48
    Arunachal Pradesh,140.61,0.0,0.0,14.85,1115.0,1270.46
    Assam,34.11,0.0,2.0,196.54,350.0,582.65
    
    ### mnre_re_share_in_total_capacity_2025.csv
    State_UT,Non_RE_Capacity_MW,RES_excl_Hydro_MW,Large_Hydro_MW,Total_RE_incl_Hydro_MW,Grand_Total_Capacity_MW,RES_Share_Percent,RE_Share_Percent
    Andhra Pradesh,17905.34,10504.48,1610.0,12114.48,30019.82,34.99,40.35
    Arunachal Pradesh,0.0,155.46,1115.0,1270.46,1270.46,12.24,100.0
    Assam,1347.36,232.65,350.0,582.65,1930.01,12.05,30.19
    
    ### region_cordinates.csv
    Region,Latitude,Longitude
    NorthEastern,25.5736,93.2473
    Eastern,22.8962,85.98
    Western ,23.9074,72.7097
    
    ### State_Region_corrected.csv
    State / Union territory (UT),Area (km2),Region,National Share (%)
    Rajasthan,342239,Northern,10.55
    Madhya Pradesh,308350,Central,9.37
    Maharashtra,307713,Western,9.36
    
    ### state-ground-water-level-information.csv
    State,Total Number of Monitored Stations,Observed Range of Water Level-min,Observed Range of Water Level-max
    Andhra Pradesh,280,-98.46,203.54
    Arunachal Pradesh,4,-4.19,-0.52
    Assam,68,-89.66,30.73
    
    ### statewise land cost.csv
    "State","Lowest (Rs/Acre)","Average (Rs/Acre)","Highest (Rs/Acre)","5-Year CAGR"
    "Rajasthan","â‚¹50,000","â‚¹8,00,000","â‚¹30,00,000","14%"
    "Madhya Pradesh","â‚¹2,00,000","â‚¹5,00,000","â‚¹25,00,000","18%"
    "Uttar Pradesh","â‚¹3,00,000","â‚¹12,00,000","â‚¹80,00,000","15%"
    
    ### Substation_Details_1789031375809.csv
    Name,Sector,Voltage Ratio (kV/kV),Executive Agency,Capacity (MW/MVA),Month Of Completion,Year Of Completion (FY)
    Biswanath Chariyali & Agra HVDC terminal (Pole-I),Central,Â±800,PGCIL,1500.0,NOV-15,2015-16
    Angul (ICT-II),Central,765/400,PGCIL,1500.0,APR-15,2015-16
    Bareilly (ICT-I),Central,765/400,PGCIL,1500.0,APR-15,2015-16
    
    ### sub-stations-220-kv-and.csv
    "Sector","State Sector"
    "400/220kV/kV<br>Bhopal 400 kV SS (replacement of 315 MVA by 500 MVA T/F)",185
    "400/220kV/kV<br>400 kV S/S Nakodar",500
    "400/110kV/kV<br>Vellalaviduthi (400/110 kV T/F-II)",200
    
    ### Unrequired data\global-data-center-dataset.csv
    country,total_data_centers,hyperscale_data_centers,colocation_data_centers,floor_space_sqft_total,power_capacity_MW_total,average_renewable_energy_usage_percent,tier_distribution,key_operators,cloud_provider,internet_penetration_percent,avg_latency_to_global_hubs_ms,number_of_fiber_connections,growth_rate_of_data_centers_percent_per_year,cooling_technologies_common,regulatory_challenges_or_limits,disaster_recovery_sites_common,green_dc_initiatives_description,source_of_data,Unnamed: 19,Unnamed: 20,,,,,,,,,,,,,,,,,,
    United States,5426,300,2000,3552000000,12000,27,I:5 II:15 III:60 IV:20,Equinix Digital Realty CoreSite AWS,AWS:Yes GCP:Yes Azure:Yes Oracle:Yes,92,40,60,12,Air Liquid Immersion,Power grid strain in VA moratoriums in some states,Yes especially for finance/health,Solar wind PPA immersion cooling LEED,Statista Brightlio IEA CBRE,,,,,,,,,,,,,,,,,,,,
    Germany,529,50,200,350000000,2000,40,II:10 III:70 IV:20,Equinix Digital Realty e-shelter,AWS:Yes GCP:Yes Azure:Yes Oracle:Yes,92,50,30,8,Air Indirect Evap.,Power caps in Frankfurt strict emissions,Yes especially for finance,Wind solar carbon-neutral push,Statista CBRE IEA,,,,,,,,,,,,,,,,,,,,
    United Kingdom,523,30,150,200000000,1000,0.45,II:15 III:70 IV:15,Equinix Telehouse Virtus,AWS:Yes GCP:Yes Azure:Yes Oracle:Yes,96,40,25,7,Air Free Cooling,Power grid constraints in London,Yes especially for finance,Wind solar carbon-neutral targets,Statista CBRE IEA,,,,,,,,,,,,,,,,,,,,
    
    ### Unrequired data\global-data-center-dataset-original.csv
    country,total_data_centers,hyperscale_data_centers,colocation_data_centers,floor_space_sqft_total,power_capacity_MW_total,average_renewable_energy_usage_percent,tier_distribution,key_operators,cloud_provider,internet_penetration_percent,avg_latency_to_global_hubs_ms,number_of_fiber_connections,growth_rate_of_data_centers_percent_per_year,cooling_technologies_common,regulatory_challenges_or_limits,disaster_recovery_sites_common,green_dc_initiatives_description,source_of_data,,,,,,,,,,,,,,,,
    United States,5426,300+,"~2,000+","~3,552,000,000","~12,000+",~27%,"I:5%, II:15%, III:60%, IV:20%","Equinix, Digital Realty, CoreSite, AWS","AWS:Yes, GCP:Yes, Azure:Yes, Oracle:Yes",92%,40,60+,12%,"Air, Liquid, Immersion","Power grid strain in VA, moratoriums in some states","Yes, especially for finance/health","Solar, wind PPA, immersion cooling, LEED","Statista, Brightlio, IEA, CBRE",,,,,,,,,,,,,,,,
    Germany,529,50,~200,"~350,000,000","~2,000+",40%+,"II:10%, III:70%, IV:20%","Equinix, Digital Realty, e-shelter","AWS:Yes, GCP:Yes, Azure:Yes, Oracle:Yes",92%,50,30+,8%,"Air, Indirect Evap.","Power caps in Frankfurt, strict emissions","Yes, especially for finance","Wind, solar, carbon-neutral push","Statista, CBRE, IEA",,,,,,,,,,,,,,,,
    United Kingdom,523,30,~150,"~200,000,000","~1,000+",0.45,"II:15%, III:70%, IV:15%","Equinix, Telehouse, Virtus","AWS:Yes, GCP:Yes, Azure:Yes, Oracle:Yes",96%,40,25+,7%,"Air, Free Cooling",Power grid constraints in London,"Yes, especially for finance","Wind, solar, carbon-neutral targets","Statista, CBRE, IEA",,,,,,,,,,,,,,,,
    
    ### Unrequired data\global-data-center-energy-consumption.csv
    Region,Country,Number of data centre,,,,,
    ,,Total,both metrics available,n/a white space data,n/a gross power data,available white space data,available gross power data
    Americas,Dominican Republic,1,0,1,1,0,0
    Americas,Guatemala,1,0,1,1,0,0
    ✓ • 193ms

## Activity

    $ & { $excel = New-Object -ComObject Excel.Application; $excel.Visible = $false; $excel.DisplayAlerts = $false; try { Get-ChildItem -File -Filter '*.xlsx' | Sort-Object Name | ForEach-Object { $wb = $excel.Workbooks.Open($_.FullName, 0, $true); try { foreach ($ws in $wb.Worksheets) { $used = $ws.UsedRange; $rows = $used.Rows.Count; $cols = $used.Columns.Count; $headers = @(); for ($c = 1; $c -le $cols; $c++) { $headers += [string]$used.Cells.Item(1,$c).Text }; [PSCustomObject]@{File=$_.Name; Sheet=$ws.Name; Rows=$rows-1; Columns=$cols; Headers=($headers -join ' | ')} | ConvertTo-Json -Compress } } finally { $wb.Close($false) } } } finally { $excel.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($excel) } }
    {"File":"Datacenters distribution in india.xlsx","Sheet":"Substation_Details","Rows":34,"Columns":2,"Headers":"Market | Data Centers"}
    {"File":"Substation_Details_1789031375809.xlsx","Sheet":"Substation_Details","Rows":2851,"Columns":7,"Headers":"Name | Sector | Voltage Ratio (kV/kV) | Executive Agency | Capacity (MW/MVA) | Month Of Completion | Year Of Completion (FY)"}
    ✓ • 11.49s

## Activity

    $ & { Get-ChildItem -File -Filter '*.pdf' | Sort-Object Name | ForEach-Object { "### $($_.Name)"; & 'C:\Users\nitin\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdfinfo.exe' $_.FullName | Select-String 'Pages|Title|Author|Creator|Producer|Page size'; '--- Extract preview ---'; & 'C:\Program Files\Git\mingw64\bin\pdftotext.exe' -layout $_.FullName - | Select-Object -First 80 } }
    ### Executive_Summary_July_2026_Actual.pdf
    
    Author:          RKGUPTA
    Creator:         Microsoft® Excel® 2013
    Producer:        Microsoft® Excel® 2013
    Pages:           66
    Page size:       595.2 x 841.68 pts (A4)
    --- Extract preview ---
    
                             Government of India
    
    
                               Ministry of Power
    
                      Central Electricity Authority
    
    Executive Summary on Power Sector
                          July-2026
        Executive Summary for the Month of July-2026
    
                                                     Contents
    
    SN                              Section A - Highlights of Power Sector                                      Page
    
    1 Electricity Generation                                                                                    1A & 1B
                                                                                                                     2
    2 Generating Capacity Addition                                                                                   3
                                                                                                                     3
    3 List of Projects Commissioned                                                                                  4
                                                                                                                     5
    4 All India Installed Capacity (MW) Region-wise                                                                  6
                                                                                                                     7
    5 All India Installed Capacity (MW) Sector-wise as on 31-07-2026                                               8-9
                                                                                                                    10
    6 Transmission Lines Added during the month
                                                                                                                    11
    7 Transformation Capacity Addition
    
    8 Power Supply Position (Energy & Peak)
    
    9 Peak Shortage of Power Supply (MW) in Different Regions
    
    10 All India PLF Sector-wise
    
    11 Trend of T & D and AT & C Losses (%)
    
    12 All India Village Electrification Status
    
    13 Average cost of Power & Average Realisation
    
    14 All India Coal consumption for Power Generation (MT)
    
                                        Section B - Capacity Addition
    
    1   Capacity Addition Targets and Achievements in 12th Plan(2012-17), 2017-18 , 2018-19 ,2019-20, 2020-21,  12
        2022-23,2023-24
    
    2 Capacity Addition Targets & Achievements during Jul-2026 and Apr-26 to Jul-26                               13
    3 Installed Capacity in various Regions including their shares.                                             14-19
    
                                                Section C - Transmission Lines
    
    1 Executive summary of Target and Achievement of Transmission Lines during 2025-26                          20(1)
    
    2 List of Transmission Lines Commissioned in the month.                                                     20(2)
    
                                                       Section D - Substation
    
    1 Executive summary of Target and Achievement of Substations during 2025-26                                 21(1)
    
    2 Sub Stations (220 kV and above) commissioned/Ready for commissioning in the month.                        21(2)
    
                                               Section E - Electricity Generation                                 22
    
    1 Electricity Generation (MU) Targets and Achievements for 2025-26                                            23
                                                                                                                  24
                                              Section F - Power Supply Position                                   25
                                                                                                                  26
    1 Energy Power Supply Position (Provisional) for the month.                                                   27
    2 Peak Power Supply Position (Provisional) for the month.                                                     28
    3 Energy Power Supply Position (Revised) for Jul-2026 and during Apr-26 to Jul-26                             29
    4 Peak Power Supply Position (Revised) for Jul-2026 and during Apr-26 to Jul-26                               30
    5 Power Supply to Agricultural Sector during Jul-2026                                                         31
    6 Power Supply Position since 2003-04 (Energy Requirement / Availability)
    7 Graph for Energy Requirement, Availability(BU) & Shortages (2003-04 to 2024-25)                             32
    8 Power Supply Position since 2003-04 (Peak Demand / Peak Met)                                                33
    9 Graph for Peak Demand, Peak Demand Met(GW) & Shortages (2003-04 to 2024-25)                                 34
    
    ### statewise and national renewable energy stats.pdf
    Creator:         Adobe InDesign 20.5 (Windows)
    Producer:        iLovePDF
    Pages:           121
    Page size:       595.276 x 841.89 pts (A4)
    --- Extract preview ---
    RENEWABLE ENERGY STATISTICS
                        2024-25
    
                           Government of India
                Ministry of New & Renewable Energy
    
                             Statistics Division
    
                                               A
    i
    ii
    iii
    iv
    v
                        Contents
    
      Sl. No.                   CONTENTS                                                   PAGE NO.
    INSTALLED CAPACITY       Scope & Coverage                                                    1
                                                                                                 2
                                 Introduction                                                   3-8
                                  Highlights
                        ALL INDIA STATUS
    
    Chapter 1           Installed Capacity - RE and Non-RE sector                          10-13
                                                                                             10
               Table 1.1 Cumulative installed capacity since 2014-15
                                                                                           14-20
    Chapter 2 Installed Capacity - Wind, Solar, Small Hydro & Bioenergy (RES)
                                                  sector                                     14
    
               Table 2.1 Cumulative installed Capacity under RES since 2014-15
    
    ENERGY GENERATION
    
    Chapter 3           Energy Generation - RE and Non-RE sector                           21-23
    
               Table 3.1 Year-wise All India Energy Generation since 2014-15               21
    
    Chapter 4  Energy Generation � Wind, Solar, SHP & Bioenergy (RES) sector               24-27
    
               Table 4.1 Year-wise Energy Generation under RES since 2014-15               24
    
    INSTALLED CAPACITY & ENERGY GENERATION DURING -2024-25 and SDG-NIF
    
    Chapter 5   Monthly Installed Capacity and Electricity Generation during 2024-         28-30
    Chapter 6                                             25
                                                                                             29
               Table 5.1 Monthly Capacity Addition during 2024-25                            29
                                                                                             30
               Table 5.2 Monthly Sector Wise RE Capacity Addition during 2024-25             30
                                                                                           31-33
               Table 5.3 Monthly Electricity Generation during 2024-25                       31
    
               Table 5.4 Monthly Electricity Generation under RES during 2024-25             32
    
                                     Sustainable Development Goal-NIF
    
               Table 6.1 SDG � NIF Indicators 7.b.1/12. a.1- Installed renewable energy
                           generating capacity in the country (in watts per capita)
    
               Table 6.2 SDG Indicator 7.2.1- RE share in the total installed electricity
                           generation
    
                                             STATEWISE STATUS
    
    POTENTIAL AND INSTALLED CAPACITY
    
    Chapter 7    Estimated RE Potential and Installed Capacity in RE and Non-RE            35-38
                                                        sector
                                                                                             36
               Table 7.1 Estimated potential in RE sector                                  37-38
    
               Table 7.2 State wise Non-RE and RE Cumulative Installed Capacity as on
                           31.03.2018 and 31.03.2025
    
                                      vi
    Chapter 8                            Installed capacity in RE sector                  39-46
                                                                                          39-40
                Table 8.1 Region wise/State wise RE Cumulative Installed Capacity from
                          2017-18 to 2024-25                                                43
    
    
    ✓ • 1.96s

## Activity

    $ & { $p = Resolve-Path 'archive\india_states.geojson'; $g = Get-Content -Raw -LiteralPath $p | ConvertFrom-Json; $features = @($g.features); $types = $features | ForEach-Object { $_.geometry.type } | Group-Object | ForEach-Object { "$($_.Name)=$($_.Count)" }; $keys = $features[0].properties.PSObject.Properties.Name; $samples = $features | Select-Object -First 5 | ForEach-Object { ($_.properties.PSObject.Properties | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join '; ' }; [PSCustomObject]@{File=(Split-Path $p -Leaf); TopLevelType=$g.type; FeatureCount=$features.Count; GeometryTypes=($types -join ' | '); PropertyKeys=($keys -join ' | '); Samples=($samples -join ' || ')} | ConvertTo-Json -Compress }
    {"File":"india_states.geojson","TopLevelType":"FeatureCollection","FeatureCount":35,"GeometryTypes":"MultiPolygon=15 | Polygon=20","PropertyKeys":"ID_0 | ISO | NAME_0 | ID_1 | NAME_1 | NL_NAME_1 | VARNAME_1 | TYPE_1 | ENGTYPE_1 | filename | filename_1 | filename_2 | filename_3 | filename_4","Samples":"ID_0=105; ISO=IND; NAME_0=India; ID_1=1; NAME_1=Andaman and Nicobar; NL_NAME_1=; VARNAME_1=Andaman \u0026 Nicobar Islands|Andaman et Nicobar|Iihas de Andama e Nicobar|Inseln Andamanen und Nikobare; TYPE_1=Union Territor; ENGTYPE_1=Union Territory; filename=; filename_1=; filename_2=; filename_3=; filename_4= || ID_0=105; ISO=IND; NAME_0=India; ID_1=2; NAME_1=Andhra Pradesh; NL_NAME_1=; VARNAME_1=; TYPE_1=State; ENGTYPE_1=State; filename=; filename_1=; filename_2=; filename_3=; filename_4= || ID_0=105; ISO=IND; NAME_0=India; ID_1=3; NAME_1=Arunachal Pradesh; NL_NAME_1=; VARNAME_1=Agence de la Frontire du Nord-Est(French-obsolete)|North East Frontier Agency; TYPE_1=State; ENGTYPE_1=State; filename=; filename_1=; filename_2=; filename_3=; filename_4= || ID_0=105; ISO=IND; NAME_0=India; ID_1=4; NAME_1=Assam; NL_NAME_1=; VARNAME_1=; TYPE_1=State; ENGTYPE_1=State; filename=; filename_1=; filename_2=; filename_3=; filename_4= || ID_0=105; ISO=IND; NAME_0=India; ID_1=5; NAME_1=Bihar; NL_NAME_1=; VARNAME_1=; TYPE_1=State; ENGTYPE_1=State; filename=; filename_1=; filename_2=; filename_3=; filename_4="}
    ✓ • 2.23s

## Activity

    $ & { $r = @(Import-Csv -LiteralPath 'file_02.csv'); $dups = $r | Group-Object { "$($_.Date)|$($_.Region)" } | Where-Object Count -gt 1; $missByRegion = $r | Group-Object Region | ForEach-Object { [PSCustomObject]@{Region=$_.Name; Rows=$_.Count; NuclearActualBlank=@($_.Group | Where-Object { [string]::IsNullOrWhiteSpace($_.'Nuclear Generation Actual (in MU)') }).Count; NuclearEstimatedBlank=@($_.Group | Where-Object { [string]::IsNullOrWhiteSpace($_.'Nuclear Generation Estimated (in MU)') }).Count} }; [PSCustomObject]@{Rows=$r.Count; DateMin=(($r | ForEach-Object {[datetime]$_.Date} | Measure-Object -Minimum).Minimum.ToString('yyyy-MM-dd')); DateMax=(($r | ForEach-Object {[datetime]$_.Date} | Measure-Object -Maximum).Maximum.ToString('yyyy-MM-dd')); Regions=(($r.Region | Sort-Object -Unique) -join ' | '); DuplicateDateRegionGroups=$dups.Count; IndexDuplicates=(($r.index | Group-Object | Where-Object Count -gt 1).Count); MissingByRegion=$missByRegion} | ConvertTo-Json -Depth 4 }
    {
        "Rows":  4945,
        "DateMin":  "2017-09-01",
        "DateMax":  "2020-08-01",
        "Regions":  "Eastern | NorthEastern | Northern | Southern | Western",
        "DuplicateDateRegionGroups":  0,
        "IndexDuplicates":  310,
        "MissingByRegion":  [
                                {
                                    "Region":  "Northern",
                                    "Rows":  989,
                                    "NuclearActualBlank":  0,
                                    "NuclearEstimatedBlank":  0
                                },
                                {
                                    "Region":  "Western",
                                    "Rows":  989,
                                    "NuclearActualBlank":  0,
                                    "NuclearEstimatedBlank":  0
                                },
                                {
                                    "Region":  "Southern",
                                    "Rows":  989,
                                    "NuclearActualBlank":  0,
                                    "NuclearEstimatedBlank":  0
                                },
                                {
                                    "Region":  "Eastern",
                                    "Rows":  989,
                                    "NuclearActualBlank":  927,
                                    "NuclearEstimatedBlank":  927
                                },
                                {
                                    "Region":  "NorthEastern",
                                    "Rows":  989,
                                    "NuclearActualBlank":  927,
                                    "NuclearEstimatedBlank":  927
                                }
                            ]
    }
    ✓ • 6.18s

## Activity

    $ & { $r = @(Import-Csv -LiteralPath 'cea_installed_capacity_statewise_fuelwise_jul2026.csv'); $stateGroups = $r | Group-Object State_UT; $checks = foreach ($x in $r) { $thermal = [double]$x.Coal_MW + [double]$x.Lignite_MW + [double]$x.Gas_MW + [double]$x.Diesel_MW; $res = [double]$x.Hydro_MW + [double]$x.RES_MNRE_MW; $grand = [double]$x.Thermal_Total_MW + [double]$x.Nuclear_MW + [double]$x.Total_RES_incl_Hydro_MW; [PSCustomObject]@{ThermalDelta=[math]::Round([double]$x.Thermal_Total_MW-$thermal,4); RESDelta=[math]::Round([double]$x.Total_RES_incl_Hydro_MW-$res,4); GrandDelta=[math]::Round([double]$x.Grand_Total_MW-$grand,4)} }; [PSCustomObject]@{Rows=$r.Count; Regions=(($r.Region | Sort-Object -Unique) -join ' | '); Sectors=(($r.Sector | Sort-Object -Unique) -join ' | '); DistinctStateUT=$stateGroups.Count; RowsNamedAsRegion=@($r | Where-Object { $_.State_UT -match 'Region$' }).Count; StateUTWithMultipleRows=@($stateGroups | Where-Object Count -gt 1).Count; ThermalTotalMismatches=@($checks | Where-Object { [math]::Abs($_.ThermalDelta) -gt 0.01 }).Count; RESTotalMismatches=@($checks | Where-Object { [math]::Abs($_.RESDelta) -gt 0.01 }).Count; GrandTotalMismatches=@($checks | Where-Object { [math]::Abs($_.GrandDelta) -gt 0.01 }).Count; StateUTCounts=($stateGroups | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join ' | '} | ConvertTo-Json -Compress }
    {"Rows":177,"Regions":"Eastern Region | Islands | North Eastern Region | Northern Region | Southern Region | Western Region","Sectors":"Central | Grand Total | Private | State | Sub-Total","DistinctStateUT":15,"RowsNamedAsRegion":122,"StateUTWithMultipleRows":11,"ThermalTotalMismatches":0,"RESTotalMismatches":0,"GrandTotalMismatches":0,"StateUTCounts":"and Diu=4 | Eastern Region=26 | Eastern Region)=2 | Islands=12 | Ladakh=24 | North Eastern Region=30 | Northern Region=14 | Region)=6 | Southern Region=30 | Total (Eastern=3 | Total (North-=1 | Total (Northern=1 | Total (Southern=1 | Total (Western=1 | Western Region=22"}
    ✓ • 248ms

## Activity

    $ Get-Content -LiteralPath 'cea_installed_capacity_statewise_fuelwise_jul2026.csv' | Select-Object -Last 35
    North Eastern Region,North Eastern Region,Central,51.6,0.0,109.69,0.0,161.29,0.0,119.6,0.0,119.6,280.89
    North Eastern Region,North Eastern Region,Sub-Total,51.6,0.0,109.69,0.0,161.29,0.0,441.6,73.11,514.71,676.0
    North Eastern Region,North Eastern Region,State,0.0,0.0,105.0,0.0,105.0,0.0,0.0,0.0,0.0,105.0
    North Eastern Region,North Eastern Region,Private,0.0,0.0,0.0,0.0,0.0,0.0,0.0,53.81,53.81,53.81
    North Eastern Region,North Eastern Region,Central,106.0,0.0,381.94,0.0,487.94,0.0,92.57,5.25,97.82,585.76
    North Eastern Region,North Eastern Region,Sub-Total,106.0,0.0,486.94,0.0,592.94,0.0,92.57,59.05,151.62,744.56
    North Eastern Region,North Eastern Region,State,0.0,0.0,0.0,36.0,36.0,0.0,0.0,0.72,0.72,36.72
    North Eastern Region,North Eastern Region,Private,0.0,0.0,0.0,0.0,0.0,0.0,0.0,22.3,22.3,22.3
    North Eastern Region,North Eastern Region,Central,47.1,0.0,81.58,0.0,128.68,0.0,108.72,0.0,108.72,237.4
    North Eastern Region,North Eastern Region,Sub-Total,47.1,0.0,81.58,36.0,164.68,0.0,108.72,23.01,131.73,296.41
    North Eastern Region,North Eastern Region,State,0.0,0.0,0.0,0.0,0.0,0.0,0.0,35.07,35.07,35.07
    North Eastern Region,North Eastern Region,Private,0.0,0.0,0.0,0.0,0.0,0.0,0.0,3.68,3.68,3.68
    North Eastern Region,North Eastern Region,Central,32.1,0.0,73.93,0.0,106.03,0.0,80.69,0.0,80.69,186.72
    North Eastern Region,North Eastern Region,Sub-Total,32.1,0.0,73.93,0.0,106.03,0.0,80.69,38.75,119.44,225.47
    North Eastern Region,North Eastern Region,State,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
    North Eastern Region,North Eastern Region,Private,0.0,0.0,0.0,0.0,0.0,0.0,0.0,79.89,79.89,79.89
    North Eastern Region,North Eastern Region,Central,31.05,0.0,60.46,0.0,91.51,0.0,111.74,0.0,111.74,203.25
    North Eastern Region,North Eastern Region,Sub-Total,31.05,0.0,60.46,0.0,91.51,0.0,111.74,79.89,191.63,283.14
    North Eastern Region,North Eastern Region,Central,112.6,0.0,63.62,0.0,176.22,0.0,289.4,0.0,289.4,465.62
    North Eastern Region,North Eastern Region,State,0.0,0.0,411.36,36.0,447.36,0.0,422.0,239.19,661.19,1108.54
    North Eastern Region,Total (North-,Private,0.0,0.0,0.0,0.0,0.0,0.0,0.0,866.37,866.37,866.37
    North Eastern Region,Eastern Region),Central,1113.02,0.0,1253.6,0.0,2366.62,0.0,2050.01,102.99,2153.0,4519.62
    North Eastern Region,Eastern Region),Grand Total,1113.02,0.0,1664.96,36.0,2813.97,0.0,2472.01,1208.55,3680.56,6494.53
    Islands,Islands,State,0.0,0.0,0.0,57.52,57.52,0.0,0.0,5.25,5.25,62.77
    Islands,Islands,Private,0.0,0.0,0.0,35.19,35.19,0.0,0.0,27.82,27.82,63.01
    Islands,Islands,Central,0.0,0.0,0.0,0.0,0.0,0.0,0.0,5.0,5.0,5.0
    Islands,Islands,Sub-Total,0.0,0.0,0.0,92.71,92.71,0.0,0.0,38.07,38.07,130.78
    Islands,Islands,State,0.0,0.0,0.0,26.83,26.83,0.0,0.0,0.0,0.0,26.83
    Islands,Islands,Private,0.0,0.0,0.0,0.0,0.0,0.0,0.0,9.27,9.27,9.27
    Islands,Islands,Central,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
    Islands,Islands,Sub-Total,0.0,0.0,0.0,26.83,26.83,0.0,0.0,9.27,9.27,36.1
    Islands,Islands,State,0.0,0.0,0.0,84.35,84.35,0.0,0.0,5.25,5.25,89.6
    Islands,Islands,Private,0.0,0.0,0.0,35.19,35.19,0.0,0.0,37.09,37.09,72.28
    Islands,Islands,Central,0.0,0.0,0.0,0.0,0.0,0.0,0.0,5.0,5.0,5.0
    Islands,Islands,Grand Total,0.0,0.0,0.0,119.54,119.54,0.0,0.0,47.34,47.34,166.88
    ✓ • 93ms

## Activity

    $ Get-Content -LiteralPath 'cea_installed_capacity_statewise_fuelwise_jul2026.csv' | Select-Object -First 45
    Region,State_UT,Sector,Coal_MW,Lignite_MW,Gas_MW,Diesel_MW,Thermal_Total_MW,Nuclear_MW,Hydro_MW,RES_MNRE_MW,Total_RES_incl_Hydro_MW,Grand_Total_MW
    Northern Region,Northern Region,State,0.0,0.0,1800.4,0.0,1800.4,0.0,0.0,0.0,0.0,1800.4
    Northern Region,Northern Region,Private,878.22,0.0,0.0,0.0,878.22,0.0,0.0,546.1,546.1,1424.32
    Northern Region,Northern Region,Central,2786.14,0.0,207.01,0.0,2993.16,153.38,1178.01,0.37,1178.38,4324.92
    Northern Region,Northern Region,Sub-Total,3664.36,0.0,2007.41,0.0,5671.78,153.38,1178.01,546.47,1724.48,7549.64
    Northern Region,Northern Region,State,2510.0,0.0,150.0,0.0,2660.0,0.0,200.0,142.6,342.6,3002.6
    Northern Region,Northern Region,Private,4561.78,0.0,0.0,0.0,4561.78,0.0,539.0,3113.24,3652.24,8214.02
    Northern Region,Northern Region,Central,1610.81,0.0,431.59,0.0,2042.4,123.04,1702.12,5.0,1707.12,3872.56
    Northern Region,Northern Region,Sub-Total,8682.59,0.0,581.59,0.0,9264.18,123.04,2441.12,3260.84,5701.96,15089.18
    Northern Region,Northern Region,State,0.0,0.0,0.0,0.0,0.0,0.0,905.59,262.91,1168.5,1168.5
    Northern Region,Northern Region,Private,0.0,0.0,0.0,0.0,0.0,0.0,1609.4,1145.04,2754.44,2754.44
    Northern Region,Northern Region,Central,144.67,0.0,0.0,0.0,144.67,42.22,1432.02,1.0,1433.02,1619.92
    Northern Region,Northern Region,Sub-Total,144.67,0.0,0.0,0.0,144.67,42.22,3947.01,1408.95,5355.96,5542.86
    Northern Region,Northern Region,State,0.0,0.0,0.0,0.0,0.0,0.0,1230.0,142.97,1372.97,1372.97
    Northern Region,Northern Region,Private,0.0,0.0,0.0,0.0,0.0,0.0,0.0,284.43,284.43,284.43
    Northern Region,Ladakh,Central,577.1,0.0,129.07,0.0,706.18,95.13,1115.88,0.0,1115.88,1917.19
    Northern Region,Ladakh,Sub-Total,577.1,0.0,129.07,0.0,706.18,95.13,2345.88,427.4,2773.28,3574.58
    Northern Region,Ladakh,State,2300.0,0.0,150.0,0.0,2450.0,0.0,1243.4,135.3,1378.7,3828.7
    Northern Region,Ladakh,Private,4474.0,0.0,0.0,0.0,4474.0,0.0,288.0,2226.58,2514.58,6988.58
    Northern Region,Ladakh,Central,1476.0,0.0,0.0,0.0,1476.0,229.09,2296.04,0.0,2296.04,4001.12
    Northern Region,Ladakh,Sub-Total,8250.0,0.0,150.0,0.0,8400.0,229.09,3827.44,2361.88,6189.32,14818.41
    Northern Region,Ladakh,State,7580.0,250.0,603.5,0.0,8433.5,0.0,434.5,184.2,618.7,9052.2
    Northern Region,Ladakh,Private,3301.0,1080.0,0.0,0.0,4381.0,0.0,104.0,44287.82,44391.82,48772.82
    Northern Region,Ladakh,Central,1491.64,250.0,171.13,0.0,1912.77,806.74,1665.17,5450.82,7115.99,9835.5
    Northern Region,Ladakh,Sub-Total,12372.64,1580.0,774.63,0.0,14727.27,806.74,2203.67,49922.84,52126.51,67660.52
    Northern Region,Ladakh,State,9115.0,0.0,0.0,0.0,9115.0,0.0,724.1,21.13,745.23,9860.23
    Northern Region,Ladakh,Private,8814.33,0.0,0.0,0.0,8814.33,0.0,842.4,7816.73,8659.13,17473.46
    Northern Region,Ladakh,Central,8238.19,0.0,1029.51,0.0,9267.7,370.45,2108.52,567.06,2675.58,12313.73
    Northern Region,Ladakh,Sub-Total,26167.52,0.0,1029.51,0.0,27197.03,370.45,3675.02,8404.92,12079.94,39647.42
    Northern Region,Ladakh,State,0.0,0.0,0.0,0.0,0.0,0.0,1372.15,3.1,1375.25,1375.25
    Northern Region,Ladakh,Private,99.0,0.0,664.0,0.0,763.0,0.0,248.2,1281.85,1530.05,2293.05
    Northern Region,Ladakh,Central,554.63,0.0,69.66,0.0,624.29,47.51,743.5,2.24,745.74,1417.53
    Northern Region,Ladakh,Sub-Total,653.63,0.0,733.66,0.0,1387.29,47.51,2363.85,1287.18,3651.03,5085.83
    Northern Region,Ladakh,State,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
    Northern Region,Ladakh,Private,0.0,0.0,0.0,0.0,0.0,0.0,0.0,78.85,78.85,78.85
    Northern Region,Ladakh,Central,44.86,0.0,15.03,0.0,59.88,10.41,106.21,0.0,106.21,176.5
    Northern Region,Ladakh,Sub-Total,44.86,0.0,15.03,0.0,59.88,10.41,106.21,78.85,185.06,255.35
    Northern Region,Ladakh,Central,1703.67,0.0,291.05,0.0,1994.72,342.03,871.45,0.0,871.45,3208.21
    Northern Region,Ladakh,State,21505.0,250.0,2703.9,0.0,24458.9,0.0,6109.74,892.21,7001.95,31460.85
    Northern Region,Total (Northern,Private,22128.33,1080.0,664.0,0.0,23872.33,0.0,3631.0,60780.64,64411.64,88283.97
    Northern Region,Region),Central,18627.71,250.0,2344.06,0.0,21221.77,2220.0,13218.93,6026.49,19245.42,42687.19
    Northern Region,Region),Grand Total,62261.04,1580.0,5711.96,0.0,69553.0,2220.0,22959.67,67699.34,90659.01,162432.01
    Western Region,Western Region,State,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
    Western Region,Western Region,Private,0.0,0.0,0.0,0.0,0.0,0.0,0.0,96.7,96.7,96.7
    Western Region,Western Region,Central,492.27,0.0,19.67,0.0,511.94,41.68,6.0,1.0,7.0,560.62
    ✓ • 93ms

## Activity

    $ & { function N([string]$s) { return (($s.Trim().ToLower() -replace '&','and' -replace '[^a-z0-9]','')) }; $geo = (Get-Content -Raw -LiteralPath 'archive\india_states.geojson' | ConvertFrom-Json).features | ForEach-Object { N $_.properties.NAME_1 } | Sort-Object -Unique; $specs = @(@('area-wise-waterbodies-india-statewise.csv','State'), @('mnre_bio_and_solar_breakdown_2025.csv','State_UT'), @('mnre_re_cumulative_capacity_timeseries_2018_2025.csv','State_UT'), @('mnre_re_estimated_potential_by_state.csv','State_UT'), @('mnre_re_generation_by_source_statewise_2024_2025.csv','State_UT'), @('mnre_re_installed_capacity_by_source_2025.csv','State_UT'), @('mnre_re_share_in_total_capacity_2025.csv','State_UT'), @('State_Region_corrected.csv','State / Union territory (UT)'), @('state-ground-water-level-information.csv','State'), @('statewise land cost.csv','State')); $out = foreach($spec in $specs) { $rows = @(Import-Csv -LiteralPath $spec[0]); $vals = @($rows | ForEach-Object { [string]$_.PSObject.Properties[$spec[1]].Value } | Sort-Object -Unique); $unmatched = @($vals | Where-Object { (N $_) -notin $geo }); [PSCustomObject]@{File=$spec[0]; KeyColumn=$spec[1]; UniqueKeys=$vals.Count; NotExactGeoNormalized=($unmatched -join ' | ')} }; $out | ConvertTo-Json -Depth 3 }
    [
        {
            "File":  "area-wise-waterbodies-india-statewise.csv",
            "KeyColumn":  "State",
            "UniqueKeys":  37,
            "NotExactGeoNormalized":  "Dadara \u0026 Nagar Havelli | Ladakh | Odisha | Pondicherry | Telangana | Uttarakhand"
        },
        {
            "File":  "mnre_bio_and_solar_breakdown_2025.csv",
            "KeyColumn":  "State_UT",
            "UniqueKeys":  41,
            "NotExactGeoNormalized":  "Andaman \u0026 | Dadra \u0026 Nagar | Haveli / | Ladakh | Nicobar Islands | Odisha | Others | Pondicherry | Telangana | Total (MW) | Uttarakhand"
        },
        {
            "File":  "mnre_re_cumulative_capacity_timeseries_2018_2025.csv",
            "KeyColumn":  "State_UT",
            "UniqueKeys":  38,
            "NotExactGeoNormalized":  "Dadar \u0026 Nagar | Grand Total | Ladakh | Odisha | Others | Pondicherry | Telangana | Total | Uttarakhand"
        },
        {
            "File":  "mnre_re_estimated_potential_by_state.csv",
            "KeyColumn":  "State_UT",
            "UniqueKeys":  38,
            "NotExactGeoNormalized":  "Dadra and Nagar Haveli and Daman and Diu | Ladakh | Others | Pondicherry | Telangana | Total | Uttarakhand"
        },
        {
            "File":  "mnre_re_generation_by_source_statewise_2024_2025.csv",
            "KeyColumn":  "State_UT",
            "UniqueKeys":  38,
            "NotExactGeoNormalized":  "Dadar \u0026 Nagar | Haveli/Daman \u0026 Diu | Ladakh | Odisha | Pondicherry | Telangana | Total | Uttarakhand"
        },
        {
            "File":  "mnre_re_installed_capacity_by_source_2025.csv",
            "KeyColumn":  "State_UT",
            "UniqueKeys":  41,
            "NotExactGeoNormalized":  "\"Dadar \u0026 Nagar | Haveli/ | Islands | Ladakh | Odisha | Others | Pondicherry | Telangana | Total | Uttarakhand"
        },
        {
            "File":  "mnre_re_share_in_total_capacity_2025.csv",
            "KeyColumn":  "State_UT",
            "UniqueKeys":  39,
            "NotExactGeoNormalized":  "Dadar \u0026 Nagar | Haveli/Daman \u0026 Diu | Ladakh | Odisha | Others | Pondicherry | Telangana | Total | Uttarakhand"
        },
        {
            "File":  "State_Region_corrected.csv",
            "KeyColumn":  "State / Union territory (UT)",
            "UniqueKeys":  34,
            "NotExactGeoNormalized":  "Dadra and Nagar Haveli and Daman and Diu | Ladakh | Odisha | Telangana | Uttarakhand"
        },
        {
            "File":  "state-ground-water-level-information.csv",
            "KeyColumn":  "State",
            "UniqueKeys":  29,
            "NotExactGeoNormalized":  "Odisha | Telangana | Uttarakhand"
        },
        {
            "File":  "statewise land cost.csv",
            "KeyColumn":  "State",
            "UniqueKeys":  12,
            "NotExactGeoNormalized":  "Telangana"
        }
    ]
    ✓ • 2.25s

## Activity

    $ & { $files = 'mnre_bio_and_solar_breakdown_2025.csv','mnre_re_installed_capacity_by_source_2025.csv'; foreach($f in $files) { "### $f"; Select-String -LiteralPath $f -Pattern 'Andaman|Dadar|Haveli|Total|Others' | ForEach-Object { $_.Line } } }
    ### mnre_bio_and_solar_breakdown_2025.csv
    Andaman &,0.0,0.0,0.0,0.0,25.05,4.59,0.0,0.27
    Haveli /,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
    Others,0.0,0.0,0.0,0.0,0.0,0.0,0.0,45.01
    Total (MW),9821.32,921.79,309.34,530.87,81011.66,0.0,0.0,742.89
    ### mnre_re_installed_capacity_by_source_2025.csv
    State_UT,Small_Hydro_MW,Wind_Power_MW,Bio_Power_MW,Solar_Power_MW,Large_Hydro_MW,Total_RES_MW
    Andaman & Nicobar,5.25,0.0,0.0,29.91,0.0,35.16
    """Dadar & Nagar",0.0,0.0,3.75,48.12,0.0,51.87
    Haveli/,0.0,0.0,0.0,0.0,0.0,0.0
    Others,0.0,4.3,0.0,45.01,0.0,49.31
    Total,5100.55,50037.82,0.0,5646.49,0.0,20096.35
    ✓ • 122ms

## Activity

    $ Get-Content -LiteralPath 'mnre_bio_and_solar_breakdown_2025.csv' | Select-Object -Skip 28 -First 14; Get-Content -LiteralPath 'mnre_re_installed_capacity_by_source_2025.csv' | Select-Object -Skip 24 -First 14
    Uttar Pradesh,1985.5,165.26,0.0,158.38,2717.45,321.9,0.0,324.72
    Uttarakhand,72.72,60.0,0.0,15.81,298.4,273.71,0.0,20.96
    West Bengal,300.0,43.52,0.0,8.34,240.35,67.13,0.0,13.14
    Andaman &,0.0,0.0,0.0,0.0,25.05,4.59,0.0,0.27
    Nicobar Islands,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
    Chandigarh,0.0,0.0,0.0,0.0,6.34,71.7,0.0,0.81
    Dadra & Nagar,3.75,0.0,0.0,0.0,14.3,33.82,0.0,0.0
    Haveli /,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
    Daman & Diu,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
    Delhi,0.0,0.0,84.0,0.0,9.84,302.1,0.0,1.46
    Lakshadweep,0.0,0.0,0.0,0.0,2.45,0.0,0.0,2.52
    Pondicherry,0.0,0.0,0.0,0.0,1.03,53.3,0.0,0.18
    Others,0.0,0.0,0.0,0.0,0.0,0.0,0.0,45.01
    Total (MW),9821.32,921.79,309.34,530.87,81011.66,0.0,0.0,742.89
    Sikkim,55.11,0.0,0.0,7.56,2282.0,2344.67
    Tamil Nadu,123.05,11739.91,1046.62,10153.58,2178.2,25241.36
    Telangana,90.87,128.1,221.67,4842.1,2405.6,7688.34
    Tripura,16.01,0.0,0.0,21.24,0.0,37.25
    Uttar Pradesh,49.1,0.0,2309.14,3364.07,501.6,6223.91
    Uttarakhand,233.82,0.0,148.53,593.07,4035.35,5010.77
    West Bengal,98.5,0.0,351.86,320.62,1341.2,2112.18
    Andaman & Nicobar,5.25,0.0,0.0,29.91,0.0,35.16
    Islands,0.0,0.0,0.0,0.0,0.0,0.0
    Chandigarh,0.0,0.0,0.0,78.85,0.0,78.85
    """Dadar & Nagar",0.0,0.0,3.75,48.12,0.0,51.87
    Haveli/,0.0,0.0,0.0,0.0,0.0,0.0
    "Daman & Diu""",0.0,0.0,0.0,0.0,0.0,0.0
    Delhi,0.0,0.0,84.0,313.4,0.0,397.4
    ✓ • 176ms

## Activity

    $ & { $files = 'mnre_re_cumulative_capacity_timeseries_2018_2025.csv','mnre_re_estimated_potential_by_state.csv','mnre_re_generation_by_source_statewise_2024_2025.csv','mnre_re_share_in_total_capacity_2025.csv'; foreach($f in $files) { "### $f"; Select-String -LiteralPath $f -Pattern 'Andaman|Dadar|Dadra|Haveli|Total|Others|Islands' | ForEach-Object { $_.Line } } }
    ### mnre_re_cumulative_capacity_timeseries_2018_2025.csv
    Northern Region,Total,32567.47,34019.28,36286.95,38357.09,46646.97,52710.14,58267.19,67530.82
    Eastern Region,Total,1662.72,1795.35,2122.39,2429.56,2500.55,2566.81,2601.84,2656.41
    Western Region,Dadar & Nagar,16.07,19.93,25.32,46.01,46.18,46.47,46.47,51.87
    Western Region,Total,28106.36,30859.07,33687.29,37054.55,41041.46,46863.6,56100.54,68560.95
    Eastern Region,Total,7013.75,7391.28,7454.03,7561.67,7767.81,7836.09,8032.17,8424.17
    Southern Region,Total,46546.9,50696.95,54354.46,56560.39,58601.85,61984.07,65521.54,72874.68
    Southern Region,Others,47.66,49.31,49.31,49.31,49.31,49.31,49.31,49.31
    Southern Region,Grand Total,115944.9,124811.2,133954.5,142012.6,156607.9,172010.0,190572.7,220096.35
    ### mnre_re_estimated_potential_by_state.csv
    State_UT,Wind_Potential_MW,Small_Hydro_Potential_MW,Biomass_Potential_MW,Bagasse_Cogen_Potential_MW,Solar_Ground_Potential_MW,Large_Hydro_Potential_MW,Total_Estimated_RE_Potential_MW
    Andaman & Nicobar,1245.0,7.27,18.13,0.0,594.22,0.0,1864.62
    Dadra and Nagar Haveli and Daman and Diu,0.0,0.0,0.0,0.0,498.31,0.0,498.31
    Others,0.0,0.0,0.0,284.4,0.0,0.0,284.4
    Total,1163856.0,21133.62,28446.91,13818.4,3343378.39,133410.03,4704043.35
    ### mnre_re_generation_by_source_statewise_2024_2025.csv
    State_UT,Small_Hydro_MU,Wind_Power_MU,Bio_Power_MU,Solar_Power_MU,Large_Hydro_MU,Total_RE_Generation_MU
    Andaman & Nicobar,14.4,0.0,0.0,24.59,0.0,39.0
    Dadar & Nagar,0.0,0.0,12.76,15.87,0.0,28.63
    Haveli/Daman & Diu,0.0,0.0,0.0,0.0,0.0,0.0
    Total,11568.03,83347.19,15943.73,144150.21,0.0,3643.17
    ### mnre_re_share_in_total_capacity_2025.csv
    State_UT,Non_RE_Capacity_MW,RES_excl_Hydro_MW,Large_Hydro_MW,Total_RE_incl_Hydro_MW,Grand_Total_Capacity_MW,RES_Share_Percent,RE_Share_Percent
    Andaman & Nicobar,92.71,35.16,0.0,35.16,127.87,27.5,27.5
    Dadar & Nagar,0.0,51.87,0.0,51.87,51.87,100.0,100.0
    Haveli/Daman & Diu,0.0,0.0,0.0,0.0,0.0,0.0,0.0
    Others,0.0,49.31,0.0,49.31,49.31,0.0,0.0
    Total,255115.46,172368.18,47728.16,220096.3,0.0,0.0,46.32
    ✓ • 176ms

## Activity

    $ & { function Data([string]$f) { @(Import-Csv -LiteralPath $f | Where-Object { $_.State_UT -notmatch 'Total|Others|Haveli|Islands' }) }; $cap = Data 'mnre_re_installed_capacity_by_source_2025.csv'; $capBad = @($cap | Where-Object { [math]::Abs(([double]$_.Total_RES_MW)-([double]$_.Small_Hydro_MW+[double]$_.Wind_Power_MW+[double]$_.Bio_Power_MW+[double]$_.Solar_Power_MW+[double]$_.Large_Hydro_MW)) -gt 0.02 }); $gen = Data 'mnre_re_generation_by_source_statewise_2024_2025.csv'; $genBad = @($gen | Where-Object { [math]::Abs(([double]$_.Total_RE_Generation_MU)-([double]$_.Small_Hydro_MU+[double]$_.Wind_Power_MU+[double]$_.Bio_Power_MU+[double]$_.Solar_Power_MU+[double]$_.Large_Hydro_MU)) -gt 0.02 }); $pot = Data 'mnre_re_estimated_potential_by_state.csv'; $potBad = @($pot | Where-Object { [math]::Abs(([double]$_.Total_Estimated_RE_Potential_MW)-([double]$_.Wind_Potential_MW+[double]$_.Small_Hydro_Potential_MW+[double]$_.Biomass_Potential_MW+[double]$_.Bagasse_Cogen_Potential_MW+[double]$_.Solar_Ground_Potential_MW+[double]$_.Large_Hydro_Potential_MW)) -gt 0.05 }); $share = Data 'mnre_re_share_in_total_capacity_2025.csv'; $shareBad = @($share | Where-Object { [math]::Abs(([double]$_.Grand_Total_Capacity_MW)-([double]$_.Non_RE_Capacity_MW+[double]$_.Total_RE_incl_Hydro_MW)) -gt 0.02 }); [PSCustomObject]@{InstalledCapacity={Rows=$cap.Count; Mismatches=$capBad.Count; Examples=($capBad | Select-Object -First 5 State_UT,Total_RES_MW | ConvertTo-Json -Compress)}; Generation={Rows=$gen.Count; Mismatches=$genBad.Count; Examples=($genBad | Select-Object -First 5 State_UT,Total_RE_Generation_MU | ConvertTo-Json -Compress)}; Potential={Rows=$pot.Count; Mismatches=$potBad.Count; Examples=($potBad | Select-Object -First 5 State_UT,Total_Estimated_RE_Potential_MW | ConvertTo-Json -Compress)}; Share={Rows=$share.Count; Mismatches=$shareBad.Count; Examples=($shareBad | Select-Object -First 5 State_UT,Grand_Total_Capacity_MW | ConvertTo-Json -Compress)}} | ConvertTo-Json -Depth 5 }
    At line:2 char:148
    + ... _UT -notmatch 'Total|Others|Haveli|Islands' }) }; $cap = Data 'mnre_r ...
    +                                                                  ~
    The Data section is missing its statement block.
    At line:2 char:424
    + ... Power_MW+[double]$_.Large_Hydro_MW)) -gt 0.02 }); $gen = Data 'mnre_r ...
    +                                                                  ~
    The Data section is missing its statement block.
    At line:2 char:717
    + ... Power_MU+[double]$_.Large_Hydro_MU)) -gt 0.02 }); $pot = Data 'mnre_r ...
    +                                                                  ~
    The Data section is missing its statement block.
    At line:2 char:1090
    + ... uble]$_.Large_Hydro_Potential_MW)) -gt 0.05 }); $share = Data 'mnre_r ...
    +                                                                  ~
    The Data section is missing its statement block.
        + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException
        + FullyQualifiedErrorId : MissingStatementBlockForDataSection
    
    ✗ (1) • 180ms

## Activity

    $ & { function GetRows([string]$f) { @(Import-Csv -LiteralPath $f | Where-Object { $_.State_UT -notmatch 'Total|Others|Haveli|Islands' }) }; $cap = GetRows 'mnre_re_installed_capacity_by_source_2025.csv'; $capBad = @($cap | Where-Object { [math]::Abs(([double]$_.Total_RES_MW)-([double]$_.Small_Hydro_MW+[double]$_.Wind_Power_MW+[double]$_.Bio_Power_MW+[double]$_.Solar_Power_MW+[double]$_.Large_Hydro_MW)) -gt 0.02 }); $gen = GetRows 'mnre_re_generation_by_source_statewise_2024_2025.csv'; $genBad = @($gen | Where-Object { [math]::Abs(([double]$_.Total_RE_Generation_MU)-([double]$_.Small_Hydro_MU+[double]$_.Wind_Power_MU+[double]$_.Bio_Power_MU+[double]$_.Solar_Power_MU+[double]$_.Large_Hydro_MU)) -gt 0.02 }); $pot = GetRows 'mnre_re_estimated_potential_by_state.csv'; $potBad = @($pot | Where-Object { [math]::Abs(([double]$_.Total_Estimated_RE_Potential_MW)-([double]$_.Wind_Potential_MW+[double]$_.Small_Hydro_Potential_MW+[double]$_.Biomass_Potential_MW+[double]$_.Bagasse_Cogen_Potential_MW+[double]$_.Solar_Ground_Potential_MW+[double]$_.Large_Hydro_Potential_MW)) -gt 0.05 }); $share = GetRows 'mnre_re_share_in_total_capacity_2025.csv'; $shareBad = @($share | Where-Object { [math]::Abs(([double]$_.Grand_Total_Capacity_MW)-([double]$_.Non_RE_Capacity_MW+[double]$_.Total_RE_incl_Hydro_MW)) -gt 0.02 }); [PSCustomObject]@{InstalledCapacity=@{Rows=$cap.Count; Mismatches=$capBad.Count; Examples=@($capBad | Select-Object -First 5 State_UT,Total_RES_MW)}; Generation=@{Rows=$gen.Count; Mismatches=$genBad.Count; Examples=@($genBad | Select-Object -First 5 State_UT,Total_RE_Generation_MU)}; Potential=@{Rows=$pot.Count; Mismatches=$potBad.Count; Examples=@($potBad | Select-Object -First 5 State_UT,Total_Estimated_RE_Potential_MW)}; Share=@{Rows=$share.Count; Mismatches=$shareBad.Count; Examples=@($shareBad | Select-Object -First 5 State_UT,Grand_Total_Capacity_MW)}} | ConvertTo-Json -Depth 6 }
    {
        "InstalledCapacity":  {
                                  "Examples":  [
    
                                               ],
                                  "Rows":  37,
                                  "Mismatches":  0
                              },
        "Generation":  {
                           "Examples":  [
                                            {
                                                "State_UT":  "Andhra Pradesh",
                                                "Total_RE_Generation_MU":  "9205.31"
                                            },
                                            {
                                                "State_UT":  "Gujarat",
                                                "Total_RE_Generation_MU":  "2002.5"
                                            },
                                            {
                                                "State_UT":  "Himachal Pradesh",
                                                "Total_RE_Generation_MU":  "2534.43"
                                            },
                                            {
                                                "State_UT":  "Jammu \u0026 Kashmir",
                                                "Total_RE_Generation_MU":  "5595.82"
                                            },
                                            {
                                                "State_UT":  "Karnataka",
                                                "Total_RE_Generation_MU":  "8141.85"
                                            }
                                        ],
                           "Rows":  36,
                           "Mismatches":  11
                       },
        "Potential":  {
                          "Examples":  [
    
                                       ],
                          "Rows":  35,
                          "Mismatches":  0
                      },
        "Share":  {
                      "Examples":  [
                                       {
                                           "State_UT":  "Delhi",
                                           "Grand_Total_Capacity_MW":  "2605.8"
                                       },
                                       {
                                           "State_UT":  "Lakshadweep",
                                           "Grand_Total_Capacity_MW":  "31.8"
                                       },
                                       {
                                           "State_UT":  "Pondicherry",
                                           "Grand_Total_Capacity_MW":  "87.01"
                                       }
                                   ],
                      "Rows":  36,
                      "Mismatches":  3
                  }
    }
    ✓ • 299ms

## Activity

    $ & { $r = @(Import-Csv -LiteralPath 'mnre_re_generation_by_source_statewise_2024_2025.csv' | Where-Object { $_.State_UT -notmatch 'Total|Others|Haveli|Islands' }); $r | ForEach-Object { $sum = [double]$_.Small_Hydro_MU+[double]$_.Wind_Power_MU+[double]$_.Bio_Power_MU+[double]$_.Solar_Power_MU+[double]$_.Large_Hydro_MU; $d=[math]::Round(([double]$_.Total_RE_Generation_MU)-$sum,2); if([math]::Abs($d) -gt .02){[PSCustomObject]@{State=$_.State_UT; Reported=$_.Total_RE_Generation_MU; ComponentSum=$sum; Delta=$d}} } | Format-Table -AutoSize; ''; $s = @(Import-Csv -LiteralPath 'mnre_re_share_in_total_capacity_2025.csv' | Where-Object { $_.State_UT -in 'Delhi','Lakshadweep','Pondicherry' }); $s | Format-Table State_UT,Non_RE_Capacity_MW,RES_excl_Hydro_MW,Large_Hydro_MW,Total_RE_incl_Hydro_MW,Grand_Total_Capacity_MW,RES_Share_Percent,RE_Share_Percent -AutoSize }
    
    State            Reported ComponentSum     Delta
    -----            -------- ------------     -----
    Andhra Pradesh   9205.31      15902.23  -6696.92
    Gujarat          2002.5       45973.98 -43971.48
    Himachal Pradesh 2534.43       3148.14   -613.71
    Jammu & Kashmir  5595.82        395.17   5200.65
    Karnataka        8141.85      34085.85    -25944
    Madhya Pradesh   174.05       12567.32 -12393.27
    Maharashtra      5226.43      19591.19 -14364.76
    Rajasthan        7353.68      56447.88  -49094.2
    Tamil Nadu       8410.18      33807.45 -25397.27
    Telangana        2912.48       7641.68   -4729.2
    Uttarakhand      6117.54        933.72   5183.82
    
    
    
    
    State_UT    Non_RE_Capacity_MW RES_excl_Hydro_MW Large_Hydro_MW Total_RE_incl_Hydro_MW Grand_Total_Capacity_MW RES_Shar
                                                                                                                   e_Percen
                                                                                                                   t
    --------    ------------------ ----------------- -------------- ---------------------- ----------------------- --------
    Delhi       2208.4             397.4             0.0            0.0                    2605.8                  15.25
    Lakshadweep 26.83              4.97              0.0            0.0                    31.8                    15.63
    Pondicherry 32.5               54.51             0.0            0.0                    87.01                   62.65
    
    
    ✓ • 184ms

## Activity

    $ Select-String -LiteralPath 'mnre_re_generation_by_source_statewise_2024_2025.csv' -Pattern '^Andhra Pradesh|^Gujarat|^Jammu|^Karnataka|^Rajasthan|^Total' | ForEach-Object { $_.Line }
    Andhra Pradesh,294.36,7235.04,379.35,7993.48,0.0,9205.31
    Gujarat,205.98,25440.9,107.62,20219.48,0.0,2002.5
    Jammu & Kashmir,395.17,0.0,0.0,0.0,0.0,5595.82
    Karnataka,2259.49,13620.33,2506.4,15699.63,0.0,8141.85
    Rajasthan,4.15,6941.26,400.85,49101.62,0.0,7353.68
    Total,11568.03,83347.19,15943.73,144150.21,0.0,3643.17
    ✓ • 181ms

## Activity

    $ & { $r = @(Import-Csv -LiteralPath 'Substation_Details_1789031375809.csv'); $cap = @($r | Where-Object { $_.'Capacity (MW/MVA)' -match '^\s*\d+(\.\d+)?\s*$' } | ForEach-Object { [double]$_.'Capacity (MW/MVA)' }); $enc = @($r | Where-Object { $_.'Voltage Ratio (kV/kV)' -match 'Â' }).Count; [PSCustomObject]@{Rows=$r.Count; CompletelyBlankRows=@($r | Where-Object { -not $_.Name -and -not $_.Sector -and -not $_.'Capacity (MW/MVA)' }).Count; CapacityNumericRows=$cap.Count; CapacityMin=($cap | Measure-Object -Minimum).Minimum; CapacityMax=($cap | Measure-Object -Maximum).Maximum; SectorCounts=($r | Group-Object Sector | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join ' | '; AgencyTop10=($r | Group-Object 'Executive Agency' | Sort-Object Count -Descending | Select-Object -First 10 | ForEach-Object { "$($_.Name)=$($_.Count)" }) -join ' | '; FYRange=(($r | Where-Object { $_.'Year Of Completion (FY)' } | Select-Object -ExpandProperty 'Year Of Completion (FY)' | Sort-Object -Unique) -join ' | '); MojibakeVoltageRows=$enc} | ConvertTo-Json -Compress; ''; $r | Where-Object { -not $_.Name -or -not $_.'Capacity (MW/MVA)' } | Select-Object -First 8 Name,Sector,'Voltage Ratio (kV/kV)','Capacity (MW/MVA)','Month Of Completion','Year Of Completion (FY)' | Format-Table -AutoSize }
    {"Rows":2851,"CompletelyBlankRows":2,"CapacityNumericRows":2846,"CapacityMin":0,"CapacityMax":4500,"SectorCounts":"Central=439 | Private=79 | State=2328 | =5","AgencyTop10":"UPPTCL=443 | PGCIL=411 | GETCO=266 | MSETCL=262 | TANTRANSCO=177 | HVPNL=157 | MPPTCL=143 | PSTCL=125 | APTRANSCO=123 | KPTCL=109","FYRange":"2015-16 | 2016-17 | 2017-18 | 2018-19 | 2019-20 | 2020-21 | 2021-22 | 2022-23 | 2023-24 | 2024-25 | 2025-26 | 2026-27","MojibakeVoltageRows":0}
    
    
    Name
    ----
    
    
    Copyright © 2026, NITI Aayog
    https://iced.niti.gov.in
    The information on this platform is mainly taken from official sources. However, in some cases, a few assumptions ha...
    
    
    ✓ • 605ms

## Activity

    $ & { $r = @(Import-Csv -LiteralPath 'Electricity Substation.csv'); [PSCustomObject]@{Rows=$r.Count; Cities=(($r.'City Name' | Sort-Object -Unique) -join ' | '); CoordinatesOutsideIndia=@($r | Where-Object { [double]$_.Longitude -lt 68 -or [double]$_.Longitude -gt 98 -or [double]$_.Latitude -lt 6 -or [double]$_.Latitude -gt 38 }).Count; CapacityExpressions=(($r.'Capacity (MVA)' | Sort-Object -Unique) -join ' | '); YearValues=(($r.Year | Sort-Object -Unique) -join ' | ')} | ConvertTo-Json -Compress; $r | Format-Table -AutoSize }
    {"Rows":12,"Cities":"Aizawl","CoordinatesOutsideIndia":0,"CapacityExpressions":"1 x 12.5 | 1 x 3.5, 1 x 2.5 | 1 x 6.3, 1 x 3.5 | 2 x 25 | 2 x 6.3 | 3 x 12.5 | 4 x 12.5","YearValues":"Dec-14 | Dec-17 | Dec-19 | Jan-06 | Jan-89 | Jul-01 | Jul-02 | Jun-06 | Mar-92 | May-06 | May-16 | NA"}
    
    City Name Ward No. Year   Name of Electrical Substations     Address
    --------- -------- ----   ------------------------------     -------
    Aizawl    NA       Dec-19 New 132 kV Zuangtui Sub-Station    Zuangtui
    Aizawl    NA       Jul-01 132 kV Zuangtui Sub-Station        Zuangtui
    Aizawl    NA       Jul-02 132 kV Luangmual Sub-Station       Luangmual
    Aizawl    NA       Dec-17 132 kV Melriat Sub-station         Melriat
    Aizawl    NA       NA     132 kV Sihhmui Sub-Station         Sihhmui
    Aizawl    NA       Jan-06 33 kV Mualpui Sub-Station          Mualpui
    Aizawl    NA       Jun-06 33 kV Chawnpui Sub-Station         Chawnpui
    Aizawl    NA       Jan-89 33 kV Tlangnuam Sub-Station        Tlangnuam
    Aizawl    NA       Mar-92 33 kV Zuangtui (Lower) Sub-Station Zuangtui
    Aizawl    NA       May-06 33 kV Luangmual                    Luangmual
    Aizawl    NA       May-16 33 kV Indoor Sub-Station           Electric Veng
    Aizawl    NA       Dec-14 33 kV Durtlang Sub-Station         Durtlang
    
    
    ✓ • 167ms

## Activity

    $ & { $dc = @(Import-Csv -LiteralPath 'Datacenters distribution in india.csv'); [PSCustomObject]@{Rows=$dc.Count; TotalDataCenters=(($dc | ForEach-Object {[int]$_.'Data Centers'} | Measure-Object -Sum).Sum); Markets=(($dc.Market | Sort-Object) -join ' | '); DuplicateMarkets=(($dc.Market | Group-Object | Where-Object Count -gt 1).Count)} | ConvertTo-Json -Compress; ''; $reg = @(Import-Csv -LiteralPath 'region_cordinates.csv'); $reg | ForEach-Object { "Region='$($_.Region)' Latitude=$($_.Latitude) Longitude=$($_.Longitude)" } }
    {"Rows":34,"TotalDataCenters":305,"Markets":"Agartala | Ahmedabad | Alwar | Bangalore | Bhopal | Bhubaneswar | Chennai | Cochin | Coimbatore | Faridabad | Guntur | Gurgaon | Hyderabad | Indore | Jaipur | Jamnagar | Kolkata | Lucknow | Ludhiana | Madurai | Mohali | Mumbai | Murshidabad | Nashik | Navi Mumbai | New Delhi | Noida | Panchkula | Patna | Pondicherry | Pune | Raipur | Rohtak | Visakhapatnam","DuplicateMarkets":0}
    
    Region='NorthEastern' Latitude=25.5736 Longitude=93.2473
    Region='Eastern' Latitude=22.8962 Longitude=85.98
    Region='Western ' Latitude=23.9074 Longitude=72.7097
    Region='Northern' Latitude=28.6139 Longitude=77.209
    Region='Southern' Latitude=12.2602 Longitude=77.1461
    ✓ • 163ms

## Activity

    $ & { 'LAND UTF8:'; Get-Content -LiteralPath 'statewise land cost.csv' -Encoding UTF8 -TotalCount 2; 'SUBSTATION UTF8:'; Get-Content -LiteralPath 'Substation_Details_1789031375809.csv' -Encoding UTF8 -TotalCount 2; 'LAND BYTES:'; Format-Hex -LiteralPath 'statewise land cost.csv' -Count 120 }
    LAND UTF8:
    "State","Lowest (Rs/Acre)","Average (Rs/Acre)","Highest (Rs/Acre)","5-Year CAGR"
    "Rajasthan","₹50,000","₹8,00,000","₹30,00,000","14%"
    SUBSTATION UTF8:
    Name,Sector,Voltage Ratio (kV/kV),Executive Agency,Capacity (MW/MVA),Month Of Completion,Year Of Completion (FY)
    Biswanath Chariyali & Agra HVDC terminal (Pole-I),Central,±800,PGCIL,1500.0,NOV-15,2015-16
    LAND BYTES:
    Format-Hex : A parameter cannot be found that matches parameter name
    'Count'.
    At line:2 char:279
    + ... TES:'; Format-Hex -LiteralPath 'statewise land cost.csv' -Count 120 }
    +                                                              ~~~~~~
        + CategoryInfo          : InvalidArgument: (:) [Format-Hex], Parameter
       BindingException
        + FullyQualifiedErrorId : NamedParameterNotFound,Format-Hex
    
    ✓ • 289ms

## Activity

    $ & { $files = 'cea_historical_coal_consumption_2004_2023.csv','cea_historical_cost_of_power_supply_and_realisation.csv','cea_historical_energy_requirement_availability_2003_2026.csv','cea_historical_peak_demand_met_2003_2026.csv','cea_historical_per_capita_consumption_2005_2023.csv'; foreach($f in $files) { $r=@(Import-Csv -LiteralPath $f); $fy=@($r | Select-Object -ExpandProperty Financial_Year); [PSCustomObject]@{File=$f; Rows=$r.Count; First=$fy[0]; Last=$fy[-1]; UniqueFY=($fy | Sort-Object -Unique).Count; DuplicateFY=($fy | Group-Object | Where-Object Count -gt 1 | Measure-Object).Count; AllFY=($fy -join ' | ')} | ConvertTo-Json -Compress } }
    {"File":"cea_historical_coal_consumption_2004_2023.csv","Rows":43,"First":"2004-05","Last":"2020-21","UniqueFY":19,"DuplicateFY":17,"AllFY":"2004-05 | 2005-06 | 2006-07 | 2007-08 | 2008-09 | 2009-10 | 2010-11 | 2011-12 | 2012-13 | 2013-14 | 2014-15 | 2015-16 | 2016-17 | 2017-18 | 2018-19 | 2019-20 | 2020-21 | 2021-22 | 2022-23 | 2005-06 | 2006-07 | 2007-08 | 2008-09 | 2009-10 | 2010-11 | 2011-12 | 2012-13 | 2013-14 | 2014-15 | 2015-16 | 2016-17 | 2017-18 | 2018-19 | 2019-20 | 2020-21 | 2021-22 | 2013-14 | 2014-15 | 2015-16 | 2016-17 | 2018-19 | 2019-20 | 2020-21"}
    {"File":"cea_historical_cost_of_power_supply_and_realisation.csv","Rows":9,"First":"2004-05","Last":"2012-13","UniqueFY":9,"DuplicateFY":0,"AllFY":"2004-05 | 2005-06 | 2006-07 | 2007-08 | 2008-09 | 2009-10 | 2010-11 | 2011-12 | 2012-13"}
    {"File":"cea_historical_energy_requirement_availability_2003_2026.csv","Rows":23,"First":"2003-04","Last":"2025-26","UniqueFY":23,"DuplicateFY":0,"AllFY":"2003-04 | 2004-05 | 2005-06 | 2006-07 | 2007-08 | 2008-09 | 2009-10 | 2010-11 | 2011-12 | 2012-13 | 2013-14 | 2014-15 | 2015-16 | 2016-17 | 2017-18 | 2018-19 | 2019-20 | 2020-21 | 2021-22 | 2022-23 | 2023-24 | 2024-25 | 2025-26"}
    {"File":"cea_historical_peak_demand_met_2003_2026.csv","Rows":23,"First":"2003-04","Last":"2025-26","UniqueFY":23,"DuplicateFY":0,"AllFY":"2003-04 | 2004-05 | 2005-06 | 2006-07 | 2007-08 | 2008-09 | 2009-10 | 2010-11 | 2011-12 | 2012-13 | 2013-14 | 2014-15 | 2015-16 | 2016-17 | 2017-18 | 2018-19 | 2019-20 | 2020-21 | 2021-22 | 2022-23 | 2023-24 | 2024-25 | 2025-26"}
    {"File":"cea_historical_per_capita_consumption_2005_2023.csv","Rows":34,"First":"2014-15","Last":"2020-21","UniqueFY":18,"DuplicateFY":10,"AllFY":"2014-15 | 2015-16 | 2016-17 | 2017-18 | 2018-19 | 2019-20 | 2020-21 | 2021-22 | 2022-23 | 2005-06 | 2006-07 | 2007-08 | 2008-09 | 2009-10 | 2010-11 | 2011-12 | 2012-13 | 2013-14 | 2014-15 | 2015-16 | 2016-17 | 2017-18 | 2018-19 | 2019-20 | 2020-21 | 2021-22 | 2022-23 | 2013-14 | 2014-15 | 2015-16 | 2016-17 | 2018-19 | 2019-20 | 2020-21"}
    ✓ • 169ms

## Activity

    $ & { $files = 'cea_historical_coal_consumption_2004_2023.csv','cea_historical_per_capita_consumption_2005_2023.csv'; foreach($f in $files) { "### $f"; $r=@(Import-Csv -LiteralPath $f); $r | Group-Object Financial_Year | Where-Object Count -gt 1 | ForEach-Object { [PSCustomObject]@{FinancialYear=$_.Name; Records=$_.Count; Values=(($_.Group | ForEach-Object { ($_.PSObject.Properties | Where-Object Name -ne 'Financial_Year' | ForEach-Object Value) -join ',') -join ' | ')} } } | Format-Table -AutoSize } }
    At line:2 char:358
    + ... .Name; Records=$_.Count; Values=(($_.Group | ForEach-Object {
    ($_.PSO ...
    +                                                                 ~
    Missing closing '}' in statement block or type definition.
    At line:2 char:478
    + ... _Year' | ForEach-Object Value) -join ',') -join ' | ')} } } |
    Format- ...
    +                                                                 ~
    An empty pipe element is not allowed.
    At line:2 char:505
    + ... ject Value) -join ',') -join ' | ')} } } | Format-Table -AutoSize } }
    +                                                                         ~
    Unexpected token '}' in expression or statement.
        + CategoryInfo          : ParserError: (:) [], ParentContainsErrorReco
       rdException
        + FullyQualifiedErrorId : MissingEndCurlyBrace
    
    ✗ (1) • 90ms

## Activity

    $ & { '### Coal'; $r=@(Import-Csv -LiteralPath 'cea_historical_coal_consumption_2004_2023.csv'); $r | Group-Object Financial_Year | Where-Object Count -gt 1 | ForEach-Object { [PSCustomObject]@{FinancialYear=$_.Name; Records=$_.Count; CoalValues=(($_.Group | Select-Object -ExpandProperty Coal_Consumption_Million_Tonnes) -join ' | ')} } | Format-Table -AutoSize; '### Per capita'; $r=@(Import-Csv -LiteralPath 'cea_historical_per_capita_consumption_2005_2023.csv'); $r | Group-Object Financial_Year | Where-Object Count -gt 1 | ForEach-Object { [PSCustomObject]@{FinancialYear=$_.Name; Records=$_.Count; kWhValues=(($_.Group | Select-Object -ExpandProperty Per_Capita_Consumption_kWh) -join ' | ')} } | Format-Table -AutoSize }
    ### Coal
    
    FinancialYear Records CoalValues
    ------------- ------- ----------
    2005-06             2 281.0 | 631.4
    2006-07             2 302.0 | 671.9
    2007-08             2 330.0 | 717.1
    2008-09             2 355.0 | 733.5
    2009-10             2 367.0 | 778.6
    2010-11             2 387.0 | 818.8
    2011-12             2 417.56 | 883.63
    2012-13             2 454.6 | 914.41
    2013-14             3 489.4 | 957.0 | 519.0
    2014-15             3 530.4 | 1010.0 | 521.0
    2015-16             3 545.9 | 1075.0 | 531.0
    2016-17             3 574.3 | 1122.0 | 538.0
    2017-18             2 608.0 | 1149.0
    2018-19             3 628.9 | 1181.0 | 600.0
    2019-20             3 622.2 | 1208.0 | 614.0
    2020-21             3 615.44 | 1161.0 | 619.0
    2021-22             2 697.34 | 1255.0
    
    
    ### Per capita
    
    FinancialYear Records kWhValues
    ------------- ------- ---------
    2014-15             3 530.4 | 1010.0 | 521.0
    2015-16             3 545.9 | 1075.0 | 531.0
    2016-17             3 574.3 | 1122.0 | 538.0
    2017-18             2 608.0 | 1149.0
    2018-19             3 628.9 | 1181.0 | 600.0
    2019-20             3 622.2 | 1208.0 | 614.0
    2020-21             3 615.44 | 1161.0 | 619.0
    2021-22             2 697.34 | 1255.0
    2022-23             2 776.79 | 1331.0
    2013-14             2 957.0 | 519.0
    
    
    ✓ • 166ms

## Activity

    $ & { $r=@(Import-Csv -LiteralPath 'cubems-smart-building-energy-and-iaq-summary.csv'); [PSCustomObject]@{Rows=$r.Count; Years=(($r.year | Sort-Object -Unique) -join ' | '); Floors=(($r.floor | Sort-Object -Unique) -join ' | '); DuplicateFloorYear=(($r | Group-Object { "$($_.floor)|$($_.year)" } | Where-Object Count -gt 1).Count); Files=(($r.file | Sort-Object) -join ' | '); RecordRows=(($r.rows | Sort-Object -Unique) -join ' | ')} | ConvertTo-Json -Compress }
    {"Rows":14,"Years":"2018 | 2019","Floors":"1 | 2 | 3 | 4 | 5 | 6 | 7","DuplicateFloorYear":0,"Files":"cubems-smart-building-energy-and-iaq-data/2018Floor1.csv | cubems-smart-building-energy-and-iaq-data/2018Floor2.csv | cubems-smart-building-energy-and-iaq-data/2018Floor3.csv | cubems-smart-building-energy-and-iaq-data/2018Floor4.csv | cubems-smart-building-energy-and-iaq-data/2018Floor5.csv | cubems-smart-building-energy-and-iaq-data/2018Floor6.csv | cubems-smart-building-energy-and-iaq-data/2018Floor7.csv | cubems-smart-building-energy-and-iaq-data/2019Floor1.csv | cubems-smart-building-energy-and-iaq-data/2019Floor2.csv | cubems-smart-building-energy-and-iaq-data/2019Floor3.csv | cubems-smart-building-energy-and-iaq-data/2019Floor4.csv | cubems-smart-building-energy-and-iaq-data/2019Floor5.csv | cubems-smart-building-energy-and-iaq-data/2019Floor6.csv | cubems-smart-building-energy-and-iaq-data/2019Floor7.csv","RecordRows":"264960 | 424169 | 525600"}
    ✓ • 160ms

## Activity

    $ & { $r=@(Import-Csv -LiteralPath 'sub-stations-220-kv-and.csv'); $vals=@($r | ForEach-Object {[double]$_.'State Sector'}); [PSCustomObject]@{Rows=$r.Count; NumericSecondColumn=$vals.Count; MinSecondColumn=($vals|Measure-Object -Minimum).Minimum; MaxSecondColumn=($vals|Measure-Object -Maximum).Maximum; HtmlBreakRows=@($r | Where-Object { $_.Sector -match '<br>' }).Count; ContainsStateCodes=@($r | Where-Object { $_.Sector -match 'state|pradesh|gujarat|karnataka|tamil' }).Count; Examples=(($r | Select-Object -First 5 | ForEach-Object { "$($_.Sector) => $($_.'State Sector')"}) -join ' || ')} | ConvertTo-Json -Compress }
    {"Rows":20,"NumericSecondColumn":20,"MinSecondColumn":20,"MaxSecondColumn":500,"HtmlBreakRows":20,"ContainsStateCodes":0,"Examples":"400/220kV/kV\u003cbr\u003eBhopal 400 kV SS (replacement of 315 MVA by 500 MVA T/F) =\u003e 185 || 400/220kV/kV\u003cbr\u003e400 kV S/S Nakodar =\u003e 500 || 400/110kV/kV\u003cbr\u003eVellalaviduthi (400/110 kV T/F-II) =\u003e 200 || 400/230kV/kV\u003cbr\u003eSriperumbudur 400/230 kV SS (enhancement from 3x315+1x500 MVA to 2x315+2x500 MVA) =\u003e 185 || 230/110kV/kV\u003cbr\u003eMondipatty SS (replacement of 80 MVA T/F with 100 MVA) =\u003e 20"}
    ✓ • 205ms

## Assistant

The inspection found several source-extraction faults that materially affect sequencing: two historical CEA files contain conflicting duplicated fiscal-year values; the CEA July-2026 “statewise” file has lost most state labels; and some MNRE total/continuation rows require repair or re-extraction. I’m reflecting those as explicit quarantine/rebuild steps, rather than treating every CSV as ML-ready.

## Activity

    $ Get-ChildItem -Path 'C:\Users\nitin\.codex' -Recurse -Filter 'mark_artifact_operation_started.mjs' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
    C:\Users\nitin\.codex\plugins\cache\openai-primary-runtime\documents\26.819.11345\skills\documents\container_tools\mark_artifact_operation_started.mjs
    C:\Users\nitin\.codex\plugins\cache\openai-primary-runtime\pdf\26.819.11345\skills\pdf\container_tools\mark_artifact_operation_started.mjs
    C:\Users\nitin\.codex\plugins\cache\openai-primary-runtime\presentations\26.819.11345\skills\presentations\container_tools\mark_artifact_operation_started.mjs
    C:\Users\nitin\.codex\plugins\cache\openai-primary-runtime\spreadsheets\26.819.11345\skills\spreadsheets\container_tools\mark_artifact_operation_started.mjs
    ✓ • 1.31s

## Activity

    file changes: Completed · 1 changes
    Add: C:\Users\nitin\OneDrive\Desktop\COE Project\DataFrame\data\build_preprocessing_roadmap.ps1
    $ErrorActionPreference = 'Stop'
    
    $outputPath = Join-Path (Get-Location) 'Data_Preprocessing_and_Feature_Engineering_Roadmap.docx'
    
    function WordColor([int]$r, [int]$g, [int]$b) {
        return $r + ($g * 256) + ($b * 65536)
    }
    
    $blue = WordColor 46 116 181
    $darkBlue = WordColor 31 77 120
    $ink = WordColor 11 37 69
    $muted = WordColor 89 89 89
    $lightBlue = WordColor 232 238 245
    $lightGray = WordColor 242 244 247
    $callout = WordColor 244 246 249
    $white = WordColor 255 255 255
    $black = WordColor 0 0 0
    
    $word = $null
    $doc = $null
    
    try {
        $word = New-Object -ComObject Word.Application
        $word.Visible = $false
        $word.DisplayAlerts = 0
        $doc = $word.Documents.Add()
        $section = $doc.Sections.Item(1)
        $section.PageSetup.TopMargin = 72
        $section.PageSetup.BottomMargin = 72
        $section.PageSetup.LeftMargin = 72
        $section.PageSetup.RightMargin = 72
        $section.PageSetup.HeaderDistance = 35.4
        $section.PageSetup.FooterDistance = 35.4
    
        function New-ParaStyle([string]$name, [double]$size, [int]$color, [double]$before, [double]$after, [double]$lineSpacing, [bool]$bold = $false) {
            $style = $doc.Styles.Add($name, 1)
            $style.Font.Name = 'Calibri'
            $style.Font.Size = $size
            $style.Font.Color = $color
            $style.Font.Bold = [int]$bold
            $style.ParagraphFormat.SpaceBefore = $before
            $style.ParagraphFormat.SpaceAfter = $after
            $style.ParagraphFormat.LineSpacing = $lineSpacing
            return $style
        }
    
        $null = New-ParaStyle 'Roadmap Body' 11 $black 0 6 13.75 $false
        $null = New-ParaStyle 'Roadmap Title' 24 $ink 0 6 28 $true
        $null = New-ParaStyle 'Roadmap Subtitle' 12 $muted 0 15 15 $false
        $null = New-ParaStyle 'Roadmap H1' 16 $blue 18 10 19 $true
        $null = New-ParaStyle 'Roadmap H2' 13 $blue 14 7 16 $true
        $null = New-ParaStyle 'Roadmap H3' 12 $darkBlue 10 5 15 $true
        $null = New-ParaStyle 'Roadmap Small' 9 $muted 0 4 11 $false
    
        $header = $section.Headers.Item(1).Range
        $header.Text = 'DATA PREPARATION ROADMAP | INDIA ENERGY AND DATA-CENTRE DATA'
        $header.Font.Name = 'Calibri'
        $header.Font.Size = 8.5
        $header.Font.Color = $muted
        $header.ParagraphFormat.Alignment = 0
        $header.ParagraphFormat.SpaceAfter = 0
    
        $footer = $section.Footers.Item(1).Range
        $footer.Text = 'Data preprocessing guide | Page '
        $footer.Font.Name = 'Calibri'
        $footer.Font.Size = 8.5
        $footer.Font.Color = $muted
        $footer.ParagraphFormat.Alignment = 2
        $null = $footer.Fields.Add($footer, 33)
    
        $sel = $word.Selection
    
        function Add-Text([string]$text, [string]$style = 'Roadmap Body') {
            $sel.Style = $style
            $sel.TypeText($text)
            $sel.TypeParagraph()
        }
    
        function Add-Heading([string]$text, [int]$level = 1) {
            $style = switch ($level) {
                1 { 'Roadmap H1' }
                2 { 'Roadmap H2' }
                default { 'Roadmap H3' }
            }
            Add-Text $text $style
        }
    
        function Add-Bullet([string]$text) {
            $sel.Style = 'Roadmap Body'
            $sel.TypeText($text)
            $sel.Range.ListFormat.ApplyBulletDefault()
            $sel.TypeParagraph()
        }
    
        function Add-Note([string]$text) {
            $table = $doc.Tables.Add($sel.Range, 1, 1)
            $table.AutoFitBehavior(0)
            $table.PreferredWidthType = 3
            $table.PreferredWidth = 468
            $table.Columns.Item(1).Width = 468
            $table.Rows.SetLeftIndent(6, 0)
            $cell = $table.Cell(1, 1)
            $cell.Range.Text = $text
            $cell.Range.Font.Name = 'Calibri'
            $cell.Range.Font.Size = 10.5
            $cell.Range.Font.Color = $ink
            $cell.Range.ParagraphFormat.SpaceBefore = 3
            $cell.Range.ParagraphFormat.SpaceAfter = 3
            $cell.Shading.BackgroundPatternColor = $callout
            $table.Borders.Enable = 1
            $sel.SetRange($table.Range.End, $table.Range.End)
            $sel.TypeParagraph()
        }
    
        function Add-Table([object[]]$rows, [double[]]$widths) {
            $table = $doc.Tables.Add($sel.Range, $rows.Count, $widths.Count)
            $table.AutoFitBehavior(0)
            $table.PreferredWidthType = 3
            $table.PreferredWidth = 468
            $table.Rows.SetLeftIndent(6, 0)
            $table.Borders.Enable = 1
            for ($c = 1; $c -le $widths.Count; $c++) {
                $table.Columns.Item($c).Width = $widths[$c - 1]
                $table.Columns.Item($c).PreferredWidthType = 3
                $table.Columns.Item($c).PreferredWidth = $widths[$c - 1]
            }
            for ($r = 1; $r -le $rows.Count; $r++) {
                for ($c = 1; $c -le $widths.Count; $c++) {
                    $cell = $table.Cell($r, $c)
                    $cell.Range.Text = [string]$rows[$r - 1][$c - 1]
                    $cell.Range.Font.Name = 'Calibri'
                    $cell.Range.Font.Size = if ($r -eq 1) { 9.2 } else { 9.0 }
                    $cell.Range.ParagraphFormat.SpaceBefore = 1.5
                    $cell.Range.ParagraphFormat.SpaceAfter = 1.5
                    $cell.VerticalAlignment = 0
                    if ($r -eq 1) {
                        $cell.Range.Font.Bold = 1
                        $cell.Range.Font.Color = $ink
                        $cell.Shading.BackgroundPatternColor = $lightBlue
                    } else {
                        $cell.Range.Font.Color = $black
                        if (($r % 2) -eq 0) { $cell.Shading.BackgroundPatternColor = $white } else { $cell.Shading.BackgroundPatternColor = $lightGray }
                    }
                }
            }
            $table.Rows.Item(1).HeadingFormat = $true
            $sel.SetRange($table.Range.End, $table.Range.End)
            $sel.TypeParagraph()
        }
    
        function Add-PageBreak() { $sel.InsertBreak(7) }
    
        # Title block: named override for this report (24 pt ink-blue title, compact metadata).
        Add-Text 'DATA PREPROCESSING AND FEATURE ENGINEERING ROADMAP' 'Roadmap Title'
        Add-Text 'File-by-file guidance for the India energy, infrastructure, water and data-centre datasets' 'Roadmap Subtitle'
        Add-Text 'Prepared: 22 September 2026 | Scope: source assessment, preprocessing order and ML-ready feature planning' 'Roadmap Small'
        Add-Note 'Decision: begin with a state-level analytical panel and keep regional daily generation as a separate time-series track. Do not force all files into one training table. A prediction target has not yet been selected, so this guide creates auditable, target-agnostic assets and quarantines unsafe source extracts.'
    
        Add-Heading '1. Executive decision: where to start', 1
        Add-Text 'The useful starting point is a state dimension plus a 2025 renewable-energy and resource snapshot. It is the only coherent join path across renewable capacity, potential, water availability proxies, land costs and the geography file. The data-centre file is city-level; map its 34 markets to the same state key before using it as a target, a ranking input or a descriptive outcome.'
        Add-Table @(
            @('Build order', 'Files to use first', 'Why this comes first'),
            @('1. Canonical geography', 'archive\\india_states.geojson; State_Region_corrected.csv', 'Creates state_id, canonical state name, region, area and geometry. Every state-level join depends on this.'),
            @('2. Renewable snapshot', 'mnre_re_installed_capacity_by_source_2025.csv; mnre_re_estimated_potential_by_state.csv; mnre_re_cumulative_capacity_timeseries_2018_2025.csv', 'Best foundation for capacity, resource headroom and historical growth. Repair aliases and remove report totals before merging.'),
            @('3. Resource and cost enrichments', 'area-wise-waterbodies-india-statewise.csv; state-ground-water-level-information.csv; statewise land cost.csv', 'Useful siting inputs. Waterbody data is complete; groundwater and land cost need explicit missingness treatment.'),
            @('4. Data-centre outcome layer', 'Datacenters distribution in india.csv', 'Maps 305 data centres across 34 markets. Add a verified market-to-state crosswalk and retain city grain.'),
            @('5. Separate temporal track', 'file_02.csv; clean CEA time series where approved', 'Daily regional generation supports time-series work. It must not be cross-joined to the state snapshot without an explicit aggregation or target design.')
        ) @(102, 172, 194)
    
        Add-Heading '2. Non-negotiable preprocessing contract', 1
        Add-Bullet 'Keep raw files immutable. Write each repaired output to a clean layer and retain source_file, source_row and processing_version fields for lineage.'
        Add-Bullet 'Read text CSVs as UTF-8. The land-cost rupee symbol and the substation plus/minus voltage symbol render correctly in UTF-8; default Windows decoding makes them appear corrupted.'
        Add-Bullet 'Create a dim_state_alias table before any merge. Use state_id as the join key, not display labels. Normalise trim, case and punctuation, then explicitly map historical names such as Pondicherry/Puducherry, Odisha/Orissa and union-territory variants.'
        Add-Bullet 'Remove national, regional and report-total rows from state facts before joining. Recompute totals from components and keep a total_recomputed flag rather than trusting malformed report totals.'
        Add-Bullet 'Never encode a label, name, address, source URL or row index as a numeric feature. Preserve identifiers for joins and diagnostics only.'
        Add-Bullet 'Use train-only fitting for imputation, scaling, frequency encoding and target encoding. For time series split by time; for state/site work use group-aware or spatially aware validation rather than random row splits.'
    
        Add-Heading '3. Recommended clean-layer outputs', 1
        Add-Table @(
            @('Output asset', 'Grain / key', 'Content and gate'),
            @('dim_state.csv', 'one row per state_id', 'GeoJSON name, corrected region, area_km2, geometry reference and aliases. Extend the 34-row regional file to the GeoJSON coverage; no unmatched usable fact key is allowed.'),
            @('bridge_market_state.csv', 'one row per market', 'Verified market, state_id, city name, source and confidence. Keep Mumbai and Navi Mumbai as distinct markets while allowing a state aggregate.'),
            @('fact_re_state_2025.csv', 'state_id, snapshot_date', 'Installed capacity and estimated potential by source, after removal or repair of continuation, Others and Total rows.'),
            @('fact_re_capacity_long.csv', 'state_id, financial_year', 'Wide cumulative-capacity file reshaped to long form. Keep regional totals in a separate table, never as state rows.'),
            @('fact_state_resources.csv', 'state_id', 'Waterbody counts, groundwater range fields and land-cost fields with coverage flags.'),
            @('fact_market_datacentres.csv', 'market, snapshot_date', 'Current data-centre count plus state_id through the bridge. Do not pretend this has an observed historical date if none is present.'),
            @('fact_regional_generation_daily.csv', 'date, region', 'Actual and estimated thermal, nuclear and hydro values from file_02, plus availability flags and time features.'),
            @('quarantine_manifest.csv', 'source file / reason', 'Every file or row blocked from ML use, the failing test and the approved remediation path.')
        ) @(130, 130, 208)
    
        Add-Heading '4. Features to engineer after the clean layer', 1
        Add-Table @(
            @('Feature family', 'Examples', 'Rules / leakage controls'),
            @('Renewable capacity and headroom', 'source capacity shares; re_capacity_mw / re_potential_mw; potential_remaining_mw; source diversity index', 'Align snapshot dates. Divide only after zero checks; keep numerator and denominator. Capacity/potential ratios are descriptive unless both were available before the prediction date.'),
            @('Growth', 'year-on-year capacity delta; growth rate; 3-year CAGR; rank within region', 'Derive only from the long capacity fact and use lagged values. No future years in a training feature.'),
            @('Water and land', 'waterbody_count_total; small/large waterbody share; water_level_range; log_land_cost; land_cost_spread', 'Water-level columns are reported ranges, not a validated water-stress score. Do not infer stress direction without metadata. Land data covers only 12 states; include land_cost_missing.'),
            @('Grid and substations', 'count, capacity sum, median voltage, asset age, sector mix', 'Use only once state/city geography is resolved. Capacity is labeled MW/MVA in the large file; preserve unit uncertainty and do not mix it with MW generation.'),
            @('Data-centre market', 'market count; state aggregate; centres per area; market present flag', 'Keep city and state metrics separate. If data-centre count is the target, do not use a same-date count-derived feature as a predictor.'),
            @('Regional daily generation', 'actual-minus-estimated; absolute percentage error; weekday/month/monsoon proxy; 7/30-day rolling means; lags', 'Sort by date within region, use only prior observations for lags/rolls and retain structural nuclear-missing flags.'),
            @('Geography', 'region one-hot; centroid latitude/longitude; area', 'Use region coordinates only for display or a coarse regional reference. Prefer state geometry-derived centroids for state-level model features.')
        ) @(118, 174, 176)
    
        Add-Heading '5. Encoding and missing-data rules', 1
        Add-Table @(
            @('Field type', 'Treatment', 'Do not do this'),
            @('Low-cardinality category', 'One-hot encode region and substation sector; keep an explicit Unknown category where valid.', 'Do not ordinal-encode nominal labels such as Northern=1, Southern=2.'),
            @('High-cardinality category', 'For executive agency use train-fold frequency encoding or a regularised target encoder only after target and split are defined.', 'Do not label-encode agency, market, name or address as arbitrary integers.'),
            @('Dates / fiscal years', 'Parse into a date or financial-year start/end; derive cyclical calendar variables only for daily data.', 'Do not treat 2017-18 as a continuous numeric measurement without defining its temporal convention.'),
            @('Currency / percentage text', 'Strip rupee symbols, Indian digit separators and percent signs; store numeric rupees per acre and CAGR as decimal.', 'Do not cast strings such as Rs 8,00,000 or 14% directly without cleaning and range tests.'),
            @('Structural missing values', 'Use an availability flag. In file_02, nuclear values are missing for most Eastern and NorthEastern records; distinguish not-reported from zero.', 'Do not blindly impute structural nuclear missingness to the global mean or zero.'),
            @('Sparse coverage', 'For groundwater and land use missingness flags; evaluate model performance with and without these features.', 'Do not claim nationwide coverage from 29 groundwater or 12 land-cost records.')
        ) @(120, 183, 165)
    
        Add-PageBreak
        Add-Heading '6. File-by-file register: start and core inputs', 1
        Add-Text 'The following files are the first pass. “Repair” means create a documented clean copy; it does not mean overwrite the supplied file.'
        Add-Table @(
            @('File', 'Disposition', 'File-specific preprocessing and feature work'),
            @('archive\\india_states.geojson', 'START - core dimension', '35 Polygon/MultiPolygon features. Retain NAME_1, ID_1 and geometry; make a canonical state_id. Do not use free-text VARNAME_1 as a model feature. Build centroid only after geometry validation.'),
            @('State_Region_corrected.csv', 'START - core dimension', '34 rows with area and region. Rename headers to snake_case, parse area and national_share_pct, standardise state names and reconcile its incomplete coverage against GeoJSON.'),
            @('mnre_re_installed_capacity_by_source_2025.csv', 'START after entity repair', '37 filtered detail rows reconcile to source components. Reassemble broken union-territory continuation rows, drop Others/Total, numeric-cast MWs and recompute total_res_mw from components.'),
            @('mnre_re_estimated_potential_by_state.csv', 'START after alias mapping', '35 filtered detail rows reconcile to reported total. Drop Others/Total, numeric-cast MWs and derive source potential shares and remaining potential only when joined to a same-definition capacity snapshot.'),
            @('mnre_re_cumulative_capacity_timeseries_2018_2025.csv', 'START after reshape', '42 rows include regional totals, Grand Total and Others. Remove non-state rows, map the abbreviated Dadra and Nagar label, melt year columns to financial_year and derive lagged growth.'),
            @('area-wise-waterbodies-india-statewise.csv', 'START - resource feature', '37 complete state rows. Rename size bands, numeric-cast counts, sum to waterbody_count_total and derive size-band shares. Reconcile six names not matching GeoJSON after normalisation.'),
            @('state-ground-water-level-information.csv', 'START with coverage flag', '29 state rows. Numeric-cast station count and min/max ranges; check min <= max; derive observed_range_width. Preserve the source semantics and unit uncertainty.'),
            @('statewise land cost.csv', 'START as sparse feature', '12 rows. Read UTF-8; parse rupee/Indian-grouped strings and CAGR. Derive log_avg_land_cost and high_low_spread, retain land_cost_missing outside the 12 covered states.'),
            @('Datacenters distribution in india.csv', 'START - outcome layer', '34 unique markets and 305 total centres. Rename to market and data_center_count, integer-cast count, add a verified market-to-state bridge, then retain both city and state aggregate grains.'),
            @('region_cordinates.csv', 'START for maps only', 'Five regional reference points; trim the trailing space in Western. Use for presentation or a coarse regional join, not as a substitute for state centroids.'),
            @('file_02.csv', 'START - separate time series', '4,945 unique date-region records from 2017-09-01 to 2020-08-01. Drop index (310 duplicate values); parse comma-formatted MU fields, date and region; derive residuals, lags and rolling features within region.'),
            @('mnre_re_share_in_total_capacity_2025.csv', 'START after recomputation', 'Detail rows are largely usable, but Delhi, Lakshadweep and Pondicherry report zero total RE despite non-zero components. Drop Others/Total and recompute total_re, grand_total and shares from components for every state.')
        ) @(126, 105, 237)
    
        Add-Heading '7. File-by-file register: conditional or repair-first inputs', 1
        Add-Table @(
            @('File', 'Disposition', 'File-specific preprocessing and feature work'),
            @('mnre_bio_and_solar_breakdown_2025.csv', 'REPAIR FIRST', 'State names are split across continuation rows for Andaman/Nicobar and Dadra/Nagar Haveli/Daman/Diu; Others and a malformed Total row exist. Reassemble entities from source, remove report rows, then use source MW shares.'),
            @('mnre_re_generation_by_source_statewise_2024_2025.csv', 'QUARANTINE pending re-extract', '11 of 36 filtered state rows have total generation values that contradict component sums by material amounts. Do not train on it or silently replace totals; re-extract the official table and reconcile all components.'),
            @('cea_installed_capacity_statewise_fuelwise_jul2026.csv', 'QUARANTINE pending re-extract', '177 rows have internally consistent arithmetic, but most state labels have been lost/replaced by regional labels and broken total text. Re-extract from the CEA source before any state-level use.'),
            @('Substation_Details_1789031375809.csv', 'CONDITIONAL - useful asset table', '2,851 rows; remove five non-record/footer rows and rows with blank key fields. Parse UTF-8 voltage, numeric capacity, month-year date and fiscal year. Extract high/low kV, HVDC flag, asset age and agency/sector features after resolving location.'),
            @('Electricity Substation.csv', 'CONDITIONAL - Aizawl only', '12 coordinate-level Aizawl records. Parse MMM-YY dates, transformer expressions such as 2 x 25 into summed MVA, voltage from name and geospatial deduplication key. Useful only for local case work, not a national model.'),
            @('sub-stations-220-kv-and.csv', 'CONDITIONAL - reconstruct schema', '20 HTML-contaminated descriptions; the second “State Sector” field is numeric but does not contain a state. Rename to raw_description and reported_capacity_delta_mva only after source verification; extract voltage ratios and place names.'),
            @('cubems-smart-building-energy-and-iaq-summary.csv', 'CONTEXT / benchmark', '14 floor-year summaries for seven floors in 2018-19, not Indian data-centre operations. Derive average kW per recorded row only with sampling-frequency documentation; do not merge into the India state panel.'),
            @('cea_historical_energy_requirement_availability_2003_2026.csv', 'CONDITIONAL - clean national series', '23 unique annual rows through 2025-26. Parse fiscal year, validate supplied deficit/growth calculations and use only for national temporal context or forecasting with time-based validation.'),
            @('cea_historical_peak_demand_met_2003_2026.csv', 'CONDITIONAL - clean national series', '23 unique annual rows through 2025-26. Treat as a separate national series; derive peak deficit and growth only from earlier fiscal years.'),
            @('cea_historical_cost_of_power_supply_and_realisation.csv', 'CONTEXT ONLY', 'Nine clean rows ending 2012-13. Numeric-cast paise/kWh and derive supply-realisation gaps, but it is too small and stale for a standalone ML feature set.'),
            @('cea_historical_power_capacity_growth_since_1985.csv', 'CONTEXT ONLY', 'Eight plan-end snapshots. Extract the terminal year from Plan_Year and recompute component totals for checks; use for EDA, not model training.'),
            @('cea_transmission_grid_voltage_classes.csv', 'LOOKUP ONLY', 'Five voltage-class definitions. Standardise voltage_kv and use to validate/explain substation voltage parsing; it has no modelling sample size by itself.')
        ) @(126, 105, 237)
    
        Add-Heading '8. File-by-file register: exclude, duplicate or reference-only', 1
        Add-Table @(
            @('File', 'Disposition', 'Reason and action'),
            @('cea_historical_coal_consumption_2004_2023.csv', 'QUARANTINE', '43 rows contain 17 duplicate fiscal years with conflicting values under one coal column. This is an accidental multi-series append, not a deduplication problem. Re-extract before use.'),
            @('cea_historical_per_capita_consumption_2005_2023.csv', 'QUARANTINE', '34 rows contain 10 duplicate fiscal years with conflicting values under one per-capita column. Re-extract the official series; do not select one duplicate by position.'),
            @('Datacenters distribution in india.xlsx', 'DUPLICATE EXPORT', 'Same one-sheet, 34-row, two-column structure as the CSV. Use the UTF-8 CSV as canonical and retain XLSX only for source verification.'),
            @('Substation_Details_1789031375809.xlsx', 'DUPLICATE EXPORT', 'Same one-sheet, 2,851-row, seven-column structure as the CSV. Use one canonical export to avoid double loading; CSV is simpler for an auditable pipeline.'),
            @('Executive_Summary_July_2026_Actual.pdf', 'REFERENCE ONLY', '66-page CEA source report. It documents supply, capacity and substation tables; use it to re-extract/reconcile damaged CEA CSVs, not as a direct ML input.'),
            @('statewise and national renewable energy stats.pdf', 'REFERENCE ONLY', '121-page MNRE source report. Use for lineage and re-extraction of malformed MNRE rows/totals, not as direct tabular training data.'),
            @('Unrequired data\\global-data-center-dataset.csv', 'EXCLUDE', 'Explicitly in Unrequired data; includes Unnamed columns and substantial missingness. It is global, not a compatible India site-level panel.'),
            @('Unrequired data\\global-data-center-dataset-original.csv', 'EXCLUDE', 'Explicitly in Unrequired data and contains qualitative/approximate global values. Do not blend with measured Indian market counts.'),
            @('Unrequired data\\global-data-center-energy-consumption.csv', 'EXCLUDE', 'Explicitly in Unrequired data and has a multi-row header/schema loss. Keep outside automatic ingestion.')
        ) @(126, 105, 237)
    
        Add-Heading '9. Pipeline gates before modelling', 1
        Add-Table @(
            @('Gate', 'Pass condition', 'Failure action'),
            @('Schema', 'Expected columns, numeric types, UTF-8 decode and source row count are versioned.', 'Stop the build and record a schema-drift issue.'),
            @('Keys', 'No duplicate state_id/snapshot_date or date/region fact keys; state joins have an explicit match report.', 'Repair aliases or hold unmatched rows in quarantine; never fuzzy-match silently.'),
            @('Totals', 'Published and recomputed totals are reconciled within stated rounding tolerance.', 'Keep recomputed total only when components and definition are verified; otherwise re-extract source.'),
            @('Ranges', 'Non-negative MW/MU/count fields, valid percentages, min <= max water ranges and India coordinate bounds.', 'Flag or remove source/footer records with a reason code.'),
            @('Temporal availability', 'Every feature has an as-of date earlier than the target observation.', 'Remove or lag the leaking feature.'),
            @('Coverage', 'Feature coverage and missingness are reported by state/region and split.', 'Use a missingness flag, limit the model scope or acquire data; do not hide sparse coverage.'),
            @('Evaluation', 'Target, unit of prediction, metric and split strategy are written before encoding/model fitting.', 'Do not select a model or perform target encoding until these choices exist.')
        ) @(110, 196, 162)
    
        Add-Heading '10. Practical first sprint', 1
        Add-Text '1. Build dim_state_alias and bridge_market_state, including documented manual decisions. 2. Produce fact_re_state_2025 from the three MNRE capacity/potential files and a fact_state_resources table. 3. Run key, coverage, component-total and unit tests. 4. Create a descriptive state_snapshot_2025 feature table without a target. 5. In parallel, clean file_02 into a regional daily time-series table. 6. Re-extract every quarantined CEA/MNRE source before it can enter an ML training pipeline.'
        Add-Note 'Model decision still needed: choose whether the eventual target is (a) market/site suitability or data-centre concentration, (b) regional generation/forecast error, (c) substation capacity or commissioning, or another outcome. Each requires a different grain, date alignment and validation plan; selecting it after the clean layer prevents preventable leakage.'
    
        Add-Text 'Assessment basis: 33 source files in the supplied directory, including CSV, XLSX, GeoJSON and two source PDFs. Counts and quality findings in this guide are from direct structural inspection of the supplied files on 22 September 2026.' 'Roadmap Small'
    
        $doc.BuiltInDocumentProperties.Item('Title').Value = 'Data Preprocessing and Feature Engineering Roadmap'
        $doc.BuiltInDocumentProperties.Item('Subject').Value = 'India energy and data-centre dataset assessment'
        $doc.BuiltInDocumentProperties.Item('Author').Value = 'Codex'
        $doc.SaveAs2($outputPath, 16)
        $doc.Close($false)
        $doc = $null
        $word.Quit()
        $word = $null
        Write-Output $outputPath
    }
    finally {
        if ($doc -ne $null) { $doc.Close($false) }
        if ($word -ne $null) { $word.Quit() }
    }

## Assistant

I’ve completed the source audit and am now generating the Word guide. It will include the recommended starting datasets, a clean-layer design, encoding and feature rules, and a disposition with next action for every file.

## Activity

    $ node 'C:\Users\nitin\.codex\plugins\cache\openai-primary-runtime\documents\26.819.11345\skills\documents\container_tools\mark_artifact_operation_started.mjs' --operation-kind create --expected-output-count 1 --output-format docx
    ✓ • 74ms

## Activity

    $ & '.\build_preprocessing_roadmap.ps1'
    Object reference not set to an instance of an object.
    At C:\Users\nitin\OneDrive\Desktop\COE
    Project\DataFrame\data\build_preprocessing_roadmap.ps1:282 char:5
    +     $doc.BuiltInDocumentProperties.Item('Title').Value = 'Data Prepro ...
    +     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        + CategoryInfo          : OperationStopped: (:) [], NullReferenceExcep
       tion
        + FullyQualifiedErrorId : System.NullReferenceException
    
    ✗ (1) • 23.76s

## User

run the last build roadmap step
