from abc import ABC, abstractmethod
from PIL import Image, ImageDraw
import math
from typing import Optional, Callable, Any
from dataclasses import dataclass
from runtime.exceptions import StopException, ReturnException


@dataclass
class Method:
    method: Callable
    argc: Optional[int] = None


class Enviroment(ABC):
    def __init__(self):
        self.vars = {}
        self.commands = {}
        self.functions = {}
        self.image = None
        self.draw = None
        self.stack = []

        self.register_commands()
        self.register_functions()

    @abstractmethod
    def register_commands(self):
        pass

    @abstractmethod
    def register_functions(self):
        pass

    def call_command(self, cmd_name: str, args: list):
        if cmd_name not in self.commands:
            raise Exception(f"Command '{cmd_name}' not found")

        callable = self.commands[cmd_name]
        if callable.argc is not None and len(args) != callable.argc:
            raise Exception(f"Command '{cmd_name}' takes {callable.argc} "
                            f"arguments, {len(args)} given")

        callable.method(*args)

    def call_function(self, function: str, args: list) -> int:
        if function not in self.functions:
            raise Exception(f"Function '{function}' not found")

        callable = self.functions[function]
        if callable.argc is not None and len(args) != callable.argc:
            raise Exception(f"Function '{function}' takes {callable.argc} "
                            f"arguments, {len(args)} given")

        return callable.method(*args)

    def declare_variable(self, name: str, value: Any = 0):
        if name in self.vars:
            raise Exception(f"Variable '{name}' already declared")

        self.vars[name] = value

    def assign_variable(self, name: str, value: Any):
        if name not in self.vars:
            raise Exception(f"Variable '{name}' not found")

        self.vars[name] = value

    def get_variable(self, name: str):
        if name not in self.vars:
            raise Exception(f"Variable '{name}' not found")

        return self.vars[name]

    def push_stack(self, value: Any):
        self.stack.append(value)

    def extend_stack(self, values: list):
        self.stack.extend(values)

    def pop_stack(self) -> Any:
        if len(self.stack) == 0:
            raise Exception("Pop from empty stack")

        return self.stack.pop()


class TPVEnviroment(Enviroment):
    def __init__(self):
        super().__init__()
        self.stack = []

        COLORS = {"white", "green", "brown", "lime", "black", "blue", "gray",
                  "grey", "magenta", "red", "orange", "yellow", "gold",
                  "lightgray"}

        for color in COLORS:
            self.declare_variable(color, color)

    def register_commands(self):
        self.commands["size"] = Method(self.command_size, 2)
        self.commands["line"] = Method(self.command_line, 6)
        self.commands["rect"] = Method(self.command_rect, 6)
        self.commands["oval"] = Method(self.command_oval, 6)
        self.commands["stop"] = Method(self.command_stop, 0)

    def register_functions(self):
        self.functions["sin"] = Method(self.function_sin, 1)
        self.functions["cos"] = Method(self.function_cos, 1)

    def get_variable(self, name: str):
        if name == "top":
            return len(self.stack)

        return super().get_variable(name)

    def command_size(self, width: float, height: float):
        self.image = Image.new("RGB", (int(width), int(height)), "lightgray")
        self.draw = ImageDraw.Draw(self.image)

    def command_line(self, color: str, x1: float, y1: float, x2: float,
                     y2: float, thickness: float):
        shape = (int(x1), int(y1), int(x2), int(y2))
        self.draw.line(shape, fill=color, width=int(thickness))

    def command_rect(self, color: str, x1: float, y1: float, width: float,
                     height: float, thickness: int):
        shape = (int(x1), int(y1), int(x1 + width), int(y1 + height))
        thickness = int(thickness)

        if thickness == 0:
            self.draw.rectangle(shape, fill=color)
        else:
            self.draw.rectangle(shape, outline=color, width=thickness)

    def command_oval(self, color: str, x1: float, y1: float, width: float,
                     height: float, thickness: int):
        shape = (int(x1), int(y1), int(x1 + width), int(y1 + height))
        thickness = int(thickness)

        if thickness == 0:
            self.draw.ellipse(shape, fill=color)
        else:
            self.draw.ellipse(shape, outline=color, width=thickness)

    def command_stop(self):
        raise StopException()

    def function_sin(self, value: float) -> float:
        return math.sin(math.radians(value))

    def function_cos(self, value: float) -> float:
        return math.cos(math.radians(value))
