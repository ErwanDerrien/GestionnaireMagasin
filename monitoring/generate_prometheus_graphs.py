import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import argparse
import os
import dateutil.parser

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
    response = requests.get(
        f"{PROMETHEUS_URL}/api/v1/query_range",
        params={
            "query": query,
            "start": start_time.timestamp(),
            "end": end_time.timestamp(),
            "step": step,
        },
    )
    return response.json()

def plot_to_pdf(queries_data, output_dir, filename, figsize):
    plt.figure(figsize=figsize)
    
    ordered_titles = [
        "Requests per second",
        "Memory (MB)",
        "CPU (%)",
        "Average Latency (s)",
        "Error Rate (%)"
    ]
    
    for i, title in enumerate(ordered_titles, 1):
        plt.subplot(5, 1, i)
        data = queries_data[title]
        for series in data["data"]["result"]:
            x = [datetime.fromtimestamp(float(val[0])) for val in series["values"]]
            y = [float(val[1]) for val in series["values"]]
            plt.plot(x, y, label=series["metric"].get("path", series["metric"].get("instance", "N/A")))
        plt.title(title)
        plt.grid(True)
        
        if title == "Error Rate (%)":
            plt.ylim(0, 100)
        
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{filename}.pdf")
    plt.savefig(output_path, bbox_inches='tight')
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