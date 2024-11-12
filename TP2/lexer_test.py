from lexer import lexer

def test_lexer(input_text):
    lexer.input(input_text)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

if __name__ == "__main__":
    test_input = 'your test input here'
    test_lexer(test_input)
