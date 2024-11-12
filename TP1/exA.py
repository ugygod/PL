import json
import argparse
from graphviz import Digraph

def ler_automato(arquivo):
    # Abre o ficheiro JSON e carrega a definição do autómato
    with open(arquivo, "r", encoding="utf-8") as f:
        return json.load(f)

def gerar_grafo(automato):
    # Inicializa um grafo utilizando a biblioteca Graphviz
    dot = Digraph(comment='Automato')

    # Adiciona um nó de início vazio ao grafo
    dot.node('start', shape='none', label='') 

    # Percorre os estados do autómato
    for estado in automato["delta"].keys():
        # Define a forma do nó como "duplo círculo" se o estado for final, senão como "círculo"
        shape = "doublecircle" if estado in automato["F"] else "circle"
        # Adiciona o estado como um nó ao grafo
        dot.node(estado, estado, shape=shape)

    # Percorre as transições do autómato
    for estado_inicial, transitions in automato["delta"].items():
        # Percorre as transições a partir de cada estado inicial
        for simbolo, estado_final in transitions.items():
            # Define o rótulo da transição como o símbolo, exceto se for "ε" (epsilon), que é representado como "ε"
            label = simbolo if simbolo != "ε" else "ε"
            # Adiciona uma aresta ao grafo representando a transição
            dot.edge(estado_inicial, estado_final, label=label)

    return dot

def reconhecer_palavra(automato, palavra):
    # Inicializa o estado atual com o estado inicial do autómato
    estado_atual = automato["q0"]
    # Inicializa uma lista para armazenar o caminho percorrido no autómato
    caminho = ["q0"]

    # Percorre cada símbolo na palavra a ser reconhecida
    for simbolo in palavra:
        # Verifica se o símbolo não pertence ao alfabeto do autómato
        if simbolo not in automato["delta"][estado_atual]:
            # Retorna uma mensagem indicando que a palavra não é reconhecida devido a um símbolo inválido
            return f"'{palavra}' não é reconhecida\n[símbolo '{simbolo}' não pertence ao alfabeto]"
        
        # Atualiza o estado atual de acordo com a transição para o próximo estado com base no símbolo atual
        estado_atual = automato["delta"][estado_atual].get(simbolo, None)
        # Adiciona o estado atual ao caminho percorrido
        caminho.append(estado_atual)
    
    # Verifica se o estado atual é um estado final do autómato
    if estado_atual in automato["F"]:
        # Retorna uma mensagem indicando que a palavra é reconhecida e o caminho percorrido
        return f"'{palavra}' é reconhecida\n[caminho {'->'.join(caminho)}]"
    else:
        # Retorna uma mensagem indicando que a palavra não é reconhecida porque o estado atual não é final
        return f"'{palavra}' não é reconhecida\n[caminho {'->'.join(caminho)}, {estado_atual} não é final]"

def main():
    # Configura o parser de argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Reconhecedor de linguagens baseado em um Autómato Finito Determinístico (AFD)")
    parser.add_argument('arquivo', help="Caminho para o ficheiro JSON que contém a definição do AFD")
    parser.add_argument('-graphviz', '--grafo', action='store_true', help="Gerar o grafo do autómato")
    parser.add_argument('-rec', '--palavra', help="Palavra a ser reconhecida pelo AFD")

    # Analisa os argumentos da linha de comando
    args = parser.parse_args()

    # Lê a definição do autómato a partir do ficheiro JSON
    automato = ler_automato(args.arquivo)

    # Gera o grafo do autómato se a opção correspondente for ativada
    if args.grafo:
        dot = gerar_grafo(automato)
        dot.render('automato_grafo', view="True", format='png')
       

    # Reconhece a palavra especificada pelo utilizador, se fornecida
    if args.palavra:
        resultado = reconhecer_palavra(automato, args.palavra)
        print(resultado)

if __name__ == "__main__":
    main()


