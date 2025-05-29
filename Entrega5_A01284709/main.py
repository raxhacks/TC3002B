from lark import Lark
from grammar import grammar
from semantic_analyzer import SemanticAnalyzer
from ast_generator import ASTTransformer

test1 = '''
program myprog;
var id1,x,y : int; id2: float;
main {
    x = 12;
    id2 = 1*3-4-2;
    if (1 > 0) {
        y = 1;
    } else {
        y = 0;
    };
}
end
'''

test2 = '''
program myprog;
var id1 : int;
main {
    id1 = 0;
    while (id1 < 10) do {
        print("Value of id1:", id1);
        id1 = id1 + 1;
    };
}
end
'''

test3 = '''
program myprog;
var id1 : int; id2 : float;
void func1(x: int, y: float) [
var id3 : int;
    {
        id2 = x + y;
        print("id2: ", id2);
    }
];
main {
    id1 = 2 + 10;
    func1(id1,2.5);
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

test5 = '''
program fibonacci;
var n,a,b,count,temp : int;
main {
    n = 10;
    if (n < 0) {
        print("Error: n must be greater than 0");
    };
    if (n < 1) {
        print("Fibonacci of", n, "is", 0);
    };
    if (n < 2) {
        print("Fibonacci of", n, "is", 1);
    } else {
        a = 0;
        b = 1;
        count = 2;
        while (count < n+1) do {
            temp = a+b;
            a = b;
            b = temp;
            count = count + 1;
        };
        print("Fibonacci of", n, "is", b);
    };
}
end
'''

test5 = '''
program fibonacci;
var input: int;
void print_fibonacci(n: int, b:int) [
    {
        print("Fibonacci of", n, "is", b);
    }
];
void fibonacci(n: int) [
var a,b,count,temp : int;
{
    if (n < 0) {
        print("Error: n must be greater than 0");
    };
    if (n < 1) {
        print_fibonacci(n,0);
    };
    if (n < 2) {
        print_fibonacci(n,1);
    } else {
        a = 0;
        b = 1;
        count = 2;
        while (count < n+1) do {
            temp = a+b;
            a = b;
            b = temp;
            count = count + 1;
        };
        print_fibonacci(n,b);
    };
}];
main {
    input = 10;
    fibonacci(input);
}
end
'''

tests = [
    {'name': 'Test 1', 'code': test1},
    {'name': 'Test 2', 'code': test2},
    {'name': 'Test 3', 'code': test3},
    {'name': 'Test 4', 'code': test4}
]

parser = Lark(grammar, start='start')

for test in tests:
    print(f"\n{'='*50}")
    print(f"Running {test['name']}")
    print(f"{'='*50}")
    
    try:
        parse_tree = parser.parse(test['code'])
        
        ast = ASTTransformer().transform(parse_tree)
        program_node = ast.children[0]
        
        analyzer = SemanticAnalyzer()
        analyzer.process_ast(program_node)
        
        print("\nGenerated Quadruples:")
        for i, quad in enumerate(analyzer.quadruples):
            print(f"{i}: {quad}")
            
    except Exception as e:
        print(f"\nError in {test['name']}:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        continue
