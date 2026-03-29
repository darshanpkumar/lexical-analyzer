# ---------------- COMPACT PARSING TABLE (CLEAN) ---------------- #

parsing_table = [
    ["Non-Terminal", "int", "id", "for", "begin", "end"],

    ["program", "int main() block", "-", "-", "-", "-"],

    ["block", "-", "-", "-", "begin stmt_list end", "-"],

    ["stmt_list", "stmt stmt_list", "stmt stmt_list", "stmt stmt_list", "-", "ε"],

    ["stmt", "declaration", "assignment", "for_loop", "-", "-"],

    ["declaration", "int var_list ;", "-", "-", "-", "-"],

    ["var_list", "-", "IDENTIFIER var_list_tail", "-", "-", "-"],

    ["var_list_tail", "-", "-", "-", "-", "ε"],

    ["assignment", "-", "IDENTIFIER = expr ;", "-", "-", "-"],

    ["expr", "-", "IDENTIFIER", "-", "-", "-"],

    ["for_loop", "-", "-", "for ( init ; condition ; increment ) block", "-", "-"]
]

print("\nCOMPACT PARSING TABLE:\n")
print(tabulate(parsing_table, headers="firstrow", tablefmt="grid"))