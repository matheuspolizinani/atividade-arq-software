# Mapa de restrições e decisões

Grupo 06 — Caso Ônibus (bilhetagem e mobilidade urbana) + Envelope E (operação sob fiscalização).

Cada linha liga uma restrição do envelope **ou** um requisito que aperta do caso à decisão que a atende, com o ADR e o diagrama que a sustentam. Nenhuma restrição fica sem decisão e nenhuma decisão fica sem restrição (regra da Entrega 2).

## Parte A — Restrições do envelope E

| # | Restrição do envelope | Decisão que a atende | ADR | Diagrama |
|---|---|---|---|---|
| E1 | Operação sob fiscalização; tudo precisa ser reconstruível | Núcleo Financeiro event-sourced (append-only) + trilha de auditoria alimentada pelos eventos do barramento | 0002, 0004 | contêineres, componentes |
| E2 | LGPD com direito ao esquecimento | Segmentação do dado pessoal: identidade civil por destruição criptográfica; elegibilidade regulatória pseudonimizada e retida; totais de conciliação preservados | 0008 | componentes |
| E3 | Nuvem pública com trilha de auditoria completa | Implantação em nuvem com entrega contínua; evento retido como trilha imutável; correlação e rastreamento distribuído | 0004 | contêineres |
| E4 | Equipe de 15 desenvolvedores, 1 de conformidade (sem time grande de operação) | Núcleo transacional em monólito modular; serviços só para os quanta exigidos; gateway e plataforma únicos; invariantes por funções de aptidão | 0009, 0004, 0012 | contêineres |
| E5 | Auditoria do Tribunal de Contas sobre o repasse | Repasse reconstruível por reprodução do fluxo; projeções de conciliação por CQRS | 0002 | componentes |

## Parte B — Requisitos que apertam do caso Ônibus

| # | Subdomínio / requisito que aperta | Decisão que a atende | ADR | Diagrama |
|---|---|---|---|---|
| C1 | Validação embarcada: resposta em até 300 ms mesmo sem rede | Decisão local no validador contra lista sincronizada; nada central no caminho da resposta | 0006 | contêineres |
| C2 | Validação embarcada: nunca aceitar a mesma passagem duas vezes | Fila local append-only assinada + deduplicação idempotente no servidor; duplicidade confirmada vira glosa compensatória | 0006, 0011 | contêineres |
| C3 | Cartões e recarga: saldo consistente com atraso de sincronização | Banco por serviço/esquema por módulo + saga com compensação e passos idempotentes; consistência eventual do saldo | 0009, 0002 | contêineres |
| C4 | Cartões e recarga: fraude de recarga zero e conciliação com o banco | Recarga conciliada contra o retorno do banco pelo adaptador anticorrupção; glosa de duplicidade impede subsídio em dobro | 0002, 0003, 0011 | contêineres |
| C5 | Telemetria: absorver 80 pos/s (5× no pico) sem perder dados nem derrubar o resto | Ingestão orientada a eventos; barramento como amortecedor; serviço isolado que escala sozinho; depuração Pipes and Filters a jusante para a fiscalização | 0009, 0004, 0010 | contêineres |
| C6 | Informação ao passageiro: pico no rush, custo baixo fora do pico | Projeção de leitura por CQRS, com réplicas que sobem no pico e recuam fora dele | 0002, 0004 | contêineres |
| C7 | Repasse: recalcular o mês com a regra de tarifa vigente na data de cada viagem | Event sourcing reprocessando o fluxo; regra tarifária como estratégia versionada por vigência | 0002, 0007 | componentes |
| C8 | Repasse: fechamento mensal auditável, contestação em até 30 dias | Fluxo imutável + projeções de conciliação reconstruíveis por reprodução | 0002 | componentes |
| C9 | Integração externa: formatos impostos e janelas de indisponibilidade | Adaptadores anticorrupção; chamadas com tempo limite, retentativa e disjuntor; integração assíncrona quando possível | 0003 | contêineres |
| C10 | Atendimento: trilha de auditoria de quem alterou o quê | Registro de eventos de alteração no módulo de conformidade + trilha imutável | 0004, 0008 | contêineres |
| C11 | Guarda de dados: histórico de viagens é dado pessoal sob a LGPD | Identidade civil cifrada por titular; elegibilidade pseudonimizada retida; financeiro em claro e não identificável | 0008 | componentes |

## Cobertura reversa (cada ADR atende ao menos uma restrição/requisito)

| ADR | Atende |
|---|---|
| 0001 — composição microsserviços + eventos *(substituído pelo 0009)* | E4, C3, C5 |
| 0002 — banco por serviço + event sourcing no financeiro | E1, E5, C3, C6, C7, C8 |
| 0003 — anticorrupção assíncrona com terceiros | C4, C9 |
| 0004 — nuvem, auditoria e observabilidade | E3, E4, C5, C6, C10 |
| 0005 — crypto-shredding (auditoria × esquecimento) *(substituído pelo 0008)* | E1, E2, C10, C11 |
| 0006 — validação offline + deduplicação | C1, C2 |
| 0007 — regra tarifária versionada por vigência | C7 |
| 0008 — segmentação identidade civil × elegibilidade regulatória | E2, C10, C11 |
| 0009 — núcleo transacional em monólito modular | E4, C3, C5 |
| 0010 — depuração da telemetria (Pipes and Filters) | C5 |
| 0011 — glosa compensatória de duplicidade | C2, C4 |
| 0012 — funções de aptidão na integração contínua | E4 |
