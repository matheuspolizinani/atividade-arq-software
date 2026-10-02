# Entrega 4b — Leitura cruzada: respostas às objeções recebidas

**Grupo autor:** Grupo 06 (Ônibus, envelope E)
**Grupo revisor:** Grupo 02 (Ônibus, envelope D)
**Material revisado:** nossa Entrega 2 (documento de arquitetura, mapa, ADRs) e Entrega 3 (spike).

Respondemos abaixo **cada uma das 7 objeções**, na ordem recebida. Para cada uma: o **veredito** (aceita, aceita parcialmente ou rebatida), o **argumento**, e — quando aceita — **o que muda na Entrega 5** (com o ADR novo ou substituto correspondente e o registro no CHANGELOG, conforme a regra: mudança que contradiz um ADR aceito exige um ADR novo que o substitua).

O Grupo 02 fez uma revisão forte e específica; quatro objeções expõem lacunas reais e são aceitas, duas são aceitas em parte com o núcleo válido separado da alternativa que não se sustenta no nosso envelope, e nenhuma é descartada sem argumento.

---

## Resposta à Objeção 01 — Offline por 4 h × consulta síncrona ao "dono do dado"

**Veredito: aceita parcialmente.** Aceitamos que a redação da Seção 7.2 (item 5) está **errada e contraditória**; rebatemos a alternativa proposta (saldo em chip).

**Sobre o acerto da objeção.** A frase "o saldo usado para autorizar o próximo uso consulta-se o dono do dado, nunca uma projeção atrasada" está mal escrita e, lida ao pé da letra, contradiz o ADR 0006, que é explícito: **no ônibus a autorização é offline**, contra a lista embarcada, em até 300 ms, sem nada central no caminho da resposta. Nunca foi intenção do projeto consultar a nuvem no embarque — isso seria fisicamente impossível sob a premissa C1 (4G intermitente, até 4 h sem rede), exatamente como a objeção aponta.

**O que o projeto de fato modela (e a 7.2 deveria ter dito).** A regra "ler o dono, não a projeção" vale para o **canal online** (o aplicativo mostrando saldo, ou autorizando uma recarga na tela), **não para a catraca**. No validador, a decisão usa o **último saldo/limite conhecido sincronizado na lista embarcada** (uma *cópia em cache*, não um segundo dono do dado) somada a um **teto de risco offline** (ADR 0006); a conciliação real acontece depois, na sincronização, por saga idempotente. O "dono do dado" continua sendo o Serviço de Cartões e Recarga como **fonte de verdade de registro** — o cache embarcado não o substitui, apenas adianta uma leitura tolerante a atraso dentro de um limite de risco.

**Por que rebatemos o "saldo em chip" (stored value).** A alternativa de guardar o saldo definitivo no chip é legítima e existe no mercado, mas **piora o que o Envelope E mais exige**: com dinheiro no cartão, o valor circula offline e a fonte de verdade vira o chip, o que dificulta a **auditoria e a reconstrutibilidade** (E1/E5) e aumenta a superfície de fraude por clonagem. O modelo **baseado em conta** (saldo central + cache embarcado com teto de risco) mantém um **registro central auditável** da operação, que é o que o Tribunal de Contas precisa reconstruir. Trocar por valor-no-cartão resolveria a latência que já resolvemos offline, ao custo de enfraquecer a auditoria — o oposto da prioridade do envelope.

**O que muda na Entrega 5.** Correção de redação (sem contradizer ADR): reescrever a Seção 7.2, item 5, deixando explícito que (a) a catraca autoriza **offline** contra a lista embarcada com teto de risco (ADR 0006); (b) a regra "ler o dono" vale só para o canal online; (c) o cache embarcado é cópia tolerante a atraso, não um segundo dono. Registro no CHANGELOG como ajuste de documentação. Nenhum ADR é substituído.

---

## Resposta à Objeção 02 — Descarte do Microkernel e decretos tarifários

**Veredito: aceita parcialmente.** Aceitamos o núcleo válido (regras tarifárias/subsídio precisam ser artefatos versionados por vigência, não código recompilado a cada decreto); rebatemos a adoção do **Microkernel como estilo geral** e a afirmação de que "cada decreto obriga a reimplementar o motor".

**Por que rebatemos parte.** A objeção confunde **estilo** e **padrão** (distinção do livro, Seção 2.2). Descartamos o Microkernel como **estilo arquitetural do sistema** porque o sistema não é centrado em plugins — e isso continua correto. Além disso, a afirmação de que sem Microkernel "todo o motor contábil é retestado e há risco de regressão em meses anteriores" **ignora o que o event sourcing já nos dá** (ADR 0002, resposta C7): o repasse aplica a **tarifa vigente na data de cada viagem**, e recalcular é **reprocessar o fluxo** com a regra histórica — os meses anteriores são reconstruídos com a regra que valia então, sem reescrever cálculo. Não há o risco de regressão retroativa que a objeção descreve, justamente porque a história é imutável.

**O que aceitamos (o núcleo válido).** O ponto legítimo é: **como as regras tarifárias são representadas?** Se estiverem embutidas no agregado, cada decreto vira alteração de código. Aceitamos tornar isso explícito e melhor: a `RegraTarifaria` passa a ser uma **estratégia versionada e delimitada por data de vigência**, resolvida pelo agregado conforme a data do evento — um novo decreto **adiciona uma nova versão de regra (configuração/estratégia), sem tocar o motor de liquidação**. Isso é o uso do mecanismo de plugin **como padrão dentro de um serviço**, não a adoção do Microkernel como estilo — e é plenamente compatível com o event sourcing.

**O que muda na Entrega 5.** Novo **ADR 0007 — "representar regras tarifárias e de subsídio como estratégia versionada por vigência"**, que **refina o ADR 0002** (não o contradiz). O nível 3 (componentes do Núcleo Financeiro) passa a mostrar um componente "Catálogo de regras tarifárias (por vigência)" consultado pelo agregado. Registro no CHANGELOG. A matriz mantém o Microkernel descartado **como estilo**, com nota de que o mecanismo de plugin é usado localmente como padrão.

---

## Resposta à Objeção 03 — Crypto-shredding apaga a prova de gratuidade pública

**Veredito: aceita.** É a objeção mais forte e expõe uma falha real.

**Por que aceitamos.** O ADR 0005 e o spike cifram o **bloco pessoal inteiro** (incluindo, na prática, o status de elegibilidade) com a chave do titular. Como 25% das viagens são gratuidade/desconto subsidiado, e o Tribunal de Contas audita **se o passageiro tinha direito ao subsídio na data do evento**, destruir a chave no esquecimento apagaria também a **prova de elegibilidade** — e a operadora não conseguiria comprovar que a viagem subsidiada foi legítima. A objeção está certa: o binário "financeiro em claro / pessoal cifrado" é grosso demais, porque mistura **identidade civil** (dado pessoal sujeito a esquecimento) com **atributo regulatório de elegibilidade** (dado cuja retenção tem **base legal/regulatória própria** sob a LGPD, art. 7º e art. 16 — conservação para cumprimento de obrigação legal/regulatória).

**O que aceitamos fazer (próximo ao que o Grupo 02 propôs).** Segmentar o dado pessoal em três níveis:
1. **Identidade civil** (nome, CPF, foto, contato) → cifrada por titular, destruída no esquecimento (crypto-shredding, como já era).
2. **Elegibilidade regulatória** (tipo de benefício — idoso/estudante/PcD —, número do cartão social, entidade emissora, cota) → mantida **em claro, pseudonimizada por identificador opaco** no evento contábil, retida sob base legal/regulatória, **sem** vínculo reversível à identidade após o shredding.
3. **Dados da viagem e linha** → em claro.

Assim, ao destruir a chave, o cidadão **deixa de ser identificável** (LGPD cumprida), mas permanece a prova de que "um portador de benefício ativo do tipo X fez esta viagem" — suficiente para a auditoria de subsídio.

**O que muda na Entrega 5.** Novo **ADR 0008 — "segmentar dado pessoal em identidade civil (crypto-shredding) e elegibilidade regulatória (pseudonimizada, retida por obrigação legal)"**, com status **"substitui o ADR 0005"** (porque altera a decisão de dados do 0005). Atualização do **spike (Entrega 3)**: separar `identidade` (cifrada) de `elegibilidade` (pseudonimizada em claro) e mostrar que, após destruir a chave, o total de repasse **e** a prova de elegibilidade sobrevivem. Atualização da Seção 7.5 e do nível 3. Registro no CHANGELOG.

---

## Resposta à Objeção 04 — 7 microsserviços para 15 devs + 1 de conformidade

**Veredito: aceita parcialmente.** Aceitamos reduzir a contagem consolidando o núcleo transacional em monólito modular; mantemos separados apenas os quanta que os requisitos exigem.

**Por que aceitamos.** A objeção reforça a nossa própria "tensão honesta" (Seção 6) e a recomendação de Fowler (monolito primeiro, Seção 9.6). Para 15 pessoas com 1 de conformidade, operar 7 unidades distribuídas — CI próprio, contratos versionados, tracing, disjuntores, sagas — cobra um pedágio desproporcional (Seção 9.7) e aumenta o risco de não-conformidade sob fiscalização. Concordamos que o núcleo **transacional** não precisa ser distribuído.

**O que aceitamos fazer.** Consolidar em **um monólito modular** (Capítulo 6), com **esquemas separados por módulo** (para preservar a futura extração por strangler), os subdomínios: **Validação (lado servidor), Cartões e Recarga, Integração e Conformidade, Atendimento**. Permanecem como **quanta próprios porque o requisito obriga**, não por moda:
- **Validador embarcado** — unidade de borda, offline (C1/C2); não é "serviço de nuvem", é edge.
- **Telemetria** — carga extrema e sazonal que precisa escalar e falhar isolada (C5).
- **Informação ao Passageiro** — pico público sazonal, leitura CQRS (C6).
- **Núcleo Financeiro** — event sourcing, persistência e auditoria distintas (C7/C8/E1/E5).

Isso reduz de ~7 para **1 núcleo modular + 3 serviços + o validador de borda + o gateway**, aliviando a operação sem perder o isolamento onde os atributos divergem de verdade.

**O que muda na Entrega 5.** Novo **ADR 0009 — "consolidar o núcleo transacional em monólito modular, mantendo como serviços só os quanta exigidos pelos requisitos"**, com status **"substitui o ADR 0001"**. Atualização dos diagramas C4 (níveis 2 e 3) e da Seção 6. Registro no CHANGELOG.

---

## Resposta à Objeção 05 — Telemetria sem duto de contrapressão/limpeza para fiscalização

**Veredito: aceita.** (com uma distinção que preservamos)

**Por que aceitamos.** A Seção 7.3 respondeu à pergunta de **escala** (Q3): isolar a telemetria e amortecer o pico. Mas a objeção está certa de que, no Envelope E, a telemetria também é **prova de fiscalização** (multar atraso/desvio), e dado de GPS cru contém reflexões em desfiladeiros urbanos, lacunas de túnel e ruído. Alimentar a fiscalização com posições não depuradas pode gerar "veículos fantasma" e multas contestáveis. A nossa própria matriz já marcava Pipes and Filters como "em parte" para processamento de telemetria — a objeção mostra onde ele é necessário.

**O que aceitamos fazer.** Inserir, **entre a ingestão e o sumidouro de fiscalização**, um pipeline **Pipes and Filters** (Capítulo 16): validação geoespacial, remoção de ruído/outliers e reconciliação temporal com a grade horária oficial; contrapressão no conector de fluxo. Só as posições depuradas alimentam a fiscalização e as projeções.

**A distinção que preservamos (rebate parcial de um detalhe).** A **ingestão** continua simples e assíncrona — é isso que garante a escala da Q3; o pipeline de limpeza fica **a jusante**, como consumidor. E o **fluxo cru permanece retido (append-only)** para auditoria, porque um auditor pode exigir o dado bruto, não só o depurado. Ou seja: cru retido para auditoria + projeção depurada para fiscalização.

**O que muda na Entrega 5.** Novo **ADR 0010 — "depurar a telemetria de fiscalização por um pipeline Pipes and Filters, retendo o fluxo cru para auditoria"** (refina o ADR 0001/0004, não contradiz). Atualização do nível 2 (consumidor de telemetria) e da Seção 7.3. Registro no CHANGELOG.

---

## Resposta à Objeção 06 — Duplicidade tratada como "suspeita" sem estorno contábil

**Veredito: aceita.** (ancorando a regra para não punir baldeação legítima)

**Por que aceitamos.** A objeção aponta uma lacuna real: a Seção 7.1 (item 6) e o ADR 0006 **detectam** a duplicata, mas não fecham a questão **financeira** — qual operadora recebe, e a prefeitura paga subsídio em dobro? Deixar a colisão como "suspeita" em aberto transfere risco de fraude aos cofres públicos e fere o requisito C4 ("fraude zero e conciliação"). Precisa haver resolução contábil automática.

**O que aceitamos fazer.** Na consolidação, uma duplicata **confirmada** gera um **evento contábil compensatório (glosa)** no Núcleo Financeiro: a **primeira viagem** (por carimbo de tempo/ordem no fluxo) é liquidada como legítima; a **segunda é retida** (não paga nem subsidiada em dobro); o cartão entra na **denylist distribuída à frota** na próxima sincronização. Como é event sourcing, a glosa é um **evento novo**, nunca uma sobrescrita — preservando a trilha.

**A âncora que acrescentamos (lição da nossa própria revisão).** A confirmação de duplicidade usa **impossibilidade física** (velocidade implausível entre as duas validações) **combinada com a regra de integração tarifária**, para **não glosar baldeação legítima** — exatamente o falso positivo que nós mesmos apontamos ao revisar outro grupo. Dois débitos próximos em ônibus diferentes só viram glosa quando a distância/tempo é fisicamente impossível, não quando são uma baldeação válida.

**O que muda na Entrega 5.** Novo **ADR 0011 — "resolver duplicidade de validação por evento de glosa compensatória, ancorado em impossibilidade física e regra de integração"** (refina ADR 0006 e ADR 0002). Atualização das Seções 7.1 e do mapa (C2/C4). Registro no CHANGELOG.

---

## Resposta à Objeção 07 — Ausência de funções de aptidão no CI

**Veredito: aceita.**

**Por que aceitamos.** A objeção está correta e é sustentada pelo próprio livro (funções de aptidão, Seções 4.8 e 19.6): o ADR 0004 cobriu observabilidade em **runtime**, mas não **testes executáveis de arquitetura** que barrem o build. Com 1 pessoa de conformidade para 15 devs, confiar só em revisão humana deixa a deriva arquitetural acontecer na primeira entrega sob prazo. Funções de aptidão são o mecanismo certo para proteger os invariantes que mais importam ao Envelope E.

**O que aceitamos fazer.** Adicionar ao pipeline de integração contínua, como funções de aptidão que **reprovam o build**:
1. **Isolamento de dados** — analisador estático (import-linter/ArchUnit) que proíbe acesso de um módulo/serviço ao banco de outro, preservando o banco-por-serviço/esquema-por-módulo.
2. **Caminho de 300 ms** — proibição de chamadas de rede síncronas dentro do módulo embarcado de validação.
3. **Imutabilidade do event store** — verificador que garante ausência de `UPDATE`/`DELETE` mapeados sobre a tabela de eventos.
4. (Já tínhamos) o **verificador de ADRs** do Capítulo 4.8, que os nossos ADRs já passam.

**O que muda na Entrega 5.** Novo **ADR 0012 — "impor invariantes de arquitetura por funções de aptidão na integração contínua"** (refina ADR 0004). As funções entram no repositório e no pipeline; o CHANGELOG registra. Opcionalmente, um segundo spike pequeno pode demonstrar uma das funções reprovando um commit que quebra o isolamento.

---

## Quadro-resumo (para a Entrega 5)

| # | Objeção | Veredito | Ação na Entrega 5 | ADR |
|---|---|---|---|---|
| 01 | Offline × "dono do dado" | Aceita parcial | Corrigir redação da 7.2 (autorização offline por cache + teto de risco); manter conta central | — (doc) |
| 02 | Microkernel / decretos | Aceita parcial | Regra tarifária como estratégia versionada por vigência | ADR 0007 (refina 0002) |
| 03 | Crypto-shredding × gratuidade | Aceita | Segmentar identidade civil × elegibilidade regulatória; atualizar spike | ADR 0008 (**substitui 0005**) |
| 04 | 7 serviços p/ 15 devs | Aceita parcial | Núcleo transacional em monólito modular; manter quanta exigidos | ADR 0009 (**substitui 0001**) |
| 05 | Telemetria sem pipeline | Aceita | Pipes and Filters a jusante; reter cru p/ auditoria | ADR 0010 (refina 0001/0004) |
| 06 | Duplicidade sem estorno | Aceita | Glosa compensatória ancorada em impossibilidade física | ADR 0011 (refina 0006/0002) |
| 07 | Sem funções de aptidão | Aceita | Funções de aptidão no CI (isolamento, 300 ms, imutabilidade) | ADR 0012 (refina 0004) |

**Conclusão.** Das 7 objeções, 4 são aceitas integralmente (03, 05, 06, 07) e 3 em parte (01, 02, 04), separando o ponto válido da alternativa que não se sustenta no Envelope E. Nenhuma foi descartada sem argumento. As mudanças aceitas entram na versão final (Entrega 5), registradas no CHANGELOG; as que alteram decisões de ADRs aceitos (03 e 04) entram como ADRs novos com status "substitui o ADR X", e as demais como ADRs que refinam os existentes.
