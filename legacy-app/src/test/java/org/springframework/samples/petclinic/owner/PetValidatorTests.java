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

import org.junit.jupiter.api.Test;
import org.springframework.validation.BeanPropertyBindingResult;
import org.springframework.validation.Errors;

/**
 * Characterization tests for {@link PetValidator}. These lock in the CURRENT validation
 * behavior before migration.
 */
class PetValidatorTests {

	private final PetValidator validator = new PetValidator();

	private Errors bindingResult(Pet pet) {
		return new BeanPropertyBindingResult(pet, "pet");
	}

	private Pet validPet() {
		Pet pet = new Pet();
		pet.setId(1); // persisted → isNew() == false
		pet.setName("Max");
		PetType type = new PetType();
		type.setName("dog");
		pet.setType(type);
		pet.setBirthDate(java.time.LocalDate.of(2020, 1, 1));
		return pet;
	}

	@Test
	void validate_fullyValidPersistedPet_noErrors() {
		Pet pet = validPet();
		Errors errors = bindingResult(pet);
		validator.validate(pet, errors);
		assertThat(errors.hasErrors()).isFalse();
	}

	@Test
	void validate_blankName_rejectsNameField() {
		Pet pet = validPet();
		pet.setName("");
		Errors errors = bindingResult(pet);
		validator.validate(pet, errors);
		assertThat(errors.hasFieldErrors("name")).isTrue();
		assertThat(errors.getFieldError("name").getCode()).isEqualTo("required");
	}

	@Test
	void validate_nullNameEquivalent_rejectsNameField() {
		// PetValidator calls StringUtils.hasLength(name); null name also fails
		Pet pet = validPet();
		pet.setName(null);
		Errors errors = bindingResult(pet);
		validator.validate(pet, errors);
		assertThat(errors.hasFieldErrors("name")).isTrue();
	}

	@Test
	void validate_nullTypeOnNewPet_rejectsTypeField() {
		Pet pet = new Pet(); // isNew() == true
		pet.setName("Kitty");
		pet.setBirthDate(java.time.LocalDate.of(2022, 6, 1));
		pet.setType(null);
		Errors errors = bindingResult(pet);
		validator.validate(pet, errors);
		assertThat(errors.hasFieldErrors("type")).isTrue();
		assertThat(errors.getFieldError("type").getCode()).isEqualTo("required");
	}

	@Test
	void validate_nullTypeOnExistingPet_noTypeError() {
		// CHARACTERIZATION: type is only validated for NEW pets; existing pets with null
		// type pass the type check
		Pet pet = validPet(); // isNew() == false
		pet.setType(null);
		Errors errors = bindingResult(pet);
		validator.validate(pet, errors);
		assertThat(errors.hasFieldErrors("type")).isFalse();
	}

	@Test
	void validate_nullBirthDate_rejectsBirthDateField() {
		Pet pet = validPet();
		pet.setBirthDate(null);
		Errors errors = bindingResult(pet);
		validator.validate(pet, errors);
		assertThat(errors.hasFieldErrors("birthDate")).isTrue();
		assertThat(errors.getFieldError("birthDate").getCode()).isEqualTo("required");
	}

	@Test
	void supports_petClass_returnsTrue() {
		assertThat(validator.supports(Pet.class)).isTrue();
	}

	@Test
	void supports_otherClass_returnsFalse() {
		assertThat(validator.supports(Object.class)).isFalse();
	}

}
