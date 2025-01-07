import os
import re
from datetime import datetime

def process_md_file(file_path):
    """Process a single markdown file to update the front matter."""
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Check if the file contains front matter
    if not lines or lines[0].strip() != "---":
        print(f"Skipping {file_path}: No front matter found.")
        return

    # Extract front matter and content
    front_matter = []
    content = []
    in_front_matter = False
    in_content = False

    for line in lines:
        if line.strip() == "---" and not in_front_matter:
            in_front_matter = True
            continue
        elif line.strip() == "---" and in_front_matter:
            in_front_matter = False
            in_content = True
            continue

        if in_front_matter:
            front_matter.append(line.strip())
        elif in_content:
            content.append(line)

    # Parse front matter to extract required fields
    title = None
    categories = []
    tags = []
    date = None

    for entry in front_matter:
        if entry.startswith("title:"):
            match = re.search(r'title:\s*(.+)', entry)
            if match:
                title = match.group(1).strip()
                title = title.strip('"')  # Ensure no extra quotes
        elif entry.startswith("categories:"):
            match = re.findall(r'\[([^\]]+)\]', entry)
            if match:
                categories = [f'"{cat.strip()}"' for cat in match[0].split(",")]
        elif entry.startswith("tags:"):
            match = re.search(r'tags:\s*(.+)', entry)
            if match:
                tags = match.group(1).strip().strip("[]").split(", ")
                tags = [f'"{tag.strip()}"' for tag in tags]
        elif entry.startswith("date:"):
            match = re.search(r'date:\s*(.+)', entry)
            if match:
                date = match.group(1).strip()
                # Convert date to Zola's format (YYYY-MM-DD)
                try:
                    date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                except ValueError:
                    pass  # Keep original date if parsing fails

    # Skip processing if required fields are missing
    if not title or not date:
        print(f"Skipping {file_path}: Required fields missing.")
        return

    # Construct new front matter
    new_front_matter = ["+++"]
    if title:
        new_front_matter.append(f'title = "{title}"')
    if categories:
        new_front_matter.append(f'categories = [{", ".join(categories)}]')
    if tags:
        new_front_matter.append(f'tags = [{", ".join(tags)}]')
    if date:
        new_front_matter.append(f'date = {date}')
    new_front_matter.append("+++\n")

    # Write updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('\n'.join(new_front_matter))  # Write the updated front matter
        file.writelines(content)  # Write the original content

    print(f"Processed {file_path}")

def process_all_md_files():
    """Process all markdown files in the current directory."""
    for file_name in os.listdir('.'):
        if file_name.endswith('.md'):
            process_md_file(file_name)

if __name__ == "__main__":
    process_all_md_files()