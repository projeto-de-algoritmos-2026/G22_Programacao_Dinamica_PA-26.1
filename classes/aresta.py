from dataclasses import dataclass


@dataclass
class Aresta:
    origem: str
    destino: str
    taxa: float

    def __post_init__(self) -> None:
        self.origem = self.origem.strip().upper()
        self.destino = self.destino.strip().upper()
        self.taxa = float(self.taxa)

    def to_dict(self) -> dict:
        return {
            "origem": self.origem,
            "destino": self.destino,
            "taxa": self.taxa,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Aresta":
        return cls(
            origem=dados.get("origem", ""),
            destino=dados.get("destino", ""),
            taxa=dados.get("taxa", 0.0),
        )
