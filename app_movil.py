import flet as ft
import psycopg2
import os

# Tu enlace a Supabase (mismo que en la PC)
DB_URL = "postgresql://postgres.hhttlqfisgqvoevyoqty:Pinares5533@aws-0-us-east-2.pooler.supabase.com:5432/postgres"

def main(page: ft.Page):
    # Configuración de la ventana del celular
    page.title = "Doble A - Móvil"
    page.theme_mode = "dark" 
    page.padding = 20
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    # Función para probar la conexión
    def probar_conexion(e):
        btn_conectar.disabled = True
        status_text.value = "Conectando a la Nube..."
        status_text.color = "yellow"
        page.update()

        try:
            conn = psycopg2.connect(DB_URL)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM usuarios_caja")
            cantidad_usuarios = cursor.fetchone()[0]
            conn.close()
            
            status_text.value = f"☁️ Nube: CONECTADA 🟢\n(Usuarios registrados: {cantidad_usuarios})"
            status_text.color = "green"
        except Exception as ex:
            status_text.value = f"🔴 Error de conexión:\n{ex}"
            status_text.color = "red"
            
        btn_conectar.disabled = False
        page.update()

    # Elementos de la interfaz
    logo_texto = ft.Text("🍔 DOBLE A", size=36, weight="bold", color="red")
    subtitulo = ft.Text("Gestión Móvil en la Nube", size=16, color="grey")
    
    status_text = ft.Text("Esperando conexión...", size=16, text_align="center")
    
    btn_conectar = ft.ElevatedButton(
        "Probar Conexión",
        icon="cloud",
        color="white",
        bgcolor="red",
        on_click=probar_conexion
    )

    page.add(
        logo_texto,
        subtitulo,
        ft.Divider(height=40, color="grey"),
        status_text,
        ft.Container(height=20),
        btn_conectar
    )

# Configuración dinámica para servidores en la nube
puerto = int(os.environ.get("PORT", 8550))
ft.app(target=main, host="0.0.0.0", port=puerto, view=ft.AppView.WEB_BROWSER)