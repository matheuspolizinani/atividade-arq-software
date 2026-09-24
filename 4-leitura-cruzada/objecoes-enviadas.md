# Entrega 4a — Leitura cruzada: objeções ao Grupo 07

**Grupo revisor:** Grupo 06 (Ônibus, envelope E)
**Grupo revisado:** Grupo 07 (Ônibus, envelope A — startup, 6 desenvolvedores, sem equipe de operação)
**Repositório revisado:** https://github.com/Silveira-k7/grupo-07-onibus-a-arquitetura

Todas as objeções abaixo consideram o envelope A: time pequeno, pouco dinheiro e ninguém dedicado a operar infraestrutura. O que pesamos é se a decisão se sustenta **nessas** condições, não se é a que nós tomaríamos no envelope E.

---

## Objeção 1 — Uso duplicado com a mesma sequência some sem aviso

**Trecho atacado:** `3-spike/exemplo.py`, classe `ReconciliadorEventos`, método `receber`.

```python
@dataclass(frozen=True)
class Evento:
    ...
    seq: int  # ordem causal do cartao, definida no instante da validacao

def receber(self, ev):
    if ev.event_id in self.processados:
        self.duplicatas_filtradas += 1
        return
    self.processados.add(ev.event_id)
    if ev.seq != self.esperado[ev.cartao]:
        self.buffer[ev.cartao][ev.seq] = ev
        self.eventos_reordenados += 1
        return
    self._aplicar(ev)
    prox = self.esperado[ev.cartao]
    while prox in self.buffer[ev.cartao]:
        self._aplicar(self.buffer[ev.cartao].pop(prox))
        prox = self.esperado[ev.cartao]
```

**Argumento:** O `seq` por cartão é gerado na simulação por um contador global (`seq = defaultdict(int)` em `gerar_eventos_reais`) que enxerga todos os ônibus ao mesmo tempo. Na vida real, dois validadores offline não conseguem combinar esse número: se o contador fica no cartão, um cartão clonado (ou lido em dois ônibus antes de gravar) produz **dois eventos com o mesmo `seq`**. No código acima, o segundo evento tem `seq` menor que o esperado, cai no `buffer` e nunca mais sai, porque `esperado` só cresce. Ele não entra na trilha, não debita e, como `detectar_uso_duplicado` só lê a trilha, também não é detectado. Ou seja, o cenário que o spike diz provar (uso duplicado) é justamente o que o código esconde, e ainda o conta em `eventos_reordenados`.

**O que faríamos:** gerar o `seq` como o validador realmente consegue (por dispositivo, ou `seq` do cartão + id do validador), tratar colisão de `seq` como sinal explícito de fraude e incluir no spike um caso de teste com dois eventos de mesmo `seq`.

---

## Objeção 2 — Um evento perdido congela o saldo do cartão para sempre

**Trecho atacado:** `3-spike/exemplo.py`, `ReconciliadorEventos.receber` e `simular_rede_instavel`.

```python
if ev.seq != self.esperado[ev.cartao]:
    self.buffer[ev.cartao][ev.seq] = ev
    self.eventos_reordenados += 1
    return
```

```python
def simular_rede_instavel(eventos, rng):
    entregues = list(eventos)
    duplicatas = rng.sample(eventos, k=max(1, len(eventos) // 6))
    entregues.extend(duplicatas)
    rng.shuffle(entregues)
    return entregues
```

**Argumento:** O buffer espera indefinidamente pelo `seq` que falta, sem prazo nem alerta. E a simulação de rede só duplica e embaralha: `entregues = list(eventos)` garante que todo evento chega, então perda nunca é testada. Se um validador quebra, é trocado ou passa das 4 h offline e descarta eventos, todos os eventos seguintes daquele cartão ficam presos: o saldo para de ser atualizado e nada avisa. No envelope A não existe equipe de operação para perceber isso; o problema só aparece quando o passageiro reclama, possivelmente depois da janela de contestação de 30 dias.

**O que faríamos:** prazo máximo de espera por lacuna, aplicar os eventos seguintes marcando a lacuna na trilha e gerar alerta automático (e-mail ou painel simples) em vez de depender de alguém olhar logs. Na simulação, descartar parte dos eventos para testar esse caminho.

---

## Objeção 3 — A "prova de auditabilidade" é circular

**Trecho atacado:** `3-spike/exemplo.py`, `_aplicar`, `reconstruir_do_log` e a verificação em `main`; `3-spike/README.md`, seção "O que prova".

```python
def _aplicar(self, ev):
    self.saldo[ev.cartao] += ev.valor if ev.tipo == "recarga" else -ev.valor
    self.log.append(ev)
    self.esperado[ev.cartao] += 1

def reconstruir_do_log(self):
    saldo = defaultdict(float)
    for ev in self.log:
        saldo[ev.cartao] += ev.valor if ev.tipo == "recarga" else -ev.valor
    return dict(saldo)
```

```python
reconstruido = idem.reconstruir_do_log()
...
bate = reconstruido == dict(idem.saldo)
```

**Argumento:** `_aplicar` atualiza o saldo e acrescenta à trilha no mesmo passo, com a mesma fórmula, e `reconstruir_do_log` repete essa fórmula sobre a mesma lista. Comparar os dois vai dar "SIM" sempre, por construção; o teste não pode falhar. Além disso, `self.log` é uma lista Python em memória (`self.log = []`): nada no spike demonstra imutabilidade nem persistência. O README afirma que o reconciliador é "100% reconstruível a partir só da trilha (prova de auditabilidade)", o que é mais forte do que o código mostra.

**O que faríamos:** persistir a trilha (mesmo um arquivo append-only ou tabela só com INSERT), derrubar o processo no meio e reconstruir a partir do armazenamento, comparando com `saldo_verdadeiro(eventos)`, não com o próprio estado.

---

## Objeção 4 — Idempotência só vale enquanto o processo não reinicia

**Trecho atacado:** `3-spike/exemplo.py`, `ReconciliadorEventos.__init__` e `receber`.

```python
def __init__(self):
    self.saldo = defaultdict(float)
    self.processados = set()
    ...

def receber(self, ev):
    if ev.event_id in self.processados:
        self.duplicatas_filtradas += 1
        return
    self.processados.add(ev.event_id)
```

**Argumento:** A deduplicação depende de um `set` em memória que cresce sem limite (1.200 validadores gerando eventos o dia inteiro) e desaparece a cada reinício. Depois de um deploy ou queda, toda retransmissão volta a ser aplicada — exatamente o comportamento do `ReconciliadorIngenuo` que o spike usa como contraexemplo. A parte difícil da idempotência (onde guardar os ids já vistos, por quanto tempo) não foi provada, e é a que mais custa para um time sem operação.

**O que faríamos:** restrição de unicidade em `event_id` no banco (`INSERT ... ON CONFLICT DO NOTHING`), com o prazo de retenção dos ids amarrado às 4 h offline + retransmissões, e um teste de reinício no spike.

---

## Objeção 5 — O spike prova que é preciso idempotência, não que é preciso arquitetura orientada a eventos com Event Sourcing

**Trecho atacado:** `3-spike/exemplo.py`, classe `ReconciliadorIngenuo`; `3-spike/README.md`, seções "O que prova" e "Se a decisão estivesse errada"; decisão em `1-matriz/matriz.md`, "Direção arquitetural adotada".

```python
class ReconciliadorIngenuo:
    """O que a matriz evita: aplica cada evento na ordem em que chega, sem
    dedup e sem reconciliacao causal. Serve para mostrar o custo de NAO
    seguir a decisao."""

    def receber(self, ev):
        self.saldo[ev.cartao] += ev.valor if ev.tipo == "recarga" else -ev.valor
```

**Argumento:** A única alternativa comparada é um consumidor sem deduplicação nenhuma, que ninguém proporia. A alternativa relevante para o envelope A é mais barata: um banco relacional com tabela de lançamentos (ledger) só de inserção e `event_id` único dá deduplicação, trilha e reconstrução de saldo sem broker, sem projeções e sem versionamento de esquema de eventos. Esses custos — operar um broker, reprocessar projeções, evoluir eventos antigos — caem sobre 6 desenvolvedores sem ninguém de operação e não aparecem em lugar nenhum do spike nem do README. Mostrar que o `ReconciliadorIngenuo` erra não prova que Event Sourcing é necessário, só que deduplicação é.

**O que faríamos:** comparar no spike o ledger relacional com a solução de eventos e registrar no ADR o custo operacional de cada uma; adotar Event Sourcing só se o ledger simples não resolver algo concreto.

---

## Objeção 6 — Janela de 5 minutos marca integração legítima como fraude

**Trecho atacado:** `3-spike/exemplo.py`, constante `JANELA_SUSPEITA_MIN`, injeção de casos em `gerar_eventos_reais` e `detectar_uso_duplicado`.

```python
JANELA_SUSPEITA_MIN = 5  # 2 debitos do mesmo cartao em onibus diferentes,
                         # com essa distancia ou menos, viram suspeita de uso duplicado
```

```python
for cartao, b1, b2 in [("C002", "BUS01", "BUS03"), ("C006", "BUS04", "BUS02")]:
    minuto += rng.randint(5, 10)
    novo(cartao, b1, minuto, "debito", TARIFA)
    novo(cartao, b2, minuto + rng.randint(1, 3), "debito", TARIFA)
```

```python
for a, b in zip(evs, evs[1:]):
    if b.minuto - a.minuto <= janela_min and a.onibus != b.onibus:
        achados.append((cartao, a, b))
```

**Argumento:** Dois débitos do mesmo cartão em ônibus diferentes em até 5 minutos é também o padrão de um passageiro que desce de um ônibus e embarca em outro (baldeação). O spike só injeta casos fraudulentos, sempre com 1 a 3 minutos de diferença (dentro da janela, por construção), e nunca mede falso positivo, então o "PASS" não diz nada sobre a qualidade da detecção. Além disso, a regra usa `minuto`, o relógio do validador, que passou até 4 h sem sincronizar e pode estar adiantado ou atrasado. Numa startup sem operação, cada falso positivo vira análise manual ou bloqueio indevido de cliente.

**O que faríamos:** regra baseada em impossibilidade física (sobreposição de viagens ou distância entre linhas), respeitando a regra de integração tarifária, registrar a hora de sincronização junto da hora do validador e incluir baldeações legítimas na simulação para medir falsos positivos.

---

## Objeção 7 — Detectar sem reagir: não há bloqueio nem política de saldo negativo

**Trecho atacado:** `3-spike/exemplo.py`, constantes, recarga inicial e condição de sucesso em `main`; `3-spike/README.md`, "Se a decisão estivesse errada".

```python
TARIFA = 4.30
RECARGA_INICIAL = 50.00
...
for c in cartoes:
    novo(c, "APP", 0, "recarga", RECARGA_INICIAL)
```

```python
if todos_ok and bate and divergentes > 0 and achados:
    print("RESULTADO: PASS -- ...")
```

**Argumento:** A detecção só acontece depois da sincronização, até 4 h depois, e o spike para aí: o `PASS` exige apenas que `achados` não esteja vazio. Não há lista de bloqueio enviada aos validadores, então o cartão fraudado continua aceito offline até a próxima sincronização. Também, como os validadores debitam sem conhecer o saldo atual, um cartão pode ficar negativo ao ser usado em vários ônibus — a simulação evita isso começando todos com R$ 50 e nunca verifica `saldo < 0`. O prejuízo que a decisão diz evitar continua acontecendo, só que agora com registro.

**O que faríamos:** lista de bloqueio distribuída a cada sincronização, limite de saldo negativo aceito offline definido no ADR e um caso no spike com cartão sem saldo.

---

## Objeção 8 — Valores monetários em `float`

**Trecho atacado:** `3-spike/exemplo.py`, constantes, estado do reconciliador e comparação em `main`.

```python
TARIFA = 4.30
...
self.saldo = defaultdict(float)
...
ok = abs(v - i) < 1e-9
```

**Argumento:** A decisão existe para que a conciliação com o banco feche. Somar tarifas em `float` acumula erro de arredondamento, e o próprio spike precisa de tolerância (`1e-9`) para comparar saldos. Em milhões de débitos por mês, "quase igual" não fecha conciliação nem sustenta uma contestação.

**O que faríamos:** valores em centavos inteiros (ou `Decimal`) e comparação exata.

---

## Objeção 9 — O spike não está ligado a um ADR

**Trecho atacado:** `3-spike/README.md`, cabeçalho; docstring de `3-spike/exemplo.py`.

```markdown
**ADR que este código prova:** a decisão mais arriscada do projeto, registrada em
`1-matriz/matriz.md`, seção "Direção arquitetural adotada" (deve corresponder ao
ADR-0005 — "decisão mais arriscada" — na Entrega 2; os ADRs formais ainda não
foram anexados a esta conversa, então o spike referencia a matriz diretamente).
```

```python
Prova a decisao mais arriscada do projeto, registrada em matriz.md, secao
"Direcao arquitetural adotada": ...
```

**Argumento:** O próprio README diz que deveria corresponder ao ADR-0005, mas aponta para a matriz porque os ADRs não estavam disponíveis. A Entrega 3 pede código que prove uma decisão registrada; sem o vínculo, não dá para saber quais alternativas e custos foram considerados, nem conferir se o spike testa o que o ADR afirma.

**O que faríamos:** referenciar o ADR-0005 diretamente, com as consequências que o spike confirma ou derruba.
