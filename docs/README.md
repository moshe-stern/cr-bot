# Central Reach Updater

Welcome to the documentation for the **Central Reach Updater**. This tool is designed to streamline and automate key operations in Central Reach, making tasks such as updating timesheets, managing codes, and adjusting schedules more efficient.

## Features

**Note:** Some columns support `;;` separated values in one cell.

The Central Reach Updater offers the following key functionalities:

### 1. Schedules
The **Schedules** module focuses on maintaining accurate and up-to-date schedules for clients and providers:
- Modify authorizations associated with schedules to reflect changes in service plans or client needs.

##### Columns for Schedules:
- `client_id`
- `auths` (Supports `;;` separated values)

---

### 2. Auth-Setting

#### Payor Changes
The **Auth-Setting (Payor Changes)** module allows you to:
- Update payor information to align with current billing requirements.

##### Columns for Payor Changes:
- `resource_id`
- `global_payor`

#### Service Code Changes
The **Auth-Setting (Service Code Changes)** module allows you to:
- Add or remove service codes as needed for accurate authorization mapping.

##### Columns for Service Code Changes:
- `resource_id`
- `to_add` (Supports `;;` separated values)
- `to_remove` (Supports `;;` separated values)

---

### 3. Billing

#### Timesheet Authorization Changes
The **Billing (Timesheet Authorization Changes)** module allows you to:
- Update authorization details directly on billing records to reflect changes in service authorizations.

##### Columns for Timesheet Authorization Changes:
- `client_id`
- `start_date`
- `end_date`
- `authorization_id`

#### Payor Changes
The **Billing (Payor Changes)** module allows you to:
- Modify payor information to ensure accurate billing alignment.

##### Columns for Payor Changes:
- `client_id`
- `start_date`
- `end_date`
- `insurance_id`

---



## Getting Started

### Prerequisites
To use the Central Reach Updater, you need to:
1. Fill out the required [form](https://forms.office.com/Pages/ResponsePage.aspx?id=yUIn2NRNYkGj73cnwNnViJGfELrUJ3xDijChDtOubttUREtWS0VFUUlNRjkwQjBMRTQ4Wk9DOVZYTy4u) to access the updater.
2. Ensure the Excel file you upload has the exact format in column names corresponding to the update type (Schedules, Auth-Setting, or Billing).

---

## Support
If you encounter any issues or have questions about the Central Reach Updater, please contact the development team at **[moshe.stern@attainaba.com](mailto:moshe.stern@attainaba.com)**.

