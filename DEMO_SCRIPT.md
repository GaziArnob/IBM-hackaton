# LegacyLift – Demo Video Script

**Length:** ~4 minutes · **Language:** English narration · **Resolution:** 1920×1080

---

## Before you record (prep checklist)

- [ ] Close notifications, other chats, and any non-Bob AI extensions/tabs (keep the focus on IBM Bob).
- [ ] Increase editor font size (Ctrl + `=` two or three times) so code is readable in the video.
- [ ] Pull the latest code: `git pull`
- [ ] Open these tabs in Bob IDE, in this order:
  1. `README.md` (preview mode: Ctrl+Shift+V)
  2. `reports/ARCHITECTURE.md` (preview)
  3. `reports/COVERAGE.md` (preview)
  4. `legacy-app/src/test/java/org/springframework/samples/petclinic/owner/OwnerTests.java`
  5. `reports/CHANGELOG.md` (preview)
  6. `reports/MIGRATION_REPORT.md` (preview)
- [ ] Start the dashboard in a separate terminal and open http://localhost:8501:
  ```powershell
  .venv\Scripts\python.exe -m streamlit run dashboard/app.py
  ```
- [ ] **Pre-record the test run** (it takes 1–2 minutes; you will cut it down):
  ```powershell
  java -version
  cd legacy-app
  .\mvnw.cmd clean test
  ```
- [ ] Have the Bob task summary panel ready to open (Tasks → select task → click header).

**Recording tools:** OBS Studio, or Windows `Win + Alt + R` (Xbox Game Bar), or Clipchamp for editing.

---

## Scene-by-scene script

### Scene 1 — Hook (0:00–0:20)
**Screen:** Dashboard header and the KPI row.

> "Legacy Java applications run a lot of critical business software, but upgrading them is slow and risky. Nobody remembers what the code does, and there are few tests to catch mistakes.
> This is LegacyLift. With IBM Bob, we migrated a real Spring application from Java 8 to Java 21 in 1.7 hours, with zero failing tests."

---

### Scene 2 — The idea (0:20–0:40)
**Screen:** Dashboard pipeline row (Explain → Protect → Migrate → Prove), then the README "Results" table.

> "LegacyLift is a four-step workflow run by IBM Bob in agent mode: Explain the code, Protect it with tests, Migrate it, and Prove nothing broke.
> Our target is Spring PetClinic, an open-source app pinned at its last Java 8 and Spring Boot 2.7 version."

---

### Scene 3 — Explain (0:40–1:15)
**Screen:** `reports/ARCHITECTURE.md` — scroll to the Mermaid diagram (section 4), then the migration inventory (section 6), then "Summary of gaps" (section 8).

> "First, Bob reads the whole repository. It produces a module map, a dependency diagram, and traces a real request from controller to database.
> It lists everything blocking Java 21 and Spring Boot 3, ranked by risk.
> Most importantly, it compares the existing tests with the code and finds exactly where the gaps are. For example, the Owner domain logic and the PetValidator had no direct tests."

---

### Scene 4 — Protect (1:15–1:55)
**Screen:** `reports/COVERAGE.md` metrics table → `OwnerTests.java` (show one test with the `// CHARACTERIZATION` comment).

> "Before touching any code, Bob writes characterization tests. These tests record what the code does today, not what it should do.
> Bob added 30 tests, from 41 to 71, and pushed branch coverage of Owner and PetValidator to 100 percent.
> When the current behavior looks odd, Bob still locks it in and marks it, so the migration can't silently change it."

---

### Scene 5 — Migrate (1:55–2:35)
**Screen:** `reports/CHANGELOG.md` before/after table → scroll through the pom.xml changes and the javax → jakarta list.

> "Then Bob migrates the app on a separate branch: Spring Boot 2.7.3 to 3.4.5, Java 8 to 21, 14 files from javax to jakarta, plus JaCoCo, Checkstyle, the Maven wrapper and other plugins.
> We gave Bob one strict rule: you may not change a single test assertion. The tests are the judge."

---

### Scene 6 — Prove (2:35–3:10)
**Screen:** Pre-recorded terminal — `java -version` showing 21 → end of `mvnw clean test` showing `Tests run: 71, Failures: 0, Errors: 0, Skipped: 1` and `BUILD SUCCESS`.

> "Here is the proof. On Java 21, all 71 tests run. Zero failures.
> We also checked Bob's work ourselves: apart from imports and formatting, the test logic is identical before and after the migration. So this result means the behavior was preserved, not that the tests were adjusted."

**Optional (5–10 s):** Show the "Post-migration corrections" note at the top of `ARCHITECTURE.md`.

> "And we kept humans in the loop: our review caught places where Bob's first analysis was wrong, and we documented them."

---

### Scene 7 — Dashboard & evidence (3:10–3:40)
**Screen:** Dashboard → KPI row → coverage chart → time chart → click "Bob Evidence" tab and scroll through the screenshots. Then briefly open one Bob task summary panel in Bob IDE.

> "Everything is summarized in this dashboard, built from the report data: 92.9 percent time saved against a 24-hour manual estimate, 30 new tests, zero regressions.
> The Bob Evidence tab shows every Bob session. Two team members used 39 Bobcoins in total."

---

### Scene 8 — Close (3:40–4:00)
**Screen:** README top (title + Results table) or the dashboard header.

> "LegacyLift turns legacy migration from weeks of risky manual work into a repeatable workflow: explain, protect, migrate, prove.
> All prompts are in the repository, so any team can run it on their own legacy code. Thank you."

---

## Numbers to say (double-check before recording)

| Claim | Value | Source |
|---|---|---|
| Java / Spring Boot | 8 → 21 / 2.7.3 → 3.4.5 | CHANGELOG.md |
| Tests | 41 → 71 (+30 by Bob) | COVERAGE.md |
| Result after migration | 70 passed, 1 skipped, 0 failures | MIGRATION_REPORT.md |
| Owner / PetValidator branch coverage | 100% / 100% | COVERAGE.md |
| javax files | 14 → 0 | CHANGELOG.md |
| Time | 1.7 h vs 24 h estimate → 92.9% saved | metrics.json |
| Bobcoins | 35.44 + 3.79 = 39.23 | bob_sessions/ |

**Always say "estimate" for the 24 hours.** It is not a measured number.

## Editing tips

- Cut the Maven download and test-running wait; keep only `java -version` and the final summary lines.
- Zoom in (crop) on the terminal result and the KPI tiles.
- Add a title card at the start: "LegacyLift – IBM Bob 2.0 Hackathon" and the team name.
- Add the GitHub link on the last frame.
- Export as MP4, 1080p. Target under 5 minutes.
