from fpdf import FPDF
import datetime

class Receipt:
    def __init__(self, entry_data, user_data):
        self.pdf = FPDF()
        self.entry_data = entry_data
        self.user_data = user_data
    
    def generate(self):
        self.pdf.add_page()
        
        # Header
        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(190, 10, 'MilkMagic', 0, 1, 'C')
        
        # User Details
        self.pdf.set_font('Arial', '', 12)
        self.pdf.cell(190, 10, f"Supplier: {self.user_data['name']}", 0, 1)
        self.pdf.cell(190, 10, f"Date: {self.entry_data['date']}", 0, 1)
        self.pdf.cell(190, 10, f"Shift: {self.entry_data['shift']}", 0, 1)
        
        # Milk Details
        self.pdf.ln(10)
        self.pdf.cell(95, 10, "Parameter", 1)
        self.pdf.cell(95, 10, "Value", 1)
        self.pdf.ln()
        
        details = [
            ("Quantity", f"{self.entry_data['quantity']} L"),
            ("Fat %", f"{self.entry_data['fat']}"),
            ("SNF %", f"{self.entry_data['snf']}"),
            ("CLR", f"{self.entry_data['clr']}"),
            ("Amount", f"₹ {self.entry_data['amount']}")
        ]
        
        for label, value in details:
            self.pdf.cell(95, 10, label, 1)
            self.pdf.cell(95, 10, value, 1)
            self.pdf.ln()
        
        # Footer
        self.pdf.ln(10)
        self.pdf.cell(190, 10, "Thank you for your business!", 0, 1, 'C')
        
        return self.pdf.output(dest='S').encode('latin1') 