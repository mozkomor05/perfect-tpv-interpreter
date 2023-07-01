from abc import ABC, abstractmethod


class Statement(ABC):
    @abstractmethod
    def __init__(self):
        pass

    def __repr__(self):
        items = ("%s = %r" % (k, v) for k, v in self.__dict__.items())
        return "<%s: {%s}>" % (self.__class__.__name__, ', '.join(items))


class Program(Statement):
    def __init__(self):
        self.statements = []


class NoOp(Statement):
    def __init__(self):
        pass


class Expression(Statement):
    pass


class NumericLiteral(Expression):
    def __init__(self, value: int):
        self.value = value


class Identifier(Expression):
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Identifier) and self.name == other.name


class BinaryExpression(Expression):
    def __init__(self, operator: str, left: Expression, right: Expression):
        self.operator = operator
        self.left = left
        self.right = right


class UnaryExpression(Expression):
    def __init__(self, operator: str, expression: Expression):
        self.operator = operator
        self.expression = expression


class CallFn(Expression):
    """
    Represents a function call, e.g. `sin(90)`.
    To not be confused with procedure CALL command which is a statement.
    """

    def __init__(self, name: Identifier, args: list[Expression]):
        self.name = name
        self.args = args


class CallProcedure(Statement):
    """
    Represents a procedure call, e.g. `CALL foo`.
    """

    def __init__(self, name: Identifier):
        self.name = name


class Return(Statement):
    def __init__(self):
        pass


class IntDeclaration(Statement):
    def __init__(self, vars: list[Identifier]):
        self.vars = vars


class IfBlock(Statement):
    def __init__(self, condition: Expression, body: list[Statement], else_body: list[Statement]):
        self.condition = condition
        self.body = body
        self.else_body = else_body


class WhileBlock(Statement):
    def __init__(self, condition: Expression, body: list[Statement]):
        self.condition = condition
        self.body = body


class ProcedureDeclaration(Statement):
    def __init__(self, name: Identifier, body: list[Statement]):
        self.name = name
        self.body = body


class Assignment(Statement):
    def __init__(self, identifier: Identifier, expression: Expression):
        self.identifier = identifier
        self.expression = expression


class Command(Statement):
    def __init__(self, command: Identifier, args: list[Expression]):
        self.command = command
        self.args = args


class PushStack(Statement):
    def __init__(self, args: list[Expression]):
        self.args = args


class PopStack(Statement):
    def __init__(self, vars: list[Identifier]):
        self.vars = vars
