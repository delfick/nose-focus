from tests.examples.lineage import AClass, ASubMixin

class BSubClass(AClass):
    def onlyBSubClass(self):
        pass

class BSubClassOverride(AClass):
    def aMethod(self):
        pass

    def onlyBSubClassOverride(self):
        pass

class BGrandChildClass(BSubClass):
    def onlyBGrandChildClass(self):
        pass

class BGrandChildClassOverride(BSubClass):
    def aMethod(self):
        pass

    def onlyBGrandChildClassOverride(self):
        pass

class BClassWithASubMixin(ASubMixin):
    def onlyBClassWithASubMixin(self):
        pass

class BClassWithASubMixinOverride(ASubMixin):
    def aMethod(self):
        pass

    def onlyBClassWithASubMixinOverride(self):
        pass
