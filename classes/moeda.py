from dataclasses import dataclass


@dataclass
class Moeda:
    nome: str
    sigla: str

    def __post_init__(self) -> None:
        self.nome = self.nome.strip()
        self.sigla = self.sigla.strip().upper()

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "sigla": self.sigla,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Moeda":
        return cls(
            nome=dados.get("nome", ""),
            sigla=dados.get("sigla", ""),
        )
