
import sqlite3
from pathlib import Path
from datetime import date
import calendar

import pandas as pd
import plotly.express as px
import streamlit as st


# -------------------- CONFIGURATION --------------------

st.set_page_config(
    page_title="Personal Expense Tracker",
    page_icon="💰",
    layout="wide",
)

DB_PATH = Path(__file__).resolve().parent / "expense_tracker.db"

EXPENSE_CATEGORIES = [
    "Food", "Transport", "Shopping", "Bills",
    "Health", "Education", "Entertainment", "Other"
]

INCOME_CATEGORIES = [
    "Salary", "Freelance", "Business", "Gift", "Other"
]


# -------------------- DATABASE --------------------

def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                description TEXT DEFAULT ''
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                budget_month TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                UNIQUE(budget_month, category)
            )
        """)


def load_transactions():
    with get_connection() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM transactions ORDER BY transaction_date DESC, id DESC",
            conn,
        )
    if not df.empty:
        df["transaction_date"] = pd.to_datetime(
            df["transaction_date"]
        ).dt.date
    return df


def load_budgets():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM budgets ORDER BY budget_month DESC, category",
            conn,
        )


def add_transaction(tx_date, tx_type, category, amount, description):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO transactions
            (transaction_date, transaction_type, category, amount, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                tx_date.isoformat(),
                tx_type,
                category,
                float(amount),
                description.strip(),
            ),
        )


def update_transaction(tx_id, tx_date, tx_type, category, amount, description):
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE transactions
            SET transaction_date = ?, transaction_type = ?,
                category = ?, amount = ?, description = ?
            WHERE id = ?
            """,
            (
                tx_date.isoformat(),
                tx_type,
                category,
                float(amount),
                description.strip(),
                int(tx_id),
            ),
        )


def delete_transaction(tx_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM transactions WHERE id = ?",
            (int(tx_id),),
        )


def save_budget(budget_month, category, amount):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO budgets (budget_month, category, amount)
            VALUES (?, ?, ?)
            ON CONFLICT(budget_month, category)
            DO UPDATE SET amount = excluded.amount
            """,
            (budget_month, category, float(amount)),
        )


def delete_budget(budget_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM budgets WHERE id = ?",
            (int(budget_id),),
        )


# -------------------- HELPERS --------------------

def money(amount):
    return f"₹{amount:,.2f}"


def month_string(value):
    return value.strftime("%Y-%m")


def filter_transactions(df, start_date, end_date, tx_type, category):
    if df.empty:
        return df.copy()

    result = df[
        (df["transaction_date"] >= start_date)
        & (df["transaction_date"] <= end_date)
    ].copy()

    if tx_type != "All":
        result = result[result["transaction_type"] == tx_type]

    if category != "All":
        result = result[result["category"] == category]

    return result


# -------------------- INITIALIZE --------------------

initialize_database()

st.title("💰 Personal Expense Tracker")
st.caption("Track your money. Understand your habits. Stay within budget.")

transactions = load_transactions()
budgets = load_budgets()

# -------------------- SIDEBAR --------------------

st.sidebar.header("🔎 Filter Records")

today = date.today()
first_day = today.replace(day=1)
last_day = today.replace(
    day=calendar.monthrange(today.year, today.month)[1]
)

start_date = st.sidebar.date_input(
    "Start date",
    value=first_day,
    key="filter_start",
)

end_date = st.sidebar.date_input(
    "End date",
    value=today,
    key="filter_end",
)

type_filter = st.sidebar.selectbox(
    "Transaction type",
    ["All", "Income", "Expense"],
)

available_categories = sorted(
    set(EXPENSE_CATEGORIES + INCOME_CATEGORIES)
)

category_filter = st.sidebar.selectbox(
    "Category",
    ["All"] + available_categories,
)

if start_date > end_date:
    st.error("Start date must be on or before the end date.")
    st.stop()

filtered = filter_transactions(
    transactions,
    start_date,
    end_date,
    type_filter,
    category_filter,
)

# -------------------- NAVIGATION --------------------

tab_dashboard, tab_transactions, tab_budgets, tab_export = st.tabs(
    ["📊 Dashboard", "🧾 Transactions", "🎯 Budgets", "📥 Export"]
)


# -------------------- DASHBOARD --------------------

with tab_dashboard:
    st.subheader("Financial Overview")

    income_total = filtered.loc[
        filtered["transaction_type"] == "Income", "amount"
    ].sum() if not filtered.empty else 0.0

    expense_total = filtered.loc[
        filtered["transaction_type"] == "Expense", "amount"
    ].sum() if not filtered.empty else 0.0

    balance = income_total - expense_total

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Income", money(income_total))
    col2.metric("Total Expenses", money(expense_total))
    col3.metric("Net Balance", money(balance))

    st.caption(
        f"Showing transactions from {start_date} to {end_date} "
        f"with the selected sidebar filters."
    )

    if filtered.empty:
        st.info(
            "No transactions match these filters. "
            "Open Transactions to add your first record."
        )
    else:
        left, right = st.columns(2)

        with left:
            st.markdown("#### Expenses by Category")
            expense_data = filtered[
                filtered["transaction_type"] == "Expense"
            ]

            if expense_data.empty:
                st.info("No expenses in this selection.")
            else:
                category_totals = (
                    expense_data.groupby("category", as_index=False)["amount"]
                    .sum()
                )
                fig = px.pie(
                    category_totals,
                    names="category",
                    values="amount",
                    hole=0.45,
                    title="Expense Distribution",
                )
                st.plotly_chart(fig, use_container_width=True)

        with right:
            st.markdown("#### Income vs Expenses by Month")

            monthly = filtered.copy()
            monthly["month"] = pd.to_datetime(
                monthly["transaction_date"]
            ).dt.to_period("M").astype(str)

            monthly_summary = (
                monthly.groupby(["month", "transaction_type"])["amount"]
                .sum()
                .reset_index()
            )

            fig = px.bar(
                monthly_summary,
                x="month",
                y="amount",
                color="transaction_type",
                barmode="group",
                title="Monthly Cash Flow",
                labels={
                    "month": "Month",
                    "amount": "Amount (₹)",
                    "transaction_type": "Type",
                },
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Recent Transactions")
        recent = filtered.head(5).copy()
        recent["transaction_date"] = recent[
            "transaction_date"
        ].astype(str)
        recent["amount"] = recent["amount"].map(money)

        st.dataframe(
            recent[
                [
                    "transaction_date",
                    "transaction_type",
                    "category",
                    "amount",
                    "description",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    # Current-month budget progress
    st.markdown("#### Current Month Budget Progress")

    current_month = month_string(today)

    if not budgets.empty:
        current_budgets = budgets[
            budgets["budget_month"] == current_month
        ]

        if current_budgets.empty:
            st.info("No budgets set for this month yet.")
        else:
            month_expenses = transactions[
                (transactions["transaction_type"] == "Expense")
                & (
                    pd.to_datetime(
                        transactions["transaction_date"]
                    ).dt.strftime("%Y-%m") == current_month
                )
            ] if not transactions.empty else pd.DataFrame()

            for _, budget in current_budgets.iterrows():
                spent = 0.0

                if not month_expenses.empty:
                    spent = month_expenses.loc[
                        month_expenses["category"] == budget["category"],
                        "amount",
                    ].sum()

                limit = float(budget["amount"])
                ratio = spent / limit if limit > 0 else 0

                st.write(
                    f"**{budget['category']}** — "
                    f"{money(spent)} spent of {money(limit)}"
                )
                st.progress(min(ratio, 1.0))

                if ratio > 1:
                    st.warning(
                        f"{budget['category']} budget exceeded by "
                        f"{money(spent - limit)}."
                    )
                elif ratio >= 0.8:
                    st.info("You have used at least 80% of this budget.")
    else:
        st.info("Set a budget in the Budgets tab to track your spending.")


# -------------------- TRANSACTIONS --------------------

with tab_transactions:
    st.subheader("Manage Transactions")

    with st.expander("➕ Add a transaction", expanded=True):
        with st.form("add_transaction_form", clear_on_submit=True):
            new_date = st.date_input("Date", value=today)
            new_type = st.selectbox(
                "Type", ["Expense", "Income"], key="new_type"
            )

            new_category = st.selectbox(
                "Category",
                EXPENSE_CATEGORIES
                if new_type == "Expense"
                else INCOME_CATEGORIES,
                key="new_category",
            )

            new_amount = st.number_input(
                "Amount (₹)", min_value=0.01, value=100.0, step=50.0
            )
            new_description = st.text_input(
                "Description", placeholder="e.g. Lunch or monthly salary"
            )

            submitted = st.form_submit_button(
                "Save Transaction", type="primary"
            )

            if submitted:
                add_transaction(
                    new_date,
                    new_type,
                    new_category,
                    new_amount,
                    new_description,
                )
                st.success("Transaction saved successfully!")
                st.rerun()

    st.markdown("#### Filtered Transaction Records")

    if filtered.empty:
        st.info("No transactions match your selected filters.")
    else:
        display_df = filtered.copy()
        display_df["transaction_date"] = display_df[
            "transaction_date"
        ].astype(str)
        display_df["amount"] = display_df["amount"].map(money)

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("#### Edit or Delete a Transaction")

    if transactions.empty:
        st.info("Add a transaction first to enable editing and deletion.")
    else:
        transaction_ids = transactions["id"].astype(int).tolist()

        selected_id = st.selectbox(
            "Select transaction ID",
            transaction_ids,
            format_func=lambda tx_id: (
                f"#{tx_id} | "
                f"{transactions.loc[transactions['id'] == tx_id, 'transaction_date'].iloc[0]} | "
                f"{transactions.loc[transactions['id'] == tx_id, 'category'].iloc[0]} | "
                f"{money(transactions.loc[transactions['id'] == tx_id, 'amount'].iloc[0])}"
            ),
        )

        record = transactions[
            transactions["id"] == selected_id
        ].iloc[0]

        with st.form("edit_transaction_form"):
            edit_date = st.date_input(
                "Edit date",
                value=record["transaction_date"],
                key="edit_date",
            )

            edit_type = st.selectbox(
                "Edit type",
                ["Expense", "Income"],
                index=(
                    0 if record["transaction_type"] == "Expense" else 1
                ),
            )

            edit_categories = (
                EXPENSE_CATEGORIES
                if edit_type == "Expense"
                else INCOME_CATEGORIES
            )

            old_category = record["category"]
            edit_category = st.selectbox(
                "Edit category",
                edit_categories,
                index=(
                    edit_categories.index(old_category)
                    if old_category in edit_categories
                    else 0
                ),
            )

            edit_amount = st.number_input(
                "Edit amount (₹)",
                min_value=0.01,
                value=float(record["amount"]),
                step=50.0,
            )

            edit_description = st.text_input(
                "Edit description",
                value=str(record["description"] or ""),
            )

            update_clicked = st.form_submit_button("Update Transaction")

            if update_clicked:
                update_transaction(
                    selected_id,
                    edit_date,
                    edit_type,
                    edit_category,
                    edit_amount,
                    edit_description,
                )
                st.success("Transaction updated!")
                st.rerun()

        confirm_delete = st.checkbox(
            f"I confirm deletion of transaction #{selected_id}",
            key="confirm_delete",
        )

        if st.button("🗑️ Delete Selected Transaction", type="secondary"):
            if confirm_delete:
                delete_transaction(selected_id)
                st.success("Transaction deleted.")
                st.rerun()
            else:
                st.warning("Please confirm before deleting.")


# -------------------- BUDGETS --------------------

with tab_budgets:
    st.subheader("Monthly Budgets")
    st.write(
        "Create a monthly spending limit for each expense category. "
        "Saving a budget again for the same month and category updates it."
    )

    with st.form("budget_form"):
        budget_date = st.date_input(
            "Choose a date in the budget month",
            value=today,
            key="budget_date",
        )

        budget_category = st.selectbox(
            "Expense category",
            EXPENSE_CATEGORIES,
            key="budget_category",
        )

        budget_amount = st.number_input(
            "Budget limit (₹)",
            min_value=0.01,
            value=5000.0,
            step=500.0,
        )

        budget_submitted = st.form_submit_button("Save Monthly Budget")

        if budget_submitted:
            save_budget(
                month_string(budget_date),
                budget_category,
                budget_amount,
            )
            st.success("Budget saved!")
            st.rerun()

    budgets = load_budgets()

    st.markdown("#### Saved Budgets")

    if budgets.empty:
        st.info("You have not created any budgets yet.")
    else:
        budget_view = budgets.copy()
        budget_view["amount"] = budget_view["amount"].map(money)
        st.dataframe(
            budget_view,
            use_container_width=True,
            hide_index=True,
        )

        budget_ids = budgets["id"].astype(int).tolist()
        selected_budget_id = st.selectbox(
            "Select a budget to delete",
            budget_ids,
            format_func=lambda budget_id: (
                f"#{budget_id} | "
                f"{budgets.loc[budgets['id'] == budget_id, 'budget_month'].iloc[0]} | "
                f"{budgets.loc[budgets['id'] == budget_id, 'category'].iloc[0]}"
            ),
        )

        confirm_budget_delete = st.checkbox(
            "I confirm deletion of this budget",
            key="confirm_budget_delete",
        )

        if st.button("Delete Selected Budget"):
            if confirm_budget_delete:
                delete_budget(selected_budget_id)
                st.success("Budget deleted.")
                st.rerun()
            else:
                st.warning("Please confirm before deleting.")


# -------------------- CSV EXPORT --------------------

with tab_export:
    st.subheader("Export Your Transactions")

    st.write(
        "Download the transactions matching your sidebar date, type, "
        "and category filters."
    )

    export_df = filtered.copy()

    if not export_df.empty:
        export_df["transaction_date"] = export_df[
            "transaction_date"
        ].astype(str)

    st.metric("Records to export", len(export_df))

    csv_data = export_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="📥 Download Filtered Transactions (CSV)",
        data=csv_data,
        file_name=f"transactions_{start_date}_{end_date}.csv",
        mime="text/csv",
        disabled=export_df.empty,
    )

    st.caption(
        "CSV files can be opened in Microsoft Excel or Google Sheets. "
        "Exported files contain transaction records, not saved budgets."
    )

st.divider()
st.caption("Personal Expense Tracker | Built with Python, SQLite, Streamlit, Pandas and Plotly")