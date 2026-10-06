# Spike — ADR 0008: identidade civil (esquecimento) + elegibilidade regulatória (auditoria)

> Este spike provava originalmente o **ADR 0005**. Após a leitura cruzada (objeção 03 do Grupo 02), o ADR 0005 foi substituído pelo **ADR 0008**, que segmenta o dado pessoal; o spike foi atualizado para provar a decisão vigente. Veja o CHANGELOG em `5-final/CHANGELOG.md`.

## O que este spike prova

Demonstra a decisão do **ADR 0008**: manter a auditoria imutável e o esquecimento LGPD por destruição criptográfica, **separando** dentro do evento:

1. **Identidade civil** (nome, CPF) — cifrada com uma chave por titular; destruí-la a torna irrecuperável (crypto-shredding).
2. **Elegibilidade regulatória** (tipo de benefício, emissor, pseudônimo opaco) — em claro, pseudonimizada, retida por base legal; **não depende da chave do titular**.
3. **Dados financeiros/viagem** (linha, operador, subsídio devido) — em claro.

O fluxo demonstrado:

1. Registra uma viagem **subsidiada** (estudante): o passageiro paga 0 e a prefeitura deve R$ 5,40 ao operador.
2. Antes do esquecimento, a identidade é recuperável e o subsídio é auditável com prova de elegibilidade.
3. O pedido de esquecimento grava um novo evento e **destrói a chave** do titular.
4. Depois: a identidade vira irrecuperável (`None`), **mas** o total de subsídio devido **e** a prova de que havia um benefício ativo (ESTUDANTE, pseudônimo) **permanecem**.

Assim, o spike cobre o ponto que a leitura cruzada expôs: o esquecimento do passageiro **não** apaga a prova de que o subsídio público foi legítimo, que o Tribunal de Contas precisa auditar.

## Como executar

Requisito: **Python 3.12+** (testado em 3.13). Dentro desta pasta:

```bash
python3 exemplo.py
```

Só biblioteca padrão; sem banco, serviços externos ou internet. A saída esperada está em `saida-esperada.txt` e é determinística (rodar duas vezes produz o mesmo resultado).

## O que está sendo simulado

- `EventStore`: armazenamento de eventos append-only.
- `KeyStore`: cofre externo de chaves por titular (dicionário em memória, para manter o spike pequeno).
- `cifrar/decifrar`: cifra **didática** (XOR com keystream HMAC-SHA256). **Não é criptografia de produção** — serve só para demonstrar a relação entre dado cifrado e chave.
- `pseudonimo`: identificador opaco e estável do titular, **não reversível** à identidade após o shredding.

## O que aconteceria se a decisão estivesse errada?

- Se a **identidade** ficasse em claro no evento: violaria o direito ao esquecimento.
- Se a **elegibilidade** fosse cifrada junto com a identidade (como no ADR 0005 original): ao destruir a chave, a prova do subsídio sumiria e a operadora não poderia comprovar o direito na auditoria.
- Se o evento fosse **apagado fisicamente**: quebraria o histórico financeiro e a reconstrução exigida pela fiscalização.

Com o ADR 0008, destruir a chave remove só a identidade civil; subsídio e elegibilidade (pseudonimizada) permanecem auditáveis.

## Limite do spike

Comprova a **decisão arquitetural e o fluxo técnico**. Não comprova, sozinho, conformidade jurídica com a LGPD nem substitui os requisitos de segurança (algoritmo real, gestão de chaves, controle de acesso, rotação, backup) de uma implementação de produção.
