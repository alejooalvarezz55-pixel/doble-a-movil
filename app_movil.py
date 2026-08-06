import flet as ft
import os

def main(page: ft.Page):
    # Configuración principal de la app
    page.title = "Doble A"
    page.theme_mode = "dark"
    page.padding = 20

    # --- DISEÑO DE LAS PANTALLAS (Vistas) ---
    
    # 1. Pantalla de CAJA
    vista_caja = ft.Column([
        ft.Text("Módulo de Caja 🍔", size=24, weight="bold", color="red"),
        ft.Text("Aquí irán los botones para cargar ventas, Pedix y cierres de turno.", color="grey"),
        # Aquí meteremos tu código de la PC después
    ], visible=True) # <-- Esta es la que se ve al abrir la app

    # 2. Pantalla de GASTOS
    vista_gastos = ft.Column([
        ft.Text("Carga de Gastos 💸", size=24, weight="bold", color="green"),
        ft.Text("Aquí pondremos el formulario para anotar compras de mercadería y gastos fijos.", color="grey"),
    ], visible=False)

    # 3. Pantalla de STOCK
    vista_stock = ft.Column([
        ft.Text("Control de Stock 📦", size=24, weight="bold", color="blue"),
        ft.Text("Aquí irá el listado de insumos y el botón para marcar faltantes.", color="grey"),
    ], visible=False)

    # --- LÓGICA DE NAVEGACIÓN ---
    def cambiar_pestana(e):
        # e.control.selected_index nos dice qué botón tocó el usuario (0, 1 o 2)
        index = e.control.selected_index
        
        # Mostramos solo la pantalla que coincide con el botón tocado
        vista_caja.visible = (index == 0)
        vista_gastos.visible = (index == 1)
        vista_stock.visible = (index == 2)
        
        page.update() # Actualizamos la pantalla

    # --- BARRA INFERIOR (Menú) ---
    page.navigation_bar = ft.NavigationBar(
        on_change=cambiar_pestana,
        destinations=[
            ft.NavigationDestination(icon="point_of_sale", label="Caja"),
            ft.NavigationDestination(icon="attach_money", label="Gastos"),
            ft.NavigationDestination(icon="inventory", label="Stock"),
        ]
    )

    # Agregamos las tres pantallas a la aplicación
    page.add(vista_caja, vista_gastos, vista_stock)


# Configuración dinámica para servidores en la nube
puerto = int(os.environ.get("PORT", 8550))
ft.app(target=main, host="0.0.0.0", port=puerto, view=ft.AppView.WEB_BROWSER)
