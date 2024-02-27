from scrapy.item import Item, Field
from scrapy.spiders import Spider
from scrapy.selector import Selector
from datetime import datetime
from scrapy.loader import ItemLoader
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import os
from sqlalchemy import text
import uuid
from sqlalchemy import inspect

# Obtener la ruta absoluta del archivo de logs
log_file = os.path.join(os.path.dirname(__file__), 'app.log')

# Configurar el logger
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#from extraccion import Rate, Rate_BCV
Base = declarative_base()

class Rate(Base):
    __tablename__ = 'tasa'
    id = Column(Integer, Sequence('tasa_id_seq'), primary_key=True)
    uuid = Column(String, default=str(uuid.uuid4()), unique=True)
    moneda_id = Column(Integer)
    valor = Column(Numeric(10, 2))
    fecha_tasa = Column(DateTime)


class Rate_Struct(Item):
    rate = Field()
    date = Field()

class Rate_BCV(Spider):
    name = "rate_BCV"
    start_urls = ['http://www.bcv.org.ve/']

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 10,
        'DOWNLOAD_DELAY': 2,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
    }

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
    
    engine = create_engine('sqlite:///rates.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Verificar si la tabla ya existe en la base de datos
    inspector = inspect(engine)
    if 'tasa' not in inspector.get_table_names():
        Base.metadata.create_all(engine)
    
    def parse(self, response):
        sel = Selector(response)
        rate = sel.xpath('//div[@id="dolar"]//strong/text()')
        item = ItemLoader(Rate_Struct(), rate)
        _rate = self.__cast_rate__(rate.extract_first())
        item.add_value('rate', _rate)
        #item.add_value('date', datetime.now().strftime('%Y-%m-%d'))
        item.add_value('date', datetime.now())
        rate_item = item.load_item()
        self.save_to_database(rate_item)
        yield rate_item

    def __cast_rate__(self, rate):
        rate = rate.replace(',', '.').strip()
        
        try:
            rate = round(float(rate), 2)
        except Exception as e:
            logging.error(f"Error occurred while casting rate: {e}")
            rate = 0
        return rate

    def save_to_database(self, rate_item):

        #fecha = datetime.strptime(rate_item['date'][0], '%Y-%m-%d').date()
        fecha = rate_item['date'][0]
        valor = rate_item['rate'][0]

        rate = Rate(moneda_id=1,valor=valor,fecha_tasa=fecha)
        self.session.add(rate)
        self.session.commit()

        return rate



        def save_to_database(self, rate_item):
            fecha = rate_item['date'][0]
            valor = rate_item['rate'][0]
            query = text("""INSERT INTO rates (
                 moneda_id,
                 valor,
                 fecha_tasa
                 ) VALUES (
                    :moneda_id, 
                    :valor,
                    :fecha_tasa
                    )
                 """)
            self.session.execute(query,
             {'moneda_id': 2,
              'valor': valor,
              'fecha_tasa': fecha 
               })
            self.session.commit()

    def __del__(self):
        self.session.close()


    
