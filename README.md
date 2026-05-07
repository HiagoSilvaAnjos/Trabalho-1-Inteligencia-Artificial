# 👑 Automação de IA: Hill Climbing (8-Rainhas) + n8n + Gemini

Este projeto implementa uma solução completa e automatizada para o problema das **8-Rainhas** utilizando o algoritmo **Hill Climbing**. Toda a execução, análise de dados e geração de gráficos é orquestrada através do **n8n**, com a inteligência do **Google Gemini** para análises profundas, e uma **API Flask em Python** para gerenciar o ambiente local de forma segura e eficiente.

---

## 🏗️ Como o Sistema Funciona (Arquitetura)

O sistema foi arquitetado em formato de **Serviço/API Local (A "Abordagem B")**.
Em vez do n8n rodar comandos diretamente no terminal (o que gera problemas de permissão e limitação de manipulação de arquivos, como o famoso erro `Module 'fs' is disallowed`), o sistema utiliza uma API em Python como "Ponte":

1. **n8n (Orquestrador)**: Gerencia o fluxo visual, o disparo das tarefas e integrações externas.
2. **API Flask (`api_projeto.py`)**: Fica escutando as ordens do n8n na porta `5000`. Ela tem permissão total para rodar os códigos localmente, acessar as pastas e salvar os arquivos no seu computador sem ser bloqueada pelo n8n.
3. **Algoritmos Core (`codigo/`)**: Onde a mágica acontece. Scripts isolados que resolvem o problema e geram os gráficos.
4. **Google Gemini**: Integrado via n8n para atuar como um "Analista de Dados Inteligente", avaliando o desempenho e categorizando cada execução do algoritmo.

---

## 📂 Estrutura de Pastas

```text
Trabalho-1-Inteligencia-Artificial/
│
├── api_projeto.py          # (O Coração) Servidor Flask que conecta o n8n aos scripts
├── TUTORIAL_EXECUCAO.md    # Guia rápido de execução alternativa
├── README.md               # Este arquivo de documentação geral
│
├── codigo/                 # Scripts principais
│   ├── hill_climbing.py         # Algoritmo Hill Climbing (30 execuções)
│   └── analisar_resultados.py   # Script de geração de gráficos estatísticos
│
├── resultados/             # Pasta gerada automaticamente após a execução
│   ├── execucoes.csv            # Dados brutos de cada execução (criado pela API)
│   ├── grafico1_sucesso_falha.png
│   ├── grafico2_iteracoes_linha.png
│   ├── grafico3_histograma_tempo.png
│   └── grafico4_boxplot_iteracoes.png
│
└── workflow/               # Arquivos de exportação do n8n
    └── n8n_workflow.json        # Fluxo do n8n para importar
```

---

## 🛠️ Pré-requisitos

Para rodar este projeto na sua máquina e poder modificá-lo, você precisa ter:

1. **Python 3.8+** instalado em seu sistema.
2. O **n8n** instalado (pode ser via `npx n8n`, pacote global do npm, Docker ou Desktop App).
3. Uma **Chave de API do Google Gemini** (gerada gratuitamente no Google AI Studio).

---

## 🚀 Como Rodar o Projeto (Passo a Passo)

A execução do projeto é dividida em três etapas vitais: Instalação, Inicialização da API e Execução no n8n. Siga **exatamente** esta ordem.

### Passo 1: Instalação das Dependências (Apenas na primeira vez)
Abra um terminal na raiz da pasta do projeto e instale as bibliotecas Python obrigatórias:
```bash
pip install flask pandas matplotlib seaborn
```

### Passo 2: Iniciar a API Local (A Ponte)
Ainda no terminal (ou no Prompt de Comando/PowerShell), rode o arquivo que servirá de servidor web para o n8n:
```bash
python api_projeto.py
```
> **Importante:** Mantenha este terminal **aberto**. Ele vai mostrar uma mensagem de que o Flask está rodando (`Running on http://127.0.0.1:5000`). É essa API que fará todo o trabalho de execução nos bastidores.

### Passo 3: Importar e Configurar o n8n
1. Abra o n8n no seu navegador (normalmente o endereço é `http://localhost:5678`).
2. Na página principal, clique em **Add Workflow** ou vá em **Workflows > Import from File**.
3. Selecione o arquivo `workflow/n8n_workflow.json` que está dentro da pasta do projeto.

### Passo 4: Adicionar a sua Chave do Gemini
1. Com o fluxo aberto na tela do n8n, encontre o nó chamado **"Análise Gemini"**.
2. Clique nele para abrir suas configurações.
3. Na aba **Parameters**, procure pelo campo **URL**.
4. No final da URL (`...generateContent?key=SUA_CHAVE_API_AQUI`), apague a parte "SUA_CHAVE_API_AQUI" e cole a sua chave verdadeira do Google.
5. Salve o fluxo (ícone de disquete ou botão Save).

### Passo 5: Executar o Fluxo 🚀
1. Clique no botão azul **"Execute Workflow"** (ou "Test Workflow").
2. O n8n fará chamadas pela rede local para o seu terminal, acionando os scripts Python. O Gemini analisará os resultados quase instantaneamente.
3. Ao finalizar o processo (quando todos os nós concluírem e o fluxo terminar), **vá até a pasta `resultados/`** no seu computador.
4. Você encontrará o relatório em formato `.csv` e as imagens de altíssima qualidade de toda a análise de desempenho do Hill Climbing.

---

## 🧩 O Funcionamento dos Nós do n8n (A Engenharia do Fluxo)

Caso precise replicar ou entender como o fluxo foi elaborado logicamente:

1. **Iniciar Experimento (`Manual Trigger`)**: Inicia todo o pipeline.
2. **Rodar Hill Climbing (`HTTP Request`)**:
   - Faz um `POST` para `http://127.0.0.1:5000/executar`.
   - **O que acontece nos bastidores:** A API Python roda o algoritmo 30 vezes, extrai os resultados e converte em CSV (salvando o arquivo fisicamente na pasta `resultados/`). Por fim, devolve os dados envelopados em formato JSON (`{"execucoes": [...]}`) para o n8n.
3. **Análise Gemini (`HTTP Request`)**: 
   - Recebe os dados, envelopa em um JSON de Prompt dinâmico, garantindo formatação pura (`{{ JSON.stringify(...) }}`), e bate diretamente na API oficial do Google. O Google age como analista e classifica/avalia as execuções (onde o algoritmo caiu em um Platô, se o sucesso foi rápido, etc).
4. **Parsear Métricas Gemini (`Code`)**:
   - Nó simples feito em JavaScript que "limpa" a resposta do Google Gemini, extraindo exclusivamente a seção JSON contendo a análise da IA para ser exibida nos dados de saída do n8n.
5. **Gerar Gráficos (`HTTP Request`)**:
   - Faz um `POST` para `http://127.0.0.1:5000/gerar-graficos`.
   - **O que acontece nos bastidores:** A API Python aciona o arquivo `analisar_resultados.py`. Esse arquivo consome o CSV gerado pelo Passo 2 e pinta quatro gráficos profissionais (`.png`) na pasta resultados. O n8n então finaliza seu trabalho com sucesso.

Nesta estrutura moderna, o n8n age puramente como Orquestrador, enquanto o Python atua como Serviço de Processamento (Worker). Isso traz performance total e nenhuma chance de bloqueio por conta do sistema operacional Windows.
