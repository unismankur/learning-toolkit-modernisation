# Tax Document Automation Pipeline — Flow Overview

Privacy-safe architecture documentation. All names, properties, and paths are
genericised. No personal data, real folder paths, or identifying keywords
appear in this repo — classification keywords live only in the local
`config.json` and script copy, which are excluded from version control.

---

## 1. End-to-End Pipeline

```mermaid
flowchart TD
    A[Source folders<br/>multiple cloud-synced roots<br/>income statements, invoices, receipts,<br/>rental and super deduction documents] --> B[Scan script<br/>recursive walk of all configured roots<br/>any folder depth]

    B --> C[SHA-256 content hash<br/>per file]
    C --> D{Duplicate content?<br/>same bytes, any filename,<br/>any folder}
    D -- Yes --> E[Skip copy<br/>log as duplicate in audit trail]
    D -- No --> F{Ownership classification<br/>priority-ordered rules}

    F -- "Joint keyword match<br/>(shared property / joint super)" --> G[Joint bucket]
    F -- "Person A keyword or tag match" --> H[Person A bucket]
    F -- "Person B keyword or tag match" --> I[Person B bucket]
    F -- "No tag, or conflicting tags" --> J[Needs-Review bucket<br/>never guessed]

    G --> K[Accountant-ready output folder<br/>per-person and joint subfolders<br/>by category]
    H --> K
    I --> K
    J --> L[Manual review<br/>human moves files to correct bucket]
    L --> K

    E --> M[Audit log CSV<br/>original path, new path, owner,<br/>category, status, hash]
    K --> M

    M --> N{Human QA<br/>spot-check audit log +<br/>folder structure}
    N -- Issues --> B
    N -- Pass --> O[Share output folder with tax agent<br/>via cloud share link<br/>unredacted originals - validation purpose]

    O --> P[Excel summary per person<br/>figures in agent's required format<br/>NEXT BUILD]
    P --> Q[Agent correspondence<br/>drafted with masked account digits<br/>human reviews and sends<br/>NEXT BUILD]
```

---

## 2. Classification Priority (why order matters)

```mermaid
flowchart LR
    A[File path + filename] --> B{1. Joint keywords?<br/>shared property,<br/>joint super deduction}
    B -- Yes --> C[Joint<br/>overrides any personal tag<br/>also present]
    B -- No --> D{2. Person-specific<br/>property keywords?}
    D -- Person A property --> E[Person A]
    D -- Person B property --> F[Person B]
    D -- No --> G{3. Generic initials tag?<br/>delimiter-aware matching:<br/>underscore, hyphen, space, dot}
    G -- One person only --> H[That person]
    G -- Both or neither --> I[Needs-Review<br/>flagged, not guessed]
```

Key design rules:

- **Joint beats personal.** A file tagged with a person's initials but also
  matching a joint-property keyword is classified joint — ownership follows
  the asset, not the person who saved the file.
- **Conflicts are surfaced, never guessed.** A file matching both people's
  tags goes to review. Silent misclassification into the wrong person's tax
  return is the costliest failure mode.
- **Delimiter-aware tag matching.** Initials glued with underscores
  (`XX_Invoice.pdf`) match; substrings inside words (initials inside an
  unrelated word) do not. Standard regex word-boundaries fail on
  underscores, so explicit delimiters are used.

---

## 3. Privacy Controls in This Pipeline

```mermaid
flowchart TD
    A[Raw documents<br/>cloud-synced folders] -->|COPY only<br/>originals never modified| B[Reorganised output]
    B -->|Cloud share link| C[Tax agent<br/>unredacted - validation purpose]

    A -.->|NEVER| D[Git repository]
    B -.->|NEVER| D
    E[Scripts + this doc only] --> D

    F[Any AI/cloud analysis<br/>e.g. categorisation assistance] --> G[Local redaction first<br/>TFN, BSB, ABN fully redacted<br/>account and employee numbers<br/>partially masked - last digits kept]
    G --> H[Sanitised text only<br/>leaves the machine]
```

Controls, stated as rules:

1. **Repo contains code and documentation only.** `.gitignore` blocks all
   document formats and output folders; the local `config.json` (which
   contains real paths and classification keywords) is never committed.
2. **Copy, never move.** The reorganisation is non-destructive; sources are
   deleted by a human only after output verification.
3. **Full audit trail.** Every file's original location, destination,
   classification, and content hash is logged per run.
4. **Redaction before any cloud AI step.** A separate local script strips
   tax file numbers, bank identifiers, and addresses, and partially masks
   account-type numbers, before any content is used outside the machine.
5. **Agent communication convention.** Emails reference accounts by last
   digits only (rest masked); full documents are shared exclusively via the
   controlled cloud folder link, never as email attachments.

---

## 4. Current Status and Next Builds

| Stage | Status |
|---|---|
| Redaction script (PDF extraction + PII masking) | Done, tested |
| Scan / dedupe / reorganise across all roots | Done, first real run complete |
| Manual review of unclassified files | In progress (human task) |
| Second person's documents | Pending upload |
| Excel figure summary per person | Next build |
| Agent email drafting workflow (masked digits) | Next build |
