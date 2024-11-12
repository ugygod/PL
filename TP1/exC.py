import json
import argparse

def fecho_epsilon(estados, delta):
    # Calcula o fecho epsilon de um conjunto de estados em um AFN.
    fecho = set(estados)
    pilha = list(estados)
    while pilha:
        estado = pilha.pop()
        novos_estados = delta.get(estado, {}).get("ε", [])
        for novo_estado in novos_estados:
            if novo_estado not in fecho:
                fecho.add(novo_estado)
                pilha.append(novo_estado)
    return fecho

def transicao(estados, simbolo, delta):
    # Calcula o conjunto de estados alcançáveis a partir de um conjunto de estados e um símbolo de entrada em um AFN.
    resultado = set()
    for estado in estados:
        transicoes = delta.get(estado, {})
        resultado.update(transicoes.get(simbolo, []))
    return resultado

def nfa_para_dfa(nfa):
    # Converte um autómato finito não determinístico (AFN) em um autômato finito determinístico (AFD).
    V, q0, F = nfa["V"], nfa["q0"], nfa["F"]
    delta_nfa = nfa["delta"]
    Q_dfa, delta_dfa = [], {}
    fila = [fecho_epsilon({q0}, delta_nfa)]
    mapa_estados_dfa = {frozenset(fila[0]): "q0"}

    while fila:
        estados_atuais = fila.pop(0)
        estado_dfa_atual = mapa_estados_dfa[frozenset(estados_atuais)]
        Q_dfa.append(estado_dfa_atual)

        for simbolo in V:
            proximos_estados = fecho_epsilon(transicao(estados_atuais, simbolo, delta_nfa), delta_nfa)
            if proximos_estados:
                if frozenset(proximos_estados) not in mapa_estados_dfa:
                    fila.append(proximos_estados)
                    novo_estado = "q" + str(len(mapa_estados_dfa))
                    mapa_estados_dfa[frozenset(proximos_estados)] = novo_estado
                delta_dfa.setdefault(estado_dfa_atual, {})[simbolo] = mapa_estados_dfa[frozenset(proximos_estados)]

        if any(estado in F for estado in estados_atuais):
            F.append(estado_dfa_atual)

    return {"V": V, "Q": Q_dfa, "delta": delta_dfa, "q0": q0, "F": F}

def main():
    # Configura o parser de argumentos da linha de comando
    parser = argparse.ArgumentParser(description='Converter AFND para AFD')
    parser.add_argument('input', help='Arquivo de entrada do AFND no formato JSON')
    parser.add_argument('--output', help='Arquivo de saída do AFD no formato JSON')
    args = parser.parse_args()

    # Lê a definição do AFND a partir do arquivo JSON
    with open(args.input, "r") as f:
        nfa = json.load(f)

    # Converte o AFND em um AFD
    dfa = nfa_para_dfa(nfa)

    # Define o nome do arquivo de saída ou usa o padrão "AFD.json"
    output_file = args.output if args.output else "AFD.json"
    # Escreve a definição do AFD no arquivo JSON de saída
    with open(output_file, "w") as f:
        json.dump(dfa, f, indent=4)

if __name__ == "__main__":
    main()

