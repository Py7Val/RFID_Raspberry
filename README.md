# RFID_Raspberry
Importante: Para que el código principal funcione hay que descargarse e instalar las librerías 'MFRC522-python' para el lector de tarjetas RFID, 'pyTelegramBotAPI' para poder interactuar con los bots de Telegram, y 'SPI-Py' para la comunicación SPI.

Se tratan de dos proyectos por separado, aunque el código es esencialmente el mismo y solo hay pequeñas variaciones:
- Proyecto: Se simula un acceso a una vivienda. Si el lector RFID identificada el identificador del tag se permitirá el acceso y se notificará la temperatura de la casa dependiendo del valor de esta gracias a la Sense Hat, al móvil. Si el tag no es reconocido por el lector, la picamera hace una foto y la envía por correo y por Telegram mediante un bot para avisarnos del intento de acceso fallido.

- Domótica: Se simula un acceso a una vivienda. Si el lector RFID identificada el identificador del tag se permitirá el acceso y se notificará la temperatura de la casa dependiendo del valor de esta gracias a la Sense Hat, al móvil. Si el tag no es reconocido por el lector, la picamera hace una grabación y la envía por correo para avisarnos del intento de acceso fallido.
