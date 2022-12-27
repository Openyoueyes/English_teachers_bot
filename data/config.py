from environs import Env
env = Env()
env.read_env()

API_TOKEN = env.str("API_TOKEN")
DB_HOST = env.str("POSTGRES_HOST")
ADMINS = env.list("ADMIN_ID")

APP_NAME = env.str("APP_NAME")

if APP_NAME:
    # webhook settings
    WEBHOOK_HOST = 'https://your_domain'
    WEBHOOK_PATH = f'/bot'
    WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
    # webserver settings
    WEBAPP_HOST = '0.0.0.0'
    WEBAPP_PORT = 3001
else:
    WEBAPP_HOST = ""
    
