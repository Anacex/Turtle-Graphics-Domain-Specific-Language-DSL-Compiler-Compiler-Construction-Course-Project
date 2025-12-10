# ==============================================================
# turtle_compiler.py  (IMPROVED VERSION)
# Run: python turtle_compiler.py
# ==============================================================

import re
import sys
import math
import tkinter as tk
from tkinter import messagebox, scrolledtext
import turtle
from dataclasses import dataclass
import pprint

# ----------------------------
# Exceptions
# ----------------------------
class LexerError(Exception):
    pass

class ParserError(Exception):
    pass

class SemanticError(Exception):
    pass

class RuntimeErrorTurtle(Exception):
    pass

# ----------------------------
# Token
# ----------------------------
@dataclass
class Token:
    type: str
    value: any
    line: int
    col: int

    def __repr__(self):
        return f"{self.type}({self.value}) @ {self.line}:{self.col}"

# ----------------------------
# Token specs
# ----------------------------
TOKEN_SPEC = [
    ('NUMBER',   r'\d+(\.\d+)?'),
    ('EQ',       r'=='),
    ('NEQ',      r'!='),
    ('LE',       r'<='),
    ('GE',       r'>='),
    ('ASSIGN',   r'='),
    ('LT',       r'<'),
    ('GT',       r'>'),
    ('PLUS',     r'\+'),
    ('MINUS',    r'-'),
    ('MULT',     r'\*'),
    ('DIV',      r'/'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('SEMI',     r';'),
    ('COMMA',    r','),
    ('IDENT',    r'[A-Za-z_][A-Za-z0-9_]*'),
    ('STRING',   r'"[^"]*"'),
    ('NEWLINE',  r'\n'),
    ('SKIP',     r'[ \t\r]+'),
    ('COMMENT',  r'//[^\n]*'),
    ('MISMATCH', r'.'),
]

MASTER_RE = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC))

KEYWORDS = {
    'move': 'MOVE',
    'turn': 'TURN',
    'pen': 'PEN',
    'up': 'UP',
    'down': 'DOWN',
    'color': 'COLOR',
    'repeat': 'REPEAT',
    'if': 'IF',
    'else': 'ELSE',
    'print': 'PRINT',
    'true': 'TRUE',
    'false': 'FALSE'
}

ALLOWED_COLORS = {
    'white','black','red','green','blue','cyan','yellow','magenta','orange',
    'brown','purple','pink','gray','gold','navy','lime'
}

# ----------------------------
# Lexer
# ----------------------------
def tokenize(text):
    line = 1
    col = 1
    tokens = []

    for mo in MASTER_RE.finditer(text):
        kind = mo.lastgroup
        val = mo.group(kind)

        if kind == 'NEWLINE':
            line += 1
            col = 1
            continue
        elif kind in ('SKIP', 'COMMENT'):
            col += len(val)
            continue
        elif kind == 'NUMBER':
            val = float(val) if '.' in val else int(val)
            tok = Token('NUMBER', val, line, col)
        elif kind == 'IDENT':
            tok_type = KEYWORDS.get(val, 'IDENT')
            tok = Token(tok_type, val, line, col)
        elif kind == 'STRING':
            tok = Token('STRING', val[1:-1], line, col)
        elif kind == 'MISMATCH':
            raise LexerError(f"Unexpected character {val} at {line}:{col}")
        else:
            tok = Token(kind, val, line, col)

        tokens.append(tok)
        col += len(mo.group(0))

    tokens.append(Token('EOF', None, line, col))
    return tokens

# ----------------------------
# AST Classes
# ----------------------------
class ASTNode: pass

@dataclass
class Program(ASTNode):
    statements: list

@dataclass
class Move(ASTNode):
    expr: ASTNode

@dataclass
class Turn(ASTNode):
    expr: ASTNode

@dataclass
class Pen(ASTNode):
    up: bool

@dataclass
class Color(ASTNode):
    name: any

@dataclass
class Assign(ASTNode):
    name: str
    expr: ASTNode

@dataclass
class Repeat(ASTNode):
    count: ASTNode
    body: list

@dataclass
class If(ASTNode):
    cond: ASTNode
    then_body: list
    else_body: list

@dataclass
class Print(ASTNode):
    expr: ASTNode

@dataclass
class BinOp(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode

@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode

@dataclass
class Number(ASTNode):
    value: any

@dataclass
class Var(ASTNode):
    name: str

@dataclass
class BoolLiteral(ASTNode):
    value: bool

# ----------------------------
# Parser
# ----------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.cur = tokens[0]

    def advance(self):
        self.i += 1
        self.cur = self.tokens[self.i] if self.i < len(self.tokens) else Token('EOF', None, self.cur.line, self.cur.col)

    def expect(self, typ):
        if self.cur.type == typ:
            val = self.cur.value
            self.advance()
            return val
        raise ParserError(f"Expected {typ}, got {self.cur.type} at {self.cur.line}:{self.cur.col}")

    def parse(self):
        stmts = []
        while self.cur.type != 'EOF':
            if self.cur.type == 'SEMI':
                self.advance()
                continue
            stmts.append(self.parse_statement())
        return Program(stmts)

    # ---- statements ----
    def parse_statement(self):
        t = self.cur.type

        if t == 'MOVE':
            self.advance()
            expr = self.parse_expr()
            self.expect('SEMI')
            return Move(expr)

        if t == 'TURN':
            self.advance()
            expr = self.parse_expr()
            self.expect('SEMI')
            return Turn(expr)

        if t == 'PEN':
            self.advance()
            if self.cur.type == 'UP':
                self.advance()
                self.expect('SEMI')
                return Pen(True)
            elif self.cur.type == 'DOWN':
                self.advance()
                self.expect('SEMI')
                return Pen(False)
            raise ParserError("pen must be followed by up/down")

        if t == 'COLOR':
            self.advance()
            if self.cur.type in ('IDENT', 'STRING'):
                name = self.cur.value
                self.advance()
            else:
                raise ParserError("color requires identifier or string")
            self.expect('SEMI')
            return Color(name)

        if t == 'REPEAT':
            self.advance()
            count = self.parse_expr()
            self.expect('LBRACE')
            body = []
            while self.cur.type != 'RBRACE':
                body.append(self.parse_statement())
            self.expect('RBRACE')
            return Repeat(count, body)

        if t == 'IF':
            self.advance()
            self.expect('LPAREN')
            cond = self.parse_cond_expr()
            self.expect('RPAREN')

            self.expect('LBRACE')
            then_body = []
            while self.cur.type != 'RBRACE':
                then_body.append(self.parse_statement())
            self.expect('RBRACE')

            else_body = []
            if self.cur.type == 'ELSE':
                self.advance()
                self.expect('LBRACE')
                while self.cur.type != 'RBRACE':
                    else_body.append(self.parse_statement())
                self.expect('RBRACE')

            return If(cond, then_body, else_body)

        if t == 'IDENT':
            name = self.cur.value
            self.advance()
            self.expect('ASSIGN')
            expr = self.parse_expr()
            self.expect('SEMI')
            return Assign(name, expr)

        if t == 'PRINT':
            self.advance()
            self.expect('LPAREN')
            expr = self.parse_expr()
            self.expect('RPAREN')
            self.expect('SEMI')
            return Print(expr)

        raise ParserError(f"Unexpected token {t}")

    # ---- expressions ----
    def parse_expr(self):
        node = self.parse_term()
        while self.cur.type in ('PLUS', 'MINUS'):
            op = '+' if self.cur.type == 'PLUS' else '-'
            self.advance()
            node = BinOp(op, node, self.parse_term())
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.cur.type in ('MULT', 'DIV'):
            op = '*' if self.cur.type == 'MULT' else '/'
            self.advance()
            node = BinOp(op, node, self.parse_factor())
        return node

    def parse_factor(self):
        if self.cur.type == 'NUMBER':
            val = self.cur.value
            self.advance()
            return Number(val)
        if self.cur.type == 'IDENT':
            name = self.cur.value
            self.advance()
            return Var(name)
        if self.cur.type == 'STRING':
            val = self.cur.value
            self.advance()
            return Var(val)        # treat string as variable name
        if self.cur.type == 'MINUS':
            self.advance()
            return UnaryOp('-', self.parse_factor())
        if self.cur.type == 'TRUE':
            self.advance()
            return BoolLiteral(True)
        if self.cur.type == 'FALSE':
            self.advance()
            return BoolLiteral(False)
        if self.cur.type == 'LPAREN':
            self.advance()
            node = self.parse_expr()
            self.expect('RPAREN')
            return node

        raise ParserError(f"Unexpected token {self.cur.type}")

    def parse_cond_expr(self):
        left = self.parse_expr()
        if self.cur.type in ('EQ','NEQ','LT','GT','LE','GE'):
            op_map = {
                'EQ': '==', 'NEQ': '!=', 'LT': '<', 'GT': '>',
                'LE': '<=', 'GE': '>='
            }
            op = op_map[self.cur.type]
            self.advance()
            right = self.parse_expr()
            return BinOp(op, left, right)
        return left

# ----------------------------
# Semantic Analysis
# ----------------------------
class SemanticAnalyzer:
    def __init__(self):
        self.symbols = {}

    def analyze(self, program):
        for s in program.statements:
            self.check_stmt(s)

    def check_stmt(self, s):
        if isinstance(s, Move):
            self.must_be_number(s.expr, "move")
        elif isinstance(s, Turn):
            self.must_be_number(s.expr, "turn")
        elif isinstance(s, Assign):
            t = self.type_of(s.expr)
            self.symbols[s.name] = {'type': t}
        elif isinstance(s, Repeat):
            self.must_be_number(s.count, "repeat")
            for b in s.body: self.check_stmt(b)
        elif isinstance(s, If):
            ct = self.type_of(s.cond)
            if ct not in ('number','bool'):
                raise SemanticError("if condition must be numeric or boolean")
            for b in s.then_body: self.check_stmt(b)
            for b in s.else_body: self.check_stmt(b)
        elif isinstance(s, Color):
            name = s.name
            if name not in ALLOWED_COLORS:
                raise SemanticError(f"Unknown color '{name}'")
        elif isinstance(s, Print):
            self.type_of(s.expr)
        # Pen has no check

    def must_be_number(self, expr, context):
        if self.type_of(expr) != 'number':
            raise SemanticError(f"{context} requires a numeric expression")

    def type_of(self, expr):
        if isinstance(expr, Number): return 'number'
        if isinstance(expr, BoolLiteral): return 'bool'
        if isinstance(expr, Var):
            if expr.name in ALLOWED_COLORS:
                return 'color'
            if expr.name not in self.symbols:
                raise SemanticError(f"Use of undeclared variable '{expr.name}'")
            return self.symbols[expr.name]['type']
        if isinstance(expr, UnaryOp):
            if expr.op == '-' and self.type_of(expr.operand) == 'number':
                return 'number'
        if isinstance(expr, BinOp):
            lt = self.type_of(expr.left)
            rt = self.type_of(expr.right)
            if expr.op in ('+','-','*','/'):
                if lt != 'number' or rt != 'number':
                    raise SemanticError("Arithmetic operands must be numeric")
                return 'number'
            if expr.op in ('==','!=','<','>','<=','>='):
                if lt != rt:
                    raise SemanticError("Comparison operand type mismatch")
                return 'bool'
        raise SemanticError(f"Invalid expression '{expr}'")

# ----------------------------
# IR Generation
# ----------------------------
def ast_to_ir(program):
    ir = []
    for st in program.statements:
        ir.extend(stmt_to_ir(st))
    return ir

def stmt_to_ir(s):
    if isinstance(s, Move): return [('MOVE', s.expr)]
    if isinstance(s, Turn): return [('TURN', s.expr)]
    if isinstance(s, Pen): return [('PEN', 'UP' if s.up else 'DOWN')]
    if isinstance(s, Color): return [('COLOR', s.name)]
    if isinstance(s, Assign): return [('ASSIGN', s.name, s.expr)]
    if isinstance(s, Print): return [('PRINT', s.expr)]
    if isinstance(s, Repeat):
        body = []
        for x in s.body: body.extend(stmt_to_ir(x))
        return [('REPEAT', s.count, body)]
    if isinstance(s, If):
        t = []
        e = []
        for x in s.then_body: t.extend(stmt_to_ir(x))
        for x in s.else_body: e.extend(stmt_to_ir(x))
        return [('IF', s.cond, t, e)]
    raise RuntimeError("Unknown AST node")

# ----------------------------
# Constant Folding + Optimization
# ----------------------------
def fold_constants_expr(expr):
    if isinstance(expr, Number) or isinstance(expr, BoolLiteral) or isinstance(expr, Var):
        return expr
    if isinstance(expr, UnaryOp):
        op = fold_constants_expr(expr.operand)
        if isinstance(op, Number):
            return Number(-op.value)
        return UnaryOp(expr.op, op)
    if isinstance(expr, BinOp):
        left = fold_constants_expr(expr.left)
        right = fold_constants_expr(expr.right)
        if isinstance(left, Number) and isinstance(right, Number):
            lv, rv = left.value, right.value
            if expr.op == '+': return Number(lv + rv)
            if expr.op == '-': return Number(lv - rv)
            if expr.op == '*': return Number(lv * rv)
            if expr.op == '/':
                if rv == 0: raise SemanticError("Division by zero")
                return Number(lv / rv)
        if isinstance(left, BoolLiteral) and isinstance(right, BoolLiteral):
            if expr.op == '==': return BoolLiteral(left.value == right.value)
            if expr.op == '!=': return BoolLiteral(left.value != right.value)
        return BinOp(expr.op, left, right)
    return expr

def optimize_ir(ir):
    out = []
    for node in ir:
        t = node[0]
        if t in ('MOVE','TURN','PRINT','COLOR'):
            out.append((t, fold_constants_expr(node[1])))
        elif t == 'ASSIGN':
            out.append((t, node[1], fold_constants_expr(node[2])))
        elif t == 'REPEAT':
            cnt = fold_constants_expr(node[1])
            body = optimize_ir(node[2])
            if isinstance(cnt, Number) and int(cnt.value) == 0:
                continue
            out.append(('REPEAT', cnt, body))
        elif t == 'IF':
            cond = fold_constants_expr(node[1])
            thenb = optimize_ir(node[2])
            elseb = optimize_ir(node[3])
            if isinstance(cond, BoolLiteral):
                out.extend(thenb if cond.value else elseb)
            else:
                out.append(('IF', cond, thenb, elseb))
        else:
            out.append(node)
    return out

# ----------------------------
# Interpreter
# ----------------------------
class Interpreter:
    def __init__(self, ir):
        self.ir = ir
        self.env = {}

        turtle.reset()
        turtle.speed(2)     # SLOW for visible movement
        turtle.pensize(2)

    def eval_expr(self, e):
        if isinstance(e, Number): return e.value
        if isinstance(e, BoolLiteral): return e.value
        if isinstance(e, Var):
            if e.name in ALLOWED_COLORS: return e.name
            if e.name not in self.env:
                raise RuntimeErrorTurtle(f"Undeclared variable '{e.name}'")
            return self.env[e.name]
        if isinstance(e, UnaryOp):
            v = self.eval_expr(e.operand)
            return -v
        if isinstance(e, BinOp):
            l = self.eval_expr(e.left)
            r = self.eval_expr(e.right)
            if e.op == '+': return l + r
            if e.op == '-': return l - r
            if e.op == '*': return l * r
            if e.op == '/':
                if r == 0: raise RuntimeErrorTurtle("division by zero")
                return l / r
            if e.op == '==': return l == r
            if e.op == '!=': return l != r
            if e.op == '<': return l < r
            if e.op == '>': return l > r
            if e.op == '<=': return l <= r
            if e.op == '>=': return l >= r
        raise RuntimeErrorTurtle("Unknown expr")

    def run(self):
        self.exec_block(self.ir)
        turtle.done()

    def exec_block(self, block):
        for node in block:
            t = node[0]

            if t == 'MOVE':
                turtle.forward(self.eval_expr(node[1]))

            elif t == 'TURN':
                turtle.right(self.eval_expr(node[1]))

            elif t == 'PEN':
                if node[1] == 'UP': turtle.penup()
                else: turtle.pendown()

            elif t == 'COLOR':
                turtle.color(node[1])

            elif t == 'ASSIGN':
                self.env[node[1]] = self.eval_expr(node[2])

            elif t == 'REPEAT':
                c = int(self.eval_expr(node[1]))
                for _ in range(c):
                    self.exec_block(node[2])

            elif t == 'IF':
                cond = self.eval_expr(node[1])
                if cond: self.exec_block(node[2])
                else: self.exec_block(node[3])

            elif t == 'PRINT':
                print(self.eval_expr(node[1]))

# ----------------------------
# Compiler pipeline
# ----------------------------
def print_banner(msg):
    print("\n" + "="*60)
    print(msg)
    print("="*60)

def compile_and_run(text, show_ir=True):

    # LEXING
    print_banner("LEXICAL ANALYSIS – TOKENS")
    tokens = tokenize(text)
    for t in tokens: print(t)

    # PARSING
    print_banner("SYNTAX ANALYSIS – AST")
    parser = Parser(tokens)
    program = parser.parse()
    pprint.pprint(program, width=120)

    # SEMANTICS
    print_banner("SEMANTIC ANALYSIS – SYMBOL TABLE")
    sem = SemanticAnalyzer()
    sem.analyze(program)
    print(sem.symbols)

    # IR
    print_banner("RAW IR")
    raw_ir = ast_to_ir(program)
    pprint.pprint(raw_ir)

    # OPTIMIZED IR
    print_banner("OPTIMIZED IR")
    opt_ir = optimize_ir(raw_ir)
    pprint.pprint(opt_ir)

    # RUN
    print_banner("RUNNING PROGRAM")
    interp = Interpreter(opt_ir)
    interp.run()

# ----------------------------
# GUI
# ----------------------------
DEFAULT_PROGRAM = """color blue;
pen down;
x = 80;
repeat 5 {
    move x;
    turn 144;
}
pen up;
"""

def on_run(txt):
    src = txt.get("1.0", tk.END)
    try:
        compile_and_run(src)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def main_ui():
    root = tk.Tk()
    root.title("Turtle DSL Compiler")

    lbl = tk.Label(root, text="Enter Turtle DSL program:")
    lbl.pack(anchor="w")

    text = scrolledtext.ScrolledText(root, width=80, height=20, font=("Consolas", 11))
    text.pack()
    text.insert("1.0", DEFAULT_PROGRAM)

    btn = tk.Button(root, text="Run Program", command=lambda:on_run(text))
    btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_ui()
