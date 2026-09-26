# Coverage Report — Characterization Test Baseline

> Generated: 2026-09-26  
> Tool: JaCoCo 0.8.7 (configured in `legacy-app/pom.xml`)  
> Build command: `mvnw.cmd clean test jacoco:report`  
> JDK: AdoptOpenJDK 11.0.11 (embedded in STM32CubeIDE)

---

## 1. Coverage Metrics — Baseline vs. After Characterization Tests

### Overall project

| Metric | Baseline | After characterization tests |
|--------|----------|------------------------------|
| **Instruction coverage** | 97.0 % | **98.3 %** |
| **Branch coverage** | 88.7 % | **96.8 %** |
| **Line coverage** | 96.3 % | **97.5 %** |
| **Total tests** | 41 | **71** |
| **Passed** | 40 | **70** |
| **Skipped** | 1 | 1 |
| **Failures / Errors** | 0 | 0 |

### Per-class coverage for the 6 targeted classes

| Class | Metric | Baseline | After |
|-------|--------|----------|-------|
| `Owner` | Instruction | 98.8 % | **100 %** |
| | Branch | 83.3 % | **100 %** |
| | Line | 97.6 % | **100 %** |
| `PetValidator` | Instruction | 87.8 % | **100 %** |
| | Branch | 87.5 % | **100 %** |
| | Line | 90.9 % | **100 %** |
| `Visit` | Instruction | 100 % | 100 % |
| | Branch | N/A | N/A |
| | Line | 100 % | 100 % |
| `VisitController` | Instruction | 100 % | 100 % |
| | Branch | 100 % | 100 % |
| | Line | 100 % | 100 % |
| `OwnerController` | Instruction | 100 % | 100 % |
| | Branch | 100 % | 100 % |
| | Line | 100 % | 100 % |
| `PetController` | Instruction | 96.1 % | **100 %** |
| | Branch | 75.0 % | **83.3 %** |
| | Line | 96.8 % | **100 %** |

> `PetController` branch coverage did not reach 100 % because 2 branches in `PetController` are not covered by tests.

---

## 2. New and Extended Test Classes

| Test class | Status | Tests added | Behaviors covered |
|------------|--------|-------------|-------------------|
| `owner/OwnerTests.java` | **NEW** | 15 | `getPet(String)` case-insensitive lookup; `getPet(String, boolean)` ignoreNew flag; `getPet(Integer)` by ID; `addPet` new-vs-existing guard; `addVisit` happy path, null petId, null visit, unknown petId |
| `owner/PetValidatorTests.java` | **NEW** | 8 | Blank name rejection; null name; null type on new pet; null type on existing pet (no error); null birthDate; fully valid pet; `supports()` true/false |
| `owner/VisitTests.java` | **NEW** | 4 | Constructor sets date to today; null description default; date setter/getter round-trip; description setter/getter round-trip |
| `owner/VisitControllerTests.java` | **EXTENDED** | 1 | `loadPetWithVisit` pre-attaches blank `Visit` to the pet model attribute before handler runs |
| `owner/OwnerControllerTests.java` | **EXTENDED** | 1 | `GET /owners?page=1` with no `lastName` param returns `owners/ownersList` (broadest search path) |
| `owner/PetControllerTests.java` | **EXTENDED** | 1 | Posting a new pet whose name matches an existing persisted pet returns `"duplicate"` field error |

---

## 3. Tests Marked `// CHARACTERIZATION`

These tests assert the **current behavior as-is**, which may not be the intended long-term design.
They must remain green even if the behavior looks surprising — they are the safety net for migration.

| Test | File | Observed behavior (why it is surprising) |
|------|------|------------------------------------------|
| `getPetByName_caseInsensitive_returnsPet` | `OwnerTests` | `getPet(String)` normalises both the query and stored name to lower-case before comparing — lookup is case-insensitive even though no JSR-303 constraint enforces case |
| `getPetById_newPet_skippedInSearch` | `OwnerTests` | Searching by `Integer` ID skips pets whose `id` is `null` (i.e. `isNew() == true`); passing `null` as the target ID returns `null` rather than matching new pets |
| `addPet_existingPet_isNotAddedAgain` | `OwnerTests` | `addPet()` silently ignores already-persisted pets (`isNew() == false`); callers that pass a persisted pet get no error but the list is unchanged |
| `validate_nullTypeOnExistingPet_noTypeError` | `PetValidatorTests` | `PetValidator` only enforces `type != null` for new pets; an existing pet can have a `null` type and pass validation — this asymmetry could be a design oversight |
| `newVisit_descriptionIsNullByDefault` | `VisitTests` | `Visit`'s no-arg constructor does not initialise `description`; the field is `null` until explicitly set, yet `@NotEmpty` is declared on the field — validation only fires on form submission, not on object construction |
| `testLoadPetWithVisit_petInModelHasVisitPreAttached` | `VisitControllerTests` | `loadPetWithVisit()` calls `pet.addVisit(visit)` as a side-effect inside a `@ModelAttribute` method, mutating the pet in-memory before the handler method is even invoked |

---

## 4. Test Authorship

| Test class | Author |
|------------|--------|
| `model/ValidatorTests.java` | Original spring-petclinic test (upstream) |
| `owner/OwnerControllerTests.java` — first 12 methods | Original spring-petclinic test (upstream) |
| `owner/OwnerControllerTests.java` — `testProcessFindForm_noLastNameParam_returnsOwnersList` | **Added by Bob (LegacyLift, 2026-09-26)** |
| `owner/PetControllerTests.java` — first 6 methods | Original spring-petclinic test (upstream) |
| `owner/PetControllerTests.java` — `testProcessCreationForm_duplicatePetName_rejectsWithDuplicateCode` | **Added by Bob (LegacyLift, 2026-09-26)** |
| `owner/PetTypeFormatterTests.java` | Original spring-petclinic test (upstream) |
| `owner/VisitControllerTests.java` — first 3 methods | Original spring-petclinic test (upstream) |
| `owner/VisitControllerTests.java` — `testLoadPetWithVisit_petInModelHasVisitPreAttached` | **Added by Bob (LegacyLift, 2026-09-26)** |
| `owner/OwnerTests.java` | **Added by Bob (LegacyLift, 2026-09-26)** |
| `owner/PetValidatorTests.java` | **Added by Bob (LegacyLift, 2026-09-26)** |
| `owner/VisitTests.java` | **Added by Bob (LegacyLift, 2026-09-26)** |
| `PetClinicIntegrationTests.java` | Original spring-petclinic test (upstream) |
| `service/ClinicServiceTests.java` | Original spring-petclinic test (upstream) |
| `system/CrashControllerTests.java` | Original spring-petclinic test (upstream) |
| `vet/VetControllerTests.java` | Original spring-petclinic test (upstream) |
| `vet/VetTests.java` | Original spring-petclinic test (upstream) |
