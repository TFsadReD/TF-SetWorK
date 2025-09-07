from collections import namedtuple
import re

Token = namedtuple('Token', ['type', 'value'])

TOKEN_SPECIFICATION = [
    ('HEADER', r'!TF:'),                                 # начало файла
    ('NUMBER', r'\d+(\.\d*)?'),                          # числа
    ('STRING', r'"[^"\n]*"'),                            # строковые литералы в кавычках
    ('ID', r'[a-zA-Z_][a-zA-Z_0-9]*'),                   # переменные
    ('OPER', r'[@]=|==|!=|<=|>=|,\+|\$\+|[+\-*/=<>]'),   # операции
    ('NEWLINE', r'\n'),                                  # новая строка
    ('LPAREN', r'\('),                                   # (
    ('RPAREN', r'\)'),                                   # )
    ('SKIP', r'[ \t]+'),                                 # пробелы
    ('MISSMATCH', r'.'),                                 # всё остальное
]

def lexicon(code):
    # Разбивает исходный код на токены
    reg_token = "|".join(
        f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPECIFICATION
    )

    for match in re.finditer(reg_token, code):
        kind = match.lastgroup
        value = match.group()

        match kind:
            case 'NUMBER':
                value = float(value) if '.' in value else int(value)
                yield Token(kind, value)

            case 'STRING':
                yield Token("STRING", value.strip('"'))

            case 'ID':
                if value == "echo":
                    yield Token("ECHO", value)
                else:
                    yield Token("ID", value)

            case 'HEADER':
                yield Token("HEADER", value)

            case 'OPER':
                yield Token(kind, value)

            case 'NEWLINE':
                yield Token("NEWLINE", value)

            case 'SKIP':
                continue

            case 'LPAREN' | 'RPAREN':
                yield Token(kind, value)

            case 'MISSMATCH':
                raise SyntaxError(f"Unexpected token: {value!r}")
