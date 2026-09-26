# LegacyLift Converter

Upload a **legacy Maven + Spring Boot 2.x** project as a `.zip` and get it back on
**Java 21 + Spring Boot 3.x**, with a report that proves the tests still pass.

> **How this tool was built.** Unlike the main LegacyLift workflow (where IBM Bob did the
> analysis, test generation, migration and reports, see `../bob_sessions/`), this converter was
> written with **Claude Code**, not IBM Bob. It is a companion tool that packages the
> *mechanical* part of the migration (OpenRewrite + known fixes) into one click. The parts that
> need understanding (explaining the code and writing characterization tests) remain IBM Bob's
> job in LegacyLift.

It is **rule-based, no AI**: it uses [OpenRewrite](https://docs.openrewrite.org) (Spring's
official migration recipes) plus fixes learned from real migrations.

## How it works

| Step | What happens |
|---|---|
| 1. Extract | Unzips safely, finds `pom.xml`, reads Java and Spring Boot versions, counts `javax` EE imports |
| 2. Baseline | Builds and tests the **original** project (JDK 17, then 11, 8). Stops if the original is broken |
| 3. OpenRewrite | Runs `UpgradeSpringBoot_3_x` + `UpgradeToJava21` (javax → jakarta, versions, properties, APIs) |
| 4. Known fixes | JaCoCo, Maven wrapper, MySQL driver, git-commit-id plugin, JAXB, formatter versions |
| 5. Verify | Builds and tests the **migrated** project on JDK 21 |
| 6. Prove | Checks that test logic did not change, writes report, patch, metrics, zip |

Result: **SUCCESS** (all tests pass, test logic unchanged), **PARTIAL** (compiles, some tests
fail or test logic changed) or **FAILED** (does not compile; the report lists the errors).

## Requirements (Windows)

```powershell
winget install --id EclipseAdoptium.Temurin.21.JDK -e
winget install --id EclipseAdoptium.Temurin.17.JDK -e
winget install --id Python.Python.3.12 -e
winget install --id Git.Git -e
```

Maven is not required: the project's `mvnw` is used, or Apache Maven is downloaded once to
`%USERPROFILE%\.legacylift`. An internet connection is needed for Maven dependencies.

## Run

**Web app**

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Open http://localhost:8501, upload the zip, click **Convert**, download the result.

**Command line**

```powershell
python converter.py C:\path\to\old-project.zip --java 21 --boot 3.4
```

Output goes to `%LOCALAPPDATA%\LegacyLift\work\<project>-<timestamp>\`: `*-migrated.zip`, `MIGRATION_REPORT.md`,
`migration.patch`, `metrics.json`, `build.log`.

## Limits

- Maven only (no Gradle yet), single-module projects work best.
- Custom compile errors are not auto-fixed; the report lists them for manual fixing.
- It proves behaviour only as far as the project's **existing tests** go. For code with few
  tests, write characterization tests first (see LegacyLift `PROMPTS_TEMPLATE.md`).
- Formatting and checkstyle gates are skipped during conversion; run the formatter afterwards.
- The first run downloads OpenRewrite recipes and can take 10+ minutes.
- Building a project executes its code. Only convert projects you trust.
