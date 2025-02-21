import streamlit as st
from PIL import Image
import io
import easyocr

def extract_w2_data(image):
    reader = easyocr.Reader(['en'])
    results = reader.readtext(image, detail=0)
    extracted_data = {}
    
    for i, text in enumerate(results):
        if "Wages, tips, other comp." in text:
            extracted_data["wages"] = float(results[i+1].replace(",", ""))
        elif "Federal income tax withheld" in text:
            extracted_data["federal_withholding"] = float(results[i+1].replace(",", ""))
        elif "Social security wages" in text:
            extracted_data["social_security_wages"] = float(results[i+1].replace(",", ""))
        elif "State income tax" in text:
            extracted_data["state_withholding"] = float(results[i+1].replace(",", ""))
    
    return extracted_data

def calculate_taxes(wages, short_term_gains, business_profit, k401_contribution, mortgage_interest,
                     property_taxes, childcare_expenses, federal_withholding, state_withholding):
    # 2024 Standard Deduction for Married Filing Jointly
    standard_deduction = 29200
    
    # Calculate Adjusted Gross Income (AGI)
    agi = wages + short_term_gains + business_profit - k401_contribution
    
    # Determine itemized deductions
    itemized_deductions = mortgage_interest + property_taxes
    deductions = max(standard_deduction, itemized_deductions)
    
    # Compute taxable income
    taxable_income = max(0, agi - deductions)
    
    # 2024 Federal Tax Brackets for Married Filing Jointly
    federal_brackets = [
        (0, 23200, 0.10),
        (23200, 94300, 0.12),
        (94300, 201050, 0.22),
        (201050, 383900, 0.24),
        (383900, 487450, 0.32),
        (487450, 731200, 0.35),
        (731200, float("inf"), 0.37)
    ]
    
    federal_tax = 0
    previous_bracket = 0
    for lower, upper, rate in federal_brackets:
        if taxable_income > lower:
            tax_at_bracket = min(taxable_income, upper) - previous_bracket
            federal_tax += tax_at_bracket * rate
            previous_bracket = upper
        else:
            break
    
    # Childcare Credit (20% of eligible expenses, up to $6000 max)
    childcare_credit = min(childcare_expenses, 6000) * 0.20
    
    # Final Federal Tax Liability
    final_federal_tax = federal_tax - childcare_credit
    federal_refund_or_owed = federal_withholding - final_federal_tax
    
    # New York State Tax Brackets for 2024
    ny_brackets = [
        (0, 17150, 0.04), (17150, 23600, 0.045), (23600, 27900, 0.0525),
        (27900, 43000, 0.059), (43000, 161550, 0.0597), (161550, 323200, 0.0633),
        (323200, 2155350, 0.0685), (2155350, float("inf"), 0.10)
    ]
    
    state_taxable_income = max(0, wages - deductions - k401_contribution)
    state_tax = 0
    previous_bracket = 0
    for lower, upper, rate in ny_brackets:
        if state_taxable_income > lower:
            tax_at_bracket = min(state_taxable_income, upper) - previous_bracket
            state_tax += tax_at_bracket * rate
            previous_bracket = upper
        else:
            break
    
    state_refund_or_owed = state_withholding - state_tax
    
    return agi, final_federal_tax, federal_refund_or_owed, state_tax, state_refund_or_owed

# Streamlit UI
st.title("2024 Tax Calculator (Federal & New York State)")

# File uploader for W-2 image
uploaded_file = st.file_uploader("Upload W-2 Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    extracted_data = extract_w2_data(image)
    st.write("Extracted Data:", extracted_data)

# Inputs
wages = st.number_input("W-2 Wages ($)", min_value=0, value=extracted_data.get("wages", 656490))
federal_withholding = st.number_input("Federal Tax Withheld ($)", min_value=0, value=extracted_data.get("federal_withholding", 137405))
state_withholding = st.number_input("State Tax Withheld ($)", min_value=0, value=extracted_data.get("state_withholding", 63843))
short_term_gains = st.number_input("Short-Term Capital Gains ($)", min_value=0, value=48000)
business_profit = st.number_input("Business Profit ($)", min_value=0, value=11700)
k401_contribution = st.number_input("401(k) Contributions ($)", min_value=0, value=23000)
mortgage_interest = st.number_input("Mortgage Interest Paid ($)", min_value=0, value=17600)
property_taxes = st.number_input("Property Taxes Paid ($)", min_value=0, value=20534)
childcare_expenses = st.number_input("Childcare Expenses ($)", min_value=0, value=5000)

# Calculate Taxes
if st.button("Calculate Taxes"):
    agi, federal_tax, federal_refund, state_tax, state_refund = calculate_taxes(
        wages, short_term_gains, business_profit, k401_contribution, mortgage_interest,
        property_taxes, childcare_expenses, federal_withholding, state_withholding
    )
    
    # Display Results
    st.subheader("Tax Results")
    st.write(f"**Adjusted Gross Income (AGI):** ${agi:,.2f}")
    st.write(f"**Federal Tax Liability:** ${federal_tax:,.2f}")
    st.write(f"**Federal Refund / Amount Owed:** ${federal_refund:,.2f}")
    st.write(f"**NY State Tax Liability:** ${state_tax:,.2f}")
    st.write(f"**State Refund / Amount Owed:** ${state_refund:,.2f}")
