# bloodpressure-monitor-bot
A simple Telegram bot that helps you registers your Blood Pressure measures into a Google Spreedsheet


----

If you want to use your own Bot with your own Google Credentials your need to follow the next steps.

# Google API

1. Create a Project: [Google Resource Manager](https://console.developers.google.com/cloud-resource-manager)
    - Click on **+ Create a New Project** button
    - Complete with a `Project Name`
    - *Optional* This will set up automatically a `Project ID`, you can change it if you want
    - Finish this step clicking on **Create** button
2. Create a Service Account: [Service Account Panel](https://console.developers.google.com/iam-admin/serviceaccounts)
    - Make sure your are selecting Service Accounts for the new project: `Service accounts for project "Your Project Name"`.
    - Click on **+ Create Service Account** button
    - Complete with `Service Account Name`
    - Complete with a `Service Account ID`
    - *Optional* Complete with a Service Account Description
    - Finish this step clicking on **Create** button
    - Select `Project -> Editor` for Role.
    - Finish this step clicking on **Continue** button
3. Create a Key: [API & Services Credentials](https://console.developers.google.com/apis/credentials)
    - Select **Create credentials** with *Service Account key* option.
    - Choose `JSON` key type.
    - Finish this step clicking on **Create** button
    - Save the `JSON` file into your working directory inside `credentials/`
4. Enable Google's Spreadsheet API
    - Go to **Dashboard** option in [API & Services Credentials](https://console.developers.google.com/apis/credentials)
    - Click on **+ Enable APIs and Services** button
    - Find `Google Sheet API` & click on **Enable** button
5. Share the Spreadsheet with the **email** located on the `JSON` file downloaded on step 4.
    - Open your credentials `JSON` file
    - Locate `client_email` key and copy its value
    - Open your Google Spreadsheet and click on **Share** button
    - Paste `client_email` value and click **OK**.
6. Update source code with your Spreadsheet ID:
 - Located on URL: `https://docs.google.com/spreadsheets/d/your_spreadsheet_id/edit#gid=0`
 - Update `SERVICE_ACCOUNT_FILE` with your credentials filename
