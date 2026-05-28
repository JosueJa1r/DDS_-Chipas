import urllib.request
import urllib.error
import json

def test():
    url = "http://127.0.0.1:5000/api/diagnostico_completo"
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
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            print("Status Code:", status_code)
            res_data = json.loads(response.read().decode('utf-8'))
            print("Keys in response:", list(res_data.keys()))
            print("\nAnalisis Avanzado Crop:", res_data["analisis_avanzado"]["cultivo"])
            print("Gauss pH Points Count:", len(res_data["analisis_avanzado"]["gauss_ph"]))
            print("Scatter Parcelas Count:", len(res_data["analisis_avanzado"]["correlacion"]["parcelas"]))
            print("Monte Carlo Hist Bins:", len(res_data["analisis_avanzado"]["montecarlo"]["histograma"]))
            print("Monte Carlo Prob Exito:", res_data["analisis_avanzado"]["montecarlo"]["probabilidad_exito"])
            print("Monte Carlo Equilibrio (Ton):", res_data["analisis_avanzado"]["montecarlo"]["rendimiento_equilibrio"])
            print("\nSuccess! API behaves as expected.")
    except urllib.error.HTTPError as e:
        print("HTTP Error:", e.code, e.read().decode('utf-8'))
    except Exception as e:
        print("Request failed:", e)

if __name__ == "__main__":
    test()
