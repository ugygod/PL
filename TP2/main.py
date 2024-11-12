import sys
from grammar import parse_file

def main():
    # Verifica se o número de argumentos da linha de comando é igual a 2
    if len(sys.argv) != 2:
        # Imprime a mensagem de uso correto do script
        print("Usage: python main.py <filename>")
        # Encerra o programa com o código de status 1 (indicando um erro)
        sys.exit(1)

    # Obtém o nome do arquivo a partir dos argumentos da linha de comando
    filename = sys.argv[1]
    # Chama a função parse_file com o nome do arquivo
    parse_file(filename)

# Verifica se o script está sendo executado diretamente (e não importado como módulo)
if __name__ == "__main__":
    # Chama a função principal
    main()


