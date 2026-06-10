# --- LIBRARIES ---
import streamlit as st
import itertools
from itertools import product
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- APP LAYOUT CREATION ---
st.header("UNCERTAINTY INTERVAL CALCULATOR")
st.page_link("https://github.com/labMEQ/unctool/blob/main/README.md", label = "About and instructions of use", use_container_width = True)

## --- Lateral bar construction ---

### Lateral bar title
st.sidebar.subheader("Simulation parameters")

### Container 1: "Analytical criteria"
container_1 = st.sidebar.container()

with container_1:
    st.write("Analytical criteria")
    low_rec_selected, upp_rec_selected = st.sidebar.slider("Recovery range (%)", 30, 150, (98, 102))
    prec_values = st.sidebar.slider("Precision value (%)", 0, 50, 2)
    real_mean_value = st.number_input("Mean value", value = 100.00, format="%0.2f")
    real_std_value = st.number_input("Standard deviation", value = 5.00, format="%0.2f")

### Container 2: "Simulation parameters"
container_2 = st.sidebar.container()

with container_2:
    st.write("Simulation parameters")
    sim_number = st.number_input("Number of simulations", value = 1000000)
    data_used = st.pills("Simulation model", ["All simulations", "Non-negative simulations"], selection_mode = "single", default = ["Non-negative simulations"])
    uct_model = st.pills("Uncertainty model", ["Symmetrical", "Asymmetrical"], selection_mode = "multi") 

### Container 3: "Graph properties"
container_3 = st.sidebar.container()

with container_3:
    st.write("Graph properties")
    graph_axis = st.selectbox("Graph axis", 
            ["Recovery (%) x Precision (%)",
            "Bias (%) x Precision (%)"])

### Container 4: "Run simulation"
container_4 = st.sidebar.container()

with container_4:
   run_command = st.button("Run simulation", type = "primary", use_container_width = True)

## --- Right panel ---

### Arithmetic progression function
def arithmetic_progression(recovery_low = low_rec_selected, 
                           recovery_upp = upp_rec_selected, 
                           precision_limit = prec_values):
    
#### Arithmetic progression parameters
    A_rec = recovery_low
    D_rec = (recovery_upp - recovery_low)/9
    A_prec = 0.1*precision_limit
    D_prec = precision_limit/10

#### Definion of lists to store values
    rec_list = []
    prec_list = []

#### Arithmetric progression
    for i in range(10):
        rec_value = A_rec + ((i)*D_rec)
        prec_value= A_prec + ((i) * D_prec)
        rec_list.append(round(rec_value, 1))
        prec_list.append(round(prec_value, 1))
        
    return (rec_list, prec_list)

# Combining precision and recovery values function

def combination(rec_list, prec_list):

    values_list = list(itertools.product(rec_list, prec_list))
    return values_list

# Monte Carlo simulations coding

## Symmetric
def monte_carlo_symmetric(
    real_mean=100.00,
    real_std_dv=5.00,
    mean_rec=85.00,
    mean_prec=0.00,
    u_prec=25.00,
    simulation_n = 1000000
):

# Additional calculation for recovery
    
    c_mean_rec = (mean_rec - 100) # Bias estimation
    u_rec = (u_prec * mean_rec)/100 # Recovery uncertainty estimation
    
# MONTE CARLO SIMULATION
# Simulated data generation

    real_value = np.random.normal(real_mean, real_std_dv, size= simulation_n)
    rec_error = np.random.normal((mean_rec - 100), u_rec, size= simulation_n)
    prec_error = np.random.normal(0.00, u_prec, size= simulation_n)
    meas_value = real_value + rec_error + prec_error

# Symmetric simulation
    
## Symmetric confidence intervals

    symmetric_int_low = -2 * np.sqrt((c_mean_rec**2 + u_rec**2 + u_prec**2))
    symmetric_int_upp = 2 * np.sqrt((c_mean_rec**2 + u_rec**2 + u_prec**2))

# Simulated values ~ symmetric interval

    sym_low_lim = meas_value + symmetric_int_low
    sym_upp_lim = meas_value + symmetric_int_upp

# Conditional logic test
    
    low_sym = np.where(sym_low_lim < 0, np.nan, sym_low_lim)

# Comparison of real values and confidence intervals

    sym_in = np.sum((real_value >= low_sym) & (real_value <= sym_upp_lim) & (~np.isnan(low_sym)))
    sym_NA = np.sum(np.isnan(low_sym))
    sym_out = simulation_n - sym_NA - sym_in

# Coverage estimation 

    # simulations used (non-NA)
    simulation_used_sym = (simulation_n - sym_NA)

    sym_included = (sym_in / simulation_n * 100) # symmetric simulations that include real_value (%)
    sym_not_included = (sym_out / simulation_n * 100) # symmetric simulations that do not include real_value (%)
    sym_below_zero = (sym_NA / simulation_n * 100) # symmetric simulations with negative interval (lower limit <0) (%)

    sym_used_included = (sym_in / simulation_used_sym * 100) # symmetric simulations that include real_value (%), without NA intervals
    sym_used_not_included = (sym_out / simulation_used_sym * 100) # symmetric simulations that do not include real_value (%), without NA intervals

# Dataframe sym

    symmetric_df = pd.DataFrame({
        "REC (%)": [mean_rec],
        "PREC (%)": [u_prec],
        "Abrang (%) 1": [sym_included],
        "Abrang (%) 2": [sym_used_included],
        "Fora (%) 1": [sym_not_included],
        "Fora (%) 2": [sym_used_not_included],
        "NA (%)": [sym_below_zero],
        "Sim (n)": [simulation_used_sym],
        "IN (n)": [sym_in],
        "OUT (n)": [sym_out],
        "NA (n)": [sym_NA],
        "LI": [symmetric_int_low],
        "LS": [symmetric_int_upp]
    })
    
    return symmetric_df

## Asymmetric
def monte_carlo_asymmetric(
    real_mean=100.00,
    real_std_dv=5.00,
    mean_rec=85.00,
    mean_prec=0.00,
    u_prec=25.00,
    simulation_n = 1000000
):

# Additional calculations for recovery
    
    c_mean_rec = (mean_rec - 100) # Bias estimation
    u_rec = (u_prec * mean_rec)/100 # Recovery uncertainty estimation
    
# MONTE CARLO SIMULATION
# Simulated data generation

    real_value = np.random.normal(real_mean, real_std_dv, size= simulation_n)
    rec_error = np.random.normal((mean_rec - 100), u_rec, size= simulation_n)
    prec_error = np.random.normal(0.00, u_prec, size= simulation_n)
    meas_value = real_value + rec_error + prec_error

## Asymmetric confidence intervals
    asymmetric_int_low = -2 * np.sqrt((u_rec**2 + u_prec**2)) - (c_mean_rec)
    asymmetric_int_upp = 2 * np.sqrt((u_rec**2 + u_prec**2)) - (c_mean_rec)
    
# Simulated data ~ asymmetric interval
    
    asym_low_lim = meas_value + asymmetric_int_low
    asym_upp_lim = meas_value + asymmetric_int_upp

# Conditional logic test
    
    low_asym = np.where(asym_low_lim < 0, np.nan, asym_low_lim)

# Comparison of real values anda confidence intervals
    
    asym_in = np.sum((real_value >= low_asym) & (real_value <= asym_upp_lim) & (~np.isnan(low_asym)))
    asym_NA = np.sum(np.isnan(low_asym))
    asym_out = simulation_n - asym_NA - asym_in
    
# Coverage estimation

    # simulations used (non-NA)
    simulation_used_asym = (simulation_n - asym_NA)
    
    asym_included = (asym_in / simulation_n * 100) # asymmetric simulations that include real_value (%)
    asym_not_included = (asym_out / simulation_n * 100) # asymmetric simulations that do not include real_value (%)
    asym_below_zero = (asym_NA / simulation_n * 100) # asymmetric simulations with negative interval (lower limit <0) (%)

    asym_used_included = (asym_in / simulation_used_asym * 100) # asymmetric simulations that include real_value (%) without NA cases
    asym_used_not_included = (asym_out / simulation_used_asym * 100) # asymmetric simulations that do not include real_value (%) without NA cases
    
# Dataframe

    asymmetric_df = pd.DataFrame({
        "REC (%)": [mean_rec],
        "PREC (%)": [u_prec],
        "Abrang (%) 1": [asym_included],
        "Abrang (%) 2": [asym_used_included],
        "Fora (%) 1": [asym_not_included],
        "Fora (%) 2": [asym_used_not_included],
        "NA (%)": [asym_below_zero],
        "Assim (n)": [simulation_used_asym],
        "IN (n)": [asym_in],
        "OUT (n)": [asym_out],
        "NA (n)": [asym_NA],
        "LI": [asymmetric_int_low],
        "LS": [asymmetric_int_upp]
    })

    return asymmetric_df

# --- SIMULATION AND RESULTS ---
if run_command:
    
## Arithmetic progression calculation
    rec_list, prec_list = arithmetic_progression()

## Combination of arithmetric progression lists
    combination_list = combination(rec_list, prec_list)

## Monte Carlo for each lists

### Symmetric

    Symmetric_heatmap_results = [] # Creating an empty list to store results

    for mean_rec, u_prec in combination_list: # MCS loop for list (mean_rec, u_prec)
        sym_result_df = monte_carlo_symmetric(
            real_mean = real_mean_value,
            real_std_dv = real_std_value,
            mean_rec = mean_rec,
            u_prec = u_prec,
            simulation_n = sim_number)

        c_mean_rec = (mean_rec - 100)

        if data_used == "All simulations":
            Sym_recovery = sym_result_df["REC (%)"].values[0]
            Sym_precision = sym_result_df["PREC (%)"].values[0]            
            Sym_abrang_1 = sym_result_df["Abrang (%) 1"].values[0]
            Sym_abrang_NA = sym_result_df["NA (%)"].values[0]
            Sym_abrang_OUT_1 = sym_result_df["Fora (%) 1"].values[0]
            Sym_LI = sym_result_df["LI"].values[0]
            Sym_LS = sym_result_df["LS"].values[0]
            Symmetric_heatmap_results.append({
                    "Recovery": Sym_recovery,
                    "Precision": Sym_precision,
                    "Coverage": round(Sym_abrang_1, 2),
                    "Width": round((Sym_LS - Sym_LI), 1),
                    "Bias": round(c_mean_rec, 1),
                    "NA (%)": round(Sym_abrang_NA, 2),
                    "OUT (%)": round(Sym_abrang_OUT_1, 2)
            })

        elif data_used == "Non-negative simulations":
            Sym_recovery = sym_result_df["REC (%)"].values[0]
            Sym_precision = sym_result_df["PREC (%)"].values[0]            
            Sym_abrang_2 = sym_result_df["Abrang (%) 2"].values[0]
            Sym_abrang_NA = sym_result_df["NA (%)"].values[0]
            Sym_abrang_OUT_2 = sym_result_df["Fora (%) 2"].values[0]
            Sym_LI = sym_result_df["LI"].values[0]
            Sym_LS = sym_result_df["LS"].values[0]
            Symmetric_heatmap_results.append({
                    "Recovery": Sym_recovery,
                    "Precision": Sym_precision,
                    "Coverage": round(Sym_abrang_2, 2),
                    "Width": round((Sym_LS - Sym_LI), 1),
                    "Bias": round(c_mean_rec, 1),
                    "NA (%)": round(Sym_abrang_NA, 2),
                    "OUT (%)": round(Sym_abrang_OUT_2, 2)
            })

        sym_heatmap_df = pd.DataFrame(Symmetric_heatmap_results)

### Asymmetric

    Asymmetric_heatmap_results = [] # Creating an empty list to store results

    for mean_rec, u_prec in combination_list: # MCS loop for list (mean_rec, u_prec)
        asym_result_df = monte_carlo_asymmetric(
            real_mean = real_mean_value,
            real_std_dv = real_std_value,
            mean_rec = mean_rec,
            u_prec = u_prec,
            simulation_n = sim_number)

        c_mean_rec = (mean_rec - 100)
        
        if data_used == "All simulations":
            Asym_recovery = asym_result_df["REC (%)"].values[0]
            Asym_precision = asym_result_df["PREC (%)"].values[0]            
            Asym_abrang_1 = asym_result_df["Abrang (%) 1"].values[0]
            Asym_abrang_NA = asym_result_df["NA (%)"].values[0]
            Asym_abrang_OUT_1 = asym_result_df["Fora (%) 1"].values[0]
            Asym_LI = asym_result_df["LI"].values[0]
            Asym_LS = asym_result_df["LS"].values[0]
            Asymmetric_heatmap_results.append({
                    "Recovery": Asym_recovery,
                    "Precision": Asym_precision,
                    "Coverage": round(Asym_abrang_1, 2),
                    "Width": round((Asym_LS - Asym_LI), 1),
                    "Bias": round(c_mean_rec, 1),
                    "NA (%)": round(Asym_abrang_NA, 2),
                    "OUT (%)": round(Asym_abrang_OUT_1, 2)
            })

        elif data_used == "Non-negative simulations":
            Asym_recovery = asym_result_df["REC (%)"].values[0]
            Asym_precision = asym_result_df["PREC (%)"].values[0]            
            Asym_abrang_2 = asym_result_df["Abrang (%) 2"].values[0]
            Asym_abrang_NA = asym_result_df["NA (%)"].values[0]
            Asym_abrang_OUT_2 = asym_result_df["Fora (%) 2"].values[0]
            Asym_LI = asym_result_df["LI"].values[0]
            Asym_LS = asym_result_df["LS"].values[0]
            Asymmetric_heatmap_results.append({
                    "Recovery": Asym_recovery,
                    "Precision": Asym_precision,
                    "Coverage": round(Asym_abrang_2, 2),
                    "Width": round((Asym_LS - Asym_LI), 1),
                    "Bias": round(c_mean_rec, 1),
                    "NA (%)": round(Asym_abrang_NA, 2),
                    "OUT (%)": round(Asym_abrang_OUT_2, 2)
            })

        asym_heatmap_df = pd.DataFrame(Asymmetric_heatmap_results)

## Heatmaps

### Creating tabs:
    
    tabs = []
    
    if "Symmetrical" in uct_model:
        tabs.append("Symmetrical interval")

    if "Asymmetrical" in uct_model:
        tabs.append("Asymmetrical interval")

    if tabs:
        selected_tab = st.tabs(tabs)

        for i, tab_name in enumerate(tabs):
            with selected_tab[i]:
                
### Symmetric results

### --- symmetric - recovery (%) x precision (%):

                if tab_name == "Symmetrical interval":

                    sym_heatmap_df = sym_heatmap_df.fillna(0)
                    
                    if graph_axis == "Recovery (%) x Precision (%)":
                        Sym_hmap_coverage = sym_heatmap_df.pivot(index = "Recovery", columns = "Precision", values = "Coverage")
                        Sym_hmap_width = sym_heatmap_df.pivot(index = "Recovery", columns = "Precision", values = "Width")
                        Sym_hmap_out = sym_heatmap_df.pivot(index = "Recovery", columns = "Precision", values = "OUT (%)")
                        Sym_hmap_na = sym_heatmap_df.pivot(index = "Recovery", columns = "Precision", values = "NA (%)")
                        y_label = "Recovery (%)"
                        x_label = "Precision (%)" 
                    elif graph_axis == "Bias (%) x Precision (%)":
                        Sym_hmap_coverage = sym_heatmap_df.pivot(index = "Bias", columns = "Precision", values = "Coverage")
                        Sym_hmap_width = sym_heatmap_df.pivot(index = "Bias", columns = "Precision", values = "Width")
                        Sym_hmap_out = sym_heatmap_df.pivot(index = "Bias", columns = "Precision", values = "OUT (%)")
                        Sym_hmap_na = sym_heatmap_df.pivot(index = "Bias", columns = "Precision", values = "NA (%)")           
                        y_label = "Bias (%)"
                        x_label = "Precision (%)" 

                    customdata = np.dstack((
                        Sym_hmap_out.values,
                        Sym_hmap_na.values))

                    text = np.where(
                        Sym_hmap_na.values > 10.0,
                        np.round(Sym_hmap_coverage.values, 2).astype(str) + "∗",
                        np.round(Sym_hmap_coverage.values, 2).astype(str))

                    fig1 = go.Figure(
                        data = go.Heatmap(
                            z = Sym_hmap_coverage.values,
                            x = Sym_hmap_coverage.columns,
                            y = Sym_hmap_coverage.index,
                            text = text,
                            customdata = customdata,
                            hovertemplate = (
                                "Recovery: %{y}%<br>"
                                "Precision: %{x}%<br>"
                                "Coverage: %{z:.2f}%<br>"
                                "NA: %{customdata[1]:.2f}%"
                                "<extra></extra>"
                            ),
                            texttemplate = "%{text}",
                            colorscale = "Blues",
                            showscale = True,
                            zmax = 100.00,
                            zmin = 0.00))

                    fig2 = go.Figure(
                        data = go.Heatmap(
                            z = Sym_hmap_width.values,
                            x = Sym_hmap_width.columns,
                            y = Sym_hmap_width.index,
                            text = Sym_hmap_width.values,
                            customdata = customdata,
                            hovertemplate = (
                                "Recovery: %{y}%<br>"
                                "Precision: %{x}%<br>"
                                "Interval: %{z:.2f}%<br>"
                                "NA: %{customdata[1]:.2f}%"
                                "<extra></extra>"
                            ),
                            texttemplate = "%{text:.2f}",
                            colorscale = "Greens",
                            showscale = True))
                        
                    fig1.update_layout(
                        title = "SYMMETRIC COVERAGE LEVELS",
                        yaxis_title = y_label,
                        xaxis_title = x_label)

                    fig2.update_layout(
                        title = "SYMMETRIC INTERVAL RANGE",
                        yaxis_title = y_label,
                        xaxis_title = x_label)
                    
                    st.plotly_chart(fig1, use_container_width=True)
                    st.plotly_chart(fig2, use_container_width=True)
                    st.write("**SYMMETRIC INTERVAL DATATABLE**")
                    st.write(sym_heatmap_df)
                    
### Asymmetric results

### --- asymmetric - recovery (%) x precision (%):

                elif tab_name == "Asymmetrical interval":

                    asym_heatmap_df = asym_heatmap_df.fillna(0)
                    
                    if graph_axis == "Recovery (%) x Precision (%)":
                        Asym_hmap_coverage = asym_heatmap_df.pivot(index = "Recovery", columns = "Precision", values = "Coverage")
                        Asym_hmap_width = asym_heatmap_df.pivot(index = "Recovery", columns = "Precision", values = "Width")
                        Asym_hmap_out = asym_heatmap_df.pivot(index = "Recovery", columns = "Precision", values = "OUT (%)")
                        Asym_hmap_na = asym_heatmap_df.pivot(index = "Recovery", columns = "Precision", values = "NA (%)")
                        y_label = "Recovery (%)"
                        x_label = "Precision (%)" 
                    elif graph_axis == "Bias (%) x Precision (%)":
                        Asym_hmap_coverage = asym_heatmap_df.pivot(index = "Bias", columns = "Precision", values = "Coverage")
                        Asym_hmap_width = asym_heatmap_df.pivot(index = "Bias", columns = "Precision", values = "Width")
                        Asym_hmap_out = asym_heatmap_df.pivot(index = "Bias", columns = "Precision", values = "OUT (%)")
                        Asym_hmap_na = asym_heatmap_df.pivot(index = "Bias", columns = "Precision", values = "NA (%)")
                        y_label = "Bias (%)"
                        x_label = "Precision (%)" 

                    customdata = np.dstack((
                        Asym_hmap_out.values,
                        Asym_hmap_na.values))
                    
                    text = np.where(
                        Asym_hmap_na.values > 10.0,
                        np.round(Asym_hmap_coverage.values, 2).astype(str) + "∗",
                        np.round(Asym_hmap_coverage.values, 2).astype(str))

                    fig3 = go.Figure(
                        data = go.Heatmap(
                            z = Asym_hmap_coverage.values,
                            x = Asym_hmap_coverage.columns,
                            y = Asym_hmap_coverage.index,
                            text = text,
                            customdata = customdata,
                            hovertemplate = (
                                "Recovery: %{y}%<br>"
                                "Precision: %{x}%<br>"
                                "Coverage: %{z:.2f}%<br>"
                                "NA: %{customdata[1]:.2f}%"
                                "<extra></extra>"
                            ),
                            texttemplate = "%{text}",
                            colorscale = "Blues",
                            showscale = True,
                            zmax = 100.00,
                            zmin = 0.00))

                    fig4 = go.Figure(
                        data = go.Heatmap(
                            z = Asym_hmap_width.values,
                            x = Asym_hmap_width.columns,
                            y = Asym_hmap_width.index,
                            text = Asym_hmap_width.values,
                            customdata = customdata,
                            hovertemplate = (
                                "Recovery: %{y}%<br>"
                                "Precision: %{x}%<br>"
                                "Interval: %{z:.2f}%<br>"
                                "NA: %{customdata[1]:.2f}%"
                                "<extra></extra>"
                            ),
                            texttemplate = "%{text:.2f}",
                            colorscale = "Greens",
                            showscale = True))
                    
                    fig3.update_layout(
                        title = "ASYMMETRIC COVERAGE LEVELS",
                        yaxis_title = y_label,
                        xaxis_title = x_label)
                    
                    fig4.update_layout(
                        title = "ASYMMETRIC INTERVAL RANGE",
                        yaxis_title = y_label,
                        xaxis_title = x_label)
                    
                    st.plotly_chart(fig3, use_container_width=True)
                    st.plotly_chart(fig4, use_container_width=True)
                    st.write("**ASYMMETRIC INTERVAL DATATABLE**")
                    st.write(asym_heatmap_df)
