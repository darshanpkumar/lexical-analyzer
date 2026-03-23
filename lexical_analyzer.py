import re
from tabulate import tabulate # type: ignore

# Sample source code (your question)
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

# Define token patterns
token_specification = [
    ('KEYWORD', r'\b(int|main|begin|end|for)\b'),
    ('NUMBER', r'\b\d+\b'),
    ('IDENTIFIER', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('OPERATOR', r'\+\+|<=|=|\+'),
    ('SYMBOL', r'[(),;]'),
    ('SKIP', r'[ \t\n]+'),
    ('MISMATCH', r'.'),
]

# Combine patterns
tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)

# Tokenization
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

# Print token table
print("TOKEN TABLE:\n")
print(tabulate(tokens, headers=["Type", "Lexeme", "Token ID"], tablefmt="grid"))