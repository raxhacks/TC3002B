from typing import Union
from lark import Lark
from ast_generator import ASTTransformer
from semantic_analyzer import SemanticAnalyzer
from grammar import grammar

class VirtualMachine:
    def __init__(self, compilation_data):
        self.quadruples = compilation_data['quadruples']
        self.function_directory = compilation_data['function_directory']
        self.memory_map = compilation_data['memory_map']
        
        # inicializamos los segmentos de memoria
        self.global_memory = {}
        self.local_memory = {}
        self.temp_memory = {}
        self.constant_memory = {}
        
        # inicializamos las variables globales
        for var_name, address in self.memory_map['globals'].items():
            self.global_memory[address] = var_name
            
        # inicializamos las constantes
        for const_type, const_values in self.memory_map['constants'].items():
            for value, address in const_values.items():
                if const_type == 'int':
                    self.constant_memory[address] = int(value)
                elif const_type == 'float':
                    self.constant_memory[address] = float(value)
        
        self.pc = 0 # puntero de programa
        self.call_stack = [] # pila de llamadas a funciones
        self.current_function = None # funcion actual
        self.param_mapping = {}  # mapeo de nombres de parametros a direcciones
        self.func_stack = []  # pila de contextos de funciones

    def execute(self):
        while self.pc < len(self.quadruples):
            quad = self.quadruples[self.pc]
            op = quad[0]
            
            if op == 'MAIN_START':
                self.pc = quad[3]
                continue
                
            elif op == 'FUNC':
                # solo movemos al siguiente quad
                self.pc += 1
                continue
                
            elif op == 'ENDFUNC':
                # regresamos de la funcion
                if self.call_stack:
                    self.pc = self.call_stack.pop()
                else:
                    self.pc += 1
                continue
                
            elif op == 'ERA':
                # preparamos para la llamada a la funcion y limpiamos la memoria local
                self.local_memory = {}
                self.pc += 1
                continue
                
            elif op == 'PARAM':
                # asignamos el valor del parametro en la memoria local
                param_value = self.get_value(quad[1])
                param_addr = quad[3]
                self.local_memory[param_addr] = param_value
                self.pc += 1
                continue
                
            elif op == 'GOSUB':
                # guardamos la direccion de retorno y saltamos a la funcion
                self.call_stack.append(self.pc + 1)
                func_info = self.function_directory[quad[1]]
                self.pc = func_info['start_quad']
                continue
                
            elif op == '=':
                src_value = self.get_value(quad[1])
                dest_addr = quad[3]
                self.set_value(dest_addr, src_value)
                
            elif op == '+':
                left = self.get_value(quad[1])
                right = self.get_value(quad[2])
                result = left + right
                self.temp_memory[quad[3]] = result
            elif op == '-':
                left = self.get_value(quad[1])
                right = self.get_value(quad[2])
                result = left - right
                self.temp_memory[quad[3]] = result
                
            elif op == '*':
                left = self.get_value(quad[1])
                right = self.get_value(quad[2])
                result = left * right
                self.temp_memory[quad[3]] = result
                
            elif op == '/':
                left = self.get_value(quad[1])
                right = self.get_value(quad[2])
                result = left / right
                self.temp_memory[quad[3]] = result
            
            elif op == '>':
                left = self.get_value(quad[1])
                right = self.get_value(quad[2])
                result = left > right
                self.temp_memory[quad[3]] = result
                
            elif op == '<':
                left = self.get_value(quad[1])
                right = self.get_value(quad[2])
                result = left < right
                self.temp_memory[quad[3]] = result
                
            elif op == '!=':
                left = self.get_value(quad[1])
                right = self.get_value(quad[2])
                result = left != right
                self.temp_memory[quad[3]] = result
                
            elif op == 'GOTOF':
                condition = self.get_value(quad[1])
                if not condition:
                    self.pc = quad[3]
                    continue
                
            elif op == 'GOTO':
                self.pc = quad[3]
                continue
                
            elif op == 'PRINT':
                item = quad[3]
                if isinstance(item, str) and item.startswith('"'):
                    print(item.strip('"'), end=' ')
                else:
                    value = self.get_value(item)
                    print(value, end=' ')
                    
            elif op == 'ENDPROGRAM':
                break
                
            else:
                raise ValueError(f"Unknown operation: {op}")
                
            self.pc += 1

        print()

    def get_value(self, address: Union[int, str]):
        # manejamos los nombres de los parametros
        if isinstance(address, str) and address.startswith('param'):
            param_addr = self.param_mapping.get(address)
            if param_addr is None:
                raise ValueError(f"Unknown parameter: {address}")
            address = param_addr
            
        # checamos la memoria de constantes primero
        if address in self.constant_memory:
            return self.constant_memory[address]
            
        # checamos la memoria global
        if address in self.global_memory:
            return self.global_memory[address]
            
        # checamos la memoria local
        if address in self.local_memory:
            return self.local_memory[address]
            
        # checamos la memoria temporal
        if address in self.temp_memory:
            return self.temp_memory[address]
            
        raise ValueError(f"Unknown address: {address}")

    def set_value(self, address: Union[int, str], value):
        # manejamos los nombres de los parametros
        if isinstance(address, str) and address.startswith('param'):
            param_addr = self.param_mapping.get(address)
            if param_addr is None:
                raise ValueError(f"Unknown parameter: {address}")
            address = param_addr
            
        # variables globales
        if address in self.global_memory:
            self.global_memory[address] = value
        # variables locales
        elif address in self.local_memory:
            self.local_memory[address] = value
        # variables temporales
        elif isinstance(address, int) and address >= 5000:
            self.temp_memory[address] = value
        else:
            raise ValueError(f"Cannot set value at unknown address: {address}")

def compile_and_execute(source_code):
    parser = Lark(grammar, start='start')
    transformer = ASTTransformer()
    analyzer = SemanticAnalyzer()
    
    try:
        parse_tree = parser.parse(source_code)
        ast = transformer.transform(parse_tree)
        analyzer.process_ast(ast.children[0])
        
        compilation_data = analyzer.get_compilation_data()
        
        vm = VirtualMachine(compilation_data)
        vm.execute()
        
    except Exception as e:
        print(f"\nError during execution: {str(e)}")

def main():
    print("=== BabyDuck VM ===")
    print("Enter your code (press Enter twice to finish):\n")
    
    code_lines = []
    
    while True:
        try:
            line = input()
            if line.strip() == '':
                break
            code_lines.append(line.strip())
        except EOFError:
            break
    
    source_code = ' '.join(code_lines)
    
    print("Output:")
    if source_code.strip():
        compile_and_execute(source_code)
    else:
        print("No code entered.")

if __name__ == "__main__":
    main()