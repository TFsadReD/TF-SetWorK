from core.lexer import lexicon, Token

class Interpreter:
    def __init__(self):
        self.variables = {}

    def eval_expr(self, tokens, line_num, line_text):
        """Вычисляет выражение, заменяя переменные значениями."""
        if not tokens:  # если список пуст → echo без аргументов
            return ""   # вернём пустую строку

        expr_parts = []
        for tok in tokens:
            if tok.type == "ID":
                if tok.value in self.variables:
                    expr_parts.append(str(self.variables[tok.value]))
                else:
                    raise NameError(
                        f"Line {line_num}: Undefined variable '{tok.value}'\n> {line_text}"
                    )
            else:
                expr_parts.append(str(tok.value))

        expr = "".join(expr_parts)
        try:
            return eval(expr)
        except Exception as e:
            raise SyntaxError(
                f"Line {line_num}: Invalid expression '{expr}'\n> {line_text}\n{e}"
            )

    def run(self, code):
        lines = code.strip().splitlines()

        # Проверяем заголовок
        if not lines or not lines[0].startswith("!TF:"):
            raise SyntaxError("File must start with !TF:")

        # Выполняем построчно
        for line_num, line in enumerate(lines[1:], start=2):  # начиная со 2 строки
            if not line.strip():
                continue

            tokens = list(lexicon(line))
            if not tokens:
                continue

            try:
                # echo <expr> или echo
                if tokens[0].type == "ECHO":
                    result = self.eval_expr(tokens[1:], line_num, line)
                    print(result)

                # <id> @= <expr>
                elif tokens[0].type == "ID" and len(tokens) >= 3 and tokens[1].value == "@=":
                    var_name = tokens[0].value
                    expr_tokens = tokens[2:]
                    self.variables[var_name] = self.eval_expr(expr_tokens, line_num, line)

                else:
                    raise SyntaxError(
                        f"Line {line_num}: Unknown statement\n> {line}"
                    )

            except Exception as e:
                raise e
