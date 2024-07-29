from apps.app import create_app as application

application = application('local')

if __name__ == '__main__':
    application.run()