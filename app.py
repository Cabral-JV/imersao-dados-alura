import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configurações da página ---
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados", page_icon="📊", layout="wide"
)

# --- Carregamento dos dados ---
df = pd.read_csv(
    "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
)

# --- Barra Lateral (filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df["ano"].unique())
ano_selecionado = st.sidebar.multiselect(
    "Ano", anos_disponiveis, default=anos_disponiveis
)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df["senioridade"].unique())
senioridade_selecionada = st.sidebar.multiselect(
    "Senioridade", senioridades_disponiveis, default=senioridades_disponiveis
)

# Filtro por Tipo de Contrato
tipos_contrato_disponiveis = sorted(df["contrato"].unique())
tipo_contrato_selecionado = st.sidebar.multiselect(
    "Contrato", tipos_contrato_disponiveis, default=tipos_contrato_disponiveis
)

# Filtro por Tamanho da Empresa
tamanhos_empresa_disponiveis = sorted(df["tamanho_empresa"].unique())
tamanho_empresa_selecionado = st.sidebar.multiselect(
    "Tamanho da Empresa",
    tamanhos_empresa_disponiveis,
    default=tamanhos_empresa_disponiveis,
)

# --- Filtragem do DataFrame ---
df_filtrado = df[
    (df["ano"].isin(ano_selecionado))
    & (df["senioridade"].isin(senioridade_selecionada))
    & (df["contrato"].isin(tipo_contrato_selecionado))
    & (df["tamanho_empresa"].isin(tamanho_empresa_selecionado))
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados ")
st.markdown(
    "Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros na barra lateral para personalizar a visualização."
)

# --- Métricas Principais (KPIs) ---
st.subheader("🎯 Métricas Principais (Salário Anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado["usd"].mean()
    salario_maximo = df_filtrado["usd"].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio = 0
    salario_maximo = 0
    total_registros = 0
    cargo_mais_frequente = ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Médio (USD)", f"${salario_medio:,.2f}")
col2.metric("Salário Máximo (USD)", f"${salario_maximo:,.2f}")
col3.metric("Total de Registros", total_registros)
col4.metric("Cargo Mais Frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análise Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = (
            df_filtrado.groupby("cargo")["usd"]
            .mean()
            .nlargest(10)
            .sort_values(ascending=True)
            .reset_index()
        )
        grafico_cargos = px.bar(
            top_cargos,
            x="usd",
            y="cargo",
            orientation="h",
            title="Top 10 Cargos por Salário Médio (USD)",
            labels={"usd": "Salário Médio (USD)", "cargo": "Cargo"},
        )
        grafico_cargos.update_layout(
            title_x=0.1, yaxis={"categoryorder": "total ascending"}
        )
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x="usd",
            nbins=30,
            title="Distribuição dos Salários Anuais (USD)",
            labels={"usd": "Faixa Salarial(USD)", "count": ""},
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)
with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado["remoto"].value_counts().reset_index()
        remoto_contagem.columns = ["tipo_trabalho", "quantidade"]
        grafico_remoto = px.pie(
            remoto_contagem,
            values="quantidade",
            names="tipo_trabalho",
            title="Proporção dos Tipos de Trabalho",
            hole=0.5,
        )
        grafico_remoto.update_traces(textposition="inside", textinfo="percent+label")
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning(
            "Nenhum dado disponível para exibir no gráfico de tipos de trabalho."
        )

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado["cargo"] == "Data Scientist"]
        media_ds_pais = df_ds.groupby("residencia_iso3")["usd"].mean().reset_index()
        grafico_pais = px.choropleth(
            media_ds_pais,
            locations="residencia_iso3",
            color="usd",
            color_continuous_scale="rdylgn",
            title="Salário Médio de Data Scientists por País",
            labels={"usd": "Salário Médio (USD)", "residencia_iso3": "País"},
        )
        st.plotly_chart(grafico_pais, use_container_width=True)
    else:
        st.warning(
            "Nenhum dado disponível para exibir no gráfico de salários por país."
        )

# --- Tabela de Dados Detalhados ---
st.subheader("Tabela de Dados Detalhados")
st.dataframe(df_filtrado)
