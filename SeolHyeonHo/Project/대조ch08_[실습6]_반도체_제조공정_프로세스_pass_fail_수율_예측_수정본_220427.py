# -*- coding: utf-8 -*-
"""대조ch08-[실습6]-반도체-제조공정-프로세스-pass-fail-수율-예측-수정본-220427.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1reGTlanbFRqo0mB_S2wyykxnVoctwEBz

* [uci-secom.csv] : https://www.kaggle.com/paresh2047/uci-semcom

#Part4. [실습6] 반도체 제조 공정 프로세스 Pass_Fail 수율 예측

* matplotlib 한글 깨짐 현상 해결
> 셀 실행 후 런타임 재시작 필요
"""

# import matplotlib.pyplot as plt

# !apt-get update -qq
# !apt-get install fonts-nanum* -qq

# import matplotlib.font_manager as fm

# path = '/usr/share/fonts/truetype/nanum/NanumGothicEco.ttf'
# font_name = fm.FontProperties(fname=path, size=10).get_name()

# plt.rc('font', family=font_name)

# fm._rebuild()

from google.colab import drive
drive.mount('/content/drive')

from matplotlib import pyplot as plt
plt.rc('font', family='NanumBarunGothic')

"""## 01. 데이터 소개 및 분석프로세스 수립
 : "강의자료 → Ch04. [실습6] 반도체 제조 공정 프로세스 Pass_Fail 수율 예측" 참고

## 02. 데이터 준비를 위한 EDA 및 전처리

### 0. 데이터 불러오기
"""

############################################## 00. 필요한 파이썬 라이브러리 불러오기 #####################################################
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('fivethirtyeight')

# Plotly
import plotly.offline as py
py.init_notebook_mode(connected=True)
import plotly.graph_objs as go
import plotly.tools as tls

from sklearn.model_selection import train_test_split

import xgboost as xgb
from xgboost.sklearn import XGBClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import Lasso
from sklearn.svm import OneClassSVM

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# data = pd.read_csv('/content/drive/MyDrive/강의/01_패스트캠퍼스_머신러닝실습프로젝트/실습자료/data/ch6/uci-secom.csv')
data = pd.read_csv('/content/drive/MyDrive/강의 /01_패스트캠퍼스_머신러닝실습프로젝트/실습자료/data/ch6/uci-secom.csv')
data.head()

# 데이터의 모양 알아보기
data.shape

"""### 1. 데이터 탐색

#### 1) 데이터 타입
"""

# 컬럼별 데이터 타입 알아보기
data.info()

"""#### 2) 데이터 통계값"""

# 컬럼별 간단한 통계값 보기
data.describe()

"""#### 3) 결측값"""

data.isnull().any().any()

"""#### 4) 중복값"""

# 중복된 항목 수 알아보기
print("중복된 항목 수 :", len(data[data.duplicated()]))

"""### 2. 데이터 전처리

#### 1. 결측값 채우기
"""

# NaN 을 0으로 채우기
data = data.replace(np.NaN, 0)

# 결측값 확인
data.isnull().any().any()

"""### 3. Target Feature 정의

#### 1) 데이터 탐색
"""

data['Pass/Fail'].unique()

"""> Pie Chart"""

labels = ['Pass', 'Fail']
size = data['Pass/Fail'].value_counts()
colors = ['blue', 'green']
explode = [0, 0.1]

plt.style.use('seaborn-deep')
plt.rcParams['figure.figsize'] = (8, 8)
plt.pie(size, labels =labels, colors = colors, explode = explode, autopct = "%.2f%%", shadow = True)
plt.axis('off')
plt.title('Target: Pass or Fail', fontsize = 20)
plt.legend()
plt.show()
data['Pass/Fail'].value_counts().plot(kind="bar");

"""* 매우 불균형한 데이터

#### 2) 각 센서별 Target Feature 분포
"""

unique_vals = data['Pass/Fail'].unique()
targets = [data.loc[data['Pass/Fail'] == val] for val in unique_vals]

targets

fig = plt.figure(figsize=(20,20))

plt.subplot(2, 2, 1)
for target in targets:
    sns.distplot(target['1'], hist=True, rug=True)
plt.title('1번 센서 계측값', fontsize = 20)

plt.subplot(2, 2, 2)
for target in targets:
    sns.distplot(target['2'], hist=True, rug=True)
plt.title('2번 센서 계측값', fontsize = 20)

plt.subplot(2, 2, 3)
for target in targets:
    sns.distplot(target['3'], hist=True, rug=True)
plt.title('3번 센서 계측값', fontsize = 20)

plt.subplot(2, 2, 4)
for target in targets:
    sns.distplot(target['4'], hist=True, rug=True)
plt.title('4번 센서 계측값', fontsize = 20)

#sns.add_legend()
#plt.legend()
fig.legend(labels=['Pass','Fail'])
plt.show()

"""### 4. 상관성에 따른 Feature 정제

#### 1) 히트맵 확인
"""

plt.rcParams['figure.figsize'] = (18, 18)
sns.heatmap(data.corr(), cmap = "YlGnBu")
plt.title('상관 히트맵', fontsize = 20)

"""#### 2) 상관계수

##### 상관계수 필터링 함수

> 입력한 상관계수 threshold 에 따라 Feature 들 필터링하는 함수 정의
"""

# 상관계수 구하기
data.corr()

def remove_collinear_features(x, threshold):
    # 데이터프레임 x 의 상관계수 구하기
    corr_matrix = x.corr()
    # Pass / Fail 을 제외한 컬럼수
    iters = range(len(corr_matrix.columns) - 1)
    # 제거할 컬럼들 저장할 리스트
    drop_cols = []

    for i in iters:
        for j in range(i+1):

            # j행 (i+1)열 상관계수 가져오기
            item = corr_matrix.iloc[j:(j+1), (i+1):(i+2)]
            # 상관계수 셀의 컬럼명 가져오기
            col = item.columns
            # 상관계수 셀의 행 인덱스 가져오기
            row = item.index
            # 상관계수의 절대값
            val = abs(item.values)

            if val >= threshold:
                print(col.values[0], "열", row.values[0], "행의 상관계수 : ", round(val[0][0], 2))
                drop_cols.append(col.values[0])

    drops = set(drop_cols)
    x = x.drop(columns=drops)

    return x

threshold = 0.70
data = remove_collinear_features(data,threshold)

data.shape

"""#### 3) 머신러닝 모델 입력 데이터 생성"""

# Time 컬럼 삭제
data = data.drop(columns = ['Time'], axis = 1)

data.shape

data.head()

"""### 5. Target Feature 불균형 문제 처리

#### 1. UnderSampling

> 데이터 탐색
"""

# Pass 라벨이 1 인 데이터 개수 구하기
failed_tests = data[data['Pass/Fail'] == 1]
number_failed_tests = len(failed_tests)
print(number_failed_tests)

# Pass 라벨이 -1 인 데이터 개수 구하기
normal_indices = data[data['Pass/Fail'] == -1]
number_normal_indices = len(normal_indices)
print(number_normal_indices)

#Pass 라벨(값이 1)에서 랜덤으로 104개 가져오기
###### 코드 작성 부분 시작 ######
random_normal_indices = np.random.choice(number_normal_indices, size = number_failed_tests, replace = True)
random_normal_indices = np.array(random_normal_indices)
###### 코드 작성 부분 마침######
print(len(random_normal_indices))

# Pass 라벨값이 -1인 데이터에서 Pass 라벨이 1 인 데이터 개수만큼 랜덤으로 가져오기
random_normal_indices = normal_indices.sample(n=number_failed_tests, replace = False)
print(random_normal_indices.shape)

# 같은 비율로 합친 Pass/Fail 데이터 생성
under_sample = np.concatenate([failed_tests.index, random_normal_indices.index])
print(len(under_sample))

undersample_data = data.iloc[under_sample, :]

undersample_data['Pass/Fail'].value_counts()

x = undersample_data.iloc[:, undersample_data.columns != 'Pass/Fail']
y = undersample_data.iloc[:, undersample_data.columns == 'Pass/Fail']

print(x.shape)
print(y.shape)

# 언더샘플링 데이터 훈련/테스트 데이터 분할
from sklearn.model_selection import train_test_split

x_train_us, x_test_us, y_train_us, y_test_us = train_test_split(x, y, test_size = 0.3, random_state = 1)

print(x_train_us.shape)
print(y_train_us.shape)
print(x_test_us.shape)
print(y_test_us.shape)

# StandardScaler 적용
sc = StandardScaler()
x_train_us = sc.fit_transform(x_train_us)
x_test_us = sc.transform(x_test_us)

"""#### 2. OverSampling using SMOTE"""

# SMOTE 적용
x_resample, y_resample  = SMOTE(random_state=1).fit_resample(x, y.values.ravel())

print(x_resample.shape)
print(y_resample.shape)

x_train_os, x_test_os, y_train_os, y_test_os = train_test_split(x, y, test_size = 0.3, random_state = 1)

print(x_train_os.shape)
print(y_train_os.shape)
print(x_test_os.shape)
print(y_test_os.shape)

# standardScale 적용
sc = StandardScaler()
x_train_os = sc.fit_transform(x_train_os)
x_test_os = sc.transform(x_test_os)

"""## 03. 머신러닝 모델링

### 1) 데이터 준비
"""

data.head()

x = data.iloc[:,:(data.shape[1]-1)]
y = data["Pass/Fail"]

print("shape of x:", x.shape)
print("shape of y:", y.shape)

# 훈련/테스트 데이터 세트 나누기
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.3, random_state = 1)

print("shape of x_train: ", x_train.shape)
print("shape of x_test: ", x_test.shape)
print("shape of y_train: ", y_train.shape)
print("shape of y_test: ", y_test.shape)

"""### 2) 다양한 Classifier 와 Grid Search 를 활용한 최적 모델 탐색

#### 1. Feature Scailing
"""

from sklearn.preprocessing import StandardScaler

# StandardScaler 선언
sc = StandardScaler()
# StandardScaler 에 fit_transform
x_train = sc.fit_transform(x_train)
x_test = sc.transform(x_test)

"""#### 2. XGBoost (Scaled 데이터)"""

xg = XGBClassifier(random_state=1)
xg.fit(x_train, y_train)
y_pred = xg.predict(x_test)

"""> Confusion Matrix"""

cm = confusion_matrix(y_test, y_pred)
plt.rcParams['figure.figsize'] = (5, 5)
sns.set(style = 'dark', font_scale = 1.4)
sns.heatmap(cm, annot = True, annot_kws = {"size": 15})

print("Accuracy: ", xg.score(x_test,y_test)*100)

"""#### 3. RandomForest (Scaled 데이터)"""

rf = RandomForestClassifier(n_estimators=100, random_state=1,verbose=0 )
rf.fit(x_train, y_train)
y_pred = rf.predict(x_test)

"""> Confusion Matrix"""

cm = confusion_matrix(y_test, y_pred)
plt.rcParams['figure.figsize'] = (5, 5)
sns.set(style = 'dark', font_scale = 1.4)
sns.heatmap(cm, annot = True, annot_kws = {"size": 15})

print("Accuracy: ", rf.score(x_test,y_test)*100)

"""#### 4. Logistic Regression (Scaled 데이터)"""

lr = LogisticRegression(random_state=1)
lr.fit(x_train, y_train)
y_pred = lr.predict(x_test)

"""> Confusion Matrix"""

cm = confusion_matrix(y_test, y_pred)
plt.rcParams['figure.figsize'] = (5, 5)
sns.set(style = 'dark', font_scale = 1.4)
sns.heatmap(cm, annot = True, annot_kws = {"size": 15})

print("Accuracy: ", lr.score(x_test,y_test)*100)

"""#### 5. Lasso (Scaled 데이터)"""

lasso = Lasso(alpha=0.1,random_state=1)
lasso.fit(x_train,y_train)
y_pred = lasso.predict(x_test)

# 예측값의 부호를 classifier 로 변환
y_pred2 = np.sign(y_pred)

print("Accuracy: ", lasso.score(x_test,y_test)*100)

"""> Confusion Matrix"""

cm = confusion_matrix(y_test, y_pred2)
sns.heatmap(cm, annot = True, cmap = 'rainbow')

"""### 3) 언더샘플링 데이터 대상 재모델링

#### 1. XGBoost (Undersampled 데이터)
"""

model = XGBClassifier(random_state=1)
model.fit(x_train_us, y_train_us)
y_pred = model.predict(x_test_us)

"""> Confusion Matrix"""

cm = confusion_matrix(y_test_us, y_pred)

plt.rcParams['figure.figsize'] = (5, 5)
sns.set(style = 'dark', font_scale = 1.4)
sns.heatmap(cm, annot = True, annot_kws = {"size": 15})

print("Accuracy: ", model.score(x_test,y_test)*100)

"""#### 2. Grid Search - XGBoost (Undersampled 데이터)"""

parameters = [{'max_depth' : [1, 2, 3, 4, 5, 6],
              'cv' : [2,4,6,8,10],
              'random_state' : [1]}]

grid_search = GridSearchCV(estimator = model, param_grid = parameters, scoring = 'accuracy',  n_jobs = -1)

grid_search = grid_search.fit(x_train_us, y_train_us)
best_accuracy = grid_search.best_score_
best_parameters = grid_search.best_params_

print("Best Accuracy: ", best_accuracy*100)
print("Best Parameter: ", best_parameters)

# scale_pos_weights 사용
weights = (y == 0).sum()/(1.0*(y == -1).sum())

model = XGBClassifier(max_depth = 3, scale_pos_weights = weights, n_jobs = 4,random_state=1,cv=2)
model.fit(x_train_us, y_train_us)
y_pred = model.predict(x_test_us)

print("Accuracy: ", model.score(x_test,y_test)*100)

"""> Confusion Matrix"""

cm = confusion_matrix(y_test_us, y_pred)

plt.rcParams['figure.figsize'] = (5, 5)
sns.set(style = 'dark', font_scale = 1.4)
sns.heatmap(cm, annot = True, annot_kws = {"size": 15})

"""#### 2. Random Forest (Undersampled 데이터)"""

model = RandomForestClassifier(n_estimators=100, random_state=1,verbose=0 )
model.fit(x_train_us, y_train_us)
y_pred = model.predict(x_test_us)

"""> Confusion Matrix"""

cm = confusion_matrix(y_test_us, y_pred)

plt.rcParams['figure.figsize'] = (5, 5)
sns.set(style = 'dark', font_scale = 1.4)
sns.heatmap(cm, annot = True, annot_kws = {"size": 15})

print("Accuracy: ", model.score(x_test,y_test)*100)

"""#### 3. Logistic Regression (Undersampled 데이터)"""

lr = LogisticRegression(random_state=1)
lr.fit(x_train_us, y_train_us)

y_pred = lr.predict(x_test_us)

"""**Confusion matrix for Logistic Regression (Undersampled)**"""

cm = confusion_matrix(y_test_us, y_pred)

plt.rcParams['figure.figsize'] = (5, 5)
sns.set(style = 'dark', font_scale = 1.4)
sns.heatmap(cm, annot = True, annot_kws = {"size": 15})

print("Accuracy: ", lr.score(x_test,y_test)*100)

"""#### 4. Lasso (Undersampled 데이터)"""

lasso = Lasso(alpha=0.1,random_state=1)
lasso.fit(x_train_us,y_train_us)
#print ("Lasso model:", (lasso.coef_))

y_pred = lasso.predict(x_test_us)

print(y_pred)

print(y_test_us)

y_pred2 = np.sign(y_pred)

"""> Confusion Matrix"""

cm = confusion_matrix(y_test_us, y_pred2)

plt.rcParams['figure.figsize'] = (5, 5)
sns.set(style = 'dark', font_scale = 1.4)
sns.heatmap(cm, annot = True, annot_kws = {"size": 15})

print("Accuracy: ", lasso.score(x_test_us,y_test_us)*100)

"""### 4) 오버샘플링 데이터 대상 재모델링

#### 1. Grid Search - XGBoost (Oversampled 데이터)
"""

import xgboost as xgb
from xgboost.sklearn import XGBClassifier

model = XGBClassifier(random_state=1)
model.fit(x_train_os, y_train_os)
y_pred = model.predict(x_test_os)

from sklearn.model_selection import GridSearchCV

parameters = [{'max_depth' : [1, 2, 3, 4, 5, 6],
              'cv' : [2,4,6,8,10],
              'random_state' : [1]}]

grid_search = GridSearchCV(estimator = model, param_grid = parameters, scoring = 'accuracy', n_jobs = -1)
grid_search = grid_search.fit(x_train_os, y_train_os)

best_accuracy = grid_search.best_score_
best_parameters = grid_search.best_params_

print("Best Accuracy: ", best_accuracy)
print("Best Parameter: ", best_parameters)

weights = (y == 0).sum()/(1.0*(y == -1).sum())

model = XGBClassifier(max_depth = 1, scale_pos_weights = weights, n_jobs = 4,random_state=1,cv=2)
model.fit(x_train_os, y_train_os)
y_pred = model.predict(x_test_os)

"""> Confusion Matrix"""

cm = confusion_matrix(y_test_os, y_pred)

plt.rcParams['figure.figsize'] = (5, 5)
sns.set(style = 'dark', font_scale = 1.4)
sns.heatmap(cm, annot = True, annot_kws = {"size": 15}, cmap = 'spring')

print("Accuracy: ", model.score(x_test,y_test)*100)

"""#### 2. Random Forest (Oversampled 데이터)"""

model = RandomForestClassifier(n_estimators=100, random_state=1,verbose=0 )
model.fit(x_train_os, y_train_os)
y_pred = model.predict(x_test_os)
print("Accuracy: ", model.score(x_test_os,y_test_os)*100)

"""> Confusion Matrix"""

# printing the confusion matrix
cm = confusion_matrix(y_test_os, y_pred)
sns.heatmap(cm, annot = True, cmap = 'rainbow')

"""#### 3. Logistic Regression (Oversampled 데이터)"""

lr = LogisticRegression(random_state=1)
lr.fit(x_train_os, y_train_os)
y_pred = lr.predict(x_test_os)

print("Accuracy: ", lr.score(x_test_os,y_test_os)*100)

"""> Confusion Matrix"""

cm = confusion_matrix(y_test_os, y_pred)
sns.heatmap(cm, annot = True, cmap = 'rainbow')

"""### 5) PCA 를 활용한 차원 축소"""

data.shape

"""#### 1. Scailing using zscore"""

from scipy.stats import zscore
data_new=data.iloc[:,:306].apply(zscore)
data_new.head()

data_new.isnull().any().any()

data_new = data_new.replace(np.NaN, 0)

data_new.isnull().any().any()

x = data_new.iloc[:,:306]
y = data["Pass/Fail"]

print("shape of x:", x.shape)
print("shape of y:", y.shape)

"""#### 2. PCA Step 1 - Covariance Matrix 만들기"""

cov_matrix = np.cov(x.T)
print('Covariance Matrix \n%s', cov_matrix)

"""#### 3. PCA Step 2 - Eigen Values 와 Eigen Vector 만들기"""

eig_vals, eig_vecs = np.linalg.eig(cov_matrix)
print('Eigen Vectors \n%s', eig_vecs)
print('\n Eigen Values \n%s', eig_vals)

tot = sum(eig_vals)
var_exp = [( i /tot ) * 100 for i in sorted(eig_vals, reverse=True)]
cum_var_exp = np.cumsum(var_exp)
print("누적 분산 설명력", cum_var_exp)

plt.plot(var_exp)

"""> Explained Variance Ratio : 각각의 주성분 벡터가 이루는 축에 투영(projection)한 결과의 분산의 비율 (=각 eigenvalue 의 비율)"""

# Ploting plt.figure(figsize=(10 , 5))
plt.bar(range(1, eig_vals.size + 1), var_exp, alpha = 0.5, align = 'center', label = 'Individual explained variance')
plt.step(range(1, eig_vals.size + 1), cum_var_exp, where='mid', label = 'Cumulative explained variance')
plt.ylabel('Explained Variance Ratio')
plt.xlabel('Principal Components')
plt.legend(loc = 'best')
plt.tight_layout()
plt.show()

len(cum_var_exp)

"""#### 4. Scikit-learn 으로 PCA 적용하기


"""

# Using scikit learn PCA here. It does all the above steps and maps data to PCA dimensions in one shot
from sklearn.decomposition import PCA

pca = PCA(n_components=130)
data_reduced = pca.fit_transform(x)
data_reduced.transpose()

pca.components_

df_comp = pd.DataFrame(pca.components_,columns=list(x))
df_comp.head()

plt.figure(figsize=(12,6))
sns.heatmap(df_comp,cmap='plasma',)

"""> PCA 적용된 데이터 탐색"""

data_reduced.shape

df_red2 = pd.DataFrame(data_reduced)
df_red2.head()

"""> Pass/Fail 데이터 합치기"""

df_red3 = df_red2.copy()
df_red4 = df_red3
df_red4["Pass/Fail"] = data["Pass/Fail"]

df_red4.head()

df_red4.shape

"""#### 5. 이상치 제거

> Pass/Fail 별 PCA 데이터의 이상치 탐색
"""

df_red4.boxplot(column = [df_red4.columns[0],
                          df_red4.columns[1],
                          df_red4.columns[2],
                          df_red4.columns[3],
                          df_red4.columns[4],
                          df_red4.columns[5],
                         ]
                          , by = 'Pass/Fail', figsize=(20,20))

"""> 이상치 제거 적용 (Quantile, IQR 사용)"""

pd_data = df_red4.copy()

from scipy import stats

def outlier_removal_max(var):
    var = np.where(var > var.quantile(0.75)+ stats.iqr(var),var.quantile(0.50),var)
    return var

def outlier_removal_min(var):
    var = np.where(var < var.quantile(0.25) - stats.iqr(var),var.quantile(0.50),var)
    return var

for column in pd_data:
    pd_data[column] = outlier_removal_max(pd_data[column])
    pd_data[column] = outlier_removal_min(pd_data[column])

pd_data.boxplot( column =[df_red4.columns[0],
                          df_red4.columns[1],
                          df_red4.columns[2],
                          df_red4.columns[3],
                          df_red4.columns[4],
                          df_red4.columns[5],
                         ],by = 'Pass/Fail', figsize=(20,20))

"""### 6) PCA 적용+이상치 제거 데이터 재모델링

#### 1. 언더샘플링
"""

x = df_red4.iloc[:, df_red4.columns != 'Pass/Fail']
y = df_red4.iloc[:, df_red4.columns == 'Pass/Fail']

print("shape of x:", x.shape)
print("shape of y:", y.shape)

failed_tests = np.array(df_red4[df_red4['Pass/Fail'] == 1].index)
no_failed_tests = len(failed_tests)

print(no_failed_tests)

normal_indices = df_red4[df_red4['Pass/Fail'] == -1]
no_normal_indices = len(normal_indices)

print(no_normal_indices)

random_normal_indices = np.random.choice(no_normal_indices, size = no_failed_tests, replace = True)
random_normal_indices = np.array(random_normal_indices)

print(len(random_normal_indices))

under_sample = np.concatenate([failed_tests, random_normal_indices])
print(len(under_sample))

undersample_data = df_red4.iloc[under_sample, :]

x = undersample_data.iloc[:, undersample_data.columns != 'Pass/Fail']
y = undersample_data.iloc[:, undersample_data.columns == 'Pass/Fail']

print(x.shape)
print(y.shape)

from sklearn.model_selection import train_test_split

x_train_us, x_test_us, y_train_us, y_test_us = train_test_split(x, y, test_size = 0.3, random_state = 1)

print(x_train_us.shape)
print(y_train_us.shape)
print(x_test_us.shape)
print(y_test_us.shape)

"""#### 1. XGBoost-PCA (Undersampled 데이터)"""

model = XGBClassifier(random_state=1)
model.fit(x_train_us, y_train_us)
y_pred = model.predict(x_test_us)

"""> Confusion Matrix"""

cm = confusion_matrix(y_test_us, y_pred)

plt.rcParams['figure.figsize'] = (5, 5)
sns.set(style = 'dark', font_scale = 1.4)
sns.heatmap(cm, annot = True, annot_kws = {"size": 15})

print("Accuracy: ", model.score(x_test_us,y_test_us)*100)

"""#### 2. Grid Search - XGBoost - PCA (Undersampled 데이터)"""

parameters = [{'max_depth' : [1, 2, 3, 4, 5, 6],
              'cv' : [2,4,6,8,10],
             'random_state' : [1]}]

grid_search = GridSearchCV(estimator = model, param_grid = parameters, scoring = 'accuracy', n_jobs = -1)

grid_search = grid_search.fit(x_train_us, y_train_us)
best_accuracy = grid_search.best_score_
best_parameters = grid_search.best_params_

print("Best Accuracy: ", best_accuracy*100)
print("Best Parameter: ", best_parameters)

weights = (y == 0).sum()/(1.0*(y == -1).sum())

model = XGBClassifier(max_depth = 4, scale_pos_weights = weights, n_jobs = 4,random_state=1,cv=2)
model.fit(x_train_us, y_train_us)
y_pred = model.predict(x_test_us)

print("Accuracy: ", model.score(x_test_us,y_test_us)*100)

"""> Confusion Matrix"""

cm = confusion_matrix(y_test_us, y_pred)

plt.rcParams['figure.figsize'] = (5, 5)
sns.set(style = 'dark', font_scale = 1.4)
sns.heatmap(cm, annot = True, annot_kws = {"size": 15})

"""#### 3. Random Forest - PCA (Undersampled 데이터)"""

model = RandomForestClassifier(n_estimators=100, random_state=1,verbose=0 )
model.fit(x_train_us, y_train_us)
y_pred = model.predict(x_test_us)

cm = confusion_matrix(y_test_us, y_pred)
sns.heatmap(cm, annot = True, cmap = 'rainbow')

print("Accuracy: ", model.score(x_test_us,y_test_us)*100)

"""#### 3. Logistic Regression - PCA (Undersampled 데이터)"""

lr = LogisticRegression(random_state=1)
lr.fit(x_train_us, y_train_us)
y_pred = lr.predict(x_test_us)

cm = confusion_matrix(y_test_us, y_pred)
sns.heatmap(cm, annot = True, cmap = 'rainbow')

print("Accuracy: ", lr.score(x_test_us,y_test_us)*100)

"""#### 4. Lasso - PCA (Undersampled 데이터)"""

lasso = Lasso(alpha=0.1,random_state=1)
lasso.fit(x_train_us,y_train_us)

y_pred = lasso.predict(x_test_us)

y_pred2 = np.sign(y_pred)

actual_cost = list(y_test_us)
actual_cost = np.asarray(actual_cost)
y_pred_lass = lasso.predict(x_test_us)

print("Accuracy: ", lasso.score(x_test_us, y_test_us)*100)

"""> Confusion Matrix"""

cm = confusion_matrix(y_test_us, y_pred2)
sns.heatmap(cm, annot = True, cmap = 'rainbow')

"""### Feature Importances"""

from numpy import loadtxt
from xgboost import XGBClassifier
from xgboost import plot_importance
from matplotlib import pyplot

model = XGBClassifier()
model.fit(x_train_us, y_train_us)

import plotly.io as pio
pio.renderers.default = 'notebook_connected'
pio.renderers
pio.renderers.default = 'colab'
pio.renderers

trace = go.Scatter(
    y = model.feature_importances_,
    x = x_train_us.columns.values,
    mode='markers',
    marker=dict(
        sizemode = 'diameter',
        sizeref = 1,
        size = 13,
        color = model.feature_importances_,
        colorscale='Portland',
        showscale=True
    ),
    text = x_train_us.columns.values
)
data = [trace]

layout= go.Layout(
    autosize= True,
    title= 'Gradient Boosting Model Feature Importance',
    hovermode= 'closest',
     xaxis= dict(
         ticklen= 5,
         showgrid=False,
        zeroline=False,
        showline=False
     ),
    yaxis=dict(
        title= 'Feature Importance',
        showgrid=False,
        zeroline=False,
        ticklen= 5,
        gridwidth= 2
    ),
    showlegend= False
)
fig = go.Figure(data=data, layout=layout)
py.iplot(fig,filename='scatter')