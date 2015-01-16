import smtplib


class responseEmail(object):

        def __init__(self, toMail,mensaje,asunto):
                self.to = toMail
                self.mensaje =mensaje
                self.asunto = asunto
        def send(self):
                gmail_user = 'vigilancialac@gmail.com'

                # escribe tu password
                gmail_pwd = 'raspberry1122'

                #comandos para iniciar al servidor
                smtpserver = smtplib.SMTP("smtp.gmail.com",587)
                smtpserver.ehlo()
                smtpserver.starttls()
                smtpserver.ehlo

                # nos logueamos con el servidor
                smtpserver.login(gmail_user, gmail_pwd)

                #escribimos la cabecera
                header = 'To:' + self.to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject :'+ self.asunto+'\n'


                # escribimos el cuerpo del mensaje
                msg = header + '\n'+ self.mensaje+'\n\n'

                # enviamos el mail
                smtpserver.sendmail(gmail_user, self.to, msg)

                #cerramos el servidor
                smtpserver.close()

