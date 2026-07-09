import os
from kivy.config import Config
from kivy.utils import platform

# Responsive Windows view on PC / Automatic on Mobile
if platform not in ('android', 'ios'):
    Config.set('graphics', 'width', '450')  
    Config.set('graphics', 'height', '750')
    Config.set('graphics', 'resizable', False)

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.clock import Clock
from kivy.core.window import Window
import sqlite3
from datetime import datetime
from plyer import notification

# =========================================================
# 🔐 SCREEN 1: LOGIN SCREEN (WITH REMEMBER ME & TAB)
# =========================================================
class LoginScreen(MDScreen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.md_bg_color = [0.95, 0.96, 0.98, 1]
        
        main_layout = MDBoxLayout(orientation="vertical", padding=30, spacing=20, size_hint_y=None, pos_hint={"center_x": 0.5, "center_y": 0.5})
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        login_card = MDCard(
            orientation="vertical", padding=[20, 35, 20, 35], spacing=18,
            size_hint_x=0.9, size_hint_y=None, height="460dp", pos_hint={"center_x": 0.5},
            elevation=2, radius=[16, 16, 16, 16], md_bg_color=[1, 1, 1, 1]
        )
        
        # Title
        login_card.add_widget(MDLabel(text="Login", font_style="H5", bold=True, halign="center", height="40dp", size_hint_y=None))
        
        # Updated Sub-label text as requested
        login_card.add_widget(MDLabel(text="Please enter your username & password", font_style="Caption", halign="center", theme_text_color="Secondary", height="20dp", size_hint_y=None))
        
        self.username = MDTextField(hint_text="Username", mode="rectangle", icon_left="account", write_tab=False)
        self.password = MDTextField(hint_text="Password", mode="rectangle", icon_left="lock", password=True, write_tab=False)
        
        self.username.bind(on_text_validate=self.focus_password)
        self.password.bind(on_text_validate=self.verify_login)
        
        login_card.add_widget(self.username)
        login_card.add_widget(self.password)
        
        # Remember Me Layout with Checkbox
        remember_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="40dp", spacing=5)
        self.remember_checkbox = MDCheckbox(size_hint=(None, None), size=("36dp", "36dp"), pos_hint={"center_y": 0.5})
        remember_label = MDLabel(text="Remember this user", font_style="Body2", theme_text_color="Secondary", pos_hint={"center_y": 0.5})
        
        remember_layout.add_widget(self.remember_checkbox)
        remember_layout.add_widget(remember_label)
        login_card.add_widget(remember_layout)
        
        login_btn = MDFillRoundFlatButton(text="Login Now", size_hint_x=1, height="48dp")
        login_btn.bind(on_release=self.verify_login)
        login_card.add_widget(login_btn)
        
        main_layout.add_widget(login_card)
        self.add_widget(main_layout)

    def on_pre_enter(self):
        """Pre-fill username if 'Remember Me' was checked previously"""
        saved_user, remember_status = self.app.get_remembered_user()
        if remember_status == 1:
            self.username.text = saved_user
            self.remember_checkbox.active = True
        else:
            self.username.text = ""
            self.remember_checkbox.active = False

    def focus_password(self, instance):
        self.password.focus = True

    def verify_login(self, instance):
        stored_user, stored_pass = self.app.get_credentials()
        if self.username.text.strip() == stored_user and self.password.text.strip() == stored_pass:
            # Save or clear remember state
            remember_val = 1 if self.remember_checkbox.active else 0
            self.app.update_remember_me(self.username.text.strip(), remember_val)
            
            self.manager.current = "dashboard_screen"
            self.app.dashboard_screen.update_stats()
        else:
            dialog = MDDialog(title="Access Denied", text="Invalid username or password.", size_hint=(0.8, None))
            dialog.open()

# =========================================================
# 🏛️ SCREEN 2: MAIN DASHBOARD SCREEN (4 BOXES GRID)
# =========================================================
class DashboardScreen(MDScreen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.md_bg_color = [0.95, 0.96, 0.98, 1]
        
        base_layout = MDBoxLayout(orientation="vertical")
        
        toolbar = MDTopAppBar(title="Scholarship Main Hub", anchor_title="left", elevation=2, md_bg_color=self.app.theme_cls.primary_color)
        toolbar.right_action_items = [["logout", lambda x: self.logout()]]
        base_layout.add_widget(toolbar)
        
        scroll = MDScrollView()
        content = MDBoxLayout(orientation="vertical", padding=20, spacing=20, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        content.add_widget(MDLabel(text="Welcome Back, Admin!", font_style="H6", bold=True, height="30dp", size_hint_y=None))
        
        grid = MDGridLayout(cols=2, spacing=15, size_hint_y=None, height="260dp")
        
        card1 = MDCard(orientation="vertical", padding=15, elevation=1, radius=12, md_bg_color=[1, 1, 1, 1], on_release=lambda x: self.navigate_to("entry_screen"))
        card1.add_widget(MDIconButton(icon="plus-box", icon_size="32dp", theme_text_color="Custom", text_color=self.app.theme_cls.primary_color, pos_hint={"center_x": 0.5}))
        card1.add_widget(MDLabel(text="Add Entry", font_style="Subtitle2", bold=True, halign="center"))
        
        card2 = MDCard(orientation="vertical", padding=15, elevation=1, radius=12, md_bg_color=[1, 1, 1, 1], on_release=lambda x: self.navigate_to("entry_screen"))
        self.lbl_total = MDLabel(text="0", font_style="H4", bold=True, halign="center", theme_text_color="Custom", text_color=self.app.theme_cls.primary_color)
        card2.add_widget(self.lbl_total)
        card2.add_widget(MDLabel(text="Total Saved", font_style="Subtitle2", halign="center", theme_text_color="Secondary"))
        
        card3 = MDCard(orientation="vertical", padding=15, elevation=1, radius=12, md_bg_color=[1, 1, 1, 1], on_release=lambda x: self.navigate_to("entry_screen"))
        self.lbl_expired = MDLabel(text="0", font_style="H4", bold=True, halign="center", theme_text_color="Custom", text_color=[0.85, 0, 0, 1])
        card3.add_widget(self.lbl_expired)
        card3.add_widget(MDLabel(text="Expired Data", font_style="Subtitle2", halign="center", theme_text_color="Secondary"))
        
        card4 = MDCard(orientation="vertical", padding=15, elevation=1, radius=12, md_bg_color=[1, 1, 1, 1], on_release=lambda x: self.navigate_to("settings_screen"))
        card4.add_widget(MDIconButton(icon="cog", icon_size="32dp", theme_text_color="Custom", text_color=[0.4, 0.4, 0.4, 1], pos_hint={"center_x": 0.5}))
        card4.add_widget(MDLabel(text="Settings Panel", font_style="Subtitle2", bold=True, halign="center"))
        
        grid.add_widget(card1)
        grid.add_widget(card2)
        grid.add_widget(card3)
        grid.add_widget(card4)
        content.add_widget(grid)
        
        backend_btn = MDFillRoundFlatButton(text="Run in Backend (Hide)", size_hint_x=1, height="48dp", md_bg_color=[0.2, 0.6, 0.2, 1])
        backend_btn.bind(on_release=self.app.minimize_app)
        content.add_widget(backend_btn)
        
        base_layout.add_widget(scroll)
        scroll.add_widget(content)
        self.add_widget(base_layout)

    def navigate_to(self, screen_name):
        self.manager.current = screen_name

    def logout(self):
        self.manager.current = "login_screen"

    def update_stats(self):
        conn = sqlite3.connect(self.app.conn_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM scholarships")
        self.lbl_total.text = str(cursor.fetchone()[0])
        
        cursor.execute("SELECT deadline FROM scholarships")
        rows = cursor.fetchall()
        expired_count = 0
        today = datetime.now().date()
        for row in rows:
            try:
                d_date = datetime.strptime(row[0], "%d-%m-%Y").date()
                if (d_date - today).days < 0:
                    expired_count += 1
            except:
                pass
        self.lbl_expired.text = str(expired_count)
        conn.close()

# =========================================================
# 📝 SCREEN 3: APPLICATION DATA ENTRY SCREEN
# =========================================================
class EntryScreen(MDScreen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        
        base_layout = MDBoxLayout(orientation="vertical", md_bg_color=[0.95, 0.96, 0.98, 1])
        toolbar = MDTopAppBar(title="Data Records Studio", anchor_title="left", elevation=2, md_bg_color=self.app.theme_cls.primary_color)
        toolbar.left_action_items = [["arrow-left", lambda x: self.go_back()]]
        base_layout.add_widget(toolbar)
        
        main_scroll = MDScrollView()
        dashboard_layout = MDBoxLayout(orientation="vertical", padding=15, spacing=15, size_hint_y=None)
        dashboard_layout.bind(minimum_height=dashboard_layout.setter('height'))
        
        add_box_card = MDCard(orientation="vertical", padding=[15, 20, 15, 20], spacing=15, size_hint_y=None, height="340dp", elevation=1, radius=12, md_bg_color=[1, 1, 1, 1])
        add_box_card.add_widget(MDLabel(text="Create New Entry", font_style="Subtitle1", bold=True, height="30dp", size_hint_y=None))
        
        self.app.name_input = MDTextField(hint_text="Scholarship Name", mode="rectangle", icon_left="school", write_tab=False)
        self.app.country_input = MDTextField(hint_text="Target Country", mode="rectangle", icon_left="earth", write_tab=False)
        self.app.deadline_input = MDTextField(hint_text="Deadline (DD-MM-YYYY)", mode="rectangle", icon_left="calendar-clock", write_tab=False)
        
        add_box_card.add_widget(self.app.name_input)
        add_box_card.add_widget(self.app.country_input)
        add_box_card.add_widget(self.app.deadline_input)
        
        btn_box = MDBoxLayout(spacing=10, size_hint_y=None, height="45dp", padding=[0, 5, 0, 0])
        save_btn = MDFillRoundFlatButton(text="Save Record", size_hint_x=0.5)
        save_btn.bind(on_release=self.app.save_data)
        refresh_btn = MDFillRoundFlatButton(text="Refresh", size_hint_x=0.5, md_bg_color=[0.45, 0.45, 0.48, 1])
        refresh_btn.bind(on_release=self.app.load_list)
        btn_box.add_widget(save_btn)
        btn_box.add_widget(refresh_btn)
        add_box_card.add_widget(btn_box)
        
        list_box_card = MDCard(orientation="vertical", padding=[15, 20, 15, 20], spacing=10, size_hint_y=None, height="400dp", elevation=1, radius=12, md_bg_color=[1, 1, 1, 1])
        list_box_card.add_widget(MDLabel(text="Active Tracking Feed", font_style="Subtitle1", bold=True, height="30dp", size_hint_y=None))
        
        inner_scroll = MDScrollView()
        self.app.list_container = MDList()
        inner_scroll.add_widget(self.app.list_container)
        list_box_card.add_widget(inner_scroll)
        
        dashboard_layout.add_widget(add_box_card)
        dashboard_layout.add_widget(list_box_card)
        main_scroll.add_widget(dashboard_layout)
        base_layout.add_widget(main_scroll)
        self.add_widget(base_layout)

    def go_back(self):
        self.app.dashboard_screen.update_stats()
        self.manager.current = "dashboard_screen"

# =========================================================
# ⚙️ SCREEN 4: CREDENTIALS SETTINGS SCREEN
# =========================================================
class SettingsScreen(MDScreen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.md_bg_color = [0.95, 0.96, 0.98, 1]
        
        base_layout = MDBoxLayout(orientation="vertical")
        toolbar = MDTopAppBar(title="System Access Settings", anchor_title="left", elevation=2, md_bg_color=self.app.theme_cls.primary_color)
        toolbar.left_action_items = [["arrow-left", lambda x: self.go_back()]]
        base_layout.add_widget(toolbar)
        
        container = MDBoxLayout(orientation="vertical", padding=20, spacing=20, size_hint_y=None, pos_hint={"center_y": 0.5})
        container.bind(minimum_height=container.setter('height'))
        
        settings_card = MDCard(orientation="vertical", padding=20, spacing=15, radius=12, elevation=1, md_bg_color=[1, 1, 1, 1], size_hint_y=None)
        settings_card.bind(minimum_height=settings_card.setter('height'))
        
        settings_card.add_widget(MDLabel(text="Modify Credentials", font_style="H6", bold=True, height="30dp", size_hint_y=None))
        
        self.new_username = MDTextField(hint_text="New Username", mode="rectangle", icon_left="account-edit", write_tab=False)
        self.new_password = MDTextField(hint_text="New Password", mode="rectangle", icon_left="lock-reset", password=True, write_tab=False)
        
        settings_card.add_widget(self.new_username)
        settings_card.add_widget(self.new_password)
        
        save_settings_btn = MDFillRoundFlatButton(text="Update Credentials", size_hint_x=1, height="48dp")
        save_settings_btn.bind(on_release=self.update_auth)
        settings_card.add_widget(save_settings_btn)
        
        container.add_widget(settings_card)
        base_layout.add_widget(container)
        self.add_widget(base_layout)

    def on_pre_enter(self):
        current_user, current_pass = self.app.get_credentials()
        self.new_username.text = current_user
        self.new_password.text = current_pass

    def update_auth(self, instance):
        u = self.new_username.text.strip()
        p = self.new_password.text.strip()
        if u and p:
            conn = sqlite3.connect(self.app.conn_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE auth_settings SET username=?, password=? WHERE id=1", (u, p))
            conn.commit()
            conn.close()
            self.app.show_dialog("Updated", "Security configurations updated successfully.")
            self.manager.current = "dashboard_screen"
        else:
            self.app.show_dialog("Error", "Fields cannot be blank.")

    def go_back(self):
        self.manager.current = "dashboard_screen"

# =========================================================
# ⚙     MAIN APPLICATION CORE ENGINE
# =========================================================
class MastersScholarshipApp(MDApp):
    def build(self):
        self.title = "Master's Scholarship App"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.primary_hue = "700"
        self.theme_cls.theme_style = "Light"
        
        self.db_setup()
        
        self.sm = MDScreenManager()
        self.dashboard_screen = DashboardScreen(app_instance=self, name="dashboard_screen")
        
        self.sm.add_widget(LoginScreen(app_instance=self, name="login_screen"))
        self.sm.add_widget(self.dashboard_screen)
        self.sm.add_widget(EntryScreen(app_instance=self, name="entry_screen"))
        self.sm.add_widget(SettingsScreen(app_instance=self, name="settings_screen"))
        
        self.load_list()
        Clock.schedule_interval(self.check_background_deadlines, 60)
        
        return self.sm

    def minimize_app(self, instance):
        if platform not in ('android', 'ios'):
            Window.minimize()  
        else:
            try:
                from android import activity
                activity.moveTaskToBack(True)
            except Exception as e:
                print("Android intent minimize error:", e)

    def check_background_deadlines(self, dt):
        conn = sqlite3.connect(self.conn_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, country, deadline FROM scholarships")
        rows = cursor.fetchall()
        conn.close()
        
        today = datetime.now().date()
        for row in rows:
            name, country, deadline_str = row
            try:
                deadline_date = datetime.strptime(deadline_str, "%d-%m-%Y").date()
                remaining_days = (deadline_date - today).days
                if 0 <= remaining_days <= 3:
                    self.send_notification("⚠️ Urgent Deadline Alert", f"'{name.upper()}' ({country}) closes in {remaining_days} days!")
            except:
                pass

    def db_setup(self):
        if platform == 'android':
            from android.storage import app_storage_dir
            db_path = os.path.join(app_storage_dir(), "scholarships.db")
        else:
            db_path = "scholarships.db"
            
        self.conn_path = db_path
        conn = sqlite3.connect(self.conn_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS scholarships (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, country TEXT, deadline TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS auth_settings (id INTEGER PRIMARY KEY, username TEXT, password TEXT, remember_me INTEGER DEFAULT 0)")
        
        cursor.execute("SELECT COUNT(*) FROM auth_settings")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO auth_settings (id, username, password, remember_me) VALUES (1, 'admin', 'admin123', 0)")
        else:
            try:
                cursor.execute("ALTER TABLE auth_settings ADD COLUMN remember_me INTEGER DEFAULT 0")
            except:
                pass
                
        conn.commit()
        conn.close()

    def get_credentials(self):
        conn = sqlite3.connect(self.conn_path)
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM auth_settings WHERE id=1")
        row = cursor.fetchone()
        conn.close()
        return row[0], row[1]

    def get_remembered_user(self):
        conn = sqlite3.connect(self.conn_path)
        cursor = conn.cursor()
        cursor.execute("SELECT username, remember_me FROM auth_settings WHERE id=1")
        row = cursor.fetchone()
        conn.close()
        return row[0], row[1]

    def update_remember_me(self, username, remember_val):
        conn = sqlite3.connect(self.conn_path)
        cursor = conn.cursor()
        if remember_val == 1:
            cursor.execute("UPDATE auth_settings SET username=?, remember_me=? WHERE id=1", (username, remember_val))
        else:
            cursor.execute("UPDATE auth_settings SET remember_me=? WHERE id=1", (remember_val,))
        conn.commit()
        conn.close()

    def save_data(self, instance):
        name = self.name_input.text.strip()
        country = self.country_input.text.strip()
        deadline = self.deadline_input.text.strip()
        
        if name and country and deadline:
            try:
                datetime.strptime(deadline, "%d-%m-%Y")
                conn = sqlite3.connect(self.conn_path)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO scholarships (name, country, deadline) VALUES (?, ?, ?)", (name, country, deadline))
                conn.commit()
                conn.close()
                
                self.name_input.text = ""
                self.country_input.text = ""
                self.deadline_input.text = ""
                self.load_list()
                self.show_dialog("Success", "Scholarship saved successfully.")
            except ValueError:
                self.show_dialog("Date Error", "Use DD-MM-YYYY format.")
        else:
            self.show_dialog("Alert", "All fields are required.")

    def send_notification(self, title, message):
        try:
            notification.notify(title=title, message=message, app_name="Master's Scholarship", timeout=5)
        except Exception:
            pass

    def load_list(self, *args):
        if not hasattr(self, 'list_container'):
            return
        self.list_container.clear_widgets()
        conn = sqlite3.connect(self.conn_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scholarships")
        rows = cursor.fetchall()
        conn.close()
        
        today = datetime.now().date()
        for row in rows:
            id_num, name, country, deadline_str = row
            status_tag = ""
            text_color = [0, 0, 0, 1] 
            
            try:
                deadline_date = datetime.strptime(deadline_str, "%d-%m-%Y").date()
                remaining_days = (deadline_date - today).days
                
                if remaining_days < 0:
                    status_tag = "[ EXPIRED ]"
                    text_color = [0.5, 0.5, 0.5, 1] 
                elif remaining_days <= 3:
                    status_tag = f"URGENT: Only {remaining_days} Days Left!"
                    text_color = [0.85, 0, 0, 1] 
                elif remaining_days >= 10:
                    status_tag = f"{remaining_days} Days Left (Safe)"
                    text_color = [0.1, 0.55, 0.1, 1] 
                else:
                    status_tag = f"{remaining_days} Days Left"
                    text_color = [0.9, 0.45, 0, 1] 
            except Exception:
                status_tag = f"Target: {deadline_str}"

            item = ThreeLineAvatarIconListItem(
                text=f"{name.upper()} ({country})",
                secondary_text=status_tag,
                tertiary_text=f"End Date: {deadline_str}",
                secondary_text_color=text_color,
                secondary_theme_text_color="Custom"
            )
            
            left_icon = IconLeftWidget(icon="bookmark-check", theme_text_color="Custom", text_color=self.theme_cls.primary_color)
            item.add_widget(left_icon)
            
            right_icon = IconRightWidget(icon="trash-can-outline", theme_text_color="Custom", text_color=[0.8, 0.2, 0.2, 1],
                                         on_release=lambda x, s_id=id_num: self.delete_scholarship(s_id))
            item.add_widget(right_icon)
            
            self.list_container.add_widget(item)

    def delete_scholarship(self, s_id):
        conn = sqlite3.connect(self.conn_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scholarships WHERE id=?", (s_id,))
        conn.commit()
        conn.close()
        self.load_list()
        self.dashboard_screen.update_stats()

    def show_dialog(self, title, text):
        dialog = MDDialog(title=title, text=text, size_hint=(0.8, None))
        dialog.open()

if __name__ == "__main__":
    MastersScholarshipApp().run()