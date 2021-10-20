from typing import Optional
from common.repositories import BaseRepository
from sqlalchemy.future import select
from .models import Instrument, InstrumentType, TradingSession


class InstrumentRepo(BaseRepository):
    async def search_by_symbol_and_type(
        self, symbol: Optional[str], type: Optional[InstrumentType]
    ) -> list[Instrument]:
        async with self._session_factory() as session:
            async with session.begin():
                query = select(self._model_class)

                if symbol:
                    query = query.where(self._model_class.symbol.contains(symbol))
                if type:
                    query = query.filter_by(type=type)

            result = await session.execute(query)

            return result.scalars().all()


instrument_repo = InstrumentRepo(Instrument)
trading_session_repo = BaseRepository(TradingSession)
