# 💰 Personal Expense Tracker

A beginner-friendly personal finance web application built with **Python, SQLite, Streamlit, Pandas, and Plotly**. It helps users manage their income and expenses, monitor monthly budgets, visualize spending patterns, and export transaction records to CSV.

## 🚀 Features

* **Interactive Dashboard:** View total income, total expenses, and net balance.
* **Transaction Management:** Add, edit, and delete income and expense records.
* **Category-Based Tracking:** Organize transactions into categories such as Food, Transport, Shopping, Salary, and Bills.
* **Monthly Budget Management:** Set spending limits for expense categories and monitor budget usage.
* **Data Visualization:** Analyze spending with interactive pie charts and monthly income-versus-expense bar charts.
* **Date and Category Filters:** Filter transactions by date range, transaction type, and category.
* **CSV Export:** Download filtered transaction records for further analysis in Excel or other spreadsheet applications.
* **Persistent Storage:** Store transaction and budget records locally using SQLite.

## 🛠️ Technologies Used

* **Python** – Application logic and calculations
* **Streamlit** – Interactive web interface
* **SQLite** – Local database management
* **Pandas** – Data processing and analysis
* **Plotly** – Interactive charts and visualizations

## 📋 Prerequisites

Install the following before running the project:

* Python 3.12 or a compatible Python version
* Visual Studio Code
* Git (optional, for version control)

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/PersonalExpenseTracker.git
cd PersonalExpenseTracker
```

Replace `YOUR_USERNAME` with your GitHub username.

Alternatively, download the repository as a ZIP file and extract it.

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 5. Run the application

```powershell
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually:

`http://localhost:8501`

## 📊 How to Use

1. Open the application in your browser.
2. Navigate to the **Transactions** tab to add income or expenses.
3. Enter the transaction date, type, category, amount, and description.
4. Visit the **Dashboard** to review totals and spending charts.
5. Open **Budgets** to create monthly spending limits for expense categories.
6. Use the sidebar filters to view specific dates, categories, or transaction types.
7. Open **Export** to download filtered transaction records as a CSV file.

## 🗄️ Database

The application automatically creates a local SQLite database named `expense_tracker.db` when it starts.

The database stores:

* Transaction dates and types
* Income and expense categories
* Transaction amounts and descriptions
* Monthly category budgets

The database file is intended for local use and should not be committed to a public repository if it contains personal financial information.

## 📁 Project Structure

```text
PersonalExpenseTracker/
│
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Files excluded from Git
├── .venv/                 # Virtual environment (not committed)
└── expense_tracker.db     # Local SQLite database (not committed)
```

## 🔐 Data Privacy

* Transaction data is stored locally in SQLite.
* The application does not require an online financial account.
* The database is excluded from Git using `.gitignore`.
* Avoid uploading personal transaction data or other sensitive information to public repositories.

## 🔮 Future Enhancements

* User authentication and individual profiles
* Recurring income and expense tracking
* Savings goals and financial reports
* Monthly report generation
* Automated database backups
* Unit tests and additional input validation

## 🎯 Learning Outcomes

This project demonstrates practical experience with Python programming, SQL database operations, CRUD functionality, data analysis, interactive dashboard development, data visualization, and CSV file handling.

## 👩‍💻 Author

**Your Name**

GitHub: [Your GitHub Profile](https://github.com/kusumabaddu)

---

⭐ If you find this project useful, consider giving the repository a star!
