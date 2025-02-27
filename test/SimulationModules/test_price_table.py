from datetime import datetime, timedelta
import pytest
from config.logger_config import get_module_logger
logger = get_module_logger(__name__)

#@pytest.mark.skip
from SimulationModules.ElectricityCost.ElectricyPrice import PriceTable, StockPriceTable

@pytest.fixture
def stock_price_table():
    start_time = datetime(year=2022, month=8, day=8, hour=6)
    return StockPriceTable(start_time=start_time)

#at first, the simple price tabele is tested
def test_price_table():
    start_time = datetime.now()
    price_table = PriceTable(start_time=start_time)

def test_price_table_calc():
    start_time = datetime.now()
    price_table = PriceTable(start_time=start_time)
    value = price_table.get_price(timedelta(seconds= 100))


def test_price_table_prediction():

    start_time = datetime.now()
    simtime = start_time+ timedelta(hours=3)
    price_table = PriceTable(start_time=start_time)
    values = price_table.get_price_future(date_time=simtime-start_time, horizon=12, step_times=timedelta(seconds=900))
    logger.info(values)
    assert len(values)>1


def test_price_table_prediction_before_end():

    start_time = datetime.now()
    simtime = start_time+ timedelta(hours=23)
    price_table = PriceTable(start_time=start_time)
    values = price_table.get_price_future(date_time=simtime-start_time, horizon=12, step_times=timedelta(seconds=900))
    logger.info(values)
    assert len(values)>1


def test_price_table_future():
    start_time = datetime.now()
    simtime = start_time+ timedelta(hours=23, minutes=0, seconds=0)
    price_table = PriceTable(start_time=start_time)
    values, dt_array = price_table.get_price_future(date_time=simtime-start_time, horizon=12, step_times=timedelta(seconds=900))
    logger.info('\n')
    logger.info(f'Values are {values}')
    logger.info(f'Time vector is {dt_array}')


@pytest.mark.skip(reason="This test takes way too long for a unit test")
#then the pricetable which works with the stock market is tested
def test_stock_price_table(stock_price_table:StockPriceTable):
    #start_time = datetime(year=2022, month=8, day=8, hour=6)
    price_table = stock_price_table#StockPriceTable(start_time=start_time)
    assert price_table.get_price(timedelta(seconds= 7234)) == 414.68
    assert price_table.get_price(datetime(year=2022, month=8, day=8, hour=10)) == 339.44
    assert price_table.get_price(7234) == 414.68

    assert price_table.get_price(datetime(year=2023, month=12, day=23, hour=9)) == 42.08
    assert price_table.get_price(datetime(year=2024, month=7, day=3, hour=12)) == 71.76
    #for the following two cases, the code looks up the data for 202 instead
    assert price_table.get_price(datetime(year=2028, month=12, day=23, hour=9)) == 222.2
    assert price_table.get_price(datetime(year=2024, month=11, day=20, hour=7)) == 194.19

@pytest.mark.skip(reason="This test takes way too long for a unit test")
def test_stock_price_table_prediction_before_end(stock_price_table:StockPriceTable):

    start_time = datetime(year=2022, month=8, day=8, hour=6)
    simtime = start_time+ timedelta(hours=23)
    price_table = stock_price_table#StockPriceTable(start_time=start_time)
    values = price_table.get_price_future(date_time=simtime-start_time, horizon=12, step_time=timedelta(seconds=900))
    logger.info(values)
    assert len(values)>1
    
@pytest.mark.skip(reason="This test takes way too long for a unit test")
def test_convert_to_datetime(stock_price_table:StockPriceTable):
    start_time = datetime(year=2022, month=8, day=8, hour=0)
    price_table = stock_price_table#StockPriceTable(start_time=start_time)
    assert price_table.convert_to_datetime(3600) == datetime(year=2022, month=8, day=8, hour=1)
    assert price_table.convert_to_datetime(3600.0) == datetime(year=2022, month=8, day=8, hour=1)
    assert price_table.convert_to_datetime(timedelta(hours=2)) == datetime(year=2022, month=8, day=8, hour=2)
    assert price_table.convert_to_datetime(datetime(year=2022, month=8, day=8, hour=3)) == datetime(year=2022, month=8, day=8, hour=3)

@pytest.mark.skip(reason="This test takes way too long for a unit test")
def test_pick_future_prices(stock_price_table:StockPriceTable):
    start_time = datetime(year=2022, month=8, day=8, hour=6)
    simtime = start_time+ timedelta(hours=23)
    price_table =stock_price_table #StockPriceTable(start_time=start_time,
                                  #end_time=start_time+timedelta(days=5))
    values = price_table.get_price_future(date_time=simtime-start_time, horizon=12, step_time=timedelta(seconds=900))
    logger.info(values[0])
    assert len(values[0])==12
    assert values[0] == [320.01, 320.01, 320.01, 320.01, 
                      382.92, 382.92, 382.92, 382.92, 
                      414.98, 414.98, 414.98, 414.98]




