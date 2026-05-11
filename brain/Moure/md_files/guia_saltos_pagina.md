# 📄 Guía de Control de Saltos de Página (Markdown & PDF)

Este documento contiene las anotaciones técnicas para gestionar cómo se divide el contenido al exportar tus apuntes a PDF.

---

## 1. Métodos Modernos (Recomendados)

### A. HTML + CSS (El más fiable)
Casi todos los editores (Obsidian, Ghostwriter, VS Code) y motores de renderizado entienden estas etiquetas.

* **Forzar salto después de un bloque:**
    ```html
    <div style="page-break-after: always;"></div>
    ```

* **Forzar que un bloque empiece en hoja nueva:**
    *(Ideal para ponerlo justo antes de una tabla o un bloque de código largo en C)*
    ```html
    <div style="page-break-before: always;"></div>
    ```

### B. Línea Horizontal (Markdown puro)
Muchos conversores están configurados para interpretar tres guiones como un salto físico de página.

* **Código:**
    ```markdown
    ---
    ```
    *(Nota: Deja una línea en blanco arriba y otra abajo para que se interprete correctamente).*

---

## 2. El Método "Legacy" (La famosa ^L)

Es el carácter que encontraste en los documentos de MoureDev. No se recomienda usarlo en documentos nuevos, pero es útil conocerlo.

* **Nombre técnico:** Form Feed (FF).
* **Representación:** `^L` o ``.
* **Uso original:** Comando para que las impresoras matriciales expulsaran el papel.

---

## 3. Consejos de Nivel Senior

1.  **Tablas Intactas:** Si ves que una tabla de tipos de datos en C se corta, pon el `<div>` de salto de página justo encima de la tabla.
2.  **Organización por Temas:** Usa un salto de página antes de cada encabezado de nivel 1 (`# Título`) para que cada tema importante tenga su propia sección limpia.
3.  **Limpieza en Arch Linux:** Si descargas archivos con el símbolo `^L` y quieres limpiarlos todos de golpe en tu terminal:
    ```bash
    sed -i 's/\x0c//g' *.md
    ```

---
*Apuntes generados para Nando - Máster en Programación.*
