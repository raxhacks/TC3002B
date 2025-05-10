

grammar = r"""
%import common.WS
%ignore WS

PROGRAM: "program"
MAIN: "main"
END: "end"
INT: "int"
FLOAT: "float"
VOID: "void"
IF: "if"
ELSE: "else"
WHILE: "while"
DO: "do"
PRINT: "print"
VAR: "var"
ID: /[a-zA-Z_][a-zA-Z0-9_]*/
CTE_INT: /[0-9]+/
CTE_FLOAT: /[0-9]+\.[0-9]+/
CTE_STRING: /"[^"]*"/
PLUS: "+"
MINUS: "-"
TIMES: "*"
DIVIDE: "/"
EQUAL: "="
NEQ: "!="
LT: "<"
GT: ">"
LPAR: "("
RPAR: ")"
LBRACK: "["
RBRACK: "]"
LBRACE: "{"
RBRACE: "}"
COLON: ":"
SEMI: ";"
COMMA: ","

start: programa

# <Programa>
programa: PROGRAM ID SEMI pro_vars_dec funcs_loop MAIN body END #<Programa> → program id ; <PRO_VARS_DEC> <FUNCS_LOOP> main <Body> end
pro_vars_dec: #<PRO_VARS_DEC> → ε
    | vars #<PRO_VARS_DEC> → <VARS>
funcs_loop: #<FUNCS_LOOP> → ε
    | funcs funcs_loop #<FUNCS_LOOP> → <FUNCS> <FUNCS_LOOP>

# <VARS>
vars: VAR variable vars_prime #<VARS> → var <VARIABLE> <VARS’>
vars_prime: #<VARS’> → ε
    | variable vars_prime #<VARS’> → <VARIABLE> <VARS’>
variable: ID var_id COLON type SEMI #<VARIABLE> → id <VAR_ID> : <TYPE> ;
var_id: #<VAR_ID> → ε
    | COMMA ID var_id #<VAR_ID> → , id <VAR_ID>

# <TYPE>
type: INT #<TYPE> → int
    | FLOAT #<TYPE> → float

# <BODY>
body: LBRACE statement_loop RBRACE #<Body> → { <STATEMENT_LOOP> }
statement_loop: #<STATEMENT_LOOP> → ε
    | statement statement_loop #<STATEMENT_LOOP> → <STATEMENT> <STATEMENT_LOOP>


# <STATEMENT>
statement: assign #<STATEMENT> → <ASSIGN>
    | condition #<STATEMENT> → <CONDITION>
    | cycle #<STATEMENT> → <CYCLE>
    | f_call #<STATEMENT> → <F_Call>
    | print_stmt #<STATEMENT> → <PRINT>


# <Print>
print_stmt: PRINT LPAR expstr_loop RPAR SEMI #<Print> → print ( <EXPSTR_LOOP> ) ;
expstr_loop: expresion expstr_loop_prime #<EXPSTR_LOOP> → <EXPRESIÓN> <EXPSTR_LOOP’>
    | CTE_STRING expstr_loop_prime #<EXPSTR_LOOP> → cte.string <EXPSTR_LOOP’>
expstr_loop_prime: #<EXPSTR_LOOP’> → ε
    | COMMA expresion expstr_loop_prime #<EXPSTR_LOOP’> → , <EXPRESIÓN> <EXPSTR_LOOP’>
    | COMMA CTE_STRING expstr_loop_prime #<EXPSTR_LOOP’> → , cte.string <EXPSTR_LOOP’>

# <ASSIGN>
assign: ID EQUAL expresion SEMI #<ASSIGN> → id = <EXPRESIÓN> ;

# <CYCLE>
cycle: WHILE LPAR expresion RPAR DO body SEMI #<CYCLE> → while ( <EXPRESIÓN> ) do <CUERPO> ;

# <CONDITION>
condition: IF LPAR expresion RPAR body if_else SEMI #<CONDITION> → if ( <EXPRESIÓN> ) <Body> <IF_ELSE> ;
if_else: ELSE body #<IF_ELSE> → else <Body>
    | #<IF_ELSE> → ε

# <CTE>
cte: CTE_INT #<CTE> → cte_int
    | CTE_FLOAT #<CTE> → cte_float

# <EXPRESION>
expresion: exp #<EXPRESION> → <EXP>
    | exp GT exp # <EXPRESION> → <EXP> > <EXP>
    | exp LT exp # <EXPRESION> → <EXP> < <EXP>
    | exp NEQ exp # <EXPRESION> → <EXP> != <EXP>


# <EXP>
exp: exp_loop #<EXP> → <EXP_LOOP>
exp_loop: termino exp_loop_prime #<EXP_LOOP> → <TERMINO> <EXP_LOOP’>
exp_loop_prime: #<EXP_LOOP’> → ε
    | PLUS exp_loop #<EXP_LOOP’> → + <EXP_LOOP>
    | MINUS exp_loop #<EXP_LOOP’> → - <EXP_LOOP>

# <TERMINO>
termino: term_loop #<TERMINO> → <TERM_LOOP>
term_loop: factor term_loop_prime #<TERM_LOOP> → <FACTOR> <TERM_LOOP’>
term_loop_prime: #<TERM_LOOP’> → ε
    | TIMES term_loop #<TERM_LOOP’> → * <TERM_LOOP>
    | DIVIDE term_loop #<TERM_LOOP’> → / <TERM_LOOP>

# <FACTOR>
factor: LPAR expresion RPAR #<FACTOR> → ( <EXPRESIÓN> )
    | ops idcte #<FACTOR> → <OPS> <IDCTE>
ops: PLUS #<OPS> → +
    | MINUS #<OPS> → -
    | #<OPS> → ε
idcte: ID #<IDCTE> → id
    | cte #<IDCTE> → cte


# <FUNCS>
funcs: VOID ID LPAR id_loop RPAR LBRACK vars_des body RBRACK SEMI #<FUNCS> → void id ( <ID_LOOP> ) [ <VARS_DES> <Body> ]  ;
id_loop: #<ID_LOOP> → ε
    | ID COLON type id_loop_prime #<ID_LOOP> → id : <TYPE> <ID_LOOP’>
id_loop_prime: #<ID_LOOP’> → ε
    | COMMA ID COLON type id_loop_prime #<ID_LOOP’> → , id : <TYPE> <ID_LOOP’>
vars_des: #<VARS_DES> → ε
    | vars #<VARS_DES> → <VARS>

# <F_Call>
f_call: ID LPAR exp_fcall_loop RPAR SEMI #<F_Call> → id ( <EXP_FCALL_LOOP> ) ;
exp_fcall_loop: #<EXP_FCALL_LOOP> → ε
    | expresion exp_fcall_loop_prime #<EXP_FCALL_LOOP> → <EXPRESIÓN> <EXP_FCALL_LOOP’>
exp_fcall_loop_prime: #<EXP_FCALL_LOOP’> → ε
    | COMMA expresion exp_fcall_loop_prime #<EXP_FCALL_LOOP’> → , <EXPRESIÓN> <EXP_FCALL_LOOP’>
"""
