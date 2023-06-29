from parser import Parser
from PIL import Image, ImageDraw


class Interpreter():
    def __init__(self, source: str):
        self.ast = Parser(source).parse()
        self.GLOBAL_SCOPE = {}
        self.image = None

    def run(self) -> Image:
        print(self.ast)

        # TODO: Implement interpreter

        if self.image is None:
            raise Exception(
                "Missing or unreachable SIZE command, cannot create image")

        return self.image
