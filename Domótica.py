#!/usr/bin/env python
# -*- coding: utf8 -*-

# Importamos librerías
import RPi.GPIO as GPIO
import os
import MFRC522
import signal
import shlex
import subprocess
import datetime as dt
import time
import smtplib
import telebot
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
from picamera import PiCamera
from sense_hat import SenseHat

# Definimos variables de leds de Sense Hat y direcciones email para alerta de seguridad
R = [255, 0, 0]  # Rojo
G = [0, 255, 0]  # Verde
direccion_fuente = "prlab201819@gmail.com"
direccion_destino = "viktor4194@gmail.com"
recording_time = 10

# Creamos objeto de Sense Hat, del RFID y definimos TOKEN e ID de conversación de Telegram
sense=SenseHat()
MIFAREReader = MFRC522.MFRC522()
chatid = '701895569'
TOKEN = '696629732:AAFYMI-OB67XU9r-9umdaFuaELg-WV6T1mM'
tb = telebot.TeleBot(TOKEN)

# Variable para hacer el bucle de lecturas de tarjetas RFID
lectura_continua = True

# Esto se ejecuta cuando se deja de leer tarjetas RFID con Control + C
def end_read(signal,frame):
    global lectura_continua
    print "Lectura finalizada"
    lectura_continua = False
    sense.clear()
    GPIO.cleanup()

# Para coger la señal
signal.signal(signal.SIGINT, end_read)

# Mensaje comienzo del proceso
print "Bienvenido"
print "Presiona Ctrl-C para parar el proceso\n"

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while lectura_continua:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # SI encontramos tarjeta, lo imprimimos por pantalla
    if status == MIFAREReader.MI_OK:
        print "Tarjeta detectada"
    
    # Obtener ID tarjeta
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # Si tenemos la ID, nos la imprime por pantalla
    if status == MIFAREReader.MI_OK:
        print "Lectura tarjeta User ID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3])
        time.sleep(1)

        # Si la tarjeta tiene el UID que buscamos se permite el acceso
        if uid[0] == 227 and uid[1] == 93 and uid[2] == 65 and uid[3] == 197:

            #Pantalla en verde
            question_mark = [
            G, G, G, G, G, G, G, G,
            G, G, G, G, G, G, G, G,
            G, G, G, G, G, G, G, G,
            G, G, G, G, G, G, G, G,
            G, G, G, G, G, G, G, G,
            G, G, G, G, G, G, G, G,
            G, G, G, G, G, G, G, G,
            G, G, G, G, G, G, G, G
            ]

            sense.set_pixels(question_mark)
            time.sleep(1)
            
            # Mensaje de bienvenida por pantalla y por Sense Hat
            print "¡¡Bienvenido a casa¡¡"
            sense.show_message('BIENVENIDO',text_colour=[100,100,100], scroll_speed = 0.05)

            # Medida de temperatura
            Temp1=sense.get_temperature_from_humidity()
            T1=float(round(Temp1,2))
            print("La temperatura es de: %.2f" % (Temp1))
            TStr=str(round(Temp1,2))
            sense.show_message("TEMPERATURA: "+TStr, scroll_speed = 0.05)

            # Envío de mensajes de temperatura al móvil
            print("Enviando mensaje al móvil...")
            if T1 < 20:
                tb.send_message(chatid, '¡¡Bienvenido a casa!! Hoy es '+ time.strftime ('%d %b y son las %H:%M. La temperatura ambiente es de '+TStr + ' ºC, por lo que creo que quizás deberías encender la calefacción.'))

            elif T1 > 32:
                tb.send_message(chatid, '¡¡Bienvenido a casa!! Hoy es '+ time.strftime ('%d %b y son las %H:%M. La temperatura ambiente es de '+TStr + ' ºC, por lo que creo que deberías encender el aire acondicionado.'))

            else:
                tb.send_message(chatid, '¡¡Bienvenido a casa!! Hoy es '+ time.strftime ('%d %b y son las %H:%M. La temperatura ambiente es de '+TStr + ' ºC, por lo que creo que la temperatura ambiente es ideal y no deberías encender ni la calefacción ni el aire acondicionado.'))
                
            print("Mensaje enviado\n")

        # Si no es la ID que queremos no deja acceder a la casa  
        else:
            # Si no tiene esa ID la Sense Hat entera en rojo
            question_mark = [
            R, R, R, R, R, R, R, R,
            R, R, R, R, R, R, R, R,
            R, R, R, R, R, R, R, R,
            R, R, R, R, R, R, R, R,
            R, R, R, R, R, R, R, R,
            R, R, R, R, R, R, R, R,
            R, R, R, R, R, R, R, R,
            R, R, R, R, R, R, R, R
            ]

            sense.set_pixels(question_mark)
            time.sleep(1)
            
            # Acceso denegado por pantalla y Sense Hat
            print "Error de autenticación"

            # Hacemos foto para ver quién está intentando acceder.
            # Creamos objeto de la PiCámara y la configuramos
            print "Realizando grabación de seguridad..."
            camera = PiCamera()
            camera.resolution = (640,480)
            camera.rotation = 180
            camera.start_preview(fullscreen=False, window=(200,200,640,480))
            print("Intrusión detectada, tomando imágenes...")
            for i in range(1,11):
                print(i)
            
            # Realizar grabación con Pi Camera con fecha y hora reales
            camera.start_recording('/home/pi/git/practicas_sdaa_copia/proyecto/intruso.h264')
            camera.annotate_text = dt.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
            start = dt.datetime.now()
            os.remove('/home/pi/git/practicas_sdaa_copia/proyecto/intruso.mp4')
            clipname = "intruso.h264"
            sendname = "intruso.mp4"
            
            while (dt.datetime.now() - start).seconds < recording_time:
                camera.annotate_text = dt.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
                camera.wait_recording(.2)
                      
            camera.stop_recording()
            camera.stop_preview()
            camera.close()
            print("Fin de grabación. Conviertiendo archivo...")
            
            # Conversión de formato de vídeo de .h264 a .mp4
            command = shlex.split("MP4Box -add intruso.h264 intruso.mp4". format(clipname))
            output = subprocess.check_output(command, stderr=subprocess.STDOUT)
            print("¡Conversión satisfactoria! Enviando archivo...")
            
            # Envio correo electrónico con aviso de seguridad y adjuntando la foto hecha
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(direccion_fuente, "xxxxXXXXX")
            msg = MIMEMultipart()
            msg['From'] = direccion_fuente
            msg['To'] = direccion_destino
            msg['Subject'] = "[Alerta de Seguridad] Intento de acceso a su casa"
            # Configuramos el cuerpo de mensaje y adjuntamos la imagen hecha
            cuerpo_mensaje = "Se ha recibido una alerta de que alguien sin permiso de autorización ha intentado acceder a su casa el " + time.strftime("%d %b %Y a las %H:%M:%S. Por favor, no responda a este mensaje, se trata de un mensaje automatizado y solo se ha enviado para informar de la alerta.")
            msg.attach(MIMEText(cuerpo_mensaje, 'plain'))
            archivo = "imagen.jpg"
            adjunto = open(archivo, "rb")
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((adjunto).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % archivo)
            msg.attach(part)
            texto = msg.as_string()
            try:
                print "Enviando alerta de seguridad al correo"
                print server.sendmail(direccion_fuente, direccion_destino, texto)
                server.quit()
            except:
                print "Error al enviar el correo"
                server.quit()
            print "\n"
