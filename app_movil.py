import flet as ft
import psycopg2
import os

# Lee la URL de la base de datos de forma segura desde las variables de entorno del servidor
DB_URL = os.environ.get("DB_URL")

def main(page: ft.Page):
    page.title = "DOBLE A - Sistema Integral"
    page.theme_mode = "dark"
    page.padding = 15

    # ==========================================
    # 0. PANTALLA DE LOGIN
    # ==========================================
    usuario_input = ft.TextField(label="Nombre de Usuario", color="white", border_color="grey")
    password_input = ft.TextField(label="Clave de Acceso", password=True, can_reveal_password=True, color="white", border_color="grey")
    sucursal_select = ft.Dropdown(
        label="Sucursal de Trabajo",
        options=[ft.dropdown.Option("Almafuerte"), ft.dropdown.Option("Embalse")],
        value="Almafuerte",
        color="white"
    )
    login_status = ft.Text("", size=14)

    def verificar_login(e):
        if not usuario_input.value or not password_input.value:
            login_status.value = "⚠️ Ingresa usuario y clave"
            login_status.color = "yellow"
            page.update()
            return

        if not DB_URL:
            login_status.value = "🔴 Error: Falta configurar la variable de entorno DB_URL"
            login_status.color = "red"
            page.update()
            return

        try:
            conn = psycopg2.connect(DB_URL)
            cursor = conn.cursor()
            cursor.execute("SELECT clave, sucursal FROM usuarios_caja WHERE nombre = %s", (usuario_input.value,))
            row = cursor.fetchone()
            conn.close()

            if row:
                clave_db, sucursal_db = row
                if clave_db == password_input.value:
                    page.clean()
                    cargar_app_principal(usuario_input.value, sucursal_select.value)
                else:
                    login_status.value = "🔴 Clave incorrecta"
                    login_status.color = "red"
                    page.update()
            else:
                login_status.value = "🔴 El usuario no existe"
                login_status.color = "red"
                page.update()
        except Exception as ex:
            login_status.value = f"🔴 Error de conexión: {ex}"
            login_status.color = "red"
            page.update()

    vista_login = ft.Column([
        ft.Container(height=30),
        ft.Text("🍔 DOBLE A", size=32, weight="bold", color="red", text_align="center"),
        ft.Text("Acceso al Sistema en la Nube", size=14, color="grey"),
        ft.Container(height=20),
        usuario_input,
        password_input,
        sucursal_select,
        ft.Container(height=10),
        ft.ElevatedButton("🔑 Ingresar al Sistema", icon="login", color="white", bgcolor="red700", on_click=verificar_login),
        login_status
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # ==========================================
    # APLICACIÓN PRINCIPAL (WEB)
    # ==========================================
    def cargar_app_principal(usuario, sucursal):
        
        # --- 1. MÓDULO DE CAJA ---
        efectivo_input = ft.TextField(label="Efectivo Neto en Cajón ($)", value="0", keyboard_type=ft.KeyboardType.NUMBER)
        digital_input = ft.TextField(label="Transferencias / MP Point ($)", value="0", keyboard_type=ft.KeyboardType.NUMBER)
        gastos_input = ft.TextField(label="Gastos del Turno ($)", value="0", keyboard_type=ft.KeyboardType.NUMBER)
        obs_input = ft.TextField(label="Observaciones de Caja")
        resultado_caja = ft.Text("Carga los valores para calcular el arqueo.", size=14, color="grey")

        def calcular_y_guardar_caja(e):
            try:
                ef = float(efectivo_input.value or 0)
                dg = float(digital_input.value or 0)
                gs = float(gastos_input.value or 0)
                total_rendido = ef + dg + gs
                
                conn = psycopg2.connect(DB_URL)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO cierres_diarios 
                    (fecha, sucursal, total_pedix, efectivo_real, digital_real, gastos, total_rendido, diferencia, observaciones)
                    VALUES (NOW()::text, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (sucursal, 0.0, ef, dg, gs, total_rendido, 0.0, obs_input.value))
                conn.commit()
                conn.close()
                resultado_caja.value = f"✅ Cierre guardado con éxito. Total rendido: ${total_rendido:,.2f}"
                resultado_caja.color = "green"
            except Exception as ex:
                resultado_caja.value = f"🔴 Error al guardar: {ex}"
                resultado_caja.color = "red"
            page.update()

        contenido_caja = ft.Column([
            ft.Text(f"⚖️ Arqueo de Caja - {sucursal}", size=22, weight="bold", color="red"),
            efectivo_input,
            digital_input,
            gastos_input,
            obs_input,
            ft.ElevatedButton("💾 Guardar Cierre en la Nube", icon="save", color="white", bgcolor="red700", on_click=calcular_y_guardar_caja),
            resultado_caja
        ], scroll=ft.ScrollMode.AUTO)

        # --- 2. MÓDULO DE PERSONAL Y SUELDOS ---
        emp_input = ft.TextField(label="Nombre del Empleado")
        pago_input = ft.TextField(label="Pago Diario ($)", value="0", keyboard_type=ft.KeyboardType.NUMBER)
        adelanto_input = ft.TextField(label="Adelanto ($)", value="0", keyboard_type=ft.KeyboardType.NUMBER)
        consumo_input = ft.TextField(label="Consumo Local ($)", value="0", keyboard_type=ft.KeyboardType.NUMBER)
        status_personal = ft.Text("", size=14)

        def guardar_turno(e):
            try:
                conn = psycopg2.connect(DB_URL)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO turnos_personal 
                    (fecha, sucursal, nombre, rol, pago_diario, adelantos, consumos, observaciones)
                    VALUES (CURRENT_DATE::text, %s, %s, %s, %s, %s, %s, %s)
                """, (sucursal, emp_input.value, "General", float(pago_input.value or 0), float(adelanto_input.value or 0), float(consumo_input.value or 0), ""))
                conn.commit()
                conn.close()
                status_personal.value = f"✅ Turno de {emp_input.value} guardado correctamente."
                status_personal.color = "green"
            except Exception as ex:
                status_personal.value = f"🔴 Error: {ex}"
                status_personal.color = "red"
            page.update()

        contenido_personal = ft.Column([
            ft.Text("👥 Control de Personal y Turnos", size=22, weight="bold", color="orange"),
            emp_input,
            pago_input,
            adelanto_input,
            consumo_input,
            ft.ElevatedButton("💾 Registrar Turno", icon="badge", color="white", bgcolor="orange800", on_click=guardar_turno),
            status_personal
        ], scroll=ft.ScrollMode.AUTO)

        # --- 3. MÓDULO DE FALTANTES ---
        contenido_stock = ft.Column([
            ft.Text("📋 Lista de Compras y Faltantes", size=22, weight="bold", color="blue"),
            ft.Text("Los insumos sincronizados de la base de datos aparecerán aquí.", color="grey")
        ], scroll=ft.ScrollMode.AUTO)

        # --- NAVEGACIÓN ---
        pantalla_actual = ft.Container(content=contenido_caja, expand=True)

        def cambiar_vista(e):
            sel = e.control.data
            btn_caja.bgcolor = "red700" if sel == "caja" else "grey800"
            btn_personal.bgcolor = "orange800" if sel == "personal" else "grey800"
            btn_stock.bgcolor = "blue700" if sel == "stock" else "grey800"

            if sel == "caja": pantalla_actual.content = contenido_caja
            elif sel == "personal": pantalla_actual.content = contenido_personal
            elif sel == "stock": pantalla_actual.content = contenido_stock
            page.update()

        btn_caja = ft.ElevatedButton("Caja", icon="point_of_sale", color="white", bgcolor="red700", data="caja", on_click=cambiar_vista)
        btn_personal = ft.ElevatedButton("Personal", icon="badge", color="white", bgcolor="grey800", data="personal", on_click=cambiar_vista)
        btn_stock = ft.ElevatedButton("Faltantes", icon="inventory", color="white", bgcolor="grey800", data="stock", on_click=cambiar_vista)

        menu_superior = ft.Row([btn_caja, btn_personal, btn_stock], scroll=ft.ScrollMode.AUTO)

        header_info = ft.Row([
            ft.Text(f"👤 {usuario} | 📍 {sucursal}", size=14, color="cyan")
        ], alignment=ft.MainAxisAlignment.END)

        page.clean()
        page.add(
            header_info,
            menu_superior,
            ft.Divider(height=15, color="grey800"),
            pantalla_actual
        )

    page.add(vista_login)

puerto = int(os.environ.get("PORT", 8550))
ft.run(main, host="0.0.0.0", port=puerto, view=ft.AppView.WEB_BROWSER)
