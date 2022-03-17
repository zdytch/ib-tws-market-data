from ib_insync import IB, Contract
from instruments.models import Exchange, InstrumentType
from bars.models import Bar, BarSet
from .schemas import InstrumentInfo
from common.schemas import Interval
from decimal import Decimal
from . import utils
from common.utils import round_with_quantum
from loguru import logger


class IBConnector:
    def __init__(self):
        self._ib = IB()
        self._ib.errorEvent += self._error_callback

    @property
    def is_connected(self) -> bool:
        return self._ib.isConnected()

    async def get_instrument_info(
        self, symbol: str, exchange: Exchange
    ) -> InstrumentInfo:
        await self._connect()

        contract = self._get_contract(symbol, exchange)
        await self._ib.qualifyContractsAsync(contract)
        details = await self._ib.reqContractDetailsAsync(contract)

        type = utils.get_instrument_type_by_exchange(exchange)
        is_stock = type == InstrumentType.STOCK
        (
            tr_symbol,
            tr_multiplier,
            tr_tick_size,
            tr_description,
            _,
        ) = self._get_special_case_translated_values(symbol, exchange, type)

        ib_symbol = tr_symbol or symbol
        description = tr_description or details[0].longName
        multiplier = tr_multiplier or ('1.00' if is_stock else contract.multiplier)
        tick_size = tr_tick_size or ('0.01' if is_stock else str(details[0].minTick))
        trading_hours = details[0].liquidHours if is_stock else details[0].tradingHours
        nearest_trading_interval = utils.get_nearest_trading_interval(
            trading_hours, details[0].timeZoneId
        )

        return InstrumentInfo(
            symbol=symbol,
            ib_symbol=ib_symbol,
            exchange=exchange,
            type=type,
            description=description,
            tick_size=Decimal(tick_size),
            multiplier=Decimal(multiplier),
            nearest_session=nearest_trading_interval,
        )

    async def get_historical_bars(
        self,
        bar_set: BarSet,
        interval: Interval,
    ) -> list[Bar]:
        await self._connect()

        instrument = bar_set.instrument
        contract = self._get_contract(instrument.symbol, instrument.exchange)
        is_stock = instrument.type == InstrumentType.STOCK
        volume_multiplier = 100 if is_stock else 1

        ib_bars = await self._ib.reqHistoricalDataAsync(
            contract=contract,
            endDateTime=interval.end,
            durationStr=utils.duration_to_ib(interval.start, interval.end),
            barSizeSetting=utils.timeframe_to_ib(bar_set.timeframe),
            whatToShow='TRADES',
            useRTH=is_stock,
            formatDate=2,
            keepUpToDate=False,
        )

        bars = []
        for ib_bar in ib_bars:
            tick_size = instrument.tick_size
            timestamp = utils.timestamp_from_ib(ib_bar.date)

            if interval.start <= timestamp <= interval.end:
                bar = Bar(
                    bar_set_id=bar_set.id,
                    open=round_with_quantum(Decimal(ib_bar.open), tick_size),
                    high=round_with_quantum(Decimal(ib_bar.high), tick_size),
                    low=round_with_quantum(Decimal(ib_bar.low), tick_size),
                    close=round_with_quantum(Decimal(ib_bar.close), tick_size),
                    volume=int(ib_bar.volume) * volume_multiplier,
                    timestamp=timestamp,
                )

                bars.append(bar)

        return bars

    async def search_instrument_info(self, symbol: str) -> list[InstrumentInfo]:
        await self._connect()

        results = []
        for type in tuple(InstrumentType):
            contract = self._get_contract(symbol, instrument_type=type)
            details = await self._ib.reqContractDetailsAsync(contract)

            for item in details:
                if item.contract:
                    exchange = (
                        item.contract.primaryExchange
                        if type == InstrumentType.STOCK
                        else item.contract.exchange
                    )
                    if exchange in tuple(Exchange) and not next(
                        (res for res in results if res.exchange == exchange), None
                    ):
                        instrument_info = await self.get_instrument_info(
                            symbol, Exchange(exchange)
                        )
                        results.append(instrument_info)

        return results

    async def _connect(self, client_id=14):
        if not self.is_connected:
            await self._ib.connectAsync('trixter-ib', 4002, client_id)

    def _get_contract(
        self,
        symbol: str,
        exchange: Exchange | None = None,
        instrument_type: InstrumentType | None = None,
    ) -> Contract:
        (
            tr_symbol,
            tr_multiplier,
            _,
            _,
            is_contract_spec,
        ) = self._get_special_case_translated_values(symbol, exchange, instrument_type)
        contract_symbol = tr_symbol or symbol
        contract_multiplier = tr_multiplier if is_contract_spec else ''
        contract_type = utils.security_type_to_ib(exchange, instrument_type)

        if contract_type == 'STK':
            contract_exchange = f'SMART:{exchange.value}' if exchange else 'SMART'
        else:
            contract_exchange = exchange.value if exchange else ''

        return Contract(
            symbol=contract_symbol,
            exchange=contract_exchange,
            secType=contract_type,
            multiplier=contract_multiplier,
            currency='USD',
        )

    def _error_callback(
        self, req_id: int, error_code: int, error_string: str, contract: Contract
    ) -> None:
        logger.debug(f'{req_id} {error_code} {error_string} {contract}')

    def _get_special_case_translated_values(
        self,
        symbol: str,
        exchange: Exchange | None = None,
        instrument_type: InstrumentType | None = None,
    ) -> tuple:
        tr_symbol = ''
        tr_multiplier = ''
        tr_tick_size = ''
        tr_description = ''
        is_contract_spec = False

        if symbol == 'SIL' and (
            exchange == Exchange.NYMEX or instrument_type == InstrumentType.FUTURE
        ):
            tr_symbol = 'SI'
            tr_multiplier = '1000'
            tr_description = 'Silver Micro Futures'
            is_contract_spec = True

        elif symbol in ('ZC', 'ZS', 'ZW') and (
            exchange == Exchange.ECBOT or instrument_type == InstrumentType.FUTURE
        ):
            tr_multiplier = '50'
            tr_tick_size = '0.25'

        elif symbol == 'ZL' and (
            exchange == Exchange.ECBOT or instrument_type == InstrumentType.FUTURE
        ):
            tr_multiplier = '600'
            tr_tick_size = '0.01'

        return tr_symbol, tr_multiplier, tr_tick_size, tr_description, is_contract_spec


ib_connector = IBConnector()
