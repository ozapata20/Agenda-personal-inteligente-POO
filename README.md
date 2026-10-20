# Agenda personal inteligente

Aplicación de consola para administrar usuarios y sus agendas, actividades
(tareas, eventos y compromisos), categorías, contactos, recurrencias y
recordatorios. Está desarrollada en Python, usa Peewee para el acceso a datos y
MySQL para guardar la información.

Esta guía describe cómo obtener una copia con GitHub Desktop, instalar los
requisitos en Windows, preparar MySQL y ejecutar el programa desde cero.

## Requisitos

- Windows 10 u 11.
- GitHub Desktop.
- Python 3.10 o superior. Durante la instalación de Python, habilita la opción
  **Add Python to PATH**.
- MySQL Server 8.x instalado y en ejecución. MySQL Workbench es opcional, pero
  facilita la configuración de la base de datos.

## 1. Clonar el proyecto con GitHub Desktop

1. Abre GitHub Desktop e inicia sesión en GitHub.
2. Selecciona **File > Clone repository...**.
3. Abre la pestaña **URL** e introduce:

   ```text
   https://github.com/ozapata20/Agenda-personal-inteligente-POO.git
   ```

4. En **Local path**, selecciona la carpeta donde guardarás el proyecto y pulsa
   **Clone**.
5. Selecciona **Repository > Open in Visual Studio Code** (o abre la carpeta
   clonada en tu editor).

Los siguientes comandos deben ejecutarse en una terminal de PowerShell abierta
en la carpeta del proyecto, donde están `app.py` y `requirements.txt`.

## 2. Instalar e iniciar MySQL Server

Si MySQL Server aún no está instalado:

1. Descarga e instala MySQL Server desde el instalador oficial de MySQL para
   Windows.
2. En el asistente, configura MySQL como servicio de Windows y conserva el
   puerto predeterminado `3306`, salvo que ya esté ocupado.
3. Define una contraseña para la cuenta administrativa `root` y guárdala en un
   lugar seguro. No uses esa cuenta para la conexión habitual de la aplicación.
4. Inicia el servicio MySQL si el instalador no lo dejó iniciado. Puedes
   comprobarlo en **Servicios** de Windows o en MySQL Workbench.
5. (Opcional) Instala MySQL Workbench para ejecutar las sentencias SQL de la
   siguiente sección desde una interfaz gráfica.

## 3. Crear la base de datos y el usuario de la aplicación

La aplicación necesita una base de datos llamada `agenda` y un usuario MySQL
propio. Este usuario tendrá permisos sobre esa base, no permisos administrativos
globales.

Conéctate al servidor con `root` (por ejemplo, desde MySQL Workbench) y ejecuta
estas sentencias. Sustituye `EligeUnaClaveSegura_123!` por una contraseña propia
y segura; usarás la misma en `database.conf` en el siguiente paso.

```sql
CREATE DATABASE agenda
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'agenda_app'@'localhost'
  IDENTIFIED BY 'EligeUnaClaveSegura_123!';

GRANT ALL PRIVILEGES ON agenda.* TO 'agenda_app'@'localhost';
```

Si creaste la base o el usuario anteriormente, no vuelvas a ejecutar a ciegas
las sentencias `CREATE`: verifica que existan y actualiza la contraseña o los
permisos según corresponda. No hace falta ejecutar `FLUSH PRIVILEGES`.

## 4. Configurar la conexión de la aplicación

Desde la carpeta raíz del proyecto, crea el archivo local de configuración a
partir de la plantilla:

```powershell
Copy-Item database.example.conf database.conf
```

Si `database.conf` ya existe, no ejecutes el comando para sobrescribirlo; edita
ese archivo. Ábrelo con el editor y deja la sección `[mysql]` con valores
equivalentes a estos:

```ini
[mysql]
host = localhost
port = 3306
database = agenda
user = agenda_app
password = EligeUnaClaveSegura_123!
charset = utf8mb4
connect_timeout = 5
```

La contraseña debe coincidir con la que estableciste para el usuario MySQL.
`database.conf` contiene credenciales y está excluido del control de versiones;
no lo subas ni compartas. Si cambias el puerto de MySQL, actualiza `port` aquí
también. La aplicación busca este archivo en la carpeta del proyecto donde está
`config.py`.

## 5. Crear el entorno de Python e instalar dependencias

En PowerShell, desde la carpeta del proyecto, comprueba que el lanzador `py`
encuentre Python 3.10 o superior:

```powershell
py -3 --version
```

Crea un entorno virtual e instala las dependencias del proyecto:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Los comandos usan directamente el Python del entorno virtual, por lo que no es
necesario activarlo. Si `py -3` no encuentra una versión compatible, instala
Python 3.10 o superior y vuelve a abrir PowerShell.

## 6. Ejecutar el programa

Desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe app.py
```

Al iniciar, la aplicación se conecta a MySQL y crea automáticamente las tablas
que falten. No elimina datos ni migra tablas preexistentes. Para una instalación
nueva solo es necesario haber creado la base `agenda` en el paso 3; no ejecutes
`AGENDAINTELIGENTE.sql` para inicializarla. Ese archivo contiene un esquema SQL
separado y puede no corresponder al esquema que administra actualmente la
aplicación.

Cuando aparezca el menú, selecciona **Usuarios y agendas** para registrar el
primer usuario. Al crearlo, también se crea su agenda. Luego podrás gestionar
actividades y los demás datos desde las opciones del menú. Las fechas se
ingresan como `AAAA-MM-DD` y las horas como `HH:MM`.

## 7. Ejecutar las pruebas

Las pruebas usan una base SQLite temporal en memoria; no necesitan MySQL y no
modifican la base de datos de la aplicación.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Solución de problemas

- **No existe `database.conf`:** ejecuta `Copy-Item database.example.conf
  database.conf` desde la raíz y completa la contraseña.
- **Access denied / acceso denegado:** verifica `user`, `password` y `host` en
  `database.conf`, y que el usuario tenga permisos sobre `agenda.*`.
- **Unknown database / base de datos desconocida:** crea la base `agenda` con
  las sentencias del paso 3.
- **Can't connect / conexión rechazada:** confirma que MySQL Server esté
  iniciado y que el puerto de `database.conf` coincida con el configurado en
  MySQL.
- **No se encuentra `py` o Python:** instala Python 3.10 o superior, habilita
  **Add Python to PATH** y abre una terminal nueva.
- **Falta un módulo de Python:** activa la carpeta del proyecto y repite
  `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.

## Notas sobre datos existentes

La aplicación crea tablas faltantes, pero no realiza migraciones del esquema.
Si conectas una base de datos que ya contiene tablas, haz una copia de seguridad
y verifica que su estructura sea compatible antes de usarla.
