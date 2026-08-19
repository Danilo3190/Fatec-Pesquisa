# 🎓 Fatec Pesquisa

Plataforma integrada de **Inteligência de Dados e Coleta de Pesquisas Acadêmicas** desenvolvida em **Python (Dash, Plotly & SQLite)** para a **Faculdade de Tecnologia de Franca (FATEC Franca - Dr. Thomaz Novelino)**.

---

## 🚀 Arquitetura Visual: Clique e Veja

### 1. 🏛️ Cards de Cursos no Topo (ADS, DSM, GPI, GRH, GE e Geral)
* O usuário clica no **Card do Curso** desejado para focar exclusivamente nos dados dele.
* Cada card exibe em tempo real o número de alunos respondentes, modalidade e turnos.

---

### 2. 🗂️ Catálogo Visual de Perguntas (Sem menus suspensos confusos)
Todas as perguntas da pesquisa estão organizadas em **botões visuais e clicáveis por categoria**:
* **👤 Perfil & Dados Pessoais**: *Turno*, *Cidade*, *Gênero*, *Faixa Etária*, *Histórico Escolar*, *Estado Civil*, *Filhos*.
* **🏠 Renda & Condição Familiar**: *Faixa de Renda*, *Situação do Domicílio*, *Com Quem Mora*, *Pessoas na Residência*, *Escolaridade da Mãe/Pai*.
* **💼 Mercado de Trabalho & Carreira**: *Trabalha Atualmente?*, *Tipo de Vínculo (CLT/Estágio)*, *Área do Curso*, *Regime*, *Plano de Saúde*.
* **💻 Acesso à Tecnologia & Bens**: *Painel Geral de Equipamentos*, *Internet*, *Smartphone*, *Notebook*, *Desktop*, *Automóvel*, *Motocicleta*, *Streaming*.
* **🎯 Finalidades de Uso da Tecnologia**: *Trabalhos Escolares*, *Profissionais*, *Entretenimento*, *Operações Bancárias*.
* **☁️ Expectativas, Motivações & Sonhos**: *Nuvem de Sonhos*, *Expectativa do Curso*, *Expectativa Pós-Formatura*, *Motivo da Escolha*.
* **📋 Tabela de Respostas do Curso**: *Listagem individual e botões para exportar em Excel e CSV*.

---

### 3. 💡 Leitura Fácil dos Resultados
* Ao clicar em qualquer botão de pergunta, o gráfico é gerado instantaneamente logo abaixo com:
  * Rótulos diretos (`XX% (YY alunos)`)
  * Card explicativo em português claro (*💡 Leitura Fácil dos Resultados*)
  * Tabela resumo de frequências.

---

## 💻 Como Executar

1. Dê dois cliques no arquivo:
   👉 **`iniciar_dashboard.bat`**
2. Acesse no navegador:
   👉 **[http://127.0.0.1:8050](http://127.0.0.1:8050)**
