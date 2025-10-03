from flask import Flask, request, render_template
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/visualize', methods=['POST'])
def visualize():
    file = request.files['file']

    if file.filename.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
        df = pd.read_excel(file)
    else:
        return "Unsupported file type", 400

    numeric_cols = df.select_dtypes(include='number').columns
    if len(numeric_cols) == 0:
        return "No numeric columns found for visualization", 400

    col = numeric_cols[0]
    ax = df[col].value_counts().plot(kind='bar')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return render_template('result.html', image_data=img_base64, column=col)

if __name__ == '__main__':
    app.run(debug=True)