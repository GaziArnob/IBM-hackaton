# LegacyLift – Bob IDE Prompts (from zero)

Solo plan, 40 Bobcoins. Use **Agent mode** for every prompt.
One prompt = one Bob task. After each task, save the task summary screenshot to `bob_sessions/`.
Replace anything in `[SQUARE BRACKETS]` before sending.

| # | Prompt | Coins (approx) | Screenshot name |
|---|---|---|---|
| 0 | Project setup | ~4 | `legacylift_task00_project_setup_summary.png` |
| 1 | Explain | ~5 | `legacylift_task01_architecture_summary.png` |
| 2 | Tests + coverage | ~9 | `legacylift_task02_characterization_tests_summary.png` |
| 3 | Migrate | ~10 | `legacylift_task03_migration_summary.png` |
| 3B | Build errors (only if needed) | ~3 | `legacylift_task03b_build_fix_summary.png` |
| 4 | Test failures (only if needed) | ~3 | `legacylift_task04_test_fix_summary.png` |
| 5 | Report | ~2 | `legacylift_task05_migration_report_summary.png` |
| 6 | Dashboard (optional) | ~3 | `legacylift_task06_dashboard_summary.png` |
| — | Reserve | ~1 | — |

---

## STEP 0 – Manual, no Bob (no coins)

Do these yourself before Prompt 0:

1. Install: IBM Bob IDE (v2.0.2 or later), Git, JDK 8 (or 11), JDK 21, Maven, Python 3.
2. Open Bob IDE → sign in with your IBMid.
3. Settings → switch to the hackathon account `ibm-coding-challenge-uat`, region `us-east`.
4. Create an empty folder `E:\Project\Hackathon\LegacyLift` and open it in Bob IDE (File → Open Folder).
5. Create an empty public GitHub repository named `LegacyLift` and copy its URL.
6. Switch the Bob chat to **Agent mode**.

---

## Prompt 0 – Project setup

```
I am building "LegacyLift", a hackathon project that modernizes a legacy Java application with test-backed safety. The current folder is empty. Set up the project from scratch.

1. Create this structure:
   - `legacy-app/` (will contain the legacy Java project)
   - `reports/` (generated documents)
   - `dashboard/` (Streamlit app, later)
   - `bob_sessions/` (screenshots of Bob task summaries; add a `.gitkeep`)
   - `README.md`, `DATA_SOURCES.md`, `.gitignore` (Java, Maven, IntelliJ, VS Code, Python, OS files)

2. Clone https://github.com/spring-projects/spring-petclinic.git into `legacy-app/`.
   Using `git log -- pom.xml`, find the most recent commit where pom.xml uses Java 8 (`java.version` 1.8) and Spring Boot 2.x. Check out that commit, then delete `legacy-app/.git` so it becomes part of our repository.

3. Check which JDKs are installed (`java -version`, and JAVA_HOME). Build the legacy app with the oldest JDK available (8 or 11) using `mvn clean test`. If the build fails, find the cause and tell me the fix; do not upgrade the project yet.

4. Write `DATA_SOURCES.md` with: repository URL, exact commit hash and date, licence (read the LICENSE file), today's date, and one line on how it is used.

5. Write `README.md` with: project name, one-paragraph description (Explain → Protect → Migrate → Prove), folder structure, prerequisites, how to build the legacy app, and a section "Bob IDE usage" explaining that task screenshots are in `bob_sessions/`.

6. Initialize git, commit everything with message "Initial project setup", add the remote `[YOUR GITHUB REPO URL]` and push to `main`.

At the end, report: chosen commit hash, Java and Spring Boot versions of the legacy app, build result, and number of existing tests.
```

---

## Prompt 1 – Explain (architecture)

```
Analyze the legacy Java application in `legacy-app/` and create `reports/ARCHITECTURE.md` containing:

1. Overview: what the application does, in 5-8 sentences.
2. Tech stack: Java version, Spring Boot version, build tool, database, and all major libraries with their current versions.
3. Module map: a table of every package with its responsibility and key classes.
4. Dependency diagram: a Mermaid `graph TD` diagram showing how the packages depend on each other.
5. Request flow: how one HTTP request travels from controller to database for the "owner" feature.
6. Migration inventory: every item that must change to reach Java 21 and Spring Boot 3 (javax imports, deprecated APIs, old configuration properties, outdated dependencies). Give file paths.
7. Risk list: rank migration risks as High / Medium / Low with one-line reasons.
8. Test targets: which classes in the `owner` and `visit` features most need characterization tests before migration, and why.

Do not modify any source code. Use real file and class names from this repository.
Commit with message "Add architecture analysis" and push.
```

---

## Prompt 2 – Protect (tests + coverage)

```
Read `reports/ARCHITECTURE.md`, especially sections 6-8. Then do the following in `legacy-app/`:

1. Add the JaCoCo Maven plugin to `pom.xml` (prepare-agent + report goals, bound to the test phase). Run `mvn clean test` and record the BASELINE line and branch coverage from `target/site/jacoco/index.html`.

2. Write JUnit characterization tests for the `owner` and `visit` features. The goal is to lock in the CURRENT behavior before migration, not ideal behavior.
   - Controllers: use MockMvc; assert view names, model attributes, redirects, validation errors and HTTP status codes.
   - Data access: test save, find by id, last-name search (full, partial, no match), and visit creation.
   - Use Mockito only where a real dependency is impractical.
   - If current behavior looks wrong, still assert what it does now and add the comment `// CHARACTERIZATION: current behavior, not necessarily correct`.
   - Use descriptive test names, e.g. `findOwnerByLastName_partialMatch_returnsAllMatchingOwners`.
   - Use the same JUnit version the project already uses.
   - Do not change any production code.

3. Run `mvn clean test` and fix any failing TEST until all pass. Record the NEW coverage.

4. Create `reports/COVERAGE.md` with a table: metric | baseline | after characterization tests, plus the number of tests added per class.

Commit with message "Add characterization tests and coverage baseline" and push.
```

---

## Prompt 3 – Migrate

```
Create a new git branch `migration` and migrate `legacy-app/` to Java 21 and the latest stable Spring Boot 3.x.

Use `reports/ARCHITECTURE.md` section 6 (Migration inventory) as your checklist.

1. Update `pom.xml`: Java 21, Spring Boot 3 parent, compatible versions of all dependencies and plugins (keep JaCoCo, update to a Java 21 compatible version).
2. Replace `javax.*` imports with `jakarta.*` wherever required (persistence, validation, servlet, annotation).
3. Replace deprecated or removed APIs and migrate any JUnit 4 tests to JUnit 5 (imports and annotations only).
4. Update configuration properties renamed or removed in Spring Boot 3.
5. Work feature by feature: `owner`, then `visit`, then everything else.

Strict rules:
- Do NOT change any test assertion or expected value, and do NOT delete any test. The tests are the proof that behavior is preserved. Only imports and test setup code may change.
- No new features and no refactoring beyond what the migration requires.

Build with JDK 21 using `mvn clean compile` and fix all compile errors. Then run `mvn clean test` and tell me how many tests pass and fail — do not fix failing tests yet.

Create `reports/CHANGELOG.md`: one line per changed file explaining why. Commit with message "Migrate to Java 21 and Spring Boot 3" and push the `migration` branch.
```

---

## Prompt 3B – Build errors (only if the build still fails)

```
The build on the `migration` branch still fails. Full output of `mvn clean compile`:

[PASTE THE FULL ERROR OUTPUT HERE]

Group the errors by root cause and fix all of them in one pass. Do not change test assertions. Run `mvn clean compile` again, confirm success, update `reports/CHANGELOG.md`, commit and push.
```

---

## Prompt 4 – Prove (fix failing tests, only if needed)

```
On the `migration` branch these characterization tests fail:

[PASTE THE FAILING TEST NAMES AND ERROR MESSAGES HERE]

These tests describe the behavior BEFORE migration, so each failure means the migration changed behavior.

For each failure:
1. Explain the root cause in one or two sentences.
2. Fix the PRODUCTION code so the original behavior is restored.
3. Only change a test if the failure is purely technical (import or setup API), never an expected value.

Run `mvn clean test` until all tests pass, then record the final coverage.
Append to `reports/COVERAGE.md` a section "After migration" with coverage and pass rate, and a table: test name | root cause | fix applied.
Commit with message "Fix behavior regressions found by characterization tests" and push.
```

---

## Prompt 5 – Report

```
Create `reports/MIGRATION_REPORT.md` using the git diff between `main` and `migration`, and the files `reports/ARCHITECTURE.md`, `reports/COVERAGE.md` and `reports/CHANGELOG.md`.

My own measurements:
- Total time spent with LegacyLift: [H] hours
- Estimated manual time for the same work: [M] hours

The report must contain:
1. Summary (5 lines) of what was migrated and the result.
2. Before/after table: Java version, Spring Boot version, key dependency versions.
3. Metrics table: coverage (baseline / after tests / after migration), tests written, pass rate before and after fixes, time spent vs manual estimate, and time saved in percent.
4. What changed, grouped by category (build, imports, APIs, config) with file counts.
5. Regressions caught by the characterization tests and how they were fixed.
6. Remaining risks and untested areas.
7. Recommended next steps.

Use only facts from the repository and the numbers above. Do not invent any metric.
Also save the key numbers in `reports/metrics.json` (flat JSON, one key per metric).
Merge `migration` into `main`, commit and push.
```

---

## Prompt 6 – Dashboard (optional, skip if coins are low)

```
Create a single-file Streamlit app `dashboard/app.py` plus `dashboard/requirements.txt` for the LegacyLift demo.

It reads `reports/metrics.json`, `reports/ARCHITECTURE.md` and `reports/MIGRATION_REPORT.md` and shows:
1. Header: "LegacyLift – Legacy to Modern, with Tests as Proof".
2. The four stages Explain → Protect → Migrate → Prove as a row of status cards.
3. KPI tiles: coverage before/after, tests written, final pass rate, time saved %.
4. A bar chart comparing coverage baseline / after tests / after migration.
5. Before/after version table (Java, Spring Boot).
6. The Mermaid dependency diagram rendered from ARCHITECTURE.md (use streamlit-mermaid or show the code block if unavailable).
7. Expandable sections showing the full reports.

Keep it simple, no external services. Add run instructions to README.md (`pip install -r dashboard/requirements.txt` and `streamlit run dashboard/app.py`). Commit and push.
```

---

## Coin-saving rules

- One detailed prompt per step; never many short follow-ups.
- Paste all errors at once.
- If Bob's answer is wrong, list ALL problems in one message.
- Check remaining coins in Settings → General after every task.
- If coins run low: skip Prompt 6 (write the dashboard yourself or show the reports), then skip Prompt 5 (write the report yourself using the same structure).
