/*
 * Copyright 2012-2019 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.springframework.samples.petclinic.owner;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.LocalDate;

import org.junit.jupiter.api.Test;

/**
 * Characterization tests for {@link Visit}. These lock in the CURRENT constructor and
 * accessor behavior before migration.
 */
class VisitTests {

	@Test
	void newVisit_setsDateToToday() {
		// CHARACTERIZATION: the no-arg constructor sets date to LocalDate.now()
		LocalDate before = LocalDate.now();
		Visit visit = new Visit();
		LocalDate after = LocalDate.now();
		assertThat(visit.getDate()).isNotNull();
		assertThat(visit.getDate()).isAfterOrEqualTo(before).isBeforeOrEqualTo(after);
	}

	@Test
	void setAndGetDate_roundTrips() {
		Visit visit = new Visit();
		LocalDate date = LocalDate.of(2023, 5, 15);
		visit.setDate(date);
		assertThat(visit.getDate()).isEqualTo(date);
	}

	@Test
	void setAndGetDescription_roundTrips() {
		Visit visit = new Visit();
		visit.setDescription("Post-surgery follow-up");
		assertThat(visit.getDescription()).isEqualTo("Post-surgery follow-up");
	}

	@Test
	void newVisit_descriptionIsNullByDefault() {
		// CHARACTERIZATION: description is not set by the constructor
		Visit visit = new Visit();
		assertThat(visit.getDescription()).isNull();
	}

}
