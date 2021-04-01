from functools import cached_property


# A sample class
class Sample():

    def __init__(self):
        self.result = 50

    @cached_property
    # a method to increase the value of
    # result by 50
    def increase(self):
        self.result = self.result + 50
        print("Called")
        return self.result


# obj is an instance of the class sample
obj = Sample()
print(obj.increase)
print(obj.increase)
print(obj.increase)