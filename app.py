import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import PyPDF2
from dotenv import load_dotenv  # .env dosyasını yüklemek için



load_dotenv()


app = Flask(__name__)

# Sabit API Key ve PDF yolu
API_KEY = os.getenv("OPENAI_API_KEY")
PDF_PATH = "yonerge.pdf"  # Sabit PDF yolu

class PDFChatAssistant:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.system_prompt = """
Sen bir PDF doküman analiz asistanısın. Sorulan soruya:
- Kısa ve öz cevap ver
- Yalnızca PDF içeriğinden bilinen bilgileri kullan
- Gereksiz detaylardan kaçın
- Net ve anlaşılır bir dil kullan
-pdf harici sorulara "maalesef sorduğunuz soru pdf ile ilgili değil" yaz 
"""

    def ask_gpt(self, pdf_content, question):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"PDF İçeriği: {pdf_content}"},
                {"role": "user", "content": f"Soru: {question}"}
            ],
            max_tokens=300,
            temperature=0.5
        )
        return response.choices[0].message.content

def extract_pdf_content(file_path):
    pdf_reader = PyPDF2.PdfReader(file_path)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask-question', methods=['POST'])
def ask_question():
    # PDF içeriğini çıkar
    pdf_content = extract_pdf_content(PDF_PATH)
    
    question = request.form.get('question')
    
    if not question:
        return jsonify({"status": "error", "message": "Soru boş bırakılamaz"})
    
    assistant = PDFChatAssistant(API_KEY)
    answer = assistant.ask_gpt(pdf_content, question)
    
    return jsonify({"status": "success", "answer": answer})

if __name__ == '__main__':
    # Eğer documents klasörü yoksa oluştur
    os.makedirs('documents', exist_ok=True)
    app.run(debug=True)