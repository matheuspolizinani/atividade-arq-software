# ADR 0012: impor invariantes de arquitetura por funções de aptidão na integração contínua

**Status:** aceito

**Contexto:** O ADR 0004 tratou a observabilidade em tempo de execução, mas não previu testes executáveis que verifiquem a arquitetura no momento da integração. A leitura cruzada (objeção 07 do Grupo 02) observou que, com 1 responsável por conformidade para 15 desenvolvedores, confiar só em revisão humana deixa a deriva arquitetural (seção 4.1) acontecer na primeira entrega sob prazo. O livro trata função de aptidão como instrumento para barrar essa deriva na integração contínua (seções 4.8 e 19.6). Este ADR refina o ADR 0004.

**Decisão:** Adicionar ao pipeline de integração contínua funções de aptidão que **reprovam o build** quando um invariante é violado: (1) isolamento de dados — analisador estático que proíbe um módulo ou serviço de acessar o banco ou o esquema de outro; (2) caminho de 300 ms — proibição de chamada de rede síncrona dentro do módulo embarcado de validação; (3) imutabilidade do event store — verificação de ausência de `UPDATE` ou `DELETE` mapeados sobre a tabela de eventos; e (4) o verificador de ADRs do capítulo 4.8, que os registros já passam. As funções rodam no mesmo pedido de alteração em que a mudança é proposta.

**Alternativas consideradas:**
- Confiar apenas em revisão humana: descartada porque uma pessoa de conformidade não cobre o volume de 15 desenvolvedores sob prazo.
- Checagem manual periódica: descartada por encontrar a deriva tarde, depois de ela já ter entrado no repositório.
- Não impor invariante automatizado: descartada porque a deriva apareceria já na primeira entrega e comprometeria a certificação da auditoria.

**Consequências:**
- Positivas: os invariantes que mais importam ao envelope E são verificados automaticamente e a deriva é barrada antes do merge; a conformidade escala além da capacidade de uma pessoa.
- Negativas: custo de montar e manter as funções; um falso positivo pode travar um build legítimo; as próprias funções viram código a manter e versionar.
