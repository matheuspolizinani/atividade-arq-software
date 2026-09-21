# ADR 0004: operar em nuvem com trilha de auditoria e observabilidade obrigatórias

**Status:** aceito

**Contexto:** O envelope E coloca a operação sob fiscalização de órgão regulador, em nuvem pública, com exigência de trilha de auditoria completa: tudo que acontece precisa ser reconstruível. A equipe tem 15 desenvolvedores e 1 responsável por conformidade, sem um time de operação grande. A composição do ADR 0001 é distribuída, e a seção 9.2 lembra que, em um sistema por eventos, ler um registro de log por vez não reconstrói o que aconteceu. A carga é desigual: a validação tem pico de 120 por segundo no rush, a telemetria tem pico de cinco vezes a média e a informação ao passageiro dispara no horário de pico e cai fora dele.

**Decisão:** Implantar em nuvem pública com entrega contínua automatizada, contêineres e um gateway de API único na borda (autenticação, limite de uso e roteamento). Toda requisição carrega um identificador de correlação propagado entre serviços, e a plataforma reúne log correlacionado, métricas por serviço e por dependência e rastreamento distribuído (seção 9.2). Cada evento de negócio publicado no barramento é retido como trilha de auditoria imutável, alimentada pelo mesmo fluxo do Núcleo Financeiro (ADR 0002). O escalonamento é automático e por serviço: a informação ao passageiro (CQRS) sobe réplicas de leitura no pico e recua fora dele; a telemetria absorve o pico no barramento, sem repassá-lo aos demais.

**Alternativas consideradas:**
- Servidores próprios em data center municipal: descartada porque contraria a infraestrutura de nuvem pública definida no envelope E e obrigaria a equipe pequena a operar o hardware.
- Escalar o sistema inteiro como um bloco para o pico: descartada porque o custo cresceria em todos os subdomínios para atender a carga de um só, contra a métrica de custo por mil pedidos (seção 2.3).
- Trilha de auditoria montada só com logs de aplicação: descartada porque log é volátil, amostrado e reescrito, e não sustenta a reconstrução completa que a fiscalização exige.

**Consequências:**
- Positivas: um incidente é diagnosticado por correlação e rastreamento, e não por leitura manual; o custo acompanha a carga real de cada serviço; a trilha por eventos dá à auditoria a reconstrução que o envelope pede.
- Negativas: a plataforma de entrega, descoberta, gateway e rastreamento é pré-requisito e consome parte da capacidade de uma equipe pequena; reter tudo de forma reconstruível cresce em armazenamento e entra em tensão direta com o direito ao esquecimento, resolvida no ADR 0005.
