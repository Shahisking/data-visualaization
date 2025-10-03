from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

app = Flask(__name__)

latest_result = {}

@app.route('/')
def home():
    return render_template("uploaded.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    global latest_result
    try:
        file = request.files['file']
        chart_type = request.form.get('chart_type')
        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        # Select target column (automatic for simplicity—let user choose in advanced case)
        col = df.select_dtypes(include=['object', 'category']).columns[0] if not df.select_dtypes(include=['object', 'category']).empty else df.columns[0]

        plt.figure(figsize=(8, 6))
        
        if chart_type == "bar":
            sns.countplot(x=col, data=df)
            plt.title(f"Bar Chart of {col}")
            plt.xlabel(col)
            plt.ylabel("Count")
            plt.xticks(rotation=30)
        elif chart_type == "line":
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col].plot(kind='line')
            else:
                df[col].value_counts().sort_index().plot(kind='line')
            plt.title(f"Line Chart of {col}")
            plt.xlabel(col)
            plt.ylabel("Value")
        elif chart_type == "pie":
            vc = df[col].value_counts().head(10)  # Limit to top 10 for readability
            vc.plot(kind='pie', autopct='%1.1f%%', startangle=140, legend=False)
            plt.ylabel('')
            plt.title(f"Pie Chart of {col}")
            plt.tight_layout()
        else:
            sns.countplot(x=col, data=df)  # default to bar

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")

        latest_result = {
            "chart": f"data:image/png;base64,{img_base64}",
            "columns": df.columns.tolist(),
            "preview": df.head(5).to_dict(orient="records")
        }
        return redirect(url_for("result"))

    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/result')
def result():
    return render_template("results.html", result=latest_result)

if __name__ == "__main__":
    app.run(debug=True)