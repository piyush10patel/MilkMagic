import streamlit as st
from database import save_fat_rate, get_fat_rate

def manage_rates():
    st.title("💰 Rate Management")
    
    # Get current fat rate
    current_rate = get_fat_rate()
    
    st.subheader("Fat Rate Settings")
    with st.form("fat_rate_form"):
        new_rate = st.number_input(
            "Rate per Fat Percentage (₹)",
            min_value=0.0,
            value=float(current_rate),
            step=0.1,
            help="This rate will be multiplied by the fat percentage to calculate the rate per liter"
        )
        
        # Example calculation
        example_fat = 6.0
        example_rate = example_fat * new_rate
        st.write("Example calculation:")
        st.write(f"For milk with {example_fat}% fat:")
        st.write(f"{example_fat}% × ₹{new_rate:.2f} = ₹{example_rate:.2f} per liter")
        
        submit = st.form_submit_button("Update Rate")
        
        if submit:
            if save_fat_rate(new_rate):
                st.success("Fat rate updated successfully!")
                st.rerun()

if __name__ == "__main__":
    manage_rates() 