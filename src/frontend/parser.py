from frontend.lexer import Lexer, TokenType, Token
from typing import Optional
from frontend.tpv_ast import CallProcedure, IntDeclaration, Program, \
    Return, Statement, Expression, NumericLiteral, \
    Identifier, BinaryExpression, ProcedureDeclaration, IfBlock, \
    WhileBlock, Assignment, Command, NoOp, UnaryExpression, CallFn, \
    PushStack, PopStack


class Parser:
    def __init__(self, source: str):
        self.tokens = Lexer(source).tokenize()
        self.program = Program()

    def parse(self) -> Program:
        while self.at().type != TokenType.EOF:
            self.program.statements.append(self.parse_statement())

        return self.program

    def eat(self, token_type: Optional[TokenType] = None,
            error_message: Optional[str] = None) -> Token:
        if not self.tokens:
            raise Exception('Unexpected end of input')

        token = self.tokens.pop(0)

        if token_type and token.type != token_type:
            raise Exception(error_message or f'Unexpected token: {token}')

        return token

    def at(self) -> Token:
        if not self.tokens:
            raise Exception('Unexpected end of input')

        return self.tokens[0]

    def peek(self, i: int) -> Optional[Token]:
        return self.tokens[i] if len(self.tokens) > i else None

    def parse_statement(self) -> Statement:
        statement = self.parse_statement_internal()

        if self.at().type == TokenType.EOL:
            self.eat()
        elif self.at().type != TokenType.EOF:
            raise Exception(f'Unexpected token: {self.at()}')

        return statement

    def parse_statement_internal(self) -> Statement:
        if self.at().type == TokenType.Int:
            return self.parse_int_declaration()

        if self.at().type == TokenType.If:
            return self.parse_if_statement()

        if self.at().type == TokenType.While:
            return self.parse_while_statement()

        if self.at().type == TokenType.Procedure:
            return self.parse_procedure_declaration()

        if self.at().type == TokenType.Call:
            return self.parse_call_statement()

        if self.at().type == TokenType.Return:
            return self.parse_return_statement()

        if self.at().type == TokenType.Push:
            return self.parse_push_statement()

        if self.at().type == TokenType.Pop:
            return self.parse_pop_statement()

        if self.at().type == TokenType.Identifier and \
                self.peek(1) is not None and \
                self.peek(1).type == TokenType.Equals:
            return self.parse_assignment()

        if self.at().type == TokenType.Identifier:
            return self.parse_command()

        return NoOp()

    def parse_int_declaration(self) -> IntDeclaration:
        self.eat()

        vars = [self.parse_identifier()]

        while self.at().type == TokenType.Comma:
            self.eat()
            vars.append(self.parse_identifier())

        return IntDeclaration(vars)

    def parse_if_statement(self) -> IfBlock:
        self.eat()

        condition = self.parse_expression()

        self.eat(TokenType.EOL, 'Expected new line after if condition')

        body = []

        while self.at().type not in (TokenType.Else, TokenType.Endif, TokenType.EOF):
            body.append(self.parse_statement())

        else_body = []

        if self.at().type == TokenType.Else:
            self.eat()

            while self.at().type not in (TokenType.Endif, TokenType.EOF):
                else_body.append(self.parse_statement())

        self.eat(TokenType.Endif, 'Expected ENDIF after if statement')

        return IfBlock(condition, body, else_body)

    def parse_procedure_declaration(self) -> ProcedureDeclaration:
        self.eat()

        name = self.parse_identifier()

        self.eat(TokenType.EOL, 'Expected new line after procedure name')

        body = []

        while self.at().type not in (TokenType.Return, TokenType.EOF):
            body.append(self.parse_statement())

        self.eat(TokenType.Return, 'Expected RETURN after procedure body')

        return ProcedureDeclaration(name, body)

    def parse_while_statement(self) -> WhileBlock:
        self.eat()

        condition = self.parse_expression()

        self.eat(TokenType.EOL, 'Expected new line after while condition')

        body = []

        while self.at().type not in (TokenType.Endwhile, TokenType.EOF):
            body.append(self.parse_statement())

        self.eat(TokenType.Endwhile, 'Expected LOOP after while statement')

        return WhileBlock(condition, body)

    def parse_assignment(self) -> Statement:
        identifier = self.parse_identifier()

        self.eat()  # Equal sign

        expression = self.parse_expression()

        return Assignment(identifier, expression)

    def parse_call_statement(self) -> CallProcedure:
        self.eat()

        name = self.parse_identifier()

        return CallProcedure(name)

    def parse_return_statement(self) -> Return:
        self.eat()

        return Return()

    def parse_push_statement(self) -> PushStack:
        self.eat()

        args = self.parse_args()

        return PushStack(args)

    def parse_pop_statement(self) -> PopStack:
        self.eat()

        vars = [self.parse_identifier()]

        while self.at().type == TokenType.Comma:
            self.eat()
            vars.append(self.parse_identifier())

        return PopStack(vars)

    def parse_command(self) -> Command:
        cmd = self.parse_identifier()
        args = self.parse_args() if self.at().type not in (
            TokenType.EOL, TokenType.EOF) else []

        return Command(cmd, args)

    def parse_expression(self) -> Expression:
        return self.parse_additive_expression()

    def parse_additive_expression(self) -> Expression:
        left = self.parse_multiplicative_expression()

        while self.tokens and self.at().value in ('+', '-'):
            operator = self.eat().value
            right = self.parse_multiplicative_expression()
            left = BinaryExpression(operator, left, right)

        return left

    def parse_multiplicative_expression(self) -> Expression:
        left = self.parse_call_member_expression()

        while self.tokens and self.at().value in ('*', '/'):
            operator = self.eat().value
            right = self.parse_call_member_expression()
            left = BinaryExpression(operator, left, right)

        return left

    def parse_call_member_expression(self) -> Expression:
        member = self.parse_primary_expression()

        if self.at().type == TokenType.OpenParen:
            if not isinstance(member, Identifier):
                raise Exception(f'Unexpected "(" after {member}')

            return self.parse_call_expression(member)

        return member

    def parse_call_expression(self, member: Identifier) -> Expression:
        self.eat()

        args = self.parse_args() \
            if self.at().type != TokenType.CloseParen else []

        self.eat(TokenType.CloseParen, 'Expected closing parenthesis')

        return CallFn(member, args)

    def parse_primary_expression(self) -> Expression:
        if self.at().type == TokenType.Number:
            return self.parse_number()

        if self.at().type == TokenType.BinaryOperator and \
                self.at().value == '-':
            return self.parse_negation()

        if self.at().type == TokenType.Identifier:
            return self.parse_identifier()

        if self.at().type == TokenType.OpenParen:
            return self.parse_parenthesized_expression()

        raise Exception(f'Unexpected token: {self.at()}')

    def parse_negation(self) -> Expression:
        self.eat()
        return UnaryExpression('-', self.parse_expression())

    def parse_number(self) -> NumericLiteral:
        return NumericLiteral(self.eat().value)

    def parse_identifier(self) -> Identifier:
        return Identifier(self.eat().value)

    def parse_args(self) -> list[Expression]:
        args = [self.parse_expression()]

        while self.at().type == TokenType.Comma:
            self.eat()
            args.append(self.parse_expression())

        return args

    def parse_parenthesized_expression(self) -> Expression:
        self.eat()
        expression = self.parse_expression()
        self.eat(TokenType.CloseParen,
                 'Unexpected token found inside parenthesized expression. '
                 'Expected closing parenthesis.')
        return expression
