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

# ── Tema visual ──────────────────────────────────────────────────────────────
plt.style.use("dark_background")
PALETTE = {
    "sucesso":  "#00C896",
    "falha":    "#FF4C6A",
    "linha":    "#7B9EFF",
    "hist":     "#A78BFA",
    "box":      "#FFB347",
    "grid":     "#2A2A3A",
    "bg":       "#12121E",
    "text":     "#E8E8F0",
}

def apply_base_style(ax, title, xlabel, ylabel):
    ax.set_facecolor(PALETTE["bg"])
    ax.set_title(title, color=PALETTE["text"], fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, color=PALETTE["text"], fontsize=11)
    ax.set_ylabel(ylabel, color=PALETTE["text"], fontsize=11)
    ax.tick_params(colors=PALETTE["text"])
    ax.spines["bottom"].set_color(PALETTE["grid"])
    ax.spines["left"].set_color(PALETTE["grid"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, color=PALETTE["grid"], linestyle="--", alpha=0.5)

# ── Leitura do CSV ───────────────────────────────────────────────────────────
df = pd.read_csv(CSV_PATH)

# Normaliza nomes de colunas com caracteres especiais
rename_map = {}
for col in df.columns:
    clean = col.strip()
    rename_map[col] = clean
df.rename(columns=rename_map, inplace=True)

# Garante tipos corretos
iter_col   = [c for c in df.columns if "iter" in c.lower()][0]
tempo_col  = [c for c in df.columns if "tempo" in c.lower()][0]
sucesso_col= [c for c in df.columns if "sucesso" in c.lower()][0]
h_col      = [c for c in df.columns if "h_final" in c.lower()][0]
reinicio_col=[c for c in df.columns if "reini" in c.lower()][0]
plato_col  = [c for c in df.columns if "plat" in c.lower()][0]
id_col     = [c for c in df.columns if "id_exec" in c.lower()][0]

df[iter_col]  = pd.to_numeric(df[iter_col],  errors="coerce").fillna(0).astype(int)
df[tempo_col] = pd.to_numeric(df[tempo_col], errors="coerce").fillna(0.0)
df[h_col]     = pd.to_numeric(df[h_col],     errors="coerce").fillna(0)
df[reinicio_col] = pd.to_numeric(df[reinicio_col], errors="coerce").fillna(0)

# Booleanos podem vir como string "True"/"False"
for col in [sucesso_col, plato_col]:
    if df[col].dtype == object:
        df[col] = df[col].map({"True": True, "False": False, True: True, False: False})

# ── Métricas ─────────────────────────────────────────────────────────────────
n            = len(df)
sucessos     = df[sucesso_col].sum()
falhas       = n - sucessos

metricas = {
    # Obrigatórias
    "media_iteracoes":          round(df[iter_col].mean(), 4),
    "desvio_padrao_iteracoes":  round(df[iter_col].std(),  4),
    "media_tempo_ms":           round(df[tempo_col].mean(), 4),
    "desvio_padrao_tempo_ms":   round(df[tempo_col].std(),  4),
    "taxa_sucesso_pct":         round(sucessos / n * 100, 2),
    "taxa_falha_pct":           round(falhas   / n * 100, 2),
    "media_h_final":            round(df[h_col].mean(), 4),
    # Extras
    "max_iteracoes":            int(df[iter_col].max()),
    "min_iteracoes":            int(df[iter_col].min()),
    "total_execucoes":          n,
    "media_reinicios":          round(df[reinicio_col].mean(), 4),
    "quantidade_platos":        int(df[plato_col].sum()),
}

# Imprimir JSON das métricas (n8n pode capturar)
print(json.dumps(metricas, ensure_ascii=False, indent=2))

# ── Gráfico 1: Barras – Sucesso vs Falha ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
fig.patch.set_facecolor(PALETTE["bg"])
categorias = ["Sucesso", "Falha"]
valores    = [int(sucessos), int(falhas)]
cores      = [PALETTE["sucesso"], PALETTE["falha"]]
bars = ax.bar(categorias, valores, color=cores, width=0.5, zorder=3)
for bar, val in zip(bars, valores):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            str(val), ha="center", va="bottom", color=PALETTE["text"], fontweight="bold", fontsize=13)
apply_base_style(ax, "Sucesso vs Falha (30 Execuções)", "Resultado", "Quantidade")
ax.set_ylim(0, max(valores) + 4)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "grafico1_sucesso_falha.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()
print("[OK] grafico1_sucesso_falha.png salvo.")

# ── Gráfico 2: Linha – Iterações por Execução ─────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 5))
fig.patch.set_facecolor(PALETTE["bg"])
ids   = df[id_col].tolist()
iters = df[iter_col].tolist()
ax.plot(ids, iters, color=PALETTE["linha"], linewidth=2, marker="o", markersize=5, zorder=3)
ax.axhline(metricas["media_iteracoes"], color=PALETTE["sucesso"], linestyle="--",
           linewidth=1.5, label=f'Média: {metricas["media_iteracoes"]:.1f}')
ax.legend(facecolor=PALETTE["bg"], edgecolor=PALETTE["grid"], labelcolor=PALETTE["text"])
apply_base_style(ax, "Iterações por Execução", "ID da Execução", "Iterações")
ax.set_xticks(ids)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "grafico2_iteracoes_linha.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()
print("[OK] grafico2_iteracoes_linha.png salvo.")

# ── Gráfico 3: Histograma – Distribuição do Tempo ────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor(PALETTE["bg"])
ax.hist(df[tempo_col], bins=10, color=PALETTE["hist"], edgecolor=PALETTE["bg"], linewidth=0.8, zorder=3)
ax.axvline(metricas["media_tempo_ms"], color=PALETTE["sucesso"], linestyle="--",
           linewidth=2, label=f'Média: {metricas["media_tempo_ms"]:.2f} ms')
ax.legend(facecolor=PALETTE["bg"], edgecolor=PALETTE["grid"], labelcolor=PALETTE["text"])
apply_base_style(ax, "Distribuição do Tempo de Execução", "Tempo (ms)", "Frequência")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "grafico3_histograma_tempo.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()
print("[OK] grafico3_histograma_tempo.png salvo.")

# ── Gráfico 4: Boxplot – Iterações ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 6))
fig.patch.set_facecolor(PALETTE["bg"])
bp = ax.boxplot(df[iter_col], patch_artist=True, notch=False,
                medianprops=dict(color=PALETTE["sucesso"], linewidth=2.5),
                boxprops=dict(facecolor=PALETTE["box"], color=PALETTE["box"], alpha=0.7),
                whiskerprops=dict(color=PALETTE["text"]),
                capprops=dict(color=PALETTE["text"]),
                flierprops=dict(marker="o", markerfacecolor=PALETTE["falha"],
                                markersize=7, linestyle="none"))
apply_base_style(ax, "Boxplot das Iterações", "Hill Climbing", "Iterações")
ax.set_xticklabels(["30 Execuções"])
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "grafico4_boxplot_iteracoes.png"), dpi=150, facecolor=PALETTE["bg"])
plt.close()
print("[OK] grafico4_boxplot_iteracoes.png salvo.")

# ── Tabela 1: Resumo das Métricas ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4))
fig.patch.set_facecolor(PALETTE["bg"])
ax.axis('tight')
ax.axis('off')

tabela1_dados = [
    ["Métrica", "Valor"],
    ["Taxa de Sucesso", f'{metricas["taxa_sucesso_pct"]}%'],
    ["Taxa de Falha", f'{metricas["taxa_falha_pct"]}%'],
    ["Média de Iterações", f'{metricas["media_iteracoes"]} ± {metricas["desvio_padrao_iteracoes"]}'],
    ["Tempo Médio (ms)", f'{metricas["media_tempo_ms"]} ± {metricas["desvio_padrao_tempo_ms"]}'],
    ["Média H Final", f'{metricas["media_h_final"]}'],
    ["Reinícios Médios", f'{metricas["media_reinicios"]}'],
    ["Total de Platôs", f'{metricas["quantidade_platos"]}']
]

table1 = ax.table(cellText=tabela1_dados, colLabels=None, cellLoc='center', loc='center')
table1.auto_set_font_size(False)
table1.set_fontsize(12)
table1.scale(1, 2)

for (row, col), cell in table1.get_celld().items():
    cell.set_edgecolor(PALETTE["grid"])
    if row == 0:
        cell.set_text_props(weight='bold', color=PALETTE["bg"])
        cell.set_facecolor(PALETTE["text"])
    else:
        cell.set_text_props(color=PALETTE["text"])
        cell.set_facecolor(PALETTE["bg"])

plt.title("Resumo das Métricas", color=PALETTE["text"], fontsize=14, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "tabela1_resumo.png"), dpi=150, facecolor=PALETTE["bg"], bbox_inches='tight')
plt.close()
print("[OK] tabela1_resumo.png salvo.")

# ── Tabela 2: 5 Melhores Soluções Distintas ──────────────────────────────────
estado_col_list = [c for c in df.columns if "estado_final" in c.lower()]
estado_col_name = estado_col_list[0] if estado_col_list else "estado_final"

if estado_col_name in df.columns:
    melhores_df = df.sort_values(by=h_col).drop_duplicates(subset=[estado_col_name]).head(5)
    
    fig, ax = plt.subplots(figsize=(10, 3))
    fig.patch.set_facecolor(PALETTE["bg"])
    ax.axis('tight')
    ax.axis('off')
    
    tabela2_dados = [["Rank", "ID Exec", "Conflitos (h)", "Estado Final (Solução)"]]
    for idx, (_, row) in enumerate(melhores_df.iterrows(), 1):
        tabela2_dados.append([
            f"#{idx}",
            str(row[id_col]),
            str(row[h_col]),
            str(row[estado_col_name])
        ])
    
    table2 = ax.table(cellText=tabela2_dados, colLabels=None, cellLoc='center', loc='center')
    table2.auto_set_font_size(False)
    table2.set_fontsize(11)
    table2.scale(1, 2)
    
    for (row, col), cell in table2.get_celld().items():
        cell.set_edgecolor(PALETTE["grid"])
        if row == 0:
            cell.set_text_props(weight='bold', color=PALETTE["bg"])
            cell.set_facecolor(PALETTE["sucesso"])
        else:
            cell.set_text_props(color=PALETTE["text"])
            cell.set_facecolor(PALETTE["bg"])
    
    plt.title("Top 5 Melhores Soluções Distintas", color=PALETTE["text"], fontsize=14, fontweight="bold", pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "tabela2_melhores_solucoes.png"), dpi=150, facecolor=PALETTE["bg"], bbox_inches='tight')
    plt.close()
    print("[OK] tabela2_melhores_solucoes.png salvo.")

print("\n[CONCLUÍDO] Todos os gráficos e tabelas foram salvos em:", OUT_DIR)
