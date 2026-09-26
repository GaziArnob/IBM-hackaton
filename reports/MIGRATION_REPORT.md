# LegacyLift Migration Report

> Project: Spring PetClinic modernisation  
> Branch: `migration` → merged to `main`  
> Date: 2026-09-26  
> Workflow: **Explain → Protect → Migrate → Prove**

---

## 1. Summary

The legacy Spring PetClinic application — a veterinary practice management system running on
Java 8 bytecode and Spring Boot 2.7.3 — was successfully migrated to **Java 21 and Spring Boot
3.4.5** using the LegacyLift workflow powered by IBM Bob. The four-phase workflow (Explain the
codebase, Protect it with characterization tests, Migrate the code and build, Prove with a full
green test run) required **1.7 hours** of elapsed time. The characterization safety net grew from
41 original tests to **71 tests**, all of which passed on the new platform with **zero regressions**.
The entire `javax.persistence`, `javax.validation`, and `javax.xml.bind` namespace was replaced
with `jakarta.*` across 13 production source files and 1 test file, and 13 build-level items in `pom.xml` were updated.
No production logic was altered; only imports, build descriptors, and code formatting changed.

---

## 2. Before / After

| Property | Before | After |
|----------|--------|-------|
| **Java version** | 1.8 (bytecode target; compiled with JDK 11) | **21** |
| **Spring Boot** | 2.7.3 | **3.4.5** |
| **Hibernate** | 5.6.x (via Boot BOM) | **6.6.x** (via Boot BOM) |
| **JaCoCo** | 0.8.7 | **0.8.12** |
| **Maven wrapper** | 3.8.2 | **3.9.9** |
| **Files with `import javax.*`** (excl. `javax.cache`) | **14** | **0** |
| **`import javax.cache`** (intentionally kept) | 1 | 1 |

---

## 3. Metrics

### Test suite

| Metric | Value |
|--------|-------|
| Original upstream tests | 41 |
| Characterization tests added by Bob (Protect phase) | +30 |
| **Total tests after migration** | **71** |
| Executed (not skipped) | 70 |
| **Passed** | **70** |
| **Failures** | **0** |
| **Errors** | **0** |
| Skipped | 1 (original `@Disabled` in `CrashControllerTests` — unchanged) |

### Coverage progression

| Metric | Baseline (41 tests, JDK 11) | After characterization tests (71 tests, JDK 11) | After migration (71 tests, JDK 21) |
|--------|-----------------------------|--------------------------------------------------|-------------------------------------|
| **Instruction coverage** | 97.0 % | 98.3 % | **98.2 %** |
| **Branch coverage** | 88.7 % | 96.8 % | **96.8 %** |
| **Line coverage** | 96.3 % | 97.5 % | **97.6 %** |

### Key coverage improvements from characterization tests

| Class | Branch coverage before | Branch coverage after tests |
|-------|------------------------|-----------------------------|
| `Owner` | 83.3 % | **100 %** |
| `PetValidator` | 87.5 % | **100 %** |
| `PetController` | 75.0 % | 83.3 % |

### Time

| Measure | Value |
|---------|-------|
| **Time with LegacyLift** | **1.7 hours** (git history: first commit 14:08 → migration commit 15:48, 2026-09-26) |
| **Estimated manual time** _(estimate — see note)_ | **24 hours** (understand codebase 4 h + write 30 characterization tests 8 h + migrate 14 import files and 13 build items incl. debugging 10 h + documentation 2 h) |
| **Time saved** | **92.9 %** (= (24 − 1.7) / 24) |

> **Note:** The manual estimate of 24 hours is an informed approximation based on the scope of work
> observed: 23 Java source files read and analysed, 30 test methods written, 14 import files
> migrated, 13 `pom.xml` items updated, and 3 structured reports authored. Actual manual time would
> vary with team experience.

---

## 4. Prove Stage

All 71 characterization tests were re-run on **Java 21 + Spring Boot 3.4.5** with **zero
regressions**. No production code fix was required: every test that passed before migration passed
after migration with identical assertions. The only changes made to test files were:

- `ValidatorTests.java`: two `import javax.validation.*` lines renamed to `import jakarta.validation.*`.
- Code formatting applied by `spring-javaformat:apply` (whitespace only).

No test assertion, expected value, `@MockBean`, or `@Disabled` annotation was altered.

---

## 5. What Changed

### Build (2 files, 13 `pom.xml` items)

| Item | Change |
|------|--------|
| `.mvn/wrapper/maven-wrapper.properties` | Maven 3.8.2 → 3.9.9 (JDK 21 compatibility) |
| `pom.xml` — Spring Boot parent | 2.7.3 → 3.4.5 |
| `pom.xml` — `java.version` | 1.8 → 21 |
| `pom.xml` — JaCoCo | 0.8.7 → 0.8.12 (Java 21 bytecode support) |
| `pom.xml` — spring-javaformat | 0.0.31 → 0.0.43 (Java 21 format rules) |
| `pom.xml` — nohttp-checkstyle | 0.0.10 → 0.0.11 (Checkstyle 10 compat) |
| `pom.xml` — maven-checkstyle-plugin | 3.1.2 → 3.6.0 |
| `pom.xml` — Checkstyle rules | 8.45.1 → 10.21.4 (Java 21 syntax) |
| `pom.xml` — git-commit-id plugin | `pl.project13.maven:git-commit-id-plugin:4.9.10` → `io.github.git-commit-id:git-commit-id-maven-plugin:9.0.1` |
| `pom.xml` — MySQL connector | `mysql:mysql-connector-java` → `com.mysql:mysql-connector-j` |
| `pom.xml` — EhCache | Added `<classifier>jakarta</classifier>` |
| `pom.xml` — JAXB API | Added `jakarta.xml.bind:jakarta.xml.bind-api` |
| `pom.xml` — build-info extra properties | Removed `java.source` / `java.target` (null in Boot 3 parent) |

### Imports (13 production files + 1 test file = 14)

| Namespace replaced | Files affected |
|--------------------|---------------|
| `javax.persistence.*` → `jakarta.persistence.*` | `BaseEntity`, `NamedEntity`, `Person`, `Owner`, `Pet`, `PetType`, `Visit`, `Specialty`, `Vet` (9 files) |
| `javax.validation.*` → `jakarta.validation.*` | `Person`, `Owner`, `Visit`, `OwnerController`, `PetController`, `VisitController` (6 files) |
| `javax.xml.bind.*` → `jakarta.xml.bind.*` | `Vet`, `Vets` (2 files) |
| `javax.validation.*` → `jakarta.validation.*` (test) | `ValidatorTests` (1 test file) |

**Not renamed:** `javax.cache.*` in `CacheConfiguration.java` — the JCache API remains in the `javax.cache` package in Spring Boot 3 / EhCache 3.10.

### API changes (1 item)

| File | Change |
|------|--------|
| `pom.xml` | Removed `${maven.compiler.source}` / `${maven.compiler.target}` from `spring-boot-maven-plugin:build-info` additional properties — these properties are null in the Boot 3 parent and caused a build failure |

### Config (0 files)

No `application.properties` values were changed. All keys are valid in Spring Boot 3.4.5.

---

## 6. Remaining Risks and Untested Areas

| Risk | Severity | Detail |
|------|----------|--------|
| `PetController` branch coverage at 83.3 % | Medium | 2 branches in `PetController` are not covered by tests |
| `@MockBean` deprecated in Spring Boot 3.4 | Low | All 4 test classes still use `@MockBean`; it continues to function but will be removed in a future Boot release — should be replaced with `@MockitoBean` when upgrading past 3.4 |
| `spring.jpa.open-in-view=true` | Low | Still valid in Boot 3; lazy-loading paths that work today will throw `LazyInitializationException` if this is ever set to `false` |
| Mockito self-attach warning on JDK 21 | Low | `Mockito is currently self-attaching to enable the inline-mock-maker` appears in test output; will stop working in a future JDK — requires adding Mockito as a `-javaagent` in Surefire config |
| Gradle build not migrated | Medium | `build.gradle` and associated files were not touched; the Gradle build will not compile on Java 21 with the current `plugins {}` block referencing Boot 2.7.3 — should be migrated or removed |

---

## 7. Recommended Next Steps

1. **Replace `@MockBean` with `@MockitoBean`** across the 4 affected test classes to remove the Boot 3.4 deprecation warning and future-proof the test suite.
2. **Configure Mockito as a JVM agent** in `maven-surefire-plugin` (`<argLine>-javaagent:...</argLine>`) to eliminate the self-attach warning and ensure compatibility with JDK 24+.
3. **Set `spring.jpa.open-in-view=false`** in `application.properties` and run the full test suite to verify there are no lazy-loading regressions in the codebase.
4. **Migrate or remove the Gradle build** — update `build.gradle` to Spring Boot 3.4.5 and Java 21, or delete it to avoid confusion about which build descriptor is canonical.
5. **Add branch coverage tests for `PetController`** — write a direct unit test for the `findPet` `@ModelAttribute` method covering the `petId == null` path to close the remaining 16.7 % branch gap.
