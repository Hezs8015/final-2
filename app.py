from flask import Flask, request, jsonify, send_file, render_template
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import mean_absolute_percentage_error
import io
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def index():
    return render_template('index.html')

class TimeSeriesPredictor:
    def __init__(self):
        self.data = None
        self.dates = None
        self.y = None
    
    def load_data(self, file_path):
        df = pd.read_excel(file_path, sheet_name=0)
        
        # 检查必需列
        if 'y' not in df.columns:
            raise ValueError("Excel文件必须包含名为'y'的列")
        
        # 检查缺失值
        if df['y'].isnull().any():
            raise ValueError("'y'列中存在缺失值，请检查数据")
        
        # 提取数据
        self.y = df['y'].values
        self.data = df
        
        # 提取日期列（如果存在）
        if 'date' in df.columns:
            self.dates = df['date'].values
        else:
            self.dates = None
        
        return len(self.y)
    
    def one_step_ahead_forecast(self):
        if self.y is None:
            raise ValueError("请先加载数据")
        
        # 使用ARIMA模型进行一步向前预测
        # 自动选择最优参数
        model = self._fit_arima(self.y)
        forecast = model.forecast(steps=1)
        
        return float(forecast[0])
    
    def rolling_forecast(self, train_ratio=0.8):
        if self.y is None:
            raise ValueError("请先加载数据")
        
        n = len(self.y)
        train_size = int(n * train_ratio)
        
        # 划分训练集和测试集
        train_data = self.y[:train_size]
        test_data = self.y[train_size:]
        
        # 滚动预测
        predictions = []
        for i in range(len(test_data)):
            # 使用到当前点为止的所有数据
            available_data = np.concatenate([train_data, test_data[:i]])
            
            # 拟合模型并预测
            model = self._fit_arima(available_data)
            forecast = model.forecast(steps=1)
            predictions.append(forecast[0])
        
        # 计算评估指标
        mse = mean_squared_error(test_data, predictions)
        mae = mean_absolute_error(test_data, predictions)
        rmse = np.sqrt(mse)
        mape = mean_absolute_percentage_error(test_data, predictions)
        
        return {
            'predictions': predictions,
            'test_data': test_data.tolist(),
            'metrics': {
                'mse': float(mse),
                'mae': float(mae),
                'rmse': float(rmse),
                'mape': float(mape)
            },
            'train_size': train_size,
            'test_size': len(test_data)
        }
    
    def _fit_arima(self, data):
        # 使用简化的ARIMA模型参数
        # 对于金融时间序列，通常使用ARIMA(1,1,1)或ARIMA(2,1,2)
        try:
            model = ARIMA(data, order=(2, 1, 2))
            fitted_model = model.fit()
            return fitted_model
        except:
            # 如果复杂模型失败，使用简单的ARIMA(1,1,1)
            model = ARIMA(data, order=(1, 1, 1))
            fitted_model = model.fit()
            return fitted_model

predictor = TimeSeriesPredictor()

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not file.filename.endswith('.xlsx'):
        return jsonify({'error': '只支持.xlsx格式的文件'}), 400
    
    try:
        # 保存临时文件
        file_path = 'temp_upload.xlsx'
        file.save(file_path)
        
        # 加载数据
        n_samples = predictor.load_data(file_path)
        
        # 获取数据摘要
        summary = {
            'n_samples': n_samples,
            'mean': float(np.mean(predictor.y)),
            'std': float(np.std(predictor.y)),
            'min': float(np.min(predictor.y)),
            'max': float(np.max(predictor.y)),
            'has_dates': predictor.dates is not None
        }
        
        return jsonify({
            'success': True,
            'message': f'成功加载 {n_samples} 个样本',
            'summary': summary
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/forecast', methods=['POST'])
def forecast():
    try:
        # 一步向前预测
        forecast_value = predictor.one_step_ahead_forecast()
        
        return jsonify({
            'success': True,
            'forecast': forecast_value,
            'message': f'下一个时间点的预测值: {forecast_value:.6f}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/backtest', methods=['POST'])
def backtest():
    try:
        # 回测检验
        result = predictor.rolling_forecast()
        
        return jsonify({
            'success': True,
            'result': result,
            'message': f'回测完成，测试集包含 {result["test_size"]} 个样本'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/export', methods=['POST'])
def export_results():
    try:
        # 执行回测
        result = predictor.rolling_forecast()
        
        # 创建输出DataFrame
        output_data = {'y': result['predictions']}
        
        # 如果原始数据有日期列，添加对应的日期
        if predictor.dates is not None:
            train_size = result['train_size']
            test_dates = predictor.dates[train_size:]
            output_data['date'] = test_dates
        
        output_df = pd.DataFrame(output_data)
        
        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            output_df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='predictions.xlsx'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/summary', methods=['GET'])
def get_summary():
    try:
        if predictor.y is None:
            return jsonify({'error': '请先上传数据'}), 400
        
        summary = {
            'n_samples': len(predictor.y),
            'mean': float(np.mean(predictor.y)),
            'std': float(np.std(predictor.y)),
            'min': float(np.min(predictor.y)),
            'max': float(np.max(predictor.y)),
            'has_dates': predictor.dates is not None
        }
        
        return jsonify({'success': True, 'summary': summary})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)