# LegacyLift

> AI-assisted modernisation of a legacy Java application — with test-backed safety at every step.

## Results

| Metric | Value |
|--------|-------|
| **Time saved** | 92.9 % (1.7 h with LegacyLift vs. 24 h manual estimate) |
| **Tests** | 41 → 71 |
| **Failures after migration** | 0 |
| **`javax.*` files** | 14 → 0 |

See [`reports/MIGRATION_REPORT.md`](reports/MIGRATION_REPORT.md) for the full breakdown.

---

## Description

LegacyLift demonstrates a repeatable, four-phase strategy for safely modernising a legacy Java
codebase using IBM Bob as the AI pair-programmer. In the **Explain** phase Bob reads the existing
source tree, maps its structure, and produces a plain-language summary of what the application
does and how it is wired together. In the **Protect** phase Bob generates a comprehensive JUnit 5
test suite that locks in the current observable behaviour — these tests become the safety net for
every subsequent change. In the **Migrate** phase Bob migrates the codebase from Java 8 + Spring
Boot 2.7.3 to Java 21 + Spring Boot 3.4.5 — replacing `javax.*` imports with `jakarta.*` and
upgrading build plugins — verified by re-running 71 characterization tests with 0 failures.
Finally, in the **Prove** phase Bob produces structured reports and dashboard metrics that show
exactly what changed, why it changed, and that the application still behaves identically — giving
stakeholders evidence they can act on.

---

## Folder Structure

```
LegacyLift/
├── legacy-app/          # spring-petclinic, migrated to Java 21 / Spring Boot 3.4.5
│   ├── src/             # Java source and test trees
│   ├── pom.xml          # Maven build descriptor
│   └── mvnw / mvnw.cmd  # Maven wrapper (no separate Maven install required)
├── reports/             # Generated analysis and migration reports (Markdown) + metrics.json
├── dashboard/           # Streamlit app — visualises code-quality metrics before vs. after
├── bob_sessions/        # Screenshots and task-summary exports from each Bob IDE session
├── converter/           # LegacyLift Converter: one-click zip migration tool (built with Claude Code, not Bob)
├── PROMPTS.md           # The exact IBM Bob prompts used for PetClinic
├── PROMPTS_TEMPLATE.md  # Generic Bob prompts for any Java / Spring project
├── README.md            # This file
├── DATA_SOURCES.md      # Provenance of every data source used in the project
└── .gitignore           # Excludes build artefacts, IDE files, Python envs, and OS noise
```

---

## Prerequisites

| Tool | Minimum version | Notes |
|------|-----------------|-------|
| **JDK** | 11 | JDK 8 also works; the project targets Java 8 bytecode |
| **Maven wrapper** | bundled | `./mvnw` / `mvnw.cmd` ships in `legacy-app/` — no separate install needed |
| **Python** | 3.10 | Required only for the Streamlit dashboard |
| **Streamlit** | 1.30 | `pip install streamlit` |
| **IBM Bob IDE** | latest | Used to run the Explain → Protect → Migrate → Prove workflow |

> **`JAVA_HOME`** must point to your JDK before running `mvnw`.  
> Example (Windows PowerShell):
> ```powershell
> $env:JAVA_HOME = "C:\path\to\jdk-11"
> $env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
> ```

---

## Building the Legacy App

### Compile and run all tests

```powershell
# Windows
cd legacy-app
.\mvnw.cmd clean test
```

```bash
# macOS / Linux
cd legacy-app
./mvnw clean test
```

A successful run prints:

```
[INFO] Tests run: 40, Failures: 0, Errors: 0, Skipped: 1
[INFO] BUILD SUCCESS
```

### Skip tests (compile only)

```bash
./mvnw clean package -DskipTests
```

### Run the application

```bash
./mvnw spring-boot:run
# Open http://localhost:8080
```

---

## Dashboard

Visualises migration metrics, coverage trends, before/after comparisons, and Bob session evidence.

```powershell
# 1 – Create a virtual environment (first time only)
python -m venv .venv

# 2 – Install dependencies (first time only)
.venv\Scripts\python.exe -m pip install -r dashboard/requirements.txt

# 3 – Run the dashboard
.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

The app opens at **http://localhost:8501**.

---

## LegacyLift Converter (companion tool)

A one-click web tool in [`converter/`](converter/): upload a legacy Maven + Spring Boot 2.x
project as a `.zip` and download it migrated to Java 21 + Spring Boot 3, with a report proving
the tests still pass. It packages the **mechanical** part of the workflow (OpenRewrite + fixes
learned in this project).

> **Transparency:** the converter was built with **Claude Code, not IBM Bob**. Everything else in
> LegacyLift (analysis, characterization tests, migration, reports, dashboard) was done with
> IBM Bob, as shown in [`bob_sessions/`](bob_sessions/).

```powershell
cd converter
.\start.bat
```

Measured on the included samples: Spring PetClinic migrated with all 41 original tests passing;
the Spring JPA guide in about 3 minutes. See [`converter/README.md`](converter/README.md).

---

## Bob IDE Usage

All AI-assisted work in this project is driven from the **IBM Bob IDE**. Bob is used to:

- **Explain** — read and summarise the legacy source tree (`legacy-app/src/`)
- **Protect** — generate and validate a JUnit 5 test suite
- **Migrate** — apply refactors with instant test-feedback
- **Prove** — produce reports saved to `reports/`

### Session screenshots

Screenshots of each Bob session are saved in [`bob_sessions/`](bob_sessions/):

```
bob_sessions/
├── legacylift_task01_setup_explain_protect_overview.png   # Prompts 0-2: setup, Explain, Protect
├── legacylift_task01_setup_explain_protect_summary.png
├── legacylift_task03_migration_summary.png                # Prompt 3: Migrate + Prove
├── legacylift_task05_migration_report_summary.png         # Prompt 5: migration report
├── legacylift_task06_dashboard_overview_groupmate.png     # Prompt 6: dashboard
├── legacylift_task07_dashboard_fix_summary_groupmate.png  # Prompt 7: dashboard fixes
└── legacylift_task08_docs_fix_summary_groupmate.png       # Prompt 8: documentation fixes
```

These screenshots form an **audit trail** — reviewers and judges can trace every AI-assisted
decision back to a specific Bob task without re-running the workflow.

---

## Data Sources

See [`DATA_SOURCES.md`](DATA_SOURCES.md) for full provenance details, including the exact commit
hash and licence of the pinned `spring-petclinic` snapshot.

---

## Licence

The LegacyLift scaffolding (this repo) is released under **MIT**.  
The pinned `legacy-app/` source is from [spring-petclinic](https://github.com/spring-projects/spring-petclinic)
and is licensed under the **Apache License 2.0** — see [`legacy-app/LICENSE.txt`](legacy-app/LICENSE.txt).
