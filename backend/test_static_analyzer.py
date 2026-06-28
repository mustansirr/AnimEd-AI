import ast
import sys
sys.path.append('c:/Users/Samruddhi/Desktop/manima/backend')
from app.agents.nodes.static_analyzer import CodeValidator

test_code = """
x: int = 5
items: list[str] = []
config: dict[str, int] = {}
value: str
value = 'hello'

x += 1
for loop_var in items:
    print(loop_var)

with open('file.txt') as f:
    print(f)

try:
    pass
except Exception as e:
    print(e)

[comp_var for comp_var in items]

match x:
    case 5 as my_match:
        print(my_match)
"""

validator = CodeValidator()
validator.visit(ast.parse(test_code))
print('Errors:', validator.errors)
if not validator.errors:
    print('SUCCESS! Analyzer behaves correctly for all advanced nodes.')
