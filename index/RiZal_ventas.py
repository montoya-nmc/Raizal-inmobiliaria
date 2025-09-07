
import tkinter as tk
from tkinter import ttk, filedialog, messagebox as m
from PIL import Image, ImageTk, ImageDraw
import json
import os
from datetime import datetime

# ===================== Config / Archivos ===================== #
archivo_usuarios = "usuarios.json"
archivo_sugerencias = "sugerencias.txt"
carpeta_fotos = "fotos_perfil"

os.makedirs(carpeta_fotos, exist_ok=True)

# ===================== Cargar usuarios ===================== #
if os.path.exists(archivo_usuarios):
    with open(archivo_usuarios, "r", encoding="utf-8") as f:
        usuarios = json.load(f)
else:
    usuarios = {}

# ===================== Estado global ===================== #
usuario_logueado = ""  # username
root = None  # ventana principal
contenido_frame = None
menu_lateral = None

# ===================== Utilidades ===================== #
def guardar_usuarios():
    with open(archivo_usuarios, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)

def crear_imagen_circular(origen_path, destino_path, size=(200,200)):
    try:
        im = Image.open(origen_path).convert("RGBA").resize(size)
    except Exception:
        im = Image.new("RGBA", size, (160,160,160,255))
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0,0,size[0],size[1]), fill=255)
    im.putalpha(mask)
    im.save(destino_path)

def obtener_ruta_foto(usuario):
    ruta = os.path.join(carpeta_fotos, f"{usuario}.png")
    if not os.path.exists(ruta):
        default = os.path.join(carpeta_fotos, "default.png")
        if not os.path.exists(default):
            img = Image.new("RGB", (400,400), color=(170,170,170))
            draw = ImageDraw.Draw(img)
            draw.text((160,170), (usuario[:1] or "U").upper(), fill=(230,230,230))
            img.save(default)
        crear_imagen_circular(default, ruta, size=(400,400))
    return ruta

def leer_historial_sugerencias(usuario):
    if not os.path.exists(archivo_sugerencias):
        return []
    resultados = []
    with open(archivo_sugerencias, "r", encoding="utf-8") as f:
        for linea in f:
            linea_stripped = linea.strip()
            if not linea_stripped:
                continue
            if linea_stripped.startswith(f"{usuario}:"):
                resultados.append(linea_stripped[len(usuario)+1:].strip())
    return resultados

# ===================== Helpers de UI ===================== #
def ocultar_todo():
    for widget in contenido_frame.winfo_children():
        widget.place_forget()
        widget.pack_forget()
        widget.grid_forget()

def mostrar_inicio():
    ocultar_todo()
    fondo_label.place(x=0, y=0, relwidth=1, relheight=1)
    fondo_label.lower()
    if not usuario_logueado:
        login_embed_frame.place(relx=0.5, y=400, anchor="n")

def mostrar_contacto():
    ocultar_todo()
    contacto_frame.pack(pady=30, fill="both", expand=True)

def mostrar_sugerencias():
    if not usuario_logueado:
        m.showwarning("Acceso denegado", "Debes iniciar sesión para dejar una sugerencia.")
        mostrar_login()
        return
    ocultar_todo()
    sugerencias_frame.pack(pady=30, fill="both", expand=True)

def mostrar_login():
    ocultar_todo()
    login_embed_frame.place(relx=0.5, rely=0.5, anchor="center")

# ===================== Registro / Login (Lógica) ===================== #
def registrar_usuario_embed():
    usuario = entry_usuario.get().strip()
    contrasena = entry_contrasena.get().strip()
    if not usuario or not contrasena:
        m.showerror("Error", "Rellena todos los campos.")
        return
    if usuario in usuarios:
        m.showerror("Error", "El usuario ya existe.")
        return
    usuarios[usuario] = {
        "contrasena": contrasena,
        "nombre": usuario,
        "correo": "",
        "registro": datetime.now().strftime("%Y-%m-%d"),
    }
    guardar_usuarios()
    obtener_ruta_foto(usuario)
    m.showinfo("Éxito", f"Usuario '{usuario}' registrado correctamente.")

def info_embed():
    global usuario_logueado
    usuario = entry_usuario.get().strip()
    contrasena = entry_contrasena.get().strip()
    if not usuario or not contrasena:
        m.showerror("Advertencia", "¡Ingresa los datos correctamente!")
        return
    if usuario in usuarios and usuarios[usuario]["contrasena"] == contrasena:
        usuario_logueado = usuario
        actualizar_perfil_label()
        m.showinfo("Bienvenido", f"Hola, {usuarios[usuario].get('nombre', usuario)} 👋")
        mostrar_perfil_avanzado()
    else:
        m.showerror("Error", "Usuario o contraseña incorrectos.")

def cerrar_sesion():
    global usuario_logueado
    usuario_logueado = ""
    actualizar_perfil_label()
    m.showinfo("Sesión cerrada", "Has cerrado sesión.")
    mostrar_inicio()

# ===================== Perfil avanzado (modal) ===================== #
def actualizar_perfil_label():
    text = f"👤 Perfil: {usuarios[usuario_logueado]['nombre']}" if usuario_logueado else "👤 Perfil"
    perfil_label_main.config(text=text)

def mostrar_perfil_avanzado():
    if not usuario_logueado:
        m.showwarning("Acceso", "Debes iniciar sesión para ver el perfil.")
        mostrar_login()
        return

    user = usuarios.get(usuario_logueado, {})
    user.setdefault("nombre", usuario_logueado)
    user.setdefault("correo", "")
    user.setdefault("registro", datetime.now().strftime("%Y-%m-%d"))
    usuarios[usuario_logueado] = user
    guardar_usuarios()

    perfil_win = tk.Toplevel(root)
    perfil_win.title(f"Perfil — {user['nombre']}")
    perfil_win.geometry("520x520")
    perfil_win.resizable(False, False)
    perfil_win.transient(root)
    perfil_win.grab_set()

    cont = tk.Frame(perfil_win, bg="#f7f7f7", bd=0)
    cont.pack(fill="both", expand=True, padx=12, pady=12)

    header = tk.Frame(cont, bg="#f7f7f7")
    header.pack(fill="x", pady=(6,14))

    ruta_foto = obtener_ruta_foto(usuario_logueado)
    img = Image.open(ruta_foto).resize((110,110))
    img_tk = ImageTk.PhotoImage(img)
    lbl_foto = tk.Label(header, image=img_tk, bg="#f7f7f7")
    lbl_foto.image = img_tk
    lbl_foto.pack(side="left", padx=(10,14))

    info_frame = tk.Frame(header, bg="#f7f7f7")
    info_frame.pack(side="left", fill="y")

    lbl_nombre = tk.Label(info_frame, text=user.get("nombre", usuario_logueado),
                          font=("Arial", 16, "bold"), bg="#f7f7f7")
    lbl_nombre.pack(anchor="w")
    lbl_correo = tk.Label(info_frame, text=user.get("correo", "—"), font=("Arial", 11), bg="#f7f7f7", fg="gray")
    lbl_correo.pack(anchor="w", pady=(4,0))
    lbl_registro = tk.Label(info_frame, text=f"Miembro desde: {user.get('registro')}", font=("Arial", 10), bg="#f7f7f7", fg="gray")
    lbl_registro.pack(anchor="w", pady=(4,0))

    def accion_cambiar_foto():
        ruta = filedialog.askopenfilename(
            title="Seleccionar foto",
            filetypes=[("Imagen", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if ruta:
            destino = os.path.join(carpeta_fotos, f"{usuario_logueado}.png")
            crear_imagen_circular(ruta, destino, size=(400,400))
            nuevo = Image.open(destino).resize((110,110))
            nuevo_tk = ImageTk.PhotoImage(nuevo)
            lbl_foto.configure(image=nuevo_tk)
            lbl_foto.image = nuevo_tk
            m.showinfo("Éxito", "Foto de perfil actualizada.")

    tk.Button(header, text="Cambiar foto", command=accion_cambiar_foto,
              bg="#4D6A4D", fg="white", relief="flat").pack(side="right", padx=10)

    sep = ttk.Separator(cont, orient="horizontal")
    sep.pack(fill="x", pady=6)

    notebook = ttk.Notebook(cont)
    notebook.pack(fill="both", expand=True, pady=(8,0))

    # Info
    frame_info = tk.Frame(notebook, bg="#ffffff")
    notebook.add(frame_info, text="Información")

    tk.Label(frame_info, text="Nombre completo:", bg="#ffffff", anchor="w").pack(fill="x", padx=20, pady=(12,2))
    entry_nombre = tk.Entry(frame_info, font=("Arial", 12))
    entry_nombre.pack(fill="x", padx=20)
    entry_nombre.insert(0, user.get("nombre", usuario_logueado))

    tk.Label(frame_info, text="Correo (opcional):", bg="#ffffff", anchor="w").pack(fill="x", padx=20, pady=(12,2))
    entry_correo = tk.Entry(frame_info, font=("Arial", 12))
    entry_correo.pack(fill="x", padx=20)
    entry_correo.insert(0, user.get("correo", ""))

    def guardar_info():
        nuevo_nombre = entry_nombre.get().strip()
        nuevo_correo = entry_correo.get().strip()
        if not nuevo_nombre:
            m.showwarning("Campo vacío", "El nombre no puede quedar vacío.")
            return
        usuarios[usuario_logueado]["nombre"] = nuevo_nombre
        usuarios[usuario_logueado]["correo"] = nuevo_correo
        guardar_usuarios()
        lbl_nombre.config(text=nuevo_nombre)
        lbl_correo.config(text=nuevo_correo if nuevo_correo else "—")
        actualizar_perfil_label()
        m.showinfo("Guardado", "Información actualizada correctamente.")

    tk.Button(frame_info, text="Guardar cambios", bg="#4CAF50", fg="white", command=guardar_info, relief="flat").pack(pady=18)

    # Seguridad
    frame_seg = tk.Frame(notebook, bg="#ffffff")
    notebook.add(frame_seg, text="Seguridad")

    tk.Label(frame_seg, text="Contraseña actual:", bg="#ffffff", anchor="w").pack(fill="x", padx=20, pady=(12,2))
    entry_contra_actual = tk.Entry(frame_seg, show="*", font=("Arial", 12))
    entry_contra_actual.pack(fill="x", padx=20)

    tk.Label(frame_seg, text="Nueva contraseña:", bg="#ffffff", anchor="w").pack(fill="x", padx=20, pady=(12,2))
    entry_contra_nueva = tk.Entry(frame_seg, show="*", font=("Arial", 12))
    entry_contra_nueva.pack(fill="x", padx=20)

    tk.Label(frame_seg, text="Repetir nueva contraseña:", bg="#ffffff", anchor="w").pack(fill="x", padx=20, pady=(12,2))
    entry_contra_repeat = tk.Entry(frame_seg, show="*", font=("Arial", 12))
    entry_contra_repeat.pack(fill="x", padx=20)

    def cambiar_contrasena_perfil():
        actual = entry_contra_actual.get().strip()
        nueva = entry_contra_nueva.get().strip()
        rep = entry_contra_repeat.get().strip()
        if not actual or not nueva or not rep:
            m.showwarning("Campos", "Rellena todos los campos.")
            return
        if usuarios[usuario_logueado]["contrasena"] != actual:
            m.showerror("Error", "La contraseña actual es incorrecta.")
            return
        if nueva != rep:
            m.showerror("Error", "Las contraseñas nuevas no coinciden.")
            return
        usuarios[usuario_logueado]["contrasena"] = nueva
        guardar_usuarios()
        entry_contra_actual.delete(0, tk.END)
        entry_contra_nueva.delete(0, tk.END)
        entry_contra_repeat.delete(0, tk.END)
        m.showinfo("Éxito", "Contraseña actualizada correctamente.")

    tk.Button(frame_seg, text="Cambiar contraseña", bg="#FF8C42", fg="white", command=cambiar_contrasena_perfil, relief="flat").pack(pady=18)

    # Historial
    frame_hist = tk.Frame(notebook, bg="#ffffff")
    notebook.add(frame_hist, text="Historial")

    tk.Label(frame_hist, text="Sugerencias enviadas:", bg="#ffffff", anchor="w").pack(fill="x", padx=20, pady=(12,0))
    txt_hist = tk.Text(frame_hist, height=10, wrap="word", font=("Arial", 11))
    txt_hist.pack(fill="both", expand=True, padx=20, pady=(6,8))

    sugerencias_usuario = leer_historial_sugerencias(usuario_logueado)
    if sugerencias_usuario:
        for s in sugerencias_usuario:
            txt_hist.insert("end", f"- {s}\n\n")
    else:
        txt_hist.insert("end", "Aún no has enviado sugerencias.")

    txt_hist.config(state="disabled")

    # Pie
    pie = tk.Frame(cont, bg="#f7f7f7")
    pie.pack(fill="x", pady=(6,0))

    def accion_cerrar_sesion_desde_perfil():
        perfil_win.destroy()
        cerrar_sesion()

    tk.Button(pie, text="Cerrar sesión", bg="#A43E3E", fg="white", command=accion_cerrar_sesion_desde_perfil, relief="flat").pack(side="right", padx=12)
    tk.Button(pie, text="Cerrar", command=perfil_win.destroy, relief="flat").pack(side="right")

    perfil_win.wait_window()

# ===================== Ventas (grid centrado + scroll + mouse wheel) ===================== #
def ensure_demo_images():
    # Crea 3 imágenes simples si no existen en la carpeta de trabajo
    def crear_imagen_casa(path, color):
        img = Image.new("RGB", (400, 300), (230, 230, 230))
        draw = ImageDraw.Draw(img)
        draw.rectangle([100, 150, 300, 280], fill=color, outline="black")
        draw.polygon([(100, 150),(200, 80),(300, 150)], fill=(150, 75, 0), outline="black")
        draw.rectangle([180, 200, 220, 280], fill=(80, 50, 20))
        img.save(path)

    if not os.path.exists("casa1.png"):
        crear_imagen_casa("casa1.png", (180, 50, 50))
    if not os.path.exists("casa2.png"):
        crear_imagen_casa("casa2.png", (50, 120, 180))
    if not os.path.exists("casa3.png"):
        crear_imagen_casa("casa3.png", (50, 180, 100))

def mostrar_ventas():
    ocultar_todo()
    ventas_frame.pack(fill="both", expand=True)

    for widget in ventas_frame.winfo_children():
        widget.destroy()

    ensure_demo_images()

    # --- Scroll + contenedor centrado ---
    canvas = tk.Canvas(ventas_frame, bg="#E8E4C6", highlightthickness=0)
    scrollbar = tk.Scrollbar(ventas_frame, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#E8E4C6")

    def on_configure(_):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # centrar horizontalmente el scroll_frame dentro del canvas
        canvas_width = canvas.winfo_width()
        scroll_frame.update_idletasks()
        frame_width = max(scroll_frame.winfo_reqwidth(), canvas_width)
        canvas.itemconfig(window_id, width=frame_width)

    scroll_frame.bind("<Configure>", on_configure)

    window_id = canvas.create_window((0, 0), window=scroll_frame, anchor="n")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Habilitar rueda del mouse
    def _on_mouse_wheel(event):
        # Windows y macOS (delta suele ser +/-120)
        if event.delta:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    def _on_linux_scroll_up(event): canvas.yview_scroll(-1, "units")
    def _on_linux_scroll_down(event): canvas.yview_scroll(1, "units")

    canvas.bind_all("<MouseWheel>", _on_mouse_wheel)    # Windows/macOS
    canvas.bind_all("<Button-4>", _on_linux_scroll_up)  # Linux up
    canvas.bind_all("<Button-5>", _on_linux_scroll_down) # Linux down

    # Productos de ejemplo
    productos = [
        ("casa1.png", "Comprar Casa 1"),
        ("casa2.png", "Comprar Casa 2"),
        ("casa3.png", "Comprar Casa 3"),
        ("casa1.png", "Comprar Casa 4"),
        ("casa2.png", "Comprar Casa 5"),
        ("casa3.png", "Comprar Casa 6"),
        ("casa1.png", "Comprar Casa 7"),
        ("casa2.png", "Comprar Casa 8"),
        ("casa3.png", "Comprar Casa 9"),
    ]

    columnas = 3  # fijo
    for i, (img_path, texto) in enumerate(productos):
        fila = i // columnas
        col = i % columnas

        cont = tk.Frame(scroll_frame, bg="#E8E4C6", padx=20, pady=20)
        cont.grid(row=fila, column=col, sticky="n")

        if os.path.exists(img_path):
            img = Image.open(img_path).resize((220, 160))
            img_tk = ImageTk.PhotoImage(img)
            lbl_img = tk.Label(cont, image=img_tk, bg="#E8E4C6")
            lbl_img.image = img_tk
            lbl_img.pack()
        else:
            tk.Label(cont, text="[Imagen no disponible]", bg="#E8E4C6").pack()

        tk.Button(cont, text=texto, font=("Arial", 12, "bold"),
                  bg="#4D6A4D", fg="white", width=20,
                  command=lambda t=texto: m.showinfo("Compra", f"Has elegido {t}")).pack(pady=8)

    # Centrado de columnas
    for c in range(columnas):
        scroll_frame.grid_columnconfigure(c, weight=1)

# ===================== Componentes de la ventana principal ===================== #
def crear_boton_cascada(parent, texto, subopciones, ancho=20, alto=2):
    contenedor = tk.Frame(parent, bg="#4D6A4D")
    contenedor.pack(fill="x")
    desplegado = tk.BooleanVar(value=False)

    def toggle():
        if desplegado.get():
            for sub in sub_widgets:
                sub.pack_forget()
            desplegado.set(False)
        else:
            for sub in sub_widgets:
                sub.pack(fill="x", padx=30)
            desplegado.set(True)

    btn_principal = tk.Button(
        contenedor, text=texto, command=toggle,
        font=("Arial", 12, "bold"), bg="#4D6A4D", fg="white",
        activebackground="#6A8F6A", activeforeground="white",
        relief="flat", anchor="w", padx=20, pady=10,
        width=ancho, height=alto
    )
    btn_principal.pack(fill="x")

    sub_widgets = []
    for sub_texto, comando in subopciones:
        btn_sub = tk.Button(
            contenedor, text=f"• {sub_texto}", command=comando,
            font=("Arial", 11), bg="#6A8F6A", fg="white",
            activebackground="#87A987", activeforeground="white",
            relief="flat", anchor="w", padx=20, pady=5
        )
        sub_widgets.append(btn_sub)

    return contenedor

def mostrar_ventana_principal():
    global root, contenido_frame, menu_lateral
    global perfil_label_main, fondo_label, sugerencias_frame, contacto_frame, text_sugerencias
    global login_embed_frame, entry_usuario, entry_contrasena
    global ventas_frame

    root = tk.Tk()
    root.title("Bienes Raíces - RaiZal")
    # Pantalla completa (maximizada con bordes)
    try:
        root.state("zoomed")
    except Exception:
        root.attributes("-fullscreen", True)
        root.bind("<Escape>", lambda e: root.destroy())
    root.configure(bg="#E8E4C6")

    main_frame = tk.Frame(root, bg="#FFFFFF")
    main_frame.pack(fill="both", expand=True)

    menu_lateral = tk.Frame(main_frame, bg="#4D6A4D", width=240)
    menu_lateral.pack(side="left", fill="y")

    contenido_frame = tk.Frame(main_frame, bg="#FFFFFF")
    contenido_frame.pack(side="right", fill="both", expand=True)

    boton_estilo = {
        "font": ("Arial", 12, "bold"),
        "bg": "#4D6A4D",
        "fg": "white",
        "activebackground": "#6A8F6A",
        "activeforeground": "white",
        "relief": "flat",
        "bd": 0,
        "anchor": "w",
        "padx": 20,
        "pady": 10,
    }

    # Menú lateral
    tk.Button(menu_lateral, text="🏠 Inicio", command=mostrar_inicio, **boton_estilo).pack(fill="x")
    tk.Button(menu_lateral, text="📬 Contacto", command=mostrar_contacto, **boton_estilo).pack(fill="x")
    tk.Button(menu_lateral, text="💡 Sugerencias", command=mostrar_sugerencias, **boton_estilo).pack(fill="x")
    tk.Button(menu_lateral, text="🛒 Ventas", command=mostrar_ventas, **boton_estilo).pack(fill="x")

    crear_boton_cascada(
        menu_lateral,
        "👤 Perfil",
        [
            ("Abrir perfil", mostrar_perfil_avanzado),
            ("Ver/Enviar sugerencias", mostrar_sugerencias),
            ("Cerrar sesión", cerrar_sesion),
        ],
        ancho=20,
        alto=1
    )

    tk.Button(menu_lateral, text="🚪 Salir", command=root.quit, **boton_estilo).pack(fill="x")

    # Imagen de fondo
    fondo_path = "logo de prueba.PNG"
    if os.path.exists(fondo_path):
        try:
            imagen_fondo = Image.open(fondo_path).resize((1550, 950))
            fondo_img = ImageTk.PhotoImage(imagen_fondo)
            fondo_label_loc = tk.Label(contenido_frame, image=fondo_img, bg="#bfe9e2")
            fondo_label_loc.image = fondo_img
            # asignar a global usado en mostrar_inicio
            globals()['fondo_label'] = fondo_label_loc
        except Exception:
            globals()['fondo_label'] = tk.Label(contenido_frame, bg="#bfe9e2")
    else:
        globals()['fondo_label'] = tk.Label(contenido_frame, bg="#bfe9e2")

    # LOGIN embebido (para cuando el usuario aún no inicia sesión y está en Inicio)
    login_embed_frame = tk.Frame(contenido_frame, bg="#7e9177")
    tk.Label(login_embed_frame, text="Iniciar Sesión", font=("Arial", 18, "bold"), bg="#7e9177").pack(pady=(0, 10))
    tk.Label(login_embed_frame, text="Usuario:", font=("Arial", 14), bg="#7e9177").pack(anchor="w", padx=5)
    entry_usuario = tk.Entry(login_embed_frame, font=("Arial", 14), width=25)
    entry_usuario.pack(padx=5, pady=5)
    tk.Label(login_embed_frame, text="Contraseña:", font=("Arial", 14), bg="#7e9177").pack(anchor="w", padx=5)
    entry_contrasena = tk.Entry(login_embed_frame, show="*", font=("Arial", 14), width=25)
    entry_contrasena.pack(padx=5, pady=5)
    tk.Button(login_embed_frame, text="Entrar", font=("Arial", 12, "bold"), bg="#4D6A4D", fg="white", width=20, command=info_embed).pack(pady=10)
    tk.Button(login_embed_frame, text="Registrarse", font=("Arial", 12, "bold"), bg="#2E5E2E", fg="white", width=20, command=registrar_usuario_embed).pack(pady=5)

    # CONTACTO
    contacto_frame_loc = tk.Frame(contenido_frame, bg="#ADD8E6")
    tk.Label(contacto_frame_loc, text="Contáctanos 📬", font=("Arial", 16, "bold"), bg="#ADD8E6").pack(pady=10)
    correos = ["nicolas.montoya@tecnicopascualbreavo.edu.com", "miguel.baena@tecnicopascualbreavo.edu.com"]
    telefonos = ["+57 305 445 0072", "+57 302 841 9615"]
    for correo in correos:
        tk.Label(contacto_frame_loc, text=correo, font=("Arial", 12), bg="#ADD8E6").pack()
    for tel in telefonos:
        tk.Label(contacto_frame_loc, text=tel, font=("Arial", 14), bg="#ADD8E6").pack()

    globals()['contacto_frame'] = contacto_frame_loc

    # PERFIL LABEL EN MENÚ
    perfil_label_loc = tk.Label(menu_lateral, text="👤 Perfil", bg="#4D6A4D", fg="white",
                                font=("Arial", 12, "bold"), anchor="w", padx=20, pady=10)
    perfil_label_loc.pack(fill="x")
    globals()['perfil_label_main'] = perfil_label_loc

    # SUGERENCIAS
    sugerencias_frame_loc = tk.Frame(contenido_frame, bg="#E8E4C6")
    tk.Label(sugerencias_frame_loc, text="Tus sugerencias nos importan 💌", font=("Arial", 16, "bold"), bg="#79e689").pack(pady=10)
    text_sugerencias_loc = tk.Text(sugerencias_frame_loc, width=80, height=15, font=("Arial", 12))
    text_sugerencias_loc.pack(pady=10)

    def enviar_sugerencias():
        contenido = text_sugerencias_loc.get("1.0", "end").strip()
        if contenido:
            quien = usuario_logueado if usuario_logueado else "Anónimo"
            with open(archivo_sugerencias, "a", encoding="utf-8") as f:
                f.write(f"{quien}: {contenido}\n")
            m.showinfo("¡Gracias!", "Tu sugerencia ha sido enviada.")
            text_sugerencias_loc.delete("1.0", "end")
        else:
            m.showwarning("Campo vacío", "Por favor escribe una sugerencia antes de enviar.")

    tk.Button(sugerencias_frame_loc, text="Enviar sugerencia", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=enviar_sugerencias).pack(pady=10)
    tk.Button(sugerencias_frame_loc, text="Volver al inicio", font=("Arial", 10), background="#61994B", command=mostrar_inicio).pack()

    globals()['sugerencias_frame'] = sugerencias_frame_loc
    globals()['text_sugerencias'] = text_sugerencias_loc

    # VENTAS frame contenedor vacío (rellenado en mostrar_ventas)
    ventas_frame_loc = tk.Frame(contenido_frame, bg="#E8E4C6")
    globals()['ventas_frame'] = ventas_frame_loc

    # Mostrar inicio
    mostrar_inicio()
    root.mainloop()

# ===================== LOGIN como primera ventana ===================== #
def iniciar_sesion():
    global usuario_logueado
    usuario = login_entry_usuario.get().strip()
    contrasena = login_entry_contrasena.get().strip()

    if not usuario or not contrasena:
        m.showerror("Advertencia", "¡Ingresa los datos correctamente!")
        return

    if usuario in usuarios and usuarios[usuario]["contrasena"] == contrasena:
        usuario_logueado = usuario
        m.showinfo("Bienvenido", f"Hola, {usuarios[usuario].get('nombre', usuario)} 👋")
        login_win.destroy()
        mostrar_ventana_principal()
    else:
        m.showerror("Error", "Usuario o contraseña incorrectos.")

def registrar_usuario():
    usuario = login_entry_usuario.get().strip()
    contrasena = login_entry_contrasena.get().strip()
    if not usuario or not contrasena:
        m.showerror("Error", "Rellena todos los campos.")
        return
    if usuario in usuarios:
        m.showerror("Error", "El usuario ya existe.")
        return

    usuarios[usuario] = {
        "contrasena": contrasena,
        "nombre": usuario,
        "correo": "",
        "registro": datetime.now().strftime("%Y-%m-%d"),
    }
    guardar_usuarios()
    obtener_ruta_foto(usuario)
    m.showinfo("Éxito", f"Usuario '{usuario}' registrado correctamente.")

# ---- Ventana de Login ----
login_win = tk.Tk()
login_win.title("Login")
try:
    login_win.state("zoomed")   # pantalla completa
except Exception:
    login_win.attributes("-fullscreen", True)
    login_win.bind("<Escape>", lambda e: login_win.destroy())
login_win.config(bg="#7e9177")

login_frame = tk.Frame(login_win, bg="#7e9177", bd=2, relief="ridge")
login_frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(login_frame, text="Iniciar Sesión", font=("Arial", 18, "bold"),
         bg="#7e9177", fg="white").pack(pady=(0, 15))

tk.Label(login_frame, text="Usuario:", font=("Arial", 14), bg="#7e9177", fg="white").pack(anchor="w", padx=10)
login_entry_usuario = tk.Entry(login_frame, font=("Arial", 14), width=25)
login_entry_usuario.pack(padx=10, pady=5)

tk.Label(login_frame, text="Contraseña:", font=("Arial", 14), bg="#7e9177", fg="white").pack(anchor="w", padx=10)
login_entry_contrasena = tk.Entry(login_frame, show="*", font=("Arial", 14), width=25)
login_entry_contrasena.pack(padx=10, pady=5)

tk.Button(login_frame, text="Entrar", font=("Arial", 12, "bold"),
          bg="#4D6A4D", fg="white", width=20, command=iniciar_sesion).pack(pady=10)

tk.Button(login_frame, text="Registrarse", font=("Arial", 12, "bold"),
          bg="#2E5E2E", fg="white", width=20, command=registrar_usuario).pack(pady=5)

login_win.mainloop()
