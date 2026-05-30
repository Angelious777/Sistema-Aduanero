import urllib.request, json

urls=[
 'http://127.0.0.1:5000/api/tabla/paquete_operativo/scz',
 'http://127.0.0.1:5000/api/tabla/paquete_financiero/scz',
 'http://127.0.0.1:5000/api/tabla/movimiento/scz'
]

for u in urls:
    try:
        with urllib.request.urlopen(u, timeout=10) as r:
            j = json.load(r)
            print('URL:', u)
            print(json.dumps(j, ensure_ascii=False, indent=2))
    except Exception as e:
        print('URL:', u)
        print('ERROR:', e)
