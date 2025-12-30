# 🚀 Lite Thinking - Sistema de Gestión de Inventario

Sistema completo de gestión de inventario con **Clean Architecture**, **Domain-Driven Design** y **UN SOLO Poetry** gestionando todo el proyecto.

## 📦 Estructura del Proyecto - UN SOLO POETRY

```
lite-thinking/
├── pyproject.toml           # ← UN SOLO Poetry para TODO
├── poetry.lock
├── manage.py                # Django management
├── README.md
│
├── dominio/                 # Capa de Dominio (Python puro)
│   ├── __init__.py
│   ├── entidades/           # Modelos de negocio
│   │   ├── __init__.py
│   │   ├── empresa.py
│   │   ├── producto.py
│   │   ├── inventario.py
│   │   └── usuario.py
│   ├── excepciones/         # Excepciones de negocio
│   │   ├── __init__.py
│   │   └── dominio_excepciones.py
│   ├── casos_uso/           # Lógica de aplicación (opcional)
│   │   └── __init__.py
│   └── tests/               # Tests de dominio puro
│       ├── __init__.py
│       ├── test_empresa.py
│       └── test_producto.py
│
├── backend/                 # Aplicación Django
│   ├── __init__.py
│   ├── config/              # Configuración Django
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/                # Django Apps
│   │   ├── __init__.py
│   │   ├── empresas/
│   │   │   ├── __init__.py
│   │   │   ├── models.py        # ORM - mapea dominio.entidades.Empresa
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── tests.py
│   │   ├── productos/
│   │   ├── inventario/
│   │   └── autenticacion/
│   └── infrastructure/      # Repositorios y Adapters
│       ├── __init__.py
│       ├── repositories/
│       │   ├── __init__.py
│       │   ├── empresa_repository.py
│       │   └── producto_repository.py
│       └── adapters/
│           ├── __init__.py
│           ├── email_adapter.py
│           └── pdf_adapter.py
│
├── tests/                   # Tests de integración
│   └── __init__.py
│
└── frontend/                # React App (npm separado)
    ├── package.json
    ├── src/
    └── public/
```

## 🎯 Ventajas de UN SOLO Poetry

### ✅ Gestión Unificada
```bash
# UN SOLO comando instala TODO
poetry install

# UN SOLO entorno virtual para dominio + Django
poetry shell
```

### ✅ Dependencias Compartidas
```toml
[tool.poetry.dependencies]
python = "^3.9"
pydantic = "^2.5.0"    # Para dominio (validaciones)
django = "^5.0.0"       # Para backend
# TODO en un solo lugar
```

### ✅ Testing Unificado
```bash
# Tests de dominio puro + Django en un solo comando
poetry run pytest

# Coverage de TODO el proyecto
poetry run pytest --cov=dominio --cov=backend
```

### ✅ Imports Simplificados
```python
# En cualquier parte del proyecto
from dominio.entidades import Empresa
from dominio.excepciones import EntidadNoEncontrada
from backend.apps.empresas.models import Empresa as EmpresaModel
```

## 🚀 Instalación y Uso

### 1. Instalar Dependencias

```bash
# Instalar Poetry (si no lo tienes)
curl -sSL https://install.python-poetry.org | python3 -

# Instalar TODO el proyecto
cd lite-thinking
poetry install

# Para desarrollo (incluye herramientas de testing)
poetry install --with dev

# Para producción
poetry install --with prod --no-dev
```

### 2. Configurar Base de Datos

```bash
# Crear base de datos PostgreSQL
createdb lite_thinking_db

# Configurar .env
cp .env.example .env
# Editar credenciales en .env
```

### 3. Ejecutar Migraciones

```bash
poetry run python manage.py migrate
```

### 4. Crear Superusuario

```bash
poetry run python manage.py createsuperuser
```

### 5. Ejecutar Servidor

```bash
poetry run python manage.py runserver
# O usar el script personalizado
poetry run server
```

## 🧪 Testing

### Tests de Dominio Puro (sin Django)

```bash
# Solo tests de dominio
poetry run pytest dominio/tests -v

# Con coverage
poetry run pytest dominio/tests --cov=dominio
```

### Tests de Django

```bash
# Solo tests de Django
poetry run pytest backend/apps -v
```

### Tests Completos

```bash
# TODO el proyecto
poetry run pytest

# Con coverage completo
poetry run pytest --cov=dominio --cov=backend --cov-report=html
open htmlcov/index.html
```

### Tests por Tipo

```bash
# Solo unitarios
poetry run pytest -m unit

# Solo integración
poetry run pytest -m integration

# Excluir lentos
poetry run pytest -m "not slow"
```

## 🛠️ Comandos de Desarrollo

### Calidad de Código

```bash
# Formatear código
poetry run black .

# Ordenar imports
poetry run isort .

# Linting
poetry run flake8

# Type checking
poetry run mypy dominio backend

# Todo junto
poetry run black . && poetry run isort . && poetry run flake8
```

### Django

```bash
# Shell de Django
poetry run python manage.py shell

# Crear app
poetry run python manage.py startapp nombre_app backend/apps/

# Hacer migraciones
poetry run python manage.py makemigrations

# Ver SQL de migraciones
poetry run python manage.py sqlmigrate app_name migration_name
```

## 📂 Cómo Funciona

### Importar desde Dominio

```python
# En cualquier archivo de backend/apps/
from dominio.entidades import Empresa, Producto
from dominio.excepciones import EntidadNoEncontrada

# Crear entidad de dominio
empresa = Empresa(
    nit="900123456-7",
    nombre="Mi Empresa",
    direccion="Calle 123",
    telefono="3001234567",
    email="contacto@empresa.com"
)

# La entidad se valida automáticamente
# Si hay error, lanza ValueError
```

### Mapear Dominio ↔ Django ORM

```python
# backend/apps/empresas/models.py
from django.db import models
from dominio.entidades import Empresa as EmpresaDominio

class Empresa(models.Model):
    nit = models.CharField(max_length=15, unique=True)
    nombre = models.CharField(max_length=200)
    # ...
    
    def to_domain(self) -> EmpresaDominio:
        """Convierte modelo Django a entidad de dominio"""
        return EmpresaDominio(
            id=self.id,
            nit=self.nit,
            nombre=self.nombre,
            direccion=self.direccion,
            telefono=self.telefono,
            email=self.email,
            activa=self.activa,
            fecha_creacion=self.created_at,
            fecha_actualizacion=self.updated_at
        )
    
    @classmethod
    def from_domain(cls, entidad: EmpresaDominio):
        """Crea modelo Django desde entidad de dominio"""
        return cls(
            nit=entidad.nit,
            nombre=entidad.nombre,
            direccion=entidad.direccion,
            telefono=entidad.telefono,
            email=entidad.email,
            activa=entidad.activa
        )
```

## 🔑 Ventajas de Esta Arquitectura

### 1. Dominio Separado pero Accesible
- ✅ Lógica de negocio en `dominio/` (Python puro)
- ✅ Django en `backend/` usa el dominio
- ✅ TODO gestionado por un solo Poetry

### 2. Testing Superior
```bash
# Tests de dominio: < 1 segundo (sin Django)
poetry run pytest dominio/

# Tests de Django: normal (con DB)
poetry run pytest backend/
```

### 3. Clean Architecture Real
```
Frontend → Backend API → Use Cases → Dominio
                ↓
        Infrastructure → Dominio
```

### 4. Facilidad de Desarrollo
```bash
# UN comando para todo
poetry install

# UN entorno para todo
poetry shell

# UN test runner para todo
poetry run pytest
```

## 📊 packages en pyproject.toml

```toml
[tool.poetry]
packages = [
    { include = "dominio" },
    { include = "backend" }
]
```

Esto le dice a Poetry que **ambos** directorios son parte del paquete instalable.

## 🎓 Para la Entrevista

### Puntos Clave a Mencionar:

1. **"Usé Poetry para gestionar TODO el proyecto"**
   - No requirements.txt
   - Dependencias versionadas con poetry.lock
   - Grupos de dependencias (dev, prod)

2. **"El dominio está separado lógicamente pero no físicamente"**
   - `dominio/` contiene lógica pura
   - `backend/` usa `dominio/`
   - Un solo Poetry los gestiona

3. **"Testing en capas"**
   - Tests de dominio sin framework
   - Tests de Django con ORM
   - Coverage unificado

4. **"Imports limpios"**
   ```python
   from dominio.entidades import Empresa  # Claro y directo
   ```

5. **"Scripts personalizados en Poetry"**
   ```bash
   poetry run server  # Alias para runserver
   ```

## 📞 Comandos Más Usados

```bash
# Instalación inicial
poetry install

# Activar entorno
poetry shell

# Tests
poetry run pytest

# Servidor
poetry run python manage.py runserver

# Calidad de código
poetry run black . && poetry run isort .

# Nueva dependencia
poetry add nombre-paquete

# Dependencia de desarrollo
poetry add --group dev nombre-paquete
```

## 📄 Licencia

MIT

## 👤 Autor

Jefferson Perez - jefer5261@gmail.com
