# Sample legacy projects

Small, public open-source projects frozen at an old Spring Boot 2.x commit, for testing the
converter. Each zip contains the project's own licence file.

| File | Source repository | Commit | Spring Boot / Java | Licence |
|---|---|---|---|---|
| `01-petclinic-boot2.7.3.zip` | spring-projects/spring-petclinic | `a5cbb8505a1df3c348c06607933a07fc8c87c222` | 2.7.3 / 1.8 | Apache-2.0 |
| `02-rest-service-boot2.7.1.zip` | spring-guides/gs-rest-service (`complete/`) | `58f5ee072467c9b7990227bd0f1a25551ea72cce` | 2.7.1 / 1.8 | Apache-2.0 |
| `03-data-jpa-boot2.7.0.zip` | spring-guides/gs-accessing-data-jpa (`complete/`) | `e06d8cf55401e32222f4cebcda12bd71ccc68fd4` | 2.7.0 / 1.8 | Apache-2.0 |
| `04-jwt-security-boot2.5.4.zip` | murraco/spring-boot-jwt | `e9186360be0614873ae6d8e69c8e4d0948e09faa` | 2.5.4 / 1.8 | MIT |

## Measured results (on the author's machine)

| Sample | Result |
|---|---|
| 01-petclinic | ✅ SUCCESS: Java 21 + Boot 3.4.13, 14 → 0 javax files, 41/41 tests (1 skipped, as before) |
| 03-data-jpa | ✅ SUCCESS: Java 21 + Boot 3.4.13, 1 → 0 javax files, tests pass, 196 s |
| 02-rest-service | not yet run |
| 04-jwt-security | not yet run (uses the removed `WebSecurityConfigurerAdapter`, expected to need manual fixes) |
