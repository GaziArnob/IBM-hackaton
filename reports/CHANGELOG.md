# Migration Changelog — Java 8 + Spring Boot 2.7.3 → Java 21 + Spring Boot 3.4.5

> Branch: `migration`  
> Migrated on: 2026-09-26  
> Engineer: IBM Bob (LegacyLift project)

---

## 1. Before / After Summary

| Metric | Before | After |
|--------|--------|-------|
| **Java version** | 1.8 (bytecode target; compiled with JDK 11) | **21** |
| **Spring Boot version** | 2.7.3 | **3.4.5** |
| **Hibernate version** | 5.6.x (via Boot BOM) | **6.6.x** (via Boot BOM) |
| **JaCoCo version** | 0.8.7 | **0.8.12** |
| **Files with `import javax.*`** (excl. `javax.cache`) | **14** | **0** |
| **`import javax.cache` (intentionally kept)** | 1 | 1 |

---

## 2. Changed Files

### Build

| File | Why it changed |
|------|---------------|
| `legacy-app/.mvn/wrapper/maven-wrapper.properties` | Upgraded Maven wrapper from 3.8.2 to **3.9.9** — Maven 3.8 is incompatible with JDK 21 |
| `legacy-app/pom.xml` | All build changes below (see sub-items) |

**pom.xml changes in detail:**

| Change | Reason |
|--------|--------|
| `spring-boot-starter-parent` 2.7.3 → **3.4.5** | Core upgrade target |
| `java.version` 1.8 → **21** | Target language / bytecode level |
| `jacoco.version` 0.8.7 → **0.8.12** | 0.8.7 cannot instrument Java 21 bytecode |
| `spring-format.version` 0.0.31 → **0.0.43** | 0.0.31 rejects Java 21 source formatting rules |
| `nohttp-checkstyle.version` 0.0.10 → **0.0.11** | Compatibility with Checkstyle 10 |
| `maven-checkstyle-plugin` 3.1.2 → **3.6.0** | Required for Checkstyle 10 |
| `checkstyle` 8.45.1 → **10.21.4** | 8.x does not support Java 21 syntax |
| `pl.project13.maven:git-commit-id-plugin` → `io.github.git-commit-id:git-commit-id-maven-plugin` **9.0.1** | Artifact relocated; old groupId/artifactId not published for Boot 3 |
| `mysql:mysql-connector-java` → `com.mysql:mysql-connector-j` | groupId/artifactId changed by MySQL upstream in 8.0.31 |
| `org.ehcache:ehcache` → `org.ehcache:ehcache` with `<classifier>jakarta</classifier>` | EhCache 3.10+ ships a Jakarta EE 10 jar alongside the legacy `javax` jar; Boot 3 requires the `jakarta` classifier |
| Added `jakarta.xml.bind:jakarta.xml.bind-api` | Required for `@XmlElement` / `@XmlRootElement` on `Vet` and `Vets` after JAXB was removed from the JDK in Java 11 |
| Removed `<java.source>` / `<java.target>` additional properties from `spring-boot-maven-plugin:build-info` | Boot 3 parent no longer sets `${maven.compiler.source}` / `${maven.compiler.target}` as legacy properties; the build-info goal would fail with a null value |

### Imports (javax → jakarta)

| File | Change |
|------|--------|
| `src/main/java/.../model/BaseEntity.java` | `javax.persistence.*` → `jakarta.persistence.*` |
| `src/main/java/.../model/NamedEntity.java` | `javax.persistence.*` → `jakarta.persistence.*` |
| `src/main/java/.../model/Person.java` | `javax.persistence.*`, `javax.validation.*` → `jakarta.*` |
| `src/main/java/.../owner/Owner.java` | `javax.persistence.*`, `javax.validation.*` → `jakarta.*` |
| `src/main/java/.../owner/OwnerController.java` | `javax.validation.Valid` → `jakarta.validation.Valid` |
| `src/main/java/.../owner/Pet.java` | `javax.persistence.*` → `jakarta.persistence.*` |
| `src/main/java/.../owner/PetController.java` | `javax.validation.Valid` → `jakarta.validation.Valid` |
| `src/main/java/.../owner/PetType.java` | `javax.persistence.*` → `jakarta.persistence.*` |
| `src/main/java/.../owner/Visit.java` | `javax.persistence.*`, `javax.validation.*` → `jakarta.*` |
| `src/main/java/.../owner/VisitController.java` | `javax.validation.Valid` → `jakarta.validation.Valid` |
| `src/main/java/.../vet/Specialty.java` | `javax.persistence.*` → `jakarta.persistence.*` |
| `src/main/java/.../vet/Vet.java` | `javax.persistence.*`, `javax.xml.bind.*` → `jakarta.*` |
| `src/main/java/.../vet/Vets.java` | `javax.xml.bind.*` → `jakarta.xml.bind.*` |
| `src/test/java/.../model/ValidatorTests.java` | `javax.validation.*` → `jakarta.validation.*` (test import only) |

**Not changed (intentional):**

| File | Reason |
|------|--------|
| `src/main/java/.../system/CacheConfiguration.java` | Uses `javax.cache.*` — the JCache API remains in the `javax.cache` package in Spring Boot 3 / EhCache 3.10; this import must NOT be renamed |

### API changes

| File | Change |
|------|--------|
| `legacy-app/pom.xml` | Removed null `${maven.compiler.source}` / `${maven.compiler.target}` from `build-info` additional properties — the only API-level breakage caused by the Boot 3 parent change |

### Config

No `application.properties` values were changed. All existing keys are valid in Spring Boot 3.4.5.  
`spring.jpa.open-in-view=true` is kept as-is (still valid in Boot 3 — not changed per task rules).

---

## 3. Test Results After Migration

| Metric | Value |
|--------|-------|
| **Tests run** | 71 |
| **Passed** | 70 |
| **Skipped** | 1 (intentional `@Disabled` in `CrashControllerTests`) |
| **Failures** | 0 |
| **Errors** | 0 |

### Coverage (post-migration)

| Class | Instruction | Branch | Line |
|-------|-------------|--------|------|
| `Owner` | 100 % | 100 % | 100 % |
| `PetValidator` | 100 % | 100 % | 100 % |
| `Visit` | 100 % | N/A | 100 % |
| `VisitController` | 100 % | 100 % | 100 % |
| `OwnerController` | 100 % | 100 % | 100 % |
| `PetController` | 100 % | 83.3 % | 100 % |
| **Overall** | **98.2 %** | **96.8 %** | **97.6 %** |

---

## 4. Failing Tests

**None.** All 70 executing tests pass on Java 21 + Spring Boot 3.4.5.

> Note: Mockito prints a self-attachment warning (`Mockito is currently self-attaching to enable the
> inline-mock-maker…`) on JDK 21. This is a warning only — it does not affect test results and will
> be resolved by adding the Mockito agent to the JVM args in a future step.

---

## 5. Files NOT Changed

The following files were deliberately left unmodified to comply with the strict rules:

- All test assertions and expected values
- All `@MockBean` annotations (deprecated in Boot 3.4 but still functional)
- `src/main/resources/application.properties` (all keys remain valid)
- All Gradle files (`build.gradle`, `gradlew`, `gradlew.bat`, `settings.gradle`)
- `src/main/java/.../system/CacheConfiguration.java` source logic (only noted that `javax.cache` import is intentionally retained)
