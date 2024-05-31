import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import pymysql

import pymysql
from sqlalchemy import create_engine
from sqlalchemy import create_engine
from datetime import datetime
import pandas as pd
import urllib.parse

# 转义密码中的特殊字符
password = urllib.parse.quote_plus('abc123!@#')

# 创建数据库引擎，插入转义后的密码
cnn = create_engine(f'mysql+pymysql://sibider:{password}@rm-7xv214kbc13b54959do.mysql.rds.aliyuncs.com:3306/test123?charset=utf8mb4')


# 准备SQL查询
sql = "select * from ods_speed_saz_dpi;"

# 执行SQL查询，并将结果加载到DataFrame
df = pd.read_sql_query(sql, cnn)

# 打印DataFrame的数据类型
print(df.dtypes)