# ADR 0007: representar regras tarifárias como estratégia versionada por vigência

**Status:** aceito

**Contexto:** Sob o envelope E, tarifas, gratuidades, cotas de subsídio e matrizes de integração horária mudam por decreto municipal e portaria, às vezes com efeito retroativo ou restrito a feriados. A leitura cruzada (objeção 02 do Grupo 02) observou que, se essas regras ficam embutidas no agregado do Núcleo Financeiro, cada decreto obriga a alterar e reimplantar o motor contábil, com reteste e risco de regressão nos meses anteriores. O repasse já aplica a tarifa vigente na data de cada viagem (ADR 0002), mas a forma de representar a regra não estava registrada. Este ADR refina o ADR 0002.

**Decisão:** Tratar cada regra tarifária e de subsídio como um artefato de configuração/estratégia **versionado e delimitado por data de vigência**, guardado em um catálogo de regras que o agregado consulta pela data do evento. Um novo decreto acrescenta uma nova versão de regra ao catálogo, sem alterar o código do motor de liquidação; o recálculo retroativo (requisito C7) resolve a versão vigente na data de cada viagem.

**Alternativas consideradas:**
- Embutir as regras no agregado: descartada porque cada decreto viraria alteração de código, com reteste do motor inteiro e risco de regressão nos cálculos já fechados.
- Adotar o Microkernel como estilo do sistema: descartada porque o sistema não é centrado em plugins; o mecanismo de plugin cabe aqui como padrão dentro de um serviço, não como topologia global (distinção estilo × padrão, seção 2.2).
- Guardar a regra só como linha de banco sem vigência: descartada porque não permite reconstruir o cálculo com a regra que valia na data da viagem.

**Consequências:**
- Positivas: um decreto entra como nova versão de regra sem reimplantar o motor; o recálculo histórico usa a regra vigente na data; o motor contábil permanece estável para a auditoria do Tribunal de Contas.
- Negativas: o catálogo de regras vira um ativo versionado a governar, com teste por versão; exige disciplina de vigência e de desativação de regras antigas.
