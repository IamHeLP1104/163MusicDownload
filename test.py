from sys import argv


class A:
    def __init__(self, cls):
        del cls.name
class B:
    def __init__(self):
        self.name = 'B'
        print(self.name)
        A(self)
        print(self.name)
# B()
class C:
    def __init__(self):
        self
print(argv)