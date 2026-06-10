# unctool
The app can be accessed at https://labmeq-app-unctool.streamlit.app/

ABOUT THE APP

Streamlit app for measurement uncertainty evaluation by a top-down approach. This app offers the possibility of choosing two different models for estimating the uncertainty interval:
- SYMMETRIC APPROACH: the conventional way of estimating uncertainty, it considers the uncertainty of recovery, precision and bias on the root-sum-of-squares method.
- ASYMMETRIC APPROACH: a new proposed way of estimating uncertainty, it considers the uncertainty of recovery and precision on the root-sum-of-squares method. Bias is used to adjust the position of the interval, leading to an asymmetric interval about the measured value.

For more information about each approach, please refer to (article doi).

HOW TO USE THE APP

The settings for the simulations are made on the left-panel ("Simulation parameters"). It is divided in different containers:
1. Analytical criteria:
   - Mean value: inform a reference value for the expected mean result to the product, method, or process, as (%), for example, 100% of a given dose. 
   - Standard deviation: inform a expected standard deviation for the measurement of the "mean value", as (%);
   - Recovery range (%): select a range of expected recovery of the analytical method, the left red circle corresponds to a lower limit, while the right red circle indicates the upper recovery limit. We suggest choosing a greater range to help visualize the region on which results are still expected to comply;
   - Precision value (%): select the maximum expected value for the precision of the analytical method. We suggest choosing a greater value to help visualize the region on which results are still expected to comply.
     
2. Simulation parameters:
   - Number of simulations: select the number of iterations to be used on each simulation run. We suggest choosing a minimun of 10,000 iterations, but no more than 1,000,000 iterations. The bigger the number of simulations, the longer it will take the app to give results;
   - Simulation model: there are two options to choose from. The first option, "All simulations", considers all iterations informed. The second option, "Non-negative simulations", applies a restriction, filtering out all intervals that include a negative lower limit. This filter assumes there are no negative concentrations, and it is useful when intervals became too wide that the number of non-negative intervals decreases, hindering the simulation calculations and giving low result values;
   - Uncertainty model: there are two options to choose from, and both options can be select at the same time. The first option, "Symmetrical", is the conventional approach, computing all validation parameters into the uncertainty estimation. The second option, "Asymmetrical", estimates uncertainty as a combination of recovery and precision information only. We suggest choosing this second method when a low performance analytical method is used (i.e. poor recovery estimates and high imprecision).
     
3. Graph properties:
   - Graph axis: user can select the graph axis information. There are two options: Recovery (%) on y-axis and precision (%) on x-axis, or Bias (%) on y-axis and precision (%) on x-axis. In any choice, the coverage levels results plotted do not change.
  
4. Click "Run simulation" button to run simulation and obtain the results. These results are showed as: (i) a heatmap of coverage levels as a function of validation parameters; (ii) the width of the simulated intervals; (iii) an interactive datatable summarizing recovery value, precision value, coverage levels, width, bias, percentage of intervals with negative limits (NA (%)), percentage of intervals that are classified as "OUT" (OUT (%)).

For any further questions or suggestions, contact us at labmeq@usp.br. 
