# coding: spec

from nose_focus.plugin import Lineage
import noseOfYeti.tokeniser.support
import noseOfYeti
import pytest
import nose

from tests.examples import lineage as lg, lineage2 as lg2
from tests import examples
import tests


@pytest.fixture()
def lineage():
    return Lineage()


describe "Finding lineage":
    describe "For a built in":
        it "Finds no lineage", lineage:
            assert lineage.determine(len) == []
            assert lineage.determine(locals) == []

    describe "For a module":
        it "Finds parent modules", lineage:
            assert lineage.determine(examples) == [tests]
            assert lineage.determine(noseOfYeti.tokeniser.support) == [
                noseOfYeti.tokeniser,
                noseOfYeti,
            ]

    describe "For a class":
        it "Ignores object as a parent", lineage:
            assert lineage.determine(lg.AClass) == [
                tests.examples.lineage,
                tests.examples,
                tests,
            ]

        it "Finds parent classes and modules", lineage:
            assert lineage.determine(lg.ASubClass) == [
                tests.examples.lineage,
                tests.examples,
                tests,
                lg.AClass,
            ]
            assert lineage.determine(lg.AGrandChildClass) == [
                tests.examples.lineage,
                tests.examples,
                tests,
                lg.ASubClass,
                lg.AClass,
            ]

        it "Finds Mixins", lineage:
            assert lineage.determine(lg.AClassWithMixin) == [
                tests.examples.lineage,
                tests.examples,
                tests,
                lg.AMixin,
            ]
            assert lineage.determine(lg.AClassWithSubMixin) == [
                tests.examples.lineage,
                tests.examples,
                tests,
                lg.ASubMixin,
                lg.AMixin,
            ]
            assert lineage.determine(lg.AClassWithMultipleMixins) == [
                tests.examples.lineage,
                tests.examples,
                tests,
                lg.ASubMixin,
                lg.AMixin,
                lg.BMixin,
            ]

        it "Finds parent classes with embedded classes if they have __embedded_class_parent__", lineage:
            assert lineage.determine(lg.AClassWithEmbeddedClass.EmbeddedClass) == [
                tests.examples.lineage,
                tests.examples,
                tests,
                lg.AClassWithEmbeddedClass,
            ]

    describe "For a function":
        it "Finds the modules", lineage:
            assert lineage.determine(lg.aFunction) == [
                tests.examples.lineage,
                tests.examples,
                tests,
            ]

    describe "methods":

        def assert_finds(
            self, lineage, klses, methods, looking_for, instance_only=False, definition_only=False
        ):
            """Assert that the methods on both the kls definition and kls instance finds the lineage we are looking for"""
            if not isinstance(klses, list) and not isinstance(klses, tuple):
                klses = [klses]

            if len(set(looking_for)) != len(looking_for):
                raise Exception("Looks like you have duplicates in looking_for...")

            if instance_only and definition_only:
                raise Exception(
                    "Doesn't make sense to call assert_finds with instance_only and definition_only both set to True"
                )

            for method in methods:
                for kls in klses:
                    if not instance_only:
                        result = lineage.determine(getattr(kls, method))
                        if result != looking_for:
                            print("Determining {1} on {0} definition".format(kls, method))
                            print(result)
                            print("---")
                            print(looking_for)
                        assert result == looking_for

                    if not definition_only:
                        result = lineage.determine(getattr(kls(), method))
                        if result != looking_for:
                            print("Determining {1} on {0} instance".format(kls, method))
                            print(result)
                            print("---")
                            print(looking_for)
                        assert result == looking_for

        it "Finds parent classes and modules", lineage:
            self.assert_finds(
                lineage,
                lg.AClass,
                ["onlyAClass", "aMethod"],
                [lg.AClass, tests.examples.lineage, tests.examples, tests],
            )

        describe "Inheritance":
            it "Finds the class the method is defined on", lineage:
                klses = [
                    lg.AMixin,
                    lg.ASubMixin,
                    lg.AClassWithMixin,
                    lg.AClassWithSubMixin,
                    lg2.BClassWithASubMixin,
                    lg.AClassWithMixinOverride,
                    lg.AClassWithSubMixinOverride,
                    lg2.BClassWithASubMixinOverride,
                    lg2.BClassWithASubMixinOverride,
                    lg.AClassWithMultipleMixins,
                ]
                self.assert_finds(
                    lineage,
                    klses,
                    ["onlyAMixin"],
                    [lg.AMixin, tests.examples.lineage, tests.examples, tests],
                )

                klses = [
                    lg.ASubMixin,
                    lg.AClassWithSubMixin,
                    lg2.BClassWithASubMixin,
                    lg.AClassWithSubMixinOverride,
                    lg2.BClassWithASubMixinOverride,
                    lg.AClassWithMultipleMixins,
                ]
                self.assert_finds(
                    lineage,
                    klses,
                    ["onlyASubMixin"],
                    [lg.ASubMixin, tests.examples.lineage, tests.examples, tests, lg.AMixin,],
                )

                klses = [
                    lg.AClass,
                    lg.ASubClass,
                    lg.ASubClassOverride,
                    lg.AGrandChildClass,
                    lg.AGrandChildClassOverride,
                    lg2.BSubClass,
                    lg2.BSubClassOverride,
                    lg2.BGrandChildClass,
                    lg2.BGrandChildClassOverride,
                ]
                self.assert_finds(
                    lineage,
                    klses,
                    ["onlyAClass"],
                    [lg.AClass, tests.examples.lineage, tests.examples, tests],
                )

                klses = [
                    lg.ASubClass,
                    lg.AGrandChildClass,
                    lg.AGrandChildClassOverride,
                ]
                self.assert_finds(
                    lineage,
                    klses,
                    ["onlyASubClass"],
                    [lg.ASubClass, tests.examples.lineage, tests.examples, tests, lg.AClass,],
                )

                klses = [
                    lg2.BSubClass,
                    lg2.BGrandChildClass,
                    lg2.BGrandChildClassOverride,
                ]
                self.assert_finds(
                    lineage,
                    klses,
                    ["onlyBSubClass"],
                    [
                        lg2.BSubClass,
                        tests.examples.lineage2,
                        tests.examples,
                        tests,
                        lg.AClass,
                        tests.examples.lineage,
                    ],
                )

                self.assert_finds(
                    lineage,
                    lg.AGrandChildClass,
                    ["onlyAGrandChildClass"],
                    [
                        lg.AGrandChildClass,
                        tests.examples.lineage,
                        tests.examples,
                        tests,
                        lg.ASubClass,
                        lg.AClass,
                    ],
                )

            it "finds mixins from the method if the method is defined on the class we are getting it from", lineage:
                self.assert_finds(
                    lineage,
                    lg.AMixin,
                    ["onlyAMixin"],
                    [lg.AMixin, tests.examples.lineage, tests.examples, tests],
                )

                self.assert_finds(
                    lineage,
                    lg.ASubMixin,
                    ["onlyASubMixin"],
                    [lg.ASubMixin, tests.examples.lineage, tests.examples, tests, lg.AMixin,],
                )

                self.assert_finds(
                    lineage,
                    lg.AClassWithMixin,
                    ["onlyAClassWithMixin"],
                    [lg.AClassWithMixin, tests.examples.lineage, tests.examples, tests, lg.AMixin,],
                )

                self.assert_finds(
                    lineage,
                    lg.AClassWithSubMixin,
                    ["onlyAClassWithSubMixin"],
                    [
                        lg.AClassWithSubMixin,
                        tests.examples.lineage,
                        tests.examples,
                        tests,
                        lg.ASubMixin,
                        lg.AMixin,
                    ],
                )

                self.assert_finds(
                    lineage,
                    lg2.BClassWithASubMixin,
                    ["onlyBClassWithASubMixin"],
                    [
                        lg2.BClassWithASubMixin,
                        tests.examples.lineage2,
                        tests.examples,
                        tests,
                        lg.ASubMixin,
                        tests.examples.lineage,
                        lg.AMixin,
                    ],
                )

                self.assert_finds(
                    lineage,
                    lg.ASubClassOverride,
                    ["aMethod", "onlyASubClassOverride"],
                    [
                        lg.ASubClassOverride,
                        tests.examples.lineage,
                        tests.examples,
                        tests,
                        lg.AClass,
                    ],
                )

                self.assert_finds(
                    lineage,
                    lg.AGrandChildClassOverride,
                    ["aMethod", "onlyAGrandChildClassOverride"],
                    [
                        lg.AGrandChildClassOverride,
                        tests.examples.lineage,
                        tests.examples,
                        tests,
                        lg.ASubClass,
                        lg.AClass,
                    ],
                )

                self.assert_finds(
                    lineage,
                    lg2.BSubClassOverride,
                    ["aMethod", "onlyBSubClassOverride"],
                    [
                        lg2.BSubClassOverride,
                        tests.examples.lineage2,
                        tests.examples,
                        tests,
                        lg.AClass,
                        tests.examples.lineage,
                    ],
                )

                self.assert_finds(
                    lineage,
                    lg2.BGrandChildClassOverride,
                    ["aMethod", "onlyBGrandChildClassOverride"],
                    [
                        lg2.BGrandChildClassOverride,
                        tests.examples.lineage2,
                        tests.examples,
                        tests,
                        lg2.BSubClass,
                        lg.AClass,
                        tests.examples.lineage,
                    ],
                )

                self.assert_finds(
                    lineage,
                    lg.AClassWithMixinOverride,
                    ["aMethod", "onlyAClassWithMixinOverride"],
                    [
                        lg.AClassWithMixinOverride,
                        tests.examples.lineage,
                        tests.examples,
                        tests,
                        lg.AMixin,
                    ],
                )

                self.assert_finds(
                    lineage,
                    lg.AClassWithSubMixinOverride,
                    ["aMethod", "onlyAClassWithSubMixinOverride"],
                    [
                        lg.AClassWithSubMixinOverride,
                        tests.examples.lineage,
                        tests.examples,
                        tests,
                        lg.ASubMixin,
                        lg.AMixin,
                    ],
                )

                self.assert_finds(
                    lineage,
                    lg2.BClassWithASubMixinOverride,
                    ["aMethod", "onlyBClassWithASubMixinOverride"],
                    [
                        lg2.BClassWithASubMixinOverride,
                        tests.examples.lineage2,
                        tests.examples,
                        tests,
                        lg.ASubMixin,
                        tests.examples.lineage,
                        lg.AMixin,
                    ],
                )

                self.assert_finds(
                    lineage,
                    lg.AClassWithMultipleMixins,
                    ["onlyAClassWithMultipleMixins"],
                    [
                        lg.AClassWithMultipleMixins,
                        tests.examples.lineage,
                        tests.examples,
                        tests,
                        lg.ASubMixin,
                        lg.AMixin,
                        lg.BMixin,
                    ],
                )
