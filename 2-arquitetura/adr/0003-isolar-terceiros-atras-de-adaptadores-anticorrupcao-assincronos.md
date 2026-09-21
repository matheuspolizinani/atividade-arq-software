# ADR 0003: isolar terceiros atrás de adaptadores anticorrupção assíncronos

**Status:** aceito

**Contexto:** O sistema depende de terceiros que não controla: o banco e o adquirente para liquidar recarga e conciliar, os sistemas do órgão gestor e das operadoras para trocar dados e arquivos, e a rede externa de recarga em lojas e totens. Esses parceiros impõem formatos próprios e têm janelas de indisponibilidade previstas no caso. Sob o envelope E, a fiscalização exige que a queda de um parceiro não apague o rastro nem trave a operação. A seção 9.7 alerta que tratar a rede interna e externa como zona confiável é um custo escondido do estilo.

**Decisão:** Concentrar toda conversa com terceiros no serviço de Integração e Conformidade, escrito em arquitetura hexagonal (capítulo 7): cada parceiro entra por um adaptador que implementa uma camada anticorrupção (anti-corruption layer), traduzindo o formato externo para o modelo do domínio antes de ele cruzar a fronteira. As chamadas síncronas a parceiros levam tempo limite, retentativa e disjuntor (circuit breaker, seção 9.2); quando o parceiro pode responder depois, a integração é assíncrona, com fila e reprocessamento. A liquidação da recarga é registrada como evento e conciliada contra o retorno do banco.

**Alternativas consideradas:**
- Cada serviço falar direto com o banco e o adquirente: descartada por espalhar o formato do terceiro por todo o código, de modo que uma mudança do parceiro obrigaria a alterar vários serviços.
- Chamada síncrona direta ao parceiro no caminho da recarga: descartada porque a janela de indisponibilidade do terceiro viraria indisponibilidade da recarga para o passageiro (seção 11.6).
- Barramento de serviços (ESB) para mediar os parceiros (capítulo 10): descartada porque acrescenta um intermediário central de roteamento e transformação, contra a regra de pontas inteligentes e canais burros adotada no ADR 0001.

**Consequências:**
- Positivas: o modelo de domínio fica livre do formato do legado e de terceiros; a queda de um parceiro degrada apenas a integração, e a operação continua com reconciliação posterior; trocar um parceiro é reescrever um adaptador, não o domínio.
- Negativas: a tradução nos dois sentidos é escrita e mantida à mão em cada adaptador (seção 7.7); a consistência com o banco passa a ser eventual, com uma janela em que o sistema e o parceiro podem discordar até a conciliação fechar.
