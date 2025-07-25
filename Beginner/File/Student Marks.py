import csv

input_file = 'student_marks.csv'
full_output_file = 'student_marks_with_totals.csv'
summary_output_file = 'student_totals_summary.csv'

students_data = []
summary_data = []

with open(input_file, mode='r') as file:
    reader = csv.DictReader(file)
    for raw_row in reader:
        # Convert all keys to lowercase (normalize)
        row = {k.strip().lower(): v.strip() for k, v in raw_row.items()}
        
        # Filter out non-mark fields
        marks_keys = [key for key in row.keys() if key not in ['name', 'gender', 'roll']]
        
        try:
            marks = [float(row[key]) for key in marks_keys]
        except ValueError:
            print(f"⚠️ Skipping row due to non-numeric value: {row}")
            continue

        total = sum(marks)
        average = round(total / len(marks), 2)

        row['total_marks'] = total
        row['average'] = average

        students_data.append(row)

        summary_data.append({
            'name': row.get('name', 'Unknown'),
            'total_marks': total,
            'average': average
        })

# Write full data
with open(full_output_file, mode='w', newline='') as file:
    fieldnames = students_data[0].keys()
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(students_data)

# Write summary data
with open(summary_output_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['name', 'total_marks', 'average'])
    writer.writeheader()
    writer.writerows(summary_data)

print("✅ Finished writing:")
print(f"- Full: {full_output_file}")
print(f"- Summary: {summary_output_file}")
