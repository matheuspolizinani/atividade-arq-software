# ADR 0002: dar a cada serviço o próprio banco e usar event sourcing no financeiro

**Status:** aceito

**Contexto:** A composição do ADR 0001 exige definir onde vive cada dado, quem é o dono e como se garante consistência. O saldo do cartão envolve dinheiro e não tolera fraude; a recarga acontece no aplicativo, na loja e no totem, e o uso acontece no ônibus, com atraso de sincronização. O repasse mensal precisa ser recalculado com a regra de tarifa vigente na data de cada viagem e sobrevive a contestação por 30 dias, sob fiscalização do Tribunal de Contas. A seção 2.5 lembra que dois serviços que compartilham banco não são dois quanta: voltam a subir juntos.

**Decisão:** Adotar banco por serviço (database per service, seção 9.2): nenhum serviço lê a tabela de outro, e todo acesso a dado alheio passa pela interface publicada do dono. O Núcleo Financeiro usa event sourcing como fonte de verdade (capítulo 15), com armazenamento append-only e concorrência otimista por versão de fluxo, e projeta relatórios de conciliação por CQRS (capítulo 14). A consistência entre recarga, débito e liquidação é obtida por saga com compensação e passos idempotentes (seção 9.2), operando em consistência eventual; dados pessoais não entram em texto claro no fluxo (ADR 0005).

**Alternativas consideradas:**
- Banco relacional compartilhado entre serviços: descartada porque o esquema comum acopla as implantações e uma alteração de tabela derruba vários serviços, anulando o ganho do ADR 0001.
- Tabela de auditoria ao lado do estado atual do repasse: descartada porque registra o que mudou, não a intenção nem a ordem, e depende de disciplina de escrita em cada ponto do código (seção 15.10); não permite recalcular o mês com a regra vigente na data.
- Event sourcing em todos os subdomínios: descartada por custo desproporcional em cadastro e catálogo de cartões e por agravar o conflito com o prazo de eliminação da LGPD (seção 15.6); o benefício se concentra no financeiro.

**Consequências:**
- Positivas: cada serviço evolui o próprio esquema sem coordenar implantação; o Núcleo Financeiro reconstrói a história de qualquer viagem para auditoria e disputa, e recalcula projeções por reprocessamento; conflitos de escrita são rejeitados em vez de sobrescritos.
- Negativas: relatórios que cruzam subdomínios não saem de uma consulta única e dependem de projeções alimentadas por eventos; o armazenamento de eventos cresce sem parar e exige snapshots e retenção; a equipe precisa dominar versionamento de eventos e idempotência antes do primeiro dado em produção.
