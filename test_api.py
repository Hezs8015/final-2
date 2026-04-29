import requests
import pandas as pd
import json

API_BASE = 'http://localhost:5000/api'

def test_upload():
    print("测试1: 上传Excel文件")
    files = {'file': open('dataset.xlsx', 'rb')}
    response = requests.post(f'{API_BASE}/upload', files=files)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_forecast():
    print("\n测试2: 一步向前预测")
    response = requests.post(f'{API_BASE}/forecast')
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    return response.json()

def test_backtest():
    print("\n测试3: 回测检验")
    response = requests.post(f'{API_BASE}/backtest')
    print(f"状态码: {response.status_code}")
    result = response.json()
    if result.get('success'):
        print(f"训练集大小: {result['result']['train_size']}")
        print(f"测试集大小: {result['result']['test_size']}")
        print(f"MSE: {result['result']['metrics']['mse']:.6f}")
        print(f"MAE: {result['result']['metrics']['mae']:.6f}")
        print(f"RMSE: {result['result']['metrics']['rmse']:.6f}")
    else:
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    return result

def test_export():
    print("\n测试4: 导出预测结果")
    response = requests.post(f'{API_BASE}/export')
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        with open('test_predictions.xlsx', 'wb') as f:
            f.write(response.content)
        print("预测结果已保存到 test_predictions.xlsx")
        
        # 读取并显示前几行
        df = pd.read_excel('test_predictions.xlsx')
        print(f"\n导出文件预览:")
        print(df.head())
        print(f"\n导出文件形状: {df.shape}")
        print(f"导出文件列名: {df.columns.tolist()}")
    return response

if __name__ == '__main__':
    try:
        # 依次测试各个功能
        upload_result = test_upload()
        
        if upload_result.get('success'):
            forecast_result = test_forecast()
            backtest_result = test_backtest()
            export_result = test_export()
            
            print("\n" + "="*50)
            print("所有测试完成！")
            print("="*50)
        else:
            print("\n上传失败，跳过后续测试")
            
    except Exception as e:
        print(f"\n测试过程中出现错误: {str(e)}")