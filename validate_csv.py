import pandas as pd
import sys
from pydantic import BaseModel, ValidationError, field_validator, Field, StringConstraints, conint
from typing import Optional
from ipaddress import IPv4Network, AddressValueError

class SourceOfTruthModel(BaseModel):
    """
    Source of Truth Model
    """
    store_id: str = Field(min_length=1, max_length=20)
    zone_name: str = Field(min_length=1, max_length=50)
    machine_project_id: str = Field(min_length=1, max_length=50)
    fleet_project_id: str = Field(min_length=1, max_length=50)
    cluster_name: str = Field(min_length=1, max_length=50)
    location: str = Field(min_length=1, max_length=50)
    node_count: conint(ge=0)
    cluster_ipv4_cidr: str
    services_ipv4_cidr: str
    external_load_balancer_ipv4_address_pools: str
    sync_repo: str = Field(min_length=1, max_length=200)
    sync_branch: str = Field(min_length=1, max_length=50)
    sync_dir: str = Field(min_length=1, max_length=100)
    secrets_project_id: str = Field(min_length=1, max_length=50)
    git_token_secrets_manager_name: str = Field(min_length=1, max_length=50)
    cluster_version: str = Field(min_length=1, max_length=20)
    maintenance_window_start: Optional[str] = Field(default=None)
    maintenance_window_end: Optional[str] = Field(default=None)
    maintenance_window_recurrence: Optional[str] = Field(default=None, min_length=1, max_length=50)
    maintenance_exclusion_name_1: Optional[str] = Field(default=None, min_length=1, max_length=50)
    maintenance_exclusion_start_1: Optional[str] = Field(default=None)
    maintenance_exclusion_end_1: Optional[str] = Field(default=None)
    subnet_vlans: str = Field(min_length=1)
    recreate_on_delete: bool

    @field_validator("cluster_ipv4_cidr", "services_ipv4_cidr")
    @classmethod
    def validate_ipv4_cidr(cls, value):
        try:
            IPv4Network(value, strict=False)
        except (AddressValueError, ValueError) as e:
            raise ValueError(f"Invalid IPv4 CIDR: {value}") from e
        return value

    @field_validator("external_load_balancer_ipv4_address_pools")
    @classmethod
    def validate_ipv4_address_pools(cls, value):
        ranges = value.split(",")
        for r in ranges:
            ips = r.split("-")
            if len(ips) != 2:
                raise ValueError(f"Invalid IP address pool format: {value}")
            try:
                ip_start = ips[0]
                ip_end = ips[1]
                IPv4Network(ip_start)
                IPv4Network(ip_end)
            except (AddressValueError, ValueError) as e:
                raise ValueError(f"Invalid IP address in pool: {value}") from e
        return value

    @field_validator("sync_repo")
    @classmethod
    def validate_url(cls, value):
        if not value.startswith("https://"):  # Basic URL validation
            raise ValueError(f"Invalid URL format: {value}")
        return value

    @field_validator('maintenance_window_start', 'maintenance_window_end')
    @classmethod
    def validate_maintenance_window_time(cls, value):
        if value is None:
            return None
        try:
            pd.to_datetime(value, format="%H:%M")
        except ValueError:
            raise ValueError(f"Invalid time format. Expected HH:MM: {value}")
        return value

    @field_validator('maintenance_exclusion_start_1', 'maintenance_exclusion_end_1')
    @classmethod
    def validate_maintenance_exclusion_date(cls, value):
        if value is None:
            return None
        try:
            pd.to_datetime(value, format="%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Invalid date format. Expected %Y-%m-%d: {value}")
        return value

    @field_validator("location")
    @classmethod
    def validate_location(cls, value):
        allowed_locations = ["us-central1", "us-west1", "europe-west1"]
        if value not in allowed_locations:
            raise ValueError(f"Invalid location: {value}. Allowed values are {allowed_locations}")
        return value

def validate_data(df):
    errors = []
    for index, row in df.iterrows():
        try:
            # Convert row to a dictionary, handling NaNs
            row_dict = {k: None if pd.isna(v) else v for k, v in row.to_dict().items()}
            SourceOfTruthModel(**row_dict)  # Validate the row
        except ValidationError as e:
            # Capture the error and the row index.
            errors.append(f"Error in row {index + 2}: {e}")
        except ValueError as e:
            errors.append(f"Error in row {index + 2}: {e}")
    return errors

# Load the CSV file
csv_file = "cluster-intent-registry.csv"
try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    print(f"Error: CSV file not found at {csv_file}")
    sys.exit(1)
except pd.errors.EmptyDataError:
    print(f"Error: CSV file is empty")
    sys.exit(1)
except Exception as e:
    print(f"Error reading CSV file: {e}")
    sys.exit(1)

# Validate the header
expected_columns = [
    "store_id","zone_name","machine_project_id","fleet_project_id","cluster_name","location","node_count",
    "cluster_ipv4_cidr","services_ipv4_cidr","external_load_balancer_ipv4_address_pools",
    "sync_repo","sync_branch","sync_dir","secrets_project_id","git_token_secrets_manager_name",
    "cluster_version","maintenance_window_start","maintenance_window_end","maintenance_window_recurrence",
    "maintenance_exclusion_name_1","maintenance_exclusion_start_1","maintenance_exclusion_end_1","subnet_vlans","recreate_on_delete"
]

if list(df.columns) != expected_columns:
    print(
        "Error: CSV header does not match expected format.  Expected:"
        f" {expected_columns} Got: {list(df.columns)}"
    )
    sys.exit(1)

# Validate the data
errors = validate_data(df)

if errors:
    print("CSV validation failed:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)  # Fail the workflow
else:
    print("CSV validation successful!")
