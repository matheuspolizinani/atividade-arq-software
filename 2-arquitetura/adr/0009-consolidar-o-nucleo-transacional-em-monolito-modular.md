# ADR 0009: consolidar o núcleo transacional em monólito modular

**Status:** aceito

**Contexto:** O ADR 0001 adotou microsserviços por subdomínio, resultando em sete unidades implantáveis. A leitura cruzada (objeção 04 do Grupo 02) e a própria "tensão honesta" do documento de arquitetura apontam que, para 15 desenvolvedores e 1 responsável por conformidade, operar sete unidades distribuídas — CI próprio, contratos versionados, tracing, disjuntores e sagas — cobra um pedágio desproporcional (seção 9.7) e aumenta o risco de não-conformidade sob fiscalização. Fowler recomenda monolito primeiro, com boa modularidade interna (seção 9.6). Substitui o ADR 0001.

**Decisão:** Consolidar o núcleo transacional (Validação no lado servidor, Cartões e Recarga, Integração e Conformidade, Atendimento) em um **monólito modular** com esquemas separados por módulo, usando transação local onde cabe. Permanecem como quanta próprios apenas as unidades cujo requisito exige: **Validador embarcado** (borda, offline — C1/C2), **Telemetria** (carga extrema e sazonal — C5), **Informação ao Passageiro** (pico público, leitura CQRS — C6) e **Núcleo Financeiro** (event sourcing e auditoria — C7/C8/E1/E5). O barramento de eventos continua o conector entre as unidades; o interior segue hexagonal; os esquemas separados preservam a extração futura por estrangulamento.

**Alternativas consideradas:**
- Manter os sete microsserviços (decisão original do ADR 0001): descartada pelo pedágio operacional desproporcional para uma equipe de 15 pessoas.
- Monólito único total, inclusive validação embarcada e telemetria: descartada porque o validador é offline por natureza e a telemetria e o financeiro precisam de isolamento de carga e de persistência próprios.
- Microsserviços por camada técnica: descartada por produzir monolito distribuído (seção 9.6).

**Consequências:**
- Positivas: menos esteiras, credenciais, painéis e sagas para operar; transação local atômica no núcleo transacional; isolamento preservado onde os atributos de qualidade divergem de verdade.
- Negativas: o monólito modular pode re-acoplar se a disciplina de fronteira falhar — mitigado pelos esquemas separados e pelas funções de aptidão do ADR 0012; extrair um módulo para serviço no futuro ainda custa contrato e migração.
