# Prueba Técnica - Certiffy

## Instalación y Configuración

### 1. Clonar el repositorio e instalar dependencias

```bash
# Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Ejecutar Migraciones

```bash
python manage.py migrate
```

### 3. Poblar la base de datos

```bash
python manage.py seed
```

---

##  Ejecución del Proyecto

### Correr el servidor

```bash
python manage.py runserver
```

### Correr las pruebas

```bash
python manage.py test business
```

---

## Decisiones Técnicas Relevantes

* **Cálculo de Totales Dinámicos:** Se decidió calcular el total de una venta como `subtotal + tax` mediante agregaciones del ORM en lugar de almacenarlo estáticamente.
* **Atomicidad en el Cierre:** El proceso de cierre de remisiones utiliza `transaction.atomic`. Esto asegura que si una validación falla, no se persista ningún cambio parcial.
* **Optimización de Consultas (N+1):** Se implementó el uso de `select_related` y `prefetch_related` en los ViewSets. Para mejorar el rendimiento al realizar las consultas
* **Integridad de Datos con Validadores:** Se aplicaron validaciones coherentes en los modelos para asegurar folios únicos y montos no negativos (ventas ≥ 0 y créditos > 0).
