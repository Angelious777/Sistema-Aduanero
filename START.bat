#!/bin/bash
# Script de inicio rápido para el Sistema Aduanero Distribuido

echo "==========================================="
echo "Sistema Aduanero Distribuido - Inicio"
echo "==========================================="

# Navegar al directorio
cd "c:\Users\ROGER\Escritorio\Sistema Aduanero"

# Activar entorno virtual
echo "Activando entorno virtual..."
call venv\Scripts\activate.bat

# Instalar dependencias
echo "Verificando dependencias..."
pip install flask flask-cors psycopg2-binary pyodbc -q

# Ejecutar la aplicación
echo ""
echo "==========================================="
echo "Iniciando aplicación..."
echo "==========================================="
echo ""
echo "🌍 Sistema disponible en: http://localhost:5000"
echo ""
echo "Presiona CTRL+C para detener"
echo ""

python app.py
