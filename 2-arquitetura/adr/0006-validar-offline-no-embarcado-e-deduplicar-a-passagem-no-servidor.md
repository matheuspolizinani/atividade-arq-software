# ADR 0006: validar offline no embarcado e deduplicar a passagem no servidor

**Status:** aceito

**Contexto:** O validador precisa aceitar ou recusar a passagem em até 300 ms mesmo sem rede, e um ônibus pode ficar até 4 horas sem conexão. São 1.200 validadores e 900 mil validações por dia, com pico de 120 por segundo entre 6h30 e 8h30. Duas exigências convivem: nunca aceitar a mesma passagem duas vezes e nunca deixar o passageiro parado esperando a rede. Como não há conexão garantida no instante da validação, nenhuma verificação central pode estar no caminho da resposta.

**Decisão:** O validador embarcado decide localmente, contra uma lista de cartões e regras sincronizada quando há rede, e grava cada validação em uma fila local append-only, assinada, com identificador único (validador, cartão, viagem, carimbo de tempo). Ao reconectar, envia a fila acumulada ao Serviço de Validação com entrega ao menos uma vez (capítulo 11). O servidor é idempotente por esse identificador e reconstrói o uso a partir do fluxo (capítulo 15): quando o mesmo cartão e a mesma viagem chegam de dois validadores, a duplicata é detectada na consolidação, e não no ônibus. A política de risco offline (limite por janela sem sincronizar) fica na lista embarcada.

**Alternativas consideradas:**
- Exigir confirmação online a cada validação: descartada porque a rede 4G é intermitente e a resposta estouraria os 300 ms ou barraria o passageiro sem conexão.
- Bloquear o cartão em todos os validadores ao primeiro uso: descartada porque exigiria comunicação entre 1.200 validadores em tempo real, impossível offline, e recusaria embarques legítimos.
- Deduplicar por sobrescrita da última validação no banco: descartada porque perde o registro do uso concorrente, justamente a evidência de que a passagem foi usada em dois ônibus (seção 15.5).

**Consequências:**
- Positivas: a resposta ao passageiro não depende da rede e cabe nos 300 ms; o uso em dois ônibus é sempre descoberto depois, com prova em ordem no fluxo; a fila assinada alimenta a auditoria do envelope E.
- Negativas: entre o uso offline e a sincronização existe uma janela de consistência eventual em que a fraude ainda não foi detectada, limitada pela política embarcada; o servidor precisa tratar duplicata, ordem e reprocessamento, e o embarcado precisa de espaço para a fila durante as 4 horas sem rede.
