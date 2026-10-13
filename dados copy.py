import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

def coluna_para_indice(coluna):
    indice = 0
    for letra in coluna:
        indice = indice * 26 + (ord(letra.upper()) - ord('A') + 1)
    return indice - 1

df = pd.read_excel("Question_Socio.xlsx", sheet_name="Sheet1")

colunas_para_remover = [
    "A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "M", "N", "O", "P", "Q", "S", "T", "V", "W", "Y", "Z",
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

df = df.drop(df.columns[[coluna_para_indice(col) for col in colunas_para_remover]], axis=1)
df = df.dropna(how="all")

def generate_wordcloud(selected_column):
    if selected_column in df.columns:
        text = " ".join(df[selected_column].dropna().astype(str))
        stopwords_pt = set(stopwords.words('portuguese'))
        custom_stopwords = {
            "meu", "minha", "quero", "que", "para", "ser", "uma", "um", "ter", 
            "fazer", "vida", "curso", "anos", "depois", "porque", "área", "também"
        }
        stopwords_pt.update(custom_stopwords)

        wordcloud = WordCloud(
            width=800, height=400, 
            background_color="#1e2130",
            max_words=100, 
            colormap="viridis", 
            stopwords=stopwords_pt
        ).generate(text)

        buffer = BytesIO()
        plt.figure(figsize=(10, 5), facecolor="#1e2130")
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.savefig(buffer, format="png", facecolor="#1e2130")
        plt.close()
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    return None

COLUNAS_NUVEM = [
    "Escreva algumas linhas sobre sua história e seus sonhos de vida",
    "Qual sua maior expectativa quanto ao curso?",
    "Qual sua expectativa após se formar?",
    "Por que você escolheu este curso?"
]

app = Dash(__name__, assets_folder="assets")

app.layout = html.Div([
    html.Div([
        html.H1("Dashboard Socioeconômico - FATEC Franca", className="titulo"),

        html.Div([
            html.P("Escolha uma coluna para visualizar:", className="subtitulo"),
            dcc.Dropdown(
                id="dropdown-column",
                options=[{"label": col, "value": col} for col in df.columns],
                value=df.columns[0],
                clearable=False,
                className="dropdown"
            ),
            html.Div(
                dcc.RadioItems(
                    id="chart-type-selector",
                    options=[
                        {'label': ' Gráfico de Pizza', 'value': 'pie'},
                        {'label': ' Gráfico de Barras', 'value': 'bar'}
                    ],
                    value='pie',
                    inline=True,
                    inputStyle={"marginRight": "5px"},
                    labelStyle={"marginRight": "15px", "display": "inline-flex", "alignItems": "center"},
                    className="radio-items"
                ),
                className="radio-container"
            )
        ], className="controle-container"),

        html.Div(id="wordcloud-container", className="nuvem-container"),

        dcc.Graph(id="graph", className="grafico")

    ], className="container")
], className="fundo")

@app.callback(
    Output("graph", "figure"),
    Input("dropdown-column", "value"),
    Input("chart-type-selector", "value")
)
def update_graph(selected_column, chart_type):
    template = "plotly_dark"

    if selected_column == "Qual sua idade":
        try:
            df_idade = df.copy()
            df_idade[selected_column] = pd.to_numeric(df_idade[selected_column], errors='coerce')
            df_idade = df_idade.dropna(subset=[selected_column])
            fig = px.histogram(
                df_idade,
                x=selected_column,
                nbins=10,
                title="Distribuição de Idade",
                template=template
            )
            fig.update_layout(
                plot_bgcolor="#2a2f4f",
                paper_bgcolor="#2a2f4f",
                font_color="#ffffff"
            )
            return fig
        except Exception as e:
            print(f"Erro ao gerar histograma: {e}")

    if chart_type == 'pie':
        fig = px.pie(
            df,
            names=selected_column,
            title=f"Distribuição de {selected_column}",
            hole=0.3,
            template=template
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            marker=dict(line=dict(color='#1e2130', width=1))
        )
    else:
        fig = px.bar(
            df,
            x=selected_column,
            title=f"Distribuição de {selected_column}",
            text_auto=True,
            template=template
        )
        fig.update_layout(
            plot_bgcolor="#2a2f4f",
            paper_bgcolor="#2a2f4f",
            font_color="#ffffff"
        )
    return fig

@app.callback(
    Output("wordcloud-container", "children"),
    Input("dropdown-column", "value")
)
def update_wordcloud(selected_column):
    if selected_column in COLUNAS_NUVEM:
        image_base64 = generate_wordcloud(selected_column)
        if image_base64:
            return [
                html.H2(f"Nuvem de Palavras - {selected_column}", className="titulo"),
                html.Img(src=f"data:image/png;base64,{image_base64}", className="imagem-nuvem")
            ]
    return None

if __name__ == "__main__":
    app.run(debug=False)
