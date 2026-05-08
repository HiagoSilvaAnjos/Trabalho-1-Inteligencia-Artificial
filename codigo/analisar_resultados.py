import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json
import sys
import os

# ── Caminhos ────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "resultados", "execucoes.csv")
OUT_DIR  = os.path.join(BASE_DIR, "resultados")

os.makedirs(OUT_DIR, exist_ok=True)

# ── Tema visual (Fundo Branco) ────────────────────────────────────────────────
plt.style.use("default")
PALETTE = {
    "sucesso":  "#2ca02c",  # Verde
    "falha":    "#d62728",  # Vermelho
    "linha":    "#1f77b4",  # Azul
    "hist":     "#9467bd",  # Roxo
    "box":      "#ff7f0e",  # Laranja
    "grid":     "#e0e0e0",  # Cinza claro
    "bg":       "#ffffff",  # Branco
    "text":     "#333333",  # Cinza escuro/Preto
}

def apply_base_style(ax, title, xlabel, ylabel):
    ax.set_facecolor(PALETTE["bg"])
    ax.set_title(title, color=PALETTE["text"], fontsize=14, fontweight="bold", pad=12)
    if xlabel: ax.set_xlabel(xlabel, color=PALETTE["text"], fontsize=11)
    if ylabel: ax.set_ylabel(ylabel, color=PALETTE["text"], fontsize=11)
    ax.tick_params(colors=PALETTE["text"])
    ax.spines["bottom"].set_color(PALETTE["text"])
    ax.spines["left"].set_color(PALETTE["text"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, color=PALETTE["grid"], linestyle="--", alpha=0.7)

# ── Leitura do CSV ───────────────────────────────────────────────────────────
if not os.path.exists(CSV_PATH):
    print(f"Arquivo CSV não encontrado em {CSV_PATH}. Execute o algoritmo primeiro.")
    sys.exit(1)

df = pd.read_csv(CSV_PATH)

# Normaliza nomes de colunas
rename_map = {col: col.strip() for col in df.columns}
df.rename(columns=rename_map, inplace=True)

# Identifica colunas
iter_col   = [c for c in df.columns if "iter" in c.lower()][0]
tempo_col  = [c for c in df.columns if "tempo" in c.lower()][0]
sucesso_col= [c for c in df.columns if "sucesso" in c.lower()][0]
h_col      = [c for c in df.columns if "h_final" in c.lower()][0]
reinicio_col=[c for c in df.columns if "reini" in c.lower()][0]
plato_col  = [c for c in df.columns if "plat" in c.lower()][0]
id_col     = [c for c in df.columns if "id_exec" in c.lower()][0]
estado_col = [c for c in df.columns if "estado_final" in c.lower()][0]

otimo_list = [c for c in df.columns if "timo" in c.lower() or "otimo" in c.lower()]
otimo_col  = otimo_list[0] if otimo_list else None

# Ajuste de Tipos
df[iter_col]  = pd.to_numeric(df[iter_col],  errors="coerce").fillna(0).astype(int)
df[tempo_col] = pd.to_numeric(df[tempo_col], errors="coerce").fillna(0.0)
df[h_col]     = pd.to_numeric(df[h_col],     errors="coerce").fillna(0).astype(int)
df[reinicio_col] = pd.to_numeric(df[reinicio_col], errors="coerce").fillna(0).astype(int)

# Booleanos
bool_cols = [sucesso_col, plato_col]
if otimo_col: bool_cols.append(otimo_col)

for col in bool_cols:
    if df[col].dtype == object:
        df[col] = df[col].map({"True": True, "False": False, "true": True, "false": False, True: True, False: False})
        
# ── Métricas Gerais ──────────────────────────────────────────────────────────
n            = len(df)
sucessos     = df[sucesso_col].sum()
falhas       = n - sucessos

metricas = {
    "media_iteracoes":          round(df[iter_col].mean(), 4),
    "desvio_padrao_iteracoes":  round(df[iter_col].std(),  4),
    "media_tempo_ms":           round(df[tempo_col].mean(), 4),
    "desvio_padrao_tempo_ms":   round(df[tempo_col].std(),  4),
    "taxa_sucesso_pct":         round(sucessos / n * 100, 2) if n > 0 else 0,
    "taxa_falha_pct":           round(falhas   / n * 100, 2) if n > 0 else 0,
    "media_h_final":            round(df[h_col].mean(), 4),
    "max_iteracoes":            int(df[iter_col].max()),
    "min_iteracoes":            int(df[iter_col].min()),
    "total_execucoes":          n,
    "media_reinicios":          round(df[reinicio_col].mean(), 4),
    "quantidade_platos":        int(df[plato_col].sum()),
}

print(json.dumps(metricas, ensure_ascii=False, indent=2))

# =============================================================================
# NOVOS GRÁFICOS
# =============================================================================

# ── 1. Dispersão: Iterações vs. Tempo (ms) ──────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
fig.patch.set_facecolor(PALETTE["bg"])
colors = df[sucesso_col].map({True: PALETTE["sucesso"], False: PALETTE["falha"]})
ax.scatter(df[iter_col], df[tempo_col], c=colors, alpha=0.7, s=80, edgecolors='w', zorder=3)
apply_base_style(ax, "Dispersão: Iterações vs. Tempo", "Iterações", "Tempo (ms)")
patch_sucesso = mpatches.Patch(color=PALETTE["sucesso"], label='Sucesso')
patch_falha = mpatches.Patch(color=PALETTE["falha"], label='Falha')
ax.legend(handles=[patch_sucesso, patch_falha], loc='upper left', frameon=True, facecolor=PALETTE["bg"])
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "novo_grafico_dispersao.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()
print("[OK] novo_grafico_dispersao.png salvo.")

# ── 2. Pizza: Condições de Parada ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 7))
fig.patch.set_facecolor(PALETTE["bg"])

qtd_sucesso = int(sucessos)
qtd_plato = int(df[(df[sucesso_col] == False) & (df[plato_col] == True)].shape[0])
qtd_otimo = int(df[(df[sucesso_col] == False) & (df[otimo_col] == True)].shape[0]) if otimo_col else 0
qtd_outros = int(df[(df[sucesso_col] == False) & (df[plato_col] == False) & (df.get(otimo_col, False) == False)].shape[0])

labels, sizes, colors_pie = [], [], []

if qtd_sucesso > 0:
    labels.append(f"Sucesso ({qtd_sucesso})"); sizes.append(qtd_sucesso); colors_pie.append(PALETTE["sucesso"])
if qtd_otimo > 0:
    labels.append(f"Ótimo Local ({qtd_otimo})"); sizes.append(qtd_otimo); colors_pie.append("#ff9896")
if qtd_plato > 0:
    labels.append(f"Platô ({qtd_plato})"); sizes.append(qtd_plato); colors_pie.append("#ffbb78")
if qtd_outros > 0:
    labels.append(f"Limite Iterações ({qtd_outros})"); sizes.append(qtd_outros); colors_pie.append(PALETTE["falha"])

if sizes:
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', 
                                      startangle=140, textprops={'color': PALETTE["text"], 'fontsize': 11})
    plt.setp(autotexts, size=10, weight="bold", color="white")
    ax.set_title("Distribuição de Condições de Parada", color=PALETTE["text"], fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "novo_grafico_pizza_parada.png"), dpi=150, facecolor=PALETTE["bg"])
else:
    print("[Aviso] Sem dados para Gráfico de Pizza.")
plt.close()
print("[OK] novo_grafico_pizza_parada.png salvo.")

# ── 3. Barras: Frequência de Reinícios ──────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor(PALETTE["bg"])
restarts_counts = df[reinicio_col].value_counts().sort_index()
ax.bar(restarts_counts.index, restarts_counts.values, color=PALETTE["linha"], zorder=3, edgecolor='black')
apply_base_style(ax, "Frequência de Reinícios (Random Restarts)", "Quantidade de Reinícios", "Número de Execuções")
ax.set_xticks(restarts_counts.index)
for i, v in zip(restarts_counts.index, restarts_counts.values):
    ax.text(i, v + 0.1, str(v), ha='center', va='bottom', color=PALETTE["text"], fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "novo_grafico_barras_reinicios.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()
print("[OK] novo_grafico_barras_reinicios.png salvo.")

# ── 4. Mapa de Calor: Ocupação do Tabuleiro ─────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 6))
fig.patch.set_facecolor(PALETTE["bg"])
heatmap_data = np.zeros((8, 8))
sucesso_df = df[df[sucesso_col] == True]

for _, row in sucesso_df.iterrows():
    try:
        estado_str = row[estado_col].replace("'", '"')
        estado = json.loads(estado_str) if isinstance(estado_str, str) else estado_str
        for col_idx, lin_idx in enumerate(estado):
            if 0 <= lin_idx < 8 and 0 <= col_idx < 8:
                heatmap_data[lin_idx, col_idx] += 1
    except Exception:
        pass

im = ax.imshow(heatmap_data, cmap="Blues", origin="upper", aspect="auto")
cbar = ax.figure.colorbar(im, ax=ax)
cbar.ax.set_ylabel("Frequência", rotation=-90, va="bottom", color=PALETTE["text"])
cbar.ax.tick_params(colors=PALETTE["text"])
ax.set_xticks(np.arange(8)); ax.set_yticks(np.arange(8))
ax.set_xticklabels([f"C{i}" for i in range(8)], color=PALETTE["text"])
ax.set_yticklabels([f"L{i}" for i in range(8)], color=PALETTE["text"])
ax.set_title("Mapa de Calor: Ocupação do Tabuleiro (Apenas Sucessos)", color=PALETTE["text"], fontsize=14, fontweight="bold", pad=12)

for i in range(8):
    for j in range(8):
        val = int(heatmap_data[i, j])
        text_color = "white" if val > heatmap_data.max() / 2 else "black"
        ax.text(j, i, val, ha="center", va="center", color=text_color, fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "novo_grafico_heatmap_ocupacao.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()
print("[OK] novo_grafico_heatmap_ocupacao.png salvo.")

# =============================================================================
# NOVAS TABELAS
# =============================================================================

def render_table(fig_name, title, data, header_colors):
    fig, ax = plt.subplots(figsize=(10, max(2, len(data)*0.5)))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.axis('tight'); ax.axis('off')
    
    table = ax.table(cellText=data, colLabels=None, cellLoc='center', loc='center')
    table.auto_set_font_size(False); table.set_fontsize(11); table.scale(1, 2)
    
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("black")
        if row == 0:
            cell.set_text_props(weight='bold', color="white")
            cell.set_facecolor(header_colors[col % len(header_colors)])
        else:
            cell.set_text_props(color=PALETTE["text"])
            cell.set_facecolor("white")
            
    plt.title(title, color=PALETTE["text"], fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, fig_name), dpi=150, facecolor=PALETTE["bg"], bbox_inches='tight')
    plt.close()

# ── 1. Top 5 Soluções Mais Eficientes
top5_df = df[df[sucesso_col] == True].sort_values(by=[iter_col, tempo_col]).head(5)
tabela1_dados = [["Rank", "ID Exec", "Tempo (ms)", "Iterações", "Reinícios"]]
for idx, (_, row) in enumerate(top5_df.iterrows(), 1):
    tabela1_dados.append([f"#{idx}", str(row[id_col]), f"{row[tempo_col]:.2f}", str(row[iter_col]), str(row[reinicio_col])])
if len(tabela1_dados) > 1:
    render_table("nova_tabela_top5_eficientes.png", "Top 5 Soluções Mais Eficientes", tabela1_dados, [PALETTE["linha"]]*5)
    print("[OK] nova_tabela_top5_eficientes.png salvo.")

# ── 2. Piores Gafes Computacionais
piores_df = df[df[sucesso_col] == False].sort_values(by=[h_col, tempo_col], ascending=[False, False]).head(5)
tabela2_dados = [["Rank", "ID Exec", "Conflitos (h_final)", "Motivo da Falha", "Tempo Desp. (ms)"]]
for idx, (_, row) in enumerate(piores_df.iterrows(), 1):
    if row[plato_col]: motivo = "Preso em Platô"
    elif otimo_col and row[otimo_col]: motivo = "Ótimo Local"
    else: motivo = "Limite de Iterações"
    tabela2_dados.append([f"#{idx}", str(row[id_col]), str(row[h_col]), motivo, f"{row[tempo_col]:.2f}"])
if len(tabela2_dados) > 1:
    render_table("nova_tabela_piores_gafes.png", "Piores Gafes Computacionais (Anomalias)", tabela2_dados, [PALETTE["falha"]]*5)
    print("[OK] nova_tabela_piores_gafes.png salvo.")

# ── 3. Resumo Categórico
sucesso_rapido = df[(df[sucesso_col] == True) & (df[iter_col] < metricas["media_iteracoes"])]
sucesso_lento = df[(df[sucesso_col] == True) & (df[iter_col] >= metricas["media_iteracoes"])]
falha_otimo = df[(df[sucesso_col] == False) & (df[otimo_col] == True)] if otimo_col else pd.DataFrame()
falha_plato = df[(df[sucesso_col] == False) & (df[plato_col] == True)]

tabela3_dados = [["Categoria", "Quantidade", "Tempo Médio (ms)"]]
calc_mean = lambda sub_df: f"{sub_df[tempo_col].mean():.2f}" if not sub_df.empty else "0.00"

tabela3_dados.append(["Sucesso Rápido", str(len(sucesso_rapido)), calc_mean(sucesso_rapido)])
tabela3_dados.append(["Sucesso Lento", str(len(sucesso_lento)), calc_mean(sucesso_lento)])
tabela3_dados.append(["Falha por Ótimo Local", str(len(falha_otimo)), calc_mean(falha_otimo)])
tabela3_dados.append(["Falha por Platô", str(len(falha_plato)), calc_mean(falha_plato)])
render_table("nova_tabela_resumo_categorico.png", "Resumo Categórico", tabela3_dados, [PALETTE["hist"]]*3)
print("[OK] nova_tabela_resumo_categorico.png salvo.")

# =============================================================================
# GRÁFICOS ORIGINAIS (Atualizados p/ Fundo Branco)
# =============================================================================
fig, ax = plt.subplots(figsize=(7, 5))
fig.patch.set_facecolor(PALETTE["bg"])
bars = ax.bar(["Sucesso", "Falha"], [int(sucessos), int(falhas)], color=[PALETTE["sucesso"], PALETTE["falha"]], width=0.5, zorder=3)
for bar, val in zip(bars, [int(sucessos), int(falhas)]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, str(val), ha="center", va="bottom", color=PALETTE["text"], fontweight="bold", fontsize=13)
apply_base_style(ax, "Sucesso vs Falha", "Resultado", "Quantidade")
ax.set_ylim(0, max([int(sucessos), int(falhas)]) + 4)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "grafico1_sucesso_falha.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()

fig, ax = plt.subplots(figsize=(11, 5))
fig.patch.set_facecolor(PALETTE["bg"])
ax.plot(df[id_col].tolist(), df[iter_col].tolist(), color=PALETTE["linha"], linewidth=2, marker="o", markersize=5, zorder=3)
ax.axhline(metricas["media_iteracoes"], color=PALETTE["sucesso"], linestyle="--", linewidth=1.5, label=f'Média: {metricas["media_iteracoes"]:.1f}')
ax.legend(facecolor=PALETTE["bg"], edgecolor=PALETTE["text"], labelcolor=PALETTE["text"])
apply_base_style(ax, "Iterações por Execução", "ID da Execução", "Iterações")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "grafico2_iteracoes_linha.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()

fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor(PALETTE["bg"])
ax.hist(df[tempo_col], bins=10, color=PALETTE["hist"], edgecolor="black", linewidth=0.8, zorder=3)
ax.axvline(metricas["media_tempo_ms"], color=PALETTE["falha"], linestyle="--", linewidth=2, label=f'Média: {metricas["media_tempo_ms"]:.2f} ms')
ax.legend(facecolor=PALETTE["bg"], edgecolor=PALETTE["text"], labelcolor=PALETTE["text"])
apply_base_style(ax, "Distribuição do Tempo de Execução", "Tempo (ms)", "Frequência")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "grafico3_histograma_tempo.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()

fig, ax = plt.subplots(figsize=(6, 6))
fig.patch.set_facecolor(PALETTE["bg"])
ax.boxplot(df[iter_col], patch_artist=True, medianprops=dict(color=PALETTE["text"], linewidth=2.5),
           boxprops=dict(facecolor=PALETTE["box"], color="black", alpha=0.7),
           whiskerprops=dict(color="black"), capprops=dict(color="black"),
           flierprops=dict(marker="o", markerfacecolor=PALETTE["falha"], markersize=7, linestyle="none"))
apply_base_style(ax, "Boxplot das Iterações", "Hill Climbing", "Iterações")
ax.set_xticklabels(["Execuções"])
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "grafico4_boxplot_iteracoes.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()

print("\n[CONCLUÍDO] Todos os gráficos e tabelas originais foram salvos com fundo branco em:", OUT_DIR)
