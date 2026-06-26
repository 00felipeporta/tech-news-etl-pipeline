import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime, timedelta

print("Iniciando el pipeline...")

# 1. EXTRACT: Descargar el HTML real de internet
url = "https://news.ycombinator.com/newest"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

response = requests.get(url, headers=headers)
if response.status_code != 200:
    print(f"Error al acceder a la web: {response.status_code}")
    exit()

soup = BeautifulSoup(response.text, "html.parser")

# 2. TRANSFORM: Procesar la información cruda
datos_noticias = []

# En Hacker News, los títulos están en una fila (athing) y los metadatos en la siguiente
filas_titulos = soup.find_all("tr", class_="athing")

for fila in filas_titulos:
    try:
        # Extraer ID y Título
        id_noticia = fila.get("id")
        elemento_titulo = fila.find("span", class_="titleline")
        if not elemento_titulo:
            continue
        titulo = elemento_titulo.find("a").text
        
        # Buscar la fila de metadatos asociada (es la siguiente en el HTML)
        fila_meta = fila.find_next_sibling("tr")
        elemento_tiempo = fila_meta.find("span", class_="age")
        
        texto_tiempo = elemento_tiempo.text if elemento_tiempo else "hace 0 minutos"
        # PROCESAMIENTO CRUDO: Convertir texto relativo ("hace X minutos/horas") a una fecha real
        fecha_real = datetime.now()
        if "minute" in texto_tiempo:
            minutos = int(texto_tiempo.split()[0])
            fecha_real -= timedelta(minutes=minutos)
        elif "hour" in texto_tiempo:
            horas = int(texto_tiempo.split()[0])
            fecha_real -= timedelta(hours=horas)
        elif "day" in texto_tiempo:
            dias = int(texto_tiempo.split()[0])
            fecha_real -= timedelta(days=dias)
            
        datos_noticias.append((id_noticia, titulo, fecha_real))
    except Exception as e:
        # Manejo de errores para que el pipeline no se muera si falla una fila
        print(f"Error procesando una fila: {e}")
        continue

print(f"Se procesaron {len(datos_noticias)} noticias correctamente.")

# 3. LOAD: Guardar en PostgreSQL
try:
    conn = psycopg2.connect(
        dbname="postgres", 
        user="postgres", 
        password="contraseña_generica", 
        host="localhost"
    )
    cur = conn.cursor()
    
    # Creamos la tabla adecuada para las noticias
    cur.execute("""
        CREATE TABLE IF NOT EXISTS noticias_tech (
            noticia_id VARCHAR(50) PRIMARY KEY,
            titulo TEXT,
            fecha_publicacion TIMESTAMP
        );
    """)
    
    # Insertar los datos masivamente
    for noticia in datos_noticias:
        cur.execute("""
            INSERT INTO noticias_tech (noticia_id, titulo, fecha_publicacion)
            VALUES (%s, %s, %s)
            ON CONFLICT (noticia_id) DO UPDATE SET titulo = EXCLUDED.titulo;
        """, noticia)
        
    conn.commit()
    cur.close()
    conn.close()
    print("Datos cargados exitosamente en PostgreSQL!")

except Exception as e:
    print(f"Error en la base de datos: {e}")