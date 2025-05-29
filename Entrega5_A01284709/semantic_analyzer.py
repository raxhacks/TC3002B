from lark import Token
from ast_generator import Function, Program, Block, Assignment, WhileLoop, IfStatement, PrintStatement, Literal, Variable, BinaryOp, UnaryOp, FunctionCall
from memory_manager import MemoryManager

class CuboSemantico:
    def __init__(self):
        self.ops = {
            ('int', '+', 'int'): 'int',
            ('int', '+', 'float'): 'float',
            ('float', '+', 'int'): 'float',
            ('float', '+', 'float'): 'float',
            ('int', '-', 'int'): 'int',
            ('int', '-', 'float'): 'float',
            ('float', '-', 'int'): 'float',
            ('float', '-', 'float'): 'float',
            ('int', '*', 'int'): 'int',
            ('int', '*', 'float'): 'float',
            ('float', '*', 'int'): 'float',
            ('float', '*', 'float'): 'float',
            ('int', '/', 'int'): 'float',
            ('int', '/', 'float'): 'float',
            ('float', '/', 'int'): 'float',
            ('float', '/', 'float'): 'float',
            ('int', '>', 'int'): 'bool',
            ('int', '>', 'float'): 'bool',
            ('float', '>', 'int'): 'bool',
            ('float', '>', 'float'): 'bool',
            ('int', '<', 'int'): 'bool',
            ('int', '<', 'float'): 'bool',
            ('float', '<', 'int'): 'bool',
            ('float', '<', 'float'): 'bool',
        }

    def check_operation(self, left_type, op, right_type):
        result = self.ops.get((left_type, op, right_type))
        if result:
            return result
        
        # si no hay exacto pero la operacion es valida
        if op in ('+', '-', '*', '/') and {left_type, right_type} == {'int', 'float'}:
            return 'float'
            
        return None
    
class SemanticAnalyzer:
    def __init__(self):
        self.semantic_cube = CuboSemantico()
        self.global_vars = {}
        self.current_scope_vars = self.global_vars
        self.scope_stack = [self.global_vars]
        self.function_directory = {}  # {name: {'params': [params], 'vars': {}, 'return_type': type}}
        self.current_function = None
        self.quadruples = []
        self.operand_stack = []
        self.memory = MemoryManager()
        self.param_count = 0
        self.main_start_quad = None
    
    def get_compilation_data(self):
        return {
            'quadruples': self.quadruples,
            'function_directory': self.function_directory,
            'memory_map': {
                'globals': {name:var['address'] for name, var in self.global_vars.items()},
                'constants': self.memory.constants
            }
        }

    def enter_scope(self):
        new_scope = {}
        self.scope_stack.append(new_scope)
        self.current_scope_vars = new_scope

    def exit_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope_vars = self.scope_stack[-1]

    def lookup_variable(self, name, check_initialized=True):
        # primero checamos el scope actual (locals y params)
        if name in self.current_scope_vars:
            var_info = self.current_scope_vars[name]
            if check_initialized and not var_info['initialized']:
                raise ValueError(f"Variable '{name}' used before initialization")
            return var_info
            
        # luego checamos el scope global
        if name in self.global_vars:
            var_info = self.global_vars[name]
            if check_initialized and not var_info['initialized']:
                raise ValueError(f"Global variable '{name}' used before initialization")
            return var_info
            
        raise NameError(f"Undeclared variable: {name}")
            
    def check_function_scope(self, var_name):
        # las variables globales son siempre accesibles
        if var_name in self.global_vars:
            return True
            
        if self.current_function:
            func_data = self.function_directory[self.current_function]
            # checamos si es un parametro o una variable local
            return var_name in func_data['vars'] or var_name in {p.name for p in func_data['params']}
        
        return True 

    def process_ast(self, ast_node):
        if isinstance(ast_node, Program):
            # procesamos las declaraciones globales
            for var_decl in ast_node.variables:
                for name in var_decl.names:
                    address = self.memory.allocate_global(name, var_decl.type)
                    self.global_vars[name] = {
                        'type': var_decl.type,
                        'initialized': False,
                        'scope': 'global',
                        'address': address
                    }

            self.quadruples.insert(0, ('MAIN_START', None, None, None))

            # procesamos las funciones en dado de que existan
            functions = ast_node.functions if isinstance(ast_node.functions, list) else []
            for func in functions:
                if isinstance(func, Function):
                    self.process_function(func)
                else:
                    print(f"Warning: Skipping non-Function node in functions list: {type(func)}")
            
            # comenzamos con el MAIN_START que apuntara a la primera instruccion del main
            self.main_start_quad = len(self.quadruples)
            
            # procesamos el main
            self.process_ast(ast_node.main)
            
            # actualizamos el MAIN_START con la posicion actual
            self.quadruples[0] = ('MAIN_START', None, None, self.main_start_quad)
            
            # agregamos el ENDPROGRAM al final
            self.quadruples.append(('ENDPROGRAM', None, None, None))
        
        elif isinstance(ast_node, Function):
            if ast_node.name in self.function_directory:
                raise NameError(f"Duplicate function: {ast_node.name}")
            
            # registramos la funcion
            self.function_directory[ast_node.name] = {
                'params': ast_node.parameters,
                'vars': {},
                'return_type': 'void'
            }
            
            # actualizamos el nombre de la funcion actual
            # y entramos al scope de la funcion
            self.current_function = ast_node.name
            self.enter_scope()
            
            # procesamos los parametros (considerados declarados y inicializados)
            for param in ast_node.parameters:
                self.current_scope_vars[param.name] = {
                    'type': param.type,
                    'initialized': True,
                    'scope': 'param'
                }
                self.function_directory[ast_node.name]['vars'][param.name] = param.type
            
            # procesamos las variables locales
            for var_decl in ast_node.variables:
                for name in var_decl.names:
                    if name in self.current_scope_vars:
                        raise NameError(f"Duplicate variable in function {ast_node.name}: {name}")
                    self.current_scope_vars[name] = {
                        'type': var_decl.type,
                        'initialized': False,
                        'scope': 'local'
                    }
                    self.function_directory[ast_node.name]['vars'][name] = var_decl.type
            
            # procesamos el cuerpo de la funcion
            self.process_ast(ast_node.body)
            
            self.exit_scope()
            self.current_function = None
        
        elif isinstance(ast_node, Block):
            # dado el arreglo de statements, procesamos cada uno
            for stmt in ast_node.statements:
                self.process_ast(stmt)
        
        elif isinstance(ast_node, Assignment):
            # primero verificamos si la variable existe
            var_info = self.lookup_variable(ast_node.target, check_initialized=False)
            if not var_info:
                raise NameError(f"Undeclared variable: {ast_node.target}")
            
            # procesamos el valor derecho de la asignacion
            result_type = self.process_expression(ast_node.value)
            
            # checamos el tipo de la asignacion
            if var_info['type'] != result_type:
                if not (var_info['type'] == 'float' and result_type == 'int'):
                    raise TypeError(f"Cannot assign {result_type} to {var_info['type']}")
            
            # al terminar la marcamos como inicializada
            var_info['initialized'] = True
            
            # generamos el quadruple usando la direccion de la variable
            rhs_value = self.operand_stack.pop()
            self.quadruples.append((
                '=', 
                rhs_value, 
                None, 
                var_info['address']
            ))

        elif isinstance(ast_node, WhileLoop):
            loop_start = len(self.quadruples)
            condition_type = self.process_expression(ast_node.condition)
            
            if condition_type != 'bool':
                raise TypeError("While condition must be boolean")
            
            # generamos el GOTOF para el false, no sabemos hacia donde aun
            self.quadruples.append(('GOTOF', self.operand_stack.pop(), None, None))
            false_jump_pos = len(self.quadruples) - 1
            
            # procesamos el cuerpo del while
            self.process_ast(ast_node.body)
            
            # generamos el GOTO para donde inicia la condicion
            self.quadruples.append(('GOTO', None, None, loop_start))
            
            # actualizamos el GOTOF para el false
            self.quadruples[false_jump_pos] = (
                'GOTOF', 
                self.quadruples[false_jump_pos][1], 
                None, 
                len(self.quadruples)
            )
        
        elif isinstance(ast_node, IfStatement):
            condition_type = self.process_expression(ast_node.condition)
            
            if condition_type != 'bool':
                raise TypeError("If condition must be boolean")
            
            # generamos el GOTOF para el false, no sabemos hacia donde aun
            self.quadruples.append(('GOTOF', self.operand_stack.pop(), None, None))
            false_jump_pos = len(self.quadruples) - 1
            
            # procesamos el then block
            self.process_ast(ast_node.then_block)
            
            # si existe else block, procesamos el else block
            if ast_node.else_block:
                # se genera el GOTO para saltar el else block
                self.quadruples.append(('GOTO', None, None, None))
                skip_else_pos = len(self.quadruples) - 1
                
                # actualizamos el GOTOF para el false
                self.quadruples[false_jump_pos] = (
                    'GOTOF', 
                    self.quadruples[false_jump_pos][1], 
                    None, 
                    len(self.quadruples)
                )
                
                # procesamos el else block
                self.process_ast(ast_node.else_block)
                
                # actualizamos el GOTO para saltar el else block
                self.quadruples[skip_else_pos] = (
                    'GOTO', 
                    None, 
                    None, 
                    len(self.quadruples)
                )
            else:
                # actualizamos el GOTOF para el false
                self.quadruples[false_jump_pos] = (
                    'GOTOF', 
                    self.quadruples[false_jump_pos][1], 
                    None, 
                    len(self.quadruples)
                )
        
        elif isinstance(ast_node, PrintStatement):
            for item in ast_node.items:
                if isinstance(item, Token) and item.type == 'CTE_STRING':
                    self.quadruples.append(('PRINT', None, None, item.value))
                else:
                    # si no es un string, procesamos la expresion
                    self.process_expression(item)
                    self.quadruples.append(('PRINT', None, None, self.operand_stack.pop()))
    
        elif isinstance(ast_node, FunctionCall):
                self.process_function_call(ast_node)

    def process_function_call(self, func_call):
        # verificamos si la funcion existe
        if func_call.name not in self.function_directory:
            raise NameError(f"Function '{func_call.name}' not declared")
        
        func_info = self.function_directory[func_call.name]
        
        # generamos el ERA para la funcion
        self.quadruples.append(('ERA', func_call.name, None, None))
        
        # procesamos los argumentos
        self.param_count = 0
        for arg in func_call.arguments:
            arg_type = self.process_expression(arg)
            
            # checamos si el tipo de parametro coincide
            if self.param_count >= len(func_info['params']):
                raise TypeError(f"Too many arguments for function '{func_call.name}'")
            
            expected_type = func_info['params'][self.param_count].type
            if arg_type != expected_type:
                if not (expected_type == 'float' and arg_type == 'int'):
                    raise TypeError(f"Type mismatch in argument {self.param_count+1} for '{func_call.name}'. Expected {expected_type}, got {arg_type}")
            
            # obtenemos la direccion actual del parametro
            param_addr = func_info['params'][self.param_count].address
            
            # generamos el PARAM usando la direccion actual
            arg_address = self.operand_stack.pop()
            self.quadruples.append(('PARAM', arg_address, None, param_addr))
            self.param_count += 1
        
        # checamos si el numero de parametros es correcto
        if self.param_count < len(func_info['params']):
            raise TypeError(f"Not enough arguments for function '{func_call.name}'")
        
        # generamos el GOSUB para la funcion
        self.quadruples.append(('GOSUB', func_call.name, None, None))
        
        # si la funcion no es void, procesamos el valor de retorno
        if func_info['return_type'] != 'void':
            temp_address = self.memory.get_temp_address(func_info['return_type'])
            self.quadruples.append(('RETURN', None, None, temp_address))
            self.operand_stack.append(temp_address)

    def process_function(self, func_node):
        if not isinstance(func_node, Function):
            raise TypeError(f"Expected Function node, got {type(func_node)}")
        
        if func_node.name in self.function_directory:
            raise NameError(f"Duplicate function: {func_node.name}")
        
        # registramos la funcion con todos los campos requeridos
        self.function_directory[func_node.name] = {
            'params': func_node.parameters,
            'vars': {},
            'return_type': 'void',
            'start_quad': len(self.quadruples) + 1,
            'end_quad': None
        }

        # generamos el FUNC para la funcion, este se usara para identificar la funcion en el codigo intermedio
        self.quadruples.append(('FUNC', func_node.name, func_node.parameters, None))
        
        self.current_function = func_node.name
        self.enter_scope()
        
        # procesamos los parametros y asignamos las direcciones
        for i, param in enumerate(func_node.parameters):
            param_addr = self.memory.allocate_param(param.name, param.type)
            param.address = param_addr
            self.current_scope_vars[param.name] = {
                'type': param.type,
                'address': param_addr,
                'initialized': True,
                'scope': 'param'
            }
            self.function_directory[func_node.name]['vars'][param.name] = param.type
        
        # procesamos las variables locales
        for var_decl in func_node.variables:
            for name in var_decl.names:
                if name in self.current_scope_vars:
                    raise NameError(f"Duplicate variable in function {func_node.name}: {name}")
                address = self.memory.allocate_local(name, var_decl.type)
                self.current_scope_vars[name] = {
                    'type': var_decl.type,
                    'initialized': False,
                    'scope': 'local',
                    'address': address
                }
                self.function_directory[func_node.name]['vars'][name] = var_decl.type
                
        self.function_directory[func_node.name]['vars_addresses'] = {name: var['address'] for name, var in self.current_scope_vars.items()}
        
        # procesamos el cuerpo de la funcion
        self.process_ast(func_node.body)
        
        self.exit_scope()
        self.current_function = None

        # generamos el ENDFUNC para la funcion
        self.quadruples.append(('ENDFUNC', func_node.name, None, None))
        
        # actualizamos el end_quad
        self.function_directory[func_node.name]['end_quad'] = len(self.quadruples) - 1

    def process_expression(self, expr):
        if isinstance(expr, Literal):
            address = self.memory.get_constant_address(expr.value, expr.type)
            self.operand_stack.append(address)
            return expr.type
            
        elif isinstance(expr, Variable):
            var_info = self.lookup_variable(expr.name)
            if not var_info:
                raise NameError(f"Undeclared variable: {expr.name}")
            
            self.operand_stack.append(var_info['address'])
            return var_info['type']
            
        if isinstance(expr, BinaryOp):
            left_type = self.process_expression(expr.left)
            right_type = self.process_expression(expr.right)
            
            # checamos si la operacion es valida
            result_type = self.semantic_cube.check_operation(left_type, expr.op, right_type)
            if result_type is None:
                raise TypeError(f"Invalid operation: {left_type} {expr.op} {right_type}")
            
            # obtenemos los operandos
            right_addr = self.operand_stack.pop()
            left_addr = self.operand_stack.pop()
            
            # generamos el temp para el resultado
            temp_address = self.memory.get_temp_address(result_type)
            self.quadruples.append((expr.op, left_addr, right_addr, temp_address))
            self.operand_stack.append(temp_address)
            
            return result_type