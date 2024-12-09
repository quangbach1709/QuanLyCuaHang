import tkinter as tk
from tkinter import messagebox
import pandas as pd
import keyboard
import threading
import time

class InventoryManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quản lý kho hàng")
        self.root.geometry("800x600")
        
        # Đường dẫn file Excel
        self.excel_file = "inventory.xlsx"
        try:
            self.df = pd.read_excel(self.excel_file)
        except FileNotFoundError:
            # Tạo DataFrame mới nếu file không tồn tại
            self.df = pd.DataFrame(columns=['Mã vạch', 'Tên sản phẩm', 'Giá', 'Số lượng'])
            self.df.to_excel(self.excel_file, index=False)

        # Biến lưu mã vạch đang quét
        self.current_barcode = ""
        
        self.setup_gui()
        self.start_barcode_listener()

    def setup_gui(self):
        # Frame chính
        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Các trường nhập liệu
        tk.Label(main_frame, text="Mã vạch:").grid(row=0, column=0, sticky='w')
        self.barcode_entry = tk.Entry(main_frame)
        self.barcode_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(main_frame, text="Tên sản phẩm:").grid(row=1, column=0, sticky='w')
        self.name_entry = tk.Entry(main_frame)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(main_frame, text="Giá:").grid(row=2, column=0, sticky='w')
        self.price_entry = tk.Entry(main_frame)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(main_frame, text="Số lượng:").grid(row=3, column=0, sticky='w')
        self.quantity_entry = tk.Entry(main_frame)
        self.quantity_entry.grid(row=3, column=1, padx=5, pady=5)

        # Các nút chức năng
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Thêm/Cập nhật", command=self.add_update_product).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Xóa", command=self.delete_product).pack(side=tk.LEFT, padx=5)

    def start_barcode_listener(self):
        def listen_barcode():
            while True:
                if keyboard.is_pressed('enter'):
                    self.process_barcode(self.current_barcode)
                    self.current_barcode = ""
                    time.sleep(0.1)
                else:
                    event = keyboard.read_event(suppress=True)
                    if event.event_type == keyboard.KEY_DOWN:
                        if event.name.isalnum():
                            self.current_barcode += event.name

        # Chạy listener trong thread riêng
        thread = threading.Thread(target=listen_barcode, daemon=True)
        thread.start()

    def process_barcode(self, barcode):
        # Tìm sản phẩm trong DataFrame
        product = self.df[self.df['Mã vạch'] == barcode]
        
        if not product.empty:
            # Hiển thị thông tin sản phẩm nếu tìm thấy
            self.barcode_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)

            self.barcode_entry.insert(0, product.iloc[0]['Mã vạch'])
            self.name_entry.insert(0, product.iloc[0]['Tên sản phẩm'])
            self.price_entry.insert(0, str(product.iloc[0]['Giá']))
            self.quantity_entry.insert(0, str(product.iloc[0]['Số lượng']))
        else:
            # Nếu không tìm thấy, điền mã vạch và xóa các trường khác
            self.barcode_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            
            self.barcode_entry.insert(0, barcode)

    def add_update_product(self):
        barcode = self.barcode_entry.get()
        name = self.name_entry.get()
        price = self.price_entry.get()
        quantity = self.quantity_entry.get()

        if not all([barcode, name, price, quantity]):
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        # Cập nhật hoặc thêm mới sản phẩm
        new_data = {
            'Mã vạch': barcode,
            'Tên sản phẩm': name,
            'Giá': float(price),
            'Số lượng': int(quantity)
        }

        if barcode in self.df['Mã vạch'].values:
            self.df.loc[self.df['Mã vạch'] == barcode] = new_data
        else:
            self.df = pd.concat([self.df, pd.DataFrame([new_data])], ignore_index=True)

        self.df.to_excel(self.excel_file, index=False)
        messagebox.showinfo("Thành công", "Đã cập nhật sản phẩm!")

    def delete_product(self):
        barcode = self.barcode_entry.get()
        if not barcode:
            messagebox.showerror("Lỗi", "Vui lòng nhập mã vạch!")
            return

        if barcode in self.df['Mã vạch'].values:
            self.df = self.df[self.df['Mã vạch'] != barcode]
            self.df.to_excel(self.excel_file, index=False)
            
            self.barcode_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            
            messagebox.showinfo("Thành công", "Đã xóa sản phẩm!")
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy sản phẩm!")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = InventoryManager()
    app.run()
