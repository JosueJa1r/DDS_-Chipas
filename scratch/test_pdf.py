import urllib.request
import urllib.error
import json

def test():
    # 1. First get the diagnostic data
    url_diag = "http://127.0.0.1:5000/api/diagnostico_completo"
    payload = {
        "productor": {
            "nombre": "Juan Perez",
            "region": "Tapachula",
            "presupuesto": 90000,
            "experiencia": "3 años"
        },
        "suelo": {
            "ph": 6.2,
            "nitrogeno": 35,
            "materia_organica": 4.0
        },
        "superficie": 3.0
    }
    
    req_diag = urllib.request.Request(
        url_diag,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        print("Getting diagnostic data...")
        with urllib.request.urlopen(req_diag) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            
        # 2. Request PDF generation
        url_pdf = "http://127.0.0.1:5000/api/generar_pdf"
        print("Requesting PDF generation...")
        req_pdf = urllib.request.Request(
            url_pdf,
            data=json.dumps(res_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req_pdf) as response_pdf:
            pdf_content = response_pdf.read()
            with open("scratch/test_report.pdf", "wb") as f:
                f.write(pdf_content)
            print("Success! PDF report generated successfully at scratch/test_report.pdf")
            
    except urllib.error.HTTPError as e:
        print("HTTP Error:", e.code, e.read().decode('utf-8'))
    except Exception as e:
        print("Request failed:", e)

if __name__ == "__main__":
    test()
