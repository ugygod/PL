import json
import argparse

def construir_afnd_de_er(er_json, alfabeto=None, estados=None, transicoes=None, estados_finais=None, contador_estado=0):
    # Conjuntos para armazenar informações sobre o AFND
    alfabeto = set()  # Símbolos do alfabeto
    estados = set()  # Estados do AFND
    transicoes = {}  # Transições do AFND
    estados_finais = set()  # Estados finais do AFND

    contador_estado = 0  # Contador para gerar nomes de estados únicos

    # Função para gerar um novo nome de estado
    def gerar_estado():
        nonlocal contador_estado
        nome_estado = f"q{contador_estado}"
        contador_estado += 1
        return nome_estado

    # Função para processar um nó da árvore de expressão regular
    def processar_no(no, estado_atual):
        nonlocal alfabeto, estados, transicoes, estados_finais

        if isinstance(no, dict):
            if "simb" in no:
                # Se o nó for um símbolo, adiciona-o ao alfabeto e cria uma transição para um novo estado
                alfabeto.add(no["simb"])
                novo_estado = gerar_estado()
                estados.add(novo_estado)
                transicoes.setdefault(estado_atual, {}).setdefault(no["simb"], []).append(novo_estado)
                return novo_estado

            if "op" in no:
                if no["op"] == "seq":
                    # Se for uma sequência de símbolos, conecta cada elemento da sequência
                    estado_atual_seq = estado_atual
                    for arg in no["args"]:
                        novo_estado_seq = processar_no(arg, estado_atual_seq)
                        if novo_estado_seq:
                            estado_atual_seq = novo_estado_seq
                    estados_finais.add(estado_atual_seq)

                elif no["op"] == "alt":
                    # Se houver alternância entre expressões, são criados novos estados para cada opção.
                    novo_estado_esquerdo = processar_no(no["args"][0], estado_atual)
                    novo_estado_direito = processar_no(no["args"][1], estado_atual)
                    if novo_estado_esquerdo:
                        estados_finais.add(novo_estado_esquerdo)
                    if novo_estado_direito:
                        estados_finais.add(novo_estado_direito)
                    transicoes.setdefault(estado_atual, {}).setdefault("ε", []).extend([novo_estado_esquerdo, novo_estado_direito])

                elif no["op"] == "kle":
                    # Se for um fecho de Kleene, cria um loop com transições epsilon
                    novo_estado_kle = gerar_estado()
                    estados.add(novo_estado_kle)
                    estados_finais.add(novo_estado_kle)  # Torna o novo estado um estado final
                    estado_interno = processar_no(no["args"][0], novo_estado_kle)
                    if estado_interno:
                        transicoes.setdefault(estado_interno, {}).setdefault("ε", []).append(novo_estado_kle)
                    transicoes.setdefault(estado_atual, {}).setdefault("ε", []).append(novo_estado_kle)
                    transicoes.setdefault(novo_estado_kle, {}).setdefault("ε", []).append(estado_atual)

    estado_inicial = gerar_estado()  # Estado inicial
    estados.add(estado_inicial)
    processar_no(er_json, estado_inicial)  # Processa a expressão regular
    estados_finais.add(estado_inicial)  # Adiciona o estado inicial aos finais para permitir reconhecimento de palavra vazia

    # Retorna a estrutura do AFND
    return {
        "V": sorted(list(alfabeto)),
        "Q": sorted(list(estados)),
        "delta": transicoes,
        "q0": estado_inicial,
        "F": sorted(list(estados_finais))
    }

def ler_er_de_arquivo(caminho_arquivo):
    # Lê a expressão regular de um arquivo JSON
    with open(caminho_arquivo, "r") as arquivo:
        er_json = json.load(arquivo)
    return er_json

def guardar_afnd_em_arquivo(afnd_json, caminho_arquivo):
    # Guarda a estrutura do AFND em um arquivo JSON
    with open(caminho_arquivo, "w") as arquivo:
        json.dump(afnd_json, arquivo, indent=4)

def main():
    parser = argparse.ArgumentParser(description='Converte uma expressão regular em um autômato finito não determinístico (AFND).')
    parser.add_argument('input', help='Arquivo JSON contendo a expressão regular')
    parser.add_argument('--output', help='Nome do arquivo de saída para o AFND (padrão: afnd.json)', default='afnd.json')
    args = parser.parse_args()

    er_json = ler_er_de_arquivo(args.input)  # Lê a expressão regular do arquivo
    afnd_json = construir_afnd_de_er(er_json, alfabeto=set(), estados=set(), transicoes={}, estados_finais=set(), contador_estado=0) # Constrói o AFND a partir da expressão regular
    guardar_afnd_em_arquivo(afnd_json, args.output)  # Guarda o AFND em um arquivo JSON

    print(f"A estrutura do AFND foi guardada no arquivo '{args.output}'.")

if __name__ == "__main__":
    main()