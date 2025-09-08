from core.lexer import lexicon, Token

class Interpreter:
    def __init__(self):
        self.variables = {}

    """
    Нормализация чисел
    """
    def _normalize_float(self, value):
        if isinstance(value, float):
            value = round(value, 10)
            value = float(f"{value:.10g}")
        return value

    """
    Обработка токенов
    """
    def eval_expr(self, tokens, line_num, line_text, postfix=False):

        if not tokens:
            return ""

        def apply_op(a, op, b):
            match op:
                case '+':
                    if isinstance(a, (int,float)) and isinstance(b,(int,float)):
                        return self._normalize_float(a + b)
                    raise TypeError(f"TypeError in Line {line_num}: Invalid operator's value")
                case ',+':
                    if isinstance(a, (int,float)) and isinstance(b,(int,float)):
                        return self._normalize_float(float(a) + float(b))
                    raise TypeError(f"TypeError in Line {line_num}: Invalid operator's value")
                case ',-':
                    if isinstance(a, (int,float)) and isinstance(b,(int,float)):
                        return self._normalize_float(float(a) - float(b))
                    raise TypeError(f"TypeError in Line {line_num}: Invalid operator's value")
                case '$+':
                    return str(a) + str(b)
                case '-':
                    if isinstance(a, (int,float)) and isinstance(b,(int,float)):
                        return self._normalize_float(a - b)
                    raise TypeError(f"TypeError in Line {line_num}: Invalid operator's value")
                case '*':
                    if isinstance(a, (int,float)) and isinstance(b,(int,float)):
                        return self._normalize_float(a * b)
                    raise TypeError(f"TypeError in Line {line_num}: Invalid operator's value")
                case '/':
                    if isinstance(a, (int,float)) and isinstance(b,(int,float)):
                        return self._normalize_float(a / b)
                    raise TypeError(f"TypeError in Line {line_num}: Invalid operator's value")
                # логические и сравнения
                case '==':
                    return a == b
                case '!=':
                    return a != b
                case '<':
                    return a < b
                case '<=':
                    return a <= b
                case '>':
                    return a > b
                case '>=':
                    return a >= b
                case _:
                    raise SyntaxError(f"Unknown operator {op}")

        precedence = {
            '+': 1, '-': 1,
            ',+': 2, ',-': 2,
            '*': 3, '/': 3,
            '==': 0, '!=': 0, '<': 0, '<=': 0, '>': 0, '>=': 0,
            '$+': 4
        }

        output, ops = [], []

        for tok in tokens:
            match tok.type:
                case "NUMBER" | "STRING" | "BOOL":
                    output.append(tok.value)
                case "ID":
                    if tok.value in self.variables:
                        output.append(self.variables[tok.value])
                    else:
                        raise NameError(f"NameError in Line {line_num}: Undefined variable '{tok.value}'\n> {line_text}")
                case "OPER":
                    while ops and ops[-1] != '(' and precedence.get(ops[-1], 0) >= precedence.get(tok.value, 0):
                        output.append(ops.pop())
                    ops.append(tok.value)
                case "LPAREN":
                    ops.append('(')
                case "RPAREN":
                    while ops and ops[-1] != '(':
                        output.append(ops.pop())
                    if not ops or ops[-1] != '(':
                        raise SyntaxError(f"SyntaxError in Line {line_num}: Mismatched parentheses\n> {line_text}")
                    ops.pop()
                case _:
                    raise SyntaxError(f"SyntaxError in Line {line_num}: Invalid token {tok}\n> {line_text}")

        while ops:
            if ops[-1] in ('(', ')'):
                raise SyntaxError(f"SyntaxError in Line {line_num}: Mismatched parentheses\n> {line_text}")
            output.append(ops.pop())

        if postfix:
            print("Postfix stack:", output)

        stack = []
        for item in output:
            if isinstance(item, (int, float, bool)) or (isinstance(item, str) and item not in (',-',',+','$+','==','!=','<','<=','>','>=')):
                stack.append(item)
            else:
                try:
                    b = stack.pop()
                    a = stack.pop()
                    stack.append(apply_op(a, item, b))
                except Exception:
                    raise SyntaxError(f"SyntaxError in Line {line_num}: Invalid expression\n > {line_text}")

        if len(stack) != 1:
            raise SyntaxError(f"StackError in Line {line_num}: Invalid stack expression\n> {line_text}")

        result = stack[0]
        return self._normalize_float(result)

    """
    Запуск интерпритатора
    """
    def run(self, code, postfix=False):
        lines = code.strip().splitlines()
        if not lines or not lines[0].startswith("!TF:"):
            raise SyntaxError("File must start with !TF:")

        for line_num, line in enumerate(lines[1:], start=2):
            if not line.strip():
                continue

            tokens = list(lexicon(line))
            if not tokens:
                continue

            try:
                match tokens[0].type:
                    case "ECHO":
                        result = self.eval_expr(tokens[1:], line_num, line, postfix)
                        print(result)
                    case "ID" if len(tokens) >= 3 and tokens[1].value == "@=":
                        var_name = tokens[0].value
                        expr_tokens = tokens[2:]
                        self.variables[var_name] = self._normalize_float(
                            self.eval_expr(expr_tokens, line_num, line)
                        )
                    case _:
                        raise SyntaxError(f"Line {line_num}: Unknown statement\n> {line}")
            except Exception as e:
                print(f"~ ~ ~ ~ ~ ~ ~ ~\n{e}")
                break
