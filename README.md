Source of Truth (SoT) CSV Validation Workflow

This workflow validates the `cluster-intent-registry.csv` file, which serves as the Source of Truth (SoT) for cluster definitions.  It ensures that the data in the CSV file adheres to a predefined schema, maintaining data integrity and preventing errors in subsequent processes.

## Purpose

The primary goal of this workflow is to:

* **Validate Data Integrity**: Ensure that the `cluster-intent-registry.csv` file conforms to the expected format and data types.
* **Prevent Errors**: Catch data inconsistencies early in the development process, preventing issues in later stages such as cluster provisioning or configuration.
* **Automate Validation**: Automate the validation process, eliminating the need for manual checks and ensuring consistent validation across all changes.

## How it Works

The workflow operates as follows:

1.  **Trigger**: The workflow is triggered on every pull request to the `main` branch.
2.  **Checkout Code**: The workflow checks out the code from the repository.
3.  **Set up Python**: A Python environment is set up using the `python:3.9-slim-buster` Docker image.
4.  **Install Dependencies**: The required Python libraries, `pandas` and `pydantic`, are installed.
5.  **Copy Validation Script**: The `validate_csv.py` script is copied to the `.github/scripts` directory.
6.  **Validate CSV Contents**: The `validate_csv.py` script is executed to validate the `cluster-intent-registry.csv` file.
    * The script reads the CSV file using `pandas`.
    * It then validates each row of the CSV file against a Pydantic model (`SourceOfTruthModel`).
    * Any validation errors are reported, and the workflow fails if any errors are found.
7.  **Report Results**: The workflow reports the validation status (success or failure).

## Pydantic Model

The `validate_csv.py` script uses a Pydantic model (`SourceOfTruthModel`) to define the schema for the CSV file.  The model specifies the expected columns, data types, and constraints for each field.  This ensures that the data in the CSV file is consistent and adheres to the required format.

## Local Testing

To test the validation script locally, you can run the following command:

```bash
python validate_csv.py

Ensure that you have the required dependencies (pandas and pydantic) installed in your Python environment.  You should also have a cluster-intent-registry.csv file in the same directory as the script, or update the csv_file variable in the script.Workflow File (.github/workflows/validate_sot.yml)
The workflow definition is located in the .github/workflows/validate_sot.yml file.
This file defines the workflow's trigger, the jobs to be executed, and the steps within each job.

**Contributing**
Contributions to this workflow are welcome.
If you have any suggestions or find any issues, please feel free to open a pull request or submit an issue.
