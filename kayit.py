from firebase import firebase
import flet
from flet import Page, Text, ElevatedButton, TextField, Column


firebase = firebase.FirebaseApplication('https://yuztanimasistemi-kolayulasim-default-rtdb.firebaseio.com/',None)
def kayitsistemi(page: Page):

    page.title = "Kayıt Sistemi"

    def kayitol(e):
        col.controls = [username, password, passwordonayla, t1, onaylab2]
        col.update()

    def onaylab2(e):
        if (username.value.strip() in firebase.get(f"users/dogrulanmamis/", '') or
                username.value.strip() in firebase.get(f"users/dogrulanmis/", '')):
            t1.value = 'Böyle Bir Hesap Zaten Mevcut!'

        else:
            if username.value.strip().isnumeric() == True:
                if password.value.strip().isnumeric() == True:
                    if (len(username.value.strip()) == 11):
                        rakamtoplami = 0
                        for i in username.value.strip():
                            rakamtoplami += int(i)
                        tcdogrulama = int(rakamtoplami) - int(username.value.strip()[-1])
                        if str(tcdogrulama)[-1] == username.value.strip()[-1]:
                            if password.value == passwordonayla.value:

                                data = {'username': username.value.strip(), 'password': int(password.value.strip()),
                                        'email': ''}
                                firebase.patch(f"users/dogrulanmamis/{username.value.strip()}", data)
                                t1.value = 'Hesabınız Oluşturuldu! Lütfen Giriş Yapınız!'
                            else:
                                t1.value = 'Şifreniz Yalnızca Rakamlardan Oluşmalıdır, Lütfen Tekrar Deneyiniz!'
                        else:
                            t1.value = 'Şifreler Uyuşmuyor. Tekrar Deneyiniz!'
                    else:
                        t1.value = 'T.C. Kimlik Numarası Geçersiz, Numarayı Doğru Girdiğinizden Emin Olun!'
            else:
                t1.value = 'T.C. Kimlik Numaranız İçin Lütfen Sadece Sayıları Kullanınız'
        t1.update()

    username = TextField(label="T.C. Kimlik Numarası", hint_text="T.C. Kimlik Numaranızı Giriniz")
    password = TextField(label="Şifre", hint_text="Şifreniz Sadece Rakamlardan Oluşmalıdır",password=True)
    passwordonayla = TextField(label="Şifrenizi Onaylayın", hint_text="Şifrenizi Tekrar Giriniz", password=True)
    t1 = Text(value="")

    b2 = ElevatedButton(text="Kayıt Ol", on_click=kayitol, width=page.width)

    onaylab2 = ElevatedButton(text="Onayla",on_click=onaylab2, width=page.width)


    col = Column(controls=[t1,b2],width=page.width,height=page.height,alignment="center", horizontal_alignment="center")

    page.controls.append(col)
    page.update()

flet.app(target=kayitsistemi)