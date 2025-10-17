import tkinter as tk
from tkinter import ttk
from datetime import datetime
import platform  # Para detectar el sistema operativo
from tkinter import font  # Importar el módulo font
import win32con
import win32clipboard
import html
import re
import unicodedata

entry_inmuebles = []
fila_domicilios_base = 10  # Fila inicial donde comienzan los domicilios
domicilio_displays = []  # Lista para almacenar los widgets de texto de cada domicilio

# Variables para la serie y el número de orden
entry_serie_orden = None
entry_numero_orden_inicial = None
texto_detencion = ""  # Variable global para el texto de detención
crppa_active = False  # Variable global para el estado del botón CRPPA

display_font_size = 13   # igual a tu tamaño actual de visualización
zoom_base = 13           # 100%

base_font = None
base_font_bold = None
base_font_ital = None

def on_mousewheel(event):
    if platform.system() == 'Windows':
        left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    elif platform.system() == 'Darwin':  # macOS
        left_canvas.yview_scroll(int(-1 * (event.delta)), "units")
    else:  # Sistemas Linux
        if event.num == 4:
            left_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            left_canvas.yview_scroll(1, "units")

def reemplazar_saltos_por_punto_seguido(texto):
    texto = texto.replace('\n', '. ').replace('\r', '. ')
    texto = ' '.join(texto.split())
    return texto

def numero_a_letras(n):
    unidades = (
        '', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis',
        'siete', 'ocho', 'nueve', 'diez', 'once', 'doce',
        'trece', 'catorce', 'quince', 'dieciséis', 'diecisiete',
        'dieciocho', 'diecinueve', 'veinte', 'veintiuno', 'veintidós',
        'veintitrés', 'veinticuatro', 'veinticinco', 'veintiséis',
        'veintisiete', 'veintiocho', 'veintinueve'
    )
    decenas = (
        'treinta', 'cuarenta', 'cincuenta', 'sesenta',
        'setenta', 'ochenta', 'noventa'
    )
    centenas = (
        'ciento', 'doscientos', 'trescientos', 'cuatrocientos',
        'quinientos', 'seiscientos', 'setecientos', 'ochocientos', 'novecientos'
    )

    if n == 0:
        return 'cero'
    elif n == 100:
        return 'cien'
    elif n < 30:
        return unidades[n]
    elif n < 100:
        if n % 10 == 0:
            return decenas[(n // 10) - 3]
        else:
            return f"{decenas[(n // 10) - 3]} y {unidades[n % 10]}"
    elif n < 1000:
        if n % 100 == 0:
            return centenas[(n // 100) - 1]
        else:
            return f"{centenas[(n // 100) - 1]} {numero_a_letras(n % 100)}"
    elif n == 1000:
        return 'mil'
    elif n < 2000:
        return f"mil {numero_a_letras(n % 1000)}"
    elif n < 1000000:
        miles = n // 1000
        resto = n % 1000
        miles_letras = f"{numero_a_letras(miles)} mil"
        if resto > 0:
            miles_letras += f" {numero_a_letras(resto)}"
        return miles_letras
    else:
        return str(n)

def remove_accents(s):
    # Función para eliminar acentos de una cadena
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )

def obtener_fecha_en_letras():
    fecha_actual = datetime.now()
    dia = fecha_actual.day
    mes_numero = fecha_actual.month
    año = fecha_actual.year

    dia_letras = numero_a_letras(dia)
    año_letras = numero_a_letras(año)

    meses = {
        1: 'enero',
        2: 'febrero',
        3: 'marzo',
        4: 'abril',
        5: 'mayo',
        6: 'junio',
        7: 'julio',
        8: 'agosto',
        9: 'septiembre',
        10: 'octubre',
        11: 'noviembre',
        12: 'diciembre'
    }
    mes = meses.get(mes_numero, '')

    return f"{dia_letras} de {mes} de {año_letras}"

def obtener_fecha_formato_corto():
    fecha_actual = datetime.now()
    dia = fecha_actual.day
    mes_numero = fecha_actual.month
    año = fecha_actual.year

    meses = {
        1: 'enero',
        2: 'febrero',
        3: 'marzo',
        4: 'abril',
        5: 'mayo',
        6: 'junio',
        7: 'julio',
        8: 'agosto',
        9: 'septiembre',
        10: 'octubre',
        11: 'noviembre',
        12: 'diciembre'
    }
    mes = meses.get(mes_numero, '')

    return f"{dia} de {mes} de {año}"

def initialize_fonts():
    global base_font, base_font_bold, base_font_ital
    if base_font is None:
        base_font = font.Font(family="Times New Roman", size=display_font_size)
    if base_font_bold is None:
        base_font_bold = font.Font(family="Times New Roman", size=display_font_size, weight='bold')
    if base_font_ital is None:
        base_font_ital = font.Font(family="Times New Roman", size=display_font_size, slant='italic')


def create_tags(text_widget):
    initialize_fonts()
    text_widget.tag_configure('bold', font=base_font_bold)
    text_widget.tag_configure('underline', underline=1, font=base_font)
    text_widget.tag_configure('center', justify='center', font=base_font)
    text_widget.tag_configure('right_align', justify='right', font=base_font)
    text_widget.tag_configure('justified', justify='left', font=base_font)
    text_widget.tag_configure('italic', font=base_font_ital)

    font_height = base_font.metrics('linespace')
    interline_spacing = int(font_height * 0.5)
    text_widget.tag_configure('spacing',
                              spacing1=interline_spacing,
                              spacing2=interline_spacing,
                              spacing3=interline_spacing)


def actualizar_tamano_fuente(nuevo_tamano):
    global display_font_size
    initialize_fonts()
    display_font_size = int(max(8, nuevo_tamano))
    base_font.config(size=display_font_size)
    base_font_bold.config(size=display_font_size)
    base_font_ital.config(size=display_font_size)

    if 'template_display' in globals():
        template_display.config(state=tk.NORMAL, font=base_font)
        template_display.update_idletasks()
        template_display.config(state=tk.DISABLED)

    for txt in domicilio_displays:
        txt.config(state=tk.NORMAL, font=base_font)
        txt.update_idletasks()
        txt.config(state=tk.DISABLED)

    if 'zoom_label' in globals() and zoom_label.winfo_exists():
        porcentaje = int((display_font_size / zoom_base) * 100)
        zoom_label.config(text=f"{porcentaje}%")
        zoom_label.after(1200, lambda: zoom_label.config(text=""))


def on_ctrl_mousewheel(event):
    if event.state & 0x0004:
        delta = 1 if event.delta > 0 else -1
        actualizar_tamano_fuente(display_font_size + delta)
        return "break"

def update_detencion():
    if detencion_var.get() == "con":
        abrir_ventana_detencion()
    else:
        global texto_detencion
        texto_detencion = ""
        update_template()

def abrir_ventana_detencion():
    ventana_detencion = tk.Toplevel(app)
    ventana_detencion.title("Detalles de la Detención")
    ventana_detencion.geometry("600x500")

    tk.Label(ventana_detencion, text="Detalles de la Detención:").pack()

    texto_base_detencion = ("y a los fines de hacer efectiva la medida de coerción dispuesta -detención- "
                            "sobre [prófugo], DNI n.° [DNI], según decreto del día [fecha del decreto de detencion], "
                            "por considerarlo supuesto autor penalmente responsable del delito de …….. (arts. …… del CP). "
                            "Una vez habido se le informará al detenido que puede requerir la presencia de un defensor y dar aviso "
                            "de su situación a quien desee hacerlo. Se le harán conocer los demás derechos que le asisten, arts. 40 "
                            "y concordantes de la Constitución Provincial, y que permanecerá detenido a la orden y disposición de la "
                            "fiscalía de instrucción requirente, a la que deberá comunicarse de inmediato la medida practicada")

    entry_detencion = tk.Text(ventana_detencion, wrap=tk.WORD)
    entry_detencion.insert(tk.END, texto_base_detencion)
    entry_detencion.pack(fill=tk.BOTH, expand=True)

    def guardar_detencion():
        global texto_detencion
        texto_detencion = entry_detencion.get("1.0", tk.END).strip()
        ventana_detencion.destroy()
        update_template()

    boton_listo = tk.Button(ventana_detencion, text="Listo", command=guardar_detencion)
    boton_listo.pack(pady=10)

def update_template():
    fecha = obtener_fecha_en_letras()
    expediente = reemplazar_saltos_por_punto_seguido(entry_expediente.get())
    denuncia = reemplazar_saltos_por_punto_seguido(entry_denuncia.get())
    fiscalia = reemplazar_saltos_por_punto_seguido(fiscalia_var.get())
    
    solicitado_por = solicitado_por_var.get()
    sexo_ayudante = sexo_var.get()
    sexo_fiscal = sexo_fiscal_var.get()
    
    # Texto inicial según solicitante
    if solicitado_por == 'Ayudante Fiscal':
        ayudante_text = "del Sr. Ayudante Fiscal" if sexo_ayudante == "Masculino" else "de la Sra. Ayudante Fiscal"
        if crppa_active:
            entidad_text = "del Centro de Recepción de Procedimientos con Personas Aprehendidas"
        else:
            unidad = reemplazar_saltos_por_punto_seguido(entry_unidad_judicial.get())
            entidad_text = f"de la Unidad Judicial {unidad}"
        inicio_texto = f"A mérito de la solicitud {ayudante_text} {entidad_text}, de las constancias del EE SAC N.° {expediente}"
    else:
        fiscal_article = "del Sr. Fiscal de Instrucción" if sexo_fiscal == "Masculino" else "de la Sra. Fiscal de Instrucción"
        inicio_texto = f"A mérito de la solicitud {fiscal_article} {fiscalia}, de las constancias del EE SAC N.° {expediente}"

    inmuebles = [reemplazar_saltos_por_punto_seguido(entry.get()) for entry in entry_inmuebles if entry.get()]
    if inmuebles:
        if len(inmuebles) == 1:
            inmueble_text = "del inmueble consignado"
            inmuebles_text = inmuebles[0]
        else:
            inmueble_text = "de los inmuebles consignados"
            inmuebles_text = '; '.join([f"{idx+1}) {address}" for idx, address in enumerate(inmuebles)])
    else:
        # Si no hay inmuebles, valores predeterminados
        inmuebles_text = ""
        inmueble_text = "del inmueble consignado"

    # Preparar los fines para la parte
    if texto_detencion:
        fines_para_parte = f"{reemplazar_saltos_por_punto_seguido(entry_fines.get())}, {texto_detencion}"
    else:
        fines_para_parte = reemplazar_saltos_por_punto_seguido(entry_fines.get())

    comisionados = reemplazar_saltos_por_punto_seguido(entry_comisionados.get())
    hora = combobox_hora.get()
    habilitacion_horas = habilitacion_var.get()
    termino = termino_var.get()
    unidad_judicial = reemplazar_saltos_por_punto_seguido(entry_unidad_judicial.get())
    tribunal = reemplazar_saltos_por_punto_seguido(entry_tribunal.get())

    # Texto del trámite
    if solicitado_por == 'Ayudante Fiscal':
        if crppa_active:
            tramite = f"el Centro de Recepción de Procedimientos con Personas Aprehendidas con conocimiento e intervención de la Fiscalía de Instrucción {fiscalia}"
        else:
            tramite = f"la Unidad Judicial {unidad_judicial} con conocimiento e intervención de la Fiscalía de Instrucción {fiscalia}"
    else:
        tramite = f"la Fiscalía de Instrucción {fiscalia}"

    # Texto para habilitación horaria
    texto_italic = ("atento a la intermitencia de la actividad y a la necesidad de llevar adelante el registro "
                    "en el momento investigativamente oportuno para la constatación de que se trata, "
                    "en atención a que las ventas se incrementan en horario nocturno y a las especiales características "
                    "de la actividad que se investiga y su modalidad de comisión")

    if habilitacion_horas == "CON":
        habilitacion_texto = f"CON HABILITACIÓN HORARIA, {texto_italic}, proceda"
    else:
        habilitacion_texto = f"{habilitacion_horas} HABILITACIÓN DE LAS MISMAS, proceda"

    # Verificar encabezado para estupefacientes
    encabezado_seleccionado = encabezado_var.get().strip()
    # Normalizamos espacios para evitar problemas de coincidencia
    sin_saltos = remove_accents(encabezado_seleccionado.replace("\n", " ")).upper()
    sin_saltos = ' '.join(sin_saltos.split())  # Eliminar espacios múltiples

    frase_estupefacientes = ""
    if "FUERZA POLICIAL ANTINARCOTRAFICO" in sin_saltos:
        frase_estupefacientes = "y al secuestro de elementos en infracción con la Ley Nacional de Estupefacientes Nº 23.737, los destinados a su comisión y/o producidos del delito"

    # Incorporar frase_estupefacientes si aplica
    if frase_estupefacientes:
        fines_y_frase = f"{fines_para_parte} {frase_estupefacientes}"
    else:
        fines_y_frase = fines_para_parte

    # Construir el texto final
    if apertura_compulsiva_var.get() == "Sí":
        template_text = f"""
    Córdoba, {fecha}.
    {inicio_texto}, que tengo a la vista -fundamentalmente, {denuncia}- encontrándose reunidos los recaudos de ley (arts. 45 de la Const. Pcial.; 203, 204, 210 y concordantes del C.P.P.); RESUELVO:
    I) Hacer lugar al pedido y ordenar el allanamiento {inmueble_text} en el petitorio del día de la fecha, al solo efecto de {fines_y_frase}, todo en relación al Expediente Electrónico Nº {expediente} labrado por ante {tramite}.
    II) Autorizar la APERTURA de medios de almacenamiento de los dispositivos que se encuentren en el lugar (celulares, computadoras, notebook, tablets o dispositivos de almacenamiento de información digital informática, etc.), quedando asimismo autorizados a relevar la información de archivos existentes y, en su caso, a efectuar el backup de su contenido, interceptación de correo electrónico, redes sociales/conversaciones (mensajes y mensajería instantánea), billeteras electrónicas y cuentas de almacenamiento en línea en tiempo real y el contenido que pudiera existir en éstas; procediendo a la descarga de datos vinculados a la causa y, en caso que no fuera factible, a cambiar la contraseña de acceso por el lapso de quince días hábiles, en procura de determinar la existencia de material relevante, y en caso positivo proceder al secuestro de los dispositivos a los fines de continuar su análisis en Policía Judicial si correspondiere, como así también al secuestro de todo elemento relacionado a la investigación, dejando constancia en acta.
    III) Para el caso de que se efectúe el secuestro de teléfonos celulares y/o dispositivos con conexión a Internet, se autoriza la previsualización de los mismos y, si requirieren para su apertura el uso de huella dactilar o la exhibición del rostro por parte del usuario, se autoriza su apertura compulsiva —en caso de negativa—, ya sea para su análisis en el lugar (del contenido almacenado y de las aplicaciones accesibles) o para quitar medidas de seguridad y proceder a su posterior examen en la oficina técnica del Ministerio Público Fiscal; ello dentro de los límites del Auto n.º 332 de fecha 08/09/2020 de la Excma. Cámara de Acusación de esta ciudad, en “Quipildor, Armando Andrés…”, Expte. SACM n.º 8934647.
    IV) Autorizar al {comisionados}, para que, con personal a sus órdenes, en el término de {termino}, a contar a partir de las {hora} horas del día de la fecha, {habilitacion_texto} a cumplimentarlo, quedando facultado para hacer uso de la fuerza pública, en caso de necesidad. III) Hecho, vuelva a la Fiscalía requirente, sirviendo el presente de atenta nota de remisión y estilo.
    """
    else:
        template_text = f"""
    Córdoba, {fecha}.
    {inicio_texto}, que tengo a la vista -fundamentalmente, {denuncia}- encontrándose reunidos los recaudos de ley (arts. 45 de la Const. Pcial.; 203, 204, 210 y concordantes del C.P.P.); RESUELVO:
    I) Hacer lugar al pedido y ordenar el allanamiento {inmueble_text} en el petitorio del día de la fecha, al solo efecto de {fines_y_frase}, todo en relación al Expediente Electrónico Nº {expediente} labrado por ante {tramite}.
    II) Autorizar al {comisionados}, para que, con personal a sus órdenes, en el término de {termino}, a contar a partir de las {hora} horas del día de la fecha, {habilitacion_texto} a cumplimentarlo, quedando facultado para hacer uso de la fuerza pública, en caso de necesidad.
    III) Hecho, vuelva a la Fiscalía requirente, sirviendo el presente de atenta nota de remisión y estilo.
    """
    # Mostrar en el widget
    template_display.config(state=tk.NORMAL)
    template_display.delete(1.0, tk.END)
    template_text = "\n".join(line.lstrip() for line in template_text.splitlines())
    template_display.insert(tk.END, template_text)
    template_display.tag_add('spacing', '1.0', 'end')

    pos = template_display.search("APERTURA", "1.0", tk.END)
    while pos:
        fin = f"{pos}+{len('APERTURA')}c"
        template_display.tag_add('bold', pos, fin)
        pos = template_display.search("APERTURA", fin, tk.END)

    # Resaltar Unidad Judicial o CRPPA
    if crppa_active:
        buscar_texto_bold = "Centro de Recepción de Procedimientos con Personas Aprehendidas"
    else:
        buscar_texto_bold = f"Unidad Judicial {entry_unidad_judicial.get()}"
    start_index = "1.0"
    while True:
        pos = template_display.search(buscar_texto_bold, start_index, tk.END)
        if not pos:
            break
        end_pos = f"{pos}+{len(buscar_texto_bold)}c"
        template_display.tag_add('bold', pos, end_pos)
        start_index = end_pos

    # Negrita para habilitación (SIN o CON)
    if habilitacion_horas == "CON":
        habilitacion_phrase = "CON HABILITACIÓN HORARIA,"
    else:
        habilitacion_phrase = "SIN HABILITACIÓN DE LAS MISMAS,"
    start_index = "1.0"
    pos = template_display.search(habilitacion_phrase, start_index, tk.END)
    if pos:
        end_pos = f"{pos}+{len(habilitacion_phrase)}c"
        template_display.tag_add('bold', pos, end_pos)

    # Cursiva si hay CON habilitación
    if habilitacion_horas == "CON":
        italic_phrase = texto_italic
        start_index = '1.0'
        pos = template_display.search(italic_phrase, start_index, tk.END)
        if pos:
            end_pos = f"{pos}+{len(italic_phrase)}c"
            template_display.tag_add('italic', pos, end_pos)

    # Aplicar negritas a otras frases clave
    highlight_phrases = [
        (f"Fiscalía de Instrucción {fiscalia}", 'bold'),
        (f"EE SAC N.° {expediente}", 'bold'),
        (f"Expediente Electrónico Nº {expediente}", 'bold'),
        (f"término de {termino}", 'bold')
    ]

    for phrase, tag in highlight_phrases:
        start_index = '1.0'
        while True:
            pos = template_display.search(phrase, start_index, tk.END)
            if not pos:
                break
            end_pos = f"{pos}+{len(phrase)}c"
            template_display.tag_add(tag, pos, end_pos)
            start_index = end_pos

    # Subrayar inmuebles
    for inmueble in inmuebles:
        start_index = '1.0'
        while True:
            pos = template_display.search(inmueble, start_index, tk.END)
            if not pos:
                break
            end_pos = f"{pos}+{len(inmueble)}c"
            template_display.tag_add('underline', pos, end_pos)
            start_index = end_pos

    # Resaltar fines_y_frase
    if fines_y_frase:
        start_index = template_display.search(fines_y_frase, '1.0', tk.END)
        if start_index:
            end_index = f"{start_index}+{len(fines_y_frase)}c"
            template_display.tag_add(start_index, end_index)
    
    if fines_y_frase:
        start_fines = template_display.search(fines_y_frase, "1.0", tk.END)
        if start_fines:
            end_fines = f"{start_fines}+{len(fines_y_frase)}c"
            palabras_a_resaltar = ["secuestro", "registro", "identificación"]
            for palabra in palabras_a_resaltar:
                start_index = start_fines
                while True:
                    pos = template_display.search(palabra, start_index, stopindex=end_fines, nocase=1)
                    if not pos:
                        break
                    end_pos = f"{pos}+{len(palabra)}c"
                    template_display.tag_add('bold', pos, end_pos)
                    start_index = end_pos

    # Formatear texto de detención
    process_texto_detencion_formatting(template_display)

    # Negrita para la hora
    hora_phrase = f"{hora} horas"
    start_index = template_display.search(hora_phrase, '1.0', tk.END)
    if start_index:
        hora_start = start_index
        hora_end = f"{hora_start}+{len(hora_phrase)}c"
        template_display.tag_add('bold', hora_start, hora_end)

    # RESUELVO: en negrita y subrayado
    resuelvo_phrase = "RESUELVO:"
    start_index = template_display.search(resuelvo_phrase, '1.0', tk.END)
    if start_index:
        end_index = f"{start_index}+{len(resuelvo_phrase)}c"
        template_display.tag_add('bold', start_index, end_index)
        template_display.tag_add('underline', start_index, end_index)

    # Tribunal en negrita
    start_index = '1.0'
    while True:
        pos = template_display.search(tribunal, start_index, tk.END)
        if not pos:
            break
        end_pos = f"{pos}+{len(tribunal)}c"
        template_display.tag_add('bold', pos, end_pos)
        start_index = end_pos

    # Numerales en negrita (I), II), III), IV))
    for item in ["I)", "II)", "III)", "IV)"]:
        start_index = '1.0'
        while True:
            pos = template_display.search(item, start_index, tk.END)
            if not pos:
                break
            end_pos = f"{pos}+{len(item)}c"
            template_display.tag_add('bold', pos, end_pos)
            start_index = end_pos

    # Justificar el texto
    lines = template_display.get("1.0", "end-1c").split("\n")
    for i, line in enumerate(lines, start=1):
        line_start = f"{i}.0"
        if 'center' not in template_display.tag_names(line_start) and 'right_align' not in template_display.tag_names(line_start):
            template_display.tag_add('justified', line_start, f"{line_start} lineend")

    template_display.config(state=tk.DISABLED)

    # Actualizar domicilios
    for idx in range(len(entry_inmuebles)):
        update_domicilio_template(idx)

    validar_campos()

def update_domicilio_template(index):
    fecha = obtener_fecha_formato_corto()
    comisionados = reemplazar_saltos_por_punto_seguido(entry_comisionados.get())
    hora = combobox_hora.get()
    termino = termino_var.get()
    habilitacion = habilitacion_var.get()
    domicilio = reemplazar_saltos_por_punto_seguido(entry_inmuebles[index].get())
    fines = reemplazar_saltos_por_punto_seguido(entry_fines.get())
    if texto_detencion:
        fines_para_parte = f"{fines}, {texto_detencion}"
    else:
        fines_para_parte = fines

    # Verificar encabezado para estupefacientes
    encabezado_seleccionado = encabezado_var.get().strip()
    sin_saltos = remove_accents(encabezado_seleccionado.replace("\n", " ")).upper()
    sin_saltos = ' '.join(sin_saltos.split())  # Normalizar espacios

    frase_estupefacientes = ""
    if "FUERZA POLICIAL ANTINARCOTRAFICO" in sin_saltos:
        frase_estupefacientes = "y al secuestro de elementos en infracción con la Ley Nacional de Estupefacientes Nº 23.737, los destinados a su comisión y/o producidos del delito"

    # Incorporar la frase de estupefacientes si corresponde
    if frase_estupefacientes:
        fines_para_parte = f"{fines_para_parte} {frase_estupefacientes}"

    sexo = sexo_var.get()
    solicitado_por = solicitado_por_var.get()
    sexo_fiscal = sexo_fiscal_var.get()
    fiscal_article = "el Sr. Fiscal de Instrucción" if sexo_fiscal == "Masculino" else "la Sra. Fiscal de Instrucción"

    if solicitado_por == 'Ayudante Fiscal':
        ayudante_fiscal = f"el Sr. Ayudante Fiscal" if sexo == "Masculino" else "la Sra. Ayudante Fiscal"
        parte_final = f" al solo efecto de {fines_para_parte}"
    else:
        parte_final = f" al solo efecto de {fines_para_parte}"

    expediente = reemplazar_saltos_por_punto_seguido(entry_expediente.get())
    fiscalia = fiscalia_var.get()
    unidad_judicial = reemplazar_saltos_por_punto_seguido(entry_unidad_judicial.get())
    if solicitado_por == 'Ayudante Fiscal':
        if crppa_active:
            tramite = f"el Centro de Recepción de Procedimientos con Personas Aprehendidas con conocimiento e intervención de la Fiscalía de Instrucción {fiscalia}"
        else:
            tramite = f"la Unidad Judicial {unidad_judicial} con conocimiento e intervención de la Fiscalía de Instrucción {fiscalia}"
    else:
        tramite = f"la Fiscalía de Instrucción {fiscalia_var.get()}"
    serie_orden = reemplazar_saltos_por_punto_seguido(entry_serie_orden.get())
    try:
        initial_number = int(entry_numero_orden_inicial.get())
        numero_orden = str(initial_number + index)
    except ValueError:
        numero_orden = ""
    tribunal = reemplazar_saltos_por_punto_seguido(entry_tribunal.get())

    # Determinar la frase para personal adscripto según el encabezado
    if "FUERZA POLICIAL ANTINARCOTRAFICO" in sin_saltos:
        adscripto_frase = "adscriptos a la Fuerza Policial Antinarcotráfico"
    elif "POLICIA FEDERAL" in sin_saltos:
        adscripto_frase = "adscriptos a la Policía Federal"
    else:
        adscripto_frase = "adscriptos a la Policía de la Provincia de Córdoba"

    if apertura_compulsiva_var.get() == "Sí":
        updated_template = f"""
Córdoba, {fecha}

{encabezado_var.get()}
S/D

     Comunico a Ud. que por resolución de este {tribunal}, se ha resuelto autorizar al {comisionados}, {adscripto_frase}, con personal subordinado y de apoyo a sus órdenes, para que en el día de la fecha a partir de las {hora} horas y por el término de {termino}, {habilitacion} habilitación de horas, proceda al allanamiento del {domicilio}. El allanamiento solicitado se autoriza a los fines de {fines_para_parte}; y a la APERTURA de medios de almacenamiento de los dispositivos que se encuentren en el lugar (celulares, computadoras, notebook, tablets o dispositivos de almacenamiento de información digital informática, etc.) quedando asimismo autorizados a relevar la información de archivos existentes y en su caso a efectuar el backup de su contenido, interceptación de correo electrónico, redes sociales conversaciones (mensajes y mensajería instantánea), billeteras electrónicas y cuentas de almacenamiento en línea en tiempo real y el contenido que pudiera existir en éstas; procediendo a la descarga de datos vinculados a la causa y en caso que no fuera factible, proceder a cambiar la contraseña de acceso por el lapso de quince días hábiles, en procura de determinar la existencia de material relevante y, en caso positivo, proceder al secuestro de los dispositivos a los fines de continuar su análisis en Policía Judicial si correspondiere, como así también al secuestro de todo elemento relacionado a la presente investigación, dejando constancia en acta. Para el caso de que se efectúe el secuestro de teléfonos celulares y/o dispositivos con conexión a Internet, se ha autorizado la previsualización de los mismos y, si estos requirieren para su apertura el uso de huella dactilar o la exhibición del rostro por parte del usuario, se autoriza su apertura compulsiva —en caso de negativa—, ya sea para llevar a cabo su análisis en el lugar del secuestro (tanto del contenido almacenado como de las aplicaciones a las que se pueda acceder) o para quitar las medidas de seguridad propias del móvil y de dicha manera proceder a su posterior examen a través de la oficina técnica del Ministerio Público Fiscal; ello dentro de los límites establecidos por la Excma. Cámara de Acusación de esta ciudad, en “Quipildor, Armando Andrés…”, Expte. SACM n.º 8934647, Auto n.º 332 de fecha 08/09/2020. Todo en relación al Expediente Electrónico Nº {expediente} el que tramita por ante {tramite}.
Se deberá comunicar el resultado del mismo a este Juzgado de Control y a la Fiscalía interviniente, dentro del término de veinticuatro horas, citando orden judicial {serie_orden} - {numero_orden}.  
Queda facultado para hacer uso de la fuerza pública en la medida de su estricta necesidad.  
Si no se realiza el procedimiento o el mismo arroja resultado negativo, se devolverá inmediatamente la presente orden a la Fiscalía de Instrucción interviniente.  
Saluda a Ud. Atte.
"""
    else:
        updated_template = f"""
Córdoba, {fecha}

{encabezado_var.get()}
S/D

     Comunico a Ud. que por resolución de este {tribunal}, se ha resuelto autorizar al {comisionados}, {adscripto_frase}, con personal subordinado y de apoyo a sus órdenes, para que en el día de la fecha a partir de las {hora} horas y por el término de {termino}, {habilitacion} habilitación de horas, proceda al allanamiento del {domicilio}{parte_final}; todo en relación al Expediente Electrónico Nº {expediente} el que tramita por ante {tramite}.
Se deberá comunicar el resultado del mismo a este Juzgado de Control y a la Fiscalía interviniente, dentro del término de veinticuatro horas, citando orden judicial {serie_orden} - {numero_orden}.  
Queda facultado para hacer uso de la fuerza pública en la medida de su estricta necesidad.  
Si no se realiza el procedimiento o el mismo arroja resultado negativo, se devolverá inmediatamente la presente orden a la Fiscalía de Instrucción interviniente.  
Saluda a Ud. Atte.
"""

    domicilio_displays[index].config(state=tk.NORMAL)
    domicilio_displays[index].delete(1.0, tk.END)
    domicilio_displays[index].insert(tk.END, updated_template)
    domicilio_displays[index].tag_add('spacing', '1.0', 'end')

    pos = domicilio_displays[index].search("APERTURA", '1.0', tk.END)
    while pos:
        fin = f"{pos}+{len('APERTURA')}c"
        domicilio_displays[index].tag_add('bold', pos, fin)
        pos = domicilio_displays[index].search("APERTURA", fin, tk.END)

    start_index = domicilio_displays[index].search(f"Córdoba, {fecha}", '1.0', tk.END)
    if start_index:
        end_index = f"{start_index} lineend"
        domicilio_displays[index].tag_add('right_align', start_index, end_index)

    lines_encabezado = encabezado_var.get().split('\n')
    for line in lines_encabezado:
        start_index = domicilio_displays[index].search(line.strip(), '1.0', tk.END)
        if start_index:
            end_index = f"{start_index}+{len(line.strip())}c"
            domicilio_displays[index].tag_add('bold', start_index, end_index)

    sd_phrase = "S/D"
    start_index = domicilio_displays[index].search(sd_phrase, '1.0', tk.END)
    if start_index:
        end_index = f"{start_index}+{len(sd_phrase)}c"
        domicilio_displays[index].tag_add('bold', start_index, end_index)
        domicilio_displays[index].tag_add('underline', start_index, end_index)
    
    fiscalia_phrase = f"Fiscalía de Instrucción {fiscalia}"
    start_index = domicilio_displays[index].search(fiscalia_phrase, '1.0', tk.END)
    if start_index:
        end_index = f"{start_index}+{len(fiscalia_phrase)}c"
        domicilio_displays[index].tag_add('bold', start_index, end_index)

    saludo_phrase = "Saluda a Ud. Atte."
    start_index = domicilio_displays[index].search(saludo_phrase, '1.0', tk.END)
    if start_index:
        end_index = f"{start_index}+{len(saludo_phrase)}c"
        domicilio_displays[index].tag_add(start_index, end_index)

    tribunal_phrase = tribunal
    start_index = domicilio_displays[index].search(tribunal_phrase, '1.0', tk.END)
    if start_index:
        end_index = f"{start_index}+{len(tribunal_phrase)}c"
        domicilio_displays[index].tag_add('bold', start_index, end_index)

    hora_phrase = f"{hora} horas"
    start_index = domicilio_displays[index].search(hora_phrase, '1.0', tk.END)
    if start_index:
        hora_start = start_index
        hora_end = f"{hora_start}+{len(hora_phrase)}c"
        domicilio_displays[index].tag_add('bold', hora_start, hora_end)

    habilitacion_phrase = f"{habilitacion} habilitación de horas"
    start_index = domicilio_displays[index].search(habilitacion_phrase, '1.0', tk.END)
    if start_index:
        end_index = f"{start_index}+{len(habilitacion_phrase)}c"
        domicilio_displays[index].tag_add('bold', start_index, end_index)

    start_index = domicilio_displays[index].search(domicilio, '1.0', tk.END)
    if start_index:
        end_index = f"{start_index}+{len(domicilio)}c"
        domicilio_displays[index].tag_add('underline', start_index, end_index)

    # Ajuste de la frase a buscar según el texto actual
    if apertura_compulsiva_var.get() == "Sí":
        fines_phrase = f"a los fines de {fines_para_parte}"
    else:
        fines_phrase = f"al solo efecto de {fines_para_parte}"
    start_index = domicilio_displays[index].search(fines_phrase, '1.0', tk.END)
    if start_index:
        end_index = f"{start_index}+{len(fines_phrase)}c"
        domicilio_displays[index].tag_add(start_index, end_index)

    # Resaltar determinadas palabras dentro de los fines
    start_fines = domicilio_displays[index].search(fines_phrase, "1.0", tk.END)
    if start_fines:
        end_fines = f"{start_fines}+{len(fines_phrase)}c"
        palabras_a_resaltar = ["secuestro", "registro", "identificación"]
        for palabra in palabras_a_resaltar:
            start_idx = start_fines
            while True:
                pos = domicilio_displays[index].search(palabra, start_idx, stopindex=end_fines, nocase=1)
                if not pos:
                    break
                end_pos = f"{pos}+{len(palabra)}c"
                domicilio_displays[index].tag_add('bold', pos, end_pos)
                start_idx = end_pos

    process_texto_detencion_formatting(domicilio_displays[index])

    expediente_phrase = f"Expediente Electrónico Nº {expediente}"
    start_index = domicilio_displays[index].search(expediente_phrase, '1.0', tk.END)
    if start_index:
        end_index = f"{start_index}+{len(expediente_phrase)}c"
        domicilio_displays[index].tag_add('bold', start_index, end_index)

    if solicitado_por_var.get() == 'Ayudante Fiscal':
        if crppa_active:
            unidad_judicial_phrase = "Centro de Recepción de Procedimientos con Personas Aprehendidas"
        else:
            unidad_judicial_phrase = f"Unidad Judicial {reemplazar_saltos_por_punto_seguido(entry_unidad_judicial.get())}"
        start_index = domicilio_displays[index].search(unidad_judicial_phrase, '1.0', tk.END)
        if start_index:
            end_index = f"{start_index}+{len(unidad_judicial_phrase)}c"
            domicilio_displays[index].tag_add('bold', start_index, end_index)

    orden_phrase = f"orden judicial {serie_orden} - {numero_orden}"
    start_index = domicilio_displays[index].search(orden_phrase, '1.0', tk.END)
    if start_index:
        end_index = f"{start_index}+{len(orden_phrase)}c"
        domicilio_displays[index].tag_add('bold', start_index, end_index)

    start_index = domicilio_displays[index].search("Saluda a Ud. Atte.", '1.0', tk.END)
    if start_index:
        end_index = f"{start_index}+{len('Saluda a Ud. Atte.')}c"
        domicilio_displays[index].tag_add(start_index, end_index)

    body_start = domicilio_displays[index].search(lines_encabezado[-1], '1.0', tk.END)
    body_end = domicilio_displays[index].search("Saluda a Ud. Atte.", body_start, tk.END)
    if body_start and body_end:
        body_start = f"{body_start.split('.')[0]}.0 +4 lines"
        domicilio_displays[index].tag_add('justified', body_start, body_end)

    domicilio_displays[index].config(state=tk.DISABLED)

def agregar_domicilio():
    domicilio_num = len(entry_inmuebles) + 1
    new_label = tk.Label(left_scrollable_frame, text=f"Domicilio {domicilio_num}:")
    new_entry = tk.Entry(left_scrollable_frame, width=60)
    new_row = fila_domicilios_base + (domicilio_num - 1) * 2
    new_label.grid(row=new_row, column=0, sticky="w")
    new_entry.grid(row=new_row, column=1, sticky="ew")
    entry_inmuebles.append(new_entry)
    index = len(entry_inmuebles) - 1
    new_entry.bind("<KeyRelease>", lambda e: (update_template(), validar_campos()))
    new_tab = tk.Frame(notebook)
    notebook.add(new_tab, text=f"Domicilio {domicilio_num}")
    initialize_fonts()
    new_tab_display = tk.Text(new_tab, wrap=tk.WORD, font=base_font)
    new_tab_display.pack(fill=tk.BOTH, expand=True)
    create_tags(new_tab_display)
    new_tab_display.bind("<Control-MouseWheel>", on_ctrl_mousewheel)
    initial_template = f"""
Córdoba, [fecha]

AL SEÑOR
JEFE DE LA POLICÍA DE LA
PROVINCIA DE CÓRDOBA
S__________/___________D

     Comunico a Ud. que por resolución de este [tribunal], se ha resuelto autorizar al [comisionados], adscriptos a la Policía de la Provincia de Córdoba, con personal a sus órdenes, para que en el día de la fecha a partir de las [hora] horas y por el término de [término], [habilitación] habilitación de horas, proceda al allanamiento del [domicilio]; a los fines de [fines], por haber sido así requerido por [ayudante fiscal]; todo en relación al expediente SAC N.° [expediente] el que tramita por ante [trámite].
Se deberá comunicar el resultado del procedimiento dentro del término de veinticuatro horas, citando orden judicial [serie] - [número]. Queda facultado para hacer uso de la fuerza pública en la medida de su estricta necesidad. Si no se realizare el procedimiento o el mismo arrojare resultado negativo, se devolverá inmediatamente la presente orden a la fiscalía de instrucción interviniente.
Saluda a Ud. Atte.
"""
    new_tab_display.insert(tk.END, initial_template)
    new_tab_display.config(state=tk.DISABLED)
    new_tab_display.tag_add('spacing', '1.0', 'end')
    new_tab_scroll = tk.Scrollbar(new_tab, command=new_tab_display.yview)
    new_tab_display.config(yscrollcommand=new_tab_scroll.set)
    new_tab_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    copiar_domicilio_button = tk.Button(new_tab, text=f"Copiar Domicilio {domicilio_num} al Portapapeles", command=lambda: copiar_al_portapapeles(new_tab_display))
    copiar_domicilio_button.pack(pady=10)
    domicilio_displays.append(new_tab_display)
    reubicar_elementos(new_row + 1)
    update_template()

def reubicar_elementos(start_row):
    new_row = start_row + len(entry_inmuebles)
    label_fines.grid(row=new_row + 1, column=0, sticky="w")
    entry_fines.grid(row=new_row + 1, column=1, sticky="ew")
    label_detencion.grid(row=new_row + 2, column=0, sticky="w")
    detencion_sin.grid(row=new_row + 2, column=1, sticky="w")
    detencion_con.grid(row=new_row + 2, column=1, sticky="w", padx=100)
    label_apertura_compulsiva.grid(row=new_row + 3, column=0, sticky="w")
    apertura_no.grid(row=new_row + 3, column=1, sticky="w")
    apertura_si.grid(row=new_row + 3, column=1, sticky="w", padx=100)
    label_comisionados.grid(row=new_row + 4, column=0, sticky="w")
    entry_comisionados.grid(row=new_row + 4, column=1, sticky="ew")
    procesar_comisionados_button.grid(row=new_row + 5, column=1, sticky="ew")
    label_hora.grid(row=new_row + 6, column=0, sticky="w")
    combobox_hora.grid(row=new_row + 6, column=1, sticky="ew")
    label_habilitacion.grid(row=new_row + 7, column=0, sticky="w")
    sin_horas_button.grid(row=new_row + 7, column=1, sticky="w")
    con_horas_button.grid(row=new_row + 7, column=1, sticky="w", padx=100)
    label_termino.grid(row=new_row + 8, column=0, sticky="w")
    termino_combobox.grid(row=new_row + 8, column=1, sticky="ew")
    label_orden.grid(row=new_row + 9, column=0, sticky="w")
    frame_orden.grid(row=new_row + 9, column=1, sticky="ew")
    label_encabezado.grid(row=new_row + 10, column=0, sticky="w")
    encabezado_combo.grid(row=new_row + 10, column=1, sticky="ew")

def mostrar_ocultar_campos(*args):
    global crppa_active
    solicitado_por = solicitado_por_var.get()
    if solicitado_por == 'Ayudante Fiscal':
        unidad_judicial_label.grid(row=6, column=0, sticky="w")
        frame_unidad_judicial.grid(row=6, column=1, sticky="ew")
        sexo_label.grid(row=7, column=0, sticky="w")
        sexo_masculino.grid(row=7, column=1, sticky="w")
        sexo_femenino.grid(row=7, column=1, sticky="w", padx=100)
    else:
        unidad_judicial_label.grid_forget()
        frame_unidad_judicial.grid_forget()
        crppa_active = False
        entry_unidad_judicial.config(state='normal')
        crppa_button.config(relief='raised')
        sexo_label.grid_forget()
        sexo_masculino.grid_forget()
        sexo_femenino.grid_forget()
    update_template()

def procesar_comisionados():
    texto = entry_comisionados.get()
    palabras = texto.split()
    palabras_procesadas = []
    conectores = ["y/o", "y/u", "y", "o", "u"]
    for palabra in palabras:
        if palabra.lower() in conectores:
            palabras_procesadas.append(palabra.lower())
        else:
            palabras_procesadas.append(palabra.capitalize())
    texto_procesado = ' '.join(palabras_procesadas)
    entry_comisionados.delete(0, tk.END)
    entry_comisionados.insert(0, texto_procesado)
    update_template()

def process_texto_detencion_formatting(text_widget):
    if texto_detencion:
        start_index = text_widget.search(texto_detencion, '1.0', tk.END)
        if start_index:
            texto_detencion_length = len(texto_detencion)
            end_index = f"{start_index}+{texto_detencion_length}c"
            texto_detencion_text = text_widget.get(start_index, end_index)
            exceptions = ["CP", "C.P.", "Código Penal", "Codigo Penal", "Una", "Se", "Constitución", "Provincial", "DNI", "D.N.I."]
            pattern = r"\b(|[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+|detención|)\b"
            for match in re.finditer(pattern, texto_detencion_text):
                word = match.group()
                if word in exceptions:
                    continue
                rel_start = match.start()
                rel_end = match.end()
                abs_start_index = f"{start_index}+{rel_start}c"
                abs_end_index = f"{start_index}+{rel_end}c"
                text_widget.tag_add('bold', abs_start_index, abs_end_index)

def copiar_al_portapapeles(text_widget):
    """
    Copia el contenido del widget al portapapeles en formato RTF, HTML y texto plano,
    manteniendo los formatos originales.
    """
    # Generar RTF y HTML
    rtf_data = generate_rtf(text_widget)  # Mantener intacta la función RTF
    html_data = generate_html(text_widget)  # HTML con interlineado de 1.5
    plain_text = text_widget.get("1.0", "end-1c")  # Texto plano

    # Formatos específicos para el portapapeles
    CF_RTF = win32clipboard.RegisterClipboardFormat("Rich Text Format")
    CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")

    # Estructurar HTML para el portapapeles
    clipboard_html = create_clipboard_html(html_data)

    # Copiar los datos al portapapeles
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, plain_text)  # Texto plano
        win32clipboard.SetClipboardData(CF_RTF, rtf_data.encode('cp1252'))  # Mantener RTF
        win32clipboard.SetClipboardData(CF_HTML, clipboard_html.encode('utf-8'))  # HTML actualizado
    finally:
        win32clipboard.CloseClipboard()

def generate_rtf(text_widget):
    rtf_header = r"""{\rtf1\ansi\deff0
{\fonttbl{\f0 Times New Roman;}}
{\colortbl;\red0\green0\blue0;}
"""
    # Configuración de interlineado 1.5
    rtf_body = r"\pard\sl360\slmult1 "

    all_text = text_widget.get("1.0", "end-1c")
    lines = all_text.split('\n')

    for line_num in range(1, len(lines) + 1):
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        line_tags = text_widget.tag_names(line_start)

        # Alineación de párrafo
        if 'center' in line_tags:
            rtf_body += r"\qc "
        elif 'right_align' in line_tags:
            rtf_body += r"\qr "
        elif 'justified' in line_tags:
            rtf_body += r"\qj "
        else:
            rtf_body += r"\qj "

        line_text = text_widget.get(line_start, line_end)
        is_bold = False
        is_underline = False

        for index, char in enumerate(line_text):
            char_index = f"{line_num}.{index}"
            char_tags = text_widget.tag_names(char_index)

            # Control de negrita
            if 'bold' in char_tags and not is_bold:
                rtf_body += r"\b "
                is_bold = True
            elif 'bold' not in char_tags and is_bold:
                rtf_body += r"\b0 "
                is_bold = False

            # Control de subrayado
            if 'underline' in char_tags and not is_underline:
                rtf_body += r"\ul "
                is_underline = True
            elif 'underline' not in char_tags and is_underline:
                rtf_body += r"\ulnone "
                is_underline = False

            # Escapar caracteres especiales en RTF
            if char == '\\':
                rtf_body += r"\\"
            elif char == '{':
                rtf_body += r"\{"
            elif char == '}':
                rtf_body += r"\}"
            elif ord(char) > 127:
                rtf_body += r"\'%02x" % (ord(char) & 0xFF)
            else:
                rtf_body += char

        # Al final de la línea, si quedaron formatos abiertos, cerrarlos:
        if is_bold:
            rtf_body += r"\b0 "
            is_bold = False
        if is_underline:
            rtf_body += r"\ulnone "
            is_underline = False

        rtf_body += r"\par "

    rtf_footer = r"}"
    return rtf_header + rtf_body + rtf_footer

def generate_html(text_widget):
    """
    Genera el texto en formato HTML a partir del contenido del widget,
    con interlineado de 1.5 y espaciado uniforme entre líneas y párrafos.
    """
    all_text = text_widget.get("1.0", "end-1c")
    lines = all_text.split('\n')

    html_body = ""

    for line_num in range(1, len(lines) + 1):
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"

        line_tags = text_widget.tag_names(line_start)

        # Aplicar alineación y estilo CSS
        paragraph_style = "line-height: 1.5; margin: 0;"  # Interlineado de 1.5 y sin márgenes
        if 'center' in line_tags:
            paragraph_style += "text-align: center;"
        elif 'right_align' in line_tags:
            paragraph_style += "text-align: right;"
        elif 'justified' in line_tags:
            paragraph_style += "text-align: justify;"
        else:
            paragraph_style += "text-align: justify;"

        html_body += f'<p style="{paragraph_style}">'

        is_bold = False
        is_underline = False

        line_text = text_widget.get(line_start, line_end)
        index = 0
        while index < len(line_text):
            char_index = f"{line_num}.{index}"
            char = line_text[index]
            char_tags = text_widget.tag_names(char_index)

            # Negrita
            if 'bold' in char_tags and not is_bold:
                html_body += '<b>'
                is_bold = True
            if 'underline' in char_tags and not is_underline:
                html_body += '<u>'
                is_underline = True

            # Cerrar etiquetas si no aplican más
            if 'bold' not in char_tags and is_bold:
                html_body += '</b>'
                is_bold = False
            if 'underline' not in char_tags and is_underline:
                html_body += '</u>'
                is_underline = False

            # Escapar caracteres HTML especiales
            html_body += html.escape(char)
            index += 1

        # Cerrar etiquetas abiertas al final de la línea
        if is_bold:
            html_body += '</b>'
            is_bold = False
        if is_underline:
            html_body += '</u>'
            is_underline = False

        html_body += '</p>'

    # Construir el documento HTML completo
    html_complete = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{
    font-family: 'Times New Roman', serif;
    font-size: 13pt;
    line-height: 1.5; /* Configuración global de interlineado */
    margin: 0; /* Sin margen global */
    padding: 0; /* Sin relleno global */
}}
p {{
    line-height: 1.5; /* Interlineado fijo */
    margin: 0; /* Sin margen adicional entre párrafos */
}}
</style>
</head>
<body>
<!--StartFragment-->
{html_body}
<!--EndFragment-->
</body>
</html>
"""
    return html_complete

def create_clipboard_html(html_data):
    """
    Estructura el contenido HTML con los metadatos necesarios para el portapapeles.
    """
    start_marker = "<!--StartFragment-->"
    end_marker = "<!--EndFragment-->"

    start_fragment = html_data.find(start_marker)
    end_fragment = html_data.find(end_marker)

    if start_fragment == -1:
        start_fragment = 0
    else:
        start_fragment += len(start_marker)

    if end_fragment == -1:
        end_fragment = len(html_data)

    html_header = """Version:0.9
StartHTML:{0:010d}
EndHTML:{1:010d}
StartFragment:{2:010d}
EndFragment:{3:010d}
StartSelection:{2:010d}
EndSelection:{3:010d}
"""

    html_data_bytes = html_data.encode('utf-8')
    # Generar encabezado temporal
    temp_header = html_header.format(0, 0, 0, 0)
    start_html = len(temp_header)
    end_html = start_html + len(html_data_bytes)

    # Ajustar índices relativos al inicio del HTML
    fragment_start = start_html + start_fragment
    fragment_end = start_html + end_fragment

    # Reemplazar los valores con los correctos
    final_header = html_header.format(start_html, end_html, fragment_start, fragment_end)
    clipboard_html = final_header + html_data

    return clipboard_html

def toggle_crppa():
    global crppa_active
    crppa_active = not crppa_active
    if crppa_active:
        entry_unidad_judicial.config(state='disabled')
        crppa_button.config(relief='sunken')
    else:
        entry_unidad_judicial.config(state='normal')
        crppa_button.config(relief='raised')
    update_template()

def validar_campos():
    # Validar que todos los entry y el combobox_hora estén completos
    tribunal = entry_tribunal.get().strip()
    expediente = entry_expediente.get().strip()
    denuncia = entry_denuncia.get().strip()
    # Al menos el primer domicilio
    domicilio_1 = entry_inmuebles[0].get().strip() if entry_inmuebles else ""
    fines = entry_fines.get().strip()
    comisionados = entry_comisionados.get().strip()
    serie_orden = entry_serie_orden.get().strip()
    numero_orden_inicial = entry_numero_orden_inicial.get().strip()
    hora = combobox_hora.get().strip()

    # Verificar que no estén vacíos
    if (tribunal and expediente and denuncia and domicilio_1 and 
        fines and comisionados and serie_orden and numero_orden_inicial and hora):
        copiar_decreto_button.config(state=tk.NORMAL)
    else:
        copiar_decreto_button.config(state=tk.DISABLED)


app = tk.Tk()
app.title("Orden de Allanamiento")
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
window_width = int(screen_width * 0.900)
window_height = int(screen_height * 0.8)
x_coordinate = int((screen_width / 2) - (window_width / 2))
y_coordinate = int((screen_height / 2) - (window_height / 2))
app.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

left_frame = tk.Frame(app)
right_frame = tk.Frame(app)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
right_frame.pack_propagate(0)
right_frame.config(width=500)

left_canvas = tk.Canvas(left_frame)
left_scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=left_canvas.yview)
left_scrollable_frame = tk.Frame(left_canvas, bd=0, highlightthickness=0)
def on_frame_configure(event):
    bbox = left_canvas.bbox("all")
    if bbox:
        x0, y0, x1, y1 = bbox
        left_canvas.configure(scrollregion=(x0, 0, x1, y1))
left_scrollable_frame.columnconfigure(0, weight=0)
left_scrollable_frame.columnconfigure(1, weight=1)
left_canvas.create_window((0, 0), window=left_scrollable_frame, anchor='nw')
left_canvas.configure(yscrollcommand=left_scrollbar.set)
left_scrollable_frame.bind("<Configure>", on_frame_configure)
left_canvas.pack(side="left", fill="both", expand=True)
left_scrollbar.pack(side="right", fill="y")

if platform.system() == 'Linux':
    left_canvas.bind_all("<Button-4>", on_mousewheel)
    left_canvas.bind_all("<Button-5>", on_mousewheel)
else:
    left_canvas.bind_all("<MouseWheel>", on_mousewheel)
def _on_enter(event):
    left_canvas.bind_all("<MouseWheel>", on_mousewheel)
def _on_leave(event):
    left_canvas.unbind_all("<MouseWheel>")
left_canvas.bind("<Enter>", _on_enter)
left_canvas.bind("<Leave>", _on_leave)

notebook = ttk.Notebook(right_frame)
notebook.pack(fill=tk.BOTH, expand=True)
decreto_tab = tk.Frame(notebook)
notebook.add(decreto_tab, text="Decreto")
initialize_fonts()
template_display = tk.Text(decreto_tab, wrap=tk.WORD, font=base_font)
template_display.pack(fill=tk.BOTH, expand=True)
create_tags(template_display)
template_display.config(state=tk.DISABLED)
decreto_scrollbar = tk.Scrollbar(decreto_tab, command=template_display.yview)
template_display.config(yscrollcommand=decreto_scrollbar.set)
decreto_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
copiar_decreto_button = tk.Button(decreto_tab, text="Copiar Decreto al Portapapeles", command=lambda: copiar_al_portapapeles(template_display))
copiar_decreto_button.pack(pady=10)
control_frame = tk.Frame(decreto_tab)
control_frame.pack(pady=5)
zoom_label = tk.Label(control_frame, text="", font=("Times New Roman", 11))
zoom_label.pack(side=tk.LEFT, padx=5)
template_display.bind("<Control-MouseWheel>", on_ctrl_mousewheel)

domicilio_tab_1 = tk.Frame(notebook)
notebook.add(domicilio_tab_1, text="Domicilio 1")
domicilio_display_1 = tk.Text(domicilio_tab_1, wrap=tk.WORD, font=base_font)
domicilio_display_1.pack(fill=tk.BOTH, expand=True)
create_tags(domicilio_display_1)
domicilio_display_1.bind("<Control-MouseWheel>", on_ctrl_mousewheel)

initial_template = f"""
Córdoba, [fecha]

AL SEÑOR 
JEFE DE LA POLICÍA DE LA
PROVINCIA DE CÓRDOBA
S__________/___________D

     Comunico a Ud. que por resolución de este [tribunal], se ha resuelto autorizar al [comisionados], adscriptos a la Policía de la Provincia de Córdoba, con personal a sus órdenes, para que en el día de la fecha a partir de las [hora] horas y por el término de [término], [habilitación] habilitación de horas, proceda al allanamiento del [domicilio]; a los fines de [fines], por haber sido así requerido por [ayudante fiscal]; todo en relación al expediente SAC N.° [expediente] el que tramita por ante [trámite].
Se deberá comunicar el resultado del procedimiento dentro del término de veinticuatro horas, citando orden judicial [serie] - [número]. Queda facultado para hacer uso de la fuerza pública en la medida de su estricta necesidad. Si no se realizare el procedimiento o el mismo arrojare resultado negativo, se devolverá inmediatamente la presente orden a la fiscalía de instrucción interviniente.
Saluda a Ud. Atte.
"""
domicilio_display_1.insert(tk.END, initial_template)
domicilio_display_1.config(state=tk.DISABLED)
domicilio_scrollbar_1 = tk.Scrollbar(domicilio_tab_1, command=domicilio_display_1.yview)
domicilio_display_1.config(yscrollcommand=domicilio_scrollbar_1.set)
domicilio_scrollbar_1.pack(side=tk.RIGHT, fill=tk.Y)
copiar_domicilio1_button = tk.Button(domicilio_tab_1, text="Copiar Domicilio 1 al Portapapeles", command=lambda: copiar_al_portapapeles(domicilio_display_1))
copiar_domicilio1_button.pack(pady=10)
domicilio_displays.append(domicilio_display_1)

tk.Label(left_scrollable_frame, text="Tribunal:").grid(row=0, column=0, sticky="w")
entry_tribunal = tk.Entry(left_scrollable_frame, width=60)
entry_tribunal.insert(0, "Juzgado de Control y Faltas N.° 11")
entry_tribunal.grid(row=0, column=1, sticky="ew")
entry_tribunal.bind("<KeyRelease>", lambda e: (update_template(), validar_campos()))

tk.Label(left_scrollable_frame, text="Número de expediente:").grid(row=1, column=0, sticky="w")
entry_expediente = tk.Entry(left_scrollable_frame, width=60)
entry_expediente.grid(row=1, column=1, sticky="ew")
entry_expediente.bind("<KeyRelease>", lambda e: (update_template(), validar_campos()))

tk.Label(left_scrollable_frame, text="Denuncia y declaraciones:").grid(row=2, column=0, sticky="w")
entry_denuncia = tk.Entry(left_scrollable_frame, width=60)
entry_denuncia.grid(row=2, column=1, sticky="ew")
entry_denuncia.bind("<KeyRelease>", lambda e: (update_template(), validar_campos()))

tk.Label(left_scrollable_frame, text="Solicitado por:").grid(row=4, column=0, sticky="w")
solicitado_por_var = tk.StringVar()
solicitado_por_combo = ttk.Combobox(left_scrollable_frame, textvariable=solicitado_por_var, state='readonly', width=57)
solicitado_por_combo['values'] = ['Ayudante Fiscal', 'Fiscal de Instrucción']
solicitado_por_combo.grid(row=4, column=1, sticky="ew")
solicitado_por_combo.bind("<<ComboboxSelected>>", lambda e: mostrar_ocultar_campos())

unidad_judicial_label = tk.Label(left_scrollable_frame, text="Unidad Judicial:")

frame_unidad_judicial = tk.Frame(left_scrollable_frame)
frame_unidad_judicial.columnconfigure(0, weight=1)

entry_unidad_judicial = tk.Entry(frame_unidad_judicial, width=50)
entry_unidad_judicial.bind("<KeyRelease>", lambda e: (update_template(), validar_campos()))
entry_unidad_judicial.pack(side=tk.LEFT, fill=tk.X, expand=True)

crppa_button = tk.Button(frame_unidad_judicial, text="CRPPA", command=toggle_crppa)
crppa_button.pack(side=tk.LEFT, padx=5)

sexo_label = tk.Label(left_scrollable_frame, text="Género del Ayudante Fiscal:")
sexo_var = tk.StringVar(value="Masculino")
sexo_masculino = tk.Radiobutton(left_scrollable_frame, text="Masculino", variable=sexo_var, value="Masculino", command=lambda: (update_template()))
sexo_femenino = tk.Radiobutton(left_scrollable_frame, text="Femenino", variable=sexo_var, value="Femenino", command=lambda: (update_template()))

tk.Label(left_scrollable_frame, text="Fiscalía de Instrucción:").grid(row=8, column=0, sticky="w")
fiscalia_var = tk.StringVar()
fiscalia_combo = ttk.Combobox(left_scrollable_frame, textvariable=fiscalia_var, width=57, state="normal")  # Permite escribir
fiscalia_combo['values'] = ['del Distrito III Turno 4', 'del Distrito III Turno 6', 'de Lucha Contra el Narcotráfico del Turno 3']
fiscalia_combo.grid(row=8, column=1, sticky="ew")
fiscalia_combo.bind("<<ComboboxSelected>>", lambda e: update_template())

sexo_fiscal_label = tk.Label(left_scrollable_frame, text="Género del Fiscal de Instrucción:")
sexo_fiscal_var = tk.StringVar(value="Masculino")
sexo_fiscal_masculino = tk.Radiobutton(left_scrollable_frame, text="Masculino", variable=sexo_fiscal_var, value="Masculino", command=lambda: update_template())
sexo_fiscal_femenino = tk.Radiobutton(left_scrollable_frame, text="Femenino", variable=sexo_fiscal_var, value="Femenino", command=lambda: update_template())
sexo_fiscal_label.grid(row=9, column=0, sticky="w")
sexo_fiscal_masculino.grid(row=9, column=1, sticky="w")
sexo_fiscal_femenino.grid(row=9, column=1, sticky="w", padx=100)

tk.Label(left_scrollable_frame, text="Domicilio a allanar:").grid(row=10, column=0, sticky="w")
entry_inmueble = tk.Entry(left_scrollable_frame, width=60)
entry_inmueble.grid(row=10, column=1, sticky="ew")
entry_inmueble.bind("<KeyRelease>", lambda e: (update_template(), validar_campos()))
entry_inmuebles.append(entry_inmueble)
agregar_domicilio_button = tk.Button(left_scrollable_frame, text="Agregar otro domicilio", command=agregar_domicilio)
agregar_domicilio_button.grid(row=11, column=1, sticky="ew")

label_fines = tk.Label(left_scrollable_frame, text="Fines del allanamiento:")
label_fines.grid(row=12, column=0, sticky="w")
entry_fines = tk.Entry(left_scrollable_frame, width=60)
entry_fines.grid(row=12, column=1, sticky="ew")
entry_fines.bind("<KeyRelease>", lambda e: (update_template(), validar_campos()))

label_detencion = tk.Label(left_scrollable_frame, text="Detención:")
label_detencion.grid(row=13, column=0, sticky="w")
detencion_var = tk.StringVar(value="sin")
detencion_sin = tk.Radiobutton(left_scrollable_frame, text="Sin", variable=detencion_var, value="sin", command=update_detencion)
detencion_sin.grid(row=13, column=1, sticky="w")
detencion_con = tk.Radiobutton(left_scrollable_frame, text="Con", variable=detencion_var, value="con", command=update_detencion)
detencion_con.grid(row=13, column=1, sticky="w", padx=100)

label_apertura_compulsiva = tk.Label(left_scrollable_frame, text="Apertura compulsiva:")
label_apertura_compulsiva.grid(row=14, column=0, sticky="w")
apertura_compulsiva_var = tk.StringVar(value="No")
apertura_no = tk.Radiobutton(left_scrollable_frame, text="No", variable=apertura_compulsiva_var, value="No", command=update_template)
apertura_no.grid(row=14, column=1, sticky="w")
apertura_si = tk.Radiobutton(left_scrollable_frame, text="Sí", variable=apertura_compulsiva_var, value="Sí", command=update_template)
apertura_si.grid(row=14, column=1, sticky="w", padx=100)

label_comisionados = tk.Label(left_scrollable_frame, text="Comisionados:")
label_comisionados.grid(row=15, column=0, sticky="w")
entry_comisionados = tk.Entry(left_scrollable_frame, width=60)
entry_comisionados.grid(row=15, column=1, sticky="ew")
entry_comisionados.bind("<KeyRelease>", lambda e: (update_template(), validar_campos()))
procesar_comisionados_button = tk.Button(left_scrollable_frame, text="Comisionados en minúscula", command=procesar_comisionados)
procesar_comisionados_button.grid(row=16, column=1, sticky="ew")

horas_24 = [f"{h:02d}:{m:02d}" for h in range(24) for m in range(0, 60, 30)]
label_hora = tk.Label(left_scrollable_frame, text="Hora (formato 00:00):")
label_hora.grid(row=17, column=0, sticky="w")
hora_var = tk.StringVar()
combobox_hora = ttk.Combobox(left_scrollable_frame, textvariable=hora_var, values=horas_24, state='readonly', width=57)
combobox_hora.grid(row=17, column=1, sticky="ew")
combobox_hora.bind("<<ComboboxSelected>>", lambda e: (update_template(), validar_campos()))

label_habilitacion = tk.Label(left_scrollable_frame, text="Habilitación de horas:")
label_habilitacion.grid(row=18, column=0, sticky="w")
habilitacion_var = tk.StringVar(value="SIN")
sin_horas_button = tk.Radiobutton(left_scrollable_frame, text="SIN", variable=habilitacion_var, value="SIN", command=update_template)
sin_horas_button.grid(row=18, column=1, sticky="w")
con_horas_button = tk.Radiobutton(left_scrollable_frame, text="CON", variable=habilitacion_var, value="CON", command=update_template)
con_horas_button.grid(row=18, column=1, sticky="w", padx=100)

label_termino = tk.Label(left_scrollable_frame, text="Término:")
label_termino.grid(row=19, column=0, sticky="w")
termino_var = tk.StringVar(value="veinticuatro horas")
termino_combobox = ttk.Combobox(left_scrollable_frame, textvariable=termino_var, state='readonly', width=57)
termino_combobox['values'] = ["veinticuatro horas", "cuarenta y ocho horas", "setenta y dos horas"]
termino_combobox.grid(row=19, column=1, sticky="ew")
termino_combobox.bind("<<ComboboxSelected>>", lambda e: update_template())

label_orden = tk.Label(left_scrollable_frame, text="Serie y Número de orden:")
label_orden.grid(row=20, column=0, sticky="w")
frame_orden = tk.Frame(left_scrollable_frame)
frame_orden.grid(row=20, column=1, sticky="ew")
entry_serie_orden = tk.Entry(frame_orden, width=5)
entry_serie_orden.pack(side=tk.LEFT, padx=(0, 10))
entry_serie_orden.insert(0, "A")
entry_numero_orden_inicial = tk.Entry(frame_orden, width=10)
entry_numero_orden_inicial.pack(side=tk.LEFT, fill=tk.X, expand=True)
entry_serie_orden.bind("<KeyRelease>", lambda e: (update_template(), validar_campos()))
entry_numero_orden_inicial.bind("<KeyRelease>", lambda e: (update_template(), validar_campos()))

label_encabezado = tk.Label(left_scrollable_frame, text="Encabezado de oficios:")
label_encabezado.grid(row=21, column=0, sticky="w")

encabezado_var = tk.StringVar()
encabezado_combo = ttk.Combobox(left_scrollable_frame, textvariable=encabezado_var, state='readonly', width=57)
encabezado_combo['values'] = [
    "AL SEÑOR JEFE \nDE LA POLICÍA \nDE LA PROV. DE CÓRDOBA",
    "AL SEÑOR JEFE \nDE LA POLICÍA FEDERAL",
    "AL SEÑOR JEFE \nDE LA FUERZA POLICIAL \nANTINARCOTRÁFICO"
]
encabezado_combo.current(0)
encabezado_combo.grid(row=21, column=1, sticky="ew")
encabezado_combo.bind("<<ComboboxSelected>>", lambda e: update_template())

copiar_decreto_button.config(state=tk.DISABLED)  # Deshabilitado hasta que se completen los campos

update_template()

app.mainloop()
