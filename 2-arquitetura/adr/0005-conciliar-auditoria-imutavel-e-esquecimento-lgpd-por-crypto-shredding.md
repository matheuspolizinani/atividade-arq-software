# ADR 0005: conciliar auditoria imutável e esquecimento LGPD por destruição criptográfica

**Status:** aceito

**Contexto:** O envelope E impõe duas exigências que se contradizem. A fiscalização pede trilha completa e reconstruível, e o repasse é event-sourced, com armazenamento append-only onde o evento antigo é imutável (ADR 0002, capítulo 15). A LGPD dá ao passageiro o direito de pedir a eliminação do histórico de viagens, que é dado pessoal (Lei nº 13.709/2018). A seção 15.6 registra o conflito direto: um armazenamento imutável não apaga registros sem quebrar a integridade do fluxo, e o repasse financeiro depende desse fluxo para fechar e para responder a contestação em até 30 dias. É a decisão de maior risco do projeto, e por isso é a provada pelo código pequeno da Entrega 3.

**Decisão:** Separar, dentro de cada evento, o dado pessoal do dado financeiro. Os campos que identificam o passageiro são cifrados com uma chave por titular, guardada em um keystore fora do event store (seção 15.7); os campos usados no repasse (linha, operadora, tarifa vigente, valor) ficam em claro e sem identificar a pessoa. Atender a um pedido de esquecimento é destruir a chave daquele titular (crypto-shredding): o conteúdo pessoal torna-se irrecuperável, o evento e sua ordem permanecem, e os totais de conciliação continuam fechando. A exclusão dentro do fluxo nunca apaga um fato: grava-se um evento de reversão.

**Alternativas consideradas:**
- Apagar fisicamente os eventos da pessoa no armazenamento append-only: descartada porque quebra a cadeia de versões, invalida os snapshots e impede a reconstrução exigida pela auditoria.
- Manter todo o dado pessoal fora do fluxo, referenciado por identificador (a outra saída da seção 15.7): descartada como opção única porque a viagem precisa de atributos do titular (gratuidade, tipo de benefício) no momento da apuração; parte deles é mantida cifrada no próprio evento para não depender de uma leitura externa a cada reprocessamento.
- Anonimizar por hash irreversível na escrita: descartada porque impede a operação legítima de atendimento e contestação antes do pedido de esquecimento, quando o titular ainda precisa ser identificável.

**Consequências:**
- Positivas: a mesma base atende auditoria e esquecimento; a destruição da chave é uma operação pontual, registrada e verificável; o repasse e a conciliação seguem íntegros após o esquecimento.
- Negativas: acrescenta cifra em toda leitura e escrita do financeiro e exige gestão de chaves robusta, com o keystore virando ativo crítico; perder uma chave sem pedido de esquecimento equivale a perder o dado; o versionamento de eventos precisa prever a rotação de chaves.
