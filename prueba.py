from sendEmail import responseEmail
mensaje = "Mensaje erroneo. Solo texto, sin imagenes ni archivos adjutos"
asunto = "Mensaje incorrecto. Verifique"
mailfrom = "mardom4164@gmail.com"
responseEmail(mailfrom,mensaje, asunto).send() # Respondo el email con msj erroneo