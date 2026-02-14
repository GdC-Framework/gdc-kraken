# Installer les dépendances :
# pip install mysql-connector-python

# Utilisation : 
# python mysql_to_csv_export.py <database_name>

import mysql.connector
import csv
import sys

# --- CONFIGURATION ---
MYSQL_CONFIG = {
    'host': 'TBD',
    'user': 'TBD',
    'password': 'TBD',
    'database': 'TBD',
    'port': 0000,
    'use_pure': True
}
# Tables à exporter (adapter les noms si besoin)
TABLES = [
    'joueurs',
    'missions',
    'mission_joueur_role',
    'role',
]

# --- SCRIPT ---
def export_table_to_csv(cursor, table_name, output_dir='TBD'):
    cursor.execute(f"SELECT * FROM `{table_name}`")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    csv_path = f"{output_dir}\\{table_name}.csv"
    print("JJJ")
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        writer.writerows(rows)
    print(f"Exporté : {csv_path} ({len(rows)} lignes)")

def main():
    config = MYSQL_CONFIG.copy()
    if len(sys.argv) > 1:
        config['database'] = sys.argv[1]
    if not config['database']:
        print("Usage: python mysql_to_csv_export.py <database>")
        sys.exit(1)
    print("Try to connect...")
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    print("Connected !")
    for table in TABLES:
        try:
            export_table_to_csv(cursor, table)
        except Exception as e:
            print(f"Erreur pour la table {table} : {e}")
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
