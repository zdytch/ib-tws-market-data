from schemas import InstrumentType, Exchange, Bar, ChartData


def get_instrument_type_by_exchange(exchange: Exchange) -> InstrumentType:
    if exchange in (Exchange.NASDAQ, Exchange.NYSE):
        instrument_type = InstrumentType.STOCK
    elif exchange in (Exchange.GLOBEX, Exchange.ECBOT, Exchange.NYMEX):
        instrument_type = InstrumentType.FUTURE
    else:
        raise ValueError(f'Cannot get instrument type, exchange unknown: {exchange}')

    return instrument_type


async def get_symbol_info(ticker: str) -> dict:
    exchange, symbol = tuple(ticker.split(':'))

    # instrument = await instrument_services.get_instrument_by_ticker(ticker)
    # instrument_type = chart_utils.convert_instrument_type_to_chart(instrument.type)
    # session, timezone = chart_utils.get_session_and_timezone(instrument.exchange)
    # price_scale = 10 ** abs(instrument.tick_size.normalize().as_tuple().exponent)
    # min_movement = int(instrument.tick_size * price_scale)

    return {
        'name': ticker,
        'ticker': ticker,
        # 'type': instrument_type,
        'description': 'Description',
        # 'exchange': instrument.exchange,
        # 'listed_exchange': instrument.exchange,
        'session': '1700-1600',
        'timezone': 'America/Chicago',
        # 'currency_code': 'USD',
        'has_daily': True,
        'has_intraday': True,
        'minmov': 1,
        'pricescale': 100,
    }


def get_config() -> dict:
    return {
        'supported_resolutions': ['1', '5', '30', '1D'],
        'supports_search': True,
        'supports_group_request': False,
        'supports_marks': False,
        'supports_timescale_marks': False,
    }


def convert_bar_list_to_chart_data(bar_list: list[Bar]) -> ChartData:
    # chart_data = {'t': [], 'h': [], 'l': [], 'o': [], 'c': [], 'v': [], 's': 'no_data'}
    chart_data = ChartData()
    for bar in bar_list:
        chart_data.o.append(bar.o)
        chart_data.h.append(bar.h)
        chart_data.l.append(bar.l)
        chart_data.c.append(bar.c)
        chart_data.v.append(bar.v)
        chart_data.t.append(bar.t)
    if all(value for value in chart_data.dict().values()):
        chart_data.s = 'ok'

    return chart_data
