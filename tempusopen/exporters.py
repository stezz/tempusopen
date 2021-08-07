from scrapy.exporters import BaseItemExporter
import pytablewriter as ptw
import datetime


class XlsxItemExporter(BaseItemExporter):
    def __init__(self, file, **kwargs):
        self._configure(kwargs, dont_fail=True)
        self.file = file
        self.first_item = True

    def start_exporting(self):
        self.writer = ptw.ExcelXlsxTableWriter()
        self.writer.format_table['cell']['font_name'] = 'Calibri'
        self.writer.format_table['cell']['font_size'] = 12
        self.writer.format_table['header']['font_name'] = 'Calibri'
        self.writer.format_table['header']['font_size'] = 12
        headers = ['name', 'gender', 'born', 'team', 'style', 'date', 'FINA', 'time', 'competition', 'age']
        self.writer.headers = headers
        self.writer.table_name = 'Tempusopen'
        self.data = []

    def finish_exporting(self):
        self.writer.value_matrix = self.data
        self.writer.dump(self.file)

    def export_item(self, item):
        for style in item['styles']:
            print('this is style', style)
            for time in style['times']:
                print('this is time', time)
                self.data.append([item['name'], item['gender'], item['born'],
                                  item['team'], style['name'], time['date'], time['FINA'], time['time'],
                                  time['competition'],
                                  datetime.datetime.strptime(time['date'], '%Y-%m-%d').year
                                  - int(item['born'])])
