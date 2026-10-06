# atividade-arq-software — Grupo 06

Trabalho de **Padrões e Arquitetura de Software** · PUC-Campinas · 2026-2
Projeto "Um problema, cinco realidades" — arquitetura sob restrição.

## Tema sorteado

- **Caso:** Ônibus — bilhetagem e mobilidade urbana
- **Envelope:** E — Operação sob fiscalização de órgão regulador (15 desenvolvedores, 1 responsável por conformidade; nuvem pública com trilha de auditoria completa; LGPD com direito ao esquecimento)
- **Pergunta que o envelope obriga a responder:** como guardar tudo para sempre e ainda assim apagar o que a lei manda apagar?

## Integrantes

- _Joao Pedro Barbosa da Silva — 25016974_
- _Caio Eduardo Monforte Medeiros — 24017959_
- _Henrique Creolezi — 24019853_
- _Matheus Polizidani — 24011419_
- _Guilerme Mourad — 24024625_
- _Gabriel Freire — 23017628_

## Como navegar

| Pasta | Conteúdo | Status |
|---|---|---|
| [`1-matriz/`](1-matriz/matriz.md) | Matriz de estilos aplicada ao caso e ao envelope | Entrega 1 ✅ |
| [`2-arquitetura/`](2-arquitetura/) | Documento de arquitetura, diagramas C4, mapa de restrições e decisões, ADRs (0001–0012) | Entrega 2 ✅ (revisada) |
| [`3-spike/`](3-spike/) | Código pequeno que prova a decisão mais arriscada (ADR 0008) | Entrega 3 ✅ |
| [`4-leitura-cruzada/`](4-leitura-cruzada/) | Objeções enviadas (ao Grupo 07) e respostas recebidas (do Grupo 02) | Entrega 4 ✅ |
| [`5-final/`](5-final/CHANGELOG.md) | Versão revisada; o que mudou pela leitura cruzada está no CHANGELOG | Entrega 5 ✅ |

> **Versão final.** O repositório foi revisado após a leitura cruzada. O que mudou e por quê está em [`5-final/CHANGELOG.md`](5-final/CHANGELOG.md): seis ADRs novos (0007–0012), com o 0008 substituindo o 0005 e o 0009 substituindo o 0001.

### Entrega 2 — por onde começar

1. [`documento-arquitetura.md`](2-arquitetura/documento-arquitetura.md) — o documento principal, com os três níveis C4, os trade-offs e as cinco respostas obrigatórias.
2. [`adr/0001-...`](2-arquitetura/adr/) — o ADR de composição é o primeiro a ler; explica os estilos e onde cada fronteira começa e termina.
3. [`mapa-restricoes-decisoes.md`](2-arquitetura/mapa-restricoes-decisoes.md) — liga cada restrição do envelope e cada requisito do caso a uma decisão.

Os diagramas C4 têm fonte em Mermaid (`.mmd`) e imagem renderizada (`.png`) na pasta `2-arquitetura/`.
