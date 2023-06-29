from parser import Parser


class Interpreter():
    def __init__(self, source: str):
        self.ast = Parser(source).parse()
        self.GLOBAL_SCOPE = {}

    def run(self):
        print(self.ast)
