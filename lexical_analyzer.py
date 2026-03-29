import re
from tabulate import tabulate

# ---------------- SOURCE CODE ---------------- #
source_code = """
int main()
begin
    int n, i, sum = 0;
    for(i=1; i <= n; ++i)
    begin
        expr = expr + expr;
    end
end
"""

# ---------------- LEXICAL ANALYZER ---------------- #
token_specification = [
    ('KEYWORD', r'\b(int|main|begin|end|for)\b'),
    ('NUMBER', r'\b\d+\b'),
    ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('OPERATOR', r'\+\+|<=|=|\+'),
    ('SYMBOL', r'[(),;]'),
    ('SKIP', r'[ \t\n]+'),
    ('MISMATCH', r'.'),
]

tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)

tokens = []
token_id = 1

for mo in re.finditer(tok_regex, source_code):
    kind = mo.lastgroup
    value = mo.group()

    if kind == 'SKIP':
        continue
    elif kind == 'MISMATCH':
        raise RuntimeError(f'Unexpected character: {value}')
    
    tokens.append((kind, value, token_id))
    token_id += 1

print("TOKEN TABLE:\n")
print(tabulate(tokens, headers=["Type", "Lexeme", "Token ID"], tablefmt="grid"))

# ---------------- SYMBOL TABLE ---------------- #
keywords = set()
identifiers = set()
literals = set()

for token in tokens:
    if token[0] == 'KEYWORD':
        keywords.add(token[1])
    elif token[0] == 'IDENTIFIER':
        identifiers.add(token[1])
    elif token[0] == 'NUMBER':
        literals.add(token[1])

print("\nSYMBOL TABLE - Keywords:")
print(tabulate([[k] for k in sorted(keywords)], headers=["Keyword"], tablefmt="grid"))

print("\nSYMBOL TABLE - Identifiers:")
print(tabulate([[i] for i in sorted(identifiers)], headers=["Identifier"], tablefmt="grid"))

print("\nSYMBOL TABLE - Literals:")
print(tabulate([[l] for l in sorted(literals)], headers=["Literal"], tablefmt="grid"))

# ---------------- FIRST & FOLLOW ---------------- #

first_sets_data = [
    ["program", "int"],
    ["block", "begin"],
    ["stmt_list", "int, id, for, ε"],
    ["stmt", "int, id, for"],
    ["declaration", "int"],
    ["var_list", "id"],
    ["var_tail", ", ε"],
    ["assignment", "id"],
    ["expr", "id, num"],
    ["for_loop", "for"],
    ["init", "id"],
    ["condition", "id"],
    ["increment", "++"]
]

follow_sets_data = [
    ["program", "$"],
    ["block", "$, end"],
    ["stmt_list", "end"],
    ["stmt", "int, id, for, end"],
    ["declaration", "int, id, for, end"],
    ["var_list", ";"],
    ["var_tail", ";"],
    ["assignment", "int, id, for, end"],
    ["expr", ";, )"],
    ["for_loop", "int, id, for, end"],
    ["init", ";"],
    ["condition", ";"],
    ["increment", ")"]
]

print("\nFIRST SETS:")
print(tabulate(first_sets_data, headers=["Non-Terminal", "FIRST"], tablefmt="grid"))

print("\nFOLLOW SETS:")
print(tabulate(follow_sets_data, headers=["Non-Terminal", "FOLLOW"], tablefmt="grid"))

# ---------------- Grammar Production Rules---------------- #
grammar = {
    "program": ["int main ( ) block"],
    
    "block": ["begin stmt_list end"],
    
    "stmt_list": ["stmt stmt_list", "ε"],
    
    "stmt": ["declaration", "assignment", "for_loop"],
    
    "declaration": ["int var_list ;"],
    
    "var_list": ["IDENTIFIER var_list_tail"],
    
    "var_list_tail": [", IDENTIFIER var_list_tail", "ε"],
    
    "assignment": ["IDENTIFIER = expr ;"],
    
    "expr": ["IDENTIFIER + IDENTIFIER", "IDENTIFIER", "NUMBER"],
    
    "for_loop": ["for ( init ; condition ; increment ) block"],
    
    "init": ["IDENTIFIER = NUMBER"],
    
    "condition": ["IDENTIFIER <= IDENTIFIER"],
    
    "increment": ["++ IDENTIFIER"]
}

# Print the grammar
print("\nGRAMMAR:")
for non_terminal, productions in grammar.items():
    for production in productions:
        print(f"{non_terminal} -> {production}")

# ---------------- PARSING ACTIONS ---------------- #
print("\nPARSING ACTIONS:\n")

stack = ['$', 'program']
input_tokens = ['int', 'main', '(', ')', 'begin',
                'int', 'id', ',', 'id', ',', 'id', ';',
                'for', '(', 'id', '=', 'num', ';', 'id', '<=', 'id', ';', '++', 'id', ')',
                'begin', 'id', '=', 'id', '+', 'id', ';', 'end',
                'end', '$']

steps_data = []
step = 1

steps_data.append([step, '$', '', 'Start parsing'])
step += 1

while stack:
    stack_snapshot = ' '.join(stack[-6:])

    top = stack.pop()
    current_input = input_tokens[0]

    action = ""

    # MATCH
    if top == current_input:
        action = f"Match '{top}'"
        input_tokens.pop(0)

    elif top == 'program':
        action = "Apply: program → int main ( ) block"
        stack.extend(['block', ')', '(', 'main', 'int'])

    elif top == 'block':
        action = "Apply: block → begin stmt_list end"
        stack.extend(['end', 'stmt_list', 'begin'])

    elif top == 'stmt_list':
        if current_input in ['int', 'id', 'for']:
            action = "Apply: stmt_list → stmt stmt_list"
            stack.extend(['stmt_list', 'stmt'])
        else:
            action = "Apply: stmt_list → ε"

    elif top == 'stmt':
        if current_input == 'int':
            action = "Apply: stmt → declaration"
            stack.append('declaration')
        elif current_input == 'id':
            action = "Apply: stmt → assignment"
            stack.append('assignment')
        elif current_input == 'for':
            action = "Apply: stmt → for_loop"
            stack.append('for_loop')

    elif top == 'declaration':
        action = "Apply: declaration → int var_list ;"
        stack.extend([';', 'var_list', 'int'])

    elif top == 'var_list':
        action = "Apply: var_list → id var_list_tail"
        stack.extend(['var_list_tail', 'id'])

    elif top == 'var_list_tail':
        if current_input == ',':
            action = "Apply: var_list_tail → , id var_list_tail"
            stack.extend(['var_list_tail', 'id', ','])
        else:
            action = "Apply: var_list_tail → ε"

    elif top == 'assignment':
        action = "Apply: assignment → id = expr ;"
        stack.extend([';', 'expr', '=', 'id'])

    elif top == 'expr':
        if current_input == 'id':
            action = "Apply: expr → id expr_tail"
            stack.extend(['expr_tail', 'id'])
        elif current_input == 'num':
            action = "Apply: expr → num expr_tail"
            stack.extend(['expr_tail', 'num'])

    elif top == 'expr_tail':
        if current_input == '+':
            action = "Apply: expr_tail → + expr"
            stack.extend(['expr', '+'])
        else:
            action = "Apply: expr_tail → ε"

    elif top == 'for_loop':
        action = "Apply: for_loop → for ( init ; condition ; increment ) block"
        stack.extend(['block', ')', 'increment', ';', 'condition', ';', 'init', '(', 'for'])

    elif top == 'init':
        action = "Apply: init → id = num"
        stack.extend(['num', '=', 'id'])

    elif top == 'condition':
        action = "Apply: condition → id <= id"
        stack.extend(['id', '<=', 'id'])

    elif top == 'increment':
        action = "Apply: increment → ++ id"
        stack.extend(['id', '++'])

    else:
        action = "Error"
        steps_data.append([step, stack_snapshot, current_input, action])
        break

    steps_data.append([step, stack_snapshot, current_input, action])
    step += 1

if not stack and not input_tokens:
    steps_data.append([step, '$', '$', 'Parsing completed successfully'])

print(tabulate(
    steps_data,
    headers=["Step", "Stack", "Input Symbol", "Action"],
    tablefmt="grid",
    maxcolwidths=[5, 40, 15, 50]
))