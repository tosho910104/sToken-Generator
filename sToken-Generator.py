import sys
import secrets
import string
import base64

# Kontrola a automatická inštalácia PyQt5, ak chýba
try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
    from PyQt5 import QtWidgets, QtCore, QtGui


class TokenGenerator(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Slovník preklady (EN / SK)
        self.translations = {
            'en': {
                'windowTitle': "Secure Token Generator",
                'title': "Secure Token Generator",
                'type_label': "Token type:",
                'length_label': "Token length:",
                'generate_button': "Generate token",
                'copy_button': "Copy token",
                'copied_title': "Copy",
                'copied_msg': "Token has been copied to clipboard! 😊",
                'error_title': "Error",
                'error_msg': "No token to copy. 😕",
                'combo_alphanumeric': "Alphanumeric",
                'combo_hex': "Hexadecimal",
                'combo_base64': "Base64",
                'language_label': "Language:"
            },
            'sk': {
                'windowTitle': "Secure Token Generátor",
                'title': "Secure Token Generátor",
                'type_label': "Typ tokenu:",
                'length_label': "Dĺžka tokenu:",
                'generate_button': "Generovať token",
                'copy_button': "Kopírovať token",
                'copied_title': "Kopírovanie",
                'copied_msg': "Token bol skopírovaný do schránky! 😊",
                'error_title': "Chyba",
                'error_msg': "Žiadny token na kopírovanie. 😕",
                'combo_alphanumeric': "Alfanumerický",
                'combo_hex': "Hexadecimálny",
                'combo_base64': "Base64",
                'language_label': "Jazyk:"
            }
        }

        # Načítame jazyk z QSettings (ak nie je uložený, bude SK)
        self.currentLanguage = self.loadLanguage()

        # Inicializácia UI
        self.setGeometry(100, 100, 400, 300)
        self.setupUI()
        self.setLanguage(self.currentLanguage)  # Aplikujeme preklady

    def setupUI(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)

        # 1) Panel na výber jazyka
        lang_layout = QtWidgets.QHBoxLayout()
        self.language_label = QtWidgets.QLabel()  # Text doplníme pri preklade
        self.language_combo = QtWidgets.QComboBox()

        # Pridáme položky do ComboBoxu (angličtina, slovenčina)
        # data() = kód jazyka, zobrazovaný text sa zmení pri preklade
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Slovak", "sk")

        # Nastavíme ComboBox na posledne zvolený jazyk
        if self.currentLanguage == "en":
            self.language_combo.setCurrentIndex(0)
        else:
            self.language_combo.setCurrentIndex(1)

        # Prepojenie zmeny jazyka s metódou
        self.language_combo.currentIndexChanged.connect(self.changeLanguage)

        lang_layout.addWidget(self.language_label)
        lang_layout.addWidget(self.language_combo)
        self.layout.addLayout(lang_layout)

        # 2) Názov aplikácie
        self.title_label = QtWidgets.QLabel()
        self.title_label.setFont(QtGui.QFont("Arial", 18))
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # 3) Výber typu tokenu
        type_layout = QtWidgets.QHBoxLayout()
        self.type_label = QtWidgets.QLabel()
        self.type_combo = QtWidgets.QComboBox()
        type_layout.addWidget(self.type_label)
        type_layout.addWidget(self.type_combo)
        self.layout.addLayout(type_layout)

        # 4) Výber dĺžky tokenu
        length_layout = QtWidgets.QHBoxLayout()
        self.length_label = QtWidgets.QLabel()
        self.length_spin = QtWidgets.QSpinBox()
        self.length_spin.setRange(8, 128)
        self.length_spin.setValue(16)
        length_layout.addWidget(self.length_label)
        length_layout.addWidget(self.length_spin)
        self.layout.addLayout(length_layout)

        # 5) Zobrazenie vygenerovaného tokenu
        token_layout = QtWidgets.QHBoxLayout()
        self.token_edit = QtWidgets.QLineEdit()
        self.token_edit.setReadOnly(True)
        token_layout.addWidget(self.token_edit)
        self.layout.addLayout(token_layout)

        # 6) Tlačidlá
        button_layout = QtWidgets.QHBoxLayout()
        self.generate_button = QtWidgets.QPushButton()
        self.generate_button.clicked.connect(self.generateToken)
        self.copy_button = QtWidgets.QPushButton()
        self.copy_button.clicked.connect(self.copyToken)
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.copy_button)
        self.layout.addLayout(button_layout)

    def translateUI(self):
        """
        Aplikovanie prekladu podľa self.currentLanguage.
        Nastavíme text pre všetky popisy, tlačidlá a hlavičky.
        """
        t = self.translations[self.currentLanguage]

        # Nastavenie titulku okna
        self.setWindowTitle(t['windowTitle'])

        # Nastavenie textov labelov a tlačidiel
        self.language_label.setText(t['language_label'])
        self.title_label.setText(t['title'])
        self.type_label.setText(t['type_label'])
        self.length_label.setText(t['length_label'])
        self.generate_button.setText(t['generate_button'])
        self.copy_button.setText(t['copy_button'])

        # Pretypovanie ComboBoxu pre typ tokenu
        self.type_combo.clear()
        self.type_combo.addItem(t['combo_alphanumeric'])
        self.type_combo.addItem(t['combo_hex'])
        self.type_combo.addItem(t['combo_base64'])

    def changeLanguage(self):
        """
        Volá sa, keď používateľ zmení jazyk v ComboBoxe.
        Získa nový kód jazyka z ComboBoxu a nastaví ho.
        """
        lang_code = self.language_combo.currentData()
        self.setLanguage(lang_code)

    def setLanguage(self, lang_code):
        """
        Uloží jazyk do QSettings a aplikuje preklad.
        """
        self.currentLanguage = lang_code
        settings = QtCore.QSettings("MyCompany", "TokenGenerator")
        settings.setValue("language", lang_code)
        self.translateUI()

    def loadLanguage(self):
        """
        Načítame jazyk z QSettings, ak nie je, predvolene 'sk'.
        """
        settings = QtCore.QSettings("MyCompany", "TokenGenerator")
        return settings.value("language", "sk")

    def generateToken(self):
        token_type = self.type_combo.currentText()
        length = self.length_spin.value()
        token = ""

        # Podľa aktuálneho jazyka rozhodneme, aké reťazce hľadať
        if self.currentLanguage == 'en':
            alpha_text = self.translations['en']['combo_alphanumeric']
            hex_text = self.translations['en']['combo_hex']
            base64_text = self.translations['en']['combo_base64']
        else:
            alpha_text = self.translations['sk']['combo_alphanumeric']
            hex_text = self.translations['sk']['combo_hex']
            base64_text = self.translations['sk']['combo_base64']

        if token_type == alpha_text:  # Alfanumerický / Alphanumeric
            chars = string.ascii_letters + string.digits
            token = ''.join(secrets.choice(chars) for _ in range(length))
        elif token_type == hex_text:  # Hexadecimálny / Hexadecimal
            nbytes = (length + 1) // 2
            token = secrets.token_hex(nbytes)[:length]
        elif token_type == base64_text:  # Base64
            nbytes = length
            token = base64.urlsafe_b64encode(secrets.token_bytes(nbytes)).decode('utf-8').rstrip('=')
            token = token[:length]
        else:
            token = "Unknown token type"  # Rezerva pre prípad, že by niečo nesedelo

        self.token_edit.setText(token)

    def copyToken(self):
        t = self.translations[self.currentLanguage]
        token = self.token_edit.text()
        if token:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(token)
            QtWidgets.QMessageBox.information(self, t['copied_title'], t['copied_msg'])
        else:
            QtWidgets.QMessageBox.warning(self, t['error_title'], t['error_msg'])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Moderný tmavý dizajn aplikácie
    app.setStyleSheet("""
    QWidget {
        background-color: #2C2F33;
        color: #FFFFFF;
        font-family: Arial;
    }
    QPushButton {
        background-color: #7289DA;
        border: none;
        padding: 10px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #5b6eae;
    }
    QLineEdit, QComboBox, QSpinBox {
        background-color: #23272A;
        border: 1px solid #7289DA;
        border-radius: 5px;
        padding: 5px;
    }
    QLabel {
        font-size: 14px;
    }
    """)

    window = TokenGenerator()
    window.show()
    sys.exit(app.exec_())
