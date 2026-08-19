# -*- coding: utf-8 -*-
"""
=============================================================================
FATEC Pesquisa - Plataforma Analítica & Portal do Aluno
Faculdade de Tecnologia de Franca (Dr. Thomaz Novelino)
Visualização Direta, Sem Gráficos de Pizza, Focada em Leitura Rápida e Simples
=============================================================================
"""

import sys
import os
import re
import base64
import sqlite3
import hashlib
from io import BytesIO, StringIO
from datetime import datetime
import collections

# Configuração de encoding seguro para console Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, State, callback_context, dash_table, ALL
import plotly.express as px
import plotly.graph_objects as go

# =============================================================================
# CURSOS OFICIAIS DA FATEC FRANCA
# =============================================================================
CURSOS_FATEC_FRANCA = [
    {
        "id": "ADS",
        "nome": "Análise e Desenvolvimento de Sistemas",
        "sigla": "ADS",
        "modalidade": "Presencial",
        "periodo": "Tarde e Noite",
        "duracao": "3 anos (6 semestres)",
        "icone": "💻",
        "tag": "Tecnologia da Informação",
        "cor": "#0284c7",
        "descricao": "Projeta, documenta, especifica, testa, implanta e mantém sistemas computacionais e softwares corporativos."
    },
    {
        "id": "DSM",
        "nome": "Desenvolvimento de Software Multiplataforma",
        "sigla": "DSM",
        "modalidade": "Presencial",
        "periodo": "Noite",
        "duracao": "3 anos (6 semestres)",
        "icone": "📱",
        "tag": "Web / Mobile / Cloud / IA",
        "cor": "#7c3aed",
        "descricao": "Desenvolve soluções multiplataforma para web, nuvem, dispositivos móveis e IoT com IA integrada."
    },
    {
        "id": "GPI",
        "nome": "Gestão da Produção Industrial",
        "sigla": "GPI",
        "modalidade": "Presencial",
        "periodo": "Noite",
        "duracao": "3 anos (6 semestres)",
        "icone": "⚙️",
        "tag": "Engenharia & Processos",
        "cor": "#059669",
        "descricao": "Planeja, supervisiona e otimiza processos de manufatura, logística, custos industriais e controle de qualidade."
    },
    {
        "id": "GRH",
        "nome": "Gestão de Recursos Humanos",
        "sigla": "GRH",
        "modalidade": "Presencial",
        "periodo": "Manhã e Noite",
        "duracao": "3 anos (6 semestres)",
        "icone": "🤝",
        "tag": "Pessoas & Estratégia",
        "cor": "#d97706",
        "descricao": "Atua no planejamento e desenvolvimento de pessoas, recrutamento, treinamento, remuneração e clima corporativo."
    },
    {
        "id": "GE",
        "nome": "Gestão Empresarial",
        "sigla": "GE",
        "modalidade": "EaD (Educação a Distância)",
        "periodo": "Ambiente Virtual / Flexível",
        "duracao": "3 anos (6 semestres)",
        "icone": "📊",
        "tag": "Negócios & Gestão Global",
        "cor": "#e11d48",
        "descricao": "Formação holística em gestão corporativa, finanças, marketing, planejamento estratégico e empreendedorismo."
    }
]

OPCOES_CURSOS_COMPLETAS = [
    {"label": "💻 Análise e Desenvolvimento de Sistemas (ADS)", "value": "Análise e Desenvolvimento de Sistemas (ADS)"},
    {"label": "📱 Desenvolvimento de Software Multiplataforma (DSM)", "value": "Desenvolvimento de Software Multiplataforma (DSM)"},
    {"label": "⚙️ Gestão da Produção Industrial (GPI)", "value": "Gestão da Produção Industrial (GPI)"},
    {"label": "🤝 Gestão de Recursos Humanos (GRH)", "value": "Gestão de Recursos Humanos (GRH)"},
    {"label": "📊 Gestão Empresarial (GE - EaD)", "value": "Gestão Empresarial (GE)"}
]

# =============================================================================
# CATÁLOGO VISUAL DE PERGUNTAS CLICÁVEIS POR CATEGORIA (SEM PIZZA)
# =============================================================================
CATALOGO_PERGUNTAS = [
    {
        "categoria": "👤 Perfil & Dados Pessoais",
        "cor": "#0284c7",
        "itens": [
            {"id": "q_periodo", "titulo": "Turno / Período", "icone": "🕒", "termos": ["período que cursa", "periodo", "turno"], "tipo": "bar-h"},
            {"id": "q_cidade", "titulo": "Cidade Onde Reside", "icone": "📍", "termos": ["cidade você reside", "cidade"], "tipo": "bar-h"},
            {"id": "q_genero", "titulo": "Gênero dos Alunos", "icone": "👫", "termos": ["gênero", "genero"], "tipo": "bar-h"},
            {"id": "q_faixa", "titulo": "Faixa Etária / Idade", "icone": "🎂", "termos": ["faixa etária", "faixa etaria"], "tipo": "bar-h"},
            {"id": "q_escola", "titulo": "Histórico Escolar (Ensino Médio)", "icone": "🏫", "termos": ["vida escolar", "estudou"], "tipo": "bar-h"},
            {"id": "q_civil", "titulo": "Estado Civil", "icone": "💍", "termos": ["estado civil"], "tipo": "bar-h"},
            {"id": "q_filhos", "titulo": "Quantidade de Filhos", "icone": "👶", "termos": ["filhos você tem", "filhos"], "tipo": "bar-h"},
        ]
    },
    {
        "categoria": "🏠 Renda & Condição Familiar",
        "cor": "#7c3aed",
        "itens": [
            {"id": "q_renda", "titulo": "Faixa de Renda Familiar", "icone": "💵", "termos": ["faixa de renda", "renda mensal"], "tipo": "bar-h"},
            {"id": "q_domicilio", "titulo": "Situação do Domicílio", "icone": "🏠", "termos": ["situação do domicílio", "situacao"], "tipo": "bar-h"},
            {"id": "q_mora_com", "titulo": "Com Quem o Aluno Mora", "icone": "👥", "termos": ["com quem você mora", "com quem"], "tipo": "bar-h"},
            {"id": "q_moradores", "titulo": "Pessoas na Residência", "icone": "👨‍👩‍👧‍👦", "termos": ["quantas pessoas", "moram no seu domicílio"], "tipo": "bar-h"},
            {"id": "q_esc_mae", "titulo": "Escolaridade da Mãe", "icone": "👩‍🎓", "termos": ["escolaridade da sua mãe", "mãe"], "tipo": "bar-h"},
            {"id": "q_esc_pai", "titulo": "Escolaridade do Pai", "icone": "👨‍🎓", "termos": ["escolaridade do seu pai", "pai"], "tipo": "bar-h"},
        ]
    },
    {
        "categoria": "💼 Mercado de Trabalho & Carreira",
        "cor": "#059669",
        "itens": [
            {"id": "q_trabalha", "titulo": "Trabalha Atualmente?", "icone": "💼", "termos": ["você trabalha?", "trabalha?"], "tipo": "bar-h"},
            {"id": "q_vinculo", "titulo": "Tipo de Vínculo (CLT/Estágio)", "icone": "📝", "termos": ["vínculo com o emprego", "vinculo"], "tipo": "bar-h"},
            {"id": "q_area_trab", "titulo": "Trabalha na Área do Curso?", "icone": "🎯", "termos": ["área do seu trabalho", "área"], "tipo": "bar-h"},
            {"id": "q_regime", "titulo": "Regime de Trabalho", "icone": "⏰", "termos": ["regime de trabalho"], "tipo": "bar-h"},
            {"id": "q_saude", "titulo": "Possui Plano de Saúde?", "icone": "🏥", "termos": ["plano de saúde", "saude"], "tipo": "bar-h"},
        ]
    },
    {
        "categoria": "💻 Acesso à Tecnologia & Bens",
        "cor": "#d97706",
        "itens": [
            {"id": "q_bens_geral", "titulo": "Painel Geral de Equipamentos", "icone": "📊", "termos": ["bens_geral"], "tipo": "bens_geral"},
            {"id": "q_internet", "titulo": "Internet em Casa", "icone": "🌐", "termos": ["internet"], "tipo": "bar-h"},
            {"id": "q_smartphone", "titulo": "Smartphone / Celular", "icone": "📱", "termos": ["celular e(ou) smartphone", "smartphone"], "tipo": "bar-h"},
            {"id": "q_notebook", "titulo": "Possui Notebook", "icone": "💻", "termos": ["notebook"], "tipo": "bar-h"},
            {"id": "q_desktop", "titulo": "Computador Desktop", "icone": "🖥️", "termos": ["microcomputador", "desktop"], "tipo": "bar-h"},
            {"id": "q_automovel", "titulo": "Possui Automóvel", "icone": "🚗", "termos": ["automóvel", "automovel"], "tipo": "bar-h"},
            {"id": "q_motocicleta", "titulo": "Possui Motocicleta", "icone": "🏍️", "termos": ["motocicleta"], "tipo": "bar-h"},
            {"id": "q_streaming", "titulo": "Streaming / TV por Assinatura", "icone": "📺", "termos": ["streaming", "tv por assinatura"], "tipo": "bar-h"},
        ]
    },
    {
        "categoria": "🎯 Finalidades de Uso da Tecnologia",
        "cor": "#0891b2",
        "itens": [
            {"id": "q_fin_escolar", "titulo": "Para Trabalhos Escolares", "icone": "📚", "termos": ["para trabalhos escolares"], "tipo": "bar-h"},
            {"id": "q_fin_prof", "titulo": "Para Trabalhos Profissionais", "icone": "💼", "termos": ["para trabalhos profissionais"], "tipo": "bar-h"},
            {"id": "q_fin_entret", "titulo": "Para Entretenimento & Redes", "icone": "🎮", "termos": ["para entretenimento"], "tipo": "bar-h"},
            {"id": "q_fin_banco", "titulo": "Para Operações Bancárias", "icone": "🏦", "termos": ["para operações bancárias", "operações bancárias"], "tipo": "bar-h"},
        ]
    },
    {
        "categoria": "☁️ Expectativas, Motivações & Sonhos",
        "cor": "#e11d48",
        "itens": [
            {"id": "q_nuvem_sonhos", "titulo": "Nuvem de Sonhos de Vida", "icone": "☁️", "termos": ["história e seus sonhos", "sonhos"], "tipo": "wordcloud"},
            {"id": "q_exp_curso", "titulo": "Maior Expectativa Quanto ao Curso", "icone": "🎓", "termos": ["expectativa quanto ao curso"], "tipo": "wordcloud"},
            {"id": "q_exp_formar", "titulo": "Expectativa Pós-Formatura", "icone": "🚀", "termos": ["expectativa após se formar"], "tipo": "wordcloud"},
            {"id": "q_motivo", "titulo": "Por Que Escolheu a FATEC Franca?", "icone": "💡", "termos": ["escolheu este curso"], "tipo": "wordcloud"},
        ]
    },
    {
        "categoria": "📋 Tabela de Respostas do Curso",
        "cor": "#4f46e5",
        "itens": [
            {"id": "q_tabela_geral", "titulo": "Tabela de Respostas & Exportação", "icone": "📋", "termos": ["tabela"], "tipo": "tabela"}
        ]
    }
]

# =============================================================================
# BANCO DE DADOS LOCAL (SQLITE)
# =============================================================================
DB_FILE = os.path.join(os.path.dirname(__file__), "fatec_pesquisa.db")

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_banco_dados():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS respostas_pesquisa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ra TEXT UNIQUE NOT NULL,
        cpf TEXT UNIQUE NOT NULL,
        nome TEXT NOT NULL,
        senha_hash TEXT,
        data_envio TEXT NOT NULL,
        curso TEXT,
        periodo TEXT,
        cidade_reside TEXT,
        genero TEXT,
        data_nascimento TEXT,
        estado_civil TEXT,
        filhos TEXT,
        mora_com TEXT,
        moradores TEXT,
        situacao_domicilio TEXT,
        renda_familiar TEXT,
        trabalha TEXT,
        vinculo_trabalho TEXT,
        regime_trabalho TEXT,
        area_trabalho TEXT,
        plano_saude TEXT,
        escolaridade_mae TEXT,
        escolaridade_pai TEXT,
        vida_escolar TEXT,
        internet TEXT,
        smartphone TEXT,
        notebook TEXT,
        desktop TEXT,
        streaming TEXT,
        automovel TEXT,
        motocicleta TEXT,
        finalidade_escolar TEXT,
        finalidade_profissional TEXT,
        finalidade_entretenimento TEXT,
        finalidade_banco TEXT,
        expectativa_curso TEXT,
        expectativa_formar TEXT,
        motivo_escolha TEXT,
        historia_sonhos TEXT
    )
    """)
    conn.commit()
    conn.close()

inicializar_banco_dados()

# =============================================================================
# BIBLIOTECAS DE PROCESSAMENTO DE TEXTO
# =============================================================================
HAVE_WORDCLOUD = False
HAVE_NLTK = False

try:
    from wordcloud import WordCloud
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAVE_WORDCLOUD = True
except Exception:
    pass

try:
    import nltk
    from nltk.corpus import stopwords
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    STOPWORDS_PT = set(stopwords.words('portuguese'))
    HAVE_NLTK = True
except Exception:
    STOPWORDS_PT = {
        'de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não',
        'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi',
        'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua', 'ou', 'ser', 'quando', 'muito',
        'nos', 'já', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre',
        'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'quem', 'nas', 'me',
        'esse', 'eles', 'estão', 'você', 'tinha', 'foram', 'essa', 'num', 'nem', 'suas',
        'meu', 'às', 'minha', 'têm', 'numa', 'pelos', 'elas', 'havia', 'seja', 'qual'
    }

CUSTOM_STOPWORDS = {
    "meu", "minha", "quero", "que", "para", "ser", "uma", "um", "ter", "fazer", 
    "vida", "curso", "anos", "depois", "porque", "área", "também", "fatec", "assim",
    "poder", "sempre", "sobre", "onde", "estou", "estudo", "apenas", "pois", "conseguir",
    "hoje", "ainda", "dia", "cada", "tudo", "mim", "além", "bem", "pouco", "bom", "forma",
    "trabalho", "formar", "expectativa", "maior", "escolhi", "sonhos", "historia", "história",
    "área", "area", "mercado", "futuro", "melhor", "aprender", "conhecimento", "grande"
}
STOPWORDS_PT.update(CUSTOM_STOPWORDS)

# =============================================================================
# CONSTANTES DE DESIGN & TEMAS CLAROS
# =============================================================================
THEME_TEMPLATE = "plotly_white"
COLOR_SEQUENCE = [
    "#0284c7", "#7c3aed", "#059669", "#d97706", "#e11d48",
    "#2563eb", "#06b6d4", "#f97316", "#14b8a6", "#6366f1"
]

LAYOUT_DEFAULTS = dict(
    template=THEME_TEMPLATE,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, -apple-system, sans-serif", color="#1e293b", size=13),
    margin=dict(l=20, r=25, t=35, b=25),
    hoverlabel=dict(bgcolor="#0f172a", font_size=13, font_family="Inter, sans-serif", font_color="#ffffff", bordercolor="#0284c7")
)

COLUNAS_QUALITATIVAS = [
    "Escreva algumas linhas sobre sua história e seus sonhos de vida",
    "Qual sua maior expectativa quanto ao curso?",
    "Qual sua expectativa após se formar?",
    "Por que você escolheu este curso?"
]

# =============================================================================
# HIGIENIZAÇÃO E PROCESSAMENTO DOS DADOS
# =============================================================================
def calcular_idade_e_faixa(val):
    if pd.isna(val) or val == "":
        return None, "Não informado"
    
    hoje = datetime.now()
    idade = None

    if isinstance(val, (int, float)) and not isinstance(val, bool):
        if 10 <= val <= 100:
            idade = int(val)
    elif isinstance(val, str) and val.strip().isdigit():
        num = int(val.strip())
        if 10 <= num <= 100:
            idade = num
    
    if idade is None:
        try:
            if isinstance(val, (pd.Timestamp, datetime)):
                nasc = val
            else:
                s = str(val).strip()
                try:
                    nasc = pd.to_datetime(s, format="%d/%m/%Y", errors="coerce")
                except:
                    nasc = pd.to_datetime(s, errors="coerce")
            
            if pd.notna(nasc):
                idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
        except Exception:
            idade = None

    if idade is None or idade < 10 or idade > 100:
        return None, "Não informado"
    
    if idade < 18:
        faixa = "Menor de 18 anos"
    elif 18 <= idade <= 24:
        faixa = "18 a 24 anos"
    elif 25 <= idade <= 29:
        faixa = "25 a 29 anos"
    elif 30 <= idade <= 39:
        faixa = "30 a 39 anos"
    elif 40 <= idade <= 49:
        faixa = "40 a 49 anos"
    else:
        faixa = "50+ anos"
        
    return idade, faixa

def limpar_nome_coluna(col):
    col = str(col).strip()
    col = re.sub(r'[\*\#]', '', col)
    col = re.sub(r'\s+', ' ', col)
    return col.strip()

def processar_dataframe(df_raw):
    df = df_raw.copy()
    df.columns = [limpar_nome_coluna(c) for c in df.columns]
    
    colunas_sistema = [
        "id", "hora de início", "hora de inicio", "hora de conclusão", "hora de conclusao",
        "email", "nome", "total de pontos", "comentários do teste", "comentarios do teste",
        "hora da última modificação", "hora da ultima modificacao", "informe o número do seu ra:",
        "informe o numero do seu ra:", "ra", "cpf", "senha_hash", "data_envio"
    ]
    
    colunas_manter = []
    for col in df.columns:
        col_lower = col.lower()
        if any(col_lower.startswith(pref) for pref in ["pontos -", "comentários -", "comentarios -"]):
            continue
        if col_lower in colunas_sistema:
            continue
        colunas_manter.append(col)
        
    df = df[colunas_manter]
    df = df.dropna(how="all")
    
    coluna_nasc = None
    for c in df.columns:
        if "nascimento" in c.lower() or c.lower() == "qual sua idade":
            coluna_nasc = c
            break
            
    if coluna_nasc:
        idades_e_faixas = df[coluna_nasc].apply(calcular_idade_e_faixa)
        df["Idade"] = [item[0] for item in idades_e_faixas]
        df["Faixa Etária"] = [item[1] for item in idades_e_faixas]
    else:
        df["Idade"] = np.nan
        df["Faixa Etária"] = "Não informado"
        
    return df

def carregar_dados_consolidados():
    df_excel = pd.DataFrame()
    caminhos = [
        "Question_Socio.xlsx",
        os.path.join(os.path.dirname(__file__), "Question_Socio.xlsx"),
        os.path.join(os.path.dirname(__file__), "..", "Question_Socio.xlsx"),
    ]
    for p in caminhos:
        if os.path.exists(p):
            try:
                df_excel = processar_dataframe(pd.read_excel(p))
                break
            except Exception:
                pass
                
    try:
        conn = get_db()
        df_db = pd.read_sql_query("SELECT * FROM respostas_pesquisa", conn)
        conn.close()
        
        if not df_db.empty:
            mapeamento_banco = {
                "curso": "Qual o seu curso?",
                "periodo": "Qual o período que cursa?",
                "cidade_reside": "Em qual cidade você reside?",
                "genero": "Qual é o seu gênero?",
                "data_nascimento": "Qual a sua data de nascimento?",
                "estado_civil": "Qual é o seu estado civil?",
                "filhos": "Quantos filhos você tem?",
                "mora_com": "Com quem você mora atualmente?",
                "moradores": "Quantas pessoas, incluindo você, moram no seu domicílio?",
                "situacao_domicilio": "Qual é a situação do domicílio em que você reside?",
                "renda_familiar": "Qual é a faixa de renda mensal da sua família?",
                "trabalha": "Você trabalha?",
                "vinculo_trabalho": "Qual é seu vínculo com o emprego?",
                "regime_trabalho": "Qual é o seu regime de trabalho?",
                "area_trabalho": "Qual a área do seu trabalho?",
                "plano_saude": "Você tem plano de saúde privado?",
                "escolaridade_mae": "Qual é o grau de escolaridade da sua mãe?",
                "escolaridade_pai": "Qual é o grau de escolaridade do seu pai?",
                "vida_escolar": "Na sua vida escolar, você estudou....",
                "internet": "Internet",
                "smartphone": "Celular e(ou) Smartphone",
                "notebook": "Notebook",
                "desktop": "Microcomputador de mesa/Desktop",
                "streaming": "TV por assinatura e(ou) Serviços de Streaming",
                "automovel": "Automóvel",
                "motocicleta": "Motocicleta",
                "finalidade_escolar": "Para trabalhos escolares",
                "finalidade_profissional": "Para trabalhos profissionais",
                "finalidade_entretenimento": "Para entretenimento (música, redes sociais,...)",
                "finalidade_banco": "Para operações bancárias",
                "expectativa_curso": "Qual sua maior expectativa quanto ao curso?",
                "expectativa_formar": "Qual sua expectativa após se formar?",
                "motivo_escolha": "Por que você escolheu este curso?",
                "historia_sonhos": "Escreva algumas linhas sobre sua história e seus sonhos de vida"
            }
            df_db = df_db.rename(columns=mapeamento_banco)
            df_db = processar_dataframe(df_db)
            
            if not df_excel.empty:
                df_final = pd.concat([df_excel, df_db], ignore_index=True)
            else:
                df_final = df_db
            return df_final
    except Exception as e:
        print(f"Erro lendo banco: {e}")
        
    return df_excel if not df_excel.empty else pd.DataFrame()

DF_GLOBAL_INICIAL = carregar_dados_consolidados()

# =============================================================================
# INICIALIZAÇÃO DO APP DASH
# =============================================================================
app = Dash(
    __name__,
    assets_folder="assets",
    title="FATEC Pesquisa | Inteligência Acadêmica & Portal do Aluno",
    suppress_callback_exceptions=True
)
server = app.server

# =============================================================================
# ANÁLISE QUALITATIVA & NUVEM DE PALAVRAS
# =============================================================================
def extrair_top_palavras(series, n=12):
    if series.dropna().empty:
        return []
    texto = " ".join(series.dropna().astype(str).str.lower())
    palavras = re.findall(r'\b[a-záàâãéèêíïóôõöúçñ]{3,}\b', texto)
    palavras_filtradas = [p for p in palavras if p not in STOPWORDS_PT]
    contagem = collections.Counter(palavras_filtradas)
    return contagem.most_common(n)

def gerar_imagem_nuvem(series):
    if not HAVE_WORDCLOUD or series.dropna().empty:
        return None
    try:
        texto = " ".join(series.dropna().astype(str))
        wc = WordCloud(
            width=850,
            height=380,
            background_color="#ffffff",
            colormap="tab10",
            max_words=100,
            stopwords=STOPWORDS_PT,
            collocations=False
        ).generate(texto)
        
        buf = BytesIO()
        plt.figure(figsize=(9, 4.0), facecolor="#ffffff")
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout(pad=0)
        plt.savefig(buf, format="png", facecolor="#ffffff", bbox_inches='tight', dpi=120)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        return None

# =============================================================================
# LAYOUT PRINCIPAL
# =============================================================================
app.layout = html.Div([
    dcc.Store(
        id='dataset-store', 
        data=DF_GLOBAL_INICIAL.to_json(date_format='iso', orient='split') if not DF_GLOBAL_INICIAL.empty else None
    ),
    dcc.Store(id='active-course-store', data="ADS"),
    dcc.Store(id='active-question-id-store', data="q_periodo"),
    dcc.Download(id="download-dataframe-csv"),
    dcc.Download(id="download-dataframe-excel"),

    # HEADER EXECUTIVO COM NAVEGADOR PRINCIPAL
    html.Header(className="header-container", children=[
        html.Div(className="brand-wrapper", children=[
            html.Div("FATEC", className="brand-badge"),
            html.Div([
                html.H1("Fatec Pesquisa", className="brand-title"),
                html.P("Faculdade de Tecnologia de Franca · Dr. Thomaz Novelino · Centro Paula Souza", className="brand-subtitle")
            ])
        ]),
        
        html.Div(className="nav-switch-wrapper", children=[
            dcc.RadioItems(
                id="main-view-mode",
                options=[
                    {"label": "📊 Painel por Cursos", "value": "view-dashboard"},
                    {"label": "✍️ Área do Aluno (Responder)", "value": "view-form"}
                ],
                value="view-dashboard",
                inline=True,
                className="view-mode-selector",
                inputStyle={"marginRight": "6px"}
            )
        ])
    ]),

    # CONTAINER DINÂMICO PRINCIPAL
    html.Main(id="main-view-container", className="main-wrapper"),

    # RODAPÉ
    html.Footer(className="dashboard-footer", children=[
        html.P("Fatec Pesquisa · Faculdade de Tecnologia de Franca · Centro Estadual de Educação Tecnológica Paula Souza")
    ])
])

# =============================================================================
# HELPER: CONTAGEM DE ALUNOS POR CURSO
# =============================================================================
def contar_alunos_por_curso(df):
    contagens = {"ADS": 0, "DSM": 0, "GPI": 0, "GRH": 0, "GE": 0, "TODOS": len(df)}
    if df.empty:
        return contagens
        
    col_curso = None
    for c in df.columns:
        if "curso" in c.lower():
            col_curso = c
            break
            
    if col_curso:
        for val in df[col_curso].dropna().astype(str):
            for sigla in ["ADS", "DSM", "GPI", "GRH", "GE"]:
                if sigla in val:
                    contagens[sigla] += 1
                    break
    return contagens

# =============================================================================
# HELPER: HUB DE CARDS DE CADA CURSO DA FATEC FRANCA
# =============================================================================
def renderizar_cards_de_cursos(df, active_course):
    contagens = contar_alunos_por_curso(df)
    cards = []
    
    # 1. Card "Todos os Cursos"
    is_active_all = (active_course == "TODOS")
    cards.append(
        html.Button(
            id={"type": "btn-course-card", "index": "TODOS"},
            className=f"course-hub-card {'course-hub-card-active' if is_active_all else ''}",
            n_clicks=0,
            children=[
                html.Div(className="course-hub-top", children=[
                    html.Span("🏛️", className="course-hub-icon"),
                    html.Span("Geral FATEC", className="course-hub-sigla", style={"backgroundColor": "#f1f5f9", "color": "#0284c7", "borderColor": "#cbd5e1"})
                ]),
                html.H3("Visão Geral Consolidada", className="course-hub-title"),
                html.Div(className="course-hub-badge-row", children=[
                    html.Span("Todos os 5 Cursos", className="hub-badge-periodo")
                ]),
                html.Div(className="course-hub-footer", children=[
                    html.Span(f"{contagens['TODOS']} Respostas Totais", className="hub-student-count-pill")
                ])
            ]
        )
    )
    
    # 2. Cards dos 5 Cursos Oficiais
    for c in CURSOS_FATEC_FRANCA:
        is_active = (active_course == c["sigla"])
        qtd = contagens.get(c["sigla"], 0)
        
        cards.append(
            html.Button(
                id={"type": "btn-course-card", "index": c["sigla"]},
                className=f"course-hub-card {'course-hub-card-active' if is_active else ''}",
                style={"borderColor": f"{c['cor']}88" if is_active else "#e2e8f0"},
                n_clicks=0,
                children=[
                    html.Div(className="course-hub-top", children=[
                        html.Span(c["icone"], className="course-hub-icon"),
                        html.Span(c["sigla"], className="course-hub-sigla", style={"backgroundColor": f"{c['cor']}15", "color": c["cor"], "borderColor": f"{c['cor']}44"})
                    ]),
                    html.H3(c["nome"], className="course-hub-title"),
                    html.Div(className="course-hub-badge-row", children=[
                        html.Span(c["modalidade"], className="hub-badge-mod"),
                        html.Span(f"🕒 {c['periodo']}", className="hub-badge-periodo")
                    ]),
                    html.Div(className="course-hub-footer", children=[
                        html.Span(
                            f"✓ {qtd} Aluno(s) Respondentes" if qtd > 0 else "0 Alunos (Sem respostas)",
                            className="hub-student-count-pill",
                            style={"color": c["cor"] if qtd > 0 else "#94a3b8", "backgroundColor": f"{c['cor']}12" if qtd > 0 else "#f1f5f9"}
                        )
                    ])
                ]
            )
        )
        
    return html.Div(className="course-hub-grid", children=cards)

# =============================================================================
# HELPER DE RENDERIZAÇÃO DE RESULTADOS: SIMPLES, DIRETO E SEM PIZZA
# =============================================================================
def criar_grafico_para_leigos(df, col, titulo, tipo='bar-h'):
    if col not in df.columns or df[col].dropna().empty:
        return html.Div(className="chart-card full-width", style={"textAlign": "center", "padding": "40px"}, children=[
            html.H4("Nenhum dado registrado para esta pergunta neste curso.", style={"color": "#0f172a"}),
            html.P("Assim que alunos deste curso responderem pelo formulário, as métricas aparecerão automaticamente.", style={"color": "#64748b"})
        ])
        
    vc = df[col].dropna().astype(str).value_counts().reset_index()
    vc.columns = [col, 'Respostas']
    total = vc['Respostas'].sum()
    vc['Percentual'] = (vc['Respostas'] / total) * 100
    vc['Texto'] = [f"{p:.1f}% ({r} alunos)" for p, r in zip(vc['Percentual'], vc['Respostas'])]
    
    item_lider = vc.iloc[0][col]
    pct_lider = vc.iloc[0]['Percentual']
    qtd_lider = vc.iloc[0]['Respostas']
    
    # 1. CARDS VISUAIS DE PROGRESSO (MÉTRICA RÁPIDA E ELEGANTE)
    cards_opcoes = []
    icones_rank = ["🥇 1º Mais Votado", "🥈 2º Lugar", "🥉 3º Lugar", "4º Lugar", "5º Lugar", "6º Lugar", "7º Lugar", "8º Lugar"]
    
    for idx, row in vc.head(8).iterrows():
        is_leader = (idx == 0)
        rank_label = icones_rank[idx] if idx < len(icones_rank) else f"{idx+1}º Lugar"
        pct_val = row['Percentual']
        bar_color = "#0284c7" if is_leader else "#64748b"
        
        cards_opcoes.append(
            html.Div(className=f"metric-option-card {'metric-option-leader' if is_leader else ''}", children=[
                html.Div(className="metric-option-top", children=[
                    html.Span(rank_label, className="metric-rank-badge", style={"color": "#0284c7" if is_leader else "#64748b"}),
                    html.Span(f"{row['Respostas']} aluno(s)", className="metric-count-pill")
                ]),
                html.Div(row[col], className="metric-option-name"),
                html.Div(className="metric-option-percent-row", children=[
                    html.Span(f"{pct_val:.1f}%", className="metric-large-percent"),
                    html.Span(f"({row['Respostas']}/{total})", className="metric-fraction")
                ]),
                html.Div(className="metric-progress-bg", children=[
                    html.Div(className="metric-progress-fill", style={"width": f"{pct_val:.1f}%", "backgroundColor": bar_color})
                ])
            ])
        )

    # 2. GRÁFICO DE BARRAS HORIZONTAIS LIMPO
    vc_chart = vc.head(10).sort_values(by='Respostas', ascending=True)
    fig = px.bar(
        vc_chart,
        x='Respostas',
        y=col,
        orientation='h',
        text='Texto',
        color='Respostas',
        color_continuous_scale="Blues",
        title=titulo
    )
    fig.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title="Número de Alunos", **LAYOUT_DEFAULTS)
    fig.update_traces(textposition='outside', cliponaxis=False)

    # 3. RESUMO DIRETO PARA LEIGOS
    resumo_leigo = html.Div(className="layman-insight-card", children=[
        html.Div(className="insight-badge", children="💡 Resumo Claro dos Resultados"),
        html.P([
            html.Span("Maioria dos alunos escolheu: ", style={"fontWeight": "600", "color": "#0f172a"}),
            html.Strong(f"'{item_lider}'", style={"color": "#0284c7"}),
            f" representando ",
            html.Strong(f"{pct_lider:.1f}%", style={"color": "#059669"}),
            f" do total ({qtd_lider} de {total} alunos que responderam)."
        ], style={"margin": 0, "fontSize": "0.95rem", "lineHeight": "1.5"})
    ])

    return html.Div(className="chart-card full-width", children=[
        html.H3(titulo, className="chart-card-title", style={"marginBottom": "16px"}),
        resumo_leigo,
        html.Div(className="metric-cards-grid", children=cards_opcoes),
        html.Hr(style={"borderColor": "rgba(226, 232, 240, 0.8)", "margin": "24px 0 16px 0"}),
        html.H4("Visualização Gráfica Comparativa", style={"fontSize": "0.95rem", "fontWeight": "700", "color": "#0f172a", "marginBottom": "8px"}),
        dcc.Graph(figure=fig)
    ])

# =============================================================================
# HELPER: ÁREA DO ALUNO
# =============================================================================
def criar_layout_area_do_aluno():
    return html.Div(className="aluno-portal-wrapper", children=[
        html.Div(className="form-intro-card", children=[
            html.Div(className="form-intro-header", children=[
                html.Span("🎓", style={"fontSize": "2.5rem"}),
                html.Div([
                    html.H2("Questionário Socioeconômico do Estudante", className="form-intro-title"),
                    html.P("Sua participação é fundamental para aprimorar as ações pedagógicas, estrutura e apoio aos alunos da FATEC Franca.", className="form-intro-subtitle")
                ])
            ]),
            html.Div(className="form-rule-notice", children=[
                html.Span("🔒 Identificação Acadêmica: ", style={"fontWeight": "bold", "color": "#0284c7"}),
                "O acesso é identificado por RA e CPF. Cada aluno possui permissão para preencher a pesquisa apenas uma única vez."
            ])
        ]),

        html.Div(className="form-container-card", children=[
            # SEÇÃO 1: IDENTIFICAÇÃO DO ALUNO
            html.Div(className="form-section-block", children=[
                html.H3("1. Identificação do Estudante", className="form-section-title"),
                html.Div(className="form-grid-4", children=[
                    html.Div(className="form-field-group", children=[
                        html.Label("Nome Completo *", className="form-label"),
                        dcc.Input(id="aluno-nome", type="text", placeholder="Ex: Samuel Silva", className="form-input")
                    ]),
                    html.Div(className="form-field-group", children=[
                        html.Label("RA (Registro Acadêmico) *", className="form-label"),
                        dcc.Input(id="aluno-ra", type="text", placeholder="Ex: 2791382411001", className="form-input")
                    ]),
                    html.Div(className="form-field-group", children=[
                        html.Label("CPF (Apenas números) *", className="form-label"),
                        dcc.Input(id="aluno-cpf", type="text", placeholder="Ex: 12345678900", className="form-input")
                    ]),
                    html.Div(className="form-field-group", children=[
                        html.Label("Data de Nascimento *", className="form-label"),
                        dcc.Input(id="aluno-nascimento", type="text", placeholder="Ex: 15/03/2003", className="form-input")
                    ]),
                ])
            ]),

            # SEÇÃO 2: CURSO & DADOS ACADÊMICOS
            html.Div(className="form-section-block", children=[
                html.H3("2. Curso & Vida Acadêmica na FATEC Franca", className="form-section-title"),
                html.Div(className="form-grid-3", children=[
                    html.Div(className="form-field-group", children=[
                        html.Label("Qual o seu curso? *", className="form-label"),
                        dcc.Dropdown(
                            id="aluno-curso",
                            options=OPCOES_CURSOS_COMPLETAS,
                            placeholder="Selecione seu curso",
                            className="dash-dropdown"
                        )
                    ]),
                    html.Div(className="form-field-group", children=[
                        html.Label("Período / Turno *", className="form-label"),
                        dcc.Dropdown(
                            id="aluno-periodo",
                            options=[
                                {"label": "Matutino (Manhã)", "value": "Manhã"},
                                {"label": "Vespertino (Tarde)", "value": "Tarde"},
                                {"label": "Noturno (Noite)", "value": "Noite"},
                                {"label": "EaD (Horário Flexível)", "value": "EaD"}
                            ],
                            placeholder="Selecione o turno",
                            className="dash-dropdown"
                        )
                    ]),
                    html.Div(className="form-field-group", children=[
                        html.Label("Cidade em que reside *", className="form-label"),
                        dcc.Input(id="aluno-cidade", type="text", placeholder="Ex: Franca, Patrocínio Paulista...", className="form-input")
                    ]),
                ]),
                html.Div(className="form-grid-2", style={"marginTop": "14px"}, children=[
                    html.Div(className="form-field-group", children=[
                        html.Label("Histórico Escolar Anterior (Ensino Médio) *", className="form-label"),
                        dcc.Dropdown(
                            id="aluno-escola",
                            options=[
                                {"label": "Sempre na escola pública", "value": "Sempre na escola pública"},
                                {"label": "Maior parte na escola pública", "value": "Maior parte na escola pública"},
                                {"label": "Sempre em escola particular", "value": "Sempre em escola particular"},
                                {"label": "Maior parte em escola particular", "value": "Maior parte em escola particular"}
                            ],
                            placeholder="Selecione sua formação",
                            className="dash-dropdown"
                        )
                    ]),
                    html.Div(className="form-field-group", children=[
                        html.Label("Gênero *", className="form-label"),
                        dcc.Dropdown(
                            id="aluno-genero",
                            options=[
                                {"label": "Masculino", "value": "Masculino"},
                                {"label": "Feminino", "value": "Feminino"},
                                {"label": "Outro", "value": "Outro"},
                                {"label": "Prefiro não responder", "value": "Prefiro não responder"}
                            ],
                            placeholder="Selecione",
                            className="dash-dropdown"
                        )
                    ])
                ])
            ]),

            # SEÇÃO 3: PERFIL SOCIOECONÔMICO & MORADIA
            html.Div(className="form-section-block", children=[
                html.H3("3. Moradia & Condição Socioeconômica", className="form-section-title"),
                html.Div(className="form-grid-3", children=[
                    html.Div(className="form-field-group", children=[
                        html.Label("Estado Civil *", className="form-label"),
                        dcc.Dropdown(
                            id="aluno-civil",
                            options=[
                                {"label": "Solteiro(a)", "value": "Solteiro(a)"},
                                {"label": "Casado(a) / União Estável", "value": "Casado(a)"},
                                {"label": "Divorciado(a)", "value": "Divorciado(a)"},
                                {"label": "Viúvo(a)", "value": "Viúvo(a)"}
                            ],
                            placeholder="Selecione",
                            className="dash-dropdown"
                        )
                    ]),
                    html.Div(className="form-field-group", children=[
                        html.Label("Quantos filhos você tem? *", className="form-label"),
                        dcc.Dropdown(
                            id="aluno-filhos",
                            options=[{"label": str(i), "value": str(i)} for i in ["Nenhum", "1", "2", "3", "4 ou mais"]],
                            placeholder="Selecione",
                            className="dash-dropdown"
                        )
                    ]),
                    html.Div(className="form-field-group", children=[
                        html.Label("Com quem mora atualmente? *", className="form-label"),
                        dcc.Dropdown(
                            id="aluno-mora-com",
                            options=[
                                {"label": "Com os pais / familiares", "value": "Com os pais"},
                                {"label": "Com cônjuge / filhos", "value": "Com cônjuge / filhos"},
                                {"label": "Sozinho(a)", "value": "Sozinho"},
                                {"label": "Com amigos / república", "value": "Com amigos / república"}
                            ],
                            placeholder="Selecione",
                            className="dash-dropdown"
                        )
                    ]),
                ]),
                html.Div(className="form-grid-2", style={"marginTop": "14px"}, children=[
                    html.Div(className="form-field-group", children=[
                        html.Label("Situação do Domicílio *", className="form-label"),
                        dcc.Dropdown(
                            id="aluno-moradia-tipo",
                            options=[
                                {"label": "Próprio", "value": "Próprio"},
                                {"label": "Financiado", "value": "Financiado"},
                                {"label": "Alugado", "value": "Alugado"},
                                {"label": "Cedido / Outros", "value": "Cedido"}
                            ],
                            placeholder="Selecione a situação",
                            className="dash-dropdown"
                        )
                    ]),
                    html.Div(className="form-field-group", children=[
                        html.Label("Faixa de Renda Mensal Familiar *", className="form-label"),
                        dcc.Dropdown(
                            id="aluno-renda",
                            options=[
                                {"label": "Até 1,5 Salário Mínimo (Até R$ 2.100)", "value": "Até R$ 1.518,00"},
                                {"label": "De 1,5 a 3 Salários Mínimos (R$ 2.100 a R$ 4.500)", "value": "De R$ 1.518,01 até R$ 3.036,00"},
                                {"label": "De 3 a 5 Salários Mínimos (R$ 4.500 a R$ 7.500)", "value": "De R$ 3.036,01 até R$ 5.000,00"},
                                {"label": "Acima de 5 Salários Mínimos (Acima de R$ 7.500)", "value": "Mais de R$ 5.000,00"}
                            ],
                            placeholder="Selecione a faixa de renda",
                            className="dash-dropdown"
                        )
                    ])
                ])
            ]),

            # SEÇÃO 4: TRABALHO & CARREIRA
            html.Div(className="form-section-block", children=[
                html.H3("4. Situação de Trabalho & Profissional", className="form-section-title"),
                html.Div(className="form-grid-3", children=[
                    html.Div(className="form-field-group", children=[
                        html.Label("Você trabalha atualmente? *", className="form-label"),
                        dcc.Dropdown(
                            id="aluno-trabalha",
                            options=[{"label": "Sim", "value": "Sim"}, {"label": "Não", "value": "Não"}],
                            placeholder="Selecione",
                            className="dash-dropdown"
                        )
                    ]),
                    html.Div(className="form-field-group", children=[
                        html.Label("Vínculo Empregatício", className="form-label"),
                        dcc.Dropdown(
                            id="aluno-vinculo",
                            options=[
                                {"label": "CLT (Carteira Assinada)", "value": "Sou registrado(a) no comércio"},
                                {"label": "Estágio", "value": "Estágio"},
                                {"label": "Autônomo / PJ", "value": "Autônomo"},
                                {"label": "Servidor Público", "value": "Servidor Público"},
                                {"label": "Não trabalho", "value": "Não trabalho"}
                            ],
                            placeholder="Selecione o vínculo",
                            className="dash-dropdown"
                        )
                    ]),
                    html.Div(className="form-field-group", children=[
                        html.Label("Atuação na Área do Curso", className="form-label"),
                        dcc.Dropdown(
                            id="aluno-area-trab",
                            options=[
                                {"label": "Sim, trabalho na área do curso", "value": "Trabalho na área do curso"},
                                {"label": "Não, trabalho em outra área", "value": "Trabalho em outra área"},
                                {"label": "Não estou trabalhando", "value": "Não se aplica"}
                            ],
                            placeholder="Selecione",
                            className="dash-dropdown"
                        )
                    ])
                ])
            ]),

            # SEÇÃO 5: TECNOLOGIA & BENS NO DOMICÍLIO
            html.Div(className="form-section-block", children=[
                html.H3("5. Acesso à Tecnologia & Recursos", className="form-section-title"),
                html.Div(className="form-grid-4", children=[
                    html.Div(className="form-field-group", children=[
                        html.Label("Possui Internet em Casa? *", className="form-label"),
                        dcc.Dropdown(id="aluno-internet", options=[{"label": "Sim", "value": "Sim"}, {"label": "Não", "value": "Não"}], value="Sim", className="dash-dropdown")
                    ]),
                    html.Div(className="form-field-group", children=[
                        html.Label("Possui Smartphone / Celular? *", className="form-label"),
                        dcc.Dropdown(id="aluno-smartphone", options=[{"label": "Sim", "value": "Sim"}, {"label": "Não", "value": "Não"}], value="Sim", className="dash-dropdown")
                    ]),
                    html.Div(className="form-field-group", children=[
                        html.Label("Possui Notebook? *", className="form-label"),
                        dcc.Dropdown(id="aluno-notebook", options=[{"label": "Sim", "value": "Sim"}, {"label": "Não", "value": "Não"}], value="Sim", className="dash-dropdown")
                    ]),
                    html.Div(className="form-field-group", children=[
                        html.Label("Possui Computador de Mesa (Desktop)? *", className="form-label"),
                        dcc.Dropdown(id="aluno-desktop", options=[{"label": "Sim", "value": "Sim"}, {"label": "Não", "value": "Não"}], value="Não", className="dash-dropdown")
                    ]),
                ])
            ]),

            # SEÇÃO 6: EXPECTATIVAS & DISSERTAÇÃO
            html.Div(className="form-section-block", children=[
                html.H3("6. Expectativas, Motivações & Sonhos", className="form-section-title"),
                html.Div(className="form-field-group", style={"marginBottom": "14px"}, children=[
                    html.Label("Por que você escolheu este curso na FATEC Franca? *", className="form-label"),
                    dcc.Textarea(id="aluno-motivo", placeholder="Descreva o que motivou sua escolha...", style={"width": "100%", "height": "75px"}, className="form-textarea")
                ]),
                html.Div(className="form-field-group", style={"marginBottom": "14px"}, children=[
                    html.Label("Qual sua maior expectativa quanto ao curso? *", className="form-label"),
                    dcc.Textarea(id="aluno-expectativa-curso", placeholder="O que você espera aprender e desenvolver durante a graduação?", style={"width": "100%", "height": "75px"}, className="form-textarea")
                ]),
                html.Div(className="form-field-group", style={"marginBottom": "14px"}, children=[
                    html.Label("Qual sua expectativa após se formar? *", className="form-label"),
                    dcc.Textarea(id="aluno-expectativa-formar", placeholder="Quais são seus planos profissionais pós-formatura?", style={"width": "100%", "height": "75px"}, className="form-textarea")
                ]),
                html.Div(className="form-field-group", children=[
                    html.Label("Escreva algumas linhas sobre sua história e seus sonhos de vida *", className="form-label"),
                    dcc.Textarea(id="aluno-historia-sonhos", placeholder="Compartilhe suas conquistas, desafios e sonhos futuros...", style={"width": "100%", "height": "95px"}, className="form-textarea")
                ]),
            ]),

            html.Div(id="aluno-form-status-box"),

            html.Div(className="form-submit-footer", children=[
                html.Button("📤 Enviar Minha Pesquisa", id="btn-submit-pesquisa", className="btn-submit-large", n_clicks=0)
            ])
        ])
    ])

# =============================================================================
# CALLBACK: ALTERNAR VISÃO PRINCIPAL (DASHBOARD vs ÁREA DO ALUNO)
# =============================================================================
@app.callback(
    Output('main-view-container', 'children'),
    Input('main-view-mode', 'value')
)
def switch_main_view(view_mode):
    if view_mode == 'view-form':
        return criar_layout_area_do_aluno()
    
    # Visão Dashboard Centrada nos Cards de Cursos
    return [
        # HUB DE CARDS DE CURSOS (TOPO)
        html.Section(className="courses-section-wrapper", children=[
            html.Div(className="section-header-row", children=[
                html.H2("🎓 Selecione o Card do Curso para Ver os Resultados", className="section-title"),
                html.Span("Clique em qualquer curso abaixo para abrir as pesquisas e gráficos exclusivos dele", className="section-hint")
            ]),
            html.Div(id="course-hub-cards-container")
        ]),

        # CONTEÚDO DEDICADO DO CURSO SELECIONADO
        html.Section(id="active-course-details-section", style={"marginTop": "24px"})
    ]

# =============================================================================
# CALLBACK: ATUALIZAR OS CARDS DE CURSO E ESTADO ATIVO
# =============================================================================
@app.callback(
    Output('course-hub-cards-container', 'children'),
    Input('dataset-store', 'data'),
    Input('active-course-store', 'data')
)
def update_course_cards(json_data, active_course):
    if not json_data:
        return html.Div()
    df = pd.read_json(StringIO(json_data), orient='split')
    return renderizar_cards_de_cursos(df, active_course or "ADS")

# =============================================================================
# CALLBACK: ATIVAR CURSO AO CLICAR EM SEU CARD
# =============================================================================
@app.callback(
    Output('active-course-store', 'data'),
    Input({'type': 'btn-course-card', 'index': ALL}, 'n_clicks'),
    State('active-course-store', 'data'),
    prevent_initial_call=True
)
def select_active_course(n_clicks_list, current_course):
    ctx = callback_context
    if not ctx.triggered:
        return current_course
    prop_id = ctx.triggered[0]['prop_id']
    try:
        import json
        prop_dict = json.loads(prop_id.split(".")[0])
        return prop_dict["index"]
    except Exception:
        return current_course

# =============================================================================
# CALLBACK: ATIVAR PERGUNTA CLICADA NO CATÁLOGO VISUAL
# =============================================================================
@app.callback(
    Output('active-question-id-store', 'data'),
    Input({'type': 'btn-question-tile', 'index': ALL}, 'n_clicks'),
    State('active-question-id-store', 'data'),
    prevent_initial_call=True
)
def select_active_question(n_clicks_list, current_q):
    ctx = callback_context
    if not ctx.triggered:
        return current_q
    prop_id = ctx.triggered[0]['prop_id']
    try:
        import json
        prop_dict = json.loads(prop_id.split(".")[0])
        return prop_dict["index"]
    except Exception:
        return current_q

# =============================================================================
# CALLBACK: RENDERIZAR O PAINEL ESPECÍFICO DO CURSO ATIVO
# =============================================================================
@app.callback(
    Output('active-course-details-section', 'children'),
    Input('active-course-store', 'data'),
    Input('active-question-id-store', 'data'),
    Input('dataset-store', 'data')
)
def render_active_course_section(active_course, active_question_id, json_data):
    if not json_data:
        return html.Div()
        
    df_global = pd.read_json(StringIO(json_data), orient='split')
    sigla = active_course or "ADS"
    pergunta_ativa = active_question_id or "q_periodo"
    
    # 1. Filtrar a base para o curso selecionado
    if sigla == "TODOS":
        df_curso = df_global.copy()
        curso_info = {
            "nome": "Visão Geral Consolidada (Todos os Cursos)",
            "sigla": "FATEC",
            "icone": "🏛️",
            "cor": "#0284c7",
            "modalidade": "Presencial & EaD",
            "periodo": "Todos os Turnos",
            "duracao": "3 anos",
            "descricao": "Dados consolidados de todos os estudantes respondentes da FATEC Franca."
        }
    else:
        curso_info = next((c for c in CURSOS_FATEC_FRANCA if c["sigla"] == sigla), CURSOS_FATEC_FRANCA[0])
        col_curso = None
        for c in df_global.columns:
            if "curso" in c.lower():
                col_curso = c
                break
        if col_curso:
            df_curso = df_global[df_global[col_curso].astype(str).str.contains(sigla, case=False, na=False)].copy()
        else:
            df_curso = df_global.copy()

    total_alunos = len(df_curso)
    
    # Métricas do curso
    media_idade_str = f"{df_curso['Idade'].mean():.1f} anos" if "Idade" in df_curso.columns and not df_curso["Idade"].dropna().empty else "N/D"
    
    pct_trabalha_str = "N/D"
    for col in df_curso.columns:
        if "trabalha" in col.lower() and "?" in col:
            vc = df_curso[col].astype(str).str.strip().str.lower().value_counts(normalize=True)
            for k, v in vc.items():
                if "sim" in k:
                    pct_trabalha_str = f"{v * 100:.1f}%"
                    break
            break
            
    pct_internet_str = "N/D"
    for col in df_curso.columns:
        if col.strip().lower() == "internet":
            vc = df_curso[col].astype(str).str.strip().str.lower().value_counts(normalize=True)
            for k, v in vc.items():
                if "sim" in k:
                    pct_internet_str = f"{v * 100:.0f}%"
                    break
            break

    # Header Card do Curso
    banner_curso = html.Div(className="course-focus-banner", style={"borderLeftColor": curso_info["cor"]}, children=[
        html.Div(className="course-banner-top", children=[
            html.Div(className="course-banner-left", children=[
                html.Span(curso_info["icone"], className="course-banner-icon"),
                html.Div([
                    html.H2(f"Pesquisa: {curso_info['nome']}", className="course-banner-title"),
                    html.P(curso_info["descricao"], className="course-banner-desc")
                ])
            ]),
            html.Div(className="course-banner-right", children=[
                html.Span(f"🎓 {curso_info['sigla']}", className="course-banner-badge", style={"backgroundColor": f"{curso_info['cor']}15", "color": curso_info["cor"], "borderColor": f"{curso_info['cor']}44"})
            ])
        ]),
        
        # 4 Mini-KPIs exclusivos deste curso
        html.Div(className="course-kpis-strip", children=[
            html.Div(className="course-mini-kpi", children=[
                html.Div("👥 Alunos Respondentes", className="mini-kpi-label"),
                html.Div(f"{total_alunos} alunos", className="mini-kpi-value")
            ]),
            html.Div(className="course-mini-kpi", children=[
                html.Div("🎂 Idade Média", className="mini-kpi-label"),
                html.Div(media_idade_str, className="mini-kpi-value")
            ]),
            html.Div(className="course-mini-kpi", children=[
                html.Div("💼 Taxa de Emprego", className="mini-kpi-label"),
                html.Div(pct_trabalha_str, className="mini-kpi-value")
            ]),
            html.Div(className="course-mini-kpi", children=[
                html.Div("🌐 Internet em Casa", className="mini-kpi-label"),
                html.Div(pct_internet_str, className="mini-kpi-value")
            ]),
        ])
    ])

    # =========================================================================
    # CATÁLOGO VISUAL DE BOTÕES CLICÁVEIS DE PERGUNTAS
    # =========================================================================
    blocos_catalogo = []
    
    for grupo in CATALOGO_PERGUNTAS:
        botoes_grupo = []
        for item in grupo["itens"]:
            is_active = (pergunta_ativa == item["id"])
            botoes_grupo.append(
                html.Button(
                    id={"type": "btn-question-tile", "index": item["id"]},
                    className=f"question-tile-btn {'question-tile-btn-active' if is_active else ''}",
                    n_clicks=0,
                    children=[
                        html.Span(item["icone"], className="tile-icon"),
                        html.Span(item["titulo"], className="tile-text"),
                        html.Span("✓" if is_active else "➔", className="tile-indicator")
                    ]
                )
            )
            
        blocos_catalogo.append(
            html.Div(className="question-group-block", children=[
                html.Div(className="group-title-row", children=[
                    html.Span(grupo["categoria"], className="group-category-title", style={"color": grupo["cor"]})
                ]),
                html.Div(className="question-tiles-grid", children=botoes_grupo)
            ])
        )

    painel_catalogo_visual = html.Div(className="catalog-visual-wrapper", children=[
        html.Div(className="catalog-header-bar", children=[
            html.H3("👇 Clique na pergunta que deseja analisar neste curso:", className="catalog-main-title"),
            html.Span("Selecione qualquer opção abaixo para abrir os resultados instantaneamente", className="catalog-sub-title")
        ]),
        html.Div(className="catalog-groups-container", children=blocos_catalogo)
    ])

    # =========================================================================
    # RENDERIZADOR DO RESULTADO DA PERGUNTA CLICADA
    # =========================================================================
    def achar_col(termos):
        for col in df_curso.columns:
            if any(t.lower() in col.lower() for t in termos):
                return col
        return None

    item_selecionado = None
    for grupo in CATALOGO_PERGUNTAS:
        for item in grupo["itens"]:
            if item["id"] == pergunta_ativa:
                item_selecionado = item
                break
        if item_selecionado:
            break
            
    if not item_selecionado:
        item_selecionado = CATALOGO_PERGUNTAS[0]["itens"][0]

    conteudo_grafico = []

    # 1. Caso Especial: Painel Geral de Bens Tecnológicos
    if item_selecionado["tipo"] == "bens_geral":
        colunas_bens = ["Internet", "Celular e(ou) Smartphone", "Notebook", "Microcomputador de mesa/Desktop", "Automóvel", "TV por assinatura e(ou) Serviços de Streaming"]
        posse_dados = []
        for bem in colunas_bens:
            matching_col = achar_col([bem])
            if matching_col:
                serie = df_curso[matching_col].dropna().astype(str).str.strip().str.lower()
                positivos = serie.apply(lambda x: 0 if x in ["0", "nenhum", "não", "nao", "nenhuma", ""] else 1)
                pct = (positivos.sum() / len(serie)) * 100 if len(serie) > 0 else 0
                posse_dados.append({"Equipamento": bem, "Porcentagem": pct, "Qtd": positivos.sum()})

        if posse_dados:
            df_bens = pd.DataFrame(posse_dados).sort_values(by="Porcentagem", ascending=True)
            df_bens["Texto"] = [f"{p:.1f}% ({q} alunos)" for p, q in zip(df_bens["Porcentagem"], df_bens["Qtd"])]
            
            # Cards de resumo dos bens
            cards_bens = []
            for _, r in df_bens.sort_values(by="Porcentagem", ascending=False).iterrows():
                cards_bens.append(
                    html.Div(className="metric-option-card", children=[
                        html.Div(className="metric-option-top", children=[
                            html.Span("📱 Recurso", className="metric-rank-badge"),
                            html.Span(f"{r['Qtd']} alunos", className="metric-count-pill")
                        ]),
                        html.Div(r['Equipamento'], className="metric-option-name"),
                        html.Div(className="metric-option-percent-row", children=[
                            html.Span(f"{r['Porcentagem']:.1f}%", className="metric-large-percent"),
                            html.Span(f"({r['Qtd']}/{total_alunos})", className="metric-fraction")
                        ]),
                        html.Div(className="metric-progress-bg", children=[
                            html.Div(className="metric-progress-fill", style={"width": f"{r['Porcentagem']:.1f}%", "backgroundColor": "#0284c7"})
                        ])
                    ])
                )
            
            fig_bens = px.bar(
                df_bens, x="Porcentagem", y="Equipamento", orientation='h',
                text="Texto", color="Porcentagem", color_continuous_scale="Blues",
                title=f"Acesso à Tecnologia dos Alunos de {curso_info['sigla']}"
            )
            fig_bens.update_traces(textposition='outside', cliponaxis=False)
            fig_bens.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title="Porcentagem (%)", **LAYOUT_DEFAULTS)
            
            conteudo_grafico = html.Div(className="chart-card full-width", children=[
                html.H3(f"Acesso a Recursos Tecnológicos ({curso_info['sigla']})", className="chart-card-title", style={"marginBottom": "16px"}),
                html.Div(className="layman-insight-card", children=[
                    html.Div(className="insight-badge", children="💡 Leitura Fácil"),
                    html.P(f"Visão consolidada dos equipamentos e serviços de conectividade dos estudantes de {curso_info['sigla']}.", style={"margin": 0, "fontSize": "0.95rem"})
                ]),
                html.Div(className="metric-cards-grid", children=cards_bens),
                html.Hr(style={"borderColor": "rgba(226, 232, 240, 0.8)", "margin": "24px 0 16px 0"}),
                dcc.Graph(figure=fig_bens)
            ])
            
    # 2. Caso Especial: Nuvem de Palavras / Questões Qualitativas
    elif item_selecionado["tipo"] == "wordcloud":
        col_sonhos = achar_col(item_selecionado["termos"])
        if not col_sonhos:
            col_sonhos = COLUNAS_QUALITATIVAS[0]
            
        serie_texto = df_curso[col_sonhos].dropna().astype(str) if col_sonhos in df_curso.columns else pd.Series()
        img_b64 = gerar_imagem_nuvem(serie_texto)
        top_termos = extrair_top_palavras(serie_texto, n=10)
        
        if top_termos:
            df_termos = pd.DataFrame(top_termos, columns=["Palavra", "Ocorrências"]).sort_values(by="Ocorrências", ascending=True)
            fig_termos = px.bar(
                df_termos, x="Ocorrências", y="Palavra", orientation='h', text="Ocorrências",
                color="Ocorrências", color_continuous_scale="Blues",
                title=f"Conceitos Mais Citados ({curso_info['sigla']}) - {item_selecionado['titulo']}"
            )
            fig_termos.update_traces(textposition='outside', cliponaxis=False)
            fig_termos.update_layout(coloraxis_showscale=False, yaxis_title="", **LAYOUT_DEFAULTS)
            comp_termos = dcc.Graph(figure=fig_termos)
        else:
            comp_termos = html.Div("Volume insuficiente de respostas textuais para extrair palavras.", style={"color": "#64748b", "padding": "20px"})
            
        comp_nuvem = html.Div(className="wordcloud-img-wrapper", children=[
            html.Img(src=f"data:image/png;base64,{img_b64}", className="wordcloud-img")
        ]) if img_b64 else html.Div()
        
        conteudo_grafico = html.Div(className="chart-card full-width", children=[
            html.H3(f"{item_selecionado['icone']} {item_selecionado['titulo']} ({curso_info['sigla']})", className="chart-card-title", style={"marginBottom": "16px"}),
            html.Div(className="layman-insight-card", children=[
                html.Div(className="insight-badge", children="💡 Leitura Fácil dos Sonhos & Expectativas"),
                html.P("Os termos destacados refletem as principais ambições profissionais, crescimento pessoal e objetivos dos alunos.", style={"margin": 0, "fontSize": "0.95rem"})
            ]),
            html.Div(className="wordcloud-container", children=[comp_nuvem, comp_termos])
        ])

    # 3. Caso Especial: Tabela de Respostas
    elif item_selecionado["tipo"] == "tabela":
        colunas_exibir = [c for c in df_curso.columns if not c.startswith("Unnamed")]
        conteudo_grafico = html.Div([
            html.Div(className="table-toolbar", children=[
                html.Div([
                    html.H3(f"Respostas Individuais dos Alunos de {curso_info['sigla']}", style={"margin": 0, "fontSize": "1.1rem", "color": "#0f172a"}),
                    html.P(f"Total de {len(df_curso)} registros de estudantes encontrados.", style={"margin": "2px 0 0 0", "fontSize": "0.85rem", "color": "#64748b"})
                ]),
                html.Div(style={"display": "flex", "gap": "10px"}, children=[
                    html.Button("📥 Exportar Excel (.xlsx)", id="btn-download-excel", className="btn-export", n_clicks=0),
                    html.Button("📥 Exportar CSV (.csv)", id="btn-download-csv", className="btn-export-secondary", n_clicks=0),
                ])
            ]),
            html.Div(className="dash-table-container", children=[
                dash_table.DataTable(
                    id='datatable-interact',
                    columns=[{"name": i, "id": i} for i in colunas_exibir],
                    data=df_curso.to_dict('records'),
                    page_size=10,
                    page_action='native',
                    sort_action='native',
                    sort_mode='multi',
                    filter_action='native',
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '10px 14px', 'fontFamily': 'Inter, sans-serif', 'fontSize': '0.86rem', 'backgroundColor': '#ffffff', 'color': '#334155', 'border': '1px solid #e2e8f0'},
                    style_header={'backgroundColor': '#f8fafc', 'fontWeight': 'bold', 'color': '#0f172a', 'border': '1px solid #e2e8f0'}
                )
            ])
        ])

    # 4. Caso Padrão: Pergunta Específica Clicada (Layout Simples e Direto)
    else:
        col_encontrada = achar_col(item_selecionado["termos"])
        if col_encontrada:
            titulo_grafico = f"{item_selecionado['icone']} {item_selecionado['titulo']} ({curso_info['sigla']})"
            conteudo_grafico = criar_grafico_para_leigos(df_curso, col_encontrada, titulo_grafico, tipo='bar-h')
        else:
            conteudo_grafico = html.Div(className="chart-card full-width", style={"textAlign": "center", "padding": "40px"}, children=[
                html.H4("Pergunta não encontrada no banco de dados para este curso.", style={"color": "#0f172a"})
            ])

    return html.Div(children=[
        banner_curso,
        painel_catalogo_visual,
        html.Div(style={"marginTop": "24px"}, children=conteudo_grafico)
    ])

# =============================================================================
# CALLBACK: PROCESSAMENTO DA RESPOSTA DO ALUNO
# =============================================================================
@app.callback(
    Output('aluno-form-status-box', 'children'),
    Output('dataset-store', 'data', allow_duplicate=True),
    Input('btn-submit-pesquisa', 'n_clicks'),
    State('aluno-nome', 'value'),
    State('aluno-ra', 'value'),
    State('aluno-cpf', 'value'),
    State('aluno-nascimento', 'value'),
    State('aluno-curso', 'value'),
    State('aluno-periodo', 'value'),
    State('aluno-cidade', 'value'),
    State('aluno-escola', 'value'),
    State('aluno-genero', 'value'),
    State('aluno-civil', 'value'),
    State('aluno-filhos', 'value'),
    State('aluno-mora-com', 'value'),
    State('aluno-moradia-tipo', 'value'),
    State('aluno-renda', 'value'),
    State('aluno-trabalha', 'value'),
    State('aluno-vinculo', 'value'),
    State('aluno-area-trab', 'value'),
    State('aluno-internet', 'value'),
    State('aluno-smartphone', 'value'),
    State('aluno-notebook', 'value'),
    State('aluno-desktop', 'value'),
    State('aluno-motivo', 'value'),
    State('aluno-expectativa-curso', 'value'),
    State('aluno-expectativa-formar', 'value'),
    State('aluno-historia-sonhos', 'value'),
    State('dataset-store', 'data'),
    prevent_initial_call=True
)
def processar_submissao_aluno(n_clicks, nome, ra, cpf, nascimento,
                              curso, periodo, cidade, escola, genero, civil, filhos,
                              mora_com, moradia_tipo, renda, trabalha, vinculo, area_trab,
                              internet, smartphone, notebook, desktop,
                              motivo, exp_curso, exp_formar, historia_sonhos, current_store):
    if not n_clicks or n_clicks == 0:
        return None, current_store

    if not nome or not ra or not cpf:
        return html.Div(className="alert-box alert-warning", children=[
            html.Span("⚠️ "),
            "Por favor, preencha todos os campos obrigatórios de identificação (Nome, RA e CPF)."
        ]), current_store

    ra_limpo = re.sub(r'[^0-9a-zA-Z]', '', str(ra)).strip().upper()
    cpf_limpo = re.sub(r'[^0-9]', '', str(cpf)).strip()

    if len(cpf_limpo) < 11:
        return html.Div(className="alert-box alert-warning", children=[
            html.Span("⚠️ "),
            "Por favor, informe um CPF válido com 11 dígitos numéricos."
        ]), current_store

    if not curso or not periodo:
        return html.Div(className="alert-box alert-warning", children=[
            html.Span("⚠️ "),
            "Por favor, selecione seu Curso e Turno na Seção 2."
        ]), current_store

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT nome, data_envio FROM respostas_pesquisa WHERE ra = ? OR cpf = ?", (ra_limpo, cpf_limpo))
    existente = cur.fetchone()

    if existente:
        nome_existente = existente["nome"]
        data_existente = existente["data_envio"]
        conn.close()
        return html.Div(className="alert-box alert-duplicate", children=[
            html.H4("🚫 Participação Já Registrada!", style={"margin": "0 0 6px 0", "color": "#991b1b"}),
            html.P(f"O estudante '{nome_existente}' (RA: {ra_limpo}) já respondeu a esta pesquisa em {data_existente}.", style={"margin": 0}),
            html.P("Conforme o regulamento da instituição, cada estudante pode participar apenas uma única vez.", style={"marginTop": "4px", "fontSize": "0.85rem", "color": "#475569"})
        ]), current_store

    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    try:
        cur.execute("""
        INSERT INTO respostas_pesquisa (
            ra, cpf, nome, senha_hash, data_envio, curso, periodo, cidade_reside,
            genero, data_nascimento, estado_civil, filhos, mora_com, moradores,
            situacao_domicilio, renda_familiar, trabalha, vinculo_trabalho, regime_trabalho,
            area_trabalho, plano_saude, escolaridade_mae, escolaridade_pai, vida_escolar,
            internet, smartphone, notebook, desktop, streaming, automovel, motocicleta,
            finalidade_escolar, finalidade_profissional, finalidade_entretenimento, finalidade_banco,
            expectativa_curso, expectativa_formar, motivo_escolha, historia_sonhos
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ra_limpo, cpf_limpo, str(nome).strip(), "", data_atual,
            str(curso or ""), str(periodo or ""), str(cidade or ""),
            str(genero or ""), str(nascimento or ""), str(civil or ""), str(filhos or ""),
            str(mora_com or ""), "Não informado", str(moradia_tipo or ""), str(renda or ""),
            str(trabalha or "Não"), str(vinculo or ""), "Não informado", str(area_trab or ""),
            "Não informado", "Não informado", "Não informado", str(escola or ""),
            str(internet or "Sim"), str(smartphone or "Sim"), str(notebook or "Sim"),
            str(desktop or "Não"), "Sim", "Não informado", "Não informado",
            "Sim", "Sim", "Sim", "Sim",
            str(exp_curso or ""), str(exp_formar or ""), str(motivo or ""), str(historia_sonhos or "")
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        conn.close()
        return html.Div(className="alert-box alert-danger", children=[
            html.Span("❌ Erro ao salvar dados: "),
            str(e)
        ]), current_store

    novo_df = carregar_dados_consolidados()
    novo_store = novo_df.to_json(date_format='iso', orient='split')

    return html.Div(className="alert-box alert-success", children=[
        html.H4("🎉 Pesquisa Enviada com Sucesso!", style={"margin": "0 0 6px 0", "color": "#065f46"}),
        html.P(f"Obrigado, {nome}! Suas respostas foram salvas no sistema e incorporadas ao painel de indicadores da FATEC Franca.", style={"margin": 0}),
        html.Div(style={"marginTop": "10px"}, children=[
            html.Span("Protocolo de Envio: ", style={"fontWeight": "600"}),
            html.Code(f"FATEC-{ra_limpo}-{datetime.now().strftime('%Y%m%d%H%M')}", style={"background": "#e2e8f0", "padding": "4px 8px", "borderRadius": "4px", "color": "#0284c7"})
        ])
    ]), novo_store

# =============================================================================
# CALLBACKS DE EXPORTAÇÃO
# =============================================================================
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-download-csv", "n_clicks"),
    State("dataset-store", "data"),
    prevent_initial_call=True
)
def export_csv(n_clicks, json_data):
    if not json_data:
        return None
    df = pd.read_json(StringIO(json_data), orient='split')
    return dcc.send_data_frame(df.to_csv, "fatec_pesquisa_completa.csv", index=False, encoding='utf-8-sig')

@app.callback(
    Output("download-dataframe-excel", "data"),
    Input("btn-download-excel", "n_clicks"),
    State("dataset-store", "data"),
    prevent_initial_call=True
)
def export_excel(n_clicks, json_data):
    if not json_data:
        return None
    df = pd.read_json(StringIO(json_data), orient='split')
    return dcc.send_data_frame(df.to_excel, "fatec_pesquisa_completa.xlsx", index=False, sheet_name="Respostas")

# =============================================================================
# INICIALIZAÇÃO
# =============================================================================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    print(f"\n=======================================================")
    print(f">> Fatec Pesquisa iniciado com sucesso!")
    print(f">> Modo Visualização Direta & Sem Pizza Ativo")
    print(f">> Acesse no navegador: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(
        debug=False,
        dev_tools_ui=False,
        dev_tools_props_check=False,
        dev_tools_silence_routes_logging=True,
        port=port
    )
