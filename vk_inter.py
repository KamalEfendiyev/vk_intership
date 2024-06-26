# -*- coding: utf-8 -*-
"""vk_inter

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16k9UwRxFknSxzBRFJykeBVBDPME9vB1Y
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd

# Загрузка датасета
data = pd.read_csv('/content/drive/MyDrive/intern_task.csv')

'''print(data.head())
print(data.info())
print(data.isnull().sum())
print(data.describe())'''

grouped_data = data.groupby('query_id')

print("Количество уникальных query_id:", len(grouped_data))
print("Размеры каждой группы:")
print(grouped_data.size())

import pandas as pd
import matplotlib.pyplot as plt

# Загрузка данных
#data = pd.read_csv('/content/drive/MyDrive/intern_task.csv')

# Определение колонок с числовыми данными и исключение 'rank' и 'query_id'
numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
numeric_cols = numeric_cols.drop(['rank', 'query_id'])  # Удаляем 'rank' и 'query_id' из списка

# Рассчитаем IQR для каждой числовой колонки и фильтруем выбросы
for column in numeric_cols:
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Удаление выбросов
    # data = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]

    # Замена выбросов на медиану
    median_value = data[column].median()
    data.loc[data[column] < lower_bound, column] = median_value
    data.loc[data[column] > upper_bound, column] = median_value

data.head()

import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Загрузка данных
#data = pd.read_csv('/content/drive/MyDrive/intern_task.csv')

# Определение колонок для масштабирования, исключая 'rank' и 'query_id'
numeric_cols = data.select_dtypes(include=['float64', 'int64']).columns
numeric_cols = numeric_cols.drop(['rank', 'query_id'])  # Исключаем столбцы rank и query_id

# Стандартизация
scaler_standard = StandardScaler()
data_standardized = data.copy()
data_standardized[numeric_cols] = scaler_standard.fit_transform(data[numeric_cols])

# Минимаксная нормализация
scaler_minmax = MinMaxScaler()
data_normalized = data.copy()
data_normalized[numeric_cols] = scaler_minmax.fit_transform(data[numeric_cols])

# Вывод результатов
print("Стандартизированные данные:")
print(data_standardized.head())

print("\nМинимакс нормализованные данные:")
print(data_normalized.head())

from sklearn.model_selection import train_test_split
import xgboost as xgb

# Разделяем данные на тренировочные и тестовые
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

# Создаем DMatrix, специфичные для XGBoost структуры данных
dtrain = xgb.DMatrix(train_data.drop(['rank', 'query_id'], axis=1), label=train_data['rank'])
dtest = xgb.DMatrix(test_data.drop(['rank', 'query_id'], axis=1), label=test_data['rank'])

# Параметры модели
params = {
    'objective': 'rank:pairwise',
    'learning_rate': 0.2,
    'max_depth': 6,
    'eval_metric': 'ndcg'
}

# Обучение модели
bst = xgb.train(params, dtrain, num_boost_round=100)

test_data['predictions'] = bst.predict(dtest)

# Подготовка данных для расчета NDCG
grouped = test_data.groupby('query_id').apply(
    lambda x: x.sort_values('predictions', ascending=False)
).reset_index(drop=True)

# Расчет NDCG@5 для каждой группы
ndcg_scores = []
for _, group in grouped.groupby('query_id'):
    true_relevance = group['rank'].tolist()
    scores = group['predictions'].tolist()

    # Обеспечиваем, что оба списка имеют форму списка списков и проверяем длину списка
    if len(true_relevance) >= 5:
        ndcg = ndcg_score([true_relevance], [scores], k=5)
        ndcg_scores.append(ndcg)

# Средний NDCG@5 по всем группам, где возможен расчет
if ndcg_scores:
    average_ndcg = np.mean(ndcg_scores)
    print(f"Averaged NDCG@5: {average_ndcg}")
else:
    print("Недостаточно данных для расчета NDCG@5.")