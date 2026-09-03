# MVP - Construção de Pipeline de Dados: Monitoramento de Risco de Liquidez em Fundos de Investimento

### Contexto de Negócios e Perguntas (Etapa 2 e 4.1)
No ambiente de Corretoras de Valores, em especial nas frentes de *Compliance*, Controles Internos e Gestão de Riscos (como no contexto da Banrisul Corretora), o monitoramento contínuo da saúde financeira dos fundos de investimento ofertados aos clientes é uma exigência regulatória e estratégica. Um dos riscos mais sensíveis é o **Risco de Liquidez**, que ocorre quando um fundo sofre uma onda massiva de resgates (saques) em curto período, podendo comprometer a sua solvência e forçar a venda desfavorável de ativos.

O objetivo deste projeto acadêmico é projetar e construir, do zero, um pipeline de dados funcional em ambiente de nuvem, automatizando a extração, o tratamento, a modelagem e a análise de dados públicos de fundos para fornecer visibilidade rápida à equipe de riscos.

**Perguntas de Negócio norteadoras:**
1. Como estruturar um fluxo automatizado na nuvem para processar eficientemente o grande volume diário de informações financeiras publicadas pelos órgãos reguladores?
2. Qual é o comportamento do fluxo líquido diário (relação entre aportes e saques) nos fundos monitorados?
3. Quais fundos apresentaram uma taxa de resgate superior a 10% do seu Patrimônio Líquido em um único pregão, disparando um alerta de atenção para o controle interno?

**Sobre a Fonte dos Dados e Transparência:** 
Para assegurar o rigor acadêmico, foram utilizados dados reais e públicos disponibilizados pela **Comissão de Valores Mobiliários (CVM)**, através do conjunto de dados de **"Fundos de Investimento: Informes Diários"**.
*   **Licença:** Dados Abertos Governamentais (livre utilização para fins educacionais, de pesquisa e de mercado).
*   **Página Oficial para Consulta (Portal de Dados Abertos CVM):** [https://dados.cvm.gov.br/dataset/fi-doc-inf_diario](https://dados.cvm.gov.br/dataset/fi-doc-inf_diario)
*   **URL Direta do Arquivo Utilizado (Janeiro/2026):** `https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_202601.zip`

### Carga dos Dados (Etapa 4.2)
A ingestão foi realizada de forma programática. O pipeline em nuvem acessa diretamente via protocolo HTTP o link oficial da CVM, efetua o download do arquivo compactado (`.zip`) referente ao mês de janeiro de 2026, descompacta o conteúdo e o armazena no sistema de arquivos distribuído da nuvem (DBFS). Esse método garante reprodutibilidade total sem dependência de intervenções manuais locais.

*[Inserir Screenshot do bloco de código Python executando o download e extração dos dados da CVM no Databricks]*

### Modelagem e Catálogo de Dados (Etapa 4.3)
A organização dos dados seguiu o padrão de mercado **Arquitetura Medalhão** (Lakehouse), dividida em camadas lógicas:
*   **Camada Bronze:** Armazena o dado bruto tal qual disponibilizado na fonte oficial, servindo como histórico imutável.
*   **Camada Silver:** Destinada à higienização, conversão de tipos de dados (textos para números decimais), padronização temporal e expurgo de registros inconsistentes.
*   **Camada Gold:** Camada agregada e modelada, onde são aplicadas as regras de negócio de risco e compliance.

**Catálogo de Dados (Tabela de Consumo - Camada Gold)**
*   `CNPJ_FUNDO` (String): Identificador único nacional do fundo de investimento (Chave primária).
*   `DT_COMPTC` (Date): Data de competência ou referência da informação financeira.
*   `VL_PATRIM_LIQ` (Double): Patrimônio Líquido total do fundo no encerramento do dia.
*   `CAPTC_DIA` (Double): Montante financeiro total aportado pelos cotistas no dia.
*   `RESG_DIA` (Double): Montante financeiro total resgatado pelos cotistas no dia.
*   `FLUXO_LIQUIDO` (Double): Indicador calculado (`CAPTC_DIA` - `RESG_DIA`).
*   `TAXA_RESGATE_PL` (Double): Percentual do patrimônio líquido sacado no período (`RESG_DIA` / `VL_PATRIM_LIQ` * 100).

*[Inserir Screenshot da estrutura da tabela gerada no Databricks]*

### Pipeline de Dados (Etapa 4.4)
O processo de ETL (Extração, Transformação e Carga) foi orquestrado em um Notebook utilizando o motor de processamento distribuído Apache Spark (via PySpark), estruturando-se em:
1.  **Extract:** Leitura tabulada do arquivo CSV com separador de ponto e vírgula gerado pelo governo.
2.  **Transform:** Limpeza de linhas corrompidas e cálculo das métricas de fluxo e taxa de resgate.
3.  **Load:** Persistência dos dados processados em uma tabela virtual (*Temporary View* chamada `fundos_gold`), viabilizando consultas analíticas em SQL estruturado.

*[Inserir Screenshot do código PySpark em execução no Databricks]*

### Qualidade de Dados (Etapa 4.5 - Primeira Parte)
O processamento de bases governamentais reais exigiu etapas estritas de validação:
*   **Consistência de Tipos:** Os campos monetários e numéricos vieram originalmente em formato de texto (`String`). Foi aplicada a conversão para ponto flutuante de dupla precisão (`Double`).
*   **Completude:** Linhas sem preenchimento de CNPJ foram eliminadas via filtro (`dropna`) para evitar ruídos analíticos.
*   **Integridade Matemática:** Filtramos fundos com Patrimônio Líquido estritamente positivo para prevenir falhas de divisão por zero.

### Análise de Dados (Etapa 4.5 - Segunda Parte)
Com a camada Gold pronta, executamos consultas analíticas em SQL. Ao filtrar os fundos com `TAXA_RESGATE_PL > 10%` em um único dia, geramos um painel automatizado de alerta de liquidez, permitindo que a equipe de controle interno verifique preventivamente a situação dos ativos.

*[Inserir Screenshot do resultado da consulta SQL e do gráfico gerado no Databricks]*

### Autoavaliação
O desenvolvimento deste MVP proporcionou uma imersão valiosa no ciclo de vida dos dados em nuvem. Sendo um profissional focado em áreas de negócios, a transição para conceitos de engenharia de dados representou um desafio gratificante, superado com o suporte do ambiente integrado do Databricks. O objetivo foi plenamente alcançado. Como trabalhos futuros, destaca-se a automação da ingestão diária (D-1) via API e a conexão da camada Gold a uma ferramenta de Business Intelligence (BI).
