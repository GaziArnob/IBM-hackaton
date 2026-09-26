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
import static org.assertj.core.api.Assertions.assertThatIllegalArgumentException;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Characterization tests for {@link Owner} domain logic. These lock in the CURRENT
 * behavior of the aggregate root before migration.
 */
class OwnerTests {

	private Owner owner;

	private Pet existingPet;

	@BeforeEach
	void setUp() {
		owner = new Owner();

		existingPet = new Pet();
		existingPet.setId(1);
		existingPet.setName("Buddy");
		// Add directly to the list via addPet (new pet path)
		owner.getPets().add(existingPet);
	}

	// -------------------------------------------------------------------------
	// getPet(String name)
	// -------------------------------------------------------------------------

	@Test
	void getPetByName_existingName_returnsPet() {
		assertThat(owner.getPet("Buddy")).isSameAs(existingPet);
	}

	@Test
	void getPetByName_caseInsensitive_returnsPet() {
		// CHARACTERIZATION: current behavior - lookup is case-insensitive
		assertThat(owner.getPet("BUDDY")).isSameAs(existingPet);
	}

	@Test
	void getPetByName_unknownName_returnsNull() {
		assertThat(owner.getPet("Unknown")).isNull();
	}

	// -------------------------------------------------------------------------
	// getPet(String name, boolean ignoreNew)
	// -------------------------------------------------------------------------

	@Test
	void getPetByName_ignoreNewFalse_findsNewPet() {
		Pet newPet = new Pet(); // id == null → isNew() == true
		newPet.setName("Kitty");
		owner.getPets().add(newPet);

		// ignoreNew=false → includes new (unsaved) pets in search
		assertThat(owner.getPet("Kitty", false)).isSameAs(newPet);
	}

	@Test
	void getPetByName_ignoreNewTrue_skipsNewPet() {
		Pet newPet = new Pet(); // id == null → isNew() == true
		newPet.setName("Kitty");
		owner.getPets().add(newPet);

		// ignoreNew=true → new (unsaved) pets are excluded
		assertThat(owner.getPet("Kitty", true)).isNull();
	}

	@Test
	void getPetByName_ignoreNewTrue_findsPersistedPet() {
		// existingPet has id=1 → isNew()==false, so ignoreNew=true still finds it
		assertThat(owner.getPet("Buddy", true)).isSameAs(existingPet);
	}

	// -------------------------------------------------------------------------
	// getPet(Integer id)
	// -------------------------------------------------------------------------

	@Test
	void getPetById_existingId_returnsPet() {
		assertThat(owner.getPet(1)).isSameAs(existingPet);
	}

	@Test
	void getPetById_unknownId_returnsNull() {
		assertThat(owner.getPet(99)).isNull();
	}

	@Test
	void getPetById_newPet_skippedInSearch() {
		// CHARACTERIZATION: new (unsaved) pets are skipped when searching by id
		Pet newPet = new Pet(); // isNew() == true
		newPet.setName("Ghost");
		owner.getPets().add(newPet);
		assertThat(owner.getPet((Integer) null)).isNull();
	}

	// -------------------------------------------------------------------------
	// addPet
	// -------------------------------------------------------------------------

	@Test
	void addPet_newPet_isAdded() {
		Pet newPet = new Pet(); // isNew() == true
		newPet.setName("Shadow");
		int sizeBefore = owner.getPets().size();
		owner.addPet(newPet);
		assertThat(owner.getPets()).hasSize(sizeBefore + 1);
	}

	@Test
	void addPet_existingPet_isNotAddedAgain() {
		// CHARACTERIZATION: addPet only adds the pet if pet.isNew(); persisted pets are
		// ignored
		int sizeBefore = owner.getPets().size();
		owner.addPet(existingPet); // existingPet has id=1 → isNew()==false
		assertThat(owner.getPets()).hasSize(sizeBefore);
	}

	// -------------------------------------------------------------------------
	// addVisit
	// -------------------------------------------------------------------------

	@Test
	void addVisit_validPetIdAndVisit_addsVisitToPet() {
		Visit visit = new Visit();
		visit.setDescription("Annual checkup");
		owner.addVisit(existingPet.getId(), visit);
		assertThat(existingPet.getVisits()).contains(visit);
	}

	@Test
	void addVisit_withNullPetId_throwsIllegalArgumentException() {
		assertThatIllegalArgumentException().isThrownBy(() -> owner.addVisit(null, new Visit()))
				.withMessageContaining("Pet identifier must not be null");
	}

	@Test
	void addVisit_withNullVisit_throwsIllegalArgumentException() {
		assertThatIllegalArgumentException().isThrownBy(() -> owner.addVisit(existingPet.getId(), null))
				.withMessageContaining("Visit must not be null");
	}

	@Test
	void addVisit_withUnknownPetId_throwsIllegalArgumentException() {
		assertThatIllegalArgumentException().isThrownBy(() -> owner.addVisit(999, new Visit()))
				.withMessageContaining("Invalid Pet identifier");
	}

}
