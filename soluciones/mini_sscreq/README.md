# mini_sscreq (referencia al final de M7)

Para comparar con tu trabajo en `practica/mini_sscreq`. Con el `venv` del repositorio activo:

```powershell
cd soluciones\mini_sscreq
python manage.py migrate
python manage.py loaddata datos_ficticios
python manage.py createsuperuser
python manage.py runserver 8001
python manage.py test
```

Abre http://127.0.0.1:8001 (puerto 8001 para no chocar con la plataforma de estudio).
