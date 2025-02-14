import os
from django.core.management import call_command

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.base")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

# Initialize Django
import configurations
configurations.setup()

# Generate the ERD
# Navigate up one level from the backend directory to the root
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_path = os.path.join(root_dir, 'erdImages', 'erd.png')
os.makedirs(os.path.dirname(output_path), exist_ok=True)

call_command(
    'graph_models',
    all_applications=True,
    group_models=True,
    output=output_path,
    exclude_models=[],  # Exclude specific models if needed
    exclude_apps=[],    # Exclude specific apps if needed
)

print(f"ERD generated and saved to {output_path}")
