import pandas as pd


class PhoneParserPipeline:
    def open_spider(self, spider):
        self.phones_op_systems = []

    def process_item(self, item, spider):
        self.phones_op_systems.append(
            item.get('phone_os')
        )
        return item

    def close_spider(self, spider):
        df = pd.DataFrame(self.phones_op_systems, columns=('OS version',))
        print(df.value_counts())
        df.value_counts().to_csv('res.csv', encoding='utf-8')
