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
    
precedence = {
    "(": 3,
    "*": 2,
    "/": 2,
    "+": 1,
    "-": 1,
    "=": 0,
}

class SemanticAnalyzer(Transformer):
    def __init__(self):
        self.scopes = [{}] 
        self.scope_level = 0
        self.functions = {}
        self.operands=[]
        self.operators=[]
        self.quadruples=[]
        self.temp_counter=0
        self.operand_types=[]
        self.cubo = CuboSemantico()
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
                if not scope[name]["initialized"]:
                    raise NameError(f"[error] Variable '{name}' used before initialization")
                return scope[name]["initialized"]
        raise NameError(f"[error] Variable '{name}' not declared")

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

        if self.quadruples:
            print("\nQuadruples:")
            for i, quad in enumerate(self.quadruples):
                print(f"{i}: {quad}")

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
        rhs = args[2]

        self.lookup_variable(varname)
        self.check_identifiers(rhs)

        while self.operators:
            op = self.operators.pop()
            right = self.operands.pop()
            left = self.operands.pop()
            temp = f"t{self.temp_counter}"
            self.temp_counter += 1
            self.quadruples.append((op, left, right, temp))
            self.operands.append(temp)

        result = self.operands.pop()

        var_type = self.lookup_variable(varname)["type"]
        result_type = self.operand_types.pop()

        if var_type != result_type:
            raise TypeError(f"[semantic error] No puedes asignar tipo '{result_type}' a variable '{varname}' de tipo '{var_type}'")

        self.quadruples.append(("=", varname, result, f"t{self.temp_counter}"))
        self.temp_counter+=1

        for scope in reversed(self.scopes):
            if varname in scope:
                scope[varname]["initialized"] = True
                break

        print(f"[assign] {varname} assigned")
        print(self.quadruples)


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
        print(f"[expresion] {args[0]}")
        return args[0]

    def exp(self, args):
        print(f"[exp] {args[0]}")
        return args[0]

    def termino(self, args):
        print(f"[termino] {args[0]}")
        return args[0]

    def cte(self, args):
        value = args[0]
        print(f"[cte] {value}")
        return value

    def idcte(self, args):
        value = args[0]
        if isinstance(args[0], Token) and args[0].type == 'ID':
            self.lookup_variable(value)
            self.is_initialized(value)
        return value

    def factor(self, args):
        print(f"[factor] {args}")
        if len(args) == 1:
            value = self.transform(args[0])
        else:
            value = self.transform(args[1])  # Ignora el signo (PLUS/MINUS) por ahora

        # Si la expresión anidada ya fue evaluada, no vuelvas a tocar la pila
        if isinstance(value, Token):
            operand = value.value
            self.operands.append(operand)

            if value.type == "ID":
                var = self.lookup_variable(operand)
                self.operand_types.append(var["type"])
            elif value.type == "CTE_INT":
                self.operand_types.append("int")
            elif value.type == "CTE_FLOAT":
                self.operand_types.append("float")
            else:
                raise TypeError(f"[error] Tipo no soportado: {value.type}")

            return operand
        elif isinstance(value, str):
            self.operands.append(value)
            return value
        elif isinstance(value, Tree):
            print("[factor] Ignoring Tree — expression already evaluated")
            return value  # ya está evaluado y pusheado por RPAR
        else:
            self.operands.append(value)
            return value

    def term_loop(self, args):
        left = self.transform(args[0])  # factor
        if len(args) > 1:
            right = self.transform(args[1])  # term_loop_prime
            return right  # Already processed
        return left

    def term_loop_prime(self, args):
        if not args:
            return

        op = args[0]

        right = self.operands.pop()
        left = self.operands.pop()

        type_right = self.operand_types.pop()
        type_left = self.operand_types.pop()

        cubo = CuboSemantico()
        result_type = cubo.check_operation(type_left, op, type_right)
        if result_type is None:
            raise TypeError(f"[semantic error] No se puede aplicar '{op}' entre '{type_left}' y '{type_right}'")

        temp = f"t{self.temp_counter}"
        self.temp_counter += 1

        self.quadruples.append((op, left, right, temp))
        self.operands.append(temp)
        self.operand_types.append(result_type)
        return temp


    def type(self, args):
        return args[0]
    
    def DIVIDE(self, args):
        print(f"[DIVIDE] {args[0]}")
        self.check_precedence(args[0])
        return args[0]
    
    def TIMES(self, args):
        print(f"[TIMES] {args[0]}")
        self.check_precedence(args[0])
        return args[0]
    
    def PLUS(self, args):
        print(f"[PLUS] {args[0]}")
        if not self.operators:
            self.operators.append(args[0])
        else:
            self.check_precedence(args[0])
        return args[0]
    
    def MINUS(self, args):
        print(f"[MINUS] {args[0]}")
        if not self.operators:
            self.operators.append(args[0])
        else:
            self.check_precedence(args[0])
        return args[0]
    
    def LPAR(self, args):
        self.operators.append('(')  # Solo lo empuja, no lo compara
        return args[0]

    def RPAR(self, args):
        while self.operators and self.operators[-1] != '(':
            op = self.operators.pop()
            right = self.operands.pop()
            left = self.operands.pop()
            temp = f"t{self.temp_counter}"
            self.temp_counter += 1
            self.quadruples.append((op, left, right, temp))
            self.operands.append(temp)
        if not self.operators or self.operators[-1] != '(':
            raise SyntaxError("Mismatched parenthesis")
        self.operators.pop()
        print(f"[RPAR] {args[0]}")
        print(f"[RPAR] {self.operators}")
        print(f"[RPAR] {self.operands}")
        return args[0]
    
    def check_precedence(self, op):
        print(f"[check_precedence] {op}")
        print("operators",self.operators)
        print("operands",self.operands)
        while self.operators and precedence[self.operators[-1]] >= precedence[op]:
            if self.operators[-1]=="(":
                break
            self.operators.pop()
            second_operand = self.operands.pop()
            first_operand = self.operands.pop()

            type2 = self.operand_types.pop()
            type1 = self.operand_types.pop()

            result_type = self.cubo.check_operation(type1, self.operators[-1], type2)
            if result_type is None:
                raise TypeError(f"[semantic error] Operación no válida: {type1} {op} {type2}")

            self.quadruples.append((op, first_operand, second_operand, f"t{self.temp_counter}"))
            self.operands.append(f"t{self.temp_counter}")
            self.operand_types.append(result_type)
            self.temp_counter += 1

    def check_identifiers(self, node):
        if isinstance(node, Token) and node.type == 'ID':
            print(f"[check] Checking ID token: {node.value}")
            self.lookup_variable(node.value)
            self.is_initialized(node.value)
        elif isinstance(node, Tree):
            for child in node.children:
                self.check_identifiers(child)
        elif isinstance(node, list):
            for item in node:
                self.check_identifiers(item)

