from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from cotton_market_crew.store import MercadoStore, MercadoStoreError


@pytest.fixture
def diretorio_dados(tmp_path: Path) -> Path:
    (tmp_path / "indicador_fisico.csv").write_text(
        "data,regiao,reais_por_arroba\n"
        "2026-07-20,MT,155.00\n"
        "2026-07-21,MT,158.50\n"
        "2026-07-20,BA,150.00\n"
    )
    (tmp_path / "cotacao_futura.csv").write_text(
        "data,contrato,cents_por_libra\n"
        "2026-07-20,DEZ26,70.10\n"
        "2026-07-21,DEZ26,71.35\n"
    )
    (tmp_path / "cambio.csv").write_text(
        "data,ptax_venda\n2026-07-20,5.3000\n2026-07-21,5.3421\n"
    )
    return tmp_path


class TestMercadoStore:
    def test_lista_todos_indicadores(self, diretorio_dados: Path):
        store = MercadoStore(diretorio_dados)

        assert len(store.listar_indicadores()) == 3

    def test_filtra_indicadores_por_regiao(self, diretorio_dados: Path):
        store = MercadoStore(diretorio_dados)

        indicadores_mt = store.listar_indicadores(regiao="MT")

        assert len(indicadores_mt) == 2
        assert all(i.regiao == "MT" for i in indicadores_mt)

    def test_ultimo_indicador_retorna_data_mais_recente(self, diretorio_dados: Path):
        store = MercadoStore(diretorio_dados)

        ultimo = store.ultimo_indicador("MT")

        assert ultimo.data == date(2026, 7, 21)
        assert ultimo.reais_por_arroba == Decimal("158.50")

    def test_ultimo_indicador_regiao_sem_dados_levanta_erro(
        self, diretorio_dados: Path
    ):
        store = MercadoStore(diretorio_dados)

        with pytest.raises(MercadoStoreError):
            store.ultimo_indicador("GO")

    def test_ultima_cotacao_futura(self, diretorio_dados: Path):
        store = MercadoStore(diretorio_dados)

        ultima = store.ultima_cotacao_futura()

        assert ultima.data == date(2026, 7, 21)
        assert ultima.cents_por_libra == Decimal("71.35")

    def test_ultimo_cambio(self, diretorio_dados: Path):
        store = MercadoStore(diretorio_dados)

        ultimo = store.ultimo_cambio()

        assert ultimo.ptax_venda == Decimal("5.3421")

    def test_calcular_basis_usa_ultimos_valores_disponiveis(
        self, diretorio_dados: Path
    ):
        store = MercadoStore(diretorio_dados)

        basis = store.calcular_basis("MT")

        # físico: 158.50 R$/@ com PTAX 5.3421 -> 89.72 cents/lb
        # futuro: 71.35 cents/lb (DEZ26, última data)
        # basis: 89.72 - 71.35 = 18.37
        assert basis.regiao == "MT"
        assert basis.valor_cents_por_libra == Decimal("18.37")

    def test_diretorio_inexistente_levanta_erro(self, tmp_path: Path):
        with pytest.raises(MercadoStoreError):
            MercadoStore(tmp_path / "nao_existe")


class TestMercadoStoreComDadosDoRepositorio:
    """Testes de integração contra os CSVs versionados em `dados/`."""

    def test_carrega_dados_padrao_do_repositorio(self):
        store = MercadoStore()

        assert len(store.listar_indicadores()) > 0
        assert len(store.listar_cotacoes_futuras()) > 0
        assert len(store.listar_cambios()) > 0

    def test_calcula_basis_para_cada_regiao_configurada(self):
        store = MercadoStore()

        for regiao in ("MT", "BA", "GO"):
            basis = store.calcular_basis(regiao)
            assert basis.regiao == regiao
