import os
import uuid
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, render_template, request, send_file, jsonify
from com.heciot.dss import DssReader
from dotenv import load_dotenv

# 初始化Flask应用
app = Flask(__name__)
load_dotenv()

# 配置
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['EXPORT_FOLDER'] = 'exports'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 最大上传50MB
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123456')

# 创建必要的文件夹
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)

# 设置matplotlib中文显示
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

def process_dss_file(file_path, dss_path):
    """处理DSS文件，生成PNG图表"""
    try:
        # 生成唯一的输出文件名
        output_filename = f"{uuid.uuid4()}.png"
        output_path = os.path.join(app.config['EXPORT_FOLDER'], output_filename)
        
        # 读取DSS文件
        reader = DssReader(file_path)
        data = reader.read(dss_path)
        
        # 转换为DataFrame
        df = pd.DataFrame({
            "time": data.times,
            "value": data.values
        })
        
        # 绘制图表
        plt.figure(figsize=(12, 6))
        plt.plot(df["time"], df["value"], linewidth=2, color="#2E86AB")
        plt.title("DSS数据可视化结果", fontsize=14)
        plt.xlabel("时间", fontsize=12)
        plt.ylabel("数值", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 保存为PNG
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        
        return output_filename, None
    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传和转换"""
    try:
        # 检查是否有文件上传
        if 'dssFile' not in request.files:
            return jsonify({"status": "error", "message": "请选择要上传的DSS文件"}), 400
        
        file = request.files['dssFile']
        dss_path = request.form.get('dssPath', '/PROJECT/FLOW/01JAN2020/1HOUR/VALUE/')
        
        if file.filename == '':
            return jsonify({"status": "error", "message": "文件名不能为空"}), 400
        
        # 保存上传的文件
        if file:
            # 生成唯一的文件名
            filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # 处理DSS文件
            output_filename, error = process_dss_file(file_path, dss_path)
            
            if error:
                return jsonify({"status": "error", "message": f"转换失败：{error}"}), 500
            
            # 返回成功结果
            return jsonify({
                "status": "success",
                "message": "转换完成",
                "downloadUrl": f"/download/{output_filename}"
            }), 200
    
    except Exception as e:
        return jsonify({"status": "error", "message": f"服务器错误：{str(e)}"}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """下载转换后的PNG文件"""
    try:
        file_path = os.path.join(app.config['EXPORT_FOLDER'], filename)
        return send_file(file_path, as_attachment=True, download_name="dss_result.png")
    except Exception as e:
        return jsonify({"status": "error", "message": f"下载失败：{str(e)}"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
