"""
Графический интерфейс пользователя (Tkinter)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from models import TaskStatus

class TaskManagerGUI:
    """Главное окно приложения"""

    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Tk()
        self.window.title("Менеджер задач")
        self.window.geometry("1200x700")
        self.window.configure(bg='#f0f0f0')

        self.edit_id = None
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        """Создание всех виджетов"""
        # Заголовок
        title_frame = tk.Frame(self.window, bg='#2c3e50', height=70)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="📋 Менеджер задач",
                font=('Arial', 20, 'bold'), bg='#2c3e50', fg='white').pack(pady=15)

        # Основной контейнер
        main = tk.Frame(self.window, bg='#f0f0f0')
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель - форма
        left = tk.Frame(main, bg='white', relief=tk.RAISED, bd=1)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), ipadx=10, ipady=10)
        self.create_form(left)

        # Правая панель - список задач
        right = tk.Frame(main, bg='white', relief=tk.RAISED, bd=1)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.create_task_list(right)

        # Нижняя панель - кнопки
        bottom = tk.Frame(self.window, bg='#f0f0f0', height=60)
        bottom.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.create_buttons(bottom)

    def create_form(self, parent):
        """Форма добавления/редактирования"""
        tk.Label(parent, text="Добавить/Редактировать",
                font=('Arial', 14, 'bold'), bg='white').pack(pady=(10, 20))

        # Название
        tk.Label(parent, text="Название:", font=('Arial', 10), bg='white').pack(anchor=tk.W, padx=10)
        self.title_entry = tk.Entry(parent, width=35, font=('Arial', 10))
        self.title_entry.pack(padx=10, pady=(0, 10), fill=tk.X)

        # Описание
        tk.Label(parent, text="Описание:", font=('Arial', 10), bg='white').pack(anchor=tk.W, padx=10)
        self.desc_text = scrolledtext.ScrolledText(parent, width=35, height=8, font=('Arial', 10))
        self.desc_text.pack(padx=10, pady=(0, 10), fill=tk.X)

        # Приоритет
        tk.Label(parent, text="Приоритет:", font=('Arial', 10), bg='white').pack(anchor=tk.W, padx=10)
        self.priority_var = tk.StringVar(value="Средний")
        priority_frame = tk.Frame(parent, bg='white')
        priority_frame.pack(padx=10, pady=(0, 10))

        for p in ["Низкий", "Средний", "Высокий"]:
            tk.Radiobutton(priority_frame, text=p, variable=self.priority_var,
                          value=p, bg='white').pack(side=tk.LEFT, padx=5)

        # Статус
        tk.Label(parent, text="Статус:", font=('Arial', 10), bg='white').pack(anchor=tk.W, padx=10)
        self.status_var = tk.StringVar(value="Нужно сделать")
        status_frame = tk.Frame(parent, bg='white')
        status_frame.pack(padx=10, pady=(0, 10))

        for s in ["Нужно сделать", "В процессе", "Готово"]:
            tk.Radiobutton(status_frame, text=s, variable=self.status_var,
                          value=s, bg='white').pack(side=tk.LEFT, padx=5)

        # Кнопки формы
        btn_frame = tk.Frame(parent, bg='white')
        btn_frame.pack(pady=10)

        self.add_btn = tk.Button(btn_frame, text="➕ Добавить", command=self.add_task,
                                bg='#27ae60', fg='white', font=('Arial', 10, 'bold'), padx=15, pady=5)
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.update_btn = tk.Button(btn_frame, text="✏️ Обновить", command=self.update_task,
                                   bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                                   padx=15, pady=5, state=tk.DISABLED)
        self.update_btn.pack(side=tk.LEFT, padx=5)

        self.cancel_btn = tk.Button(btn_frame, text="❌ Отмена", command=self.cancel_edit,
                                   bg='#95a5a6', fg='white', font=('Arial', 10, 'bold'),
                                   padx=15, pady=5, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)

    def create_task_list(self, parent):
        """Таблица задач"""
        # Панель фильтров
        filter_frame = tk.Frame(parent, bg='white', height=80)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        filter_frame.pack_propagate(False)

        tk.Label(filter_frame, text="Поиск:", bg='white').pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(filter_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.refresh_list())

        tk.Label(filter_frame, text="Статус:", bg='white').pack(side=tk.LEFT, padx=(20, 5))
        self.status_filter = ttk.Combobox(filter_frame, values=["Все", "Нужно сделать", "В процессе", "Готово"],
                                         width=15, state='readonly')
        self.status_filter.set("Все")
        self.status_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_list())
        self.status_filter.pack(side=tk.LEFT, padx=5)

        tk.Label(filter_frame, text="Приоритет:", bg='white').pack(side=tk.LEFT, padx=(20, 5))
        self.priority_filter = ttk.Combobox(filter_frame, values=["Все", "Низкий", "Средний", "Высокий"],
                                           width=15, state='readonly')
        self.priority_filter.set("Все")
        self.priority_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_list())
        self.priority_filter.pack(side=tk.LEFT, padx=5)

        # Таблица
        columns = ("ID", "Название", "Приоритет", "Статус", "Дата")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", height=18)

        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column("ID", width=80)
        self.tree.column("Название", width=250)
        self.tree.column("Приоритет", width=100)
        self.tree.column("Статус", width=120)
        self.tree.column("Дата", width=150)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

    def create_buttons(self, parent):
        """Кнопки действий"""
        btn_frame = tk.Frame(parent, bg='#f0f0f0')
        btn_frame.pack(expand=True)

        buttons = [
            ("🗑️ Удалить", self.delete_task, '#e74c3c'),
            ("↩️ Отменить", self.undo_action, '#f39c12'),
            ("💾 Сохранить", self.save_tasks, '#2ecc71'),
            ("📂 Загрузить", self.load_tasks, '#3498db'),
            ("ℹ️ О программе", self.show_about, '#9b59b6'),
            ("🚪 Выход", self.exit_app, '#e74c3c')
        ]

        for text, cmd, color in buttons:
            btn = tk.Button(btn_frame, text=text, command=cmd, bg=color,
                          fg='white', font=('Arial', 10, 'bold'), padx=20, pady=5)
            btn.pack(side=tk.LEFT, padx=5)

    def add_task(self):
        """Добавление задачи"""
        title = self.title_entry.get().strip()
        desc = self.desc_text.get("1.0", tk.END).strip()
        priority = self.priority_var.get()

        if not title:
            messagebox.showwarning("Ошибка", "Введите название задачи")
            return

        try:
            self.controller.add_task(title, desc, priority)
            self.clear_form()
            self.refresh_list()
            messagebox.showinfo("Успех", "Задача добавлена")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def update_task(self):
        """Обновление задачи"""
        if not self.edit_id:
            return

        title = self.title_entry.get().strip()
        desc = self.desc_text.get("1.0", tk.END).strip()
        priority = self.priority_var.get()
        status = self.status_var.get()

        if not title:
            messagebox.showwarning("Ошибка", "Введите название задачи")
            return

        try:
            self.controller.update_task(self.edit_id, title=title, description=desc,
                                       priority=priority, status=status)
            self.cancel_edit()
            self.refresh_list()
            messagebox.showinfo("Успех", "Задача обновлена")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def delete_task(self):
        """Удаление задачи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите задачу")
            return

        if messagebox.askyesno("Подтверждение", "Удалить задачу?"):
            item = self.tree.item(selected[0])
            task_id = item['values'][0]

            if self.controller.delete_task(task_id):
                self.refresh_list()
                messagebox.showinfo("Успех", "Задача удалена")

    def undo_action(self):
        """Отмена действия"""
        result = self.controller.undo()
        self.refresh_list()
        messagebox.showinfo("Отмена", result)

    def save_tasks(self):
        """Сохранение задач"""
        from utils import JSONHandler
        try:
            handler = JSONHandler()
            handler.save(self.controller.get_all_tasks())
            messagebox.showinfo("Успех", "Задачи сохранены")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def load_tasks(self):
        """Загрузка задач"""
        from utils import JSONHandler
        try:
            handler = JSONHandler()
            tasks = handler.load()

            self.controller.clear()
            for task in tasks:
                self.controller.add_task(task.get_title(), task.get_description(), task.get_priority())
                if task.get_status() != TaskStatus.TO_DO:
                    self.controller.update_task(task.get_id(), status=task.get_status())

            self.refresh_list()
            messagebox.showinfo("Успех", f"Загружено {len(tasks)} задач")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def on_select(self, event):
        """Выбор задачи из списка"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            task_id = item['values'][0]
            task = self.controller.get_task_by_id(task_id)

            if task:
                self.edit_id = task_id
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, task.get_title())

                self.desc_text.delete("1.0", tk.END)
                self.desc_text.insert("1.0", task.get_description())

                self.priority_var.set(task.get_priority())
                self.status_var.set(TaskStatus.get_russian(task.get_status()))

                self.add_btn.config(state=tk.DISABLED)
                self.update_btn.config(state=tk.NORMAL)
                self.cancel_btn.config(state=tk.NORMAL)

    def cancel_edit(self):
        """Отмена редактирования"""
        self.clear_form()
        self.edit_id = None
        self.add_btn.config(state=tk.NORMAL)
        self.update_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.DISABLED)

    def clear_form(self):
        """Очистка формы"""
        self.title_entry.delete(0, tk.END)
        self.desc_text.delete("1.0", tk.END)
        self.priority_var.set("Средний")
        self.status_var.set("Нужно сделать")

    def refresh_list(self):
        """Обновление списка задач"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        tasks = self.controller.get_all_tasks()

        # Поиск
        search = self.search_entry.get().strip()
        if search:
            tasks = self.controller.search(search)

        # Фильтр статуса
        status_filter = self.status_filter.get()
        if status_filter != "Все":
            tasks = [t for t in tasks if TaskStatus.get_russian(t.get_status()) == status_filter]

        # Фильтр приоритета
        priority_filter = self.priority_filter.get()
        if priority_filter != "Все":
            tasks = [t for t in tasks if t.get_priority() == priority_filter]

        # Сортировка по приоритету
        tasks.sort(key=lambda x: x.get_priority_value(), reverse=True)

        for task in tasks:
            self.tree.insert("", tk.END, values=(
                task.get_id(),
                task.get_title(),
                task.get_priority(),
                TaskStatus.get_russian(task.get_status()),
                task.get_created_at()
            ))

    def show_about(self):
        """О программе"""
        messagebox.showinfo("О программе",
                           "Менеджер задач v1.0\n\nПриложение для управления задачами\n"
                           "С использованием ООП, MVC, очередей/стеков и JSON")

    def exit_app(self):
        """Выход"""
        if messagebox.askyesno("Выход", "Вы уверены?"):
            self.window.quit()

    def run(self):
        """Запуск приложения"""
        self.window.mainloop()
