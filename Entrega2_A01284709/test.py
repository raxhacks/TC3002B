from lark import Tree, Token, Transformer, Lark
from parser_and_scanner import grammar

parser = Lark(grammar, start="programa", parser="lalr")

test1 = '''
program myprog;
var id1 : int; id2 : int;
main {
    id1 = 0+2;
    print("Hola mundo",b);
}
end
'''

class EvalExpressions(Transformer):
    def __init__(self):
        self.scopes = [{}]  # Global scope
        self.scope_level = 0

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

    # Handlers
    def programa(self, args):
        print("\n✅ Program parsed successfully.")

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
        print(f"[assign] {varname} found", args)
        rhs = args[2]
        print(f"[assign] RHS: {rhs}")
        self.check_identifiers(rhs)
        
        # Set variable as initialized
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

    def funcs(self, args):
        fname = args[1].value
        print(f"\n[func] Defining function: {fname}")
        self.enter_scope()
        self.transform(args[-3])  # vars_des
        self.transform(args[-2])  # body
        self.exit_scope()

    def condition(self, args):
        print("[condition] if statement encountered")
        for arg in args:
            self.transform(arg)

    def cycle(self, args):
        print("[cycle] while loop encountered")
        self.transform(args[-2])  # body

    def f_call(self, args):
        fname = args[0].value
        print(f"[call] Function call: {fname}")

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

    
    def is_initialized(self, name):
        for level, scope in reversed(list(enumerate(self.scopes))):
            if name in scope:
                return scope[name]["initialized"]
        return False 



t = parser.parse(test1)
print(EvalExpressions().transform( t ))