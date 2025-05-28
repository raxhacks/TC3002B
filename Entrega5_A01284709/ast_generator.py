from dataclasses import dataclass
from typing import List, Optional, Union
from lark import Transformer, Token

@dataclass
class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    name: str
    variables: List['VariableDecl']
    functions: List['Function']
    main: 'Block'

@dataclass
class VariableDecl(ASTNode):
    names: List[str]
    type: str  # 'int' or 'float'

@dataclass
class Function(ASTNode):
    name: str
    parameters: List['Parameter']
    variables: List['VariableDecl']
    body: 'Block'

@dataclass
class Parameter(ASTNode):
    name: str
    type: str  # 'int' or 'float'
    address: int = None

# Statements
@dataclass
class Block(ASTNode):
    statements: List['Statement']

@dataclass
class Statement(ASTNode):
    pass

@dataclass
class Assignment(Statement):
    target: str
    value: 'Expression'

@dataclass
class IfStatement(Statement):
    condition: 'Expression'
    then_block: Block
    else_block: Optional[Block]

@dataclass
class WhileLoop(Statement):
    condition: 'Expression'
    body: Block

@dataclass
class FunctionCall(Statement):
    name: str
    arguments: List['Expression']

@dataclass
class PrintStatement(Statement):
    items: List[Union['Expression', str]]  # Can be expressions or string literals

# Expressions
@dataclass
class Expression(ASTNode):
    pass

@dataclass
class BinaryOp(Expression):
    left: Expression
    op: str  # +,-,*,/,>,<,!=
    right: Expression

@dataclass
class UnaryOp(Expression):
    op: str  # +,-
    operand: Expression

@dataclass
class Variable(Expression):
    name: str

@dataclass
class Literal(Expression):
    value: Union[int, float]
    type: str  # int or float

class ASTTransformer(Transformer):
    def _create_node(self, **attrs):
        return type('Node', (), attrs)
    
    def programa(self, items):
        # PROGRAM ID SEMI pro_vars_dec funcs_loop MAIN body END
        variables = items[3] if isinstance(items[3], list) else []
        functions = items[4] if isinstance(items[4], list) else []
        
        # aplanar funciones en caso de que haya listas anidadas
        flat_functions = []
        for item in functions:
            if isinstance(item, list):
                flat_functions.extend(item)
            else:
                flat_functions.append(item)
        
        return Program(
            name=items[1].value,
            variables=variables,
            functions=flat_functions,
            main=items[6]
        )
    
    def pro_vars_dec(self, items):
        return items[0] if items else []
    
    def funcs_loop(self, items):
        # aplanar funciones en caso de que haya listas anidadas
        functions = []
        for item in items:
            if isinstance(item, list):
                functions.extend(item)
            else:
                functions.append(item)
        return functions
    
    def vars(self, items):
        # VAR variable vars_prime
        variables = [items[1]]
        if len(items) > 2:
            variables.extend(items[2])
        return variables
    
    def vars_prime(self, items):
        # aplanar variables en caso de que haya listas anidadas
        result = []
        for item in items:
            if isinstance(item, list):
                result.extend(item)
            else:
                result.append(item)
        return result
    
    def variable(self, items):
        # ids COLON type SEMI
        return VariableDecl(
            names=items[0] if isinstance(items[0], list) else [items[0]],
            type=items[2]
        )
    
    def ids(self, items):
        # ID ids_prime
        names = [items[0].value]
        if len(items) > 1:
            if isinstance(items[1], list):
                names.extend(items[1])
            else:
                names.append(items[1])
        return names

    def ids_prime(self, items):
        if not items:
            return []
        # COMMA ID ids_prime
        names = [items[1].value]
        if len(items) > 2:
            if isinstance(items[2], list):
                names.extend(items[2])
            else:
                names.append(items[2])
        return names
    
    def type(self, items):
        return items[0].type.lower()
    
    # Statements
    def body(self, items):
        # LBRACE statement_loop RBRACE
        return Block(statements=items[1])
    
    def statement_loop(self, items):
        # aplanar statements en caso de que haya listas anidadas
        statements = []
        for item in items:
            if isinstance(item, list):
                statements.extend(item)
            else:
                statements.append(item)
        return statements
    
    def statement(self, items):
        return items[0]
    
    def assign(self, items):
        # ID EQUAL expresion SEMI
        return Assignment(target=items[0].value, value=items[2])
    
    def condition(self, items):
        # IF LPAR expresion RPAR body if_else SEMI
        if_else = items[5]
        else_block = if_else if isinstance(if_else, Block) else None
        return IfStatement(
            condition=items[2],
            then_block=items[4],
            else_block=else_block
        )
    
    def if_else(self, items):
        if not items:
            return None
        # ELSE body
        return items[1]
    
    def cycle(self, items):
        # WHILE LPAR expresion RPAR DO body SEMI
        return WhileLoop(
            condition=items[2],
            body=items[5]
        )
    
    def print_stmt(self, items):
        # PRINT LPAR expstr_loop RPAR SEMI
        return PrintStatement(items=items[2])
    
    def expstr_loop(self, items):
        items_list = [items[0]]
        if len(items) > 1:
            items_list.extend(items[1])
        return items_list
    
    def expstr_loop_prime(self, items):
        if not items:
            return []
        # COMMA expresion or COMMA CTE_STRING
        items_list = [items[1]]
        if len(items) > 2:
            items_list.extend(items[2])
        return items_list
    
    # Expressions
    def expresion(self, items):
        if len(items) == 1:
            return items[0]
        # exp OP exp
        return BinaryOp(left=items[0], op=items[1].value, right=items[2])
    
    def exp(self, items):
        return items[0]
    
    def exp_loop(self, items):
        # exp_loop: termino exp_loop_prime
        left = items[0]
        
        if len(items) == 1 or not items[1]:
            return left
        
        exp_loop_prime = items[1]
        
        if isinstance(exp_loop_prime, list):
            if not exp_loop_prime:
                return left
            op = exp_loop_prime[0].value if isinstance(exp_loop_prime[0], Token) else exp_loop_prime[0]
            right = exp_loop_prime[1]
            return BinaryOp(left=left, op=op, right=right)
        
        if hasattr(exp_loop_prime, 'children'):
            op_token = exp_loop_prime.children[0]
            right = exp_loop_prime.children[1]
            return BinaryOp(left=left, op=op_token.value, right=right)
        
        return left

    def exp_loop_prime(self, items):
        # exp_loop_prime: PLUS exp_loop | MINUS exp_loop | ε
        if not items:
            return []
        return items[:2]
    
    def termino(self, items):
        return items[0]
    
    def term_loop(self, items):
        # term_loop: factor term_loop_prime
        left = items[0]
        
        # si no hay term_loop_prime o es vacio, solo retorna el factor
        if len(items) == 1 or not items[1]:
            return left
        
        # term_loop_prime contiene el operador y el operando derecho
        term_loop_prime = items[1]
        
        # si term_loop_prime es una lista (del transformer)
        if isinstance(term_loop_prime, list):
            if not term_loop_prime:
                return left
            # la lista debe contener [operador, operando derecho]
            op = term_loop_prime[0].value if isinstance(term_loop_prime[0], Token) else term_loop_prime[0]
            right = term_loop_prime[1]
            return BinaryOp(left=left, op=op, right=right)
        
        # si term_loop_prime es un Tree (original parse tree)
        if hasattr(term_loop_prime, 'children'):
            op_token = term_loop_prime.children[0]
            right = term_loop_prime.children[1]
            return BinaryOp(left=left, op=op_token.value, right=right)
        
        return left

    def term_loop_prime(self, items):
        # term_loop_prime: TIMES term_loop | DIVIDE term_loop | ε
        if not items:
            return []
        
        # retorna el operador y el operando derecho
        return items[:2] 
    
    def factor(self, items):
        if len(items) == 3:  # LPAR expresion RPAR
            return items[1]
        # ops idcte
        operand = items[1]
        if items[0]: # tiene operador
            return UnaryOp(op=items[0], operand=operand)
        return operand
    
    def ops(self, items):
        return items[0].value if items else None
    
    def idcte(self, items):
        if isinstance(items[0], Token) and items[0].type == 'ID':
            return Variable(name=items[0].value)
        return items[0]  # cte
    
    def cte(self, items):
        value = items[0].value
        if items[0].type == 'CTE_INT':
            return Literal(value=int(value), type='int')
        elif items[0].type == 'CTE_FLOAT':
            return Literal(value=float(value), type='float')
    
    # Functions
    def funcs(self, items):
        # VOID ID LPAR id_loop RPAR LBRACK vars_des body RBRACK SEMI
        return Function(
            name=items[1].value,
            parameters=items[3] if isinstance(items[3], list) else [],
            variables=items[6] if isinstance(items[6], list) else [],
            body=items[7]
        )
    
    def id_loop(self, items):
        if not items:
            return []
        # ID COLON type id_loop_prime
        param = Parameter(name=items[0].value, type=items[2])
        params = [param]
        if len(items) > 3:
            params.extend(items[3])
        return params
    
    def id_loop_prime(self, items):
        if not items:
            return []
        # COMMA ID COLON type id_loop_prime
        param = Parameter(name=items[1].value, type=items[3])
        params = [param]
        if len(items) > 4:
            params.extend(items[4])
        return params
    
    def vars_des(self, items):
        return items[0] if items else []
    
    def f_call(self, items):
        # ID LPAR exp_fcall_loop RPAR SEMI
        return FunctionCall(name=items[0].value, arguments=items[2])
    
    def exp_fcall_loop(self, items):
        if not items:
            return []
        # expresion exp_fcall_loop_prime
        args = [items[0]]
        if len(items) > 1:
            args.extend(items[1])
        return args
    
    def exp_fcall_loop_prime(self, items):
        if not items:
            return []
        # COMMA expresion exp_fcall_loop_prime
        args = [items[1]]
        if len(items) > 2:
            args.extend(items[2])
        return args