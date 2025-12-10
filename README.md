# Turtle Graphics Domain-Specific Language (DSL) Compiler

## Project Information

**Course:** Compiler Construction (CS4031)  
**Semester:** Fall 2025  
**Institution:** FAST NUCES  
**Total Marks:** 100 (Weightage: 10%)  
**Group Members:**
- Syed Abdurrehman (Roll: 22K-4666)
- M. Anas Khan (Roll: 22K-4170)

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Mini Language Specification](#mini-language-specification)
3. [Language Features](#language-features)
4. [Compiler Architecture](#compiler-architecture)
5. [Compilation Phases](#compilation-phases)
6. [Usage Instructions](#usage-instructions)
7. [Test Cases](#test-cases)
8. [Project Structure](#project-structure)
9. [Design Artifacts](#design-artifacts)
10. [Reflection](#reflection)

---

## Project Overview

This project implements a **compiler for Turtle Graphics DSL** – a custom domain-specific language designed for simple graphics programming using turtle graphics. The language allows users to write intuitive programs that control a virtual turtle to draw geometric shapes and patterns.

### Objective

The objective is to demonstrate a complete understanding of all six major phases of compiler construction:
1. **Lexical Analysis** – Token recognition and classification
2. **Syntax Analysis** – Grammar-based parsing and AST construction
3. **Semantic Analysis** – Symbol table management and type checking
4. **Intermediate Code Generation** – Three-address code representation
5. **Optimization** – Constant folding and dead code elimination
6. **Code Generation** – Execution through an interpreter

---

## Mini Language Specification

### Language Overview

**Turtle DSL** is a procedural language for drawing graphics using simple turtle movement commands. The language supports variables, conditional statements, loops, and drawing operations.

### Lexical Specification

#### Tokens

| Token Type | Pattern | Example |
|-----------|---------|---------|
| **NUMBER** | `\d+(\.\d+)?` | `42`, `3.14` |
| **IDENT** | `[A-Za-z_][A-Za-z0-9_]*` | `x`, `side_length` |
| **STRING** | `"[^"]*"` | `"hello"` |
| **Operators** | `==`, `!=`, `<`, `>`, `<=`, `>=` | Comparison operators |
| **Arithmetic** | `+`, `-`, `*`, `/` | Arithmetic operations |
| **Delimiters** | `(`, `)`, `{`, `}`, `;`, `,` | Statement and block delimiters |
| **Keywords** | See Keywords table | Reserved words |

#### Keywords

| Keyword | Purpose |
|---------|---------|
| `move` | Move turtle forward by distance |
| `turn` | Turn turtle right by angle (degrees) |
| `pen` | Control pen state |
| `up` | Lift pen (stop drawing) |
| `down` | Lower pen (start drawing) |
| `color` | Set drawing color |
| `repeat` | Loop statement |
| `if` | Conditional statement |
| `else` | Else clause |
| `print` | Output to console |
| `true`, `false` | Boolean literals |

#### Allowed Colors

`white`, `black`, `red`, `green`, `blue`, `cyan`, `yellow`, `magenta`, `orange`, `brown`, `purple`, `pink`, `gray`, `gold`, `navy`, `lime`

### Grammar Specification (EBNF)

```ebnf
Program        ::= Statement*

Statement      ::= MoveStmt | TurnStmt | PenStmt | ColorStmt 
                 | RepeatStmt | IfStmt | AssignStmt | PrintStmt

MoveStmt       ::= "move" Expression ";"
TurnStmt       ::= "turn" Expression ";"
PenStmt        ::= "pen" ("up" | "down") ";"
ColorStmt      ::= "color" (IDENT | STRING) ";"
RepeatStmt     ::= "repeat" Expression "{" Statement* "}"
IfStmt         ::= "if" "(" CondExpr ")" "{" Statement* "}" 
                   ["else" "{" Statement* "}"]
AssignStmt     ::= IDENT "=" Expression ";"
PrintStmt      ::= "print" "(" Expression ")" ";"

Expression     ::= Term (("+"|"-") Term)*
Term           ::= Factor (("*"|"/") Factor)*
Factor         ::= NUMBER | IDENT | STRING | "-" Factor 
                 | "true" | "false" | "(" Expression ")"

CondExpr       ::= Expression (("=="|"!="|"<"|">"|"<="|">=") Expression)?
```

### Semantic Rules

| Rule | Description |
|------|-------------|
| **Type System** | Two types: `number` (int/float) and `bool` |
| **Variables** | Must be declared before use with assignment |
| **move/turn** | Require numeric expressions |
| **repeat** | Count must be numeric expression (will be cast to int) |
| **if condition** | Must be numeric or boolean expression |
| **colors** | Must be from predefined allowed colors |
| **operators** | Arithmetic operators require numeric operands |
| **Comparisons** | Operands must be of same type |

---

## Language Features

### 1. Basic Movement Commands

```turtle
move 100;          // Move turtle forward 100 units
turn 90;           // Turn right 90 degrees
```

### 2. Pen Control

```turtle
pen down;          // Start drawing
pen up;            // Stop drawing
```

### 3. Color Support

```turtle
color red;         // Set drawing color to red
color blue;        // Change to blue
```

### 4. Variables and Assignments

```turtle
x = 50;            // Declare and assign variable
y = x + 25;        // Arithmetic operations
size = 100;
```

### 5. Looping (Repeat)

```turtle
repeat 4 {
    move 100;
    turn 90;
}
```

### 6. Conditional Logic (If-Else)

```turtle
x = 5;
if x > 3 {
    move 100;
    color red;
} else {
    move 50;
    color blue;
}
```

### 7. Output (Print)

```turtle
x = 10;
print x;           // Prints: 10
```

### 8. Arithmetic and Boolean Operations

```turtle
x = 2 + 3 * 4;     // x = 14 (operator precedence)
y = 10 - 5;        // y = 5
z = 20 / 4;        // z = 5
w = 3 * 3;         // w = 9

// Comparisons
if x == 14 { print true; }
if y != 0 { print true; }
if z >= 5 { print true; }
```

---

## Compiler Architecture

### High-Level Architecture

```
┌─────────────┐
│ Source Code │
└──────┬──────┘
       │
       ▼
┌──────────────────────────┐
│ Lexical Analysis (Lexer) │  → Tokens
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Syntax Analysis (Parser) │  → Abstract Syntax Tree (AST)
└──────┬───────────────────┘
       │
       ▼
┌────────────────────────────────┐
│ Semantic Analysis (Analyzer)   │  → Symbol Table, Type Checking
└──────┬─────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ IR Generation (Code Gen)     │  → Three-Address Code
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Optimization                 │  → Optimized IR (Constant Folding, Dead Code)
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│ Execution (Interpreter)      │  → Turtle Graphics Output
└──────────────────────────────┘
```

---

## Compilation Phases

### Phase 1: Lexical Analysis

**Purpose:** Convert source code into tokens

**Key Components:**
- Token patterns using regular expressions
- Master regex combining all token patterns
- Keyword recognition
- Error handling for unexpected characters

**Token Structure:**
```python
class Token:
    type: str      # Token type (NUMBER, IDENT, KEYWORD, etc.)
    value: any     # Token value
    line: int      # Line number for error reporting
    col: int       # Column number for error reporting
```

**Output:** Token stream for parser

**Example:**
```
Input:  move 100;
Output: Token(MOVE, 'move', 1, 1)
        Token(NUMBER, 100, 1, 6)
        Token(SEMI, ';', 1, 9)
        Token(EOF, None, 1, 10)
```

---

### Phase 2: Syntax Analysis (Parsing)

**Purpose:** Build Abstract Syntax Tree (AST) from tokens

**Method:** Recursive Descent Parser using operator precedence

**Grammar Implementation:**
- `parse_statement()` → Parse statements (move, turn, repeat, if, etc.)
- `parse_expr()` → Parse addition/subtraction (lowest precedence)
- `parse_term()` → Parse multiplication/division
- `parse_factor()` → Parse primary expressions (numbers, variables, parentheses)
- `parse_cond_expr()` → Parse conditional expressions

**AST Node Classes:**

| Node Type | Purpose | Fields |
|-----------|---------|--------|
| `Program` | Root node | statements |
| `Move` | Move command | expr |
| `Turn` | Turn command | expr |
| `Pen` | Pen control | up (bool) |
| `Color` | Color command | name |
| `Assign` | Variable assignment | name, expr |
| `Repeat` | Loop | count, body |
| `If` | Conditional | cond, then_body, else_body |
| `Print` | Output | expr |
| `BinOp` | Binary operation | op, left, right |
| `UnaryOp` | Unary operation | op, operand |
| `Number` | Numeric literal | value |
| `Var` | Variable reference | name |
| `BoolLiteral` | Boolean literal | value |

**Error Handling:** `ParserError` exceptions with line/column information

**Example Parse Tree for `move 100; turn 90;`:**
```
Program
├── Move
│   └── Number(100)
└── Turn
    └── Number(90)
```

---

### Phase 3: Semantic Analysis

**Purpose:** Verify semantic correctness and build symbol table

**Key Responsibilities:**
1. **Type Checking:** Ensure expressions have correct types
2. **Symbol Table Management:** Track declared variables and their types
3. **Semantic Validation:** Enforce language rules

**Type System:**
- `number` – Integer or floating-point values
- `bool` – Boolean values (true/false)
- `color` – Color identifiers (string-based)

**Symbol Table Structure:**
```python
{
    'variable_name': {
        'type': 'number' | 'bool'
    }
}
```

**Semantic Rules Enforced:**
- `move` and `turn` require numeric expressions
- `repeat` count must be numeric
- `if` condition must be numeric or boolean
- Variables must be declared before use
- Color names must be in allowed colors list
- Binary operators require compatible types
- Comparisons require same operand types

**Error Handling:** `SemanticError` exceptions with detailed messages

**Example Symbol Table:**
```python
{
    'x': {'type': 'number'},
    'y': {'type': 'number'},
    'size': {'type': 'number'}
}
```

---

### Phase 4: Intermediate Code Generation (IR)

**Purpose:** Convert AST to three-address code

**IR Format:** Tuples representing operations

**IR Instructions:**

| Instruction | Format | Meaning |
|-------------|--------|---------|
| MOVE | `('MOVE', expr)` | Move forward |
| TURN | `('TURN', expr)` | Turn right |
| PEN | `('PEN', 'UP'|'DOWN')` | Pen control |
| COLOR | `('COLOR', color_name)` | Set color |
| ASSIGN | `('ASSIGN', var, expr)` | Variable assignment |
| REPEAT | `('REPEAT', count, body)` | Loop construct |
| IF | `('IF', cond, then, else)` | Conditional |
| PRINT | `('PRINT', expr)` | Output |

**Example IR for star drawing:**
```python
[
    ('COLOR', 'blue'),
    ('PEN', 'DOWN'),
    ('ASSIGN', 'x', Number(80)),
    ('REPEAT', Number(5), [
        ('MOVE', Var('x')),
        ('TURN', Number(144))
    ])
]
```

---

### Phase 5: Optimization

**Purpose:** Improve code efficiency

**Optimization Techniques Implemented:**

#### 1. Constant Folding
Evaluates constant expressions at compile time.

```python
x = 2 + 3;     // Optimized to x = 5;
y = 10 - 5;    // Optimized to y = 5;
z = true;      // Constant propagation
```

#### 2. Dead Code Elimination
Removes unreachable code blocks.

```python
repeat 0 {     // This block is eliminated
    move 100;
}
```

#### 3. Conditional Folding
Evaluates compile-time conditions.

```python
if true {
    move 100;
}
// Else branch eliminated, then branch kept
```

**Optimization Algorithm:**
- Recursively traverse IR
- Apply constant folding to all expressions
- Remove dead loops (count = 0)
- Simplify conditionals with boolean constants

---

### Phase 6: Code Generation (Execution)

**Purpose:** Execute IR and produce turtle graphics output

**Execution Model:** Tree-walking interpreter

**Key Components:**
1. **Expression Evaluator:** `eval_expr(expr)` → Computes expression values
2. **Block Executor:** `exec_block(block)` → Executes IR instructions
3. **Environment:** Maintains variable bindings

**Execution Functions:**

| Function | Purpose |
|----------|---------|
| `eval_expr()` | Evaluate expressions to values |
| `exec_block()` | Execute block of IR instructions |
| `run()` | Start execution and display turtle window |

**Turtle Operations:**
- `turtle.forward(dist)` – Move forward
- `turtle.right(angle)` – Turn right
- `turtle.penup()` – Lift pen
- `turtle.pendown()` – Lower pen
- `turtle.color(name)` – Set color
- `print()` – Output to console
- `turtle.done()` – Display window

**Example Execution Trace:**
```
Input:  move 100; turn 90;
Execute: forward(100) → turtle moves 100 units
Execute: right(90)   → turtle turns 90 degrees
Output:  Visual line drawn on screen
```

---

## Usage Instructions

### Prerequisites

- Python 3.7 or higher
- tkinter (usually included with Python)
- turtle module (standard library)

### Running the Compiler

#### 1. GUI Mode (Recommended)

```bash
python turtle_compiler_2.py
```

This launches a graphical interface with:
- Text editor for writing Turtle DSL code
- "Run Program" button to execute code
- Turtle graphics window for output

#### 2. Command-Line Mode

```python
from turtle_compiler_2 import compile_and_run

code = """
color red;
pen down;
repeat 4 {
    move 100;
    turn 90;
}
pen up;
"""

compile_and_run(code)
```

### Default Program

The GUI starts with a sample program:
```turtle
color blue;
pen down;
x = 80;
repeat 5 {
    move x;
    turn 144;
}
pen up;
```

This draws a blue star.

---

## Test Cases

### Test Case 1: Simple Square

**Description:** Draw a blue square

**Input:**
```turtle
color blue;
pen down;
repeat 4 {
    move 100;
    turn 90;
}
pen up;
```

**Expected Output:**
- A blue square is drawn on the screen
- Turtle returns to starting position facing north

**Compilation Steps:**
1. Lexer: 16 tokens (color, blue, pen, down, repeat, etc.)
2. Parser: Program with 4 statements
3. Semantic: Variables checked, repeat count validated
4. IR: Color, Pen, Repeat with Move and Turn operations
5. Optimized: Same as raw IR (no constants to fold)
6. Execution: Draws square using turtle graphics

---

### Test Case 2: Variable Arithmetic and Star

**Description:** Draw a colored star using variables

**Input:**
```turtle
color blue;
pen down;
x = 80;
repeat 5 {
    move x;
    turn 144;
}
pen up;
```

**Expected Output:**
- A blue five-pointed star is drawn
- Demonstrates variable usage and repeat loop

**Compilation Steps:**
1. Lexer: Recognizes NUMBER, IDENT, keywords
2. Parser: Builds AST with Assign and Repeat nodes
3. Semantic: Variable `x` type inferred as `number`
   - Symbol table: `{'x': {'type': 'number'}}`
4. IR: Assignment, Color, Pen, and Repeat operations
5. Execution: Uses variable value in move command

---

### Test Case 3: Conditional Drawing

**Description:** Draw shapes based on a condition

**Input:**
```turtle
x = 10;
color red;
if x > 5 {
    pen down;
    repeat 4 {
        move 100;
        turn 90;
    }
} else {
    pen up;
}
```

**Expected Output:**
- Red square is drawn (since x = 10 > 5, condition is true)
- Then-branch executes, else-branch skipped

**Compilation Steps:**
1. Lexer: NUMBER, IDENT, comparison operators
2. Parser: If node with condition and two branches
3. Semantic: Type checking for condition (must be bool/number)
4. IR: IF instruction with optimized branches
5. Optimization: Condition evaluated at compile time (true)
6. Execution: Only then-branch executed

**Variable Symbol Table:**
```python
{'x': {'type': 'number'}}
```

---

### Test Case 4: Constant Folding

**Description:** Test optimization of constant expressions

**Input:**
```turtle
x = 2 + 3 * 4;
y = 10 - 5;
print x;
print y;
```

**Expected Output:**
```
14
5
```

**Compilation Steps:**
1. Lexer: Numbers and arithmetic operators
2. Parser: Builds BinOp nodes for expressions
3. Semantic: All expressions are numeric
4. Raw IR:
   ```python
   ('ASSIGN', 'x', BinOp('+', Number(2), BinOp('*', Number(3), Number(4))))
   ('ASSIGN', 'y', BinOp('-', Number(10), Number(5)))
   ```
5. **Optimized IR:**
   ```python
   ('ASSIGN', 'x', Number(14))    # Folded: 2 + (3 * 4) = 14
   ('ASSIGN', 'y', Number(5))     # Folded: 10 - 5 = 5
   ```
6. Execution: Prints constants directly

---

### Test Case 5: Complex Pattern with Nested Loops

**Description:** Draw concentric squares

**Input:**
```turtle
size = 100;
pen down;
repeat 3 {
    repeat 4 {
        move size;
        turn 90;
    }
    turn 30;
    size = size - 20;
}
pen up;
```

**Expected Output:**
- Three nested squares with decreasing sizes
- Rotated at 30-degree intervals

**Compilation Steps:**
1. Lexer: Complex token stream
2. Parser: Nested Repeat and Assign statements
3. Semantic: Variable scoping and type checking
4. IR: Nested repeat instructions
5. Optimization: Constant folding where applicable
6. Execution: Handles nested loops correctly

---

## Project Structure

```
turtle_compiler_2.py          # Main compiler implementation
├── Lexical Analysis
│   ├── Token class
│   ├── TOKEN_SPEC regex patterns
│   ├── KEYWORDS mapping
│   ├── ALLOWED_COLORS set
│   └── tokenize() function
│
├── Syntax Analysis
│   ├── AST Node classes (Program, Move, Turn, etc.)
│   └── Parser class
│       ├── parse() – Entry point
│       ├── parse_statement() – Statement parsing
│       ├── parse_expr() – Expression parsing
│       ├── parse_term() – Term parsing
│       ├── parse_factor() – Factor parsing
│       └── parse_cond_expr() – Condition parsing
│
├── Semantic Analysis
│   └── SemanticAnalyzer class
│       ├── analyze() – Main analysis
│       ├── check_stmt() – Statement checking
│       ├── must_be_number() – Type constraint
│       └── type_of() – Type inference
│
├── IR Generation
│   ├── ast_to_ir() – Convert AST to IR
│   └── stmt_to_ir() – Convert individual statements
│
├── Optimization
│   ├── fold_constants_expr() – Constant folding
│   └── optimize_ir() – IR optimization
│
├── Execution
│   └── Interpreter class
│       ├── eval_expr() – Expression evaluation
│       ├── exec_block() – Block execution
│       └── run() – Main execution loop
│
└── GUI
    ├── main_ui() – Tkinter interface
    ├── on_run() – Event handler
    └── DEFAULT_PROGRAM – Sample code
```

---

## Design Artifacts

This section describes the handwritten/documented artifacts created for each compiler phase:

### 1. Lexical Analysis Artifacts

**Artifact 1: Deterministic Finite Automaton (DFA) for Token Recognition**

A state diagram showing token recognition for basic patterns:
- Numbers: `[0-9]+(\.[0-9]+)?`
- Identifiers: `[A-Za-z_][A-Za-z0-9_]*`
- Keywords vs. identifiers distinction
- Operator and delimiter recognition

**Artifact 2: Token Classification Table**

Table mapping token patterns to categories:
- Reserved keywords
- Operators (arithmetic, comparison, assignment)
- Delimiters and punctuation
- Literals

### 2. Syntax Analysis Artifacts

**Artifact 1: Grammar in EBNF**

Formal grammar specification for Turtle DSL with:
- Production rules for each statement type
- Expression hierarchy showing precedence
- Terminal and non-terminal symbols

**Artifact 2: Parse Tree Derivations**

Two example parse trees showing:
1. **Square drawing:** How statements decompose into AST
2. **Star pattern:** How nested loops parse with variable assignment

Each tree shows:
- Root: Program
- Children: Individual statements
- Terminal nodes: Tokens

**Example Derivation:**
```
Program ⟹ Statement* 
        ⟹ Statement Statement
        ⟹ ColorStmt RepeatStmt
        ⟹ ...
```

### 3. Semantic Analysis Artifacts

**Artifact 1: Symbol Table Example with Scope**

Symbol table for test case showing:
- Variable declarations
- Type information
- Scope tracking (global scope)

**Example:**
```
┌─────────────────────────────┐
│      Symbol Table           │
├─────────┬──────────────────┤
│Variable │ Type             │
├─────────┼──────────────────┤
│ x       │ number           │
│ size    │ number           │
│ color   │ (predefined)     │
└─────────┴──────────────────┘
```

**Artifact 2: Type Checking Rules Table**

Table showing:
- Operation | Operand Types | Result Type | Constraints
- Examples for each type of expression

### 4. Intermediate Code Artifacts

**Artifact 1: Three-Address Code Sample**

Sample IR for a star-drawing program showing:
- ASSIGN instructions
- MOVE, TURN operations
- REPEAT with nested instructions
- COLOR and PEN commands

### 5. Optimization Artifacts

**Artifact 1: Constant Folding Examples**

Before and after optimization showing:
- Expression simplification
- Dead code removal
- Conditional simplification

### 6. Code Generation Artifacts

**Artifact 1: Execution Trace**

Step-by-step execution trace for simple program showing:
- Variable bindings in environment
- Graphics state (pen up/down, color)
- Turtle position and heading
- Output to console

---

## Reflection

### What We Learned

1. **Compiler Pipeline Complexity:** Understanding how source code transforms through multiple phases, each building on previous phases' output.

2. **Lexical Analysis Importance:** Regular expressions and token classification are foundational for parsing and error reporting.

3. **Recursive Descent Parsing:** Building parsers using recursive functions with backtracking, operator precedence, and error recovery.

4. **Type Systems:** Implementing basic type checking and type inference algorithms for semantic validation.

5. **Intermediate Representations:** IR serves as bridge between high-level syntax and low-level execution, enabling optimization.

6. **Optimization Techniques:** Simple optimizations like constant folding and dead code elimination can significantly improve performance.

7. **Error Handling:** Meaningful error messages with line/column information are crucial for usability.

### Strengths of Our Implementation

- **Comprehensive Phase Coverage:** All six compilation phases fully implemented
- **Clean Architecture:** Each phase has clear responsibilities and interfaces
- **Error Messages:** Detailed errors with location information aid debugging
- **Optimization:** Constant folding and dead code elimination reduce runtime
- **User-Friendly:** GUI makes testing easy without command-line knowledge
- **Extensible Design:** Easy to add new statements, operators, or colors

### Areas for Improvement

1. **Error Recovery:** Parser could recover from errors and report multiple issues instead of stopping at first error

2. **Advanced Optimization:**
   - Common subexpression elimination
   - Loop invariant code motion
   - Peephole optimization

3. **Scoping:** Support for function definitions and local scopes

4. **Type System:** Support for more types (arrays, structs) and type inference

5. **Debugging Support:** Generate symbol maps for debugger integration

6. **Code Generation:** Generate native code instead of interpreting IR

7. **Standard Library:** Built-in functions for common graphics operations

8. **Documentation:** Type annotations and docstrings for better code documentation

### Challenges Faced and Solutions

| Challenge | Solution |
|-----------|----------|
| Operator precedence | Recursive descent with separate methods for each precedence level |
| Parse tree construction | Use dataclasses for AST nodes for clean representation |
| Type checking complexity | Visitor pattern through `type_of()` method |
| Optimization correctness | Careful handling of nested structures and side effects |
| GUI responsiveness | Run compilation in main thread (acceptable for small programs) |

### Future Enhancements

1. **Language Features:**
   - Function definitions and calls
   - Arrays and string manipulation
   - Multiple data types (lists, dictionaries)
   - Exception handling (try-catch)

2. **Compiler Features:**
   - Bytecode compilation for faster execution
   - JIT compilation for real-time performance
   - Profiler to identify bottlenecks
   - Debugger with breakpoints

3. **Tooling:**
   - VS Code extension with syntax highlighting
   - Language server protocol (LSP) integration
   - REPL for interactive programming
   - Package manager for libraries

4. **Graphics:**
   - 3D graphics support
   - Turtle animation with tweening
   - Multiple turtle support
   - Export to SVG/PNG

---

## File Information

- **Main File:** `turtle_compiler_2.py`
- **Lines of Code:** ~682
- **Language:** Python 3
- **Dependencies:** tkinter, turtle (standard library)

---

## Conclusion

This compiler project demonstrates a complete implementation of a domain-specific language compiler with all six major phases. The Turtle Graphics DSL is a practical, intuitive language suitable for educational purposes while showcasing real compiler construction concepts. The modular architecture allows for future extensions and improvements, making it a solid foundation for compiler research and education.

The project successfully bridges the gap between formal compiler theory and practical implementation, providing hands-on experience with lexical analysis, parsing, semantic checking, intermediate code generation, optimization, and code execution.

---

**Date:** December 10, 2025  
**Status:** Complete  
**Version:** 2.0 (Improved Version)

---

## Appendix: Quick Reference

### Running Quick Tests

```python
# Test 1: Simple square
code1 = """
color blue;
pen down;
repeat 4 { move 100; turn 90; }
pen up;
"""

# Test 2: Variable usage
code2 = """
x = 50;
color red;
pen down;
move x;
"""

# Test 3: Conditions
code3 = """
x = 10;
if x > 5 { pen down; } else { pen up; }
move 100;
"""

from turtle_compiler_2 import compile_and_run
compile_and_run(code1)
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `LexerError: Unexpected character` | Invalid symbol in code | Use only valid tokens |
| `ParserError: Expected X got Y` | Wrong token in grammar | Check syntax against grammar |
| `SemanticError: Unknown color` | Color name not in allowed list | Use valid color from ALLOWED_COLORS |
| `SemanticError: Use of undeclared variable` | Variable used before assignment | Declare variable first |
| `RuntimeErrorTurtle: division by zero` | Division by zero during execution | Ensure divisor is non-zero |

---

