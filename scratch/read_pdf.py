import pypdf

def extract():
    try:
        reader = pypdf.PdfReader("Diversificación de cultivos y análisis de suelo.pdf")
        with open("scratch/pdf_text.txt", "w", encoding="utf-8") as f:
            f.write(f"Total Pages: {len(reader.pages)}\n\n")
            for idx, page in enumerate(reader.pages):
                f.write(f"--- Page {idx+1} ---\n")
                text = page.extract_text()
                f.write(text)
                f.write("\n\n")
        print("Success! Extracted text saved to scratch/pdf_text.txt")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    extract()
