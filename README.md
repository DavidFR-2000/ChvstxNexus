# 🌌 Chvstx Nexus

![Version](https://img.shields.io/badge/version-2.0.0-gold)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

**Chvstx Nexus** es una interfaz unificada, moderna y profundamente personalizada para gestionar tu colección de juegos clásicos. Con su nueva **Experiencia Nexus 2.0**, ofrece una navegación de élite inspirada en las consolas clásicas más premium.

> [!TIP]
> **¿Buscas la última versión ejecutable?** Descárgala directamente desde la sección de [Releases](https://github.com/DavidFR-2000/ChvstxNexux/releases/latest)

---

## 🚀 Novedades v2.0.0 (The Nexus Evolution)

- **🎮 Interfaz Estilo PSP (XMB)**: Rediseño total de la navegación. Ahora con barra superior horizontal para consolas y lista vertical dinámica para juegos, con transiciones ultra fluidas.
- **☁️ Hub de Descargas Myrient (R-Roms)**: Integración directa con el Megathread de R-Roms. Busca y descarga juegos de NES, GBA, PS1, GameCube y más de 15 consolas directamente desde la app.
- **📚 Enciclopedia Wikipedia**: Nuevo sistema de descripciones de alta precisión. Nexus ahora consulta Wikipedia (Español e Inglés) para ofrecerte información real y detallada de cada juego en tu colección.
- **⚙️ Ajustes Integrados**: Se acabó la ventana secundaria. Ahora la configuración vive dentro de la interfaz principal para una experiencia más coherente y fluida.
- **📦 Descarga de Cores Automática**: Si te falta un núcleo de RetroArch para tu juego, Nexus lo reconoce y te permite descargarlo al momento sin salir del programa.

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
Inspirado por el arte de Kingdom Hearts y el poder de **CustomTkinter**.
