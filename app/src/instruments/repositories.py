from common.repositories import BaseRepository
from .models import Instrument, TradingSession

instrument_repo = BaseRepository(Instrument)
trading_session_repo = BaseRepository(TradingSession)
