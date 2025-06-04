from firebase import firebase
import flet
from flet import Page, Text, ElevatedButton, TextField, Column
import os

firebase = firebase.FirebaseApplication('https://yuztanimasistemi-kolayulasim-default-rtdb.firebaseio.com/',None)

dogrulama1 = 0
dogrulama = 0
def usersistem(page : Page):
    page.title = "Kullanıcı Paneli"
    def userpanel(e):
        metin = ""
        global dogrulama, dogrulama1, konum
        if dogrulama1 == 1:
            if dogrulama == 1:
                metin = f"{username.value.strip()} | Hesap Durumu: Doğrulanmış"
                konum = f"users/dogrulanmis/{username.value.strip()}/"
                emailt.value = f'E-Posta Adresi: {firebase.get(konum, 'email')}'
            else:
                if dogrulama == 0:
                    metin = f"{username.value.strip()} | Hesap Durumu: Doğrulanmamış"
                    konum = f"users/dogrulanmamis/{username.value.strip()}/"
                    emailt.value = f'E-Posta Adresi: {firebase.get(konum, 'email')}'
        t1.value = metin
        if "" == firebase.get(konum, 'email'):
            col.controls = [t1, email, emailonayla]
        else:
            col.controls = [t1, emailt]
        col.update()
    page.update()

    def emailonayla2(e):
        konuum = ""
        if email.value.strip() != "":
            if "@" in email.value.strip():
                if dogrulama == 0:
                    firebase.delete(f"users/dogrulanmamis/{username.value.strip()}",'email')
                    firebase.patch(f"users/dogrulanmamis/{username.value.strip()}",{'email':email.value.strip()})
                    konuum = f"users/dogrulanmamis/{username.value.strip()}"
                    t2 = Text(value="e-Posta Adresiniz Eklendi!")
                    col.controls = [t1,emailt,t2]
                if dogrulama == 1:
                    firebase.delete(f"users/dogrulanmis/{username.value.strip()}",'email')
                    firebase.patch(f"users/dogrulanmis/{username.value.strip()}",{'email':email.value.strip()})
                    konuum = f"users/dogrulanmis/{username.value.strip()}"
                    t2 = Text(value="e-Posta Adresiniz Eklendi!")
                    col.controls = [t1,emailt,t2]
            userpanel(None)
        else:
            t2 = Text(value=firebase.get(konuum,'email'))

        col.update()

    def onaylab1(e):
        global dogrulama
        global dogrulama1
        if username.value.strip() in firebase.get(f'users/dogrulanmis/', ''):
            if ((username.value.strip() == firebase.get(f'users/dogrulanmis/{username.value.strip()}','username')) and
                    (int(password.value.strip()) == firebase.get(f'users/dogrulanmis/{username.value.strip()}','password'))):
                dogrulama1 = 1
                dogrulama = 1
                userpanel(None)


            else:
                t1.value = "T.C. Kimlik Numarası veya Şifre Hatalı!"
        if username.value.strip() in firebase.get(f'users/dogrulanmamis/', ''):
            if ((username.value.strip() == firebase.get(f'users/dogrulanmamis/{username.value.strip()}','username')) and
                    (int(password.value.strip()) == firebase.get(f'users/dogrulanmamis/{username.value.strip()}','password'))):
                dogrulama1 = 1
                dogrulama = 0
                userpanel(None)

            else:
                t1.value = "T.C. Kimlik Numarası veya Şifre Hatalı!"
        if username.value.strip() in firebase.get(f'admin/', ''):
            if (username.value.strip() == firebase.get(f'admin/{username.value.strip()}','username')):
                t1.value = f"Admin Hesabı. Lütfen Admin Paneli Üzerinden Giriş Yapınız."
                dogrulama1 = 0
            else:
                t1.value = "T.C. Kimlik Numarası veya Şifre Hatalı!"

        page.update()



    username = TextField(label="T.C. Kimlik Numarası", hint_text="T.C. Kimlik Numaranızı Giriniz")
    password = TextField(label="Şifre", hint_text="Şifrenizi Giriniz", password=True)
    email = TextField(label="e-Posta Adresi",hint_text="e-Posta Adresinizi Giriniz")
    t1 = Text(value="")
    emailt = Text(value="")

    onaylab1 = ElevatedButton(text="Giriş Yap", on_click=onaylab1, width=page.width)
    emailonayla = ElevatedButton(text="e-Posta Adresini Onayla", on_click=emailonayla2, width=page.width)

    col = Column(controls=[username, password, t1, onaylab1], width=page.width, height=page.height, alignment="center",horizontal_alignment="center")

    page.controls.append(col)
    page.update()

flet.app(target=usersistem)