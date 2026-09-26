# LegacyLift Converter – Demo Video Script

**Length:** ~2.5 minutes · **Narration:** English · **Resolution:** 1920×1080

---

## Before you record

- [ ] **Warm up once.** Convert `samples\03-data-jpa-boot2.7.0.zip` one time before recording.
      The first run downloads OpenRewrite recipes (10+ minutes). After that, the same sample
      converts in about 3 minutes.
- [ ] Close notifications and other apps. Stop any Google Meet screen sharing.
- [ ] Start the tool: double-click `start.bat` (or run `start.ps1`). Browser opens http://localhost:8501.
- [ ] Have File Explorer open at `E:\Project\legacylift-converter\samples\`.
- [ ] Optional: open the old and new `Customer.java` side by side for Scene 5
      (old: inside the sample zip, new: inside the downloaded migrated zip).

**Recommended sample for the video:** `03-data-jpa-boot2.7.0.zip` (small, fast, shows
`javax.persistence` → `jakarta.persistence`).
**Bigger example to mention:** `01-petclinic-boot2.7.3.zip` (41 tests, 14 javax files).

---

## Scene 1 — Problem (0:00–0:15)
**Screen:** The tool's start page.

> "Thousands of Java applications still run on Java 8 and Spring Boot 2, which no longer get
> free security updates. Upgrading them by hand takes days. This is LegacyLift Converter."

---

## Scene 2 — Upload (0:15–0:35)
**Screen:** Left sidebar (Target Java 21, Spring Boot 3.4, installed JDKs) → drag
`03-data-jpa-boot2.7.0.zip` into the upload box → click **Convert ▶**.

> "You upload a legacy project as a zip file and choose the target: Java 21 and Spring Boot 3.4.
> The tool checks that the right JDKs are installed, then starts."

---

## Scene 3 — The six steps (0:35–1:15)
**Screen:** The progress box showing steps 1/6 → 6/6.
**Editing:** Speed up or cut the waiting; keep each step label visible for a second.

> "First it detects the project: Java 1.8 and Spring Boot 2.7.
> Then it builds and tests the ORIGINAL project, so we know what 'working' means before we touch anything.
> Then OpenRewrite, Spring's official rule-based migration engine, upgrades the code: javax to
> jakarta, dependency versions, configuration.
> Next, the tool applies fixes that OpenRewrite misses, learned from real migrations, like the
> Maven wrapper and the JaCoCo version.
> Finally it builds and tests the MIGRATED project on Java 21."

---

## Scene 4 — Result (1:15–1:45)
**Screen:** Green SUCCESS banner → KPI row (Java 21 from 1.8, Spring Boot 3.4.x from 2.7.0,
Tests passing, javax files 0) → blue "Test integrity" message.

> "Success. The project now runs on Java 21 and Spring Boot 3.4, every test passes, and there
> are no old javax imports left.
> And this line matters most: the tool proves it did not change any test logic. So passing tests
> mean the behaviour is really preserved."

---

## Scene 5 — Download and proof (1:45–2:15)
**Screen:** Click **Migrated project (.zip)** → expand **Report** → scroll to "Changed files" →
(optional) old vs new `Customer.java` showing `import javax.persistence` → `import jakarta.persistence`.

> "You download the migrated project, a readable report, a diff and a metrics file.
> Here you can see exactly what changed, file by file."

**Optional line (bigger project):**

> "On the Spring PetClinic application, with 41 tests and 14 files to migrate, it produced the same
> result: all 41 tests passing on Java 21."

---

## Scene 6 — Close (2:15–2:30)
**Screen:** Tool start page or the report.

> "LegacyLift Converter: upload a legacy project, get it back on modern Java, with proof that
> nothing broke."

---

## Numbers you can say (measured on this computer)

| Sample | Before | After | Tests | Result |
|---|---|---|---|---|
| 03-data-jpa | Java 1.8, Boot 2.7.0, 1 javax file | Java 21, Boot 3.4.13, 0 | 1 → 1 passing | ✅ SUCCESS, 196 s |
| 01-petclinic | Java 1.8, Boot 2.7.3, 14 javax files | Java 21, Boot 3.4.13, 0 | 41 → 41 (1 skipped both times) | ✅ SUCCESS |

Do **not** quote the PetClinic time (1474 s): that run included a first-time recipe download
and a network retry.

## Say it honestly

- It is **rule-based (OpenRewrite)**, not AI.
- It proves behaviour **only as far as the project's existing tests go**.
- **Maven only** for now; Gradle is future work.
- If the project does not compile after migration, the tool reports the errors instead of
  guessing a fix.

## Hackathon note

This converter was built outside IBM Bob. In the IBM Bob hackathon video, do **not** present it
as Bob's work. You can mention it in one sentence as a companion tool or future direction:

> "Next, we packaged the mechanical part of the workflow into a one-click converter, while Bob
> handles the parts that need understanding: explaining the code and writing tests."
