# LegacyLift

> AI-assisted modernisation of a legacy Java application — with test-backed safety at every step.

## Description

LegacyLift demonstrates a repeatable, four-phase strategy for safely modernising a legacy Java
codebase using IBM Bob as the AI pair-programmer. In the **Explain** phase Bob reads the existing
source tree, maps its structure, and produces a plain-language summary of what the application
does and how it is wired together. In the **Protect** phase Bob generates a comprehensive JUnit 5
test suite that locks in the current observable behaviour — these tests become the safety net for
every subsequent change. In the **Migrate** phase Bob applies incremental, targeted refactors
(dead-code removal, naming improvements, pattern upgrades, dependency modernisation) one step at a
time, re-running the test suite after each change to surface regressions immediately. Finally, in
the **Prove** phase Bob produces structured reports and dashboard metrics that show exactly what
changed, why it changed, and that the application still behaves identically — giving stakeholders
evidence they can act on.

---

## Folder Structure

```
LegacyLift/
├── legacy-app/          # Pinned snapshot of spring-petclinic (Boot 2.7.3 / Java 8 target)
│   ├── src/             # Java source and test trees
│   ├── pom.xml          # Maven build descriptor
│   └── mvnw / mvnw.cmd  # Maven wrapper (no separate Maven install required)
├── reports/             # Generated analysis and refactoring reports (Markdown, HTML, DOCX)
├── dashboard/           # Streamlit app — visualises code-quality metrics before vs. after
├── bob_sessions/        # Screenshots and task-summary exports from each Bob IDE session
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

## Bob IDE Usage

All AI-assisted work in this project is driven from the **IBM Bob IDE**. Bob is used to:

- **Explain** — read and summarise the legacy source tree (`legacy-app/src/`)
- **Protect** — generate and validate a JUnit 5 test suite
- **Migrate** — apply refactors with instant test-feedback
- **Prove** — produce reports saved to `reports/`

### Session screenshots

After completing each Bob task, export or screenshot the task summary panel and save it to
[`bob_sessions/`](bob_sessions/). File names should follow the convention:

```
bob_sessions/
├── 01_explain_source_map.png
├── 02_protect_test_generation.png
├── 03_migrate_rename_refactor.png
└── 04_prove_report.png
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
