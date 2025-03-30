import customtkinter as ctk
import json
from datetime import datetime
from tkinter import messagebox

# Configure appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AdminPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Panel")
        self.root.attributes("-alpha", 0.95)
        self.root.geometry("900x700")
        
        # Sort variables
        self.sort_var = ctk.StringVar(value="Date (Newest)")
        self.filter_var = ctk.StringVar(value="All")
        
        self.setup_ui()
        self.update_bug_display()

    def setup_ui(self):
        # Header with sort/filter controls
        header = ctk.CTkFrame(self.root, height=60)
        header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(header, text="BUG REPORTS", font=("Arial", 16, "bold")).pack(side="left", padx=20)
        
        # Sort dropdown
        ctk.CTkLabel(header, text="Sort by:").pack(side="left", padx=(20,5))
        sort_menu = ctk.CTkComboBox(
            header,
            values=["Date (Newest)", "Date (Oldest)", "Priority (High-Low)", "Priority (Low-High)", "Status"],
            variable=self.sort_var,
            command=self.update_bug_display,
            width=150
        )
        sort_menu.pack(side="left")
        
        # Filter dropdown
        ctk.CTkLabel(header, text="Filter:").pack(side="left", padx=(20,5))
        filter_menu = ctk.CTkComboBox(
            header,
            values=["All", "Open", "Resolved", "High", "Medium", "Low"],
            variable=self.filter_var,
            command=self.update_bug_display,
            width=120
        )
        filter_menu.pack(side="left")
        
        # Main content area
        content_frame = ctk.CTkFrame(self.root)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))
        
        # Bug list (left)
        self.list_frame = ctk.CTkScrollableFrame(content_frame, width=400)
        self.list_frame.pack(side="left", fill="y", padx=(0,10))
        
        # Bug details (right)
        detail_frame = ctk.CTkFrame(content_frame)
        detail_frame.pack(side="left", fill="both", expand=True)
        
        # Detail sections
        ctk.CTkLabel(detail_frame, text="Bug Details", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.detail_text = ctk.CTkTextbox(
            detail_frame,
            width=400,
            height=300,
            font=("Arial", 12),
            wrap="word"
        )
        self.detail_text.pack(fill="both", expand=True, pady=5)
        
        # Action buttons
        button_frame = ctk.CTkFrame(detail_frame)
        button_frame.pack(fill="x", pady=10)
        
        self.resolve_btn = ctk.CTkButton(
            button_frame,
            text="Mark as Resolved",
            command=self.mark_resolved,
            state="disabled"
        )
        self.resolve_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Refresh",
            command=self.update_bug_display
        ).pack(side="left", padx=5)

    def load_bugs(self):
        try:
            with open("bugs.json", "r") as f:
                bugs = json.load(f)
                
                # Apply filters
                filter_val = self.filter_var.get()
                if filter_val == "Open":
                    bugs = [b for b in bugs if b["status"] == "Open"]
                elif filter_val == "Resolved":
                    bugs = [b for b in bugs if b["status"] == "Resolved"]
                elif filter_val in ["High", "Medium", "Low"]:
                    bugs = [b for b in bugs if b["priority"] == filter_val]
                
                # Apply sorting
                sort_val = self.sort_var.get()
                if sort_val == "Date (Newest)":
                    bugs.sort(key=lambda x: x["timestamp"], reverse=True)
                elif sort_val == "Date (Oldest)":
                    bugs.sort(key=lambda x: x["timestamp"])
                elif sort_val == "Priority (High-Low)":
                    priority_order = {"High": 3, "Medium": 2, "Low": 1}
                    bugs.sort(key=lambda x: priority_order[x["priority"]], reverse=True)
                elif sort_val == "Priority (Low-High)":
                    priority_order = {"High": 3, "Medium": 2, "Low": 1}
                    bugs.sort(key=lambda x: priority_order[x["priority"]])
                elif sort_val == "Status":
                    bugs.sort(key=lambda x: x["status"])
                
                return bugs
        except FileNotFoundError:
            return []

    def update_bug_display(self):
        # Clear existing widgets
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        bugs = self.load_bugs()
        self.bugs = bugs  # Store for reference
        
        for i, bug in enumerate(bugs):
            # Create bug card
            card = ctk.CTkFrame(
                self.list_frame,
                border_width=1,
                border_color="#444",
                corner_radius=5
            )
            card.pack(fill="x", pady=3)
            
            # Priority color coding
            priority_colors = {
                "High": "#e74c3c",
                "Medium": "#f39c12",
                "Low": "#2ecc71"
            }
            
            # Bug summary
            summary = f"{bug['program']}: {bug['title']}"
            status = f"{bug['status']} | {bug['priority']} priority"
            
            ctk.CTkLabel(
                card,
                text=summary,
                font=("Arial", 12, "bold"),
                anchor="w"
            ).pack(fill="x", padx=5, pady=(5,0))
            
            ctk.CTkLabel(
                card,
                text=status,
                text_color=("#2ecc71" if bug["status"] == "Resolved" else priority_colors[bug["priority"]]),
                font=("Arial", 10),
                anchor="w"
            ).pack(fill="x", padx=5, pady=(0,5))
            
            # Click binding to show details
            card.bind("<Button-1>", lambda e, idx=i: self.show_bug_details(idx))
            for child in card.winfo_children():
                child.bind("<Button-1>", lambda e, idx=i: self.show_bug_details(idx))

    def show_bug_details(self, index):
        bug = self.bugs[index]
        details = (
            f"Program: {bug['program']}\n"
            f"Title: {bug['title']}\n"
            f"Priority: {bug['priority']}\n"
            f"Status: {bug['status']}\n"
            f"Submitted by: {bug.get('name', 'Anonymous')}\n"
            f"Date: {bug['timestamp']}\n\n"
            f"Description:\n{bug['description']}"
        )
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", details)
        self.resolve_btn.configure(state="normal" if bug["status"] == "Open" else "disabled")

    def mark_resolved(self):
        selected_text = self.detail_text.get("1.0", "end-1c")
        for i, bug in enumerate(self.bugs):
            if bug["title"] in selected_text and bug["status"] == "Open":
                # Update in memory
                self.bugs[i]["status"] = "Resolved"
                
                # Update JSON file
                with open("bugs.json", "w") as f:
                    json.dump(self.bugs, f, indent=4)
                
                messagebox.showinfo("Success", "Bug marked as resolved!")
                self.update_bug_display()
                return
        messagebox.showerror("Error", "No open bug selected!")

if __name__ == "__main__":
    root = ctk.CTk()
    app = AdminPanel(root)
    root.mainloop()