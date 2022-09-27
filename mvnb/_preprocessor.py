if __name__ == "__main__":
    import ast
    import sys

    compound_stmts = (
        ast.FunctionDef,
        ast.If,
        ast.ClassDef,
        ast.With,
        ast.For,
        ast.Try,
        ast.While,
        ast.Match,
    )

    try:
        node = ast.parse(sys.stdin.read())
    except SyntaxError:
        exit(1)
    else:
        for n in node.body:
            lst = ast.unparse(n).splitlines()
            print("\n".join(e for e in lst if e))
            if isinstance(n, compound_stmts):
                print()
