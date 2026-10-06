# CHANGELOG — Entrega 5 (versão final)

**Grupo 06 — Ônibus + Envelope E.**

Este arquivo registra **o que mudou por causa da leitura cruzada e por quê**. O Grupo 02 (Ônibus, envelope D) revisou o nosso projeto e enviou 7 objeções; respondemos a todas em [`4-leitura-cruzada/respostas-recebidas.md`](../4-leitura-cruzada/respostas-recebidas.md). Das 7, aceitamos 4 integralmente (03, 05, 06, 07) e 3 em parte (01, 02, 04).

Regra seguida: **ADR aceito não é editado — é substituído.** Mudanças que contradizem um ADR aceito entraram como ADR novo com status "substitui o ADR X"; mudanças que apenas refinam entraram como ADR novo que cita o anterior. A única edição feita em ADRs antigos foi a troca da linha de **Status** dos substituídos (0001 e 0005), conforme o ciclo de vida da seção 4.4 do livro.

---

## 1. ADRs adicionados

| ADR | Título | Origem (objeção) | Relação |
|---|---|---|---|
| [0007](../2-arquitetura/adr/0007-representar-regras-tarifarias-como-estrategia-versionada-por-vigencia.md) | Representar regras tarifárias como estratégia versionada por vigência | 02 | refina o ADR 0002 |
| [0008](../2-arquitetura/adr/0008-segmentar-dado-pessoal-em-identidade-civil-e-elegibilidade-regulatoria.md) | Segmentar dado pessoal em identidade civil e elegibilidade regulatória | 03 | **substitui o ADR 0005** |
| [0009](../2-arquitetura/adr/0009-consolidar-o-nucleo-transacional-em-monolito-modular.md) | Consolidar o núcleo transacional em monólito modular | 04 | **substitui o ADR 0001** |
| [0010](../2-arquitetura/adr/0010-depurar-telemetria-de-fiscalizacao-por-pipes-and-filters.md) | Depurar a telemetria de fiscalização por um pipeline Pipes and Filters | 05 | refina os ADRs 0001/0004 |
| [0011](../2-arquitetura/adr/0011-resolver-duplicidade-de-validacao-por-glosa-compensatoria.md) | Resolver duplicidade de validação por evento de glosa compensatória | 06 | refina os ADRs 0006/0002 |
| [0012](../2-arquitetura/adr/0012-impor-invariantes-de-arquitetura-por-funcoes-de-aptidao-no-ci.md) | Impor invariantes de arquitetura por funções de aptidão na integração contínua | 07 | refina o ADR 0004 |

## 2. ADRs substituídos (só a linha de Status mudou)

- **ADR 0001** → status "substituído pelo ADR 0009". Motivo: a objeção 04 e a nossa própria tensão honesta mostraram que 7 serviços cobram pedágio operacional desproporcional para 15 pessoas. O núcleo transacional passa a ser um monólito modular; permanecem como serviços só os quanta exigidos pelos requisitos (validador embarcado, telemetria, informação ao passageiro, núcleo financeiro).
- **ADR 0005** → status "substituído pelo ADR 0008". Motivo: a objeção 03 mostrou que cifrar o bloco pessoal inteiro apagava, no esquecimento, a prova de elegibilidade de gratuidade exigida pela auditoria de subsídio. O dado pessoal passa a ser segmentado em identidade civil (crypto-shredding) e elegibilidade regulatória (pseudonimizada, retida por base legal).

## 3. Código pequeno (Entrega 3)

- **`3-spike/exemplo.py`** reescrito para provar o **ADR 0008** (no lugar do 0005): o evento separa identidade civil (cifrada) de elegibilidade regulatória (pseudonimizada, em claro). A saída demonstra que, após o esquecimento, a identidade fica irrecuperável **mas o total de subsídio devido e a prova de elegibilidade permanecem**. 230 linhas, só biblioteca padrão, determinístico.
- **`3-spike/README.md`** atualizado (passa a referenciar o ADR 0008, com a linhagem a partir do 0005).
- **`3-spike/saida-esperada.txt`** regenerado a partir da nova saída (em LF).

## 4. Diagramas C4 (Entrega 2)

- **`c4-conteineres.png/.mmd`** (nível 2): o núcleo transacional virou um único contêiner **"Núcleo Transacional [Monólito modular]"** (ADR 0009); acrescentado o contêiner **"Depuração de Telemetria [Pipes and Filters]"** entre a ingestão e o barramento (ADR 0010).
- **`c4-componentes.png/.mmd`** (nível 3, Núcleo Financeiro): acrescentado o componente **"Catálogo de regras tarifárias (por vigência)"** (ADR 0007); o componente de cifra passou a **"Gestor de identidade (crypto-shredding)"** e o keystore guarda só a identidade (ADR 0008); o agregado passou a citar a **glosa de duplicidade** e o app publica o evento **Glosa** (ADR 0011); a projeção de leitura passou a conter **subsídio + elegibilidade**.

## 5. Documento de arquitetura (Entrega 2)

- Seção 2 (composição e fronteiras): tabela atualizada — o estilo geral passa a ser **monólito modular + serviços para os quanta exigidos** (ADR 0009); acrescentadas as linhas de Pipes and Filters (telemetria) e do padrão de regra tarifária versionada.
- Seção 6 (trade-offs): a "tensão honesta" passa a refletir a decisão final (consolidação no monólito modular).
- Seção 7.2: corrigida a redação que sugeria consulta online no embarque — a catraca autoriza **offline** contra a lista embarcada com teto de risco (objeção 01).
- Seção 7.3: acrescentado o pipeline de depuração da telemetria de fiscalização (ADR 0010).
- Seção 7.5: atualizada para o modelo de três blocos (identidade/elegibilidade/viagem) do ADR 0008.
- Seção 8 (decisão mais arriscada): passa a apontar o ADR 0008 (refinamento do crypto-shredding), ainda provado pelo spike.
- Acrescentada a Seção 7.6 (duplicidade e glosa, ADR 0011) e a menção às funções de aptidão (ADR 0012) na seção de operação.

## 6. Mapa de restrições e decisões (Entrega 2)

- Atualizado para referenciar os ADRs novos: C5 passa a citar o ADR 0010; C4/C2 o ADR 0011; C7 o ADR 0007; E2/C11 o ADR 0008; E4 o ADR 0009; e acrescentada uma linha de governança (funções de aptidão, ADR 0012).

## 7. Matriz (Entrega 1)

- Nota acrescentada: Microkernel e Pipes and Filters permanecem descartados **como estilo geral**, mas são usados **como padrões locais** (regra tarifária versionada; depuração da telemetria), conforme a distinção estilo × padrão da seção 2.2 (objeções 02 e 05).

---

### O que NÃO mudou (e por quê)

- **Event sourcing no Núcleo Financeiro, CQRS e barramento de eventos:** confirmados pela própria leitura cruzada; o recálculo por tarifa vigente na data já resolvia a preocupação retroativa da objeção 02 sem precisar do Microkernel como estilo.
- **Validação offline com dedup no servidor (ADR 0006):** mantida; a objeção 01 era de redação (corrigida na 7.2), não de mecanismo, e a objeção 06 foi acomodada pela glosa (ADR 0011) sem mudar a validação em si.
- **Modelo baseado em conta (não saldo em chip):** mantido deliberadamente, por ser mais auditável e reconstruível sob o Envelope E (resposta à objeção 01).
