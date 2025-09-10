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

        def apply_op(a, op, b=None):
            match op:
                case '+':
                    if isinstance(a, (int,float)) and isinstance(b,(int,float)):
                        return self._normalize_float(a + b)
                    raise TypeError(f"TypeError in Line {line_num}: Invalid operator's value\n > {line_text}")
                case ',+':
                    if isinstance(a, (int,float)) and isinstance(b,(int,float)):
                        return self._normalize_float(float(a) + float(b))
                    raise TypeError(f"TypeError in Line {line_num}: Invalid operator's value\n > {line_text}")
                case ',-':
                    if isinstance(a, (int,float)) and isinstance(b,(int,float)):
                        return self._normalize_float(float(a) - float(b))
                    raise TypeError(f"TypeError in Line {line_num}: Invalid operator's value\n > {line_text}")
                case '$+':
                    return str(a) + str(b)
                case '-':
                    if isinstance(a, (int,float)) and isinstance(b,(int,float)):
                        return self._normalize_float(a - b)
                    raise TypeError(f"TypeError in Line {line_num}: Invalid operator's value\n > {line_text}")
                case '*':
                    if isinstance(a, (int,float)) and isinstance(b,(int,float)):
                        return self._normalize_float(a * b)
                    raise TypeError(f"TypeError in Line {line_num}: Invalid operator's value\n > {line_text}")
                case '/':
                    if isinstance(a, (int,float)) and isinstance(b,(int,float)):
                        return self._normalize_float(a / b)
                    raise TypeError(f"TypeError in Line {line_num}: Invalid operator's value\n > {line_text}")

                case '==': return a == b
                case '!=': return a != b
                case '<':  return a < b
                case '<=': return a <= b
                case '>':  return a > b
                case '>=': return a >= b

                case 'and': return bool(a) and bool(b)
                case 'or':  return bool(a) or bool(b)
                case 'not': return not bool(a)

                case _:
                    raise SyntaxError(f"SyntaxError in Line {line_num}: Unknown operator {op}\n > {line_text}")

        precedence = {
            '+': 1, '-': 1,
            ',+': 2, ',-': 2,
            '*': 3, '/': 3,
            '==': 0, '!=': 0, '<': 0, '<=': 0, '>': 0, '>=': 0,
            'and': -1, 'or': -2, 'not': 4,
            '$+': 5
        }

        output, ops = [], []

        for tok in tokens:
            match tok.type:
                case "NUMBER" | "STRING" | "BOOL":
                    output.append(tok.value)
                case "ID":
                    if tok.value in ("and", "or", "not"):
                        while ops and ops[-1] != '(' and precedence.get(ops[-1], 0) >= precedence.get(tok.value, 0):
                            output.append(ops.pop())
                        ops.append(tok.value)
                    elif tok.value in self.variables:
                        output.append(self.variables[tok.value])
                    else:
                        raise NameError(f"NameError in Line {line_num}: Undefined variable '{tok.value}'\n > {line_text}")
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
                        raise SyntaxError(f"SyntaxError in Line {line_num}: Mismatched parentheses\n > {line_text}")
                    ops.pop()
                case _:
                    raise SyntaxError(f"SyntaxError in Line {line_num}: Invalid token\n > {line_text}")

        while ops:
            if ops[-1] in ('(', ')'):
                raise SyntaxError(f"SyntaxError in Line {line_num}: Mismatched parentheses\n > {line_text}")
            output.append(ops.pop())

        if postfix:
            print("Postfix stack:", output)

        stack = []
        operators_check = (',-',',+','$+','==','!=','<','<=','>','>=','and','or','not')
        for item in output:
            if isinstance(item, (int, float, bool)) or (isinstance(item, str) and item not in operators_check):
                stack.append(item)
            else:
                try:
                    if item == 'not':
                        a = stack.pop()
                        stack.append(apply_op(a, item))
                    else:
                        b = stack.pop()
                        a = stack.pop()
                        stack.append(apply_op(a, item, b))
                except Exception:
                    raise SyntaxError(f"SyntaxError in Line {line_num}: Invalid expression\n > {line_text}")

        if len(stack) != 1:
            raise SyntaxError(f"StackError in Line {line_num}: Invalid stack expression\n > {line_text}")

        result = stack[0]
        return self._normalize_float(result)


    """
    Запуск интерпретатора
    """


    def run(self, code, postfix=False):
        lines = code.strip().splitlines()
        if not lines or not lines[0].startswith("!TF:"):
            raise SyntaxError("CriticalError: There is no guide determinant for the entire code")

        i = 1
        while i < len(lines):
            line_num = i + 1
            line = lines[i]

            if not line.strip():
                i += 1
                continue

            tokens = list(lexicon(line))
            if not tokens:
                i += 1
                continue

            try:
                match tokens[0].type:
                    case "ECHO":
                        result = self.eval_expr(tokens[1:], line_num, line, postfix)
                        print(result)

                    case "IF":
                        if tokens[1].type != "LPAREN":
                            raise SyntaxError(f"SyntaxError in Line {line_num}: Missing '(' after if")

                        depth = 0
                        close_index = None
                        for idx, t in enumerate(tokens[1:], start=1):
                            if t.type == "LPAREN":
                                depth += 1
                            elif t.type == "RPAREN":
                                depth -= 1
                                if depth == 0:
                                    close_index = idx
                                    break

                        if close_index is None:
                            raise SyntaxError(f"SyntaxError in Line {line_num}: Missing ')' in if condition")

                        cond_tokens = tokens[2:close_index]
                        condition = self.eval_expr(cond_tokens, line_num, line)

                        if close_index + 1 >= len(tokens) or tokens[close_index + 1].type != "LBRACE":
                            raise SyntaxError(f"SyntaxError in Line {line_num}: Missing '{{' after if condition")

                        block_lines = []
                        i += 1
                        while i < len(lines) and "}" not in lines[i]:
                            block_lines.append(lines[i])
                            i += 1
                        if i >= len(lines):
                            raise SyntaxError(f"SyntaxError: Missing '}}' for if starting at line {line_num}")

                        if condition:
                            self.run("!TF:\n" + "\n".join(block_lines), postfix=postfix)

                    case "ID" if len(tokens) >= 3 and tokens[1].value == "@=":
                        var_name = tokens[0].value
                        expr_tokens = tokens[2:]
                        value = self.eval_expr(expr_tokens, line_num, line)
                        if isinstance(value, (int, float)):
                            value = self._normalize_float(value)
                        self.variables[var_name] = value

                    case _:
                        raise SyntaxError(f"Line {line_num}: Unknown statement\n > {line}")

            except Exception as e:
                print(f"~ ~ ~ ~ ~ ~ ~ ~\n{e}")
                break
            i += 1
