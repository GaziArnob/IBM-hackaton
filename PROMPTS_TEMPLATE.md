# LegacyLift – Reusable Prompt Template

Use these prompts in **IBM Bob IDE (Agent mode)** to modernize **any** legacy Java / Spring Boot project.
`PROMPTS.md` holds the exact prompts used for Spring PetClinic; this file is the generic version.

Replace every `{PLACEHOLDER}` before sending. Run the prompts **in order**, one Bob task per prompt.

| Placeholder | Example |
|---|---|
| `{REPO_URL}` | `https://github.com/acme/billing-service.git` |
| `{REF}` | a commit hash, tag or branch of the legacy version, e.g. `v1.4.2` |
| `{TARGET_JAVA}` | `21` |
| `{TARGET_BOOT}` | `3.4.5` (or "latest stable 3.x") |
| `{BUILD}` | `Maven wrapper (mvnw.cmd)` or `Gradle wrapper (gradlew.bat)` |

---

## Workflow at a glance

```
Prompt A  Setup      → legacy app builds, baseline recorded
Prompt B  Explain    → reports/ARCHITECTURE.md          ← YOU REVIEW
Prompt C  Protect    → characterization tests + COVERAGE.md   ← YOU REVIEW
Prompt D  Migrate    → migration branch + CHANGELOG.md
  D2      Build fix  → only if the build still fails
  E       Prove fix  → only if tests fail
Prompt F  Report     → MIGRATION_REPORT.md + metrics.json → dashboard
```

**Human review is part of the workflow.** In the PetClinic run, Bob's first analysis missed 4 of 14 files and gave one wrong recommendation. Check every report against the code before moving on.

---

## Prompt A – Setup

```
I am using the LegacyLift workflow to modernize a legacy Java application.

1. Create folders `legacy-app/`, `reports/`, `bob_sessions/` (with `.gitkeep`) if they do not exist.
2. Clone {REPO_URL} into `legacy-app/`, check out {REF}, then delete `legacy-app/.git` so it becomes part of this repository.
3. Detect the build tool, Java version, Spring/Spring Boot version and test framework from the build files. Check which JDKs are installed.
4. Build and run the existing tests with the JDK the project currently targets (or the closest available), using {BUILD}. Do not upgrade anything yet. If the build fails, find the cause and tell me the fix.
5. Record in `DATA_SOURCES.md`: repository URL, exact commit/ref and date, licence (read the LICENSE file), today's date, and how it is used.
6. Commit with message "Import legacy application" and push.

Report: current Java and framework versions, build result, number of existing tests (passed/failed/skipped).
```

**Check before continuing:** the legacy build is green. If not, fix that first; you cannot prove a migration on top of a broken baseline.

---

## Prompt B – Explain

```
Analyze the legacy application in `legacy-app/` and create `reports/ARCHITECTURE.md` with:

1. Overview: what the application does (5-8 sentences).
2. Tech stack: language/framework versions, build tool, database, major libraries with versions.
3. Module map: every package with its responsibility and key classes.
4. Dependency diagram: Mermaid `graph TD` of package dependencies.
5. Request flow: trace one important user-facing request from entry point to database.
6. Migration inventory for Java {TARGET_JAVA} + Spring Boot {TARGET_BOOT}: every `javax.*` import (use grep and list ALL files), removed/deprecated APIs, renamed configuration properties, outdated dependencies and build plugins (including coverage, formatting and checkstyle plugins). Give file paths.
7. Risk list: High / Medium / Low with one-line reasons.
8. Test targets: the 3-5 most business-critical features, which classes in them already have tests, and the exact gaps (methods/branches without tests).

Do not modify any source code. Use real file and class names. Commit "Add architecture analysis" and push.
```

**Check before continuing:**
- Run `grep -rn "import javax" legacy-app/src` yourself and compare with section 6.
- Remember: `javax.cache`, `javax.sql`, `javax.crypto`, `javax.net` and other JDK packages do **not** move to `jakarta`.

---

## Prompt C – Protect

```
Read `reports/ARCHITECTURE.md`, section 8 (Test targets).

STEP 1 – Baseline coverage. Make sure JaCoCo is configured (add it only if missing; if present keep its version for now). Run the tests with a coverage report and record instruction %, branch % and line % overall and for each target class. Record the number of existing tests.

STEP 2 – Write characterization tests ONLY for the gaps listed in section 8. They must lock in CURRENT behavior, not ideal behavior.
- Follow the style, test framework and license header of the existing tests.
- If current behavior looks wrong, still assert it and add `// CHARACTERIZATION: current behavior, not necessarily correct`.
- Descriptive test names (method_condition_expectedResult).
- Do NOT change production code. Do NOT modify or delete existing tests.

STEP 3 – Run any code formatter the build requires, then run all tests until green. If a NEW test fails, fix the TEST. Record the new coverage.

STEP 4 – Create `reports/COVERAGE.md`: baseline vs after table, tests added per class, list of CHARACTERIZATION tests with one line each, and a clear list of which tests are original and which were added by Bob.

Commit "Add characterization tests and coverage baseline" and push.
```

**Check before continuing:** open 2-3 new tests and compare with the production code. The tests should describe what the code really does.

---

## Prompt D – Migrate

```
Create a new git branch `migration` and migrate `legacy-app/` to Java {TARGET_JAVA} and Spring Boot {TARGET_BOOT}, using {BUILD} with JDK {TARGET_JAVA}.

Use `grep -rn "import javax" legacy-app/src` as the source of truth for imports, and `reports/ARCHITECTURE.md` section 6 as a checklist.

1. Build file: framework parent/BOM, Java version, and every plugin/dependency that does not support Java {TARGET_JAVA} or Spring Boot {TARGET_BOOT} (coverage, formatter, checkstyle, git-info, database drivers with renamed coordinates). Update the build wrapper if it fails on the new JDK.
2. Imports: `javax.persistence`, `javax.validation`, `javax.servlet`, `javax.annotation`, `javax.transaction`, `javax.xml.bind` → `jakarta.*`. Do NOT rename JDK packages or `javax.cache`.
3. Removed APIs: replace anything removed in Spring Boot 3 / Spring Security 6 / Hibernate 6 with the smallest possible change.
4. Configuration properties renamed or removed in Spring Boot 3.

STRICT RULES
- Do NOT change any test assertion or expected value, and do NOT delete or disable any test. Only imports and test setup code may change.
- No new features and no refactoring beyond what the migration requires.

Compile and fix all compile errors. Then run all tests ONCE with coverage and record run/passed/failed/skipped and coverage. Do NOT fix failing tests yet; list them with error messages.

Create `reports/CHANGELOG.md`: before/after versions table, javax file count before/after, one line per changed file grouped as Build / Imports / API / Config, the test result, and any failing tests.
Commit "Migrate to Java {TARGET_JAVA} and Spring Boot {TARGET_BOOT}" and push the `migration` branch.
```

---

## Prompt D2 – Build fix (only if the build still fails)

```
The build on the `migration` branch still fails. Full output:

[PASTE THE FULL ERROR OUTPUT]

Group the errors by root cause and fix all of them in one pass. Do not change test assertions. Rebuild, confirm success, update `reports/CHANGELOG.md`, commit and push.
```

---

## Prompt E – Prove fix (only if tests fail)

```
On the `migration` branch these characterization tests fail:

[PASTE FAILING TEST NAMES AND ERROR MESSAGES]

They describe the behavior BEFORE migration, so each failure means the migration changed behavior.
For each: explain the root cause, fix the PRODUCTION code to restore the original behavior, and only change a test if the failure is purely technical (import/setup), never an expected value.
Run all tests until green. Append to `reports/COVERAGE.md` a table: test | root cause | fix. Commit "Fix regressions found by characterization tests" and push.
```

**Check before continuing (important):** verify that test logic did not change:

```powershell
git diff main migration -- legacy-app/src/test
```
Only `import` lines and formatting may differ.

---

## Prompt F – Report and metrics

```
Create `reports/MIGRATION_REPORT.md` from `reports/ARCHITECTURE.md`, `reports/COVERAGE.md`, `reports/CHANGELOG.md` and the git diff between `main` and `migration`. Do NOT re-run the tests.

My numbers:
- Time with LegacyLift: [H] hours (from git history: first to last commit)
- Estimated manual time: [M] hours, broken down as: understanding [..] h + tests [..] h + migration and debugging [..] h + documentation [..] h (label it as an estimate)

Sections: summary; before/after versions; metrics (tests before/after, pass rate after migration, coverage baseline/after tests/after migration, time vs estimate, % saved); what changed (Build/Imports/API/Config with counts); regressions caught and fixed; remaining risks; next steps. Use only facts from the reports and my numbers.

Also create `reports/metrics.json` with exactly these keys: java_before, java_after, boot_before, boot_after, tests_before, tests_after, tests_failed_after_migration, instruction_cov_baseline, instruction_cov_after_tests, instruction_cov_after_migration, branch_cov_baseline, branch_cov_after_tests, branch_cov_after_migration, javax_files_before, javax_files_after, hours_with_legacylift, hours_manual_estimate, time_saved_percent.

Commit "Add migration report and metrics", merge `migration` into `main` (no fast-forward), push both branches.
```

With the same `metrics.json` keys, the LegacyLift dashboard (`dashboard/app.py`) can show the new project's results.

---

## Rules that keep it safe

1. **Legacy build must be green before Prompt C.**
2. **Tests before migration.** Never skip Prompt C.
3. **Tests are never changed to make them pass.** Verify with `git diff`.
4. **grep, not memory,** for the import inventory.
5. **Review every Bob report** against the code.
6. **Screenshot every Bob task summary** into `bob_sessions/` if you need usage evidence.
7. **Save Bobcoins:** one detailed prompt per step, paste all errors at once, open a New Task when context is above ~60-70%.

## Limits

- Designed for **Java + Spring / Spring Boot + Maven or Gradle** projects.
- Very large codebases: run Prompts C and D per module instead of all at once.
- The manual-time figure is always an estimate unless you time a manual run.
