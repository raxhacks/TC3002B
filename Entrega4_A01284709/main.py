from lark import Lark, LarkError, Visitor
from parser_and_scanner import grammar
from semantic_analyzer import SemanticAnalyzer

test1 = '''
program myprog;
var id1 : int; id2: float;
main {
    id1 = 1*3+4;
    print("Hola mundo");
}
end
'''

test2 = '''
program myprog;
var id1 : int;
main {
    id1 = 0;
    while (id1 < 10) do {
        print("Value of id1:", b);
        id1 = id1 + 1;
    };
}
end
'''

test3 = '''
program myprog;
var id1 : int; id2 : float;
void func1() [
    {
        id2 = 5;
    }
];
main {
    id1 = 5 + 10;
}
end
'''

test4 = '''
program myprog;
var id1 : int;
main {
    id1 = 5 + (3 * 2;
}
end
'''

parser = Lark(grammar, start="programa", parser="lalr")

tests = [test1, test2, test3, test4]
for idx, test in enumerate(tests, 1):
    try:
        print(f"Test {idx}:")
        tree = parser.parse(test)  # 1. Verifica sintaxis'
        SemanticAnalyzer().transform(tree)
        print("\nSintaxis y semántica correctas")
    except LarkError as e:
        print(f"\nError de sintaxis: {e}")
    except Exception as e:
        print(f"\nError semántico: {e}")
    print("-" * 40)