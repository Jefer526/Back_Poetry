"""
Servicio de Chatbot (IA) con Google GenAI (nueva librería)
"""
from django.conf import settings


class ServicioChatbot:
    """
    Servicio para chatbot inteligente
    Usa Google GenAI (nueva API)
    """
    
    def __init__(self):
        # Verificar si hay Gemini API key configurada
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        self.usar_api = False
        
        if api_key and api_key != 'tu-api-key-aqui':
            try:
                from google import genai
                from google.genai import types
                
                # Configurar cliente
                self.client = genai.Client(api_key=api_key)
                self.usar_api = True
            except ImportError:
                print("⚠️ google-genai no está instalado")
                self.usar_api = False
            except Exception as e:
                print(f"⚠️ Error configurando Gemini: {e}")
                self.usar_api = False
    
    def generar_respuesta(self, mensaje_usuario, historial=None, contexto_sistema=None):
        """
        Genera respuesta del chatbot
        
        Args:
            mensaje_usuario: Mensaje del usuario
            historial: Lista de mensajes anteriores [{"role": "user|assistant", "content": "..."}]
            contexto_sistema: Contexto del sistema (información de inventario, productos, etc.)
        
        Returns:
            str: Respuesta generada
        """
        if self.usar_api:
            return self._generar_con_gemini(mensaje_usuario, historial, contexto_sistema)
        else:
            return self._generar_respuesta_basica(mensaje_usuario, contexto_sistema)
    
    def _generar_con_gemini(self, mensaje_usuario, historial, contexto_sistema):
        """Genera respuesta usando Gemini (nueva API)"""
        try:
            # Construir prompt completo
            prompt_completo = ""
            
            # System prompt
            system_prompt = """Eres un asistente inteligente para un sistema de gestión de inventario llamado Lite Thinking.

Puedes ayudar con:
- Consultas sobre productos e inventario
- Información sobre empresas registradas
- Estadísticas y reportes
- Recomendaciones sobre gestión de stock
- Orientación sobre el uso del sistema

Responde de manera clara, concisa y profesional. Si no tienes la información exacta, sugiere cómo el usuario puede obtenerla en el sistema."""
            
            prompt_completo += system_prompt + "\n\n"
            
            # Agregar contexto del sistema si existe
            if contexto_sistema:
                prompt_completo += f"Contexto actual del sistema:\n{contexto_sistema}\n\n"
            
            # Agregar historial si existe
            if historial:
                prompt_completo += "Historial de conversación:\n"
                for msg in historial:
                    rol = "Usuario" if msg["role"] == "user" else "Asistente"
                    prompt_completo += f"{rol}: {msg['content']}\n"
                prompt_completo += "\n"
            
            # Agregar mensaje actual
            prompt_completo += f"Usuario: {mensaje_usuario}\nAsistente:"
            
            # Generar respuesta con Gemini
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt_completo
            )
            
            return response.text
            
        except Exception as e:
            print(f"❌ Error en Gemini: {e}")
            return f"Disculpa, tuve un problema al procesar tu mensaje. Usando modo demo."
    
    def _generar_respuesta_basica(self, mensaje_usuario, contexto_sistema):
        """Genera respuesta básica sin API (modo demo)"""
        mensaje_lower = mensaje_usuario.lower()
        
        # Respuestas predefinidas inteligentes
        if any(palabra in mensaje_lower for palabra in ['hola', 'hi', 'buenos', 'buenas', 'hey']):
            return """¡Hola! 👋 Soy el asistente de Lite Thinking.

Puedo ayudarte con:
• 📦 Productos y inventario
• 🏢 Empresas registradas
• 📊 Reportes y estadísticas
• 💡 Recomendaciones

¿En qué puedo ayudarte hoy?"""
        
        elif any(palabra in mensaje_lower for palabra in ['producto', 'productos']):
            return """📦 **Información sobre Productos**

Puedo ayudarte con:
- Ver todos los productos registrados
- Buscar un producto específico por código o nombre
- Consultar el stock actual de un producto
- Ver productos con bajo inventario
- Información de precios (USD, COP, EUR)

¿Qué necesitas saber específicamente?"""
        
        elif any(palabra in mensaje_lower for palabra in ['inventario', 'stock']):
            return """📊 **Gestión de Inventario**

Información disponible:
- Stock actual de todos los productos
- Productos con stock bajo (alertas)
- Historial de movimientos (entradas/salidas)
- Ubicaciones en bodega
- Reportes PDF descargables

¿Quieres ver el estado general o un producto específico?"""
        
        elif any(palabra in mensaje_lower for palabra in ['empresa', 'empresas']):
            return """🏢 **Empresas Registradas**

Puedo mostrarte:
- Listado completo de empresas
- Información detallada (NIT, dirección, contacto)
- Productos asociados a cada empresa
- Estadísticas por empresa

¿Buscas una empresa en particular o quieres ver todas?"""
        
        elif any(palabra in mensaje_lower for palabra in ['reporte', 'pdf', 'descargar']):
            return """📄 **Reportes Disponibles**

El sistema puede generar:
- PDF de inventario completo
- PDF de movimientos específicos
- Envío de reportes por email
- Alertas de stock bajo

Los reportes se generan desde el panel de administración. ¿Necesitas ayuda para generarlos?"""
        
        elif any(palabra in mensaje_lower for palabra in ['movimiento', 'entrada', 'salida']):
            return """📝 **Movimientos de Inventario**

Tipos de movimientos:
- **Entrada:** Aumenta el stock (compras, devoluciones)
- **Salida:** Reduce el stock (ventas, pérdidas)

Cada movimiento queda registrado con:
- Fecha y hora
- Usuario responsable
- Cantidad y motivo
- Historial inmutable para auditoría

¿Necesitas registrar un movimiento?"""
        
        elif any(palabra in mensaje_lower for palabra in ['precio', 'costo', 'valor']):
            return """💰 **Precios de Productos**

El sistema maneja 3 monedas:
- USD (Dólares)
- COP (Pesos Colombianos)
- EUR (Euros)

Los precios se calculan automáticamente según la tasa de cambio configurada.

¿Quieres consultar el precio de algún producto?"""
        
        elif any(palabra in mensaje_lower for palabra in ['ayuda', 'help', 'que puedes', 'funciones']):
            return """💡 **Guía de Funcionalidades**

**Gestión de Datos:**
• Empresas: Registro completo con NIT
• Productos: Con códigos automáticos
• Inventario: Control de stock en tiempo real

**Operaciones:**
• Movimientos: Entrada y salida de productos
• Reportes PDF: Descarga o envío por email
• Alertas: Stock bajo automático

**Usuarios:**
• Administrador: Acceso completo (CRUD)
• Externo: Solo visualización

**Seguridad:**
• Autenticación JWT
• Contraseñas encriptadas
• Permisos diferenciados

¿Sobre qué quieres más detalles?"""
        
        elif any(palabra in mensaje_lower for palabra in ['codigo', 'generar']):
            return """🔢 **Códigos Automáticos**

El sistema genera códigos automáticamente:

**Empresas:**
- 2 primeras letras del nombre + número
- Ejemplo: "Del Alba S.A" → DA01

**Productos:**
- 2 letras de la empresa + número secuencial
- Ejemplo: Empresa DA, producto 5 → DA005

Los códigos son únicos y no se pueden duplicar."""
        
        elif any(palabra in mensaje_lower for palabra in ['usuario', 'login', 'acceso']):
            return """👤 **Sistema de Usuarios**

**Tipos de usuario:**

**Administrador:**
- Acceso completo al sistema
- Crear, editar, eliminar empresas y productos
- Gestionar inventario y movimientos
- Generar reportes

**Externo:**
- Solo visualización
- Ver empresas, productos e inventario
- No puede modificar datos

Cada usuario tiene credenciales únicas con contraseña encriptada."""
        
        elif 'gracias' in mensaje_lower or 'thanks' in mensaje_lower:
            return "¡De nada! 😊 Estoy aquí para ayudarte. Si necesitas algo más, solo pregunta."
        
        elif any(palabra in mensaje_lower for palabra in ['adios', 'bye', 'chao', 'hasta luego']):
            return "¡Hasta pronto! 👋 Estaré aquí cuando me necesites."
        
        else:
            # Respuesta genérica inteligente
            return f"""Entiendo que preguntas sobre: **{mensaje_usuario}**

Actualmente estoy en **modo demo** sin conexión a la API de IA.

Para obtener respuestas más inteligentes y contextualizadas, puedes:
1. Configurar `GEMINI_API_KEY` en el archivo .env
2. Instalar: `poetry add google-genai`

Mientras tanto, puedo ayudarte con:
• Información sobre productos
• Estado del inventario
• Empresas registradas
• Guía de funcionalidades

¿Hay algo específico en lo que pueda ayudarte?"""