# ADR 0001: compor microsserviços por subdomínio com espinha dorsal de eventos

**Status:** aceito

**Contexto:** O sistema reúne subdomínios com atributos de qualidade divergentes: a validação embarcada é tempo real, precisa responder em até 300 ms e opera até 4 horas sem rede; a telemetria é fluxo contínuo, com 80 posições por segundo em média e cinco vezes isso no pico; o repasse é lote mensal auditável, que recalcula o mês inteiro; a informação ao passageiro é analítica e tolera atraso. O envelope E impõe operação sob fiscalização, com trilha de auditoria completa e direito ao esquecimento da LGPD, e a equipe é de 15 desenvolvedores com 1 responsável por conformidade. Segundo a seção 2.5, a fronteira do quantum arquitetural é onde os requisitos podem divergir, e aqui eles divergem por subdomínio.

**Decisão:** Repartir o sistema em microsserviços alinhados a contextos delimitados (capítulo 9), usando o barramento de eventos como conector padrão entre eles (capítulo 11) e reservando a chamada síncrona para quando a resposta é necessária na hora. O interior de cada serviço segue a arquitetura hexagonal (capítulo 7); o Núcleo Financeiro segue event sourcing com CQRS (ADR 0002). Para não pulverizar além do que 15 pessoas operam, os subdomínios de baixo volume (atendimento, gratuidade, conformidade) ficam como módulos de um único serviço, e não como serviços próprios.

**Alternativas consideradas:**
- Monolito modular único (capítulo 6): descartada como estrutura geral porque o validador embarcado é, por natureza, uma unidade de implantação separada e offline, e a telemetria precisa escalar sozinha no pico; um processo único não atende esses dois requisitos ao mesmo tempo. A ideia é aproveitada em parte, mantendo os subdomínios administrativos modularizados.
- SOA com barramento de serviços (capítulo 10): descartada porque concentra roteamento e transformação em um intermediário central, que vira ponto único de falha e de disputa, contra a exigência de disponibilidade do envelope.
- Microsserviços por camada técnica (interface, regra, dados): descartada por produzir monolito distribuído, no qual nada se implanta sozinho e toda operação atravessa a rede várias vezes (seção 9.6).

**Consequências:**
- Positivas: cada subdomínio escala, é implantado e falha de forma independente; a indisponibilidade da telemetria ou da informação ao passageiro não derruba a validação nem o repasse; os eventos publicados no barramento formam um rastro natural para a auditoria do envelope E.
- Negativas: processos que cruzam serviços passam a exigir saga com compensação e idempotência (ADR 0002); a observabilidade vira distribuída e obrigatória (ADR 0004); o custo operacional se multiplica por serviço, o que pesa sobre uma equipe de 15 pessoas e obriga a limitar o número de serviços.
