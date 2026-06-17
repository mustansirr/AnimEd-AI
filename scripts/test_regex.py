import re
import json

tests = [
    r'{"foo": "\\n"}', # properly escaped newline
    r'{"foo": "\n"}',  # literal newline in string
    r'{"foo": "\\frac"}', # properly escaped frac
    r'{"foo": "\frac"}',  # unescaped frac
    r'{"foo": "C:\Windows\System32"}', # Windows path
    r'{"foo": "\\"}', # single escaped backslash
    r'{"foo": "\\pi"}', # properly escaped pi
    r'{"foo": "\pi"}', # unescaped pi
    r'{"foo": "\"quoted\""}', # properly escaped quotes
]

for s in tests:
    print("\nOriginal:", repr(s))
    # Escape all single backslashes unless followed by " or \
    s2 = re.sub(r'(?<!\\)\\(?=[^"\\])', r'\\\\', s)
    print("Replaced:", repr(s2))
    try:
        res = json.loads(s2, strict=False)
        print("Parsed:", repr(res))
    except Exception as e:
        print("Error:", e)
