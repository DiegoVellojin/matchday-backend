# 🚀 MatchDay Backend API

> **"El motor de alto rendimiento detrás de la competición deportiva."**

Proyecto de ingeniería de software backend que orquesta en tiempo real todo el ecosistema de MatchDay. Construido bajo los principios inquebrantables de **Clean Architecture**, **Inyección de Dependencias** y un manejo estricto de **Patrones de Diseño** para garantizar la escalabilidad transaccional de miles de partidos, finanzas y resultados simultáneos.

<p align="center">
   <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
   <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
   <img src="https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
   <img src="https://img.shields.io/badge/Architecture-Clean%20(4%20Layers)-success?style=for-the-badge" alt="Clean Architecture" />
</p>


## 🏛️ Arquitectura de Software: Clean Architecture Estricta

Este proyecto no es solo una API; es una implementación de referencia de **Clean Architecture** aplicada al ecosistema Python/FastAPI. La decisión de dividir el software en cuatro capas concéntricas obedece al principio de Separación de Preocupaciones (SoC).

### ¿Por qué esta separación?
1.  **Independencia del Framework:** FastAPI es solo el mecanismo de entrega web. La lógica de negocio (`Domain`) no sabe de peticiones HTTP, Headers o Routers.
2.  **Aislamiento de la Base de Datos:** SQLAlchemy se relega a la capa de Infraestructura. El dominio opera sobre objetos de memoria (Entidades), lo que teóricamente permitiría migrar de PostgreSQL a MongoDB sin tocar el núcleo de la aplicación.
3.  **Seguridad por Diseño:** El acceso a los datos y las transacciones críticas (pagos, resultados) están protegidas por interfaces (Contratos), forzando una estricta validación de roles de Capitán.

### Desglose de Capas

#### 1. Domain (Dominio) - *La Verdad Absoluta*
Es el núcleo inmutable del software. 
*   **`entities/`**: Modelos puros que representan los conceptos de negocio (Usuario, Partido, Pago).
*   **`interfaces.py`**: Aplicamos el **Principio de Inversión de Dependencias (DIP)**. Aquí se definen los contratos que los repositorios deben cumplir usando nomenclatura en inglés (ej. `IUserRepository`).
*   **`specifications/`**: Patrón Specification para definir reglas de búsqueda de forma abstracta (ej. `MatchByStatus`).

#### 2. Application (Aplicación) - *El Director de Orquesta*
Contiene la lógica transaccional y orquesta el flujo de información.
*   **`usecases/`**: Encapsulan intenciones únicas (S.R.P). Ejemplo: `AcceptMatchUseCase`. Verifican permisos (ej. "¿Es el Capitán A el que intenta aceptar?") antes de interactuar con el dominio.

#### 3. Infrastructure (Infraestructura) - *El Mundo Real*
Trata con los detalles técnicos externos y la persistencia de datos.
*   **`orm_models.py`**: Modelos de SQLAlchemy (Tablas).
*   **`repositories_impl.py`**: Los "traductores" (ej. `UserRepositoryImpl`). Ejecutan queries complejas, resuelven relaciones y devuelven Entidades puras a la capa de Aplicación.

#### 4. Presentation (Presentación) - *La Interfaz REST*
La puerta de entrada a la API.
*   **`routers.py`**: Exponen los Endpoints de FastAPI. No contienen lógica de negocio, solo validan los inputs HTTP a través de esquemas Pydantic y delegan el trabajo a los Casos de Uso vía inyección de dependencias (`Depends`).

---

## 🛠️ Stack Tecnológico

Selección de herramientas para máxima velocidad y seguridad transaccional:

### Motor & Conectividad
* **`FastAPI`**: Framework hiperrápido que aprovecha `async/await` de Python nativo, ideal para gestionar múltiples conexiones entrantes.
* **`Pydantic`**: Tipado fuerte y validación de datos estructural.

### Capa de Datos
*   **`SQLAlchemy 2.0`**: Patrón Data Mapper avanzado para aislar por completo la lógica de negocio del esquema SQL subyacente.
*   **`PostgreSQL`**: Garantía ACID para el procesamiento de pagos y resultados deportivos.

### Seguridad & Notificaciones
*   **JWT (JSON Web Tokens)**: Identificación stateless. Integrado con `Firebase Admin SDK`.
*   **Notificaciones Push**: Pub/Sub para informar a capitanes en tiempo real sobre nuevos retos o comprobantes verificados a través de FCM (Firebase Cloud Messaging).
*   **Bcrypt**: Hasheo unidireccional y robusto de credenciales locales.

---

## 🧩 Patrones de Diseño Aplicados

### Patrón State (Máquina de Estados)
Las transiciones de un partido están estrictamente bloqueadas y solo permiten avances lógicos: `publicada` -> `negociando` -> `pendiente_pago` -> `confirmada` -> `completada` o `cancelada`. El dominio prohíbe explícitamente saltarse pasos críticos.

### Domain Events (Observer / Pub-Sub)
Un cambio en un repositorio a menudo requiere efectos secundarios (ej. enviar notificación de reto aceptado). En lugar de ensuciar el UseCase, disparamos un evento (`MatchAcceptedEvent`) que un Handler independiente captura y procesa en segundo plano, manteniendo el principio S.O.L.I.D. (OCP).

### Patrón Specification
Evitamos sobrecargar los métodos de los repositorios (ej. `get_all_by_sport_and_status_and_region`). En su lugar, el Repositorio recibe Especificaciones combinables: `repo.find(MatchBySport(sport_id) & MatchByStatus('publicada'))`.

---

## 📂 Estructura del Proyecto

El backend está segmentado lógicamente por micro-módulos dentro de la carpeta `app/modules/`:

```text
app/modules/
├── auth/            # 🔐 Identidad y Tokens JWT
├── catalogs/        # 🏟️ Deporte, Regiones y Canchas
├── matches/         # ⚽ Núcleo: Máquina de estados de los Partidos
├── notifications/   # 🔔 Motor de Push Notifications (FCM)
├── payments/        # 💸 Verificación y Cuotas dinámicas por deporte
├── rankings/        # 📈 Motor de estadísticas y Leaderboard
├── teams/           # 🛡️ Capitanías y Transferencias
└── users/           # 👤 Perfiles
```

La arquitectura Clean se respeta meticulosamente **dentro de cada módulo**:
```text
app/modules/matches/
├── domain/                  # entities.py, interfaces.py, specifications.py
├── application/             # usecases.py, event_handlers.py
├── infrastructure/          # orm_models.py, repositories_impl.py
└── presentation/            # routers.py, schemas.py
```

---

## 🚀 Guía de Inicio y Despliegue Local

### Prerrequisitos
*   **Python** 3.10 o superior.
*   Instancia local o en la nube de **PostgreSQL**.
*   Archivo `.env` configurado con credenciales de DB y Firebase.

### Instalación Rápida

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/MatchDay-UCAB/matchday_backend.git
    cd matchday_backend
    ```

2.  **Entorno Virtual (Vital para IntelliSense):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # En Windows: .venv\Scripts\activate
    ```

3.  **Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar Servidor (Uvicorn):**
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```

### Documentación Interactiva
FastAPI genera la documentación OpenAPI automáticamente. Navega a:
*   **Swagger UI:** `http://localhost:8000/docs`

<br>
<hr>
<p align="center">
  <sub>Desarrollado como Pasante de <b>TecnoRed @ UCAB</b> - 2026</sub><br>
  <small>Ingeniería de Software Backend de Alto Rendimiento</small>
</p>
