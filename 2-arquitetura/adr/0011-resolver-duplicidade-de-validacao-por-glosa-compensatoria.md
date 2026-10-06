# ADR 0011: resolver duplicidade de validação por evento de glosa compensatória

**Status:** aceito

**Contexto:** O ADR 0006 detecta o uso da mesma passagem em dois ônibus, mas tratava a colisão apenas como "suspeita", sem fechar a questão financeira. A leitura cruzada (objeção 06 do Grupo 02) mostrou o custo disso no envelope E: consórcios competem por receita e a câmara de compensação municipal reparte o montante; se dois ônibus de operadoras rivais aceitam o mesmo cartão offline, é preciso decidir qual operadora recebe e impedir que a prefeitura pague subsídio em dobro. Deixar a colisão aberta transfere o risco de fraude ao erário e fere o requisito C4. Este ADR refina os ADRs 0006 e 0002.

**Decisão:** Uma duplicata confirmada gera, no Núcleo Financeiro, um **evento contábil de glosa compensatória**: a primeira viagem (pela ordem no fluxo) é liquidada como legítima, a segunda é retida — sem pagar nem subsidiar em dobro — e o cartão entra na denylist distribuída à frota na próxima sincronização. A confirmação usa **impossibilidade física** (velocidade implausível entre as duas validações) combinada com a regra de integração tarifária, para não glosar baldeação legítima. A glosa é um evento novo (event sourcing), nunca uma sobrescrita.

**Alternativas consideradas:**
- Deixar a colisão como "suspeita" aberta (comportamento original do ADR 0006): descartada por transferir o risco de fraude ao erário.
- Glosar toda colisão de cartão em ônibus diferentes: descartada por punir baldeação legítima (falso positivo) — o mesmo defeito que apontamos ao revisar outro grupo.
- Bloquear o cartão em tempo real em todos os validadores: descartada por ser impossível offline.

**Consequências:**
- Positivas: o subsídio não é pago em dobro; a operadora remunerada fica definida por regra; a glosa é registrada e auditável.
- Negativas: existe uma janela até a sincronização em que a duplicata ainda não foi glosada; a regra espaço-temporal precisa de calibragem para minimizar falso positivo; a denylist precisa chegar à frota a cada ciclo.
