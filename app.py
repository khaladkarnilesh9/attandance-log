elif nav == "💰 Payment Collection Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)

    TARGET_PAYMENT_YEAR = 2025 # Using a separate constant for clarity, though it's the same year
    current_quarter_for_payment_display = get_quarter_str_for_year(TARGET_PAYMENT_YEAR, use_current_moment=True)
    status_options_payment = ["Not Started", "Collection In Progress", "Collection Complete", "Overdue", "Cancelled"] # Slightly different statuses

    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Manage Payment Collection Goals</h4>", unsafe_allow_html=True)
        admin_action_payment = st.radio("Action:", ["View Team Collection Progress", f"Set/Edit Collection Goal for {TARGET_PAYMENT_YEAR}"],
            key="admin_payment_action_2025_q", horizontal=True)

        if admin_action_payment == "View Team Collection Progress":
            st.markdown(f"<h5>Team Payment Collection Progress for {current_quarter_for_payment_display}</h5>", unsafe_allow_html=True)
            employee_users = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
            if not employee_users: st.info("No employees found.")
            else:
                summary_data_payment = []
                for emp_name in employee_users:
                    user_info_payment = USERS.get(emp_name, {})
                    emp_current_payment_goal = payment_goals_df[(payment_goals_df["Username"].astype(str) == str(emp_name)) & (payment_goals_df["MonthYear"].astype(str) == str(current_quarter_for_payment_display))]
                    target, achieved, prog_val = 0.0, 0.0, 0.0
                    goal_desc, status_val = "Not Set", "N/A" # Default status for payment
                    if not emp_current_payment_goal.empty:
                        p_data = emp_current_payment_goal.iloc[0]
                        target = pd.to_numeric(p_data.get("TargetAmount"), errors='coerce').fillna(0.0)
                        achieved = pd.to_numeric(p_data.get("AchievedAmount"), errors='coerce').fillna(0.0)
                        if target > 0: prog_val = min(achieved / target, 1.0)
                        goal_desc = p_data.get("GoalDescription", "N/A")
                        status_val = p_data.get("Status", "N/A")
                    summary_data_payment.append({"Photo": user_info_payment.get("profile_photo",""), "Employee": emp_name, "Position": user_info_payment.get("position","N/A"),
                                                 "Goal": goal_desc, "Target Collection": target, "Amount Collected": achieved, "Progress": prog_val, "Status": status_val})
                if summary_data_payment:
                    st.dataframe(pd.DataFrame(summary_data_payment), use_container_width=True, hide_index=True, column_config={
                        "Photo": st.column_config.ImageColumn("Pic", width="small"), "Target Collection": st.column_config.NumberColumn("Target (₹)", format="%.0f"),
                        "Amount Collected": st.column_config.NumberColumn("Collected (₹)", format="%.0f"), "Progress": st.column_config.ProgressColumn("Progress", format="%.0f%%", min_value=0, max_value=1)})
                
                # Option to show chart for team payment progress
                # team_payment_df_for_chart = payment_goals_df[payment_goals_df["MonthYear"].str.startswith(str(TARGET_PAYMENT_YEAR))]
                # if not team_payment_df_for_chart.empty:
                #    render_goal_chart(team_payment_df_for_chart.groupby('MonthYear', as_index=False)[['TargetAmount', 'AchievedAmount']].sum(), "Overall Team Payment Collection vs Target 2025")


        elif admin_action_payment == f"Set/Edit Collection Goal for {TARGET_PAYMENT_YEAR}":
            st.markdown(f"<h5>Set or Update Payment Collection Goal ({TARGET_PAYMENT_YEAR} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options_payment = [u for u, d in USERS.items() if d["role"] == "employee"]
            current_selected_employee_payment = None
            if not employee_options_payment: st.warning("No employees available.")
            else:
                if "payment_goal_sel_emp_2025_q" not in st.session_state or st.session_state.payment_goal_sel_emp_2025_q not in employee_options_payment:
                    st.session_state.payment_goal_sel_emp_2025_q = employee_options_payment[0]
                try: emp_radio_idx_payment = employee_options_payment.index(st.session_state.payment_goal_sel_emp_2025_q)
                except ValueError: emp_radio_idx_payment = 0; st.session_state.payment_goal_sel_emp_2025_q = employee_options_payment[0] if employee_options_payment else None
                
                selected_emp_radio_payment = st.radio("Select Employee:", employee_options_payment, index=emp_radio_idx_payment, key="payment_goal_emp_radio_2025_q", horizontal=True)
                if st.session_state.payment_goal_sel_emp_2025_q != selected_emp_radio_payment:
                    st.session_state.payment_goal_sel_emp_2025_q = selected_emp_radio_payment
                current_selected_employee_payment = st.session_state.payment_goal_sel_emp_2025_q

            quarter_options_payment = [f"{TARGET_PAYMENT_YEAR}-Q{i}" for i in range(1, 5)]
            current_selected_period_payment = None
            if not quarter_options_payment: st.error("Quarter options list empty!")
            else:
                default_period_payment = get_quarter_str_for_year(TARGET_PAYMENT_YEAR, use_current_moment=True)
                if "payment_goal_target_period_2025_q" not in st.session_state or st.session_state.payment_goal_target_period_2025_q not in quarter_options_payment:
                    st.session_state.payment_goal_target_period_2025_q = default_period_payment if default_period_payment in quarter_options_payment else quarter_options_payment[0]
                try: period_radio_idx_payment = quarter_options_payment.index(st.session_state.payment_goal_target_period_2025_q)
                except ValueError: period_radio_idx_payment = quarter_options_payment.index(default_period_payment) if default_period_payment in quarter_options_payment else 0; st.session_state.payment_goal_target_period_2025_q = quarter_options_payment[period_radio_idx_payment]
                
                selected_period_radio_payment = st.radio(f"Goal Period ({TARGET_PAYMENT_YEAR} - Quarter):", options=quarter_options_payment, index=period_radio_idx_payment, key="payment_goal_period_radio_2025_q", horizontal=True)
                if st.session_state.payment_goal_target_period_2025_q != selected_period_radio_payment:
                    st.session_state.payment_goal_target_period_2025_q = selected_period_radio_payment
                current_selected_period_payment = st.session_state.payment_goal_target_period_2025_q
            
            if current_selected_employee_payment and current_selected_period_payment:
                existing_p_goal = payment_goals_df[(payment_goals_df["Username"].astype(str) == str(current_selected_employee_payment)) & (payment_goals_df["MonthYear"].astype(str) == str(current_selected_period_payment))]
                p_desc, p_target, p_achieved, p_status_val = "", 0.0, 0.0, "Not Started"
                if not existing_p_goal.empty:
                    p_g_data = existing_p_goal.iloc[0]
                    p_desc = p_g_data.get("GoalDescription", "")
                    raw_p_target = p_g_data.get("TargetAmount"); p_target = 0.0 if pd.isna(raw_p_target) else (0.0 if pd.isna(pd.to_numeric(raw_p_target, errors='coerce')) else float(pd.to_numeric(raw_p_target, errors='coerce')))
                    raw_p_achieved = p_g_data.get("AchievedAmount"); p_achieved = 0.0 if pd.isna(raw_p_achieved) else (0.0 if pd.isna(pd.to_numeric(raw_p_achieved, errors='coerce')) else float(pd.to_numeric(raw_p_achieved, errors='coerce')))
                    p_status_val = p_g_data.get("Status", "Not Started")
                    st.info(f"Editing payment collection goal for {current_selected_employee_payment} for {current_selected_period_payment}.")

                form_key_payment = f"set_payment_goal_form_{current_selected_employee_payment}_{current_selected_period_payment}_2025q"
                with st.form(key=form_key_payment):
                    new_p_desc = st.text_area("Payment Goal Description:", value=p_desc, key=f"desc_payment_2025q_{current_selected_employee_payment}_{current_selected_period_payment}")
                    new_p_target = st.number_input("Target Collection (INR):", value=p_target, min_value=0.0, step=1000.0, format="%.2f", key=f"target_payment_2025q_{current_selected_employee_payment}_{current_selected_period_payment}")
                    new_p_achieved = st.number_input("Amount Collected (INR):", value=p_achieved, min_value=0.0, step=100.0, format="%.2f", key=f"achieved_payment_2025q_{current_selected_employee_payment}_{current_selected_period_payment}")
                    status_radio_idx_payment = status_options_payment.index(p_status_val) if p_status_val in status_options_payment else 0
                    new_p_status = st.radio("Status:", options=status_options_payment, index=status_radio_idx_payment, key=f"status_payment_radio_{current_selected_employee_payment}_{current_selected_period_payment}", horizontal=True)
                    submitted_payment = st.form_submit_button("Save Payment Goal")

                if submitted_payment:
                    if not new_p_desc.strip(): st.warning("Description needed.")
                    elif new_p_target <= 0 and new_p_status not in ["Cancelled", "On Hold", "Not Started"]: st.warning("Target > 0 unless status is Cancelled/On Hold/Not Started.")
                    else:
                        if not existing_p_goal.empty:
                            payment_goals_df.loc[existing_p_goal.index[0]] = [current_selected_employee_payment, current_selected_period_payment, new_p_desc, new_p_target, new_p_achieved, new_p_status]
                            msg_verb="updated"
                        else:
                            new_p_entry_data = {"Username": current_selected_employee_payment, "MonthYear": current_selected_period_payment, "GoalDescription": new_p_desc,
                                                "TargetAmount": new_p_target, "AchievedAmount": new_p_achieved, "Status": new_p_status}
                            for col_name in PAYMENT_GOALS_COLUMNS:
                                if col_name not in new_p_entry_data: new_p_entry_data[col_name] = pd.NA
                            new_p_entry = pd.DataFrame([new_p_entry_data], columns=PAYMENT_GOALS_COLUMNS)
                            payment_goals_df = pd.concat([payment_goals_df, new_p_entry], ignore_index=True)
                            msg_verb="set"
                        try:
                            payment_goals_df.to_csv(PAYMENT_GOALS_FILE, index=False)
                            st.session_state.user_message = f"Payment goal for {current_selected_employee_payment} ({current_selected_period_payment}) {msg_verb}!"
                            st.session_state.message_type = "success"; st.rerun()
                        except Exception as e:
                            st.session_state.user_message = f"Error saving payment goal: {e}"
                            st.session_state.message_type = "error"; st.rerun()
    else: # Employee Payment Collection Goal View
        st.markdown("<h4>My Payment Collection Goals (2025 - Quarterly)</h4>", unsafe_allow_html=True)
        my_all_payment_goals = payment_goals_df[payment_goals_df["Username"].astype(str) == str(current_user["username"])].copy()
        if not my_all_payment_goals.empty:
            for col_n in ["TargetAmount", "AchievedAmount"]: my_all_payment_goals[col_n] = pd.to_numeric(my_all_payment_goals[col_n], errors='coerce').fillna(0.0)

        current_p_goal_emp = my_all_payment_goals[my_all_payment_goals["MonthYear"].astype(str) == str(current_quarter_for_payment_display)]
        st.markdown(f"<h5>Current Collection Period: {current_quarter_for_payment_display}</h5>", unsafe_allow_html=True)
        if not current_p_goal_emp.empty:
            p_g_e = current_p_goal_emp.iloc[0]
            p_target_amt = pd.to_numeric(p_g_e.get("TargetAmount"), errors='coerce').fillna(0.0)
            p_achieved_amt = pd.to_numeric(p_g_e.get("AchievedAmount"), errors='coerce').fillna(0.0)
            p_prog_val = min(p_achieved_amt / p_target_amt, 1.0) if p_target_amt > 0 else 0.0
            st.markdown(f"**Description:** {p_g_e.get('GoalDescription', 'N/A')}")
            pc1,pc2,pc3 = st.columns(3)
            pc1.metric("Target Collection", f"₹{p_target_amt:,.0f}"); pc2.metric("Amount Collected", f"₹{p_achieved_amt:,.0f}")
            with pc3: st.metric("Status", p_g_e.get('Status','In Progress')); st.progress(p_prog_val); st.caption(f"{p_prog_val*100:.1f}% Collected")
            st.markdown("---")
            st.markdown(f"<h6>Update My Collection for {current_quarter_for_payment_display}</h6>", unsafe_allow_html=True)
            with st.form(key=f"update_payment_ach_form_{current_user['username']}_2025q"):
                new_p_ach_val = st.number_input("My Total Amount Collected (INR):", value=float(p_achieved_amt), min_value=0.0, step=100.0, format="%.2f", key=f"emp_payment_ach_update_{current_quarter_for_payment_display}")
                submit_upd_payment = st.form_submit_button("Update Amount Collected")
            if submit_upd_payment:
                idx_to_update_payment = current_p_goal_emp.index[0]
                payment_goals_df.loc[idx_to_update_payment, "AchievedAmount"] = new_p_ach_val
                payment_goals_df.loc[idx_to_update_payment, "Status"] = "Collection Complete" if new_p_ach_val >= p_target_amt and p_target_amt > 0 else "Collection In Progress"
                try:
                    payment_goals_df.to_csv(PAYMENT_GOALS_FILE, index=False)
                    st.session_state.user_message = "Collected amount updated!"
                    st.session_state.message_type = "success"; st.rerun()
                except Exception as e:
                    st.session_state.user_message = f"Error updating collected amount: {e}"
                    st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No payment collection goal set for you for {current_quarter_for_payment_display}. Contact admin.")

        st.markdown("---")
        st.markdown("<h5>My Payment Collection Visualized (2025)</h5>", unsafe_allow_html=True)
        employee_payment_goals_2025 = my_all_payment_goals[my_all_payment_goals["MonthYear"].astype(str).str.startswith(str(TARGET_PAYMENT_YEAR))]
        if not employee_payment_goals_2025.empty:
            render_goal_chart(employee_payment_goals_2025, f"{current_user['username']}'s Payment Collection vs Target {TARGET_PAYMENT_YEAR}")
        else:
            st.info(f"No payment collection data to visualize for {TARGET_PAYMENT_YEAR}.")

        st.markdown("---")
        st.markdown("<h5>My Past Payment Collection Goals (2025)</h5>", unsafe_allow_html=True)
        past_p_goals = my_all_payment_goals[(my_all_payment_goals["MonthYear"].astype(str).str.startswith(str(TARGET_PAYMENT_YEAR))) & (my_all_payment_goals["MonthYear"].astype(str) != str(current_quarter_for_payment_display))].sort_values(by="MonthYear", ascending=False)
        if not past_p_goals.empty:
            st.dataframe(past_p_goals[["MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]], hide_index=True, use_container_width=True,
                         column_config={"TargetAmount":st.column_config.NumberColumn(format="₹%.0f"), "AchievedAmount":st.column_config.NumberColumn(format="₹%.0f")})
        else: st.info(f"No past payment collection goal records found for {TARGET_PAYMENT_YEAR} (excluding current quarter).")
    st.markdown('</div>', unsafe_allow_html=True)


elif nav == "📊 View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if current_user["role"] == "admin":
        st.markdown("<h3>📊 Employee Data Logs</h3>", unsafe_allow_html=True) # Use h3 from card styling
        employee_names = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
        if not employee_names: st.info("No employees found or no employee data to display.")
        else:
            for emp_name in employee_names:
                user_info = USERS.get(emp_name, {})
                profile_col1, profile_col2 = st.columns([1, 4])
                with profile_col1:
                    if user_info.get("profile_photo") and os.path.exists(user_info.get("profile_photo")):
                        st.image(user_info.get("profile_photo"), width=80)
                with profile_col2:
                    st.markdown(f"<h4 class='employee-section-header' style='margin-bottom: 5px; margin-top:0px; border-bottom: none; font-size: 1.2em;'>👤 {emp_name}</h4>", unsafe_allow_html=True)
                    st.markdown(f"**Position:** {user_info.get('position', 'N/A')}")
                st.markdown("---")

                # Attendance
                st.markdown("<h5 class='record-type-header'>🕒 Attendance Records:</h5>", unsafe_allow_html=True)
                emp_attendance = attendance_df[attendance_df["Username"].astype(str) == str(emp_name)].copy()
                if not emp_attendance.empty:
                    display_cols_att = [col for col in ATTENDANCE_COLUMNS if col != 'Username']
                    admin_att_display = emp_attendance[display_cols_att].copy()
                    for col_name_map in ['Latitude', 'Longitude']:
                        if col_name_map in admin_att_display.columns:
                            admin_att_display[col_name_map] = pd.to_numeric(admin_att_display[col_name_map], errors='coerce').apply(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")
                    st.dataframe(admin_att_display, use_container_width=True, hide_index=True)
                    # Map - Geolocation is disabled, so map won't show relevant data
                    # st.markdown("<h6 class='allowance-summary-header'>🗺️ Attendance Locations Map:</h6>", unsafe_allow_html=True)
                    # map_data_admin = emp_attendance.dropna(subset=['Latitude', 'Longitude']).copy() # This will be empty
                    # if not map_data_admin.empty: st.map(map_data_admin.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'}))
                    # else: st.caption(f"No location data for map for {emp_name} (geolocation disabled).")
                else: st.caption(f"No attendance records for {emp_name}.")

                # Allowances
                st.markdown("<h5 class='record-type-header' style='margin-top:25px;'>💰 Allowance Section:</h5>", unsafe_allow_html=True)
                emp_allowances = allowance_df[allowance_df["Username"].astype(str) == str(emp_name)].copy()
                if not emp_allowances.empty:
                    emp_allowances['Amount'] = pd.to_numeric(emp_allowances['Amount'], errors='coerce').fillna(0.0)
                    st.metric(label=f"Grand Total Allowance for {emp_name}", value=f"₹{emp_allowances['Amount'].sum():,.2f}")
                    st.markdown("<h6 class='allowance-summary-header'>📅 Monthly Allowance Summary:</h6>", unsafe_allow_html=True)
                    emp_allow_sum = emp_allowances.dropna(subset=['Amount']).copy()
                    if 'Date' in emp_allow_sum.columns:
                        emp_allow_sum['Date'] = pd.to_datetime(emp_allow_sum['Date'], errors='coerce')
                        emp_allow_sum.dropna(subset=['Date'], inplace=True) # Remove rows with invalid dates
                    if not emp_allow_sum.empty and 'Date' in emp_allow_sum.columns:
                        emp_allow_sum['YearMonth'] = emp_allow_sum['Date'].dt.strftime('%Y-%m')
                        monthly_summary = emp_allow_sum.groupby('YearMonth')['Amount'].sum().reset_index().sort_values('YearMonth', ascending=False)
                        st.dataframe(monthly_summary.rename(columns={'Amount': 'Total Amount (₹)', 'YearMonth': 'Month'}), use_container_width=True, hide_index=True)
                    else: st.caption("No valid allowance data for monthly summary.")
                    st.markdown("<h6 class='allowance-summary-header' style='margin-top:20px;'>📋 Detailed Allowance Requests:</h6>", unsafe_allow_html=True)
                    st.dataframe(emp_allowances[[c for c in ALLOWANCE_COLUMNS if c != 'Username']], use_container_width=True, hide_index=True)
                else: st.caption(f"No allowance requests for {emp_name}.")
                
                # Sales Goals for this employee
                st.markdown("<h5 class='record-type-header' style='margin-top:25px;'>🎯 Sales Goal History (2025):</h5>", unsafe_allow_html=True)
                emp_sales_goals_all = goals_df[(goals_df["Username"].astype(str) == str(emp_name)) & (goals_df["MonthYear"].astype(str).str.startswith(str(TARGET_SALES_GOAL_YEAR)))].copy()
                if not emp_sales_goals_all.empty:
                    for col_n in ["TargetAmount", "AchievedAmount"]: emp_sales_goals_all[col_n] = pd.to_numeric(emp_sales_goals_all[col_n], errors='coerce').fillna(0.0)
                    st.dataframe(emp_sales_goals_all[["MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]], hide_index=True, use_container_width=True,
                                 column_config={"TargetAmount":st.column_config.NumberColumn(format="₹%.0f"), "AchievedAmount":st.column_config.NumberColumn(format="₹%.0f")})
                    render_goal_chart(emp_sales_goals_all, f"{emp_name}'s Sales Goals vs Achievement {TARGET_SALES_GOAL_YEAR}")
                else:
                    st.caption(f"No sales goals found for {emp_name} for {TARGET_SALES_GOAL_YEAR}.")

                # Payment Collection Goals for this employee
                st.markdown("<h5 class='record-type-header' style='margin-top:25px;'>💰 Payment Collection Goal History (2025):</h5>", unsafe_allow_html=True)
                emp_payment_goals_all = payment_goals_df[(payment_goals_df["Username"].astype(str) == str(emp_name)) & (payment_goals_df["MonthYear"].astype(str).str.startswith(str(TARGET_PAYMENT_YEAR)))].copy()
                if not emp_payment_goals_all.empty:
                    for col_n in ["TargetAmount", "AchievedAmount"]: emp_payment_goals_all[col_n] = pd.to_numeric(emp_payment_goals_all[col_n], errors='coerce').fillna(0.0)
                    st.dataframe(emp_payment_goals_all[["MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]], hide_index=True, use_container_width=True,
                                 column_config={"TargetAmount":st.column_config.NumberColumn("Target Coll. (₹)", format="%.0f"), "AchievedAmount":st.column_config.NumberColumn("Amt. Collected (₹)", format="%.0f")})
                    render_goal_chart(emp_payment_goals_all, f"{emp_name}'s Payment Collection vs Target {TARGET_PAYMENT_YEAR}")

                else:
                    st.caption(f"No payment collection goals found for {emp_name} for {TARGET_PAYMENT_YEAR}.")


                if emp_name != employee_names[-1]: st.markdown("<hr style='margin-top: 25px; margin-bottom:10px;'>", unsafe_allow_html=True)

    else: # Employee's Own View
        st.markdown("<h3>📊 My Profile & Logs</h3>", unsafe_allow_html=True)
        my_user_info = USERS.get(current_user["username"], {})
        profile_col1_my, profile_col2_my = st.columns([1, 4])
        with profile_col1_my:
            if my_user_info.get("profile_photo") and os.path.exists(my_user_info.get("profile_photo")):
                st.image(my_user_info.get("profile_photo"), width=80)
        with profile_col2_my:
            st.markdown(f"**Name:** {current_user['username']}")
            st.markdown(f"**Position:** {my_user_info.get('position', 'N/A')}")
        st.markdown("---")

        st.markdown("<h4 class='record-type-header'>📅 My Attendance History</h4>", unsafe_allow_html=True)
        my_att_raw = attendance_df[attendance_df["Username"].astype(str) == str(current_user["username"])].copy()
        final_display_df = pd.DataFrame()
        my_att_proc = pd.DataFrame()

        if not my_att_raw.empty:
            my_att_proc = my_att_raw.copy()
            my_att_proc['Timestamp'] = pd.to_datetime(my_att_proc['Timestamp'], errors='coerce')
            my_att_proc.dropna(subset=['Timestamp'], inplace=True)
            if not my_att_proc.empty:
                my_att_proc['Latitude'] = pd.to_numeric(my_att_proc['Latitude'], errors='coerce')
                my_att_proc['Longitude'] = pd.to_numeric(my_att_proc['Longitude'], errors='coerce')
                my_att_proc['DateOnly'] = my_att_proc['Timestamp'].dt.date
                check_ins_df = my_att_proc[my_att_proc['Type'] == 'Check-In'].copy()
                check_outs_df = my_att_proc[my_att_proc['Type'] == 'Check-Out'].copy()
                first_check_in_cols = ['DateOnly', 'Check-In FullTime', 'Check-In Latitude', 'Check-In Longitude']
                first_check_ins_sel = pd.DataFrame(columns=first_check_in_cols)
                if not check_ins_df.empty:
                    first_check_ins_grouped = check_ins_df.loc[check_ins_df.groupby('DateOnly')['Timestamp'].idxmin()]
                    first_check_ins_sel = first_check_ins_grouped[['DateOnly', 'Timestamp', 'Latitude', 'Longitude']].rename(
                        columns={'Timestamp': 'Check-In FullTime', 'Latitude': 'Check-In Latitude', 'Longitude': 'Check-In Longitude'})
                last_check_out_cols = ['DateOnly', 'Check-Out FullTime', 'Check-Out Latitude', 'Check-Out Longitude']
                last_check_outs_sel = pd.DataFrame(columns=last_check_out_cols)
                if not check_outs_df.empty:
                    last_check_outs_grouped = check_outs_df.loc[check_outs_df.groupby('DateOnly')['Timestamp'].idxmax()]
                    last_check_outs_sel = last_check_outs_grouped[['DateOnly', 'Timestamp', 'Latitude', 'Longitude']].rename(
                        columns={'Timestamp': 'Check-Out FullTime', 'Latitude': 'Check-Out Latitude', 'Longitude': 'Check-Out Longitude'})
                for df_sel in [first_check_ins_sel, last_check_outs_sel]:
                    if 'DateOnly' in df_sel.columns and not df_sel.empty:
                        df_sel['DateOnly'] = pd.to_datetime(df_sel['DateOnly']).dt.date
                if not first_check_ins_sel.empty and not last_check_outs_sel.empty: combined_df = pd.merge(first_check_ins_sel, last_check_outs_sel, on='DateOnly', how='outer')
                elif not first_check_ins_sel.empty:
                    combined_df = first_check_ins_sel.copy()
                    for col_name_c in last_check_out_cols[1:]:
                        if 'Time' in col_name_c: combined_df[col_name_c] = pd.NaT
                        else: combined_df[col_name_c] = pd.NA
                elif not last_check_outs_sel.empty:
                    combined_df = last_check_outs_sel.copy()
                    for col_name_c in first_check_in_cols[1:]:
                        if 'Time' in col_name_c: combined_df[col_name_c] = pd.NaT
                        else: combined_df[col_name_c] = pd.NA
                else:
                    all_combined_cols = list(dict.fromkeys(first_check_in_cols + last_check_out_cols))
                    combined_df = pd.DataFrame(columns=all_combined_cols)

                if not combined_df.empty:
                    combined_df = combined_df.sort_values(by='DateOnly', ascending=False, ignore_index=True)
                    for ft_col in ['Check-In FullTime', 'Check-Out FullTime']:
                        if ft_col in combined_df.columns: combined_df[ft_col] = pd.to_datetime(combined_df[ft_col], errors='coerce')
                    def format_duration(row):
                        if pd.notna(row.get('Check-In FullTime')) and pd.notna(row.get('Check-Out FullTime')) and row['Check-Out FullTime'] > row['Check-In FullTime']:
                            secs = (row['Check-Out FullTime'] - row['Check-In FullTime']).total_seconds(); return f"{int(secs//3600)}h {int((secs%3600)//60)}m"
                        return "N/A"
                    combined_df['Duration'] = combined_df.apply(format_duration, axis=1)
                    for t_col, new_name in [('Check-In FullTime', 'Check-In Time'), ('Check-Out FullTime', 'Check-Out Time')]:
                        combined_df[new_name] = combined_df.get(t_col, pd.Series(dtype='datetime64[ns]')).apply(lambda x: x.strftime('%H:%M:%S') if pd.notna(x) else 'N/A')
                    combined_df['Date'] = combined_df.get('DateOnly', pd.Series(dtype='object')).apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else 'N/A')
                    final_cols = ['Date', 'Check-In Time', 'Check-In Latitude', 'Check-In Longitude', 'Check-Out Time', 'Check-Out Latitude', 'Check-Out Longitude', 'Duration']
                    final_display_df = combined_df[[c for c in final_cols if c in combined_df.columns]].copy()
                    final_display_df.rename(columns={'Check-In Time': 'Check-In', 'Check-In Latitude': 'In Lat', 'Check-In Longitude': 'In Lon', 'Check-Out Time': 'Check-Out', 'Check-Out Latitude': 'Out Lat', 'Check-Out Longitude': 'Out Lon'}, inplace=True)
                    for loc_col in ['In Lat', 'In Lon', 'Out Lat', 'Out Lon']:
                        if loc_col in final_display_df.columns: final_display_df[loc_col] = final_display_df[loc_col].apply(lambda x: f"{x:.4f}" if pd.notna(x) and isinstance(x, (float,int)) else ("N/A" if pd.isna(x) else str(x)))
        if not final_display_df.empty: st.dataframe(final_display_df, use_container_width=True, hide_index=True)
        elif my_att_raw.empty: st.info("You have no attendance records yet.")
        else: st.info("No processed attendance data (check timestamp formats).")

        # Map disabled as geolocation is disabled
        # st.markdown("<h6 class='allowance-summary-header'>🗺️ My Attendance Locations Map:</h6>", unsafe_allow_html=True)
        # if not my_att_proc.empty:
        #     my_map_data = my_att_proc.dropna(subset=['Latitude', 'Longitude']).copy()
        #     if not my_map_data.empty: st.map(my_map_data.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'}))
        #     else: st.info("No valid location data for map.")
        # elif my_att_raw.empty: st.info("No attendance records for map.")
        # else: st.info("No valid attendance data with locations for map (geolocation disabled).")

        st.markdown("<h4 class='record-type-header' style='margin-top:25px;'>🧾 My Allowance Request History</h4>", unsafe_allow_html=True)
        my_allowances = allowance_df[allowance_df["Username"].astype(str) == str(current_user["username"])].copy()
        if not my_allowances.empty: st.dataframe(my_allowances[[c for c in ALLOWANCE_COLUMNS if c != 'Username' and c in my_allowances.columns]], use_container_width=True, hide_index=True)
        else: st.info("You have not submitted any allowance requests yet.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- REMOVE ORPHANED BADGE LINES ---
# status_badge = f"<span class='badge {badge_color}'>{status}</span>" # This line was causing NameError
# st.markdown(f"Status: {status_badge}", unsafe_allow_html=True)     # This line was causing NameError
# badge_color = "green" if status == "Achieved" else "orange" if status == "In Progress" else "red" # This line was causing NameError
