Vehicle Registration Analytics Dashboard
📌 Overview
This project is a clean, investor-friendly analytics dashboard for visualizing Year-over-Year (YoY) and Quarter-over-Quarter (QoQ) trends in vehicle registrations across types, categories, and manufacturers in India.

It uses merged and cleaned public Vahan data and is built with Python, Streamlit, and Altair for interactive analysis.

🚀 Features
Interactive filters: Year range, vehicle type, category, manufacturer

YoY and QoQ growth: See trends and growth percentages via line charts

Summary metrics: Instant totals and latest YoY/QoQ figures

No-data guidance: Warnings when filter combinations return empty

Download option: Export filtered slices as CSV for offline analysis

Production-ready UI: Minimal, investor-focused design

⚙️ Setup Instructions
1️⃣ Clone the Repository
bash
Copy
Edit
git clone <YOUR_REPO_URL>
cd <YOUR_REPO_DIRECTORY>
2️⃣ Install Required Packages
bash
Copy
Edit
pip install streamlit pandas altair
3️⃣ Launch the Dashboard
bash
Copy
Edit
streamlit run app.py
The dashboard uses combined_cleaned_data.csv as the main dataset (edit/replace as needed).

📊 Data Assumptions
All input CSVs were merged and cleaned into a unified format using custom scripts.

Only major vehicle types (2W, 3W, 4W) and recognized OEMs are included.

Missing or unclassified manufacturers/categories use "All" as the placeholder.

Quarter information is used where available; otherwise, only yearly trends are shown.

Calculations for YoY and QoQ growth are taken directly from respective columns where available.

🛠 Feature Roadmap (If Continued)
 Add advanced analytics: market share visualization, state-wise breakdown, or segment forecasts

 Drilldowns: subtype trends, top N manufacturers by segment

 Enhanced UI with multi-metric overlays and export to Excel/PDF

🎥 Video Walkthrough
📺 Click to Watch (YouTube or Drive link)
Demo covers setup, usage, and a tour of all key features.

💡 Key Insights (Sample)
2W registrations remain the largest by volume, but growth is slowing compared to previous years.

4W segment showed a strong post-pandemic rebound, with notable gains by newer OEMs.

Manufacturer market share for 3W is shifting, with emerging brands gaining ground as established players plateau.

Investor Insight:
Over the last two years, the fastest growth in vehicle registrations has been in the electric three-wheeler segment, with registrations more than doubling in some quarters. This surge is largely driven by commercial fleet adoption and improving charging infrastructure. Additionally, while two-wheelers maintain the highest total registrations, their year-over-year growth is beginning to plateau, signaling a maturing market. Among manufacturers, Mahindra and Tata have seen the sharpest gains in four-wheeler registrations, reflecting consumer preference for new EV and SUV models.

📜 Assignment Info
Assignment by: Karthik R S
Contact: karthikrajesh9010@gmail.com
Data Source: Vahan Dashboard
