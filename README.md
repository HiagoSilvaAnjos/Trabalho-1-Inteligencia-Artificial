# 👑 Automação de IA: Hill Climbing (8-Rainhas) + n8n + Gemini

Este projeto implementa uma solução completa, robusta e automatizada para o problema das **8-Rainhas** utilizando o algoritmo **Hill Climbing**. Toda a orquestração do experimento, análise preditiva de dados e geração de relatórios visuais é feita de forma integrada através do **n8n**, da inteligência do **Google Gemini** e de uma **API Flask em Python**.

---

## 🏗️ A Arquitetura do Sistema (Abordagem API Local)

Para contornar limitações de permissões do n8n em ambientes Desktop/Docker (como o erro de acesso ao sistema de arquivos `Module 'fs' is disallowed`), o sistema foi arquitetado em um formato elegante de **Microsserviços**.

O n8n atua *exclusivamente* como o **Cérebro Orquestrador**, enquanto uma API Python atua como o **Motor de Processamento**, possuindo acesso total ao sistema de arquivos da máquina.

### O Pipeline de Dados:
1. **Execução:** O n8n ordena que a API rode o Hill Climbing 30 vezes. A API gera os dados, salva o histórico bruto (`.csv`) no disco e devolve um JSON encapsulado.
2. **Análise IA:** O n8n pega esse JSON e envia diretamente para a API do Google Gemini. O Gemini analisa os tempos de execução, iterações e taxas de sucesso, extraindo as 5 melhores soluções e criando uma categorização textual detalhada.
3. **Persistência de Métricas:** O n8n devolve a resposta crua do Gemini para a nossa API Python, que limpa o texto, converte para JSON estruturado e salva fisicamente (`metricas_gemini.json`).
4. **Relatórios Visuais:** O n8n aciona a API mais uma vez para consolidar os resultados em quatro gráficos avançados (`.png`) e duas tabelas estatísticas (`.png`).

---

## 📂 Estrutura de Pastas

```text
Trabalho-1-Inteligencia-Artificial/
│
├── api_projeto.py          # (Motor Principal) Servidor Flask com rotas de execução e persistência
├── TUTORIAL_EXECUCAO.md    # Guia rápido de execução alternativa
├── README.md               # Este arquivo de documentação geral
│
├── codigo/                 # Scripts Lógicos
│   ├── hill_climbing.py         # Algoritmo Hill Climbing (Resolve o tabuleiro)
│   └── analisar_resultados.py   # Motor de geração de Tabelas e Gráficos (Matplotlib/Seaborn)
│
├── resultados/             # Diretório de Saída (Gerado dinamicamente)
│   ├── execucoes.csv                # Histórico de cada uma das 30 execuções
│   ├── metricas_gemini.json         # Análise estruturada do Google Gemini
│   ├── grafico1_sucesso_falha.png   # Gráfico de barras da taxa de sucesso
│   ├── grafico2_iteracoes_linha.png # Evolução das iterações
│   ├── grafico3_histograma_tempo.png# Distribuição do tempo em milissegundos
│   ├── grafico4_boxplot_iteracoes.png# Boxplot da consistência do algoritmo
│   ├── tabela1_resumo.png           # Resumo limpo com médias e desvios
│   └── tabela2_melhores_solucoes.png# Top 5 soluções distintas (Rankeadas por conflitos)
│
└── workflow/               # Arquivos de exportação
    └── n8n_workflow.json        # Fluxo do n8n (Atenção: verifique se é a versão atualizada)
```

---

## 🛠️ Pré-requisitos do Sistema

1. **Python 3.8+** instalado.
2. **n8n** instalado (Pode ser App Desktop, Docker ou pacote `npx n8n`).
3. **Chave de API do Google Gemini** (Gratuita no Google AI Studio).

---

## 🚀 Como Rodar o Projeto (Passo a Passo Definitivo)

Siga estas instruções cronologicamente para garantir 100% de sucesso na execução do pipeline.

### Passo 1: Instalação das Bibliotecas
Abra um terminal na raiz do projeto e instale todas as dependências exigidas pelo Python:
```bash
pip install flask pandas matplotlib seaborn
```

### Passo 2: Ligar a API (O Motor de Processamento)
No mesmo terminal, inicie o servidor da nossa ponte Python:
```bash
python api_projeto.py
```
> **Atenção:** Mantenha este terminal aberto! Ele escutará as requisições na porta `5000` (ex: `http://127.0.0.1:5000`). Sem isso, o n8n não conseguirá processar nada.

### Passo 3: Importação no n8n
1. Abra o painel do seu n8n no navegador (`http://localhost:5678`).
2. Clique em **Add Workflow** > **Import from File**.
3. Selecione o arquivo `n8n_workflow.json` que está na pasta `workflow/`.

### Passo 4: Autenticação da IA
1. No fluxo importado, clique no nó **"Análise Gemini"**.
2. Na aba de parâmetros, procure o campo **URL**.
3. No final do endereço URL, encontre o texto `SUA_CHAVE_API_AQUI` e substitua-o pela sua API Key do Google (ex: `...?key=AIzaSy...`).
4. Salve o fluxo.

### Passo 5: Ignição! 🚀
1. No canto da tela, clique em **Execute Workflow** (ou Test Workflow).
2. O sistema passará por 4 etapas automáticas:
   - Acionará a rota `/executar`.
   - Conversará com o Google Gemini.
   - Acionará a rota `/salvar-metricas`.
   - Acionará a rota `/gerar-graficos`.
3. Quando todos os nós exibirem sinal verde de conclusão, **abra a pasta `resultados/`** no seu computador. Lá estará o dossiê completo da análise do Hill Climbing!

---

## 🧩 O Comportamento dos Nós (Por Trás das Cortinas)

Se você desejar auditar ou modificar a engenharia dos dados, eis como a informação transita:

1. **Iniciar Experimento (`Manual Trigger`)**: Botão de largada manual do usuário.
2. **Rodar Hill Climbing (`HTTP Request`)**:
   - Dispara um `POST` para `http://127.0.0.1:5000/executar`.
   - A API chama o script `hill_climbing.py` e executa-o 30 vezes. Transforma os resultados em um DataFrame do Pandas, salva em `resultados/execucoes.csv` e devolve um array limpo chamado `$json.execucoes` para a plataforma do n8n.
3. **Análise Gemini (`HTTP Request`)**: 
   - Dispara um `POST` para a API do Google `generativelanguage.googleapis.com`.
   - Pega as 30 execuções do passo anterior e injeta em um corpo `JSON` perfeito. O Gemini avalia métricas pesadas (médias, desvios padrões, platôs e reinícios), seleciona o **Top 5 Melhores Soluções** e categoriza detalhadamente cada execução individual.
4. **Salvar Métricas Gemini (`HTTP Request`)**:
   - Dispara um `POST` para `http://127.0.0.1:5000/salvar-metricas`.
   - Envia a resposta bruta do Gemini (que contém vários cabeçalhos e tokens) para a nossa API. O Python filtra o miolo principal da resposta da IA, certifica-se de que é um JSON válido e salva na pasta `resultados/metricas_gemini.json`.
5. **Gerar Gráficos (`HTTP Request`)**:
   - Dispara um `POST` para `http://127.0.0.1:5000/gerar-graficos`.
   - A API invoca silenciosamente o script `analisar_resultados.py`. Esse arquivo não precisa receber dados do n8n: ele lê autonomamente o `execucoes.csv`, plota quatro gráficos coloridos via Matplotlib e, como toque final, renderiza e salva **duas tabelas estatísticas em imagem PNG** na pasta.

Com isso, nenhuma etapa do fluxo no n8n depende mais do "File System" do Windows. Toda leitura e escrita em disco é responsabilidade puramente da linguagem Python!
