# 🤖 Estructura de un Prompt Perfecto

Esta es la jerarquía que debes seguir para que modelos como Claude o ChatGPT entiendan exactamente lo que necesitas.

---

## 🏗️ Los 5 Pilares Fundamentales

1. **Contexto de la Tarea (Rol)**
   - Define quién es la IA: "Eres un administrador de sistemas experto en Arch Linux".
   - Cuál es el objetivo: "Ayúdame a depurar un error de montaje en WSL".

2. **Contexto del Tono (Estilo)**
   - Define cómo habla: "Usa un tono técnico pero claro, evita explicaciones innecesarias, ve directo al grano".

3. **Datos de Contexto (Material)**
   - Pégale logs, fragmentos de código o errores:
     `Error: EISDIR: illegal operation on a directory...`

4. **Descripción y Reglas (Instrucciones)**
   - El paso a paso: "Analiza el error, dime por qué ocurre y dame el comando para solucionarlo".
   - Restricciones: "No me sugieras mover la carpeta a Windows, quiero mantenerla en el sistema de archivos de Linux".

5. **Ejemplos (Few-Shot)**
   - Si buscas un formato específico, dáselo: "Devuélveme la solución en este formato: **Problema:** [explicación], **Solución:** [comando]".

---

## 🛠️ Truco de Pro: Etiquetas XML

Claude entiende mejor la separación de información si usas etiquetas. Puedes escribir tu prompt así:

<contexto>
  Soy un estudiante de CS50 usando Arch Linux e i3wm.
</contexto>

<tarea>
  Explícame cómo funciona el bucle `for` en C usando una analogía con mi trabajo de camarero.
</tarea>

<reglas>
  - La explicación debe ser breve.
  - Usa código real de C como ejemplo.
</reglas>
