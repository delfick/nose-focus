# coding: spec

from nose_focus.plugin import Lineage

from tests.examples.test_examples.test_ignored_module.test_implicitly_ignored_module import (
    test_stuff as implicitly_ignored_module_stuff,
)
from tests.examples.test_examples.test_ignored_module import (
    test_implicitly_ignored_module as implicitly_ignored_module,
)

from tests.examples.test_examples.test_ignored_module import test_things as ignored_module_things
from tests.examples.test_examples import test_ignored_module as ignored_module

from tests.examples.test_examples.test_module import test_module_with_focus_things as focus_things
from tests.examples.test_examples.test_module import test_focus_all_module as focus_all_module
from tests.examples.test_examples.test_module import test_non_focus_module as non_focus_module
from tests.examples.test_examples.test_module import test_focus_module as focus_module

from tests.examples.test_examples.test_module import test_with_ignored_things as ignored_things
from tests.examples.test_examples.test_module import test_non_focus_module as nonfocusedd_things

import pytest
import types

some_ignored_things = [
    implicitly_ignored_module,
    implicitly_ignored_module_stuff,
    implicitly_ignored_module_stuff.test_things,
    implicitly_ignored_module_stuff.TestStuff,
    implicitly_ignored_module_stuff.TestStuff.test_other,
    ignored_module,
    ignored_module_things,
    ignored_module_things.test_things,
    ignored_module_things.TestStuff,
    ignored_module_things.TestStuff.test_other,
    ignored_things.IgnoredClass.test_blah,
    ignored_things.IgnoredClassChild,
    ignored_things.IgnoredClassChild.test_meh,
]


@pytest.fixture()
def lineage():
    return Lineage()


def ignored_things_with_attribute(**kwargs):
    """
    Yield the ignored things with particular attributes and ensure those attributes are reset afterwards

    The butterfly that this function looks like is brought to you by python3's lack of unbound methods
    """
    Empty = type("Empty", (object,), {})
    for thing in some_ignored_things:
        current_vals = dict((key, getattr(thing, key, Empty)) for key in kwargs)
        try:
            for key, val in kwargs.items():
                setattr(thing, key, val)
            yield thing
        except AttributeError as err:
            raise Exception(
                "Couldn't set {0} on {1} to {2} because {3}".format(key, thing, val, err)
            )
        finally:
            for key, val in current_vals.items():
                if val is Empty:
                    delattr(thing, key)
                else:
                    setattr(thing, key, val)


describe "Determining ignored":
    it "is ignored if set to ignored", lineage:
        assert lineage.ignored(ignored_things.test_ignored)
        assert not lineage.ignored(ignored_things.test_not_ignored)

    it "is ignored if parent is set to ignored", lineage:
        for thing in some_ignored_things:
            assert lineage.ignored(thing)

describe "Determining focus all":
    it "is not set to focused_all if anything in lineage is ignored", lineage:
        for thing in ignored_things_with_attribute(nose_focus_all=True):
            assert not lineage.focused_all(thing)

    it "is set to focused if it has focus_all set", lineage:
        assert lineage.focused_all(focus_all_module)
        assert lineage.focused_all(focus_things.TestFocusManyLayer)
        assert lineage.focused_all(focus_things.test_focus_all_function)

    it "is not necessarily set if just focus is set", lineage:
        assert not lineage.focused_all(focus_things.TestFocusOneLayer)
        assert not lineage.focused_all(focus_things.test_focused_function)

    it "is not set if the parent is ignored", lineage:
        assert not lineage.focused_all(
            implicitly_ignored_module_stuff.TestWithFocusAllButIgnoredModule
        )

    it "is set if any parent has it set", lineage:
        assert lineage.focused_all(focus_things.TestFocusManyLayer)
        assert lineage.focused_all(focus_things.TestFocusManyLayer.test_a_test)
        assert lineage.focused_all(focus_things.TestFocusManyLayerChild)
        assert lineage.focused_all(focus_things.TestFocusManyLayerChild.test_b_test)
        assert lineage.focused_all(focus_things.TestFocusManyLayerGrandChild)
        assert lineage.focused_all(focus_things.TestFocusManyLayerGrandChild.test_c_test)

        assert lineage.focused_all(focus_all_module.test_focus_function)
        assert lineage.focused_all(focus_all_module.TestFocusClass)
        assert lineage.focused_all(focus_all_module.TestFocusClass.test_blah)

describe "Determining focus":
    it "is not set to focused if anything in lineage is ignored", lineage:
        for thing in ignored_things_with_attribute(nose_focus=True):
            assert not lineage.focused(thing)

    it "is set to focused if it has focus set", lineage:
        assert lineage.focused(focus_module)
        assert lineage.focused(focus_things.TestFocusOneLayer)
        assert lineage.focused(focus_things.test_focused_function)

    it "is set to focused if anything has focus_all", lineage:
        assert lineage.focused(focus_things.TestFocusManyLayer)
        assert lineage.focused(focus_things.TestFocusManyLayer.test_a_test)
        assert lineage.focused(focus_things.TestFocusManyLayerChild)
        assert lineage.focused(focus_things.TestFocusManyLayerChild.test_b_test)
        assert lineage.focused(focus_things.TestFocusManyLayerGrandChild)
        assert lineage.focused(focus_things.TestFocusManyLayerGrandChild.test_c_test)

        assert lineage.focused(focus_all_module.test_focus_function)
        assert lineage.focused(focus_all_module.TestFocusClass)
        assert lineage.focused(focus_all_module.TestFocusClass.test_blah)

    it "is set to focused if one parent has focus", lineage:
        assert lineage.focused(focus_module.TestFocusClass)
        assert lineage.focused(focus_module.test_focus_function)
        assert lineage.focused(focus_things.TestFocusOneLayer.test_a_test)

    it "is not set to focused just because parent class is focused", lineage:
        assert not lineage.focused(non_focus_module.TestFocusClassChild)
        assert not lineage.focused(non_focus_module.TestFocusClassChild.test_stuff)
