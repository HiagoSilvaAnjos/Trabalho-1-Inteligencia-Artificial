# Trabalho Prático - Inteligência Artificial: Problema das 8-Rainhas com Hill Climbing

Este repositório contém a implementação do algoritmo **Hill Climbing (Subida de Encosta)** aplicado ao Problema das N-Rainhas (com N=8), além da estrutura e instruções necessárias para a orquestração via **n8n** e a análise posterior de dados quantitativos.

---

## 📁 Estrutura do Projeto

```text
Trabalho-1-Inteligencia-Artificial/
│── codigo/
│   ├── hill_climbing.py          # Algoritmo principal (Hill Climbing + Random Restart)
│   └── analisar_resultados.py    # Script de métricas e geração dos 4 gráficos
│
│── workflow/
│   └── n8n_workflow.json         # Workflow completo importável no n8n
│
│── resultados/                   # Pasta gerada automaticamente pelo pipeline
│   ├── execucoes.csv             # Dados brutos das 30 execuções
│   ├── metricas_gemini.json      # Análise de métricas gerada pelo Gemini
│   ├── gerar_graficos.py         # Script Python gerado dinamicamente pelo n8n
│   ├── grafico1_sucesso_falha.png
│   ├── grafico2_iteracoes_linha.png
│   ├── grafico3_histograma_tempo.png
│   └── grafico4_boxplot_iteracoes.png
│
│── relatorio/
│   └── relatorio_final.pdf       # Versão final do trabalho escrito
│
└── README.md
```

---

## 🚀 GUIA COMPLETO DE EXECUÇÃO — PASSO A PASSO

### PRÉ-REQUISITOS

Antes de começar, garanta que você tem instalado:

| Ferramenta | Verificação |
|---|---|
| **Python 3.8+** | `python --version` |
| **pip** | `pip --version` |
| **n8n** (via Node.js) | `n8n --version` |
| **Bibliotecas Python** | `pip install matplotlib pandas` |

---

### PASSO 1 — Testar o Script Python Localmente

Abra o **Prompt de Comando** ou **PowerShell** na pasta do projeto e execute:

```bash
python codigo/hill_climbing.py --num_execucoes 30 --max_iter 200 --variante restart
```

✅ **Resultado esperado:** Um JSON com 30 objetos contendo as chaves:
`id_execucao`, `estado_inicial`, `iterações`, `tempo_ms`, `estado_final`, `h_final`, `sucesso`, `reinicios`, `platô`, `ótimo_local`

Se funcionar, o Python está pronto para o n8n.

---

### PASSO 2 — Obter a Chave de API do Gemini

1. Acesse [Google AI Studio](https://aistudio.google.com/apikey)
2. Clique em **"Create API Key"**
3. Copie a chave gerada — ela será usada no Passo 5

---

### PASSO 3 — Iniciar o n8n

Abra o **Prompt de Comando** e execute:

```bash
n8n start
```

Aguarde aparecer a mensagem:
```
n8n ready on 0.0.0.0, port 5678
```

Em seguida, acesse no navegador: **http://localhost:5678**

> **Como parar o n8n:** Volte ao Prompt de Comando onde o n8n está rodando e pressione **`Ctrl + C`**. Aguarde a mensagem de encerramento. O n8n para completamente e libera a porta 5678.
>
> Se o terminal já foi fechado e o n8n continua rodando em segundo plano, pare pelo **Gerenciador de Tarefas** (atalho `Ctrl + Shift + Esc`) → aba **Processos** → localize **Node.js** → clique com botão direito → **Finalizar Tarefa**. Ou via PowerShell:
> ```powershell
> # Encontrar e encerrar o processo Node.js do n8n
> Get-Process -Name "node" | Stop-Process -Force
> ```

---

### PASSO 4 — Importar o Workflow no n8n

1. No n8n, clique em **"Workflows"** no menu lateral esquerdo
2. Clique no botão **"Add workflow"** (canto superior direito)
3. Clique nos **3 pontinhos** `⋮` no canto superior direito da tela
4. Selecione **"Import from file"**
5. Navegue até a pasta do projeto e selecione:
   ```
   workflow/n8n_workflow.json
   ```
6. O workflow será importado com os **9 nós já conectados**

---

### PASSO 5 — Configurar a Chave API do Gemini

Após importar o workflow:

1. Clique no nó **"Análise Gemini"** (5º nó laranja da sequência)
2. Na aba **Parameters**, localize o campo **URL**
3. Encontre o trecho `SUA_CHAVE_API_AQUI` e substitua pela sua chave real:

```
Antes: ...generateContent?key=SUA_CHAVE_API_AQUI
Depois: ...generateContent?key=AIzaSy_SUA_CHAVE_REAL_AQUI
```

4. Clique em **"Save"** (ícone de disquete no topo)

---

### PASSO 6 — Executar o Workflow

1. No topo da tela do workflow, clique em **"Execute Workflow"** (botão ▶️)
2. Aguarde a execução. Você verá os nós acendendo em verde um a um
3. Tempo estimado: **30–90 segundos** (dependendo da velocidade da API Gemini)

**O que acontece em cada nó:**

| Nó | Ação |
|---|---|
| 🟢 Iniciar Experimento | Dispara o pipeline manualmente |
| ⚙️ Rodar Hill Climbing | Executa `hill_climbing.py` com 30 execuções |
| 📦 Parsear JSON do Python | Converte a saída do terminal em 30 objetos n8n |
| 💾 Salvar CSV | Grava `resultados/execucoes.csv` em disco |
| 🤖 Análise Gemini | Envia os dados para o Gemini e recebe métricas + categorização |
| 📊 Parsear Métricas Gemini | Extrai o JSON e salva `metricas_gemini.json` |
| 🐍 Gerar Script de Gráficos | Cria o arquivo `gerar_graficos.py` dinamicamente com dados embutidos |
| ▶️ Gerar Gráficos | Executa o script → gera os 4 arquivos `.png` |
| ✅ Resultado Final | Exibe lista de todos os arquivos gerados |

---

### PASSO 7 — Verificar os Resultados

Após a execução, abra a pasta `resultados/` do projeto. Você deve encontrar:

```
resultados/
├── execucoes.csv                   ✅ Dados brutos das 30 execuções
├── metricas_gemini.json            ✅ Análise completa do Gemini
├── gerar_graficos.py               ✅ Script gerado automaticamente
├── grafico1_sucesso_falha.png      ✅ Barras: Sucesso vs Falha
├── grafico2_iteracoes_linha.png    ✅ Linha: Iterações por execução
├── grafico3_histograma_tempo.png   ✅ Histograma: distribuição do tempo
└── grafico4_boxplot_iteracoes.png  ✅ Boxplot: dispersão das iterações
```

---

### PASSO 8 — (Opcional) Rodar a Análise Standalone

Se quiser gerar os gráficos sem o n8n (precisa do `execucoes.csv` já gerado):

```bash
python codigo/analisar_resultados.py
```

Este script lê o CSV, calcula todas as métricas e salva os 4 gráficos diretamente.

---

## 🔧 SOLUÇÃO DE PROBLEMAS

| Problema | Causa | Solução |
|---|---|---|
| `python: command not found` | Python não está no PATH | Reinstale o Python e marque "Add to PATH" |
| `ModuleNotFoundError: matplotlib` | Biblioteca não instalada | `pip install matplotlib pandas` |
| Nó "Rodar Hill Climbing" falha | Caminho incorreto | Verifique se o projeto está em `C:/Users/Hialagol/Documents/Meus-Projetos/Trabalho-1-Inteligencia-Artificial` |
| Erro 400 no nó Gemini | Chave API inválida | Gere uma nova chave em [AI Studio](https://aistudio.google.com/apikey) |
| Erro 404 no nó Gemini | Nome do modelo errado | O modelo configurado é `gemini-3-flash-preview` |
| CSV vazio ou incorreto | JSON malformado do Python | Rode o script manualmente no terminal e verifique a saída |

---

## 📊 MÉTRICAS CALCULADAS

### Obrigatórias
| Métrica | Descrição |
|---|---|
| Média iterações | Média do número de iterações nas 30 execuções |
| Desvio padrão iterações | Dispersão em torno da média de iterações |
| Média tempo (ms) | Tempo médio de execução em milissegundos |
| Desvio padrão tempo | Dispersão em torno do tempo médio |
| Taxa de sucesso (%) | % de execuções que encontraram h=0 |
| Taxa de falha (%) | % de execuções que não convergiram |
| Valor médio h final | Média dos conflitos restantes ao fim |

### Extras
| Métrica | Descrição |
|---|---|
| Máximo iterações | Maior número de iterações em uma execução |
| Mínimo iterações | Menor número de iterações em uma execução |
| Total execuções | Número total de execuções (30) |
| Média de reinícios | Média de Random Restarts por execução |
| Quantidade de platôs | Total de execuções que travaram em platô |

---

## 🧠 SOBRE O ALGORITMO

- **Representação**: Array `[c0..c7]` onde índice = coluna e valor = linha (0–7)
- **Função Objetivo h**: Conta pares de rainhas em conflito (linha ou diagonal). Meta: `h = 0`
- **Vizinhança**: Steepest Ascent — explora todos os 56 vizinhos possíveis por iteração
- **Variante usada**: Random Restart — ao travar em platô (10 mov. laterais) ou ótimo local, reinicia aleatoriamente (até 20 reinícios por execução)

---

## 🔗 TECNOLOGIAS UTILIZADAS

| Tecnologia | Uso |
|---|---|
| Python 3 | Algoritmo Hill Climbing + geração de gráficos |
| n8n (Node.js) | Orquestração do pipeline completo |
| Google Gemini `gemini-3-flash-preview` | Análise de métricas e categorização das execuções |
| Matplotlib + Pandas | Visualização dos dados e manipulação do CSV |
