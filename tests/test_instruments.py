import pytest
from backend.core.instruments import Instrument, AssetClass, InstrumentService, DEFAULT_INSTRUMENTS

class TestInstrument:
    def test_create_spot(self):
        i = Instrument("BTCUSDT", "binance", AssetClass.CRYPTO_SPOT)
        assert i.symbol == "BTCUSDT"

    def test_create_perp(self):
        i = Instrument("BTCUSDT-PERP", "binance", AssetClass.PERP, leverage_allowed=True, max_leverage=20)
        assert i.leverage_allowed

    def test_to_dict(self):
        i = Instrument("AAPL", "alpaca", AssetClass.EQUITY)
        d = i.to_dict()
        assert d["asset_class"] == "EQUITY"

    def test_from_dict(self):
        d = {"symbol":"EURUSD","venue":"oanda","asset_class":"FX","tick_size":0.00001,"lot_size":1000}
        i = Instrument.from_dict(d)
        assert i.asset_class == AssetClass.FX

    def test_roundtrip(self):
        i = Instrument("TSLA", "alpaca", AssetClass.EQUITY, tick_size=0.01)
        assert Instrument.from_dict(i.to_dict()).symbol == "TSLA"

    @pytest.mark.parametrize("ac", list(AssetClass))
    def test_all_asset_classes(self, ac):
        i = Instrument("TEST", "test", ac)
        assert i.asset_class == ac

class TestInstrumentService:
    @pytest.fixture
    def svc(self):
        return InstrumentService()

    def test_list_all(self, svc):
        assert len(svc.list_all()) >= 5

    def test_get_existing(self, svc):
        assert svc.get("BTCUSDT") is not None

    def test_get_missing(self, svc):
        assert svc.get("NONEXISTENT") is None

    def test_register(self, svc):
        i = Instrument("DOGEUSDT", "binance", AssetClass.CRYPTO_SPOT)
        svc.register(i)
        assert svc.get("DOGEUSDT") is not None

    def test_list_by_class_equity(self, svc):
        equities = svc.list_by_class(AssetClass.EQUITY)
        assert all(i.asset_class == AssetClass.EQUITY for i in equities)

    def test_list_by_class_fx(self, svc):
        fx = svc.list_by_class(AssetClass.FX)
        assert len(fx) >= 1

    def test_default_instruments_count(self):
        assert len(DEFAULT_INSTRUMENTS) >= 5
