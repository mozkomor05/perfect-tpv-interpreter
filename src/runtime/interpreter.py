from frontend.parser import Parser
from PIL import Image
from runtime.enviroment import TPVEnviroment
from runtime.exceptions import StopException, ReturnException
from frontend.tpv_ast import Assignment, BinaryExpression, CallFn, \
    CallProcedure, Expression, Identifier, IfBlock, NoOp, \
    NumericLiteral, PopStack, ProcedureDeclaration, PushStack, Return, \
    IntDeclaration, Statement, Command, UnaryExpression, WhileBlock
import numbers


class Interpreter():
    def __init__(self, source: str):
        self.ast = Parser(source).parse()
        self.enviroment = TPVEnviroment()
        self.procedures = {}

    def run(self) -> Image.Image:
        self.load_procedures()

        try:
            for statement in self.ast.statements:
                self.evaluate(statement)
        except StopException:
            pass

        if self.enviroment.image is None:
            raise Exception(
                "Missing or unreachable SIZE command, cannot create image")

        return self.enviroment.image.transpose(Image.FLIP_TOP_BOTTOM)

    def load_procedures(self):
        for statement in self.ast.statements:
            if isinstance(statement, ProcedureDeclaration):
                self.procedures[statement.name.name] = statement

    def evaluate(self, statement: Statement):
        if isinstance(statement, Expression):
            self.evaluate_expression(statement)
            return

        if isinstance(statement, Command):
            self.execute_command(statement)
            return

        if isinstance(statement, IntDeclaration):
            self.evaluate_int_declaration(statement)
            return

        if isinstance(statement, IfBlock):
            self.evaluate_if_block(statement)
            return

        if isinstance(statement, WhileBlock):
            self.evaluate_while_block(statement)
            return

        if isinstance(statement, Assignment):
            self.evaluate_assignment(statement)
            return

        if isinstance(statement, CallProcedure):
            self.evaluate_call_procedure(statement)
            return

        if isinstance(statement, PushStack):
            self.evaluate_push_stack(statement)
            return

        if isinstance(statement, PopStack):
            self.evaluate_pop_stack(statement)
            return

        if isinstance(statement, Return):
            raise ReturnException()

        # skip as procedures are loaded in advance
        if isinstance(statement, ProcedureDeclaration):
            return

        if isinstance(statement, NoOp):
            return

        raise Exception(f"Unimplemented statement type: {type(statement)}")

    def evaluate_expression(self, expression: Expression):
        if isinstance(expression, NumericLiteral):
            return expression.value

        if isinstance(expression, Identifier):
            return self.enviroment.get_variable(expression.name)

        if isinstance(expression, BinaryExpression):
            return self.evaluate_binary_expression(expression)

        if isinstance(expression, UnaryExpression):
            return self.evaluate_unary_expression(expression)

        if isinstance(expression, CallFn):
            return self.call_function(expression)

        raise Exception(f"Unimplemented expression type: {type(expression)}")

    def evaluate_binary_expression(self,
                                   expression: BinaryExpression) -> float:
        lhs = self.evaluate_expression(expression.left)
        rhs = self.evaluate_expression(expression.right)

        if not isinstance(lhs, numbers.Real) or not isinstance(
                rhs, numbers.Real):
            raise Exception("Cannot perform binary operation"
                            " on non-numeric values")

        if expression.operator == "+":
            return lhs + rhs

        if expression.operator == "-":
            return lhs - rhs

        if expression.operator == "*":
            return lhs * rhs

        if expression.operator == "/":
            return lhs / rhs

        raise Exception(
            f"Unimplemented binary expression operator: {expression.operator}")

    def evaluate_unary_expression(self, expression: UnaryExpression) -> float:
        value = self.evaluate_expression(expression.expression)

        if expression.operator == "-":
            return -value

        raise Exception(
            f"Unimplemented unary expression operator: {expression.operator}")

    def call_function(self, expression: CallFn) -> float:
        name = expression.name.name
        args = self.evaluate_args(expression.args)

        return self.enviroment.call_function(name, args)

    def evaluate_int_declaration(self, declaration: IntDeclaration):
        for var in declaration.vars:
            self.enviroment.declare_variable(var.name)

    def execute_command(self, command: Command):
        name = command.command.name
        args = self.evaluate_args(command.args)

        self.enviroment.call_command(name, args)

    def evaluate_args(self, args: list[Expression]) -> list:
        return list(map(self.evaluate_expression, args))

    def evaluate_if_block(self, ifblock: IfBlock):
        condition = self.evaluate_expression(ifblock.condition)

        if condition > 0:
            for statement in ifblock.body:
                self.evaluate(statement)
        else:
            for statement in ifblock.else_body:
                self.evaluate(statement)

    def evaluate_while_block(self, whileblock: WhileBlock):
        while self.evaluate_expression(whileblock.condition) > 0:
            for statement in whileblock.body:
                self.evaluate(statement)

    def evaluate_call_procedure(self, call: CallProcedure):
        name = call.name.name

        if name in self.procedures:
            try:
                for statement in self.procedures[name].body:
                    self.evaluate(statement)
            except ReturnException:
                pass
        else:
            raise Exception(f"Procedure {name} not found")

    def evaluate_assignment(self, assignment: Assignment):
        value = self.evaluate_expression(assignment.expression)
        self.enviroment.assign_variable(assignment.identifier.name, value)

    def evaluate_push_stack(self, push: PushStack):
        args = self.evaluate_args(push.args)
        self.enviroment.extend_stack(args)

    def evaluate_pop_stack(self, pop: PopStack):
        for var in pop.vars:
            self.enviroment.assign_variable(
                var.name, self.enviroment.pop_stack())
