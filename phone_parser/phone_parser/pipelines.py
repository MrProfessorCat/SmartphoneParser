from datetime import datetime

import pandas as pd
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


class PhoneInfo(Base):
    __tablename__ = 'phone_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_name = Column(String(512))
    url = Column(Text)
    phone_os = Column(String(128))


class PhoneParserPipeline:
    def open_spider(self, spider):
        self.phones_op_systems = []
        engine = create_engine('sqlite:///sqlite.db')
        Base.metadata.create_all(engine)
        self.session = Session(engine)

    def process_item(self, item, spider):
        self.phones_op_systems.append(
            item.get('phone_os')
        )
        phone_info = PhoneInfo(**item)
        self.session.add(phone_info)
        self.session.commit()
        return item

    def close_spider(self, spider):
        if self.phones_op_systems:
            df = pd.DataFrame(self.phones_op_systems, columns=('OS version',))
            print(df.value_counts())
            df.value_counts().to_csv(
                'res.csv', encoding='utf-8',
                header=(
                    'OS versions stat on '
                    f'{datetime.now().strftime("%d.%m.%Y %H:%M")}'
                )
            )
        self.session.close()
