# Trabalho Prático - Inteligência Artificial: Problema das 8-Rainhas com Hill Climbing

Este repositório contém a implementação do algoritmo **Hill Climbing (Subida de Encosta)** aplicado ao Problema das N-Rainhas (com N=8), além da estrutura e instruções necessárias para a orquestração via **n8n** e a análise posterior de dados quantitativos, cumprindo rigorosamente todas as etapas especificadas.

## 📁 Estrutura do Projeto

Abaixo a estrutura completa e esperada de pastas do projeto (as pastas base já foram criadas):

```text
/projeto-ia/
│── codigo/
│   └── hill_climbing.py       # Script principal com a lógica de IA (Hill Climbing + Restart)
│
│── workflow/
│   └── n8n_workflow.json      # Onde você deverá salvar a exportação do seu workflow n8n
│
│── resultados/
│   ├── execucoes.csv          # Tabela de dados brutos que será gerada pela automação
│   ├── graficos.png           # (ou .jpg) Seus gráficos salvos a partir do Excel ou Matplotlib
│   └── analise.xlsx           # Planilha auxiliar com tratamento dos dados (caso use Excel)
│
│── relatorio/
│   └── relatorio_final.pdf    # A versão final do trabalho prático escrito
│
└── README.md                  # Este documento
```

---

## 🛠️ ETAPAS DA IMPLEMENTAÇÃO E EXECUÇÃO

### 1. Como Fazer Hill Climbing (Core Python)
O script localizado em `codigo/hill_climbing.py` foi escrito de forma estritamente modular e já resolve o problema computacional abordado:
- **Representação**: Utiliza um array unidimensional onde a posição indica a coluna e o valor indica a linha.
- **Função Objetivo ($h$)**: Analisa os pares para garantir a não-colisão nas linhas e diagonais. A meta é $h=0$.
- **Vizinhança e Variante**: Explora as 56 possibilidades (*Steepest Ascent*) e, em casos de travamento (Platô de 10 movimentos laterais ou Ótimo Local), realiza um reinício aleatório (*Random Restart*) com um limite de 20 reinícios por tentativa.

**Execução via Linha de Comando:**
Para testar, você pode abrir um terminal na raiz do projeto e rodar:
```bash
python codigo/hill_climbing.py --num_execucoes 30 --max_iter 200 --variante restart
```
Você também pode utilizar o argumento opcional `--seed <numero>` se quiser dados determinísticos. O algoritmo imprime puramente e exclusivamente um JSON válido com todos os dados calculados, para não quebrar a automação externa.

---

### 2. Como Integrar com n8n (Orquestração)
O n8n fará o meio de campo rodando a automação de experimentos de forma industrial (Low-Code). O pipeline deve seguir o fluxo sugerido no planejamento:

1. **Manual Trigger**: O nó de início manual do processo.
2. **Execute Command**: Crie este nó para rodar o script no terminal da sua máquina (onde o n8n está rodando localmente ou no Docker apontado para a máquina local):
   `python /caminho/absoluto/do/projeto/codigo/hill_climbing.py --num_execucoes 15 --max_iter 200`
3. **JSON (Item Lists) / Transform**: Como o retorno do Python é exclusivamente JSON, o n8n o transformará em arrays interativos automaticamente. O JSON conterá as exatas chaves solicitadas: `id_execucao`, `estado_inicial`, `iterações`, `tempo_ms`, `estado_final`, `h_final`, `sucesso`, `reinicios`, `platô`, `ótimo_local`.

---

### 3. Como Gerar o CSV
Existem dois caminhos principais para a geração do `execucoes.csv` em `resultados/`:
- **Via n8n (Recomendado na especificação)**: Após receber o JSON gerado pelo Python, insira um nó **Spreadsheet File** configurado para a ação "Write to File" em formato CSV, apontando o caminho de destino para sua pasta `/resultados/execucoes.csv`.
- **Via Google Sheets (Alternativa n8n)**: Outra forma muito prática é plugar um nó do **Google Sheets** no n8n que fará um "Append/Upsert" direto em uma planilha sua com os dados de execução. Em seguida, baixe-a como .xlsx para criar as tabelas dinâmicas.

---

### 4. Como Fazer Gráficos (Análise Experimental)
Com base nas 15 ou 30 execuções documentadas no seu CSV ou Sheets, calcule as seguintes métricas obrigatórias de tendência e dispersão: *média e desvio padrão das iterações, média e desvio padrão do tempo, taxa de sucesso, valor médio do h final*.

A partir desses dados organizados no Excel ou utilizando a biblioteca Python Matplotlib, você construirá os 4 gráficos sugeridos:
1. **Gráfico de Barras**: Frequência simples comparando execuções com `sucesso = true` vs `sucesso = false`.
2. **Gráfico de Linha**: A coluna `id_execucao` no eixo X e a quantidade de `iterações` daquela rodada no eixo Y.
3. **Histograma**: Selecione a coluna `tempo_ms`, divida-os em "bins" (faixas) para ver a curva de distribuição do desempenho.
4. **Boxplot**: Fundamental para a análise quantitativa; representará os quartis e possíveis *outliers* das `iterações` totais necessárias, sendo o melhor gráfico para mostrar a consistência do Random Restart.

---

### 5. Como Escrever o Relatório (Resultados e Discussão)
Utilize os dados estatísticos como suporte empírico para o seu texto. A estrutura sugerida para a discussão inclui:
- **Desempenho**: Avalie se o Hill Climbing rodou rápido ou lento, referenciando o gráfico do Boxplot e o tempo médio.
- **Problema principal e a Variante**: Explique conceitualmente por que o Hill Climbing simples falha em N-Rainhas e argumente por que o **Reinício Aleatório** e os mecanismos de escape para **Platôs/Ótimos locais** (contabilizados nas colunas do CSV) ajudaram. Relacione isso com a sua Taxa de Sucesso.
- **As 5 Melhores Soluções**: Busque no seu arquivo `.csv` as linhas onde `sucesso == true`, ordene pelas de menor `tempo_ms` e pegue o `estado_final` delas. Mostre essas 5 combinações no relatório.
- **Limitações e Melhorias Futuras**: Mencione outras formas de meta-heurísticas combinatórias que poderiam resolver o mesmo problema (Algoritmos Genéticos, Têmpera Simulada), comparando o que mudaria em relação ao seu Hill Climbing.
