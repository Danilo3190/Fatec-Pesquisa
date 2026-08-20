# -*- coding: utf-8 -*-
"""
Script de Geração de Dados de Demonstração para a FATEC Franca
Insere registros realistas para os cursos DSM, GPI, GRH e GE no SQLite.
"""

import sqlite3
import random
from datetime import datetime

DB_FILE = "fatec_pesquisa.db"

NOMES = [
    "Lucas Oliveira", "Beatriz Santos", "Gabriel Lima", "Mariana Costa", "Matheus Ribeiro",
    "Larissa Ferreira", "Felipe Almeida", "Camila Martins", "Guilherme Souza", "Juliana Rocha",
    "Rodrigo Silva", "Aline Pereira", "Bruno Barbosa", "Fernanda Dias", "Gustavo Carvalho",
    "Isabela Gomes", "Leonardo Castro", "Carolina Moreira", "Thiago Cardoso", "Patricia Ramos",
    "Rafael Duarte", "Amanda Teixeira", "Vinicius Nunes", "Bruna Mendes", "Diego Freitas",
    "Leticia Borges", "Eduardo Correia", "Vanessa Pinto", "Alexandre Neves", "Natalia Monteiro",
    "Caio Pacheco", "Bianca Antunes", "Henrique Caldeira", "Jessica Nogueira", "Lucas Marcondes",
    "Renata Camargo", "Fabio Guimaraes", "Luana Valente", "Murilo Siqueira", "Tatiane Farias"
]

CIDADES = ["Franca", "Franca", "Franca", "Franca", "Patrocínio Paulista", "Restinga", "Cristais Paulista", "Ribeirão Corrente", "Claraval", "Itirapuã", "Batatais", "São Tomás de Aquino"]

RENDAS = [
    "De R$ 1.518,01 até R$ 3.036,00", "De R$ 1.518,01 até R$ 3.036,00",
    "De R$ 3.036,01 até R$ 5.000,00", "Até R$ 1.518,00", "Mais de R$ 5.000,00"
]

ESCOLAS = [
    "Sempre na escola pública", "Sempre na escola pública",
    "Maior parte na escola pública", "Sempre em escola particular"
]

ESTADOS_CIVIS = ["Solteiro(a)", "Solteiro(a)", "Solteiro(a)", "Casado(a)", "Divorciado(a)"]
MORAS = ["Com os pais", "Com os pais", "Com cônjuge / filhos", "Sozinho", "Com amigos / república"]
DOMICILIOS = ["Próprio", "Próprio", "Financiado", "Alugado", "Alugado", "Cedido"]

SONHOS_POR_CURSO = {
    "Desenvolvimento de Software Multiplataforma (DSM)": [
        "Quero me tornar um desenvolvedor full-stack e criar aplicativos móveis inovadores com inteligência artificial.",
        "Meu sonho é trabalhar remotamente para grandes empresas de tecnologia e liderar equipes de software.",
        "Desejo me especializar em computação em nuvem e arquitetura de sistemas multiplataforma modernos.",
        "Busco adquirir conhecimento prático para empreender no mercado de tecnologia e criar minha própria startup.",
        "Minha meta é atuar na área de engenharia de software e desenvolver soluções que impactem positivamente a sociedade."
    ],
    "Gestão da Produção Industrial (GPI)": [
        "Pretendo atuar na otimização de linhas de produção industrial e implementar práticas de Lean Manufacturing.",
        "Meu objetivo é me tornar gerente de operações em indústrias e melhorar processos logísticos e de qualidade.",
        "Desejo aplicar automação e sustentabilidade nos processos produtivos das empresas da região de Franca.",
        "Sonho em liderar projetos industriais de grande porte com foco em redução de desperdícios e alta produtividade.",
        "Quero conquistar uma carreira sólida em engenharia de produção e gestão da cadeia de suprimentos."
    ],
    "Gestão de Recursos Humanos (GRH)": [
        "Minha meta é trabalhar no desenvolvimento de pessoas, recrutamento estratégico e clima organizacional humanizado.",
        "Sonho em atuar como consultora de RH e transformar a cultura corporativa das empresas.",
        "Quero me especializar em treinamento e desenvolvimento de lideranças para potencializar talentos.",
        "Desejo liderar departamentos de Recursos Humanos com foco em bem-estar e gestão estratégica de equipes.",
        "Busco aprimorar processos de atração de talentos e valorização dos colaboradores nas organizações."
    ],
    "Gestão Empresarial (GE)": [
        "Pretendo abrir meu próprio negócio e aplicar estratégias modernas de gestão corporativa e marketing.",
        "Meu objetivo é atuar em consultoria estratégica de negócios, planejamento financeiro e inovação.",
        "Sonho em alcançar cargos de alta gestão em empresas multinacionais com visão global de mercado.",
        "Desejo liderar transformações digitais e novos modelos de negócios escaláveis.",
        "Quero administrar empresas com excelência operacional, finanças sólidas e visão empreendedora."
    ]
}

def popular_banco():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    contador = 1000
    cursos_config = [
        ("Desenvolvimento de Software Multiplataforma (DSM)", "Noite", 42, "DSM"),
        ("Gestão da Produção Industrial (GPI)", "Noite", 38, "GPI"),
        ("Gestão de Recursos Humanos (GRH)", "Manhã", 40, "GRH"),
        ("Gestão Empresarial (GE)", "EaD", 45, "GE")
    ]
    
    total_inseridos = 0
    for curso_nome, turno_padrao, qtd_alunos, sigla in cursos_config:
        for i in range(qtd_alunos):
            contador += 1
            ra = f"279{sigla}{contador:05d}"
            cpf = f"{random.randint(100, 999)}{random.randint(100, 999)}{random.randint(100, 999)}{random.randint(10, 99)}"
            nome = f"{random.choice(NOMES)} {chr(65 + (i % 26))}."
            ano_nasc = random.randint(1996, 2006)
            mes_nasc = random.randint(1, 12)
            dia_nasc = random.randint(1, 28)
            nasc_str = f"{dia_nasc:02d}/{mes_nasc:02d}/{ano_nasc}"
            
            cidade = random.choice(CIDADES)
            genero = random.choice(["Masculino", "Feminino", "Masculino" if sigla in ["DSM", "GPI"] else "Feminino"])
            turno = turno_padrao if sigla in ["DSM", "GPI", "EaD"] else random.choice(["Manhã", "Noite"])
            
            trabalha = random.choice(["Sim", "Sim", "Sim", "Não"])
            vinculo = random.choice(["Sou registrado(a) no comércio", "Estágio", "Autônomo", "Servidor Público"]) if trabalha == "Sim" else "Não trabalho"
            area_trab = "Trabalho na área do curso" if (trabalha == "Sim" and random.random() > 0.4) else ("Trabalho em outra área" if trabalha == "Sim" else "Não se aplica")
            
            sonho = random.choice(SONHOS_POR_CURSO[curso_nome])
            data_envio = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            try:
                cur.execute("""
                INSERT OR IGNORE INTO respostas_pesquisa (
                    ra, cpf, nome, senha_hash, data_envio, curso, periodo, cidade_reside,
                    genero, data_nascimento, estado_civil, filhos, mora_com, moradores,
                    situacao_domicilio, renda_familiar, trabalha, vinculo_trabalho, regime_trabalho,
                    area_trabalho, plano_saude, escolaridade_mae, escolaridade_pai, vida_escolar,
                    internet, smartphone, notebook, desktop, streaming, automovel, motocicleta,
                    finalidade_escolar, finalidade_profissional, finalidade_entretenimento, finalidade_banco,
                    expectativa_curso, expectativa_formar, motivo_escolha, historia_sonhos
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ra, cpf, nome, "", data_envio,
                    curso_nome, turno, cidade,
                    genero, nasc_str, random.choice(ESTADOS_CIVIS), random.choice(["Nenhum", "Nenhum", "1", "2"]),
                    random.choice(MORAS), str(random.randint(2, 5)), random.choice(DOMICILIOS), random.choice(RENDAS),
                    trabalha, vinculo, "Presencial", area_trab,
                    random.choice(["Sim", "Não", "Sim"]), "Ensino Médio Completo", "Ensino Médio Completo", random.choice(ESCOLAS),
                    "Sim", "Sim", "Sim" if random.random() > 0.15 else "Não",
                    "Sim" if random.random() > 0.6 else "Não", "Sim", "Sim" if random.random() > 0.4 else "Não",
                    "Sim" if random.random() > 0.7 else "Não",
                    "Sim", "Sim", "Sim", "Sim",
                    "Adquirir conhecimentos práticos e teóricos de ponta para o mercado.",
                    "Atuar profissionalmente em grandes empresas ou empreender com sucesso.",
                    "Pela excelente reputação, qualidade do ensino e gratuidade da FATEC Franca.",
                    sonho
                ))
                total_inseridos += 1
            except Exception as e:
                pass
                
    conn.commit()
    conn.close()
    print(f"Total de {total_inseridos} registros de demonstração gerados com sucesso!")

if __name__ == '__main__':
    popular_banco()
