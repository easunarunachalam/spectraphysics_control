class FakeDevice:
    def __init__(self):
        ...

    def write(self, command: str):
        return command

    def query(self, command: str):
        return 123
