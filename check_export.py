import pandas as pd

df = pd.read_excel('test_predictions.xlsx')
print("导出的预测结果文件内容：")
print(df)
print(f"\n文件形状: {df.shape}")
print(f"列名: {df.columns.tolist()}")
print(f"\n前5行:")
print(df.head())
print(f"\n后5行:")
print(df.tail())