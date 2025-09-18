import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from PIL import Image, ImageTk
cart = []
import os, sys

def resource_path(filename):
    """ Get path for bundled files (images) """
    if getattr(sys, 'frozen', False):  # running as .exe
        base_path = sys._MEIPASS
    else:  # running as script
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

# --- Excel file should stay external (editable by user) ---
if getattr(sys, 'frozen', False):  
    EXCEL_PATH = os.path.join(os.path.dirname(sys.executable), "product_database.xlsx")
else:  
    EXCEL_PATH = os.path.join(os.path.dirname(__file__), "product_database.xlsx")

# --- Images (bundled inside exe) ---
# Profile Page Image
profile_img = Image.open(resource_path("Profiler.png"))
profile_img = profile_img.resize((150, 150))
profile_photo = ImageTk.PhotoImage(profile_img)

# Frame Page Image
frame_img = Image.open(resource_path("Frame.png"))
frame_img = frame_img.resize((150, 150))
frame_photo = ImageTk.PhotoImage(frame_img)

# --- Load Excel workbook ---
if not os.path.exists(EXCEL_PATH):
    messagebox.showerror("Error", "Missing 'product_database.xlsx'.\nPlease place it in the same folder as the program.")
    sys.exit()

try:
    xls = pd.ExcelFile(EXCEL_PATH)
except PermissionError:
    messagebox.showerror("Error", "The Excel file is open. Please close 'product_database.xlsx' and try again.")
    sys.exit()
except Exception as e:
    messagebox.showerror("Error", f"Failed to load Excel file:\n{e}")
    sys.exit()
# Load and clean profile sheets
sheet_names = [s for s in xls.sheet_names if s.upper().startswith("PROFILE")]
sheets_dict = {}
for name in sheet_names:
    df = xls.parse(name)
    df["Size"] = df["Size"].astype(str).str.strip().str.upper()
    df["Type"] = df["Type"].astype(str).str.strip().str.upper()
    df["Price(RM)"] = df["Price(RM)"].astype(str).str.replace("/M", "").str.strip()
    df["Total"] = df["Total"].astype(str).str.strip()
    df["PART NO"] = df["PART NO"].astype(str).str.strip() if "PART NO" in df.columns else "N/A"
    df["DESCRIPTION"] = df["DESCRIPTION"].astype(str).str.strip() if "DESCRIPTION" in df.columns else "N/A"
    sheets_dict[name] = df

# Load and clean accessory sheet
accessory_df = xls.parse("ACCESSORY")
accessory_df["Quantity"] = accessory_df["Quantity"].astype(str).str.strip()
accessory_df["Price"] = pd.to_numeric(accessory_df["Price"], errors="coerce")
accessory_df["Type"] = accessory_df["Type"].astype(str).str.strip()
accessory_df["DESCRIPTION"] = accessory_df["DESCRIPTION"].astype(str).str.strip()
accessory_df["PART NO"] = accessory_df["PART NO"].astype(str).str.strip() if "PART NO" in accessory_df.columns else "N/A"

# Load and clean BASEPLATE sheet
baseplate_df = xls.parse("BASEPLATE")
baseplate_df["Thickness (mm)"] = pd.to_numeric(baseplate_df["Thickness (mm)"], errors="coerce")
baseplate_df["Material"] = baseplate_df["Material"].astype(str).str.strip()
baseplate_df["Treatment"] = baseplate_df["Treatment"].astype(str).str.strip()
baseplate_df["Machining"] = baseplate_df["Include Machining "].astype(str).str.strip()
baseplate_df["Price"] = pd.to_numeric(baseplate_df["Price"], errors="coerce")

# Load and clean FRAME sheet
frame_df = xls.parse("FRAME")
frame_df["Hollow Size"] = frame_df["Hollow Size"].astype(str).str.strip()
frame_df["Thickness(mm)"] = frame_df["Thickness(mm)"].astype(str).str.strip()
frame_df["Price"] = pd.to_numeric(frame_df["Price"], errors="coerce")  # Ensure price is numeric

# --- Initialize Tkinter ---
root = tk.Tk()
root.title("Product Calculator")
root.geometry("800x960")

# Navigation
def show_frame(frame):
    frame.tkraise()

container = tk.Frame(root)
container.pack(side="top", fill="both", expand=True)
frames = {}
for name in ["Main", "Profile", "Accessory","Base Plate", "Frame"]:
    frame = tk.Frame(container)
    frame.grid(row=0, column=0, sticky="nsew")
    frames[name] = frame

# === Main Page ===
tk.Label(frames["Main"], text="SELECT ITEM ", font=("Arial", 18)).pack(pady=30)
tk.Button(frames["Main"], text="PROFILE", width=20, height=2, command=lambda: show_frame(frames["Profile"])).pack(pady=10)
tk.Button(frames["Main"], text="ACCESSORY", width=20, height=2, command=lambda: show_frame(frames["Accessory"])).pack(pady=10)
tk.Button(frames["Main"], text="FRAME", width=20, height=2, command=lambda: show_frame(frames["Frame"])).pack(pady=10)
tk.Button(frames["Main"], text="BASE PLATE", width=20, height=2, command=lambda: show_frame(frames["Base Plate"])).pack(pady=10)
grand_total = 0.0
grand_total_var = tk.StringVar(value="GRAND TOTAL (All Items): RM 0.00")
grand_total_label = tk.Label(frames["Main"], textvariable=grand_total_var, font=("Arial", 16, "bold"), fg="blue")
grand_total_label.pack(pady=10)


def update_grand_total(amount, result_widget):
    global grand_total
    grand_total += amount
    result_widget.insert(tk.END, f"\nGRAND TOTAL (All Items): RM {grand_total:.2f}\n", "big")
    result_widget.tag_config("big", font=("Arial", 14, "bold"))
    grand_total_var.set(f"GRAND TOTAL (All Items): RM {grand_total:.2f}")

def clear_grand_total():
    global grand_total
    grand_total = 0.0
    grand_total_var.set("GRAND TOTAL (All Items): RM 0.00")
    messagebox.showinfo("Grand Total", "Grand total cleared!")
tk.Button(frames["Main"], text="Clear Grand Total", command=clear_grand_total).pack(pady=5)
# Start UI
# === Profile Page ===
tk.Label(frames["Profile"], text="PROFILE CALCULATION", font=("Arial", 16)).grid(row=0, columnspan=2, pady=10)
profile_img = Image.open(r"C:\Users\edham\OneDrive\Documents\GitHub\PriceCalculator\Profiler.png")
profile_img = profile_img.resize((150, 150))   
profile_photo = ImageTk.PhotoImage(profile_img)

profile_image_label = tk.Label(frames["Profile"], image=profile_photo)
profile_image_label.image = profile_photo   # Keep reference to avoid garbage collection
profile_image_label.grid(row=0, column=2, padx=10, pady=10, rowspan=5)

# Create label with image
tk.Label(frames["Profile"], text="Reference", font=("Arial", 14)).grid(row=5, column=2, columnspan=2, pady=10)

sheet_var = tk.StringVar()
s1_var = tk.StringVar()
type_var = tk.StringVar()
desc_var = tk.StringVar()

tk.Label(frames["Profile"], text="Sheet").grid(row=1, column=0, sticky='w')
sheet_dropdown = ttk.Combobox(frames["Profile"], textvariable=sheet_var, values=sheet_names, state="readonly")
sheet_dropdown.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frames["Profile"], text="Sizing (A x B)").grid(row=2, column=0, sticky='w')
s1_dropdown = ttk.Combobox(frames["Profile"], textvariable=s1_var, state="readonly")
s1_dropdown.grid(row=2, column=1, padx=10, pady=5)

tk.Label(frames["Profile"], text="Type").grid(row=3, column=0, sticky='w')
type_dropdown = ttk.Combobox(frames["Profile"], textvariable=type_var, state="readonly")
type_dropdown.grid(row=3, column=1, padx=10, pady=5)

tk.Label(frames["Profile"], text="Description").grid(row=4, column=0, sticky='w')
desc_dropdown = ttk.Combobox(frames["Profile"], textvariable=desc_var, state="readonly")
desc_dropdown.grid(row=4, column=1, padx=10, pady=5)

p_total = tk.Entry(frames["Profile"])
p_qty = tk.Entry(frames["Profile"])
p_holes = tk.Entry(frames["Profile"])

tk.Label(frames["Profile"], text="Total Length (mm)").grid(row=5, column=0, sticky='w')  # Updated label
p_total.grid(row=5, column=1)

tk.Label(frames["Profile"], text="Quantity (pcs)").grid(row=6, column=0, sticky='w')
p_qty.grid(row=6, column=1)

tk.Label(frames["Profile"], text="Holes (0 if none)").grid(row=7, column=0, sticky='w')
p_holes.grid(row=7, column=1)

profile_result = tk.Text(frames["Profile"], height=15, width=80)
profile_result.grid(row=9, columnspan=2, pady=10)


def update_description_options(*args):
    df = sheets_dict.get(sheet_var.get())
    if df is None:
        return

    size_selected = s1_var.get().strip()
    type_selected = type_var.get().strip().upper()

    filtered_df = df[
        (df["Size"].astype(str).str.strip() == size_selected) &
        (df["Type"].astype(str).str.upper().str.strip() == type_selected)
    ]

    if "DESCRIPTION" in filtered_df.columns:
        descs = filtered_df["DESCRIPTION"].dropna().astype(str).str.strip().unique()
        desc_dropdown["values"] = sorted(descs)
        desc_var.set("")
        if len(descs) > 0:
            desc_var.set(descs[0])
    else:
        messagebox.showerror("Error", f"'DESCRIPTION' column not found in {sheet_var.get()} sheet")
def update_profile_options(*args):
    df = sheets_dict.get(sheet_var.get())
    if df is None:
        return

    if "Size" in df.columns:
        s1_dropdown["values"] = sorted(df["Size"].dropna().astype(str).unique())
        if s1_dropdown["values"]:
            s1_var.set(s1_dropdown["values"][0])

    if "Type" in df.columns:
        type_dropdown["values"] = sorted(df["Type"].dropna().astype(str).unique())
        if type_dropdown["values"]:
            type_var.set(type_dropdown["values"][0])

    update_description_options()  # Trigger description update

sheet_var.trace_add("write", update_profile_options)
s1_var.trace_add("write", update_description_options)
type_var.trace_add("write", update_description_options)

profile_last_price = 0.0

def calculate_profile():
    global profile_last_price
    # Do NOT clear profile_result here, so previous output stays visible
    try:
        df = sheets_dict.get(sheet_var.get())
        size_value = s1_var.get().strip()
        t = type_var.get().strip().upper()
        desc_value = desc_var.get().strip()
        total = float(p_total.get())
        qty = int(p_qty.get())
        holes = int(p_holes.get())
    except Exception as e:
        messagebox.showerror("Input Error", f"Please fill all profile fields correctly.\n{e}")
        profile_last_price = 0.0
        return

    filtered = df[
        (df["Size"].astype(str).str.strip() == size_value) &
        (df["Type"].astype(str).str.upper() == t) &
        (df["DESCRIPTION"].astype(str).str.strip().str.upper() == desc_value.upper())
    ]

    if filtered.empty:
        profile_result.insert(tk.END, "No matching profile found.\n")
        profile_last_price = 0.0
        return

    total_m = (total * qty) / 1000
    matched_rows = []
    for _, row in filtered.iterrows():
        try:
            val = float(row["Total"].strip("<>=M "))
            price = float(row["Price(RM)"])
            bracket = row["Total"].strip()
            if bracket.startswith("<") and total_m < val:
                matched_rows.append((row["PART NO"], row["DESCRIPTION"], price))
            elif bracket.startswith(">") and total_m > val:
                matched_rows.append((row["PART NO"], row["DESCRIPTION"], price))
            elif bracket.startswith("=") and total_m == val:
                matched_rows.append((row["PART NO"], row["DESCRIPTION"], price))
        except Exception:
            continue

    if not matched_rows:
        profile_result.insert(tk.END, "No matching price found.\n")
        profile_last_price = 0.0
        return

    part_no, desc, matched_price = matched_rows[0]
    m_cost = matched_price * total_m
    c_cost = qty * 6
    h_cost = holes * 8
    total_cost = m_cost + c_cost + h_cost
    profile_last_price = total_cost

    # Append result to output
    profile_result.insert(tk.END, f"Part No: {part_no}\nDescription: {desc}\n")
    profile_result.insert(tk.END, f"Profile Subtotal: RM {total_cost:.2f}\n", "big")
    profile_result.tag_config("big", font=("Arial", 14, "bold"))

def add_profile_to_total():
    global grand_total, profile_last_price
    if profile_last_price > 0:
        grand_total += profile_last_price
        grand_total_var.set(f"GRAND TOTAL (All Items): RM {grand_total:.2f}")
        messagebox.showinfo("Added", f"Added RM {profile_last_price:.2f} to Grand Total.")
        profile_last_price = 0.0
        # Do NOT clear profile_result here
    else:
        messagebox.showwarning("Nothing to Add", "Please calculate a profile first.")

def go_back_profile():
    show_frame(frames["Main"])
def clear_all_profiles():
    global profile_grand_total
    profile_grand_total = 0.0
    p_total.delete(0, tk.END)
    p_qty.delete(0, tk.END)
    p_holes.delete(0, tk.END)
    profile_result.delete("1.0", tk.END)
    messagebox.showinfo("Profile", "All profile calculations cleared!")

# --- Buttons ---
tk.Button(frames["Profile"], text="Calculate", command=calculate_profile).grid(row=8, columnspan=2, pady=5)
tk.Button(frames["Profile"], text="Add", command=add_profile_to_total).grid(row=10, column=0, pady=5)
tk.Button(frames["Profile"], text="← Back", command=go_back_profile).grid(row=11, column=0, pady=5)
tk.Button(frames["Profile"], text="Clear All", command=clear_all_profiles).grid(row=11, column=1, pady=5)
# === Accessory Page =========================================================================================================================
tk.Label(frames["Accessory"], text="ACCESSORY CALCULATION", font=("Arial", 16)).grid(row=0, columnspan=2, pady=10)
a_type = tk.StringVar()
a_desc = tk.StringVar()
a_qty = tk.Entry(frames["Accessory"])

tk.Label(frames["Accessory"], text="Accessory Type").grid(row=1, column=0, sticky='w')
type_box = ttk.Combobox(frames["Accessory"], textvariable=a_type, values=sorted(accessory_df["Type"].unique()), state="readonly")
type_box.grid(row=1, column=1)

tk.Label(frames["Accessory"], text="Description").grid(row=2, column=0, sticky='w')
desc_box = ttk.Combobox(frames["Accessory"], textvariable=a_desc, state="readonly")
desc_box.grid(row=2, column=1)

tk.Label(frames["Accessory"], text="Quantity").grid(row=3, column=0, sticky='w')
a_qty.grid(row=3, column=1)

accessory_result = tk.Text(frames["Accessory"], height=10, width=80)
accessory_result.grid(row=5, columnspan=2, pady=10)

accessory_last_price = 0.0

def update_desc(*args):
    df = accessory_df[accessory_df["Type"] == a_type.get()]
    desc_box["values"] = sorted(df["DESCRIPTION"].unique())
    if not df.empty:
        a_desc.set(df["DESCRIPTION"].iloc[0])

a_type.trace_add("write", update_desc)

def calculate_accessory():
    global accessory_last_price
    # Do NOT clear accessory_result here, so previous output stays visible
    try:
        qty = int(a_qty.get())
    except:
        messagebox.showerror("Input Error", "Enter a valid quantity.")
        accessory_last_price = 0.0
        return

    df = accessory_df[(accessory_df["Type"] == a_type.get()) & (accessory_df["DESCRIPTION"] == a_desc.get())]
    price = None
    part_no = "-"
    for _, row in df.iterrows():
        bracket = row["Quantity"].strip()
        try:
            val = int(bracket.strip("<>= "))
            if bracket.startswith("<") and qty < val:
                price = row["Price"]
                part_no = row["PART NO"]
                break
            elif bracket.startswith(">") and qty > val:
                price = row["Price"]
                part_no = row["PART NO"]
            elif bracket.startswith("=") and qty == val:
                price = row["Price"]
                part_no = row["PART NO"]
                break
        except: continue

    if price is None:
        accessory_result.insert(tk.END, "No matching price found.\n")
        accessory_last_price = 0.0
        return

    total = price * qty
    accessory_last_price = total
    accessory_result.insert(tk.END, f"Part No: {part_no}\nDescription: {a_desc.get()}\n")
    accessory_result.insert(tk.END, f"Accessory Subtotal: RM {total:.2f}\n", "big")
    accessory_result.tag_config("big", font=("Arial", 14, "bold"))

def add_accessory_to_total():
    global grand_total, accessory_last_price
    if accessory_last_price > 0:
        grand_total += accessory_last_price
        grand_total_var.set(f"GRAND TOTAL (All Items): RM {grand_total:.2f}")
        messagebox.showinfo("Added", f"Added RM {accessory_last_price:.2f} to Grand Total.")
        accessory_last_price = 0.0
        # Do NOT clear accessory_result here
    else:
        messagebox.showwarning("Nothing to Add", "Please calculate an accessory first.")

def clear_all_accessories():
    a_qty.delete(0, tk.END)
    accessory_result.delete("1.0", tk.END)
    messagebox.showinfo("Accessory", "All accessory calculations cleared!")

# --- Accessory Buttons ---
tk.Button(frames["Accessory"], text="Calculate", command=calculate_accessory).grid(row=4, columnspan=2, pady=5)
tk.Button(frames["Accessory"], text="Add", command=add_accessory_to_total).grid(row=6, column=0, pady=5)
tk.Button(frames["Accessory"], text="← Back", command=lambda: show_frame(frames["Main"])).grid(row=6, column=1, pady=5)
tk.Button(frames["Accessory"], text="Clear All", command=clear_all_accessories).grid(row=7, columnspan=2, pady=5)

# === Base Plate Page ===
tk.Label(frames["Base Plate"], text="BASE PLATE CALCULATION", font=("Arial", 16)).grid(row=0, columnspan=2, pady=10)
thickness_var = tk.StringVar()
material_var = tk.StringVar()
treatment_var = tk.StringVar()
including_Machine_var = tk.StringVar()

tk.Label(frames["Base Plate"], text="Thickness(mm)").grid(row=1, column=0, sticky='w')
thickness_dropdown = ttk.Combobox(
    frames["Base Plate"], textvariable=thickness_var,
    values=sorted(baseplate_df["Thickness (mm)"].dropna().unique()), state="readonly"
)
thickness_dropdown.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frames["Base Plate"], text="Material").grid(row=2, column=0, sticky='w')
material_dropdown = ttk.Combobox(
    frames["Base Plate"], textvariable=material_var,
    values=sorted(baseplate_df["Material"].dropna().unique()), state="readonly"
)
material_dropdown.grid(row=2, column=1, padx=10, pady=5)

tk.Label(frames["Base Plate"], text="Treatment").grid(row=3, column=0, sticky='w')
treatment_dropdown = ttk.Combobox(
    frames["Base Plate"], textvariable=treatment_var,
    values=sorted(baseplate_df["Treatment"].dropna().unique()), state="readonly"
)
treatment_dropdown.grid(row=3, column=1, padx=10, pady=5)

tk.Label(frames["Base Plate"], text="Including Machining").grid(row=4, column=0, sticky='w')
including_Machining_dropdown = ttk.Combobox(
    frames["Base Plate"], textvariable=including_Machine_var,
    values=sorted(baseplate_df["Machining"].dropna().unique()), state="readonly"
)
including_Machining_dropdown.grid(row=4, column=1, padx=10, pady=5)

b_width = tk.Entry(frames["Base Plate"])
b_length = tk.Entry(frames["Base Plate"])
b_qty = tk.Entry(frames["Base Plate"])

tk.Label(frames["Base Plate"], text="Width(mm)").grid(row=5, column=0, sticky='w')
b_width.grid(row=5, column=1)

tk.Label(frames["Base Plate"], text="Length(mm)").grid(row=6, column=0, sticky='w')
b_length.grid(row=6, column=1)

tk.Label(frames["Base Plate"], text="Quantity").grid(row=7, column=0, sticky='w')
b_qty.grid(row=7, column=1)

basePlate_result = tk.Text(frames["Base Plate"], height=15, width=80)
basePlate_result.grid(row=9, columnspan=2, pady=10)

def update_baseplate_options(*args):
    thickness_dropdown["values"] = sorted(baseplate_df["Thickness (mm)"].dropna().unique())
    material_dropdown["values"] = sorted(baseplate_df["Material"].dropna().unique())
    treatment_dropdown["values"] = sorted(baseplate_df["Treatment"].dropna().unique())
    including_Machining_dropdown["values"] = sorted(baseplate_df["Machining"].dropna().unique())
    if thickness_dropdown["values"]: thickness_var.set(thickness_dropdown["values"][0])
    if material_dropdown["values"]: material_var.set(material_dropdown["values"][0])
    if treatment_dropdown["values"]: treatment_var.set(treatment_dropdown["values"][0])
    if including_Machining_dropdown["values"]: including_Machine_var.set(including_Machining_dropdown["values"][0])

thickness_var.trace_add("write", update_baseplate_options)
material_var.trace_add("write", update_baseplate_options)
treatment_var.trace_add("write", update_baseplate_options)
including_Machine_var.trace_add("write", update_baseplate_options)

def calcula():
    basePlate_result.delete("1.0", tk.END)
    try:
        thickness = float(thickness_var.get())
        material = material_var.get().strip()
        treatment = treatment_var.get().strip()
        including_Machining = including_Machine_var.get().strip()
        width = int(b_width.get())
        length = int(b_length.get())
        qty = int(b_qty.get())
    except Exception as e:
        messagebox.showerror("Input Error", f"Please fill all base plate fields correctly.\n{e}")
        return

    df = baseplate_df[
        (baseplate_df["Thickness (mm)"] == thickness) &
        (baseplate_df["Material"] == material) &
        (baseplate_df["Treatment"] == treatment) &
        (baseplate_df["Machining"] == including_Machining)
    ]

    if df.empty:
        basePlate_result.insert(tk.END, "No matching base plate found.\n")
        return

    price_per_unit = df["Price"].values[0]
    total_area = width * length * qty
    total_price = price_per_unit * total_area / 1000000  # Convert mm^2 to m^2 for price calculation

    basePlate_result.insert(tk.END, f"Material: {material}\n")
    basePlate_result.insert(tk.END, f"Treatment: {treatment}\n")
    basePlate_result.insert(tk.END, f"Machining: {including_Machining}\n")
    basePlate_result.insert(tk.END, f"Total Area: {total_area} mm²\n")
    basePlate_result.insert(tk.END, f"Price per unit: RM {price_per_unit:.2f}\n")
    basePlate_result.insert(tk.END, f"Total Price: RM {total_price:.2f}\n", "big")
    basePlate_result.tag_config("big", font=("Arial", 14, "bold"))
tk.Button(frames["Base Plate"], text="Calculate", command=calcula).grid(row=8, columnspan=2, pady=5)
tk.Button(frames["Base Plate"], text="← Back", command=lambda: show_frame(frames["Main"])).grid(row=10, column=0, pady=5)

# === Frames Page =====================================================
tk.Label(frames["Frame"], text="FRAME CALCULATION", font=("Arial", 16)).grid(row=0, columnspan=2, pady=10)
frame_img = Image.open(r"C:\Users\edham\OneDrive\Documents\GitHub\PriceCalculator\Frame.png")
frame_img = frame_img.resize((150, 150))   
frame_photo = ImageTk.PhotoImage(frame_img)

frame_image_label = tk.Label(frames["Frame"], image=frame_photo)
frame_image_label.image = frame_photo   
frame_image_label.grid(row=0, column=2, padx=10, pady=10, rowspan=5)

# Create label with image
tk.Label(frames["Frame"], text="Reference", font=("Arial", 14)).grid(row=5, column=2, columnspan=2, pady=10)
size_var = tk.StringVar()
thickness_var = tk.StringVar()

tk.Label(frames["Frame"], text="Size").grid(row=3, column=0, sticky='w')
size_dropdown = ttk.Combobox(frames["Frame"], textvariable=size_var, values=sorted(frame_df["Hollow Size"].unique()), state="readonly")
size_dropdown.grid(row=3, column=1)

tk.Label(frames["Frame"], text="Thickness").grid(row=4, column=0, sticky='w')
thickness_dropdown = ttk.Combobox(frames["Frame"], textvariable=thickness_var, values=sorted(frame_df["Thickness(mm)"].unique()), state="readonly")
thickness_dropdown.grid(row=4, column=1)

frame_last_price = 0.0

c_width = tk.Entry(frames["Frame"])
c_length = tk.Entry(frames["Frame"])
c_height = tk.Entry(frames["Frame"])


tk.Label(frames["Frame"], text="Width(mm)").grid(row=5, column=0, sticky='w')
c_width.grid(row=5, column=1)

tk.Label(frames["Frame"], text="Length(mm)").grid(row=6, column=0, sticky='w')
c_length.grid(row=6, column=1)

tk.Label(frames["Frame"], text="Height(mm)").grid(row=7, column=0, sticky='w')
c_height.grid(row=7, column=1)

frame_result = tk.Text(frames["Frame"], height=15, width=80)
frame_result.grid(row=9, columnspan=2, pady=10)

def update_frame(*args):
    df = frame_df[frame_df["Hollow Size"] == size_var.get()]
    thickness_dropdown["values"] = sorted(df["Thickness(mm)"].unique())
    if not df.empty:
        a_desc.set(df["Thickness(mm)"].iloc[0])

size_var.trace_add("write", update_frame)

frame_last_price = 0.0
frame_material_cost = 0.0
frame_labour_cost = 0.0

def calculate_frame():
    global frame_last_price, frame_material_cost, frame_labour_cost
    # Do NOT clear frame_result here, so previous output stays visible
    try:
        size = str(size_var.get()).strip()
        thickness = str(thickness_var.get()).strip()
        width = float(c_width.get())
        length = float(c_length.get())
        height = float(c_height.get())
    except ValueError:
        messagebox.showerror("Input Error", "Please fill all frame fields with valid numbers.")
        frame_last_price = 0.0
        return

    df_filtered = frame_df[
        (frame_df["Hollow Size"].astype(str).str.strip() == size) &
        (frame_df["Thickness(mm)"].astype(str).str.strip() == thickness)
    ]

    if df_filtered.empty:
        messagebox.showerror("Data Error", "No matching price found for selected size and thickness.")
        frame_last_price = 0.0
        return

    try:
        unit_price = float(df_filtered["Price"].iloc[0])
    except (ValueError, TypeError):
        messagebox.showerror("Data Error", "Invalid price format in data.")
        frame_last_price = 0.0
        return

    # Calculate total meter and cost
    total_meter = ((width * 6) + (length * 4) + (height * 4)) / 1000 
    material_cost = total_meter * unit_price
    total_volume = (width * length * height) / 1000000000  # mm³ to m³
    labour_cost = total_volume * (300 / 0.96)
    total_price = material_cost + labour_cost
    frame_last_price = total_price
    frame_material_cost = material_cost
    frame_labour_cost = labour_cost

    # Display results 
    frame_result.insert(tk.END, f"Material cost: RM {material_cost:.2f}\n")
    frame_result.insert(tk.END, f"Labour cost: RM {labour_cost:.2f}\n")
    frame_result.insert(tk.END, f"Total price: RM {total_price:.2f}\n", "big")
    frame_result.tag_config("big", font=("Arial", 14, "bold"))

def add_frame_to_total():
    global grand_total, frame_last_price
    if frame_last_price > 0:
        grand_total += frame_last_price
        grand_total_var.set(f"GRAND TOTAL (All Items): RM {grand_total:.2f}")
        messagebox.showinfo("Added", f"Added RM {frame_last_price:.2f} to Grand Total.")
        frame_last_price = 0.0
        # Do NOT clear frame_result here
    else:
        messagebox.showwarning("Nothing to Add", "Please calculate a frame first.")

def clear_all_frames():
    c_width.delete(0, tk.END)
    c_length.delete(0, tk.END)
    c_height.delete(0, tk.END)
    frame_result.delete("1.0", tk.END)
    messagebox.showinfo("Frame", " Cleared!")

# --- Frame Buttons ---
tk.Button(frames["Frame"], text="Calculate", command=calculate_frame).grid(row=8, columnspan=2, pady=5)
tk.Button(frames["Frame"], text="Add", command=add_frame_to_total).grid(row=10, column=0, pady=5)
tk.Button(frames["Frame"], text="← Back", command=lambda: show_frame(frames["Main"])).grid(row=10, column=1, pady=5)
tk.Button(frames["Frame"], text="Clear All", command=clear_all_frames).grid(row=11, columnspan=2, pady=5)

# Start UI
show_frame(frames["Main"])
root.mainloop()