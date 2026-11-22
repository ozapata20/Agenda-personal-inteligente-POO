import re
from datetime import datetime

def validar_rut(rut):
    patron_rut = r'^\d{1,3}(\.?\d{3})*-[0-9kK]$'
    if re.match(patron_rut, rut):
        rut_limpio = rut.replace('.', '').replace('-', '')
        digito_verificador = rut_limpio[-1]
        numero_rut = rut_limpio[:-1]
        rut_inverso = numero_rut[::-1]
        
        multiplicador = 2
        multiplicaciones = []
        
        for num in rut_inverso:
            mult = multiplicador * int(num)
            multiplicador += 1
            if multiplicador > 7:
                multiplicador = 2
            multiplicaciones.append(mult)
        
        total = sum(multiplicaciones)
        resto = total % 11
        digito_calculado = 11 - resto
        
        if digito_calculado == 11:
            digito_calculado = "0"
        elif digito_calculado == 10:
            digito_calculado = "K"
        else:
            digito_calculado = str(digito_calculado)
        
        return str(digito_verificador) == digito_calculado
    else:
        return False

def validar_correo(correo):
    patron_correo = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(patron_correo, correo):
        mensaje = 'Correo Válido.'
        return correo, mensaje
    else:
        mensaje = 'Correo NO válido, ingrese nuevamente...'
        correo = ''
        return correo, mensaje
    
def validar_fecha_nacimiento(fecha_nacimiento):
    patron_fecha = r'^\b(0[1-9]|[12]\d|3[01])/(0[1-9]|1[0-2])/(19\d\d|20\d\d)\b$'

    if not re.match(patron_fecha, fecha_nacimiento):
        mensaje = 'Formato de fecha NO corresponde, ingrese nuevamente...'
        fecha_nacimiento = ''
        return fecha_nacimiento, mensaje
    else:
        try:
            mensaje = 'Formato de fecha correcto.'
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%d/%m/%Y")
            return fecha_nacimiento, mensaje
        except ValueError:
            mensaje = 'Fecha INVÁLIDA, ingrese nuevamente...'
            fecha_nacimiento = ''
            return fecha_nacimiento, mensaje

def validar_genero(genero):
    if genero not in ['1','2','3']:
        mensaje = 'Género Inválido,\ningrese nuevamente...'
        genero = ''
        return genero, mensaje
    else:
        mensaje = 'Género Válido.'
        return genero, mensaje
    
def validar_contrasenia(contrasenia):
    error = []
    if len(contrasenia) < 8:
        mensaje = 'La contraseña debe tener al menos 8 caracteres.'
        error.append(mensaje)
    
    if not any(caracter.isdigit() for caracter in contrasenia):
        mensaje = 'La contraseña debe tener al menos 1 número.'
        error.append(mensaje)
    
    if not any(caracter.islower() for caracter in contrasenia):
        mensaje = 'La contraseña debe tener al menos 1 minúscula.'
        error.append(mensaje)
    
    if not any(caracter.isupper() for caracter in contrasenia):
        mensaje = 'La contraseña debe tener al menos 1 mayúscula.'
        error.append(mensaje)
    
    if not any(caracter in ['@','$','#','!','*','&'] for caracter in contrasenia):
        mensaje = 'La contraseña debe tener al menos 1 caracter especial; @, $, #, !, *, &.'
        error.append(mensaje)
    
    if len(error) > 0:
        contrasenia = ''
    return contrasenia, error