# Agenda inteligente

Aplicación de gestión de agenda para consola, implementada con Python, Peewee y MySQL.
El código está separado en modelos, validaciones, servicios y menú de consola.

## Requisitos

- Python 3.10 o superior.
- MySQL local con la base de datos `agenda`.
- Un usuario de MySQL con permisos de lectura, escritura y creación de tablas.

Instala las dependencias desde esta carpeta:

```powershell
python -m pip install -r requirements.txt
```

## Configuración

Copia `database.example.conf` como `database.conf` y configura la clave local de MySQL.
El archivo real `database.conf` está ignorado por Git para no versionar credenciales.
La aplicación no guarda ni imprime las contraseñas de usuarios; almacena hashes PBKDF2.

La base de datos `agenda` debe existir antes de iniciar la aplicación. Al conectar,
se crean las tablas del modelo que aún no existan. No se eliminan ni migran tablas
existentes; verifica la compatibilidad de un esquema preexistente antes de usarlo.

## Ejecución

```powershell
python app.py
```

El menú permite gestionar usuarios y agendas, actividades (tareas, eventos y
compromisos), categorías, contactos, recurrencias y recordatorios. Las relaciones
dependientes se mantienen o eliminan según las reglas de claves foráneas del modelo.
Los datos ingresados en las fechas usan `AAAA-MM-DD`; las horas, `HH:MM`.

## Pruebas

```powershell
python -m unittest discover -s tests -v
```
