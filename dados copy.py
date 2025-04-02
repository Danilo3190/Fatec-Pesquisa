import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import nltk
from nltk.corpus import stopwords

# Baixa as stopwords
nltk.download('stopwords')

# Função para converter letras de colunas em índices
def coluna_para_indice(coluna):
    indice = 0
    for letra in coluna:
        indice = indice * 26 + (ord(letra.upper()) - ord('A') + 1)
    return indice - 1

# Carrega os dados
df = pd.read_excel("Question_Socio.xlsx", sheet_name="Sheet1")

# Lista de colunas a serem removidas
colunas_para_remover = [
    "A", "B", "C", "D", "F", "G", "H", "J", "K", "M", "N", "O", "P", "Q", "S", "T", "V", "W", "Y", "Z",
    "AB", "AC", "AE", "AF", "AH", "AI", "AK", "AL", "AN", "AO", "AQ", "AR", "AT", "AU", "AW", "AX", "AZ", "BA",
    "BB", "BC", "BE", "BF", "BH", "BI", "BK", "BL", "BN", "BO", "BQ", "BR", "BT", "BU", "BW", "BX", "BZ", "CA",
    "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CN", "CO", "CQ", "CR", "CT", "CU", "CW", "CX", "CZ", "DA",
    "DC", "DD", "DF", "DG", "DI", "DJ", "DL", "DM", "DO", "DP", "DR", "DS", "DU", "DV", "DW", "DX", "DZ", "EA",
    "EC", "ED", "EF", "EG", "EI", "EJ", "EK", "EL", "EN", "EO", "EQ", "ER", "ET", "EU", "EW", "EX", "EZ", "FA",
    "FC", "FD", "FE", "FF", "FH", "FI", "FK", "FL", "FN", "FO", "FQ", "FR", "FS", "FT", "FV", "FW", "FY", "FZ",
    "GB", "GC", "GE", "GF", "GH", "GI", "GK", "GL", "GM", "GN", "GP", "GQ", "GS", "GT", "GV", "GW", "GY", "GZ", 
    "HA", "HB", "HD", "HE", "HG", "HH", "HJ", "HK", "HM", "HN", "HP", "HQ", "HS", "HT", "HV", "HW", "HX", "HY", 
    "IA", "IB", "ID", "IE", "IG", "IH", "IJ", "IK", "IM", "IN", "IP", "IQ", "IR", "IS", "IU", "IV", "IX", "IY", 
    "JA", "JB", "JC", "JD", "JF", "JG", "JI", "JJ", "JL", "JM", "JO", "JP", "JR", "JS", "JU", "JV", "JX", "JY", 
    "KA", "KB", "KD", "KE", "KG", "KH", "KJ", "KK", "KM", "KN", "KP", "KQ", "KS", "KT", "KV", "KW", "KY", "KZ", 
    "LB", "LC", "LE", "LF", "LH", "LI", "LK", "LL"
]

# Remove colunas e linhas vazias
df = df.drop(df.columns[[coluna_para_indice(col) for col in colunas_para_remover]], axis=1)
df = df.dropna(how="all")

# Função para nuvem de palavras
def generate_wordcloud():
    if "Escreva algumas linhas sobre sua história e seus sonhos de vida" in df.columns:
        text = " ".join(df["Escreva algumas linhas sobre sua história e seus sonhos de vida"].dropna().astype(str))
        stopwords_pt = set(stopwords.words('portuguese'))
        custom_stopwords = {"meu", "ter", "busco", "quero", "minha", "que", "um", "uma", "também", "para", "onde", "em", "área", "vida", "anos", "sonho", "outros", "fazer", "possa","sempre","duas", "ano", "nisso"}
        stopwords_pt.update(custom_stopwords)
        
        wordcloud = WordCloud(
            width=800, height=400, background_color="white", max_words=100, colormap="viridis", stopwords=stopwords_pt
        ).generate(" ".join([word for word in text.split() if word.lower() not in stopwords_pt]))

        buffer = BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.savefig(buffer, format="png")
        plt.close()
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    return None

# Cria o app
app = Dash(__name__, assets_folder="assets")

# Layout
app.layout = html.Div([
    # Título
    html.H1("Dashboard Socioeconômico - FATEC Franca", className="dashboard-title"),
    
    # Nuvem de palavras 
    html.Div(id="wordcloud-container", className="wordcloud-container"),

    # Controles (dropdown + rádio)
    html.P("Escolha uma coluna para visualizar:", className="dashboard-description"),
    html.Div([
        dcc.Dropdown(
            id="dropdown-column",
            options=[{"label": col, "value": col} for col in df.columns],
            value=df.columns[0],
            clearable=False,
            className="dropdown"
        ),
        dcc.RadioItems(
            id="chart-type-selector",
            options=[
                {'label': 'Gráfico de Pizza', 'value': 'pie'},
                {'label': 'Gráfico de Barras', 'value': 'bar'}
            ],
            value='pie',  # Gráfico de pizza como padrão
            inline=True,
            className="radio-items"
        )
    ], className="controls-container"),

    # Gráfico (parte inferior)
    dcc.Graph(id="graph")
])

# Callbacks
@app.callback(
    Output("graph", "figure"),
    Input("dropdown-column", "value"),
    Input("chart-type-selector", "value")
)
def update_graph(selected_column, chart_type):
    if chart_type == 'pie':
        fig = px.pie(
            df, 
            names=selected_column, 
            title=f"Distribuição de {selected_column} (Pizza)",
            hole=0.3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
    else:
        fig = px.bar(
            df, 
            x=selected_column, 
            title=f"Distribuição de {selected_column} (Barras)", 
            text_auto=True
        )
    return fig

@app.callback(
    Output("wordcloud-container", "children"),
    Input("dropdown-column", "value")
)
def update_wordcloud(selected_column):
    if selected_column == "Escreva algumas linhas sobre sua história e seus sonhos de vida":
        image_base64 = generate_wordcloud()
        if image_base64:
            return [
                html.H2("Nuvem de Palavras - Sonhos e Histórias"),
                html.Img(src=f"data:image/png;base64,{image_base64}")
            ]
    return None


if __name__ == "__main__":
    app.run(debug=True)