"""
Tests for the traits type system.
"""
# pylint: disable=invalid-name,missing-class-docstring
# pylint: disable=redefined-outer-name,no-self-use
# pylint: disable=missing-function-docstring
import pytest
# TODO(DF): @pylint - re-enable once Python dev vs. install mess sorted.
# pylint: disable=no-name-in-module
from openassetio import Specification


class Test_Specification_traitIds:
    ## TODO(TC): Asset that result is a set, and not a reference to
    ## any internal structures.
    def test_when_has_no_traits_returns_empty_list(self):
        empty_specification = Specification()
        assert empty_specification.traitIds() == set()

    def test_when_has_traits_returns_expected_trait_ids(self):
        expected_ids = {"a", "b", "🐠🐟🐠🐟"}
        populated_specification = Specification(expected_ids)
        assert populated_specification.traitIds() == expected_ids


class Test_Specification_addTrait:
    def test_when_trait_is_new_then_added(self):
        specification = Specification()
        trait_name = "a 🐍"
        specification.addTrait(trait_name)
        assert specification.traitIds() == {trait_name}

    def test_when_trait_is_new_then_existing_traits_are_unaffected(self, a_specification):
        trait_set = set(a_specification.traitIds())
        new_trait = "another trait"
        a_specification.addTrait(new_trait)
        trait_set.add(new_trait)
        assert a_specification.traitIds() == trait_set

    def test_when_trait_already_exists_then_is_noop(self, a_specification):
        old_traits = a_specification.traitIds()
        a_specification.addTrait(next(iter(a_specification.traitIds())))
        assert a_specification.traitIds() == old_traits


class Test_Specification_addTraits:
    def test_when_traits_are_new_the_added(self):
        specification = Specification()
        trait_set = {"🐌", "🐞", "🐜"}
        specification.addTraits(trait_set)
        assert specification.traitIds() == trait_set

    def test_when_traits_are_new_then_existing_traits_are_unaffected(self, a_specification):
        trait_set = set(a_specification.traitIds())
        new_traits = {"🐌", "🐞", "🐜"}
        a_specification.addTraits(new_traits)
        expected_traits = trait_set.union(new_traits)
        assert a_specification.traitIds() == expected_traits

    def test_when_trait_ids_already_exist_then_is_noop(self, a_specification):
        traits = a_specification.traitIds()
        old_traits = traits
        a_specification.addTraits(traits)
        assert a_specification.traitIds() == old_traits


class Test_Specification_hasTrait:
    def test_when_has_trait_then_returns_true(self, a_specification):
        assert a_specification.hasTrait("second_trait")

    def test_when_not_has_trait_then_returns_false(self, a_specification):
        assert not a_specification.hasTrait("unknown_trait")


class Test_Specification_getsetTraitProperty:
    def test_valid_values(self, a_specification):
        a_specification.setTraitProperty("first_trait", "a string", "string")
        a_specification.setTraitProperty("second_trait", "an int", 1)
        a_specification.setTraitProperty("first_trait", "a float", 1.0)
        a_specification.setTraitProperty("second_trait", "a bool", True)

        assert a_specification.getTraitProperty("first_trait", "a string") == "string"
        assert isinstance(a_specification.getTraitProperty("first_trait", "a string"), str)
        assert a_specification.getTraitProperty("second_trait", "an int") == 1
        assert isinstance(a_specification.getTraitProperty("second_trait", "an int"), int)
        assert a_specification.getTraitProperty("first_trait", "a float") == 1.0
        assert isinstance(a_specification.getTraitProperty("first_trait", "a float"), float)
        assert a_specification.getTraitProperty("second_trait", "a bool") is True

    def test_when_key_is_not_found_then_get_returns_None(self, a_specification):
        assert a_specification.getTraitProperty("first_trait", "a string") is None

    def test_when_trait_is_not_found_then_set_adds_trait(self, a_specification):
        new_trait_id, a_property, a_value = "a_new_trait", "a string", "string"
        a_specification.setTraitProperty(new_trait_id, a_property, a_value)
        assert new_trait_id in a_specification.traitIds()
        assert a_specification.getTraitProperty(new_trait_id, a_property) == a_value

    def test_when_trait_is_not_found_then_get_raises_IndexError(self, a_specification):
        with pytest.raises(IndexError):
            _ = a_specification.getTraitProperty("unknown_trait", "a string")

    def test_when_value_is_not_supported_then_set_raises_TypeError(self, a_specification):
        with pytest.raises(TypeError):
            a_specification.setTraitProperty("first_trait", "unknown type", object())

        with pytest.raises(TypeError):
            a_specification.setTraitProperty("first_trait", "unknown type", None)


class Test_Specification_equality:
    def test_when_comparing_with_same_data_then_are_equal(self):
        spec_a = Specification({"a_trait"})
        spec_a.setTraitProperty("a_trait", "a_property", 1)
        spec_b = Specification({"a_trait"})
        spec_b.setTraitProperty("a_trait", "a_property", 1)
        assert spec_a == spec_b

    def test_when_comparing_with_different_property_value_then_are_not_equal(self):
        spec_a = Specification({"a_trait"})
        spec_a.setTraitProperty("a_trait", "a_property", 1)
        spec_b = Specification({"a_trait"})
        spec_b.setTraitProperty("a_trait", "a_property", 2)
        assert spec_a != spec_b

    def test_when_comparing_with_subset_of_properties_then_are_not_equal(self):
        spec_a = Specification({"a_trait"})
        spec_a.setTraitProperty("a_trait", "a_property", 1)
        spec_b = Specification({"a_trait"})
        spec_b.setTraitProperty("a_trait", "a_property", 1)
        spec_b.setTraitProperty("a_trait", "another_property", 1)
        assert spec_a != spec_b

    def test_when_comparing_with_different_trait_then_are_not_equal(self):
        spec_a = Specification({"a_trait"})
        spec_b = Specification({"another_trait"})
        assert spec_a != spec_b
        assert spec_a != spec_b


@pytest.fixture
def a_specification():
    return Specification({"first_trait", "second_trait"})