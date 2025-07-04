import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import argparse
import os
import dateutil.parser
from matplotlib.backends.backend_pdf import PdfPages

# Configuration Prometheus
PROMETHEUS_URL = "http://localhost:9091"
QUERIES = {
    "Requests per second": 'sum by(path)(rate(flask_http_request_duration_seconds_count{instance=~"store_manager.*"}[1m]))',
    "Memory (MB)": 'sum by(instance)(process_resident_memory_bytes / 1024 / 1024)',
    "CPU (%)": 'sum by(instance)(rate(process_cpu_seconds_total[15m]) * 100)',
    "Average Latency (s)": 'sum by(instance) (rate(flask_http_request_duration_seconds_sum[15m])) / sum by(instance) (rate(flask_http_request_duration_seconds_count[15m]))',
    "Error Rate (%)": 'sum by(instance) (rate(flask_http_request_duration_seconds_count{status=~"4..|5.."}[15m])) / sum by(instance) (rate(flask_http_request_duration_seconds_count[15m])) * 100'
}

def parse_time(time_str):
    """Parse les dates en format ISO ou timestamp"""
    try:
        return datetime.fromtimestamp(float(time_str))
    except ValueError:
        return dateutil.parser.parse(time_str)

def fetch_prometheus_data(query, start_time, end_time, step):
    try:
        # Formatage correct pour l'API v2 (ISO 8601 avec timezone)
        params = {
            "query": query,
            "start": start_time.astimezone().isoformat(),  # Format ISO 8601
            "end": end_time.astimezone().isoformat(),
            "step": step,
        }

        # Debug: Afficher l'URL appelée
        print(f"🔍 Requête envoyée à Prometheus v1: {params}")

        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query_range",
            params=params,
            timeout=10
        )

        # Debug: Afficher le code de statut
        print(f"📡 Code de réponse: {response.status_code}")

        response.raise_for_status()
        data = response.json()

        # Debug: Afficher un extrait de la réponse
        print(f"📦 Réponse reçue (extrait): {str(data)[:200]}...")

        # Conversion du format v2 vers le format v1 attendu par le reste du code
        converted_data = {
            "status": "success",
            "data": {
                "resultType": "matrix",
                "result": []
            }
        }

        for series in data.get("data", {}).get("result", []):
            try:
                values = [
                    [float(ts), str(value)] 
                    for ts, value in series.get("values", [])
                ]
                converted_data["data"]["result"].append({
                    "metric": series.get("metric", {}),
                    "values": values
                })
            except (ValueError, TypeError) as e:
                print(f"⚠️ Erreur de conversion des données pour la série: {e}")
                continue

        return converted_data

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de requête HTTP: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"Contenu de l'erreur: {e.response.text[:200]}...")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Réponse JSON invalide: {str(e)}")
        print(f"Contenu reçu: {response.text[:200]}...")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
        return None

def plot_to_pdf(queries_data, output_dir, filename, figsize):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{filename}.pdf")
    
    with PdfPages(output_path) as pdf:
        for title in [
            "Requests per second",
            "Memory (MB)",
            "CPU (%)",
            "Average Latency (s)",
            "Error Rate (%)"
        ]:
            fig, ax = plt.subplots(figsize=(figsize[0], figsize[1]/2))
            
            data = queries_data[title]
            
            # Cas spécial pour Error Rate (%) quand pas de données
            if title == "Error Rate (%)" and not data["data"]["result"]:
                x = [datetime.fromtimestamp(float(val[0])) for val in series["values"]]
                y = [0] * len(x)  # Ligne à 0%
                ax.plot(x, y, color='green', label='0% error rate')
                ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2),
                         fancybox=True, shadow=True)
            else:
                for series in data["data"]["result"]:
                    x = [datetime.fromtimestamp(float(val[0])) for val in series["values"]]
                    y = [float(val[1]) for val in series["values"]]
                    label = series["metric"].get("path", series["metric"].get("instance", "N/A"))
                    ax.plot(x, y, label=label)
            
            ax.set_title(title, fontsize=14, pad=20)
            ax.grid(True)
            
            if title == "Error Rate (%)":
                ax.set_ylim(0, 100)
            
            # Gestion de la légende
            n_series = len(data["data"]["result"])
            if n_series > 0:
                ax.legend(
                    loc='upper center',
                    bbox_to_anchor=(0.5, -0.2),
                    fancybox=True,
                    shadow=True,
                    ncol=min(3, n_series)
                )
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
    
    print(f"PDF généré : {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Génère des rapports PDF de métriques Prometheus",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Arguments obligatoires
    parser.add_argument("--repo", type=str, required=True, 
                       help="Sous-répertoire dans documentation/monitoring")
    parser.add_argument("--filename", type=str, required=True,
                       help="Nom du fichier PDF (sans extension)")
    
    # Contrôle temporel (mutuellement exclusifs)
    time_group = parser.add_mutually_exclusive_group()
    time_group.add_argument("--duration", type=int,
                          help="Durée en minutes avant maintenant")
    time_group.add_argument("--start", type=str,
                          help="Date/heure de début (ISO/timestamp)")
    parser.add_argument("--end", type=str,
                      help="Date/heure de fin (ISO/timestamp), par défaut maintenant")
    
    # Dimensions du PDF
    parser.add_argument("--width", type=float, default=14.0,
                      help="Largeur du PDF en pouces")
    parser.add_argument("--height", type=float, default=16.0,
                      help="Hauteur du PDF en pouces")
    
    args = parser.parse_args()

    # Gestion des dates
    end_time = datetime.now() if not args.end else parse_time(args.end)
    
    if args.start:
        start_time = parse_time(args.start)
    elif args.duration:
        start_time = end_time - timedelta(minutes=args.duration)
    else:
        start_time = end_time - timedelta(minutes=15)  # Default fallback

    # Validation des dates
    if start_time >= end_time:
        raise ValueError("La date de début doit être antérieure à la date de fin")

    # Construction du chemin de sortie
    output_dir = os.path.join("documentation", "monitoring", args.repo)
    
    # Récupération des données
    queries_data = {}
    for title, query in QUERIES.items():
        queries_data[title] = fetch_prometheus_data(query, start_time, end_time, step="15s")
    
    # Génération du PDF
    plot_to_pdf(
        queries_data=queries_data,
        output_dir=output_dir,
        filename=args.filename,
        figsize=(args.width, args.height)
    )