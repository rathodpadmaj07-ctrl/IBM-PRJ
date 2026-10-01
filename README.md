# Real Estate Price Outlier Analyzer

An academic-quality Python and Streamlit web application designed to statistically analyze real-estate pricing data and identify **severely underpriced and overpriced properties relative to their urban-zone characteristics**.

---

## 1. Problem Statement

In real-estate analytics, simply identifying high or low property prices globally can lead to inaccurate conclusions because property values vary drastically by location (urban zone) and size. 

This project specifically answers:
> *"Use Grubbs' test and extreme value analysis to identify severely underpriced or overpriced properties relative to their urban zone features."*

Instead of using opaque black-box machine learning models, this application employs rigorous statistical techniques—specifically **Grubbs' Test for Outliers** and **Interquartile Range (IQR) Extreme Value Analysis**—to benchmark property prices within localized urban zones and detect anomalous listings.

---

## 2. Objectives

- **Statistical Rigor:** Apply hypothesis testing (Grubbs' test) and non-parametric bounds (IQR method) correctly within localized urban zones.
- **Explainable Analytics:** Provide intuitive academic explanations for why a property is flagged as an outlier (e.g. underpriced bargain vs. overpriced listing).
- **Interactive Visualizations:** Enable exploration through Plotly histograms, box plots, scatter plots, and single-property inspection cards.
- **Robust Error Handling:** Prevent application crashes when processing custom CSV uploads with missing values, invalid numerical types, or small sample sizes.

---

## 3. Key Features

- 📁 **Flexible Data Input:** Supports one-click loading of a pre-built realistic sample dataset or custom CSV uploads.
- 🧹 **Automated Data Cleaning:** Validates required columns (`urban_zone`, `area_sqft`, `price`), handles missing optional attributes (`property_id`, `property_type`, `bedrooms`, `bathrooms`), and cleans non-positive values.
- ⚙️ **Configurable Controls:** Allows setting minimum observation thresholds ($N \ge 10$) and significance levels ($\alpha = 0.01, 0.05, 0.10$) for hypothesis testing.
- 📊 **Executive Dashboard:** Displays KPI metric cards formatted in Indian currency notation (Crores ₹ Cr, Lakhs ₹ L, Thousands ₹ K).
- 🏢 **Urban Zone Benchmarking:** Computes localized median price-per-sq.ft rates to calculate explicit **Actual Price**, **Expected Price**, **Price Difference**, and **Price Difference (%)**.
- 🔎 **Property Inspector Card:** Generates single-property statistical breakdown blocks and academic interpretations.
- 📥 **Multi-format CSV Export:** Export cleaned dataset, outlier results, and urban zone statistical summaries.

---

## 4. Technology Stack

- **Language:** Python 3.10+
- **Frontend / Framework:** Streamlit
- **Data Manipulation:** Pandas, NumPy
- **Statistical Computing:** SciPy (`scipy.stats`)
- **Interactive Data Visualization:** Plotly Express & Plotly Graph Objects

*No heavy machine-learning frameworks, external databases, or complex front-end builds are required.*

---

## 5. Project Structure

```text
real-estate-price-outlier-analyzer/
│
├── app.py                      # Main Streamlit dashboard application
├── requirements.txt            # Python package dependencies
├── README.md                   # Academic project documentation
│
├── data/
│   └── sample_real_estate.csv  # Synthetic realistic dataset with embedded outliers
│
├── src/
│   ├── __init__.py             # Package marker
│   ├── data_processing.py      # Data cleaning, currency formatting & benchmarking
│   ├── statistical_analysis.py # Grubbs' test, IQR analysis & property classification
│   └── visualizations.py      # Plotly interactive charting functions
│
└── results/                    # Output directory for exported CSV reports
```

---

## 6. Installation & Quick Start

### Step 1: Clone or Navigate to the Workspace
```bash
git clone https://github.com/your-username/real-estate-price-outlier-analyzer.git
cd real-estate-price-outlier-analyzer
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Streamlit Application
```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

---

## 7. Dataset Format

The application accepts CSV files containing property listings.

### Required Columns:
- `urban_zone` *(string)*: Name or code of the urban region/neighborhood.
- `area_sqft` *(numeric)*: Property area in square feet ($> 0$).
- `price` *(numeric)*: Total property price in INR ($> 0$).

### Optional Columns:
- `property_id` *(string)*: Unique identifier (e.g. `P1023`). Auto-generated if omitted.
- `property_type` *(string)*: Type of property (e.g. Apartment, Villa, Penthouse).
- `bedrooms` *(integer)*: Number of bedrooms.
- `bathrooms` *(integer)*: Number of bathrooms.

---

## 8. Statistical Methodology

### A. Expected Price Benchmarking
Properties vary in size within an urban zone. To enable fair comparison:

$$\text{Median Rate}_{\text{zone}} = \text{median}\left(\frac{\text{price}_i}{\text{area}_i}\right) \quad \forall i \in \text{Urban Zone}$$

$$\text{Expected Price} = \text{Median Rate}_{\text{zone}} \times \text{area\_sqft}$$

$$\text{Price Difference} = \text{Actual Price} - \text{Expected Price}$$

$$\text{Price Difference (\%)} = \frac{\text{Actual Price} - \text{Expected Price}}{\text{Expected Price}} \times 100$$

### B. Grubbs' Test for Outliers (Maximum Normed Residual Test)
Grubbs' test detects whether the single most extreme value in a univariate dataset is a statistically significant outlier at significance level $\alpha$.

#### Test Statistic ($G$):
$$G = \frac{\max_{i=1..N} |x_i - \bar{x}|}{s}$$
where $\bar{x}$ is the sample mean and $s$ is the sample standard deviation.

#### Critical Value ($G_{\text{crit}}$):
$$G_{\text{crit}} = \frac{N - 1}{\sqrt{N}} \sqrt{\frac{t_{\alpha/(2N), N-2}^2}{N - 2 + t_{\alpha/(2N), N-2}^2}}$$
where $t_{\alpha/(2N), N-2}$ is the upper critical value of Student's $t$-distribution with $N-2$ degrees of freedom at significance level $\frac{\alpha}{2N}$.

If $G > G_{\text{crit}}$, we reject the null hypothesis ($H_0$) and conclude that the extreme observation is a statistical outlier.

*Assumptions:* The data within the zone should be approximately normally distributed and sample size $N \ge \text{min\_obs}$ (default 10).

### C. IQR Extreme Value Analysis
The non-parametric Interquartile Range (IQR) method calculates limits regardless of distribution shape:
- $Q1 = 25\text{th percentile}$, $Q3 = 75\text{th percentile}$
- $\text{IQR} = Q3 - Q1$
- $\text{Lower Bound} = Q1 - 1.5 \times \text{IQR}$
- $\text{Upper Bound} = Q3 + 1.5 \times \text{IQR}$

### D. Outlier Classification System
- **Potentially Underpriced:** Actual price is substantially below expected price ($\text{Price Difference (\%)} < -15\%$) and flagged by IQR lower bound or Grubbs low extreme.
- **Potentially Overpriced:** Actual price is substantially above expected price ($\text{Price Difference (\%)} > +15\%$) and flagged by IQR upper bound or Grubbs high extreme.
- **Statistical Outlier:** Flagged as an extreme observation by Grubbs or IQR test due to unusual price-per-sq.ft ratio.
- **Normal:** Property price falls within expected statistical bounds.

---

## 9. Example Results & Interpretation

### Case Study: Property P1023
- **Urban Zone:** Zone A - Downtown Core
- **Area:** 1,500 sq.ft
- **Actual Price:** ₹72.00 L
- **Expected Price:** ₹91.20 L
- **Price Difference:** -₹19.20 L
- **Price Difference (%):** -21.0%
- **Statistical Findings:**
  - `✓ IQR Analysis: Potential Outlier (Below Lower Bound)`
  - `✓ Grubbs' Test: Flagged (Potentially Underpriced)`

> **Academic Interpretation:**
> Property P1023 is priced 21.0% below the median reference benchmark for Downtown Core. The statistical tests confirm this deviation is significant ($p < 0.05$). This property represents a candidate for further physical inspection (e.g. evaluating distressed sale status, urgent liquidation, or title encumbrances).

---

## 10. Limitations

- **Normal Distribution Assumption:** Grubbs' test assumes univariate normality within each urban zone. Severe skewness in raw prices is mitigated by executing tests on price per sq.ft and supporting non-parametric IQR bounds.
- **Single Outlier Iteration:** Standard Grubbs' test evaluates one extreme outlier per iteration; multiple extreme outliers in small datasets may cause masking effects.
- **Feature Scope:** The benchmark expected price uses area and zone median rate; qualitative factors (e.g. age of building, floor level, view) require multi-variable hedonic regression if recorded.

---

## 11. Future Improvements

- Implementation of iterative Grubbs' test (Tietjen-Moore test) for multiple simultaneous outliers.
- Robust Mahalanobis distance multivariate outlier detection combining area, bedrooms, floor number, and price simultaneously.
- Interactive GIS map integration for geospatial cluster analysis of real estate outliers.
