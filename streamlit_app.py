import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# 尝试导入statsmodels，如果失败则使用简单预测方法
try:
    from statsmodels.tsa.arima.model import ARIMA
    from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
    USE_STATSMODELS = True
except Exception as e:
    st.write(f"statsmodels导入失败，使用简单预测方法: {str(e)}")
    USE_STATSMODELS = False

class SimpleForecaster:
    """简单预测器，使用移动平均方法"""
    def __init__(self):
        self.data = None
        self.dates = None
        self.y = None
    
    def load_data(self, df):
        if 'y' not in df.columns:
            raise ValueError("Excel文件必须包含名为'y'的列")
        
        if df['y'].isnull().any():
            raise ValueError("'y'列中存在缺失值，请检查数据")
        
        self.y = df['y'].values
        self.data = df
        
        if 'date' in df.columns:
            self.dates = df['date'].values
        else:
            self.dates = None
        
        return len(self.y)
    
    def one_step_ahead_forecast(self):
        if self.y is None:
            raise ValueError("请先加载数据")
        
        if USE_STATSMODELS:
            try:
                model = ARIMA(self.y, order=(2, 1, 2))
                fitted_model = model.fit()
                forecast = fitted_model.forecast(steps=1)
                return float(forecast[0])
            except:
                # 备选方案：使用移动平均
                return float(np.mean(self.y[-20:]))
        else:
            # 使用简单移动平均
            window_size = min(20, len(self.y))
            return float(np.mean(self.y[-window_size:]))
    
    def rolling_forecast(self, train_ratio=0.8):
        if self.y is None:
            raise ValueError("请先加载数据")
        
        n = len(self.y)
        train_size = int(n * train_ratio)
        train_data = self.y[:train_size]
        test_data = self.y[train_size:]
        
        predictions = []
        for i in range(len(test_data)):
            available_data = np.concatenate([train_data, test_data[:i]])
            
            if USE_STATSMODELS:
                try:
                    model = ARIMA(available_data, order=(2, 1, 2))
                    fitted_model = model.fit()
                    forecast = fitted_model.forecast(steps=1)
                    predictions.append(float(forecast[0]))
                except:
                    window_size = min(20, len(available_data))
                    predictions.append(float(np.mean(available_data[-window_size:])))
            else:
                window_size = min(20, len(available_data))
                predictions.append(float(np.mean(available_data[-window_size:])))
        
        # 计算指标
        mse = np.mean((np.array(test_data) - np.array(predictions)) ** 2)
        mae = np.mean(np.abs(np.array(test_data) - np.array(predictions)))
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((np.array(test_data) - np.array(predictions)) / np.array(test_data))) * 100
        
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

def main():
    st.set_page_config(page_title="时间序列预测系统", layout="wide")
    
    st.title("📊 时间序列预测系统")
    st.subheader("基于ARIMA模型的股票价格预测与回测平台")
    
    # 显示当前使用的预测方法
    st.info(f"当前预测方法: {'ARIMA模型' if USE_STATSMODELS else '移动平均法'}")
    
    # 初始化预测器
    if 'predictor' not in st.session_state:
        st.session_state.predictor = SimpleForecaster()
    
    # 文件上传
    st.markdown("---")
    st.header("📁 数据上传")
    
    uploaded_file = st.file_uploader("上传Excel文件（.xlsx格式）", type="xlsx")
    
    if uploaded_file is not None:
        try:
            # 读取Excel文件
            df = pd.read_excel(uploaded_file, sheet_name=0)
            
            # 加载数据
            n_samples = st.session_state.predictor.load_data(df)
            
            st.success(f"✅ 成功加载 {n_samples} 个样本")
            
            # 显示数据摘要
            st.subheader("数据摘要")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("样本数量", n_samples)
            col2.metric("均值", f"{np.mean(st.session_state.predictor.y):.6f}")
            col3.metric("标准差", f"{np.std(st.session_state.predictor.y):.6f}")
            col4.metric("包含日期列", "是" if st.session_state.predictor.dates is not None else "否")
            
            # 自动执行一步向前预测
            st.markdown("---")
            st.header("🔮 一步向前预测")
            with st.spinner("正在执行一步向前预测..."):
                forecast_value = st.session_state.predictor.one_step_ahead_forecast()
                st.success(f"预测完成！")
                st.metric("下一个时间点的预测值", f"{forecast_value:.6f}")
            
            # 自动执行回测
            st.markdown("---")
            st.header("📈 回测检验")
            with st.spinner("正在执行回测检验..."):
                backtest_result = st.session_state.predictor.rolling_forecast()
                
                st.subheader("回测结果")
                col1, col2 = st.columns(2)
                col1.metric("训练集大小", backtest_result['train_size'])
                col2.metric("测试集大小", backtest_result['test_size'])
                
                st.subheader("评估指标")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("均方误差 (MSE)", f"{backtest_result['metrics']['mse']:.6f}")
                col2.metric("平均绝对误差 (MAE)", f"{backtest_result['metrics']['mae']:.6f}")
                col3.metric("均方根误差 (RMSE)", f"{backtest_result['metrics']['rmse']:.6f}")
                col4.metric("平均绝对百分比误差 (MAPE)", f"{backtest_result['metrics']['mape']:.4f}%")
            
            # 导出功能
            st.markdown("---")
            st.header("📥 导出预测结果")
            
            output_data = {'y': backtest_result['predictions']}
            if st.session_state.predictor.dates is not None:
                train_size = backtest_result['train_size']
                test_dates = st.session_state.predictor.dates[train_size:]
                output_data['date'] = test_dates
            
            output_df = pd.DataFrame(output_data)
            
            output_buffer = BytesIO()
            output_df.to_excel(output_buffer, index=False, sheet_name='Sheet1')
            output_buffer.seek(0)
            
            st.download_button(
                label="下载预测结果",
                data=output_buffer,
                file_name='predictions.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        except Exception as e:
            st.error(f"❌ 错误: {str(e)}")
            import traceback
            st.exception(e)
    
    # 文件格式说明
    st.markdown("---")
    st.header("📋 文件格式要求")
    st.info("""
    - **文件类型**: .xlsx 格式
    - **必填列**: 名为 `y` 的列（时间序列数据）
    - **可选列**: 名为 `date` 的列（日期信息）
    - **数据要求**: y列不能有缺失值，按时间从早到晚排序
    """)

if __name__ == '__main__':
    main()