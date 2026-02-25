from lexer import Lexer
with open("samples/sample25.prose") as f:
    text = f.read()
line17 = text.split("\n")[16]
l = Lexer(line17)
for t in l.tokenize():
    print(t)
