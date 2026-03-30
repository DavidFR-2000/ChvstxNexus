# 🌌 Chvstx Nexus

![Version](https://img.shields.io/badge/version-3.0.0-gold)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

**Chvstx Nexus** es una interfaz unificada, moderna y profundamente personalizada para gestionar tu colección de juegos clásicos. Con su nueva **Experiencia Nexus 2.0**, ofrece una navegación de élite inspirada en las consolas clásicas más premium.

> [!TIP]
> **¿Buscas la última versión ejecutable?** Descárgala directamente desde la sección de [Releases](https://github.com/DavidFR-2000/ChvstxNexux/releases/latest)

---

## 🚀 Novedades v3.0.0 (The Nexus PySide6 Engine)

- **⚡ Motor PySide6**: Reescritura completa del código nativo en C++/Qt para ofrecer un rendimiento masivo, fluidez a 60FPS y tiempos de carga instantáneos frente a CustomTkinter.
- **🎮 Interfaz Ultra-Fluida**: Rediseño total de la navegación. Ahora con layouts dinámicos y la nueva vista en cuadrícula de gran resolución.
- **☁️ Hub de Descargas Inteligente**: Integración directa con repositorios como Retrostic, Myrient y Homebrew para descargar juegos y ROMs limpiamente.
- **📦 Auto-Extracción de ROMs**: El nuevo sistema descomprime automáticamente `.zip`, `.7z` y `.rar` detectando qué consolas (como PS2 o GameCube) necesitan la ISO directamente.
- **📂 Escaneo de Subcarpetas**: Lee juegos en cualquier nivel de profundidad de carpetas.
- **📚 Enciclopedia y Ajustes Dinámicos**: Integración con Wikipedia, API REST, Ajustes in-app con detector de Cores faltantes en RetroArch, y mucho más.

---

## 🌟 Características de Élite

- **💙 Diseño Premium**: Estética moderna con efectos de cristal (glassmorphism), iluminaciones dinámicas y tipografía optimizada.
- **+18 Sistemas Soportados**: Desde NES y Game Boy hasta PS2, Dreamcast y GameCube.
- **Instalador de RetroArch Pro**: Gestión completa de la instalación y actualización de RetroArch y sus núcleos.
- **Sincronización de Logros**: Soporte total para RetroAchievements con tutorial paso a paso.
- **Portadas Inteligentes**: Motor dual de búsqueda de carátulas para que tu colección siempre luzca impecable.
- **Modo Flexible**: Elige entre instalación estándar en el sistema o modo portable para llevar tu Nexus en un USB.

---

## 🚀 Cómo empezar rápidamente

### Opción A: Usar el ejecutable (Recomendado)
1. Descarga el archivo `ChvstxNexus_vX.X.X.exe` desde [Releases](https://github.com/DavidFR-2000/ChvstxNexux/releases/latest).
2. Ejecútalo y sigue el **Asistente de Bienvenida de Chvstx**.
3. Selecciona tu carpeta de ROMs y ¡que comience la aventura!

### Opción B: Ejecutar desde el código fuente
1. Clona el repositorio: `git clone https://github.com/DavidFR-2000/ChvstxNexux.git`
2. Instala las dependencias: `pip install -r requirements.txt`
3. Lanza el Nexus: `python main.py`

---

## 🛠️ Para Desarrolladores

### Empaquetado de la aplicación
Para generar tu propio `.exe` con la nueva marca:
```bash
python build_dist.py
```
Este script actualizará la versión y generará el ejecutable `ChvstxNexus_vX.X.X.exe` en `dist/`.

---

## 🤝 Créditos
Desarrollado con ❤️ por **Chvstx**.
Inspirado por el amor a lo retro y potenciado por el motor gráfico de **PySide6 / Qt**.
