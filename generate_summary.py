import os
import json
import pandas as pd
from datetime import datetime
from google.cloud import storage

def read_settings(settings_file):
    with open(settings_file, 'r') as f:
        return json.load(f)

def parse_log(log_file):
    with open(log_file, 'r') as f:
        log_content = f.read()
    
    # Extract key information
    start_time = None
    end_time = None
    trajectories = []
    accepted_designs = []
    
    for line in log_content.split('\n'):
        if "Starting trajectory:" in line:
            trajectories.append(line.split("Starting trajectory: ")[1].strip())
        elif "passed all filters" in line:
            accepted_designs.append(line.split(" passed all filters")[0].strip())
        elif "Script execution for" in line and "trajectories took:" in line:
            end_time = line.strip()
    
    return {
        'trajectories': trajectories,
        'accepted_designs': accepted_designs,
        'end_time': end_time
    }

def generate_html(settings, log_data, design_path):
    # Read CSV files
    trajectory_df = pd.read_csv(os.path.join(design_path, 'trajectory_stats.csv'))
    final_df = pd.read_csv(os.path.join(design_path, 'final_design_stats.csv'))
    
    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>BindCraft Results: {settings['binder_name']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .summary {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
            .results {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
            .design-card {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
            .stats {{ margin-top: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f5f5f5; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>BindCraft Results: {settings['binder_name']}</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Target:</strong> {settings['binder_name']}</p>
                <p><strong>Hotspot Residues:</strong> {settings['target_hotspot_residues']}</p>
                <p><strong>Binder Length Range:</strong> {settings['lengths'][0]} - {settings['lengths'][1]} residues</p>
                <p><strong>Number of Trajectories:</strong> {len(log_data['trajectories'])}</p>
                <p><strong>Accepted Designs:</strong> {len(log_data['accepted_designs'])}</p>
                <p><strong>Completion Time:</strong> {log_data['end_time']}</p>
            </div>

            <div class="stats">
                <h2>Trajectory Statistics</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Average</th>
                        <th>Best</th>
                    </tr>
                    <tr>
                        <td>pLDDT</td>
                        <td>{trajectory_df['pLDDT'].mean():.2f}</td>
                        <td>{trajectory_df['pLDDT'].max():.2f}</td>
                    </tr>
                    <tr>
                        <td>pTM</td>
                        <td>{trajectory_df['pTM'].mean():.2f}</td>
                        <td>{trajectory_df['pTM'].max():.2f}</td>
                    </tr>
                    <tr>
                        <td>Interface pLDDT</td>
                        <td>{trajectory_df['i_pLDDT'].mean():.2f}</td>
                        <td>{trajectory_df['i_pLDDT'].max():.2f}</td>
                    </tr>
                </table>
            </div>

            <div class="results">
                <h2>Accepted Designs</h2>
                {generate_design_cards(final_df, design_path)}
            </div>
        </div>
    </body>
    </html>
    """
    return html

def generate_design_cards(df, design_path):
    cards = []
    for _, row in df.iterrows():
        design_name = row['Design_Name']
        card = f"""
        <div class="design-card">
            <h3>{design_name}</h3>
            <p><strong>pLDDT:</strong> {row['pLDDT']:.2f}</p>
            <p><strong>pTM:</strong> {row['pTM']:.2f}</p>
            <p><strong>Interface pLDDT:</strong> {row['i_pLDDT']:.2f}</p>
            <p><a href="https://storage.googleapis.com/atelasbio/results/{design_path}/Accepted/{design_name}.pdb">Download PDB</a></p>
            <p><a href="https://storage.googleapis.com/atelasbio/results/{design_path}/Accepted/Animation/{design_name}.html">View Animation</a></p>
        </div>
        """
        cards.append(card)
    return '\n'.join(cards)

def upload_to_gcs(html_content, design_path):
    # Initialize GCS client
    storage_client = storage.Client()
    bucket = storage_client.bucket('atelasbio')
    
    # Upload HTML file
    blob = bucket.blob(f'results/{design_path}/summary.html')
    blob.upload_from_string(html_content, content_type='text/html')
    
    print(f"Summary page uploaded to gs://atelasbio/results/{design_path}/summary.html")

def main():
    # Read settings
    settings = read_settings('settings_target/cas12a_small.json')
    design_path = settings['design_path'].strip('./')
    
    # Parse log
    log_data = parse_log('bindcraft.log')
    
    # Generate HTML
    html_content = generate_html(settings, log_data, design_path)
    
    # Upload to GCS
    upload_to_gcs(html_content, design_path)

if __name__ == "__main__":
    main() 