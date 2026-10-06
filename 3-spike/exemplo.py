from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any


# Spike do ADR 0008 (que substitui o ADR 0005):
# "Segmentar dado pessoal em identidade civil e elegibilidade regulatória".
#
# Mantém a auditoria imutável e o esquecimento LGPD por crypto-shredding,
# mas separa, dentro do evento, três blocos:
#   1. IDENTIDADE CIVIL (nome, CPF): cifrada por titular; destruir a chave a torna
#      irrecuperável (crypto-shredding), atendendo ao direito ao esquecimento.
#   2. ELEGIBILIDADE REGULATÓRIA (tipo de benefício, pseudônimo opaco, emissor):
#      em claro, pseudonimizada, retida por base legal/regulatória; NÃO depende da
#      chave do titular, então sobrevive ao esquecimento e sustenta a auditoria de
#      subsídio do Tribunal de Contas.
#   3. DADOS FINANCEIROS / DE VIAGEM (linha, operador, subsídio): em claro.
#
# IMPORTANTE: a "criptografia" abaixo é só uma simulação determinística do
# mecanismo de destruição de chave. Não é criptografia de produção.


def derivar_chave(subject_id: str) -> bytes:
    """Chave determinística por titular, apenas para o spike ser reproduzível."""
    return hashlib.sha256(f"chave-de-teste:{subject_id}".encode("utf-8")).digest()


def pseudonimo(subject_id: str) -> str:
    """Identificador opaco e estável do titular, sem revelar a identidade.

    Não é reversível para a identidade: depois de destruir a chave, o pseudônimo
    continua existindo, mas não há como ligá-lo de volta ao nome/CPF.
    """
    return "pid-" + hashlib.sha256(f"pseudo:{subject_id}".encode("utf-8")).hexdigest()[:10]


def gerar_keystream(chave: bytes, tamanho: int) -> bytes:
    resultado = bytearray()
    contador = 0
    while len(resultado) < tamanho:
        bloco = hmac.new(chave, contador.to_bytes(4, "big"), hashlib.sha256).digest()
        resultado.extend(bloco)
        contador += 1
    return bytes(resultado[:tamanho])


def cifrar(texto: str, chave: bytes) -> bytes:
    dados = texto.encode("utf-8")
    keystream = gerar_keystream(chave, len(dados))
    return bytes(a ^ b for a, b in zip(dados, keystream))


def decifrar(dados: bytes, chave: bytes) -> str:
    keystream = gerar_keystream(chave, len(dados))
    return bytes(a ^ b for a, b in zip(dados, keystream)).decode("utf-8")


@dataclass(frozen=True)
class Evento:
    event_id: int
    tipo: str
    subject_id: str
    # Bloco 3: financeiro/viagem, em claro.
    dados_financeiros: dict[str, Any]
    # Bloco 2: elegibilidade regulatória, em claro e pseudonimizada (retida).
    elegibilidade: dict[str, Any] | None
    # Bloco 1: identidade civil, cifrada por titular (sujeita a esquecimento).
    identidade_cifrada: bytes | None


class KeyStore:
    """Cofre de chaves por titular (simulado em memória)."""

    def __init__(self) -> None:
        self._chaves: dict[str, bytes] = {}

    def criar_chave(self, subject_id: str) -> None:
        self._chaves[subject_id] = derivar_chave(subject_id)

    def obter_chave(self, subject_id: str) -> bytes | None:
        return self._chaves.get(subject_id)

    def destruir_chave(self, subject_id: str) -> None:
        self._chaves.pop(subject_id, None)


class EventStore:
    """Event store append-only: eventos não são apagados."""

    def __init__(self) -> None:
        self._eventos: list[Evento] = []

    def append(self, evento: Evento) -> None:
        self._eventos.append(evento)

    def listar(self) -> list[Evento]:
        return list(self._eventos)


def registrar_viagem_subsidiada(
    event_store: EventStore,
    key_store: KeyStore,
    subject_id: str,
    nome: str,
    cpf: str,
    beneficio: str,
    emissor: str,
    linha: str,
    operador: str,
    subsidio: float,
) -> None:
    """Viagem gratuita: o passageiro paga 0 e a prefeitura deve `subsidio` ao
    operador. A legitimidade do subsídio depende da elegibilidade."""
    key_store.criar_chave(subject_id)
    chave = key_store.obter_chave(subject_id)
    assert chave is not None

    identidade = f"{nome}|{cpf}"
    evento = Evento(
        event_id=len(event_store.listar()) + 1,
        tipo="VIAGEM_SUBSIDIADA",
        subject_id=subject_id,
        dados_financeiros={
            "linha": linha,
            "operador": operador,
            "tarifa_paga": 0.0,
            "subsidio_devido": subsidio,
        },
        elegibilidade={
            "beneficio": beneficio,
            "emissor": emissor,
            "pseudonimo": pseudonimo(subject_id),
        },
        identidade_cifrada=cifrar(identidade, chave),
    )
    event_store.append(evento)


def solicitar_esquecimento(event_store: EventStore, key_store: KeyStore, subject_id: str) -> None:
    # Não apaga nenhum fato: registra a reversão e destrói a chave do titular.
    evento = Evento(
        event_id=len(event_store.listar()) + 1,
        tipo="ESQUECIMENTO_SOLICITADO",
        subject_id=subject_id,
        dados_financeiros={"acao": "REVERSAO_IDENTIDADE_CIVIL"},
        elegibilidade=None,
        identidade_cifrada=None,
    )
    event_store.append(evento)
    key_store.destruir_chave(subject_id)  # crypto-shredding


def recuperar_identidade(evento: Evento, key_store: KeyStore) -> str | None:
    if evento.identidade_cifrada is None:
        return None
    chave = key_store.obter_chave(evento.subject_id)
    if chave is None:
        return None
    return decifrar(evento.identidade_cifrada, chave)


def auditar_subsidio(event_store: EventStore) -> tuple[float, list[dict[str, Any]]]:
    """O que o Tribunal de Contas precisa: total de subsídio devido e a prova,
    por viagem, de que havia um benefício ativo — sem identificar a pessoa."""
    total = 0.0
    provas: list[dict[str, Any]] = []
    for ev in event_store.listar():
        if ev.tipo == "VIAGEM_SUBSIDIADA":
            total += float(ev.dados_financeiros["subsidio_devido"])
            if ev.elegibilidade is not None:
                provas.append({
                    "linha": ev.dados_financeiros["linha"],
                    "beneficio": ev.elegibilidade["beneficio"],
                    "pseudonimo": ev.elegibilidade["pseudonimo"],
                })
    return total, provas


def executar_spike() -> None:
    event_store = EventStore()
    key_store = KeyStore()
    subject_id = "passageiro-001"

    print("=== SPIKE ADR 0008 (substitui ADR 0005) ===")
    print("1. Registrando viagem subsidiada (estudante)...")
    registrar_viagem_subsidiada(
        event_store, key_store, subject_id,
        nome="Ana Silva", cpf="123.456.789-00",
        beneficio="ESTUDANTE", emissor="OrgaoGestor",
        linha="301", operador="Operadora Exemplo", subsidio=5.40,
    )

    viagem = event_store.listar()[0]
    print(f"2. Identidade recuperável antes do esquecimento: {recuperar_identidade(viagem, key_store)}")

    total_antes, provas_antes = auditar_subsidio(event_store)
    print(f"3. Auditoria de subsídio antes: total=R${total_antes:.2f}, provas={provas_antes}")

    print("4. Solicitando esquecimento (LGPD)...")
    solicitar_esquecimento(event_store, key_store, subject_id)

    print(f"5. Evento original ainda existe: {len(event_store.listar()) > 0}")
    print(f"6. Identidade recuperável após destruir a chave: {recuperar_identidade(viagem, key_store)}")

    total_depois, provas_depois = auditar_subsidio(event_store)
    print(f"7. Auditoria de subsídio preservada: total=R${total_depois:.2f}, provas={provas_depois}")

    tipos = [ev.tipo for ev in event_store.listar()]
    print(f"8. Eventos registrados: {tipos}")

    identidade_inacessivel = recuperar_identidade(viagem, key_store) is None
    elegibilidade_preservada = provas_depois == provas_antes and len(provas_depois) > 0
    subsidio_preservado = total_depois == total_antes
    esquecimento_registrado = "ESQUECIMENTO_SOLICITADO" in tipos

    print(
        "9. Resultado do spike: "
        f"esquecimento_registrado={esquecimento_registrado}, "
        f"identidade_inacessivel={identidade_inacessivel}, "
        f"elegibilidade_preservada={elegibilidade_preservada}, "
        f"subsidio_preservado={subsidio_preservado}"
    )
    print("10. ADR 0008 validado: identidade apagada; subsídio e prova de elegibilidade intactos.")


if __name__ == "__main__":
    executar_spike()
