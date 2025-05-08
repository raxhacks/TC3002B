from lark import Transformer, Tree, Token

class CuboSemantico:
    def __init__(self):
        self.ops = {
            ('int', '+', 'int'): 'int',
            ('int', '-', 'int'): 'int',
            ('int', '*', 'int'): 'int',
            ('int', '/', 'int'): 'float',
            ('float', '+', 'float'): 'float',
            ('float', '-', 'float'): 'float',
            ('float', '*', 'float'): 'float',
            ('float', '/', 'float'): 'float',
            ('int', '>', 'int'): 'bool',
            ('int', '<', 'int'): 'bool',
            ('int', '==', 'int'): 'bool',
            ('int', '!=', 'int'): 'bool',
            ('float', '>', 'float'): 'bool',
            ('float', '<', 'float'): 'bool',
            ('float', '==', 'float'): 'bool',
            ('float', '!=', 'float'): 'bool',
        }

    def check_operation(self, left_type, op, right_type):
        return self.ops.get((left_type, op, right_type))


class SemanticAnalyzer(Transformer):
    def __init__(self):
        self.scopes = [{}] 
        self.scope_level = 0
        self.functions = {}

    # Scope management
    def enter_scope(self):
        self.scope_level += 1
        self.scopes.append({})
        print(f"[scope] Entered new scope (level {self.scope_level})")

    def exit_scope(self):
        print(f"[scope] Exited scope (level {self.scope_level})")
        self.scopes.pop()
        self.scope_level -= 1

    def declare_variable(self, name, vtype):
        current = self.scopes[-1]
        if name in current:
            print(f"[warning] Variable '{name}' already declared in current scope")
            raise NameError(f"[error] Variable '{name}' already declared")
        current[name] = {"type": vtype, "initialized": False}
        print(f"[declare] {name}: {vtype} (scope {self.scope_level})")

    def lookup_variable(self, name):
        for level, scope in reversed(list(enumerate(self.scopes))):
            if name in scope:
                print(f"[lookup] {name} found in scope {level} as {scope[name]}")
                return scope[name]
        raise NameError(f"[error] Variable '{name}' not declared")

    def is_initialized(self, name):
        for level, scope in reversed(list(enumerate(self.scopes))):
            if name in scope:
                return scope[name]["initialized"]
        return False

    # Program entry
    def programa(self, args):
        print("\nProgram parsed successfully.")
        print("\nVariable Table by Scope:")

        for i, scope in enumerate(self.scopes):
            print(f"\nScope Level {i}")
            if not scope:
                print("  (no variables)")
                continue

            print("{:<15} {:<10} {:<12}".format("Variable", "Type", "Initialized"))
            print("-" * 37)
            for var, info in scope.items():
                print("{:<15} {:<10} {:<12}".format(var, info["type"], str(info["initialized"])))

        if self.functions:
            print("\nFunctions Table:")
            for fname, fdata in self.functions.items():
                param_list = ', '.join([f"{n}:{t}" for n, t in fdata['params']])
                print(f"{fname}({param_list})")

    def vars(self, args):
        for decl in args:
            if isinstance(decl, list):
                for var in decl:
                    self.declare_variable(*var)
            elif isinstance(decl, tuple):
                self.declare_variable(*decl)
            elif isinstance(decl, Tree):
                self.transform(decl)
    
    def vars_prime(self, args):
        for item in args:
            if isinstance(item, list):
                for var in item:
                    self.declare_variable(*var)
            elif isinstance(item, Tree):
                self.transform(item)

    def variable(self, args):
        base_id = args[0].value
        var_ids = [base_id]
        if len(args[1].children) > 0:
            var_ids += [tok.value for tok in args[1].children if isinstance(tok, Token) and tok.type == 'ID']
        vtype = args[3].value
        return [(vid, vtype) for vid in var_ids]

    def assign(self, args):
        varname = args[0].value
        self.lookup_variable(varname)
        rhs = args[2]
        self.check_identifiers(rhs)
        
        for scope in reversed(self.scopes):
            if varname in scope:
                scope[varname]["initialized"] = True
                break
        print(f"[assign] {varname} assigned")

    def body(self, args):
        self.enter_scope()
        for child in args:
            self.transform(child)
        self.exit_scope()

    # 🆕 Function declaration
    def funcs(self, args):
        fname = args[1].value
        print(f"\n[func] Defining function: {fname}")

        param_list = self.extract_params(args[2])
        if fname in self.functions:
            raise NameError(f"[error] Function '{fname}' already declared")
        self.functions[fname] = {
            "params": param_list
        }

        self.enter_scope()

        # Declare parameters in function scope
        for pname, ptype in param_list:
            self.declare_variable(pname, ptype)
            self.scopes[-1][pname]["initialized"] = True  # Parameters are initialized by default

        self.transform(args[-2])  # vars_des
        self.transform(args[-1])  # body

        self.exit_scope()

    # 🆕 Function call
    def f_call(self, args):
        fname = args[0].value
        arg_nodes = args[1:]
        if fname not in self.functions:
            raise NameError(f"[error] Function '{fname}' not declared")

        expected_params = self.functions[fname]['params']
        if len(expected_params) != len(arg_nodes):
            raise TypeError(f"[error] Function '{fname}' expects {len(expected_params)} arguments but got {len(arg_nodes)}")

        print(f"[call] Function call: {fname} with {len(arg_nodes)} args")
        for i, arg in enumerate(arg_nodes):
            self.check_identifiers(arg)

    def extract_params(self, tree):
        """Extract function parameters (name and type) from param tree"""
        params = []
        if isinstance(tree, Tree):
            for child in tree.children:
                if isinstance(child, Tree) and child.data == 'param':
                    pname = child.children[0].value
                    ptype = child.children[1].value
                    params.append((pname, ptype))
        return params

    def condition(self, args):
        print("[condition] if statement encountered")
        for arg in args:
            self.transform(arg)

    def cycle(self, args):
        print("[cycle] while loop encountered")
        self.transform(args[-2])  # body

    def print_stmt(self, args):
        print(f"[print] print statement")
        for arg in args:
            self.check_identifiers(arg)

    def expresion(self, args):
        return args[0]

    def exp(self, args):
        return args[0]

    def termino(self, args):
        return args[0]

    def factor(self, args):
        return args

    def cte(self, args):
        return args[0]

    def idcte(self, args):
        return args[0]

    def type(self, args):
        return args[0]
    
    def check_identifiers(self, node):
        if isinstance(node, Token) and node.type == 'ID':
            print(f"[check] Checking ID token: {node.value}")
            self.lookup_variable(node.value)
            if not self.is_initialized(node.value):
                raise NameError(f"[error] Variable '{node.value}' used before initialization")
        elif isinstance(node, Tree):
            for child in node.children:
                self.check_identifiers(child)
        elif isinstance(node, list):
            for item in node:
                self.check_identifiers(item)

