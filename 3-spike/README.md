# Spike — ADR 0005: Auditoria imutável + esquecimento LGPD

## O que este spike prova

Este spike demonstra a decisão arquitetural registrada na **ADR 0005**: manter os eventos financeiros em um histórico append-only, mas separar os dados pessoais e protegê-los com uma chave específica por titular.

O fluxo demonstrado é:

1. Uma viagem é registrada.
2. Os dados financeiros ficam no evento.
3. O nome do passageiro é armazenado de forma cifrada.
4. A chave do passageiro fica em um `KeyStore` separado.
5. Antes do esquecimento, o nome pode ser recuperado.
6. O pedido de esquecimento registra um novo evento.
7. A chave do titular é destruída (**crypto-shredding**).
8. O evento original continua existindo para auditoria.
9. O dado pessoal deixa de ser recuperável pelo sistema.
10. Os dados financeiros continuam disponíveis para auditoria e reconciliação.

Assim, o spike verifica o ponto de maior risco da arquitetura: o esquecimento do passageiro não exige apagar o evento financeiro nem destruir o histórico necessário para auditoria.

## Como executar

Requisito: **Python 3.12**.

Dentro desta pasta, execute:

```bash
python3 exemplo.py
```

O programa usa somente a biblioteca padrão do Python e não depende de banco de dados, serviços externos ou internet.

A saída esperada está registrada em `saida-esperada.txt`.

## O que está sendo simulado

O `EventStore` representa um armazenamento de eventos append-only.

O `KeyStore` representa um serviço externo de gerenciamento de chaves. No spike, ele é apenas um dicionário em memória para manter o exemplo pequeno e determinístico.

A cifra também é apenas uma **simulação didática**, criada com recursos da biblioteca padrão para demonstrar a relação entre dado cifrado e chave. Ela **não deve ser usada como implementação criptográfica de produção**. Em um sistema real, seriam necessários um algoritmo criptográfico apropriado, gerenciamento seguro de chaves, controle de acesso, rotação e mecanismos de recuperação/backup compatíveis com a política de segurança.

## O que aconteceria se a decisão estivesse errada?

Se o dado pessoal fosse armazenado diretamente no evento financeiro, o esquecimento poderia exigir a alteração ou exclusão de um fato que deveria permanecer disponível para auditoria e reconciliação.

Outra alternativa seria apagar fisicamente o evento. Isso preservaria o esquecimento do passageiro, mas quebraria o histórico financeiro necessário para reconstruir e auditar a operação.

Com a decisão do ADR 0005, a destruição da chave remove a capacidade do sistema de recuperar o dado pessoal, enquanto o evento financeiro e o registro do pedido de esquecimento permanecem.

## Limite do spike

Este código comprova apenas a **decisão arquitetural e o fluxo técnico**. Ele não comprova, sozinho, conformidade jurídica com a LGPD nem substitui os requisitos de segurança de uma implementação real.
