import pandas as pd

# 读取数据集
df = pd.read_excel('dataset.xlsx')

print("数据集信息：")
print(f"数据形状: {df.shape}")
print(f"\n列名: {df.columns.tolist()}")
print(f"\n前5行数据:")
print(df.head())
print(f"\n数据类型:")
print(df.dtypes)
print(f"\n缺失值统计:")
print(df.isnull().sum())
print(f"\n数据统计信息:")
print(df.describe())