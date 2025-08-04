import csv
import os

def update_csv_with_language():
    """Update existing CSV file to include language column"""
    
    # Read existing data
    existing_data = []
    if os.path.exists('triage_log.csv'):
        with open('triage_log.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Add 'English' as default language for existing entries
                row['language'] = 'English'
                existing_data.append(row)
    
    # Write with new header
    new_header = ['timestamp', 'name', 'age', 'language', 'symptoms', 'recommendation', 'severity']
    with open('triage_log.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_header)
        writer.writeheader()
        for row in existing_data:
            # Ensure all fields are present
            updated_row = {
                'timestamp': row.get('timestamp', ''),
                'name': row.get('name', ''),
                'age': row.get('age', ''),
                'language': row.get('language', 'English'),
                'symptoms': row.get('symptoms', ''),
                'recommendation': row.get('recommendation', ''),
                'severity': row.get('severity', '')
            }
            writer.writerow(updated_row)
    
    print(f'✅ CSV file updated with language column. {len(existing_data)} records migrated.')

if __name__ == '__main__':
    update_csv_with_language()
