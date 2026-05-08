# Automação de IA: Hill Climbing (8-Rainhas) + n8n 

Este projeto implementa uma solução completa, robusta e automatizada para o problema das **8-Rainhas** utilizando o algoritmo **Hill Climbing**. Toda a orquestração do experimento, análise preditiva de dados e geração de relatórios visuais é feita de forma integrada através do **n8n**, da inteligência do **Google Gemini** e de uma **API Flask em Python**.

---

## A ARQUITETURA DO SISTEMA

O sistema foi arquitetado em um formato de **Microsserviços**.

O n8n atua como o **Cérebro Orquestrador**, enquanto uma API Python atua como o **Motor de Processamento**, possuindo acesso total ao sistema de arquivos da máquina.

### O Pipeline de Dados:
1. **Execução:** O n8n ordena que a API rode o Hill Climbing 30 vezes. A API gera os dados, salva o histórico bruto (`.csv`) no disco e devolve um JSON encapsulado.

2. **Análise IA:** O n8n pega esse JSON e envia diretamente para a API do Google Gemini. O Gemini analisa os tempos de execução, iterações e taxas de sucesso, extraindo as 5 melhores soluções e criando uma categorização textual detalhada.

3. **Persistência de Métricas:** O n8n devolve a resposta crua do Gemini para a nossa API Python, que limpa o texto, converte para JSON estruturado e salva fisicamente (`metricas_gemini.json`).

4. **Relatórios Visuais e Planilhas:** O n8n aciona a API mais uma vez para consolidar os resultados em gráficos avançados (`.png`), tabelas estatísticas (`.png`) de fundo branco e uma **Planilha Excel** (`.xlsx`) com formatação condicional automática.

---

## ESTRUTURA DO PROJETO

```text
Trabalho-1-Inteligencia-Artificial/
│
├── api_projeto.py               # (API Flask Principal)
├── README.md                    # Este arquivo de documentação geral
│
├── codigo/                      # Scripts Lógicos
│   ├── hill_climbing.py         # Algoritmo Hill Climbing (Resolve o tabuleiro)
│   ├── analisar_resultados.py   # Motor de geração de Tabelas e Gráficos (Matplotlib)
│   └── gerar_relatorio_excel.py # Motor de geração de Planilha Excel (Pandas/Openpyxl)
│
├── resultados/                  # Diretório de Saída (Gerado dinamicamente)
│   ├── execucoes.csv                   # Histórico de cada uma das 30 execuções
│   ├── metricas_gemini.json            # Análise estruturada do Google Gemini
│   ├── relatorio_execucoes.xlsx        # Planilha Excel formatada com cores e larguras dinâmicas
│   ├── grafico1_sucesso_falha.png      # Gráfico de Barras: Sucesso vs Falha
│   ├── grafico2_iteracoes_linha.png    # Gráfico de Linha: Evolução das iterações
│   ├── grafico3_histograma_tempo.png   # Histograma: Distribuição do tempo
│   ├── grafico4_boxplot_iteracoes.png  # Boxplot: Consistência do algoritmo
│   ├── novo_grafico_dispersao.png      # Dispersão: Iterações vs. Tempo
│   ├── novo_grafico_pizza_parada.png   # Pizza: Distribuição de Condições de Parada
│   ├── novo_grafico_barras_reinicios.png # Barras: Frequência de Reinícios
│   ├── novo_grafico_heatmap_ocupacao.png # Mapa de Calor: Ocupação do Tabuleiro
│   ├── nova_tabela_top5_eficientes.png # Tabela: Top 5 Soluções Mais Eficientes
│   ├── nova_tabela_piores_gafes.png    # Tabela: Piores Gafes Computacionais
│   └── nova_tabela_resumo_categorico.png # Tabela: Resumo Categórico
│
└── workflow/                    # Arquivos de exportação
    └── Hill Climbing_n8n_workflow.json # Fluxo do n8n
```

---

## PRÉ-REQUISITOS DO SISTEMA

1. **Python 3.8+** instalado.
2. **n8n** instalado (Pode ser App Desktop, Docker ou pacote `npx n8n`).
3. **Chave de API do Google Gemini** (Gratuita no Google AI Studio).

---

## COMO RODAR O PROJETO 

Siga estas instruções cronologicamente para garantir o sucesso na execução do pipeline.

### PASSO 1: Instalação das Bibliotecas
Abra um terminal na raiz do projeto e instale todas as dependências exigidas pelo Python:
```bash
pip install flask pandas matplotlib seaborn openpyxl
```

### Passo 2: Ligar a API
No mesmo terminal, inicie o servidor da ponte Python do projeto:
```bash
python api_projeto.py
```
> **Atenção:** Mantenha este terminal aberto! Ele escutará as requisições na porta `5000` (ex: `http://127.0.0.1:5000`). Sem isso, o n8n não conseguirá processar.

### Passo 3: Importação no n8n
1. Abra o painel do seu n8n no navegador (`http://localhost:5678`).
2. Clique em **Add Workflow** > **Import from File**.
3. Selecione o arquivo `Hill Climbing_n8n_workflow.json` que está na pasta `workflow/`.

### Passo 4: Autenticação da IA
1. No fluxo importado, clique no nó **"Análise Gemini"**.
2. Na aba de parâmetros, procure o campo **URL**.
3. No final do endereço URL, encontre o texto `SUA_CHAVE_API_AQUI` e substitua-o pela sua API Key do Google (ex: `...?key=AIzaSy...`).
4. Salve o fluxo.

### Passo 5: Execução do Pipeline
1. No canto da tela, clique em **Execute Workflow** (ou Test Workflow).

2. O sistema passará por 4 etapas automáticas:
   - Acionará a rota `/executar`.
   - Conversará com o Google Gemini.
   - Acionará a rota `/salvar-metricas`.
   - Acionará a rota `/gerar-graficos`.

3. Quando todos os nós exibirem sinal verde de conclusão, **abra a pasta `resultados/`** no seu computador. Lá estarão os arquivos completos da análise do Hill Climbing (Tabelas PNG, Gráficos PNG, Planilha Excel e relatórios JSON/CSV)!

---

## O COMPORTAMENTO DOS NÓS (o que cada um faz)

1. **Iniciar Experimento (`Manual Trigger`)**: Botão de início de execução do pipeline.

2. **Rodar Hill Climbing (`HTTP Request`)**:
   - Dispara um `POST` para `http://127.0.0.1:5000/executar`.
   - A API chama o script `hill_climbing.py` (usando por padrão a variante *Subida da Encosta Mais Íngreme*) e executa-o 30 vezes. Transforma os resultados em um DataFrame do Pandas, salva em `resultados/execucoes.csv` e devolve um array limpo chamado `$json.execucoes` para a plataforma do n8n.

3. **Análise Gemini (`HTTP Request`)**: 
   - Dispara um `POST` para a API do Google `generativelanguage.googleapis.com`.
   - Pega as 30 execuções do passo anterior e injeta em um corpo `JSON`. O Gemini avalia métricas pesadas, seleciona o **Top 5 Melhores Soluções** e categoriza detalhadamente cada execução individual.

4. **Salvar Métricas Gemini (`HTTP Request`)**:
   - Dispara um `POST` para `http://127.0.0.1:5000/salvar-metricas`.
   - Envia a resposta bruta do Gemini (que contém vários cabeçalhos e tokens) para a nossa API. O Python filtra o conteúdo, certifica-se de que é um JSON válido e salva na pasta `resultados/metricas_gemini.json`.

5. **Gerar Gráficos e Planilha (`HTTP Request`)**:
   - Dispara um `POST` para `http://127.0.0.1:5000/gerar-graficos`.
   - A API chama o script `analisar_resultados.py` e, logo em seguida, o script `gerar_relatorio_excel.py`. Esses scripts leem autonomamente o `execucoes.csv`, plotam diversos gráficos e tabelas com fundo branco em PNG via Matplotlib, e geram um rico relatório Excel `.xlsx` com formatação condicional (verde para sucessos, vermelho para falhas).