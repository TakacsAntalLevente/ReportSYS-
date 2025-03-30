import customtkinter as ctk
import json
from datetime import datetime
from tkinter import messagebox

# Configure appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def validate_fields():
    """Check if all mandatory fields are filled"""
    if (not name_entry.get().strip() or 
        not title_entry.get().strip() or 
        not desc_entry.get("1.0", "end-1c").strip()):
        submit_btn.configure(state="disabled", fg_color="#666")
        return False
    submit_btn.configure(state="normal", fg_color=("#3b8ed0", "#1f6aa5"))
    return True

def on_field_change(*args):
    """Triggered when any field changes"""
    validate_fields()

def submit_bug():
    if not validate_fields():
        messagebox.showerror("Error", "Please fill all mandatory fields!")
        return

    data = {
        "name": name_entry.get(),
        "program": program_combobox.get(),
        "priority": priority_combobox.get(),
        "title": title_entry.get(),
        "description": desc_entry.get("1.0", "end-1c"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "Open"
    }

    try:
        with open("bugs.json", "r+") as f:
            try:
                bugs = json.load(f)
                if not isinstance(bugs, list):
                    bugs = []
            except json.JSONDecodeError:
                bugs = []
    except FileNotFoundError:
        bugs = []

    bugs.append(data)
    with open("bugs.json", "w") as f:
        json.dump(bugs, f, indent=4)

    # Clear form
    name_entry.delete(0, "end")
    program_combobox.set("XRAYD")
    priority_combobox.set("Medium")
    title_entry.delete(0, "end")
    desc_entry.delete("1.0", "end")
    
    # Show confirmation and disable button again
    confirmation_label.configure(text="✓ Report submitted!", text_color="#2ecc71")
    submit_btn.configure(state="disabled", fg_color="#666")
    root.after(3000, lambda: confirmation_label.configure(text=""))

# Main window
root = ctk.CTk()
root.title("Bug Reporter - v0.1")
root.geometry("600x600")

# Header
header = ctk.CTkFrame(root, height=60)
header.pack(fill="x", padx=10, pady=10)
ctk.CTkLabel(header, text="REPORT A BUG", font=("Arial", 18, "bold")).pack(side="left", padx=20)

# Form container
form_frame = ctk.CTkFrame(root, border_width=1, border_color="#444", corner_radius=10)
form_frame.pack(pady=10, padx=10, fill="both", expand=True)

# Configure grid
form_frame.grid_columnconfigure(0, weight=1)
form_frame.grid_columnconfigure(1, weight=3)

# Mandatory fields with validation
mandatory_fields = [
    ("Your Name*", "name", ctk.CTkEntry, {"placeholder_text": "Required"}),
    ("Program*", "program", ctk.CTkComboBox, {
        "values": ["XRAYD", "XRAYD - Config Editor", "Nincs felsorolva"],
        "state": "readonly"
    }),
    ("Priority*", "priority", ctk.CTkComboBox, {
        "values": ["Low", "Medium", "High"],
        "state": "readonly"
    }),
    ("Bug Title*", "title", ctk.CTkEntry, {"placeholder_text": "Required"}),
    ("Description*", "desc", ctk.CTkTextbox, {"height": 100})
]

# Track variables for validation
entry_vars = []

for i, (label, field_type, widget, kwargs) in enumerate(mandatory_fields):
    # Label with asterisk
    ctk.CTkLabel(
        form_frame,
        text=label,
        font=("Arial", 12, "bold"),
        anchor="w",
        text_color=("#333", "#ccc")
    ).grid(row=i, column=0, padx=(20,10), pady=(10,5), sticky="w")

    # Input field
    if widget == ctk.CTkEntry:
        entry = widget(
            form_frame,
            border_width=1,
            border_color="#666",
            corner_radius=8,
            **kwargs
        )
        var = ctk.StringVar()
        entry.configure(textvariable=var)
        var.trace_add("write", lambda *args: on_field_change())
        
    elif widget == ctk.CTkComboBox:
        entry = widget(
            form_frame,
            border_width=1,
            border_color="#666",
            button_color="#444",
            corner_radius=8,
            **kwargs
        )
        var = ctk.StringVar()
        entry.configure(variable=var)
        var.trace_add("write", lambda *args: on_field_change())
        
    elif widget == ctk.CTkTextbox:
        entry = widget(
            form_frame,
            border_width=1,
            border_color="#666",
            corner_radius=8,
            **kwargs
        )
        # Textboxes need custom validation
        def on_text_change(event=None):
            on_field_change()
        entry.bind("<KeyRelease>", on_text_change)
    
    entry.grid(row=i, column=1, padx=(0,20), pady=5, sticky="ew")
    entry_vars.append(var if widget != ctk.CTkTextbox else None)

    # Store references
    if field_type == "name":
        name_entry = entry
    elif field_type == "program":
        program_combobox = entry
        program_combobox.set("XRAYD")
    elif field_type == "priority":
        priority_combobox = entry
        priority_combobox.set("Medium")
    elif field_type == "title":
        title_entry = entry
    elif field_type == "desc":
        desc_entry = entry

# Submit button (initially disabled)
submit_btn = ctk.CTkButton(
    form_frame,
    text="Submit Bug",
    command=submit_bug,
    state="disabled",
    fg_color="#666",
    corner_radius=8,
    hover_color=("#3a7ebf", "#1f538d")
)
submit_btn.grid(row=len(mandatory_fields), column=0, columnspan=2, pady=20, padx=20, sticky="ew")

# Footer with validation info
footer = ctk.CTkFrame(form_frame, fg_color="transparent")
footer.grid(row=len(mandatory_fields)+1, column=0, columnspan=2, pady=(0,10))
ctk.CTkLabel(
    footer,
    text="* Mandatory fields",
    text_color="#888",
    font=("Arial", 10)
).pack(side="left", padx=20)

confirmation_label = ctk.CTkLabel(
    footer,
    text="",
    font=("Arial", 12)
)
confirmation_label.pack(side="right", padx=20)

root.mainloop()