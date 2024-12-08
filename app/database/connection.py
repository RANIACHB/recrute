from snowflake import connector

def get_snowflake_connection():
    try:
        conn = connector.connect(
            user='RCWA202411',  # Votre utilisateur Snowflake
            password='Rcw1234=',  # Mot de passe
            account='pgwebmobile.ca-central-1.aws',  # Account correct
            warehouse='PROJETRCW',  # Warehouse Snowflake
            database='PROJETRCW_DB',  # Base de données
            schema='ProjetRCWSchema'  # Schéma
        )
        print("Connexion réussie à Snowflake !")
        return conn
    except Exception as e:
        print(f"Erreur lors de la connexion à Snowflake : {e}")
        raise e
