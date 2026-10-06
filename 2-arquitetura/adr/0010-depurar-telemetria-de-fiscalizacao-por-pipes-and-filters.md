# ADR 0010: depurar a telemetria de fiscalização por um pipeline Pipes and Filters

**Status:** aceito

**Contexto:** A resposta à pergunta de escala (seção 7.3) tratou a telemetria como ingestão simples que publica `PosicaoRecebida` no barramento, amortecendo o pico. A leitura cruzada (objeção 05 do Grupo 02) lembrou que, no envelope E, a telemetria também é prova de fiscalização usada para multar operadoras por atraso e desvio de rota, e que o GPS cru contém reflexões em desfiladeiros urbanos, lacunas de túnel e ruído. Alimentar a fiscalização com posições não depuradas produz "veículos fantasma" e multas contestáveis. A matriz já marcava Pipes and Filters como "em parte" para processamento de telemetria. Este ADR refina os ADRs 0001 e 0004.

**Decisão:** Inserir, a jusante da ingestão, um pipeline **Pipes and Filters** (capítulo 16) com filtros de validação geoespacial, remoção de ruído e reconciliação temporal com a grade horária oficial da concessão, e contrapressão no conector de fluxo. Apenas as posições depuradas alimentam a fiscalização e as projeções de monitoramento; o fluxo cru é retido em modo append-only para auditoria. A ingestão permanece simples e assíncrona, preservando a escala da seção 7.3.

**Alternativas consideradas:**
- Publicar o GPS cru direto para a fiscalização: descartada por gerar veículo fantasma e multa juridicamente contestável.
- Filtrar na própria ingestão: descartada por acoplar a limpeza à escala e comprometer a absorção do pico (requisito C5).
- Descartar o fluxo cru após filtrar: descartada porque o auditor pode exigir o dado bruto, não só o depurado.

**Consequências:**
- Positivas: a fiscalização passa a decidir sobre dado válido; a escala da ingestão é preservada; o fluxo cru continua auditável.
- Negativas: mais um estágio a operar e monitorar; latência adicional até a projeção de fiscalização; as regras de limpeza viram artefato a versionar e validar.
