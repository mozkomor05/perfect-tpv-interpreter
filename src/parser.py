from lexer import Lexer, Token, TokenType
from ast import Program, Statement, Expression, NumericLiteral, \
    Identifier, BinaryExpression, ProcedureDeclaration, IfBlock, \
    WhileBlock, Assignment, Command, NoOp, UnaryExpression, CallExpression


class Parser:
    def __init__(self, source: str):
        self.tokens = Lexer(source).tokenize()
        self.program = Program()

    def parse(self) -> Program:
        while self.at().type != TokenType.EOF:
            self.program.statements.append(self.parse_statement())

        return self.program

    def eat(self, token_type: TokenType = None, error_message: str = None) -> Token:
        if not self.tokens:
            raise Exception('Unexpected end of input')

        token = self.tokens.pop(0)

        if token_type and token.type != token_type:
            raise Exception(error_message or f'Unexpected token: {token}')

        return token

    def at(self, i=0) -> Token:
        return self.tokens[i] if self.tokens else None

    def parse_statement(self) -> Statement:
        statement = self.parse_statement_internal()

        if self.at().type == TokenType.EOL:
            self.eat()
        elif self.at().type != TokenType.EOF:
            raise Exception(f'Unexpected token: {self.at()}')

        return statement

    def parse_statement_internal(self) -> Statement:
        if self.at().type == TokenType.If:
            return self.parse_if_statement()

        if self.at().type == TokenType.While:
            return self.parse_while_statement()

        if self.at().type == TokenType.Procedure:
            return self.parse_procedure_declaration()

        if self.at().type == TokenType.Identifier and \
                self.at(1) is not None and self.at(1).type == TokenType.Equals:
            return self.parse_assignment()

        # return token may specify the end of procedure OR may be used as
        # command to return early
        if self.at().type in (TokenType.Identifier, TokenType.Return):
            return self.parse_command()

        return NoOp()

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
            return self.parse_call_expression(member)

        return member

    def parse_call_expression(self, member: Expression) -> Expression:
        self.eat()

        args = self.parse_args() if self.at().type != TokenType.CloseParen else []

        self.eat(TokenType.CloseParen, 'Expected closing parenthesis')

        return CallExpression(member, args)

    def parse_primary_expression(self) -> Expression:
        if self.at().type == TokenType.Number:
            return self.parse_number()

        if self.at().type == TokenType.BinaryOperator and self.at().value == '-':
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
                 'Unexpected token found inside parenthesized expression. Expected closing parenthesis.')
        return expression
