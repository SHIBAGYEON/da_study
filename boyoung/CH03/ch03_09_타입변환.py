# -*- coding: utf-8 -*-
"""CH03_09 타입변환

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SGB_IOW_9w5e48Q-jiOQeUf-eNToZ5rO

**타입 변환**

- 데이터 생성
"""

import pandas as pd

df = pd.DataFrame({'판매일': ['5/11/21','5/12/21', '5/13/21','5/14/21', '5/15/21'],
                   '판매량': ['10','15','20','25','30'], '방문자수':['10','-','17','23','25'], 
                   '기온': ['24.1','24.3','24.8','25','25.4']})

df

"""- 타입 확인"""

df.dtypes

# 판매량이 object여서 숫자로 변환해야됨
df['판매량 보정'] = df['판매량']+1

"""문제: 판매량을 정수 형태로 변환 하시오."""

# 타입을 바꾸어라 
df.astype({'판매량':'int'})

# 변수명을 따로 지정해줘야 바뀜
df.dtypes

df = df.astype({'판매량':'int'})

df.dtypes

df['판매량 보정'] = df['판매량']+1

df

"""- 문제: 방문자수를 숫자 타입으로 변형 하시오."""

# '-'가 있어서 int로 변환 불가
df.astype({'방문자수':'int'})

#
pd.to_numeric(df['방문자수'])

# 옵션을 사용하여, 에러가 발생하면 nan값으로 대체해라
pd.to_numeric(df['방문자수'], errors = 'coerce')

# df 방문자수 재정의 해줘야함
df.dtypes

df['방문자수'] = pd.to_numeric(df['방문자수'], errors = 'coerce')

df.dtypes

df

# NaN값 때문에 int 변환 에러 발생
df = df.astype({'방문자수':'int'})

df.fillna(0, inplace = True)

df.astype({'방문자수':'int'})

df

# 방문자수 정수형태 변환 확인
df.dtypes

df

"""- 문제: 판매일을 datetime의 형태로 바꾸시오."""

# pd.to_datetime 변환함수 
df['판매일'] = pd.to_datetime(df['판매일'], format ='%m/%d/%y')

df

df.dtypes

