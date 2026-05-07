import random
import time
import json
import argparse

def calcular_conflitos(estado):
    """Calcula o número de pares de rainhas em conflito (mesma linha ou diagonal)."""
    h = 0
    n = len(estado)
    for i in range(n):
        for j in range(i + 1, n):
            if estado[i] == estado[j]:  # Mesma linha
                h += 1
            elif abs(estado[i] - estado[j]) == abs(i - j):  # Mesma diagonal
                h += 1
    return h

def obter_melhor_vizinho(estado):
    """Gera todos os 56 vizinhos possíveis e retorna o melhor (ou um dos melhores aleatoriamente)."""
    melhores_vizinhos = []
    menor_h = float('inf')
    n = len(estado)
    
    for col in range(n):
        for linha in range(n):
            if estado[col] != linha:
                vizinho = list(estado)
                vizinho[col] = linha
                h = calcular_conflitos(vizinho)
                
                if h < menor_h:
                    menor_h = h
                    melhores_vizinhos = [vizinho]
                elif h == menor_h:
                    melhores_vizinhos.append(vizinho)
                    
    # Retorna aleatoriamente um dos melhores vizinhos para evitar viés direcional
    return random.choice(melhores_vizinhos), menor_h

def executar_hill_climbing(id_execucao, max_iter, variante="restart"):
    n = 8
    # Estado: array de 8 posições onde índice = coluna, valor = linha (0-7)
    estado_inicial = [random.randint(0, n - 1) for _ in range(n)]
    estado_atual = list(estado_inicial)
    h_atual = calcular_conflitos(estado_atual)
    
    iteracoes = 0
    reinicios = 0
    movimentos_laterais = 0
    
    max_reinicios = 20
    max_laterais = 10
    
    sucesso = False
    plato = False
    otimo_local = False
    
    inicio_tempo = time.perf_counter()
    
    while True:
        if h_atual == 0:
            sucesso = True
            break
            
        if iteracoes >= max_iter:
            break
            
        vizinho, h_vizinho = obter_melhor_vizinho(estado_atual)
        iteracoes += 1
        
        if h_vizinho < h_atual:
            estado_atual = vizinho
            h_atual = h_vizinho
            movimentos_laterais = 0
            plato = False
            otimo_local = False
        elif h_vizinho == h_atual:
            estado_atual = vizinho
            h_atual = h_vizinho
            movimentos_laterais += 1
            if movimentos_laterais >= max_laterais:
                plato = True
        else:
            otimo_local = True
            
        # Condições de parada para esta tentativa / gatilhos de reinício aleatório
        if plato or otimo_local:
            if variante == "restart" and reinicios < max_reinicios:
                reinicios += 1
                estado_atual = [random.randint(0, n - 1) for _ in range(n)]
                h_atual = calcular_conflitos(estado_atual)
                movimentos_laterais = 0
                plato = False
                otimo_local = False
            else:
                # Esgotou os reinícios ou não está usando a variante de restart
                break
                
    fim_tempo = time.perf_counter()
    tempo_ms = round((fim_tempo - inicio_tempo) * 1000, 2)
    
    return {
        "id_execucao": id_execucao,
        "estado_inicial": estado_inicial,
        "iterações": iteracoes,
        "tempo_ms": tempo_ms,
        "estado_final": estado_atual,
        "h_final": h_atual,
        "sucesso": sucesso,
        "reinicios": reinicios,
        "platô": plato,
        "ótimo_local": otimo_local
    }

def main():
    parser = argparse.ArgumentParser(description="Algoritmo Hill Climbing para o Problema das 8-Rainhas")
    parser.add_argument("--num_execucoes", type=int, default=1, help="Número de execuções do algoritmo")
    parser.add_argument("--max_iter", type=int, default=200, help="Número máximo de iterações permitidas por execução")
    parser.add_argument("--variante", type=str, default="restart", help="Variante do algoritmo (ex: restart)")
    parser.add_argument("--seed", type=int, default=None, help="Semente para o gerador de números aleatórios")
    
    args = parser.parse_args()
    
    # Define a semente caso seja fornecida
    if args.seed is not None:
        random.seed(args.seed)
            
    resultados = []
    for i in range(1, args.num_execucoes + 1):
        resultado = executar_hill_climbing(i, args.max_iter, args.variante)
        resultados.append(resultado)
        
    # Garante a saída exclusivamente em JSON no terminal
    if args.num_execucoes == 1:
        print(json.dumps(resultados[0], ensure_ascii=False))
    else:
        print(json.dumps(resultados, ensure_ascii=False))

if __name__ == "__main__":
    main()
