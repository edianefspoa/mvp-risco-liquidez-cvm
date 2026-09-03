# Databricks notebook source
# Camada Bronze: Leitura dos dados brutos da CVM salvos no Unity Catalog Volume
caminho_arquivo = "/Volumes/mvp/default/mvp/inf_diario_fi_202601.csv"

df_bronze = spark.read.csv(caminho_arquivo, sep=";", header=True, inferSchema=True)

print("--- CAMADA BRONZE (DADOS BRUTOS ORIGINAIS DA CVM) ---")
# Dica: Tire o print desta tabela para a evidência da Camada Bronze no seu relatório!
display(df_bronze)

# COMMAND ----------

from pyspark.sql.functions import col, to_date

# Camada Silver: Validação usando o nome correto da coluna da CVM e conversão de datas
df_silver = df_bronze.dropna(subset=["CNPJ_FUNDO_CLASSE"]) \
    .withColumn("DT_COMPTC", to_date(col("DT_COMPTC"), "yyyy-MM-dd"))

print("--- CAMADA SILVER (DADOS HIGIENIZADOS E PADRONIZADOS) ---")
display(df_silver)

# COMMAND ----------

from pyspark.sql.functions import col

# Camada Gold: Regras de negócio de liquidez (Fluxo Líquido e Taxa de Resgate sobre o PL)
df_gold = df_silver.withColumn("FLUXO_LIQUIDO", col("CAPTC_DIA") - col("RESG_DIA")) \
    .filter(col("VL_PATRIM_LIQ") > 0) \
    .withColumn("TAXA_RESGATE_PL", (col("RESG_DIA") / col("VL_PATRIM_LIQ")) * 100)

# Criação da tabela virtual (Temporary View) para consulta SQL posterior
df_gold.createOrReplaceTempView("fundos_gold")

print("--- CAMADA GOLD (INDICADORES DE RISCO CALCULADOS) ---")
# Dica: Tire o print desta tabela para a evidência da Camada Gold no seu relatório!
display(df_gold)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Consulta SQL para o painel de alerta de risco de liquidez (> 10% de resgate do PL)
# MAGIC SELECT 
# MAGIC   CNPJ_FUNDO_CLASSE, 
# MAGIC   DT_COMPTC as Data_Referencia, 
# MAGIC   VL_PATRIM_LIQ as Patrimonio_Liquido, 
# MAGIC   RESG_DIA as Volume_Resgatado, 
# MAGIC   ROUND(TAXA_RESGATE_PL, 2) as Taxa_Saque_Percentual
# MAGIC FROM fundos_gold
# MAGIC WHERE TAXA_RESGATE_PL > 10 
# MAGIC ORDER BY TAXA_RESGATE_PL DESC