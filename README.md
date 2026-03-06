# 🌌 Chvstx Nexus

![Version](https://img.shields.io/badge/version-1.3.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

**Chvstx Nexus** es una interfaz unificada, moderna y profundamente personalizada para gestionar tu colección de juegos clásicos. Inspirada en la estética de *Kingdom Hearts*, ofrece una experiencia visual premium y altamente interactiva.

> [!TIP]
> **¿Buscas la última versión ejecutable?** Descárgala directamente desde la sección de [Releases](https://github.com/DavidFR-2000/ChvstxNexux/releases/latest)

---

## ✨ Novedades v1.3.0 (Mega Update)

- **🚀 Instalador Automático**: Nexus ahora puede instalarse en tu PC, creando un acceso directo en el escritorio y gestionando archivos en `AppData`.
- **🧱 Nuevo Onboarding de 6 Pasos**: Un asistente renovado que te guía desde la instalación hasta la configuración de RetroAchievements y carpetas.
- **🗑️ Función de Desinstalación**: Borra todos tus datos (configuración, caché, accesos directos) de forma segura desde los ajustes.
- **🖼️ Carátulas Reparadas**: Motor de búsqueda de portadas (Bing) actualizado para mayor fiabilidad.
- **🔌 RetroArch One-Click**: Instalación silenciosa de RetroArch y núcleos optimizada.
- **🛠️ Estabilidad Total**: Solucionados cierres inesperados al usar el modo portable y errores de interfaz.

---

## 🌟 Características de Élite

- **💙 Interfaz Nexus**: Diseño interactivo con efectos de cristal, iluminaciones dinámicas y transiciones fluidas.
- **7 Consolas Soportadas**: SNES, GBA, NDS, PS1, PS2, Mega Drive y Saturn.
- **Instalador de RetroArch Integrado**: Descarga e instala RetroArch y sus núcleos (cores) directamente desde la aplicación.
- **Asistente de RetroAchievements**: Tutorial paso a paso para configurar y activar tus logros en juegos clásicos.
- **Portadas Automáticas**: Descarga automática de carátulas con previsualizaciones de alta calidad.
- **Modo Portable vs Estándar**: Elige guardar todo en la misma carpeta o en tu perfil de usuario.

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
