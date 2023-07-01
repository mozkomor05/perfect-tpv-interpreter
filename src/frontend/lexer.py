from enum import Enum, auto


class TokenType(Enum):
    Number = auto()
    Identifier = auto()
    Equals = auto()
    OpenParen = auto()
    CloseParen = auto()
    BinaryOperator = auto()

    # Keywords
    Int = auto()
    If = auto()
    Else = auto()
    Endif = auto()
    While = auto()
    Endwhile = auto()
    Procedure = auto()
    Return = auto()
    Call = auto()
    Push = auto()
    Pop = auto()

    Comma = auto()

    EOL = auto()
    EOF = auto()


KEYWORDS = {
    'int': TokenType.Int,
    'if': TokenType.If,
    'else': TokenType.Else,
    'endif': TokenType.Endif,
    'while': TokenType.While,
    'loop': TokenType.Endwhile,
    'procedure': TokenType.Procedure,
    'return': TokenType.Return,
    'call': TokenType.Call,
    'push': TokenType.Push,
    'pop': TokenType.Pop,
}


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f'{self.type.name}: {self.value}'

    def __repr__(self):
        return f'<Token: type = {self.type.name}, value = {self.value}>'


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = -1
        self.ch = ''
        self.next_char()

    def next_char(self):
        self.pos += 1
        self.ch = self.text[self.pos] if self.pos < len(self.text) else ''

    def eat_whitespace(self):
        while self.ch != '':
            if self.ch in [' ', '\t', '\r']:
                self.next_char()
            else:
                break

    def get_next_token(self):
        while self.ch != '':
            self.eat_whitespace()

            SINGLE_CHAR_TOKENS = {
                TokenType.EOL: ['\n'],
                TokenType.Equals: ['='],
                TokenType.OpenParen: ['('],
                TokenType.CloseParen: [')'],
                TokenType.Comma: [','],
                TokenType.BinaryOperator: ['+', '-', '*', '/'],
            }

            for token_type, chars in SINGLE_CHAR_TOKENS.items():
                if self.ch in chars:
                    token = Token(token_type, self.ch)
                    self.next_char()
                    return token

            if self.ch.isdigit():
                return Token(TokenType.Number, self.get_number())

            if self.ch.isalpha():
                identifier = self.get_identifier()

                if identifier == 'rem':
                    while self.ch != '\n':
                        self.next_char()
                    self.next_char()
                    continue

                if identifier in KEYWORDS:
                    return Token(KEYWORDS[identifier], identifier)

                return Token(TokenType.Identifier, identifier)

            raise Exception(f'Unknown token: {self.ch}')

        return Token(TokenType.EOF, '')

    def get_number(self):
        result = ''
        while self.ch.isdigit():
            result += self.ch
            self.next_char()
        return int(result)

    def get_identifier(self):
        result = ''
        while self.ch.isalnum():
            result += self.ch
            self.next_char()
        return result.lower()

    def tokenize(self):
        tokens = []

        self.text = self.text.replace(';', '\n')

        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens
