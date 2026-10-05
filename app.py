import math
import json
import pandas as pd
import plotly.express as px
import streamlit as st
# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="Tee's Daycare Dashboard",
    page_icon="🏫",
    layout="wide",
)


# =========================================================
# LOAD SAVED DATA
# =========================================================

uploaded_file = st.sidebar.file_uploader(
    "📂 Load Saved Daycare Data",
    type=["json"],
    help="Upload a previously saved Tee's Daycare Dashboard file.",
)

if uploaded_file is not None:
    try:
        loaded_data = json.load(uploaded_file)

        if st.sidebar.button("Restore Saved Numbers"):
            # Classroom values
            for classroom in loaded_data.get("classrooms", []):
                name = classroom["Classroom"]

                st.session_state[f"{name}_capacity"] = int(
                    classroom["Capacity"]
                )
                st.session_state[f"{name}_enrolled"] = int(
                    classroom["Enrolled"]
                )
                st.session_state[f"{name}_tuition"] = float(
                    classroom["Weekly Tuition"]
                )

            # Employee values
            employees = loaded_data.get("employees", [])
            st.session_state["number_employees"] = len(employees)

            for i, employee in enumerate(employees):
                st.session_state[f"employee_name_{i}"] = employee[
                    "Employee"
                ]
                st.session_state[f"employee_wage_{i}"] = float(
                    employee["Hourly Wage"]
                )
                st.session_state[f"employee_hours_{i}"] = float(
                    employee["Weekly Hours"]
                )

            # Expenses
            expenses = loaded_data.get("expenses", {})

            st.session_state["rent"] = float(
                expenses.get("rent", 0)
            )
            st.session_state["utilities"] = float(
                expenses.get("utilities", 0)
            )
            st.session_state["food"] = float(
                expenses.get("food", 0)
            )
            st.session_state["supplies"] = float(
                expenses.get("supplies", 0)
            )
            st.session_state["insurance"] = float(
                expenses.get("insurance", 0)
            )
            st.session_state["marketing"] = float(
                expenses.get("marketing", 0)
            )
            st.session_state["other_expenses"] = float(
                expenses.get("other_expenses", 0)
            )

            # Cash
            st.session_state["cash_available"] = float(
                loaded_data.get("cash_available", 0)
            )

            # Enrollment activity
            activity = loaded_data.get("enrollment_activity", {})

            st.session_state["monthly_inquiries"] = int(
                activity.get("monthly_inquiries", 0)
            )
            st.session_state["monthly_tours"] = int(
                activity.get("monthly_tours", 0)
            )
            st.session_state["monthly_applications"] = int(
                activity.get("monthly_applications", 0)
            )
            st.session_state["monthly_new_enrollments"] = int(
                activity.get("monthly_new_enrollments", 0)
            )
            st.session_state["monthly_withdrawals"] = int(
                activity.get("monthly_withdrawals", 0)
            )

            st.session_state["data_restored"] = True
            st.rerun()

    except Exception as e:
        st.sidebar.error(
            "That file could not be loaded. Please use a "
            "dashboard backup file."
        )

if st.session_state.get("data_restored"):
    st.sidebar.success("✅ Saved numbers restored!")

st.title("🏫 Tee's Daycare Dashboard")
st.caption(
    "A business intelligence tool for understanding enrollment, "
    "staffing, financial health, and growth."
)

with st.expander("📖 How to Use This Dashboard"):
    st.write(
        "1. Enter your daycare's actual enrollment, tuition, staffing, "
        "expenses, and cash information in the Business Inputs sidebar."
    )
    st.write(
        "2. Review the dashboard to see enrollment, revenue, payroll, "
        "profitability, break-even, cash runway, and growth insights."
    )
    st.write(
        "3. When you're finished, use the Save Your Dashboard Data section "
        "to download a backup of your numbers."
    )
    st.write(
        "4. The next time you visit, upload that saved file under "
        "Load Saved Daycare Data and click Restore Saved Numbers."
    )

if st.session_state.get("data_restored"):
    st.success(
        "✅ SAVED DATA is currently loaded. The dashboard is using "
        "the numbers restored from your backup file."
    )
else:
    st.info(
        "💡 SAMPLE DATA is currently loaded. Replace the sample numbers "
        "with your daycare's actual information."
    )
WEEKS_PER_MONTH = 52 / 12


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("✏️ Business Inputs")

st.sidebar.write(
    "Update the numbers below and the entire dashboard "
    "will recalculate automatically."
)

st.sidebar.divider()


# =========================================================
# CLASSROOM / ENROLLMENT INPUTS
# =========================================================

st.sidebar.header("👶 Enrollment")

st.sidebar.caption(
    "Enter capacity, enrollment, and average weekly tuition "
    "for each classroom."
)

classroom_defaults = {
    "Infants": {
        "capacity": 10,
        "enrolled": 7,
        "tuition": 300.0,
    },
    "Toddlers": {
        "capacity": 14,
        "enrolled": 9,
        "tuition": 265.0,
    },
    "Preschool": {
        "capacity": 18,
        "enrolled": 12,
        "tuition": 225.0,
    },
    "Pre-K": {
        "capacity": 18,
        "enrolled": 10,
        "tuition": 200.0,
    },
}

classroom_data = []

for classroom, defaults in classroom_defaults.items():

    with st.sidebar.expander(
        classroom,
        expanded=(classroom == "Infants"),
    ):

        capacity = st.number_input(
            f"{classroom} Capacity",
            min_value=0,
            value=defaults["capacity"],
            step=1,
            key=f"{classroom}_capacity",
        )

        enrolled = st.number_input(
            f"{classroom} Enrolled",
            min_value=0,
            max_value=max(capacity, 1),
            value=min(defaults["enrolled"], max(capacity, 1)),
            step=1,
            key=f"{classroom}_enrolled",
        )

        tuition = st.number_input(
            f"{classroom} Weekly Tuition ($)",
            min_value=0.0,
            value=defaults["tuition"],
            step=5.0,
            key=f"{classroom}_tuition",
        )

    classroom_data.append(
        {
            "Classroom": classroom,
            "Capacity": capacity,
            "Enrolled": enrolled,
            "Weekly Tuition": tuition,
        }
    )

classroom_df = pd.DataFrame(classroom_data)


# =========================================================
# STAFFING INPUTS
# =========================================================

st.sidebar.divider()
st.sidebar.header("👩🏽‍🏫 Staffing")

st.sidebar.caption(
    "Enter each employee's approximate hourly wage "
    "and weekly hours."
)

number_employees = st.sidebar.number_input(
    "Number of Employees",
    min_value=0,
    max_value=30,
    value=10,
    step=1,
    key="number_employees",
)

employee_data = []

for i in range(number_employees):

    with st.sidebar.expander(
        f"Employee {i + 1}",
        expanded=False,
    ):

        employee_name = st.text_input(
            "Name or Role",
            value=f"Employee {i + 1}",
            key=f"employee_name_{i}",
        )

        hourly_wage = st.number_input(
            "Hourly Wage ($)",
            min_value=0.0,
            value=16.0,
            step=0.50,
            key=f"employee_wage_{i}",
        )

        weekly_hours = st.number_input(
            "Hours per Week",
            min_value=0.0,
            max_value=80.0,
            value=34.0,
            step=1.0,
            key=f"employee_hours_{i}",
        )

    monthly_employee_cost = (
        hourly_wage
        * weekly_hours
        * WEEKS_PER_MONTH
    )

    employee_data.append(
        {
            "Employee": employee_name,
            "Hourly Wage": hourly_wage,
            "Weekly Hours": weekly_hours,
            "Monthly Payroll": monthly_employee_cost,
        }
    )

employee_df = pd.DataFrame(employee_data)


# =========================================================
# OPERATING EXPENSES
# =========================================================

st.sidebar.divider()
st.sidebar.header("💰 Monthly Expenses")

rent = st.sidebar.number_input(
    "Rent / Mortgage ($)",
    min_value=0.0,
    value=6500.0,
    step=100.0,
    key="rent",
)

utilities = st.sidebar.number_input(
    "Utilities ($)",
    min_value=0.0,
    value=1200.0,
    step=50.0,
    key="utilities",
)

food = st.sidebar.number_input(
    "Food ($)",
    min_value=0.0,
    value=2200.0,
    step=50.0,
    key="food",
)

supplies = st.sidebar.number_input(
    "Supplies ($)",
    min_value=0.0,
    value=900.0,
    step=50.0,
    key="supplies",
)

insurance = st.sidebar.number_input(
    "Insurance ($)",
    min_value=0.0,
    value=1000.0,
    step=50.0,
    key="insurance",
)

marketing = st.sidebar.number_input(
    "Marketing ($)",
    min_value=0.0,
    value=500.0,
    step=50.0,
    key="marketing",
)

other_expenses = st.sidebar.number_input(
    "Other Expenses ($)",
    min_value=0.0,
    value=900.0,
    step=50.0,
    key="other_expenses",
)


# =========================================================
# CASH
# =========================================================

st.sidebar.divider()
st.sidebar.header("🏦 Cash Position")

cash_available = st.sidebar.number_input(
    "Business Cash Available ($)",
    min_value=0.0,
    value=15000.0,
    step=500.0,
    key="cash_available",
)


# =========================================================
# ENROLLMENT FUNNEL
# =========================================================

st.sidebar.divider()
st.sidebar.header("📣 Enrollment Activity")

monthly_inquiries = st.sidebar.number_input(
    "Parent Inquiries This Month",
    min_value=0,
    value=25,
    step=1,
    key="monthly_inquiries",
)

monthly_tours = st.sidebar.number_input(
    "Tours This Month",
    min_value=0,
    value=14,
    step=1,
    key="monthly_tours",
)

monthly_applications = st.sidebar.number_input(
    "Applications This Month",
    min_value=0,
    value=9,
    step=1,
    key="monthly_applications",
)

monthly_new_enrollments = st.sidebar.number_input(
    "New Enrollments This Month",
    min_value=0,
    value=6,
    step=1,
    key="monthly_new_enrollments",
)

monthly_withdrawals = st.sidebar.number_input(
    "Withdrawals This Month",
    min_value=0,
    value=3,
    step=1,
    key="monthly_withdrawals",
)


# =========================================================
# CORE CALCULATIONS
# =========================================================

total_capacity = int(classroom_df["Capacity"].sum())

total_enrollment = int(classroom_df["Enrolled"].sum())

open_seats = max(
    total_capacity - total_enrollment,
    0,
)

occupancy_rate = (
    total_enrollment / total_capacity
    if total_capacity > 0
    else 0
)

classroom_df["Open Seats"] = (
    classroom_df["Capacity"]
    - classroom_df["Enrolled"]
)

classroom_df["Monthly Revenue"] = (
    classroom_df["Enrolled"]
    * classroom_df["Weekly Tuition"]
    * WEEKS_PER_MONTH
)

monthly_revenue = classroom_df[
    "Monthly Revenue"
].sum()

monthly_payroll = (
    employee_df["Monthly Payroll"].sum()
    if not employee_df.empty
    else 0
)

non_payroll_expenses = (
    rent
    + utilities
    + food
    + supplies
    + insurance
    + marketing
    + other_expenses
)

total_expenses = (
    monthly_payroll
    + non_payroll_expenses
)

monthly_profit = (
    monthly_revenue
    - total_expenses
)

labor_percent = (
    monthly_payroll / monthly_revenue
    if monthly_revenue > 0
    else 0
)

net_enrollment_change = (
    monthly_new_enrollments
    - monthly_withdrawals
)

inquiry_conversion = (
    monthly_new_enrollments / monthly_inquiries
    if monthly_inquiries > 0
    else 0
)

tour_conversion = (
    monthly_new_enrollments / monthly_tours
    if monthly_tours > 0
    else 0
)


# =========================================================
# ESTIMATED BREAK EVEN
# =========================================================

if total_enrollment > 0:

    avg_monthly_revenue_per_child = (
        monthly_revenue / total_enrollment
    )

else:

    avg_monthly_revenue_per_child = 0


if avg_monthly_revenue_per_child > 0:

    break_even_enrollment = math.ceil(
        total_expenses
        / avg_monthly_revenue_per_child
    )

else:

    break_even_enrollment = 0


additional_children_needed = max(
    break_even_enrollment
    - total_enrollment,
    0,
)


# =========================================================
# CASH RUNWAY
# =========================================================

if monthly_profit < 0:

    monthly_burn = abs(monthly_profit)

    cash_runway = (
        cash_available / monthly_burn
        if monthly_burn > 0
        else float("inf")
    )

else:

    monthly_burn = 0
    cash_runway = None


# =========================================================
# EXECUTIVE SUMMARY
# =========================================================

st.header("📊 Executive Summary")

row1 = st.columns(4)

row1[0].metric(
    "Current Enrollment",
    total_enrollment,
    f"{open_seats} open seats",
)

row1[1].metric(
    "Occupancy",
    f"{occupancy_rate:.1%}",
)

row1[2].metric(
    "Monthly Revenue",
    f"${monthly_revenue:,.0f}",
)

row1[3].metric(
    "Monthly Profit / Loss",
    f"${monthly_profit:,.0f}",
)

row2 = st.columns(4)

row2[0].metric(
    "Monthly Payroll",
    f"${monthly_payroll:,.0f}",
)

row2[1].metric(
    "Labor % of Revenue",
    f"{labor_percent:.1%}",
)

row2[2].metric(
    "Estimated Break-Even",
    f"{break_even_enrollment} children",
)

row2[3].metric(
    "Children Needed",
    additional_children_needed,
)


if monthly_profit < 0:

    st.error(
        f"⚠️ At the current numbers, the daycare is "
        f"projected to operate approximately "
        f"${abs(monthly_profit):,.0f} below break-even "
        f"per month."
    )

elif monthly_profit == 0:

    st.warning(
        "The daycare is approximately at break-even."
    )

else:

    st.success(
        f"✅ At the current numbers, the daycare is "
        f"projected to generate approximately "
        f"${monthly_profit:,.0f} above entered expenses "
        f"per month."
    )


# =========================================================
# CASH RUNWAY
# =========================================================

st.divider()
st.header("🏦 Cash Runway")

cash1, cash2, cash3 = st.columns(3)

cash1.metric(
    "Cash Available",
    f"${cash_available:,.0f}",
)

cash2.metric(
    "Monthly Burn",
    (
        f"${monthly_burn:,.0f}"
        if monthly_burn > 0
        else "$0"
    ),
)

if cash_runway is not None:

    cash3.metric(
        "Estimated Runway",
        f"{cash_runway:.1f} months",
    )

    if cash_runway < 3:

        st.error(
            "🚨 At the current estimated loss rate, "
            "available cash would cover less than "
            "three months."
        )

    elif cash_runway < 6:

        st.warning(
            "⚠️ Available cash would cover approximately "
            f"{cash_runway:.1f} months at the current "
            "estimated loss rate."
        )

    else:

        st.info(
            f"At the current estimated loss rate, cash "
            f"would cover approximately "
            f"{cash_runway:.1f} months."
        )

else:

    cash3.metric(
        "Estimated Runway",
        "Not burning cash",
    )

    st.success(
        "The entered numbers do not currently indicate "
        "a monthly operating cash deficit."
    )


# =========================================================
# CLASSROOM PERFORMANCE
# =========================================================

st.divider()
st.header("👶 Classroom & Enrollment Health")

display_classrooms = classroom_df.copy()

display_classrooms["Occupancy"] = (
    display_classrooms.apply(
        lambda row:
        row["Enrolled"] / row["Capacity"]
        if row["Capacity"] > 0
        else 0,
        axis=1,
    )
)

st.dataframe(
    display_classrooms[
        [
            "Classroom",
            "Capacity",
            "Enrolled",
            "Open Seats",
            "Weekly Tuition",
            "Occupancy",
            "Monthly Revenue",
        ]
    ].style.format(
        {
            "Weekly Tuition": "${:,.0f}",
            "Occupancy": "{:.1%}",
            "Monthly Revenue": "${:,.0f}",
        }
    ),
    width="stretch",
    hide_index=True,
)


fig_classrooms = px.bar(
    classroom_df,
    x="Classroom",
    y=["Enrolled", "Open Seats"],
    title="Enrollment by Classroom",
    barmode="stack",
)

st.plotly_chart(
    fig_classrooms,
    width="stretch",
)


# =========================================================
# FINANCIAL HEALTH
# =========================================================

st.divider()
st.header("💰 Financial Health")

expense_df = pd.DataFrame(
    {
        "Expense": [
            "Payroll",
            "Rent",
            "Utilities",
            "Food",
            "Supplies",
            "Insurance",
            "Marketing",
            "Other",
        ],
        "Amount": [
            monthly_payroll,
            rent,
            utilities,
            food,
            supplies,
            insurance,
            marketing,
            other_expenses,
        ],
    }
)

fin1, fin2 = st.columns(2)

with fin1:

    fig_expenses = px.pie(
        expense_df,
        names="Expense",
        values="Amount",
        title="Where the Money Is Going",
        hole=0.45,
    )

    st.plotly_chart(
        fig_expenses,
        width="stretch",
    )


with fin2:

    st.subheader("Monthly Snapshot")

    st.metric(
        "Revenue",
        f"${monthly_revenue:,.0f}",
    )

    st.metric(
        "Payroll",
        f"${monthly_payroll:,.0f}",
    )

    st.metric(
        "Other Expenses",
        f"${non_payroll_expenses:,.0f}",
    )

    st.metric(
        "Total Expenses",
        f"${total_expenses:,.0f}",
    )

    st.metric(
        "Profit / Loss",
        f"${monthly_profit:,.0f}",
    )


# =========================================================
# STAFFING
# =========================================================

st.divider()
st.header("👩🏽‍🏫 Staffing Overview")

if not employee_df.empty:

    employee_display = employee_df.copy()

    st.dataframe(
        employee_display.style.format(
            {
                "Hourly Wage": "${:,.2f}",
                "Weekly Hours": "{:,.1f}",
                "Monthly Payroll": "${:,.0f}",
            }
        ),
        width="stretch",
        hide_index=True,
    )

    staffing1, staffing2, staffing3 = st.columns(3)

    staffing1.metric(
        "Employees",
        number_employees,
    )

    staffing2.metric(
        "Total Weekly Hours",
        f"{employee_df['Weekly Hours'].sum():,.0f}",
    )

    staffing3.metric(
        "Estimated Monthly Payroll",
        f"${monthly_payroll:,.0f}",
    )

else:

    st.info(
        "No employees have been entered."
    )


# =========================================================
# ENROLLMENT FUNNEL
# =========================================================

st.divider()
st.header("📣 Enrollment Funnel")

funnel_df = pd.DataFrame(
    {
        "Stage": [
            "Parent Inquiries",
            "Tours",
            "Applications",
            "New Enrollments",
        ],
        "Families": [
            monthly_inquiries,
            monthly_tours,
            monthly_applications,
            monthly_new_enrollments,
        ],
    }
)

fig_funnel = px.funnel(
    funnel_df,
    x="Families",
    y="Stage",
    title="Inquiry → Enrollment",
)

st.plotly_chart(
    fig_funnel,
    width="stretch",
)

f1, f2, f3 = st.columns(3)

f1.metric(
    "Inquiry → Enrollment",
    f"{inquiry_conversion:.1%}",
)

f2.metric(
    "Tour → Enrollment",
    f"{tour_conversion:.1%}",
)

f3.metric(
    "Net Enrollment Change",
    f"{net_enrollment_change:+d}",
)


# =========================================================
# RECOVERY TARGETS
# =========================================================

st.divider()
st.header("🎯 Enrollment Recovery Targets")

target_levels = [
    0.75,
    0.90,
    1.00,
]

target_rows = []

for target in target_levels:

    target_enrollment = math.ceil(
        total_capacity * target
    )

    children_to_add = max(
        target_enrollment - total_enrollment,
        0,
    )

    estimated_target_revenue = (
        target_enrollment
        * avg_monthly_revenue_per_child
    )

    estimated_target_profit = (
        estimated_target_revenue
        - total_expenses
    )

    target_rows.append(
        {
            "Goal": f"{int(target * 100)}% Capacity",
            "Target Enrollment": target_enrollment,
            "Additional Children": children_to_add,
            "Estimated Revenue": estimated_target_revenue,
            "Estimated Profit/Loss": estimated_target_profit,
        }
    )


if break_even_enrollment > 0:

    break_even_revenue = (
        break_even_enrollment
        * avg_monthly_revenue_per_child
    )

    target_rows.insert(
        0,
        {
            "Goal": "Estimated Break-Even",
            "Target Enrollment": break_even_enrollment,
            "Additional Children": additional_children_needed,
            "Estimated Revenue": break_even_revenue,
            "Estimated Profit/Loss": (
                break_even_revenue
                - total_expenses
            ),
        },
    )


targets_df = pd.DataFrame(target_rows)

st.dataframe(
    targets_df.style.format(
        {
            "Estimated Revenue": "${:,.0f}",
            "Estimated Profit/Loss": "${:,.0f}",
        }
    ),
    width="stretch",
    hide_index=True,
)


# =========================================================
# WHAT-IF PLANNER
# =========================================================

st.divider()
st.header("🔮 What-If Planner")

st.write(
    "Use this section to test possible changes without "
    "changing the daycare's actual numbers above."
)

what1, what2, what3 = st.columns(3)

with what1:

    scenario_children = st.slider(
        "Add Children",
        min_value=0,
        max_value=max(open_seats, 1),
        value=0,
    )


with what2:

    scenario_weekly_tuition_change = st.number_input(
        "Average Weekly Tuition Change ($)",
        min_value=-100.0,
        max_value=200.0,
        value=0.0,
        step=5.0,
    )


with what3:

    scenario_hours_cut = st.number_input(
        "Total Staff Hours Reduced per Week",
        min_value=0.0,
        value=0.0,
        step=1.0,
    )


scenario_enrollment = min(
    total_enrollment + scenario_children,
    total_capacity,
)


if total_enrollment > 0:

    average_weekly_tuition = (
        monthly_revenue
        / total_enrollment
        / WEEKS_PER_MONTH
    )

else:

    average_weekly_tuition = 0


scenario_tuition = max(
    average_weekly_tuition
    + scenario_weekly_tuition_change,
    0,
)


scenario_revenue = (
    scenario_enrollment
    * scenario_tuition
    * WEEKS_PER_MONTH
)


if not employee_df.empty:

    average_hourly_wage = (
        employee_df["Hourly Wage"].mean()
    )

else:

    average_hourly_wage = 0


scenario_payroll_savings = (
    scenario_hours_cut
    * average_hourly_wage
    * WEEKS_PER_MONTH
)


scenario_payroll = max(
    monthly_payroll
    - scenario_payroll_savings,
    0,
)


scenario_total_expenses = (
    non_payroll_expenses
    + scenario_payroll
)


scenario_profit = (
    scenario_revenue
    - scenario_total_expenses
)


scenario_change = (
    scenario_profit
    - monthly_profit
)


s1, s2, s3, s4 = st.columns(4)

s1.metric(
    "Scenario Enrollment",
    scenario_enrollment,
)

s2.metric(
    "Scenario Revenue",
    f"${scenario_revenue:,.0f}",
)

s3.metric(
    "Scenario Profit / Loss",
    f"${scenario_profit:,.0f}",
)

s4.metric(
    "Improvement",
    f"${scenario_change:,.0f}",
)


if scenario_profit >= 0:

    st.success(
        f"✅ Under this scenario, the daycare would "
        f"operate approximately ${scenario_profit:,.0f} "
        f"above the entered monthly expenses."
    )

else:

    st.warning(
        f"Under this scenario, the daycare would still "
        f"operate approximately "
        f"${abs(scenario_profit):,.0f} below break-even."
    )


# =========================================================
# QUICK INSIGHTS
# =========================================================

st.divider()
st.header("💡 Quick Insights")

if occupancy_rate < 0.75:

    st.write(
        f"• Enrollment is currently **{occupancy_rate:.1%}** "
        f"of entered capacity, leaving **{open_seats} open seats**."
    )

else:

    st.write(
        f"• Enrollment is currently **{occupancy_rate:.1%}** "
        f"of entered capacity."
    )


if labor_percent > 0:

    st.write(
        f"• Payroll currently represents approximately "
        f"**{labor_percent:.1%} of estimated tuition revenue**."
    )


if additional_children_needed > 0:

    st.write(
        f"• Based on the current assumptions, approximately "
        f"**{additional_children_needed} additional children** "
        f"would be needed to reach estimated break-even."
    )

else:

    st.write(
        "• Current estimated enrollment is at or above "
        "the calculated break-even level."
    )


if net_enrollment_change > 0:

    st.write(
        f"• Enrollment activity shows a net gain of "
        f"**{net_enrollment_change} children** this month."
    )

elif net_enrollment_change < 0:

    st.write(
        f"• Enrollment activity shows a net loss of "
        f"**{abs(net_enrollment_change)} children** this month."
    )

else:

    st.write(
        "• New enrollments and withdrawals are currently equal."
    )


# =========================================================
# DISCLAIMER
# =========================================================

st.divider()

st.caption(
    "Planning estimates only. Results depend on the accuracy of "
    "the information entered and do not include every possible "
    "tax, payroll, benefit, regulatory, or operating expense. "
    "Staffing decisions must comply with applicable childcare "
    "licensing, supervision, and child-to-staff ratio requirements."
)
# =========================================================
# SAVE DATA
# =========================================================

st.divider()
st.header("💾 Save Your Dashboard Data")

st.write(
    "Finished entering your daycare's information? "
    "Download a backup so you can keep a copy of the numbers."
)

save_data = {
    "classrooms": classroom_data,
    "employees": employee_data,
    "expenses": {
        "rent": rent,
        "utilities": utilities,
        "food": food,
        "supplies": supplies,
        "insurance": insurance,
        "marketing": marketing,
        "other_expenses": other_expenses,
    },
    "cash_available": cash_available,
    "enrollment_activity": {
        "monthly_inquiries": monthly_inquiries,
        "monthly_tours": monthly_tours,
        "monthly_applications": monthly_applications,
        "monthly_new_enrollments": monthly_new_enrollments,
        "monthly_withdrawals": monthly_withdrawals,
    },
}

json_data = json.dumps(
    save_data,
    indent=4,
)

st.download_button(
    label="💾 Download My Daycare Data",
    data=json_data,
    file_name="tees_daycare_data.json",
    mime="application/json",
)

st.caption(
    "Keep this file somewhere safe. It contains the business "
    "numbers entered into the dashboard."
)