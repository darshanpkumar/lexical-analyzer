import re
from tabulate import tabulate

# Sample source code
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

# Print Token Table
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

keyword_table = [[k] for k in sorted(keywords)]
identifier_table = [[i] for i in sorted(identifiers)]
literal_table = [[l] for l in sorted(literals)]

print("\nSYMBOL TABLE - Keywords:")
print(tabulate(keyword_table, headers=["Keyword"], tablefmt="grid"))

print("\nSYMBOL TABLE - Identifiers:")
print(tabulate(identifier_table, headers=["Identifier"], tablefmt="grid"))

print("\nSYMBOL TABLE - Literals:")
print(tabulate(literal_table, headers=["Literal"], tablefmt="grid"))

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