from ib_insync import IB, Contract, Stock, ContFuture
from schemas import Timeframe, InstrumentType, Bar
from datetime import datetime
import ib_utils
from loguru import logger


logger.add(
    'logs/ib_sync_{time}.log',
    format='{time} {level} {message}',
    level='DEBUG',
    rotation='100 MB',
    retention='14 days',
    compression='zip',
)


class IBConnector:
    def __init__(self):
        self._ib = IB()

    @property
    def is_connected(self) -> bool:
        return self._ib.isConnected()

    async def get_historical_bars(
        self,
        symbol: str,
        exchange: str,
        instrument_type: InstrumentType,
        timeframe: Timeframe,
        from_dt: datetime,
        to_dt: datetime,
    ) -> list[Bar]:
        await self._connect()

        bars = []
        if self.is_connected:
            contract = await self._get_contract(InstrumentType.FUTURE, symbol, exchange)
            is_stock = instrument_type == InstrumentType.STOCK
            volume_multiplier = 100 if is_stock else 1

            ib_bars = await self._ib.reqHistoricalDataAsync(
                contract=contract,
                endDateTime=to_dt,
                durationStr=ib_utils.duration_to_ib(from_dt, to_dt),
                barSizeSetting=ib_utils.timeframe_to_ib(timeframe),
                whatToShow='TRADES',
                useRTH=is_stock,
                formatDate=2,
                keepUpToDate=False,
            )

            for ib_bar in ib_bars:
                bar = ib_utils.bar_from_ib(ib_bar, volume_multiplier)
                bars.append(bar)

        return bars

    async def _connect(self, client_id=1):
        if not self.is_connected:
            try:
                await self._ib.connectAsync('dataserver-ib', 4002, client_id)
            except Exception as error:
                logger.error(error)

    async def _get_contract(
        self, instrument_type: InstrumentType, symbol: str, exchange: str
    ) -> Contract:
        if instrument_type == InstrumentType.STOCK:
            contract = Stock(symbol, f'SMART:{exchange}', 'USD')
        elif instrument_type == InstrumentType.FUTURE:
            contract = ContFuture(symbol, f'SMART:{exchange}', currency='USD')
        else:
            raise ValueError(
                f'Cannot get contract for type {instrument_type}, '
                f'symbol {symbol}, exchange {exchange}'
            )

        if contract:
            await self._ib.qualifyContractsAsync(contract)
            if not contract.conId:
                raise ValueError(f'Cannot qualify contract {contract}')

        return contract
