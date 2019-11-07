# coding: spec

import subprocess
import shutil
import shlex
import fcntl
import time
import sys
import os
import re

this_folder = os.path.abspath(os.path.dirname(__file__))
test_folder = os.path.join(this_folder, "examples", "test_examples")

regexes = {
    "test_result": re.compile(
        r"((?P<name>[^ ]+) \((?P<home>[^\)]+)\)|(?P<full_test>[^ ]+))( ... )?ok"
    )
}

describe "Running nose":

    def run_nose(self, other_args=""):
        """
        Run the example tests and return the names of the tests that ran

        Also make sure this doesn't hang indefinitely if things go wrong
        """
        if not shutil.which("nosetests"):
            assert False, "nosetests is not on your PATH"

        cmd = ["nosetests", test_folder, "-v", *shlex.split(other_args)]
        ran = " ".join(shlex.quote(t) for t in cmd)

        out = subprocess.run(
            cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, timeout=5, check=True
        ).stderr.decode()

        print()
        print("=" * 80)
        print(out)
        print("=" * 80)
        print()

        tests = []
        for line in out.split("\n"):
            if not line.strip():
                break

            match = regexes["test_result"].match(line)
            if not match:
                assert (
                    False
                ), "Expected all the lines to match a regex but this line didn't match: {0}".format(
                    line
                )

            groups = match.groupdict()
            if groups.get("full_test"):
                tests.append(groups["full_test"])
            else:
                tests.append("{0}.{1}".format(groups["home"], groups["name"]))

        return ran, tests

    def assert_expected_focus(self, expected, other_args=""):
        """Assert that only the tests we specify get run when we run nose with the specified args"""
        cmd, result = self.run_nose(other_args)
        if result != expected:
            print("Ran: {0}".format(cmd))
            print("Got:")
            print("\n".join(result))
            print("-" * 80)
            print("Expected:")
            print("\n".join(expected))
            print("=" * 80)
        assert result == expected

    it "runs all the tests when run without nose_focus":
        expected = [
            "tests.examples.test_examples.test_ignored_module.test_implicitly_ignored_module.test_stuff.TestStuff.test_other",
            "tests.examples.test_examples.test_ignored_module.test_implicitly_ignored_module.test_stuff.TestWithFocusAllButIgnoredModule.test_things",
            "tests.examples.test_examples.test_ignored_module.test_implicitly_ignored_module.test_stuff.test_things",
            "tests.examples.test_examples.test_ignored_module.test_things.TestStuff.test_other",
            "tests.examples.test_examples.test_ignored_module.test_things.test_things",
            "tests.examples.test_examples.test_module.test_focus_all_module.TestFocusClass.test_blah",
            "tests.examples.test_examples.test_module.test_focus_all_module.test_focus_function",
            "tests.examples.test_examples.test_module.test_focus_module.TestFocusClass.test_blah",
            "tests.examples.test_examples.test_module.test_focus_module.test_focus_function",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayer.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerChild.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerChild.test_b_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerGrandChild.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerGrandChild.test_b_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerGrandChild.test_c_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusOneLayer.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusOneLayerChild.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusOneLayerChild.test_b_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusedFunctionBrother.test_blah",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.test_focus_all_function",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.test_focused_function",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.test_focused_function_two",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.test_focused_function_brother",
            "tests.examples.test_examples.test_module.test_non_focus_module.transplant_class.<locals>.C.test_blah",
            "tests.examples.test_examples.test_module.test_non_focus_module.TestFocusClassChild.test_blah",
            "tests.examples.test_examples.test_module.test_non_focus_module.TestFocusClassChild.test_stuff",
            "tests.examples.test_examples.test_module.test_non_focus_module.TestNonFocusClass.test_blah",
            "tests.examples.test_examples.test_module.test_non_focus_module.test_nonfocus_function",
            "tests.examples.test_examples.test_module.test_with_ignored_things.IgnoredClass.test_blah",
            "tests.examples.test_examples.test_module.test_with_ignored_things.IgnoredClassChild.test_blah",
            "tests.examples.test_examples.test_module.test_with_ignored_things.IgnoredClassChild.test_meh",
            "tests.examples.test_examples.test_module.test_with_ignored_things.test_not_ignored",
            "tests.examples.test_examples.test_module.test_with_ignored_things.test_ignored",
        ]

        self.assert_expected_focus(expected)

    it "Runs all the tests except those that are ignored when run with --without-ignored":
        expected = [
            #   "tests.examples.test_examples.test_ignored_module.test_implicitly_ignored_module.test_stuff.TestStuff.test_other"
            # , "tests.examples.test_examples.test_ignored_module.test_implicitly_ignored_module.test_stuff.TestWithFocusAllButIgnoredModule.test_things"
            # , "tests.examples.test_examples.test_ignored_module.test_implicitly_ignored_module.test_stuff.test_things"
            # , "tests.examples.test_examples.test_ignored_module.test_things.TestStuff.test_other"
            # , "tests.examples.test_examples.test_ignored_module.test_things.test_things"
            "tests.examples.test_examples.test_module.test_focus_all_module.TestFocusClass.test_blah",
            "tests.examples.test_examples.test_module.test_focus_all_module.test_focus_function",
            "tests.examples.test_examples.test_module.test_focus_module.TestFocusClass.test_blah",
            "tests.examples.test_examples.test_module.test_focus_module.test_focus_function",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayer.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerChild.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerChild.test_b_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerGrandChild.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerGrandChild.test_b_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerGrandChild.test_c_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusOneLayer.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusOneLayerChild.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusOneLayerChild.test_b_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusedFunctionBrother.test_blah",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.test_focus_all_function",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.test_focused_function",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.test_focused_function_two",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.test_focused_function_brother",
            "tests.examples.test_examples.test_module.test_non_focus_module.transplant_class.<locals>.C.test_blah",
            "tests.examples.test_examples.test_module.test_non_focus_module.TestFocusClassChild.test_blah",
            "tests.examples.test_examples.test_module.test_non_focus_module.TestFocusClassChild.test_stuff",
            "tests.examples.test_examples.test_module.test_non_focus_module.TestNonFocusClass.test_blah",
            "tests.examples.test_examples.test_module.test_non_focus_module.test_nonfocus_function"
            # , "tests.examples.test_examples.test_module.test_with_ignored_things.IgnoredClass.test_blah"
            # , "tests.examples.test_examples.test_module.test_with_ignored_things.IgnoredClassChild.test_blah"
            # , "tests.examples.test_examples.test_module.test_with_ignored_things.IgnoredClassChild.test_meh"
            ,
            "tests.examples.test_examples.test_module.test_with_ignored_things.test_not_ignored"
            # , "tests.examples.test_examples.test_module.test_with_ignored_things.test_ignored"
        ]

        self.assert_expected_focus(expected, "--without-ignored")

    it "Runs only the focus tests if used with --with-focus":
        expected = [
            #   "tests.examples.test_examples.test_ignored_module.test_implicitly_ignored_module.test_stuff.TestStuff.test_other"
            # , "tests.examples.test_examples.test_ignored_module.test_implicitly_ignored_module.test_stuff.TestWithFocusAllButIgnoredModule.test_things"
            # , "tests.examples.test_examples.test_ignored_module.test_implicitly_ignored_module.test_stuff.test_things"
            # , "tests.examples.test_examples.test_ignored_module.test_things.TestStuff.test_other"
            # , "tests.examples.test_examples.test_ignored_module.test_things.test_things"
            "tests.examples.test_examples.test_module.test_focus_all_module.TestFocusClass.test_blah",
            "tests.examples.test_examples.test_module.test_focus_all_module.test_focus_function",
            "tests.examples.test_examples.test_module.test_focus_module.TestFocusClass.test_blah",
            "tests.examples.test_examples.test_module.test_focus_module.test_focus_function",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayer.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerChild.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerChild.test_b_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerGrandChild.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerGrandChild.test_b_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusManyLayerGrandChild.test_c_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusOneLayer.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusOneLayerChild.test_a_test",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusOneLayerChild.test_b_test"
            # , "tests.examples.test_examples.test_module.test_module_with_focus_things.TestFocusedFunctionBrother.test_blah"
            ,
            "tests.examples.test_examples.test_module.test_module_with_focus_things.test_focus_all_function",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.test_focused_function",
            "tests.examples.test_examples.test_module.test_module_with_focus_things.test_focused_function_two"
            # , "tests.examples.test_examples.test_module.test_module_with_focus_things.test_focused_function_brother"
            ,
            "tests.examples.test_examples.test_module.test_non_focus_module.transplant_class.<locals>.C.test_blah",
            "tests.examples.test_examples.test_module.test_non_focus_module.TestFocusClassChild.test_blah"
            # , "tests.examples.test_examples.test_module.test_non_focus_module.TestFocusClassChild.test_stuff"
            # , "tests.examples.test_examples.test_module.test_non_focus_module.TestNonFocusClass.test_blah"
            # , "tests.examples.test_examples.test_module.test_non_focus_module.test_nonfocus_function"
            # , "tests.examples.test_examples.test_module.test_with_ignored_things.IgnoredClass.test_blah"
            # , "tests.examples.test_examples.test_module.test_with_ignored_things.IgnoredClassChild.test_blah"
            # , "tests.examples.test_examples.test_module.test_with_ignored_things.IgnoredClassChild.test_meh"
            # , "tests.examples.test_examples.test_module.test_with_ignored_things.test_not_ignored"
            # , "tests.examples.test_examples.test_module.test_with_ignored_things.test_ignored"
        ]

        self.assert_expected_focus(expected, "--with-focus")
