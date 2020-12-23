import pytablewriter as ptw
import json
import datetime
writer = ptw.ExcelXlsxTableWriter()
writer.format_table['cell']['font_name'] = 'Calibri'
writer.format_table['cell']['font_size'] = 12
writer.format_table['header']['font_name'] = 'Calibri'
writer.format_table['header']['font_size'] = 12

with open('swimmers.json') as file:
    j = json.load(file)

headers = ['name', 'gender', 'born', 'team', 'style', 'date', 'time', 'competition', 'age']
writer.headers = headers
writer.table_name = 'Tempusopen'
data = []
for swimmer in j:
    for style in swimmer['styles']:
        for time in style['times']:
            data.append([swimmer['name'], swimmer['gender'], swimmer['born'], swimmer['team'], style['name'], time['date'], time['time'],
                         time['competition'], datetime.datetime.strptime(time['date'], '%Y-%m-%d').year - int(swimmer['born'])])
writer.value_matrix = data
ofile = 'tempusopen.xlsx'
writer.dump(ofile)