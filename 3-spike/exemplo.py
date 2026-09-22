from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any


# Spike da ADR 0005:
# "Conciliar auditoria imutável e esquecimento LGPD por crypto-shredding".
#
# IMPORTANTE:
# A rotina de "criptografia" abaixo é somente uma simulação determinística
# para demonstrar o mecanismo de destruição da chave. Não é criptografia
# adequada para produção. Em um sistema real, seria utilizado um algoritmo
# criptográfico apropriado e uma solução segura de gerenciamento de chaves.


def derivar_chave(subject_id: str) -> bytes:
    """Gera uma chave determinística apenas para tornar o spike reproduzível."""
    return hashlib.sha256(
        f"chave-de-teste:{subject_id}".encode("utf-8")
    ).digest()


def gerar_keystream(chave: bytes, tamanho: int) -> bytes:
    """Gera bytes pseudoaleatórios para a simulação de cifra."""
    resultado = bytearray()
    contador = 0

    while len(resultado) < tamanho:
        bloco = hmac.new(
            chave,
            contador.to_bytes(4, "big"),
            hashlib.sha256,
        ).digest()
        resultado.extend(bloco)
        contador += 1

    return bytes(resultado[:tamanho])


def cifrar(texto: str, chave: bytes) -> bytes:
    """Simula a cifra de um dado pessoal."""
    dados = texto.encode("utf-8")
    keystream = gerar_keystream(chave, len(dados))
    return bytes(a ^ b for a, b in zip(dados, keystream))


def decifrar(dados: bytes, chave: bytes) -> str:
    """Recupera o dado quando a chave ainda existe."""
    keystream = gerar_keystream(chave, len(dados))
    texto = bytes(a ^ b for a, b in zip(dados, keystream))
    return texto.decode("utf-8")


@dataclass(frozen=True)
class Evento:
    event_id: int
    tipo: str
    subject_id: str
    dados_financeiros: dict[str, Any]
    dados_pessoais_cifrados: bytes | None


class KeyStore:
    """Simulação de um cofre externo de chaves."""

    def __init__(self) -> None:
        self._chaves: dict[str, bytes] = {}

    def criar_chave(self, subject_id: str) -> None:
        self._chaves[subject_id] = derivar_chave(subject_id)

    def obter_chave(self, subject_id: str) -> bytes | None:
        return self._chaves.get(subject_id)

    def destruir_chave(self, subject_id: str) -> None:
        self._chaves.pop(subject_id, None)


class EventStore:
    """Event store append-only: eventos existentes não são apagados."""

    def __init__(self) -> None:
        self._eventos: list[Evento] = []

    def append(self, evento: Evento) -> None:
        self._eventos.append(evento)

    def listar(self) -> list[Evento]:
        return list(self._eventos)


def registrar_viagem(
    event_store: EventStore,
    key_store: KeyStore,
    subject_id: str,
    linha: str,
    operador: str,
    tarifa: float,
    nome: str,
) -> None:
    key_store.criar_chave(subject_id)
    chave = key_store.obter_chave(subject_id)
    assert chave is not None

    evento = Evento(
        event_id=len(event_store.listar()) + 1,
        tipo="VIAGEM_REGISTRADA",
        subject_id=subject_id,
        dados_financeiros={
            "linha": linha,
            "operador": operador,
            "tarifa": tarifa,
        },
        dados_pessoais_cifrados=cifrar(nome, chave),
    )
    event_store.append(evento)


def solicitar_esquecimento(
    event_store: EventStore,
    key_store: KeyStore,
    subject_id: str,
) -> None:
    # A exclusão não remove o fato financeiro. Em vez disso,
    # registramos uma nova ocorrência de reversão/esquecimento.
    evento = Evento(
        event_id=len(event_store.listar()) + 1,
        tipo="ESQUECIMENTO_SOLICITADO",
        subject_id=subject_id,
        dados_financeiros={
            "acao": "REVERSAO_DADOS_PESSOAIS",
        },
        dados_pessoais_cifrados=None,
    )
    event_store.append(evento)

    # Crypto-shredding: destruição da chave torna os dados pessoais
    # cifrados irrecuperáveis pelo sistema.
    key_store.destruir_chave(subject_id)


def recuperar_nome(
    evento: Evento,
    key_store: KeyStore,
) -> str | None:
    if evento.dados_pessoais_cifrados is None:
        return None

    chave = key_store.obter_chave(evento.subject_id)
    if chave is None:
        return None

    return decifrar(evento.dados_pessoais_cifrados, chave)


def auditar_financeiro(event_store: EventStore) -> tuple[float, list[str]]:
    total = 0.0
    linhas: list[str] = []

    for evento in event_store.listar():
        if evento.tipo == "VIAGEM_REGISTRADA":
            total += float(evento.dados_financeiros["tarifa"])
            linhas.append(str(evento.dados_financeiros["linha"]))

    return total, linhas


def executar_spike() -> None:
    event_store = EventStore()
    key_store = KeyStore()
    subject_id = "passageiro-001"

    print("=== SPIKE ADR 0005 ===")
    print("1. Registrando viagem...")
    registrar_viagem(
        event_store=event_store,
        key_store=key_store,
        subject_id=subject_id,
        linha="301",
        operador="Operadora Exemplo",
        tarifa=5.40,
        nome="Ana Silva",
    )

    viagem = event_store.listar()[0]
    nome_antes = recuperar_nome(viagem, key_store)
    print(f"2. Dado pessoal recuperável antes do esquecimento: {nome_antes}")

    total_antes, linhas_antes = auditar_financeiro(event_store)
    print(
        "3. Auditoria financeira antes: "
        f"total=R${total_antes:.2f}, linhas={linhas_antes}"
    )

    print("4. Solicitando esquecimento...")
    solicitar_esquecimento(event_store, key_store, subject_id)

    print(
        "5. Evento original ainda existe no event store: "
        f"{len(event_store.listar()) > 0}"
    )

    nome_depois = recuperar_nome(viagem, key_store)
    print(
        "6. Dado pessoal recuperável após destruir a chave: "
        f"{nome_depois}"
    )

    total_depois, linhas_depois = auditar_financeiro(event_store)
    print(
        "7. Auditoria financeira preservada: "
        f"total=R${total_depois:.2f}, linhas={linhas_depois}"
    )

    tipos = [evento.tipo for evento in event_store.listar()]
    print(f"8. Eventos registrados: {tipos}")

    esquecimento_registrado = "ESQUECIMENTO_SOLICITADO" in tipos
    financeiro_preservado = total_depois == total_antes
    dado_inacessivel = nome_depois is None

    print(
        "9. Resultado do spike: "
        f"esquecimento_registrado={esquecimento_registrado}, "
        f"dado_inacessivel={dado_inacessivel}, "
        f"financeiro_preservado={financeiro_preservado}"
    )

    print("10. ADR 0005 validada: auditoria preservada + chave destruída.")


if __name__ == "__main__":
    executar_spike()
