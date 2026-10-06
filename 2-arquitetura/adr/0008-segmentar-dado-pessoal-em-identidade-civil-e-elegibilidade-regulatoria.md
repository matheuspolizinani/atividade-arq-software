# ADR 0008: segmentar dado pessoal em identidade civil e elegibilidade regulatória

**Status:** aceito

**Contexto:** O ADR 0005 resolvia o direito ao esquecimento cifrando o bloco pessoal inteiro com uma chave por titular e destruindo-a no pedido de esquecimento. A leitura cruzada (objeção 03 do Grupo 02) mostrou uma falha: 25% das viagens são gratuidade ou desconto subsidiado, e o Tribunal de Contas audita se o passageiro tinha direito ao subsídio na data do evento; ao destruir a chave, o sistema apagava também a prova de elegibilidade, impedindo a operadora de comprovar que a viagem subsidiada foi legítima. A LGPD permite reter dado pessoal para cumprimento de obrigação legal ou regulatória (art. 7º e art. 16), base distinta do consentimento que fundamenta o esquecimento. Substitui o ADR 0005.

**Decisão:** Segmentar o dado pessoal em três níveis: (1) **identidade civil** (nome, CPF, foto, contato) cifrada por titular e destruída no esquecimento (crypto-shredding, como no ADR 0005); (2) **elegibilidade regulatória** (tipo de benefício, número do cartão social, entidade emissora, cota) mantida em claro, **pseudonimizada por um identificador opaco** no evento contábil, retida sob a base legal/regulatória e sem vínculo reversível à identidade após o shredding; (3) **dados de viagem e linha** em claro. Ao destruir a chave, o cidadão deixa de ser identificável, mas permanece a prova de que um portador de benefício ativo do tipo X fez a viagem.

**Alternativas consideradas:**
- Cifrar todo o bloco pessoal (decisão original do ADR 0005): descartada porque o esquecimento apaga junto a prova de elegibilidade exigida pela auditoria de subsídio.
- Manter a elegibilidade vinculada à identidade cifrada: descartada porque o shredding da identidade levaria a elegibilidade junto.
- Não reter a elegibilidade: descartada porque violaria a obrigação de comprovar o subsídio ao Tribunal de Contas.

**Consequências:**
- Positivas: o esquecimento é cumprido (identidade irrecuperável) e a auditoria de subsídio é preservada (elegibilidade pseudonimizada permanece); a base legal de retenção fica explícita.
- Negativas: exige classificar o dado com mais granularidade (o que é identidade e o que é elegibilidade) e governar essa fronteira; o pseudônimo opaco vira ativo crítico; pseudônimo mal gerado reabre risco de reidentificação.
