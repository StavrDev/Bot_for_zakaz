from utils import TgBot


app = TgBot(kassa_name ,
            api_key, 
            salt, 
            TOKEN_BOT,  
            admin_id)

if __name__ == "__main__":
    app.start()
