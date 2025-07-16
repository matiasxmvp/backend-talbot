# application.py - Punto de entrada para Elastic Beanstalk
# Elastic Beanstalk busca específicamente este archivo y la variable 'application'

from main import app

# Elastic Beanstalk espera una variable llamada 'application'
# que contenga la instancia de la aplicación WSGI/ASGI
application = app

# Información adicional para debugging en Elastic Beanstalk
if __name__ == "__main__":
    print(f"Application type: {type(application)}")
    print(f"Application title: {getattr(application, 'title', 'N/A')}")