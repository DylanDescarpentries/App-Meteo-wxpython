import os
import wx
import requests
import json
from gtts import gTTS
import pygame

class MyFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(MyFrame, self).__init__(*args, **kw)

        icon = wx.Icon("logo.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.panel = wx.Panel(self)

        # pour la fonction attendre
        self.clock = pygame.time.Clock()

        # Menu barre
        self.menubar = wx.MenuBar()
        self.fichier_menu = wx.Menu()
        self.parametre_menu = wx.Menu()

        self.fichier_menu.Append(
            wx.ID_EXIT, 'Quitter', 'Quitter l\'application')
        self.menubar.Append(self.fichier_menu, 'Fichier')

        self.id_dark_theme = wx.NewId()

        self.parametre_menu.Append(self.id_dark_theme,
                                   'theme sombre', 'Paramêtre')
        self.menubar.Append(self.parametre_menu, 'Paramètre')

        self.SetMenuBar(self.menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.darktheme, id=self.id_dark_theme)

        #Création des éléments de l'interface:

        # # Création du tableaux qui affichera les données de l'API
        self.list_ctrl = wx.ListCtrl(self.panel, style=wx.LC_REPORT)
        self.list_ctrl.InsertColumn(0, 'VILLE')
        self.list_ctrl.InsertColumn(1, 'TEMERATURE')
        self.list_ctrl.InsertColumn(3, 'RESSENTI')
        self.list_ctrl.InsertColumn(3, 'DESCRIPTION')
        self.list_ctrl.InsertColumn(4, 'HUMIDITE')

        ## Création des éléments interactif de l'interface
        self.label_ville = wx.StaticText(self.panel, label="Ville :", pos=(10, 10))
        self.ville = wx.TextCtrl(
        self.panel,  style=wx.TE_MULTILINE, size=(80, 20))

        self.meteo = wx.Button(
        self.panel, label="play", pos=(10, 10))
        self.meteo.Bind(wx.EVT_BUTTON, self.on_meteo)

        # Ajouter les éléments de l'interface
        sizer = wx.GridBagSizer(vgap=0, hgap=0)
        sizer.Add(self.label_ville, pos=(1, 0), flag=wx.ALL, border=5)
        sizer.Add(self.ville, pos=(1, 1), span=(1, 3), flag=wx.EXPAND | wx.ALL, border=10)
        sizer.Add(self.meteo, pos=(1, 4), flag=wx.ALL, border=10)

        sizer.Add(self.list_ctrl, pos=(3, 0), span=(1, 4), flag=wx.EXPAND | wx.ALL, border=5)

        self.panel.SetSizer(sizer)
        self.panel.Layout()

        # Fichier audio nécessaire au fonctionnement du widget
        self.fichier_audio = os.path.abspath("output.mp3")
        self.audio_erreur = os.path.abspath("audio_erreur.mp3")

        self.Show(True)

    def OnQuit(self, event):
        self.Close()

    def darktheme(self, event):
        couleur_fond = wx.Colour(15, 15, 15)
        couleur_texte_entree = wx.Colour(couleur_fond)
        couleur_button = wx.Colour(34, 34, 34)
        self.panel.SetBackgroundColour(couleur_fond)

        # couleur texte du texte des éléments
        self.label_ville.SetForegroundColour(wx.Colour(255, 255, 255))
        self.ville.SetForegroundColour(wx.Colour(255, 255, 255))
        self.meteo.SetForegroundColour(wx.Colour(255, 255, 255))
        self.list_ctrl.SetForegroundColour(wx.Colour(255, 255, 25))

        # Rafraîchir les boutons pour appliquer les changements
        self.ville.SetBackgroundColour(wx.Colour(couleur_button))
        self.meteo.SetBackgroundColour(wx.Colour(couleur_button))
        self.list_ctrl.SetBackgroundColour(wx.Colour(couleur_button))

        # Rafraîchir le widget pour appliquer les changements
        self.ville.Refresh()
        self.panel.Refresh()

    def attendre(self):
        while pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            self.clock.tick(800)

    def on_meteo(self, event):
        choix_ville = self.ville.GetValue()
        api_key = "" # insérer votre api key
        pygame.mixer.init()

        # Essaye de se connecté aux données météo depuis le lien
        # choix ville correspond à la valeur de la variable ville entré par l'utilisateur
        # api_key doit être unique, ne la partagez à personne
        try:
            reponse = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={choix_ville}&appid={api_key}&units=metric')
            status_code = reponse.status_code
            print(status_code)
            afficher_ville = []

            # capture les données dans les variables
            if status_code == 200:
                donnees = reponse.json()
                temperature = donnees['main']['temp']
                ressenti = donnees['main']['feels_like']
                description = donnees['weather'][0]['description']
                humidite = donnees['main']['humidity']

                # ajouter à la liste afficher_ville
                afficher_ville.append(choix_ville)
                afficher_ville.append(f'{temperature}°C')
                afficher_ville.append(f'{ressenti}°C')
                afficher_ville.append(description)
                afficher_ville.append(f'{humidite}%')

                # affiche la liste dans le tableau
                index = self.list_ctrl.InsertItem(0, afficher_ville[0])  # Ajoute une nouvelle ligne
                self.list_ctrl.SetItem(index, 1, afficher_ville[1])
                self.list_ctrl.SetItem(index, 2, afficher_ville[2])
                self.list_ctrl.SetItem(index, 3, afficher_ville[3])
                self.list_ctrl.SetItem(index, 4, afficher_ville[4])


                # paramêtre l'assistance vocal de google gtts
                texte_audio = f"La météo du jour pour la commune de {choix_ville} - Temperature: {temperature}°C, Ressenti: {ressenti}°C, Le ciel est: {description}, L'humidité est de {humidite}%"
                tts = gTTS(texte_audio, lang='fr')
                tts.save(self.fichier_audio)
                pygame.mixer.music.load(self.fichier_audio)
                pygame.mixer.music.play()
                self.attendre()
                pygame.mixer.quit()

            # gestion des problèmes de recuparations des données l'erreur 401 et la plus récurrente, verifier votre lien/key_api
            else:
                texte_erreur = 'Erreur lors de la récupération des données'
                tts = gTTS(texte_erreur, lang='fr', slow=False)
                tts.save(self.audio_erreur)
                pygame.mixer.music.load(texte_erreur)
                pygame.mixer.music.play()

        # capture les erreurs survenue lors de l'execution du code
        except Exception as e:
            print(f"Une erreur s'est produite :", e)
            


app = wx.App(False)
frame = MyFrame(None, title="Météo Dylan", size=(530, 350))
app.MainLoop()
