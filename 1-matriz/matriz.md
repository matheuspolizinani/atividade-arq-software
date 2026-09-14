# Entrega 1 – Matriz de Estilos Aplicada

| Estilo | Serve? | Subdomínio em que entraria | Por quê? | Qualidade |
|---|---|---|---|---|
| 5. Monolito em camadas | Não | -- | Não atende bem partes com cargas diferentes, pois o sistema escala como um todo. (Seção 5.6) | Melhora: custo operacional. Piora: escalabilidade. |
| 6. Monolito modular | Em parte | Atendimento e administrativo | Organiza bem os módulos, mas todos continuam na mesma implantação e escala. (Seção 6.6) | Melhora: modificabilidade. Piora: escalabilidade. |
| 7. Hexagonal | Sim | Recarga, repasse e integrações externas | Separa as regras de negócio de bancos, APIs e outros sistemas externos. (Seção 7.5) | Melhora: testabilidade. Piora: implantabilidade. |
| 8. Microkernel | Não | -- | É indicado quando há muitas extensões/plugins, o que não é uma necessidade central do sistema. (Seção 8.6) | Melhora: modificabilidade. Piora: escalabilidade. |
| 9. Microsserviços | Sim | Validação, recarga, telemetria e repasse | Permite que partes com cargas e disponibilidade diferentes sejam implantadas e escaladas separadamente. (Seção 9.5) | Melhora: escalabilidade. Piora: testabilidade. |
| 10. SOA / ESB | Em parte | Bancos, adquirentes e sistemas externos | Facilita a integração entre sistemas diferentes, mas adiciona um intermediário central. (Seção 10.5) | Melhora: modificabilidade. Piora: disponibilidade. |
| 11. Orientada a eventos | Sim | Telemetria, validações e auditoria | Ajuda a absorver picos e desacoplar o processamento entre diferentes partes do sistema. (Seção 11.5) | Melhora: escalabilidade. Piora: testabilidade. |
| 12. Serverless | Em parte | Tarefas agendadas e rotinas auxiliares | Funciona bem para tarefas curtas e eventuais, mas não para cargas contínuas e sensíveis à latência. (Seções 12.5 e 12.6) | Melhora: escalabilidade. Piora: testabilidade. |
| 13. Arquitetura celular | Em parte | Serviços separados por região/operadora | Pode isolar falhas por grupos, mas aumenta a dificuldade de operações globais. (Seções 13.5 e 13.6) | Melhora: disponibilidade. Piora: testabilidade. |
| 14. CQRS | Sim | Repasse, conciliação e consultas | Separa escrita e leitura, facilitando relatórios e diferentes visões dos mesmos dados. (Seção 14.5) | Melhora: desempenho. Piora: testabilidade. |
| 15. Event Sourcing | Sim, mas restrito | Repasse e auditoria financeira | Mantém o histórico necessário à auditoria, mas exige cuidado com a exclusão de dados pessoais pela LGPD. (Seções 15.5 e 15.6) | Melhora: modificabilidade. Piora: desempenho. |
| 16. Pipes and Filters | Em parte | Telemetria e processamento de relatórios | É adequado para fluxos em etapas, como validar, transformar e consolidar dados. (Seção 16.5) | Melhora: testabilidade. Piora: desempenho. |
