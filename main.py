# main.py
import flet as ft
from database import verify_user, get_schedule, save_schedule, register_student

def main(page: ft.Page):
    page.title = "Sistema Escolar"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.fonts = {
        "Poppins": "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap"
    }
    page.theme = ft.Theme(font_family="Poppins")
    
    # Almacenamiento de sesión
    class Session:
        def __init__(self):
            self.user = None
            self.ci = None
            self.role = None
            self.year = None
            self.section = None
            self.name = None
    
    session = Session()

    # ---------- PANTALLA DE LOGIN ----------
    def login(e):
        ci_value = ci_input.value.strip()
        password_value = password_input.value.strip()
        
        if not ci_value or not password_value:
            login_message.value = "Complete todos los campos"
            login_message.color = "red"
            page.update()
            return
            
        user = verify_user(ci_value, password_value)
        if user:
            session.user = user
            session.ci = user[0]
            session.name = user[1]
            session.role = user[3]
            
            if session.role == "student":
                session.year = user[4]
                session.section = user[5]
                page.go("/student")
            else:
                page.go("/coordinator")
        else:
            login_message.value = "Credenciales inválidas"
            login_message.color = "red"
            page.update()

    ci_input = ft.TextField(
        label="Número de CI",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=300,
        border_radius=15
    )
    
    password_input = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        width=300,
        border_radius=15
    )
    
    login_message = ft.Text("", color="red")
    
    login_page = ft.Column(
        [
            ft.Image(src="https://i.imgur.com/8Q7YQ9a.png", width=150, height=150),
            ft.Text("Sistema Escolar", size=30, weight="bold"),
            ci_input,
            password_input,
            ft.ElevatedButton("Ingresar", on_click=login, width=300, height=50),
            login_message
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # ---------- PANTALLA ESTUDIANTE ----------
    def build_student_schedule():
        schedules = get_schedule(session.year, session.section)
        if not schedules:
            return ft.Text("Horario no disponible", size=20)
        
        # Crear tabla de horario
        days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        
        # Encabezados de la tabla
        columns = [
            ft.DataColumn(ft.Text("Hora", weight="bold")),
            *[ft.DataColumn(ft.Text(day, weight="bold")) for day in days]
        ]
        
        # Filas de la tabla
        rows = []
        for hour in range(6):  # 6 horas (1-6)
            cells = [ft.DataCell(ft.Text(f"{hour+1}° Hora"))]
            
            for day in days:
                # Buscar el horario para este día
                day_schedule = next((s for s in schedules if s[3] == day), None)
                class_name = "-"
                if day_schedule:
                    class_name = day_schedule[4 + hour]  # hour1 está en índice 4
                
                cells.append(ft.DataCell(ft.Text(class_name)))
            
            rows.append(ft.DataRow(cells=cells))
        
        return ft.DataTable(
            columns=columns,
            rows=rows,
            border=ft.border.all(1, "#e0e0e0"),
            border_radius=10,
            heading_row_color="#e3f2fd",
        )

    # ---------- PANTALLA COORDINADOR ----------
    year_dropdown = ft.Dropdown(
        label="Año",
        options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
        width=150
    )
    section_dropdown = ft.Dropdown(
        label="Sección",
        options=[ft.dropdown.Option(sec) for sec in ["A", "B", "C"]],
        width=150
    )
    day_dropdown = ft.Dropdown(
        label="Día",
        options=[ft.dropdown.Option(day) for day in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]],
        width=200
    )
    
    hour_inputs = [
        ft.TextField(label=f"{i+1}° Hora", width=200) 
        for i in range(6)
    ]
    
    schedule_message = ft.Text("", color="green")
    
    def save_schedule_click(e):
        if not all([year_dropdown.value, section_dropdown.value, day_dropdown.value]):
            schedule_message.value = "Complete todos los campos"
            schedule_message.color = "red"
            page.update()
            return
        
        data = (
            int(year_dropdown.value),
            section_dropdown.value,
            day_dropdown.value,
            *[h.value for h in hour_inputs]
        )
        save_schedule(data)
        schedule_message.value = "Horario guardado exitosamente!"
        schedule_message.color = "green"
        for h in hour_inputs:
            h.value = ""
        page.update()
    
    # Formulario registro estudiantes
    student_ci = ft.TextField(
        label="CI del Estudiante",
        keyboard_type=ft.KeyboardType.NUMBER,
        width=200
    )
    student_name = ft.TextField(label="Nombre Completo", width=200)
    student_password = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        width=200
    )
    student_year = ft.Dropdown(
        label="Año",
        options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
        width=150
    )
    student_section = ft.Dropdown(
        label="Sección",
        options=[ft.dropdown.Option(sec) for sec in ["A", "B", "C"]],
        width=150
    )
    register_message = ft.Text("", color="green")
    
    def register_student_click(e):
        if not all([student_ci.value, student_name.value, student_password.value, 
                   student_year.value, student_section.value]):
            register_message.value = "Complete todos los campos"
            register_message.color = "red"
            page.update()
            return
            
        if register_student(
            student_ci.value,
            student_name.value,
            int(student_year.value),
            student_section.value,
            student_password.value
        ):
            register_message.value = "Estudiante registrado!"
            register_message.color = "green"
            student_ci.value = ""
            student_name.value = ""
            student_password.value = ""
            student_year.value = ""
            student_section.value = ""
        else:
            register_message.value = "CI ya registrado"
            register_message.color = "red"
        page.update()
    
    coordinator_tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text="Gestión Horarios",
                content=ft.Column([
                    ft.Row([year_dropdown, section_dropdown, day_dropdown]),
                    ft.Divider(),
                    ft.Text("Asignaturas por hora:", weight="bold"),
                    *[hour_inputs[i] for i in range(6)],
                    ft.ElevatedButton(
                        "Guardar Horario", 
                        on_click=save_schedule_click,
                        width=300,
                        height=50
                    ),
                    schedule_message,
                    ft.Container(
                        ft.ElevatedButton(
                            "Cerrar Sesión",
                            on_click=lambda _: page.go("/login"),
                            width=300,
                            height=50,
                            style=ft.ButtonStyle(
                                color="#ffffff",
                                bgcolor="#ef5350"
                            )
                        ),
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(top=20)
                    )
                ], scroll=ft.ScrollMode.AUTO)
            ),
            ft.Tab(
                text="Registrar Estudiantes",
                content=ft.Column([
                    student_ci,
                    student_name,
                    student_password,
                    ft.Row([student_year, student_section]),
                    ft.ElevatedButton(
                        "Registrar Estudiante", 
                        on_click=register_student_click,
                        width=300,
                        height=50
                    ),
                    register_message,
                    ft.Container(
                        ft.ElevatedButton(
                            "Cerrar Sesión",
                            on_click=lambda _: page.go("/login"),
                            width=300,
                            height=50,
                            style=ft.ButtonStyle(
                                color="#ffffff",
                                bgcolor="#ef5350"
                            )
                        ),
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(top=20)
                    )
                ], scroll=ft.ScrollMode.AUTO)
            )
        ]
    )
    
    # ---------- ROUTING ----------
    def route_change(route):
        page.views.clear()
        
        if page.route == "/login":
            page.views.append(ft.View("/login", [login_page]))
        
        elif page.route == "/student":
            page.views.append(
                ft.View(
                    "/student",
                    [
                        ft.AppBar(title=ft.Text(f"Horario - {session.year}°{session.section}")),
                        ft.Text(f"Bienvenido: {session.name}", size=20),
                        ft.Container(
                            build_student_schedule(),
                            padding=20
                        ),
                        ft.Container(
                            ft.ElevatedButton(
                                "Cerrar Sesión",
                                on_click=lambda _: page.go("/login"),
                                width=300,
                                height=50,
                                style=ft.ButtonStyle(
                                    color="#ffffff",
                                    bgcolor="#ef5350"
                                )
                            ),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(top=20)
                        )
                    ],
                    scroll=ft.ScrollMode.AUTO
                )
            )
        
        elif page.route == "/coordinator":
            page.views.append(
                ft.View(
                    "/coordinator",
                    [
                        ft.AppBar(title=ft.Text("Panel de Coordinador")),
                        ft.Text(f"Bienvenido coordinador: {session.name}", size=20),
                        coordinator_tabs
                    ],
                    scroll=ft.ScrollMode.AUTO
                )
            )
        
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/login")

ft.app(target=main, view=ft.FLET_APP)