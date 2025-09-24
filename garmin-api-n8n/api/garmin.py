from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs
from garminconnect import Garmin
from datetime import datetime, date

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse l'URL et les paramètres
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Récupère la date (par défaut aujourd'hui)
        date_param = query_params.get('date', [date.today().isoformat()])[0]
        
        try:
            # Connexion à Garmin
            api = Garmin(
                os.environ.get('GARMIN_EMAIL'),
                os.environ.get('GARMIN_PASSWORD')
            )
            api.login()
            
            # Endpoint pour les données de sommeil
            if '/sleep' in self.path:
                sleep_data = api.get_sleep_data(date_param)
                response_data = {
                    "date": date_param,
                    "sleep_data": sleep_data
                }
            
            # Endpoint pour les pas
            elif '/steps' in self.path:
                steps_data = api.get_steps_data(date_param)
                response_data = {
                    "date": date_param,
                    "steps_data": steps_data
                }
            
            # Endpoint pour le rythme cardiaque
            elif '/heartrate' in self.path:
                hr_data = api.get_heart_rate_data(date_param)
                response_data = {
                    "date": date_param,
                    "heart_rate_data": hr_data
                }
            
            # Endpoint pour toutes les données du jour (par défaut)
            else:
                activity_data = api.get_user_summary(date_param)
                response_data = {
                    "date": date_param,
                    "activity_summary": activity_data
                }
            
            # Réponse JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(response_data, default=str).encode('utf-8'))
            
        except Exception as e:
            # Gestion d'erreur
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))