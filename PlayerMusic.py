# Import depend
from pygame import mixer
import pygame
from tkinter import *
from tkinter import filedialog
from ttkbootstrap.constants import *
import ttkbootstrap as tb
import os

current_volume = 0.1
mixer.init()
current_song = None
timer_id = None
playlist = []
paused = False
remaining_duration = 0


def start_timer(callback):
    global timer_id, paused, remaining_duration
    if paused:
        return
    
    if remaining_duration > 0:
        remaining_duration -= 1
        song_duration_label.config(text=remaining_duration)
        timer_id = root.after(1000, start_timer, callback)
    else:
        callback()

def pause_timer():
    global paused, timer_id
    if timer_id is not None:
        root.after_cancel(timer_id)
        timer_id = None
        paused = True

def unpause_timer():
    global paused, remaining_duration
    if paused:
        paused = False
        start_timer(play_next_song)

def stop_timer():
    if timer_id is not None:
        root.after_cancel(timer_id)


def play_single():
    global paused, remaining_duration
    filename = filedialog.askopenfilename(initialdir='C:/', title='Choisir l''Emplacement.')
    song_title = filename.split('/')[-1]

    try:
        if current_song is not None:
            mixer.music.stop()
        mixer.music.load(filename)
        mixer.music.set_volume(current_volume)
        mixer.music.play()
        song_title_label.config(text='En Cours de Lecture : ' + str(song_title), bootstyle='success')
        remaining_duration = int(mixer.Sound(filename).get_length())
        start_timer(play_next_song)
    except pygame.error:
        song_title_label.config(bootstyle='warning', text='Erreur de Lecture.')

def play_next_song():
    global paused, remaining_duration
    if not playlist:
        song_title_label.config(text='Toutes les Pistes Sont Jouées.', bootstyle='success')
    song_path, song_title = playlist[0]
    try:
        if current_song is not None:
            mixer.music.stop()
        mixer.music.load(song_path)
        mixer.music.set_volume(current_volume)
        mixer.music.play()
        song_title_label.config(bootstyle='success', text='En Cours de Lecture : ' + str(song_title))
        remaining_duration = int(mixer.Sound(song_path).get_length())
        if timer_id is not None:
            stop_timer()
        start_timer(play_next_song)
    except pygame.error:
        song_title_label.config(bootstyle='warning', text='Erreur de Lecture.')
    playlist.pop(0)
    song_titles = [song[1] for song in playlist]
    song_list_string = "\n".join(song_titles)
    playlist_label.config(text=song_list_string)

def play_playlist():
    foldername = filedialog.askdirectory(initialdir='C:/', title=' Sélectionner un Dossier.')
    for root, _, files in os.walk(foldername):
        for file in files:
            if file.lower().endswith(('.mp3', '.wav', '.ogg', '.flac')):
                song_path = os.path.join(root, file)
                playlist.append([song_path, file])
    song_titles = [song[1] for song in playlist]
    song_list_string = "\n".join(song_titles)
    playlist_label.config(text=song_list_string)
    play_next_song()
    
def change_volume(volume):
    try:
        global current_volume
        current_volume = 1.0 - round(float(volume), 1)
        mixer.music.set_volume(current_volume)
    except Exception as e:
        print(e)
        song_title_label.config(bootstyle='warning', text='La Piste n''A Pas Encore Eté Sélectionnée.')

def song_toggle():
    global paused
    if paused:
        try:
            mixer.music.unpause()
            unpause_timer()
            paused = False
            toggle_button.config(text='Mettre en Pause.')
        except Exception as e:
            print(e)
            song_title_label.config(bootstyle='warning', text='La Piste n''A Pas Encore Eté Sélectionnée.')
    else:
        try:
            mixer.music.pause()
            pause_timer()
            paused = True
            toggle_button.config(text='Reprendre la Lecture.')
        except Exception as e:
            print(e)
            song_title_label.config(bootstyle='warning', text='La Piste n''A Pas Encore Eté Sélectionnée.')

def next_song():
    global playlist
    if not playlist:
        song_title_label.config(text='Toutes les Pistes Sont Jouées.', bootstyle='success')
        return
    play_next_song()


# Instantiate window
root = tb.Window(themename='vapor')
root.title('Player Music.')
root.geometry('800x600')

main_frame = tb.Frame(root)
main_frame.pack(side='top', fill='both', expand=True) # Sets position

title = tb.Label(main_frame, text='Player Music.', font=('Helvetica', 28), bootstyle='primary').pack(pady=5, padx=5)

# Song Title
song_title_label = tb.Label(main_frame, text='Ajouter une Piste.', font=('Helvetica', 15))
song_title_label.pack(padx=10, pady=10)

song_duration_label = tb.Label(main_frame, text='0', font=('Helvetica', 10))
song_duration_label.pack(side='top', padx=5, pady=5)

# Grab Song
select_button = tb.Button(main_frame, text='Choisir une Piste Audio.', bootstyle='secondary outline', command=play_single).pack(pady=5)

# Toggle Button
toggle_button = tb.Button(main_frame, text='Mettre en Pause.', bootstyle='secondary outline', command=song_toggle)
toggle_button.pack(pady=5)


# Volume Frame
volume_frame = tb.Frame(root)
volume_frame.pack(side='right', fill='both', expand=True)
volume = tb.Scale(volume_frame, orient='vertical', length=500, command=change_volume).pack(side='right', padx=15, pady=5)
volume_label = tb.Label(volume_frame, text='Volume.', bootstyle='primary', font=('Helvetica', 15)).pack(side='right', padx=5)

# Playlist Frame
playlist_frame = tb.Frame(root)
playlist_frame.pack(side='left', fill='both', expand=True)

playlist_button = tb.Button(playlist_frame, text='Choisir la Playlist.', bootstyle='primary outline', command=play_playlist)
next_song_button = tb.Button(playlist_frame, text='Piste Suivante.', bootstyle='primary outline', command=next_song)
playlist_button.pack(side='top', padx=5, pady=5)
next_song_button.pack(side='top', padx=1, pady=5)

playlist_view = tb.LabelFrame(playlist_frame, text='Playlist.', height=600, width=500, bootstyle='primary')
playlist_view.pack(side='top', padx=5, pady=5)

playlist_label = tb.Label(playlist_view, text='', bootstyle='primary', font=('Helvetica', 10))
playlist_label.pack(side='top', padx=5, pady=5)


root.mainloop()