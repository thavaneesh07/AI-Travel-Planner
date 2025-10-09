# AI Travel Planner – Phase 2 Work Distribution & Visual Workflow

Here’s a visual version of the workflow using **Mermaid** diagrams, which can render directly in GitHub, VS Code, or any Mermaid live editor.

> **VS Code Users:** To render Mermaid diagrams in the Markdown preview, install the **"Markdown Preview Mermaid Support"** extension from the Extensions panel (`Ctrl+Shift+X`). After installation, open the Markdown preview (`Ctrl+Shift+V`) to see the diagram.

You can also view the diagram in a browser using [Mermaid Live Editor](https://mermaid.live/).

```mermaid
%% =====================================
%% AI Travel Planner – Phase 2 Workflow
%% =====================================

flowchart TD
    %% --- Define Roles ---
    subgraph NLP["Brunda (NLP Developer)"]
        NLPWork["Build nlp_parser.py & mock outputs"]
    end

    subgraph Backend["Backend Developer"]
        BackendWork["Build backend endpoints using mock JSON"]
    end

    subgraph Frontend["Frontend Developer"]
        FrontendWork["Build UI using dummy JSON"]
    end

    %% --- Shared & Integration Stages ---
    API["Define Common API Contract\n(/api/parse, /api/itineraries, /api/itineraries/{id})"]
    Integration["Integrate NLP parser into backend\nConnect frontend to real API"]
    Testing["End-to-end testing\nBackend, Frontend, NLP"]

    %% --- Workflow Connections ---
    API --> NLPWork
    API --> BackendWork
    API --> FrontendWork

    NLPWork --> Integration
    BackendWork --> Integration
    FrontendWork --> Integration

    Integration --> Testing

    %% --- Styling Section ---
    style NLPWork fill:#003366,stroke:#ffffff,color:#ffffff
    style BackendWork fill:#1a4d2e,stroke:#ffffff,color:#ffffff
    style FrontendWork fill:#7a1a4d,stroke:#ffffff,color:#ffffff
    style API fill:#222222,stroke:#ffffff,color:#ffffff
    style Integration fill:#2b6cb0,stroke:#ffffff,color:#ffffff
    style Testing fill:#14532d,stroke:#ffffff,color:#ffffff

    %% --- Graph Background & Font ---
    classDef default font-family:Arial,fill:#2f2f2f,color:#fff,stroke:#fff;
```
